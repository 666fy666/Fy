"""
Author: Fy
cron: 0 */1 * * * ?
new Env('微博监控');
"""
import os
import random
import threading
import time

import pymysql
import requests

from wx import WeChatPub

url = "https://gitcode.net/qq_35720175/tip/-/raw/master/config.json"
file = requests.get(url)
User_Agent = file.json()["User-Agent"]
Cookie = file.json()["Cookie"]
pushplus = file.json()["pushplus"]
not_show = file.json()["not_show"]
email = file.json()["email"]
token = file.json()["token"]
uid = file.json()["uid"]
host = file.json()["host"]
user = file.json()["user"]
pwd = file.json()["password"]
dbs = file.json()["db"]


class WeiBo:
    def __init__(self, id):
        db = pymysql.connect(host='%s' % host, user='%s' % user, password='%s' % pwd, port=3306, db='%s' % dbs)
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor
        self.id = id  # 微博的uid，唯一的账号身份认证

    def main(self):
        url = "https://weibo.com/ajax/profile/info?uid=%s" % self.id
        r = self.pre(url)
        info = r.json()["data"]["user"]
        info_id = info["idstr"]  # UID
        info_name = info["screen_name"]  # 用户名
        try:
            info_verified_reason = info["verified_reason"]  # 认证信息
        except:
            info_verified_reason = "人气博主"  # 认证信息
        info_description = info["description"]  # 简介
        if info_description == "":
            info_description = "peace and love"  # 简介
        info_followers = info["followers_count_str"]  # 粉丝数
        info_num = info["statuses_count"]  # 微博数
        data = {
            "UID": info_id,
            "用户名": info_name,
            "认证信息": info_verified_reason,
            "简介": info_description,
            "粉丝数": info_followers,
            "微博数": str(info_num),
        }
        old = self.check()
        time.sleep(1)
        if old == "-1":
            ms = "{} 的最近一条微博😊".format(info_name)
            print(ms)
            new = 1
            self.go(data, new)
        elif int(old) < info_num:
            ms = "{} 发布了{}条微博😍".format(info_name, info_num - int(old))
            print(ms)
            new = 1
            self.go(data, new)
        elif int(old) > info_num:
            ms = "{} 删除了{}条微博😞".format(info_name, int(old) - info_num)
            print(ms)
            new = 0
            self.go(data, new)
        else:
            ms = "{} 最近在摸鱼🐟".format(info_name)
            print(ms)
        self.cursor.close()
        self.db.close()

    def go(self, data, new):
        self.choose_in(data)  # 上传服务器保存（判断是否是首次上传）
        text, mid = self.analysis()  # 解析新发微博
        self.wx_pro(text, mid, new)  # 企业微信推送（效果好）

    def choose_in(self, data):  # 判断GitHub上是否有上传记录
        print(data)
        self.del_database()
        time.sleep(1)
        self.in_database(data)

    def wx_pro(self, text, mid, new):  # 采用企业微信图文推送（效果好）
        if new == 1:
            new = "分享"
        else:
            new = "删除"
        sql = 'select 用户名, 认证信息, 简介 from weibo where UID=%s'
        self.cursor.execute(sql, self.id)
        result = self.cursor.fetchall()  # 返回所有数据
        # result = cursor.fetchone()  # 返回一行数据
        # result = cursor.fetchmany(1)  # fetchmany(size) 获取查询结果集中指定数量的记录，size默认为1
        info_name = result[0][0]
        info_verified_reason = result[0][1]
        info_description = result[0][2]
        # 图片消息
        # title,description,url,picurl,btntxt='阅读全文'
        tip = "https://v1.hitokoto.cn/"
        res = requests.get(tip).json()
        res = res["hitokoto"] + "    ----" + res["from"]
        wechat = WeChatPub()
        wechat.send_text(
            title='{} {}了一条weibo'.format(info_name, new),  # 标题
            message='Ta说:👇\n{}\n{}\n认证:{}\n\n简介:{}\n\n{}'.format
            (text, "=" * 35, info_verified_reason, info_description, res),  # 说明文案
            purl=r"https://m.weibo.cn/detail/{}".format(mid)  # 链接地址
        )

    def analysis(self):  # 解析新发微博的文字和blogid
        num = self.top()
        url = "https://weibo.com/ajax/statuses/mymblog?uid=%s&page=1&feature=0" % self.id
        r = self.pre(url)
        spacing = "\n          "  # 换行加留白，首行缩进
        text = "          " + r.json()["data"]["list"][num]["text_raw"]  # 内容原文
        try:
            pic_num = len(r.json()["data"]["list"][num]["pic_ids"])
            if pic_num > 0:
                text += spacing + "[图片]  *  %s      (详情请点击噢!)" % pic_num  # 微博的图片个数
        except:
            pass
        try:
            text += spacing + "#" + r.json()["data"]["list"][num]["url_struct"][0]["url_title"] + "#"
            # 转发的微博视频或链接
        except:
            pass
        text += spacing + "                " + r.json()["data"]["list"][num]["created_at"]  # 发微博的时间
        # 空格是适配推送图文的格式
        mid = r.json()["data"]["list"][num]["mid"]
        print(text)
        return text, mid

    def check(self):  # 判断是否是第一次录入信息并查询微博数
        try:
            sql = 'select 微博数 from weibo where UID=%s'
            self.cursor.execute(sql, self.id)
            # result = cursor.fetchall()  # 返回所有数据
            result = self.cursor.fetchone()  # 返回一行数据
            # result = cursor.fetchmany(1)  # fetchmany(size) 获取查询结果集中指定数量的记录，size默认为1
            old_num = str(result[0])
        except:
            self.db.rollback()
            print("未查找到该用户，将信息录入")
            old_num = "-1"
        return old_num

    def del_database(self):  # 更新数据库(删除旧数据)
        try:
            sql = 'delete from  weibo where UID = %s'
            self.cursor.execute(sql, self.id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)

    def in_database(self, data):  # 更新数据库(插入新数据)
        sql = ('insert into weibo(UID,用户名,认证信息,简介,粉丝数,微博数) '
               'VALUES(%(UID)s, %(用户名)s, %(认证信息)s,%(简介)s,%(粉丝数)s,%(微博数)s)')
        try:
            self.cursor.execute(sql, data)
            self.db.commit()
            print("successful")
        except Exception as e:
            self.db.rollback()
            print(e)

    def top(self):  # 验证置顶微博数，防止截图错位
        url = "https://weibo.com/ajax/statuses/mymblog?uid=%s&page=1&feature=0" % self.id
        r = self.pre(url)
        num = r.text.count("isTop")
        return int(num)

    def pre(self, url):  # 找置顶微博和解析微博的准备工作
        # proxy_ip = "https://" + self.get_ip()
        # 设置代理信息
        # proxies = {
        # "http": proxy_ip,
        # }
        # print(proxies)
        session = requests.session()
        headers = {
            "User-Agent": User_Agent,
            "Cookie": Cookie
        }
        # r = session.get(url, headers=headers, proxies=proxies, timeout=60)
        r = session.get(url, headers=headers, timeout=60)
        return r

    def get_ip(self):
        sql = 'select count(proxy) from IP'
        self.cursor.execute(sql)
        num = self.cursor.fetchall()[0][0]  # 返回所有数据
        temp_ip = []
        sql = 'select proxy from IP'
        self.cursor.execute(sql)
        for i in range(0, num):
            result = self.cursor.fetchone()[0]  # 返回一行数据
            temp_ip.append(result)
        a = random.randint(1, num - 1)
        return temp_ip[a]


def process_user(uid):
    try:
        weibo = WeiBo(uid)
        weibo.main()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    threads = []
    for i in range(len(uid)):
        thread = threading.Thread(target=process_user, args=(uid[i],))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
