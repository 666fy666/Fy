"""
Author: Fy
cron: 0 */15 * * * ?
new Env('b站监控');
"""
import random
import time
from wx import WeChatPub

import pymysql
import requests


class Bili:
    def __init__(self, id):
        self.id = id  # b站的uid，唯一的账号身份认证

    def main(self):
        url = "https://api.bilibili.com/x/space/navnum?mid=%s" % self.id
        r = self.login(url)
        try:
            info = r.json()["data"]
            info_num = info["album"] + info["article"] + info["video"]  # 投稿数
        except:
            print(r.json()["message"])
            return
        url = "https://api.bilibili.com/x/space/wbi/acc/info?mid=%s&token=&platform=web&web_location=1550101&w_rid=776709fa6a40a0a268cb5f5cb6998369&wts=1692552157" % self.id
        r = self.login(url)
        info = r.json()["data"]
        info_name = info["name"]
        info_verified_reason = info["official"]["title"]  # 认证信息
        info_description = info["sign"]  # 简介
        if info_description == "":
            info_description = "peace and love"  # 简介
        try:
            room = info["live_room"]["roomid"]
        except:
            room = "00000"
        url = "https://api.live.bilibili.com/room/v1/Room/room_init?id=%s" % room
        r = self.login(url)
        if r.json()['msg'] == '直播间不存在':
            live = "直播间不存在"
        else:
            live_status = r.json()['data']['live_status']  # 直播状态
            if live_status != 1:
                live = "下播"
            else:
                live = "开播"
        data = {
            "UID": self.id,
            "用户名": info_name,
            "认证信息": info_verified_reason,
            "简介": info_description,
            "投稿数": info_num,
            "live": live
        }
        old, old_live = self.check()
        if old == "-1":
            ms = "{} 的最近一条投稿😊".format(info_name)
            print(ms)
            new = 1
            self.go(data, new)
        elif int(old) < info_num:
            ms = "{} 发布了{}条投稿😍".format(info_name, info_num - int(old))
            print(ms)
            new = 1
            self.go(data, new)
        elif int(old) > info_num:
            ms = "{} 删除了{}条投稿😞".format(info_name, int(old) - info_num)
            print(ms)
            new = 0
            self.go(data, new)
        else:
            ms = "{} 最近在摸鱼🐟".format(info_name)
            print(ms)
            self.choose_in(data)  # 上传服务器保存（判断是否是首次上传）
        live = self.live(old_live, live)
        self.wx_live(live, room)

    def go(self, data, new):
        self.choose_in(data)  # 上传服务器保存（判断是否是首次上传）
        text, mid = self.analysis()  # 解析新发微博
        self.wx_pro(text, mid, new)  # 企业微信推送（效果好）

    def analysis(self):  # 解析新发微博的文字和blogid
        num = self.top()
        url = ("https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=&host_mid=%s&timezone_offset"
               "=-480&features=itemOpusStyle") % self.id
        r = self.login(url)
        spacing = "\n"  # 换行加留白，首行缩进
        text = ""
        try:
            text += "          " + r.json()["data"]["items"][num]["modules"]["module_dynamic"]["desc"]["text"]
        except:
            pass
        try:
            text += (spacing + "   " + r.json()["data"]["items"][num]["modules"]["module_author"]["pub_action"]
                     + "  " + r.json()["data"]["items"][num]["modules"]["module_author"]["pub_time"])
        except:
            pass

        if r.json()["data"]["items"][num]["modules"]["module_author"]["pub_action"] == "投稿了视频":
            try:
                text += spacing + "标题 : " + \
                        r.json()["data"]["items"][num]["modules"]["module_dynamic"]["major"]["archive"]["title"]
                text += spacing + "概要 : " + \
                        r.json()["data"]["items"][num]["modules"]["module_dynamic"]["major"]["archive"]["desc"]
                mid = r.json()["data"]["items"][num]["modules"]["module_dynamic"]["major"]["archive"]["bvid"]
            except:
                mid = r.json()["data"]["items"][num]["id_str"]
        else:
            mid = r.json()["data"]["items"][num]["id_str"]

        print(text)
        # 空格是适配推送图文的格式
        return text, mid

    def wx_pro(self, text, mid, new):  # 采用企业微信图文推送（效果好）
        try:
            if new == 1:
                new = "分享"
            else:
                new = "删除"
            sql = 'select 用户名, 认证信息, 简介 from bili where UID=%s'
            cursor.execute(sql, self.id)
            result = cursor.fetchall()  # 返回所有数据
            # result = cursor.fetchone()  # 返回一行数据
            # result = cursor.fetchmany(1)  # fetchmany(size) 获取查询结果集中指定数量的记录，size默认为1
            info_name = result[0][0]
            info_verified_reason = result[0][1]
            info_description = result[0][2]
            # 图片消息
            # title,description,url,picurl,btntxt='阅读全文'
            pic = "https://bing.img.run/rand_uhd.php"
            tip = "https://v1.hitokoto.cn/"
            res = requests.get(tip).json()
            res = res["hitokoto"] + "    ----" + res["from"]
            wechat = WeChatPub()
            if len(mid) > 16:
                wechat.send_news(
                    title='{} 在b站{}了投稿'.format(info_name, new),  # 标题
                    description='Ta:👇\n{}\n{}\n认证:{}\n\n简介:{}\n\n{}'.format
                    (text, "=" * 36, info_verified_reason, info_description, res),  # 说明文案
                    to_url=r"https://m.bilibili.com/opus/{}/".format(mid),  # 链接地址
                    picurl=r"%s" % pic  # 图片地址
                    # btntxt = '此处跳转'  https://www.picgo.net/image/ymwTq
                )
            else:
                wechat.send_news(
                    title='{} 在b站{}了投稿'.format(info_name, new),  # 标题
                    description='Ta:👇\n{}\n{}\n认证:{}\n\n简介:{}\n\n{}'.format
                    (text, "=" * 36, info_verified_reason, info_description, res),  # 说明文案
                    to_url=r"https://m.bilibili.com/video/{}/".format(mid),  # 链接地址
                    picurl=r"%s" % pic  # 图片地址
                    # btntxt = '此处跳转'  https://www.picgo.net/image/ymwTq
                )
        except Exception as e:
            db.rollback()
            print(e)

    def top(self):  # 验证置顶微博数，防止截图错位
        url = ("https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=&host_mid=%s&timezone_offset=-480"
               "&features=itemOpusStyle") % self.id
        r = self.login(url)
        num = r.text.count('module_tag')
        return int(num)

    def choose_in(self, data):  # 判断GitHub上是否有上传记录
        print(data)
        self.del_database()
        self.in_database(data)

    def del_database(self):  # 更新数据库(删除旧数据)
        try:
            sql = 'delete from  bili where UID = %s'
            cursor.execute(sql, self.id)
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)

    def in_database(self, data):  # 更新数据库(插入新数据)
        sql = ('insert into bili(UID,用户名,认证信息,简介,投稿数,live) '
               'VALUES(%(UID)s, %(用户名)s, %(认证信息)s,%(简介)s,%(投稿数)s,%(live)s)')
        try:
            cursor.execute(sql, data)
            db.commit()
            print("successful")
        except Exception as e:
            db.rollback()
            print(e)

    def check(self):  # 判断是否是第一次录入信息并查询投稿数
        try:
            sql = 'select 投稿数 from bili where UID=%s'
            cursor.execute(sql, self.id)
            # result = cursor.fetchall()  # 返回所有数据
            result = cursor.fetchone()  # 返回一行数据
            # result = cursor.fetchmany(1)  # fetchmany(size) 获取查询结果集中指定数量的记录，size默认为1
            old_num = str(result[0])
            sql = 'select live from bili where UID=%s'
            cursor.execute(sql, self.id)
            # result = cursor.fetchall()  # 返回所有数据
            result = cursor.fetchone()  # 返回一行数据
            # result = cursor.fetchmany(1)  # fetchmany(size) 获取查询结果集中指定数量的记录，size默认为1
            old_live = str(result[0])
        except:
            db.rollback()
            print("未查找到该用户，将信息录入")
            old_num = "-1"
            old_live = 0
        return old_num, old_live

    def live(self, old_live, live):  # 检测直播状态
        if old_live == live:
            print("%s的直播状态已提醒" % self.id)
            return 2
        elif old_live == "下播" and live == "开播":
            print("%s开播了" % self.id)
            return 1
        else:
            print("%s下播了" % self.id)
            return 0

    def wx_live(self, live, real_room_id):  # 采用企业微信图文推送（效果好）
        try:
            if live == 1:
                live = "在bilibili开播了"
            elif live == 0:
                live = "在bilibili下播了"
            else:
                return
            sql = 'select 用户名, 认证信息, 简介 from bili where UID=%s'
            cursor.execute(sql, self.id)
            result = cursor.fetchall()  # 返回所有数据
            # result = cursor.fetchone()  # 返回一行数据
            # result = cursor.fetchmany(1)  # fetchmany(size) 获取查询结果集中指定数量的记录，size默认为1
            info_name = result[0][0]
            info_verified_reason = result[0][1]
            info_description = result[0][2]
            # 图片消息
            # title,description,url,picurl,btntxt='阅读全文'
            pic = "https://bing.img.run/rand_uhd.php"
            tip = "https://v1.hitokoto.cn/"
            res = requests.get(tip).json()
            res = res["hitokoto"] + "    ----" + res["from"]
            wechat = WeChatPub()
            wechat.send_news(
                title='{} {}'.format(info_name, live),  # 标题
                description='\n认证:{}\n\n简介:{}\n\n{}'.format
                (info_verified_reason, info_description, res),  # 说明文案
                to_url=r"https://live.bilibili.com/{}?broadcast_type=0&is_room_feed=1&spm_id_from=333.999.to_liveroom"
                       r".0.click&live_from=86002".format(real_room_id),  # 链接地址
                picurl=r"%s" % pic  # 图片地址
                # btntxt = '此处跳转'  https://www.picgo.net/image/ymwTq
            )
        except Exception as e:
            db.rollback()
            print(e)

    def login(self, url):  # 发起协议模板
        proxy_ip = "https://" + self.get_ip()
        # 设置代理信息
        proxies = {
            "http": proxy_ip,
        }
        # print(proxies)
        session = requests.session()
        headers = {
            "User-Agent": User_Agent,
            "Cookie": Cookie,
        }
        r = session.get(url, headers=headers, proxies=proxies, timeout=60)
        # print(r.text)
        return r

    def get_ip(self):
        sql = 'select count(proxy) from IP'
        cursor.execute(sql)
        num = cursor.fetchall()[0][0]  # 返回所有数据
        temp_ip = []
        sql = 'select proxy from IP'
        cursor.execute(sql)
        for i in range(0, num):
            result = cursor.fetchone()[0]  # 返回一行数据
            temp_ip.append(result)
        a = random.randint(0, num)
        return temp_ip[a]


if __name__ == '__main__':
    try:
        url = "https://raw.gitcode.com/qq_35720175/web/raw/main/config.json"
        file = requests.get(url)
        User_Agent = file.json()["User-Agent"]
        Cookie = file.json()["bcookie"]
        pushplus = file.json()["pushplus"]
        not_show = file.json()["not_show"]
        email = file.json()["email"]
        token = file.json()["token"]
        uid = file.json()["bili"]
        host = file.json()["host"]
        user = file.json()["user"]
        pwd = file.json()["password"]
        dbs = file.json()["db"]
        db = pymysql.connect(host='%s' % host, user='%s' % user, password='%s' % pwd, port=3306, db='%s' % dbs)
        cursor = db.cursor()
        for i in range(len(uid)):
            try:
                bili = Bili(uid[i])
                bili.main()
                print("=" * 80)
            except Exception as e:
                print(e)
        cursor.close()
        db.close()
    except Exception as e:
        print(e)
