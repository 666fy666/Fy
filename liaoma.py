"""
Author: Fy
cron: 0 */1 * * * ?
new Env('料码监控');
"""
import json
import os

import pymysql
import requests


class LiaoMa:

    def main(self):
        url = "https://jklz.lmsc.red/dtkj/0u7Cc0E0AZEU/getUserSelds"
        for index in range(1, 9):
            r = self.pre(url, index)
            res = self.check(r)
            if res == 0:
                break

    def pre(self, url, index):
        headers = {
            "User-Agent": User_Agent,
        }
        params = {'uid': '275176',
                  'sid': 'BYXi8izVBN5K',
                  'seltype': '1',
                  'selid': '',
                  'soid': '74f9eb0b76cd6997',
                  'index': index
                  }
        r = requests.get(url, headers=headers, params=params, timeout=60)
        return r

    def check(self, r):
        r = r.json()['data']
        '''
        data = {
            "sid": r[0]['s_id'],
            "title": r[0]['title'],
            "shortmsg": r[0]['short_msg'],
            "time": r[0]['create_time'],
            "price": r[0]['price'],
        }
        self.push(data)
        '''
        for num in range(0, 10):
            if "公众号获取方式" in str(r[num]['title']):
                return 0
            data = {
                "sid": r[num]['s_id'],
                "title": r[num]['title'],
                "shortmsg": r[num]['short_msg'],
                "time": r[num]['create_time'],
                "price": r[num]['price'],
            }
            sql = ('insert into pushplus(sid,title,shortmsg,time,price) '
                   'VALUES(%(sid)s, %(title)s, %(shortmsg)s,%(time)s,%(price)s)')
            try:
                cursor.execute(sql, data)
                db.commit()
                print("successful,上新了\n%s" % data)
                self.push(data)
            except Exception as e:
                db.rollback()
                #  print(e)

    def push(self, data):
        title = data["title"]
        shortmsg = data["shortmsg"]
        price = data["price"]
        time = data["time"]
        sid = data["sid"]
        if os.getenv('push'):
            token = os.getenv('push')
            print("%s" % token)
        else:
            token = '982fe9bccbaf48cca752eb7f5ff1d976'
        url = 'http://www.pushplus.plus/send'
        data = {
            "token": token,
            "title": data["title"],
            "content": '{}\n\n{}\n\n{}\n\n{}\n\n<a href="https://jklz.lmsc.red/dtkj/0u7Cc0E0AZEU/showProDetail?reqTime=1703775340037&uid=275176&sid=BYXi8izVBN5K&spid={}&fromType=3&signtime=1703772885034&sign=8d83435d40b749e4877ab89cb85a3230&">This link</a>'.format(
                title, shortmsg, price, time, sid),
            "template": "markdown"
        }
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        requests.post(url, data=body, headers=headers)


if __name__ == '__main__':
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
    db = pymysql.connect(host='%s' % host, user='%s' % user, password='%s' % pwd, port=3306, db='%s' % dbs)
    cursor = db.cursor()
    for u in range(0, 5):
        try:
            liaoma = LiaoMa()
            liaoma.main()
            print("=" * 80)
            break
        except Exception as e:
            print(e)
    cursor.close()
    db.close()
