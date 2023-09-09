"""
Author: Fy
cron: 0 */2 * * * ?
new Env('虎牙直播监控');
"""
# 获取虎牙直播的真实流媒体地址。
import json
import time
from wx import WeChatPub

import pymysql
import requests
import re
import base64
import hashlib
from urllib.parse import parse_qs, urlencode
from datetime import datetime
import random


class HuYa:
    def __init__(self, id):
        self.room_id = id  # 虎牙房间号

    def live(self, info):
        stream_info = dict({'flv': {}, 'hls': {}})
        cdn_type = dict({'AL': '阿里', 'TX': '腾讯', 'HW': '华为', 'HS': '火山', 'WS': '网宿', 'HY': '虎牙'})
        uid = self.get_anonymous_uid()
        for s in info["roomInfo"]["tLiveInfo"]["tLiveStreamInfo"]["vStreamInfo"]["value"]:
            if s["sFlvUrl"]:
                stream_info["flv"][cdn_type[s["sCdnType"]]] = "{}/{}.{}?{}".format(s["sFlvUrl"], s["sStreamName"],
                                                                                   s["sFlvUrlSuffix"],
                                                                                   self.process_anticode(
                                                                                       s["sFlvAntiCode"],
                                                                                       uid,
                                                                                       s["sStreamName"]))
            if s["sHlsUrl"]:
                stream_info["hls"][cdn_type[s["sCdnType"]]] = "{}/{}.{}?{}".format(s["sHlsUrl"], s["sStreamName"],
                                                                                   s["sHlsUrlSuffix"],
                                                                                   self.process_anticode(
                                                                                       s["sHlsAntiCode"],
                                                                                       uid,
                                                                                       s["sStreamName"]))
        return stream_info

    def process_anticode(self, anticode, uid, streamname):
        q = dict(parse_qs(anticode))
        q["ver"] = ["1"]
        q["sv"] = ["2110211124"]
        q["seqid"] = [str(int(uid) + int(datetime.now().timestamp() * 1000))]
        q["uid"] = [str(uid)]
        q["uuid"] = [str(self.get_uuid())]
        ss = hashlib.md5("{}|{}|{}".format(q["seqid"][0], q["ctype"][0], q["t"][0]).encode("UTF-8")).hexdigest()
        q["fm"][0] = base64.b64decode(q["fm"][0]).decode('utf-8').replace("$0", q["uid"][0]).replace("$1",
                                                                                                     streamname).replace(
            "$2", ss).replace("$3", q["wsTime"][0])
        q["wsSecret"][0] = hashlib.md5(q["fm"][0].encode("UTF-8")).hexdigest()
        del q["fm"]
        if "txyp" in q:
            del q["txyp"]
        return urlencode({x: y[0] for x, y in q.items()})

    def get_anonymous_uid(self):
        proxy_ip = "https://" + self.get_ip()
        # 设置代理信息
        proxies = {
            "http": proxy_ip,
        }
        url = "https://udblgn.huya.com/web/anonymousLogin"
        resp = requests.post(url, proxies=proxies,json={
            "appId": 5002,
            "byPass": 3,
            "context": "",
            "version": "2.4",
            "data": {}
        })
        return resp.json()["data"]["uid"]

    def get_uuid(self):
        # Number((Date.now() % 1e10 * 1e3 + (1e3 * Math.random() | 0)) % 4294967295))
        now = datetime.now().timestamp() * 1000
        rand = random.randint(0, 1000) | 0
        return int((now % 10000000000 * 1000 + rand) % 4294967295)

    def get_real_url(self):
        try:
            proxy_ip = "https://" + self.get_ip()
            # 设置代理信息
            proxies = {
                "http": proxy_ip,
            }
            room_url = 'https://m.huya.com/' + str(self.room_id)
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/75.0.3770.100 Mobile Safari/537.36 '
            }
            response = requests.get(url=room_url, proxies=proxies,headers=header).text
            room_info_str = re.findall(r'\<script\> window.HNF_GLOBAL_INIT = (.*) \</script\>', response)[0]
            room_info = json.loads(room_info_str)
            data = {
                "room": self.room_id,
                "name": room_info["roomInfo"]["tProfileInfo"]["sNick"],
                "title": room_info["roomInfo"]["tLiveInfo"]["sIntroduction"],
                "kind": room_info["roomInfo"]["tLiveInfo"]["sGameFullName"],
            }
            if room_info["roomInfo"]["eLiveStatus"] == 2:  # 在直播
                print('该直播间源地址为：')
                real_url = json.dumps(self.live(room_info), indent=2, ensure_ascii=False)
                self.deal(real_url, data, num=1)
            elif room_info["roomInfo"]["eLiveStatus"] == 3:  # 下播
                print('该直播间正在回放历史直播，低清晰度源地址为：')
                real_url = "https:{}".format(base64.b64decode(room_info["roomProfile"]["liveLineUrl"]).decode('utf-8'))
                self.deal(real_url, data, num=0)
            else:
                real_url = '未开播'
                self.deal(real_url, data, num=0)
        except Exception as e:
            print(e)
            real_url = '%s 这个直播间不存在' % self.room_id
        return real_url

    def deal(self, real_url, data, num):
        try:
            sql = 'select is_live from huya where room=%s'
            cursor.execute(sql, self.room_id)
            result = cursor.fetchall()  # 返回所有数据
            old = result[0][0]
            if old == num:
                data["is_live"] = old
                data["real_url"] = real_url
                self.check(data)
                print("%s的直播状态已提醒" % self.room_id)
            else:
                data["is_live"] = num
                data["real_url"] = real_url
                self.check(data)
                self.wx_pro(data)
        except:
            data["is_live"] = num
            data["real_url"] = real_url
            self.check(data)
            self.wx_pro(data)

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
        a = random.randint(0,num)
        return temp_ip[a]

    def wx_pro(self, data):  # 采用企业微信图文推送（效果好）
        try:
            # 图片消息
            # title,description,url,picurl,btntxt='阅读全文'
            random_number = random.uniform(1, 2)
            if random_number == 1:
                pic = "https://bing.img.run/uhd.php"
            else:
                pic = "https://bing.img.run/rand_uhd.php"
            tip = "https://v1.hitokoto.cn/"
            res = requests.get(tip).json()
            res = res["hitokoto"] + "    ----" + res["from"]
            curr_time = datetime.now()
            timestamp = datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')
            if data["is_live"] == 1:
                is_live = "开播了"
            else:
                is_live = "下播了"
            wechat = WeChatPub()
            wechat.send_news(
                title='{} {}🐯🐯🐯'.format(data["name"], is_live),  # 标题
                description='Ta的虎牙房间号是 : {}\n\n标题 : {}\n\n当前在 : {}分区\n\n{}\n\n{}'.format
                (self.room_id, data["title"], data["kind"], res, timestamp),  # 说明文案
                to_url=r'https://m.huya.com/' + str(self.room_id),  # 链接地址
                picurl=r"%s" % pic  # 图片地址
                # btntxt = '此处跳转'  https://www.picgo.net/image/ymwTq
            )
        except Exception as e:
            # db.rollback()
            print(e)

    def check(self, data):  # 写入并更新直播状态
        self.del_database()
        self.in_database(data)

    def del_database(self):  # 更新数据库(删除旧数据)
        try:
            sql = 'delete from  huya where room = %s'
            cursor.execute(sql, self.room_id)
            db.commit()
        except Exception as e:
            db.rollback()
            print(e)

    def in_database(self, data):  # 更新数据库(插入新数据)
        sql = ('insert into huya(room,name,title,is_live,kind,real_url) '
               'VALUES(%(room)s, %(name)s, %(title)s,%(is_live)s,%(kind)s,%(real_url)s)')
        try:
            cursor.execute(sql, data)
            db.commit()
            print("successful")
        except Exception as e:
            db.rollback()
            print(e)


if __name__ == '__main__':
    url = "https://gitcode.net/qq_35720175/tip/-/raw/master/config.json"
    file = requests.get(url)
    rid = file.json()["room"]
    host = file.json()["host"]
    user = file.json()["user"]
    pwd = file.json()["password"]
    dbs = file.json()["db"]
    db = pymysql.connect(host='%s' % host, user='%s' % user, password='%s' % pwd, port=3306, db='%s' % dbs)
    cursor = db.cursor()
    for i in range(len(rid)):
        for u in range(0, 5):
            try:
                app = HuYa(rid[i])
                real_url = app.get_real_url()
                print(real_url)
                print("=" * 40)
                break
            except:
                print("fail")
        time.sleep(1)
