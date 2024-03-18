"""
Author: Fy
cron: */20 * * * * ?
new Env('微博监控');
"""
import threading

import pymysql
import requests

from wx import WeChatPub

url = "https://raw.gitcode.com/qq_35720175/web/raw/main/config.json"
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
        try:
            db = pymysql.connect(host='192.168.66.239', user='%s' % user, password='%s' % pwd, port=3306, db='%s' % dbs)
            cursor = db.cursor()
            self.db = db
            self.cursor = cursor
        except:
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
        old_num, old_text = self.check()  # 检查是否为新用户
        if old_num == "-1":  # -1表示为新用户，用insert插入新数据
            ms = "{} 的最近一条微博😊".format(info_name)
            print(ms)
            new = "首次录入"
            num = 1
            text, mid = self.analysis()  # 解析新发微博
            data["文本"] = text
            self.in_database(data)
            self.wx_pro(text, mid, new, num)  # 企业微信推送（效果好）
        elif int(old_num) < info_num:  # 大于0表示为老用户，用update更新数据
            num = info_num - int(old_num)
            ms = "{} 发布了{}条微博😍".format(info_name, num)
            print(ms)
            new = "分享"
            text, mid = self.analysis()  # 解析新发微博
            data["文本"] = text
            self.update_database(data)
            if text != old_text:
                self.wx_pro(text, mid, new, num)  # 企业微信推送（效果好）
        elif int(old_num) > info_num:  # 大于0表示为老用户，用update更新数据
            num = int(old_num) - info_num
            ms = "{} 删除了{}条微博😞".format(info_name, num)
            print(ms)
            new = "删除"
            text, mid = self.analysis()  # 解析新发微博
            data["文本"] = text
            self.update_database(data)
            if text != old_text:
                self.wx_pro(text, mid, new, num)  # 企业微信推送（效果好）
        else:
            ms = "{} 最近在摸鱼🐟".format(info_name)
            print(ms)
        self.cursor.close()
        self.db.close()

    def wx_pro(self, text, mid, new, num):  # 采用企业微信图文推送（效果好）
        sql = 'select 用户名, 认证信息, 简介 from weibo where UID=%s'
        self.cursor.execute(sql, self.id)
        result = self.cursor.fetchall()  # 返回所有数据
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
            title='{} {}了{}条weibo'.format(info_name, new, num),  # 标题
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
            sql1 = 'select 微博数 from weibo where UID=%s'
            self.cursor.execute(sql1, self.id)
            result1 = self.cursor.fetchone()  # 返回一行数据
            old_num = str(result1[0])
            sql2 = 'select 文本 from weibo where UID=%s'
            self.cursor.execute(sql2, self.id)
            result2 = self.cursor.fetchone()  # 返回一行数据
            old_text = str(result2[0])
        except:
            print("未查找到该用户，将信息录入")
            old_num = "-1"
            old_text = "-1"
        return old_num, old_text

    def update_database(self, data):  # 更新数据库
        try:
            sql1 = 'update weibo set 微博数=%(微博数)s where UID=%(UID)s'
            sql2 = 'update weibo set 文本=%(文本)s where UID=%(UID)s'
            self.cursor.execute(sql1, data)
            self.cursor.execute(sql2, data)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)

    def in_database(self, data):  # 插入新数据
        sql = ('insert into weibo(UID,用户名,认证信息,简介,粉丝数,微博数,文本) '
               'VALUES(%(UID)s, %(用户名)s, %(认证信息)s,%(简介)s,%(粉丝数)s,%(微博数)s,%(文本)s)')
        try:
            self.cursor.execute(sql, data)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(e)

    def top(self):  # 验证置顶微博数，防止截图错位
        url = "https://weibo.com/ajax/statuses/mymblog?uid=%s&page=1&feature=0" % self.id
        r = self.pre(url)
        num = r.text.count("isTop")
        return int(num)

    def pre(self, url):  # 找置顶微博和解析微博的准备工作
        session = requests.session()
        headers = {
            "User-Agent": User_Agent,
            "Cookie": Cookie
        }
        r = session.get(url, headers=headers, timeout=60)
        return r


def process_user(uid):
    weibo = WeiBo(uid)
    weibo.main()


if __name__ == '__main__':
    threads = []
    for i in range(len(uid)):
        thread = threading.Thread(target=process_user, args=(uid[i],))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
