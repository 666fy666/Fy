"""
Author: Fy
new Env('ip池');
"""
import re
from wx import WeChatPub

import pymysql
import requests
from lxml import etree


def get_ip():
    for i in range(1, 11):
        url = "https://proxy.ip3366.net/free/?action=china&page=%s" % i
        headers = {
            "User-Agent": User_Agent,
            "Cookie": "https_waf_cookie=bff2e02b-eb1c-404f22538018154eeb9707190b718d20f065; "
                      "Hm_lvt_96901db7af1741c2fd2d52f310d78eaa=1693283462; "
                      "Hm_lvt_c4dd741ab3585e047d56cf99ebbbe102=1693285113; "
                      "Hm_lpvt_c4dd741ab3585e047d56cf99ebbbe102=1693285229; "
                      "Hm_lpvt_96901db7af1741c2fd2d52f310d78eaa=1693285354"
        }
        res = requests.get(url, timeout=30, headers=headers)
        html = etree.HTML(res.text)
        td = html.xpath("//tbody/tr")
        for u in td:
            ip = u.xpath("./td[1]//text()")[0]  # 地址
            port = u.xpath("./td[2]//text()")[0]  # 端口
            tp = u.xpath("./td[4]//text()")[0]  # 类型
            local = u.xpath("./td[5]//text()")[0]  # 位置
            speed = u.xpath("./td[6]//text()")[0]  # 响应速度
            in_time = u.xpath("./td[7]//text()")[0]  # 录取时间
            in_database(
                {"proxy": f"{ip}:{port}", "类型": tp, "位置": local, "响应速度": speed, "录取时间": in_time})


def in_database(data):  # 更新数据库(插入新数据)
    sql = ('insert into IP(proxy,类型,位置,响应速度,录取时间) '
           'VALUES(%(proxy)s, %(类型)s, %(位置)s,%(响应速度)s,%(录取时间)s)')
    try:
        cursor.execute(sql, data)
        db.commit()
        # print("successful")
    except Exception as e:
        db.rollback()
        # print(e)


def find_all(num):
    try:
        temp_ip = []
        sql = 'select proxy from IP'
        cursor.execute(sql)
        for i in range(0, num):
            result = cursor.fetchone()[0]  # 返回一行数据
            temp_ip.append(result)
        return temp_ip
    except:
        db.rollback()


def test_ip():  # 测试ip是否可用
    sql = 'select count(proxy) from IP'
    cursor.execute(sql)
    num = cursor.fetchall()[0][0]  # 返回所有数据
    temp_ip = find_all(num)
    for u in range(0, num):
        proxy_ip = temp_ip[u]
        # 设置代理信息
        proxies = {
            "http": "http://" + proxy_ip,
            "https": "http://" + proxy_ip,
        }
        fake_ip = re.split(r'[:：]', proxy_ip)[0]
        try:
            res = requests.get(url="https://icanhazip.com/", timeout=60, proxies=proxies)
            return_ip = res.text
            text = ("返回ip:%s,格式%s" % return_ip % str(type(return_ip)))
            print(text)
            text += "\n"
            if return_ip == fake_ip:
                text += "代理IP:" + fake_ip + "有效!" + str(type(fake_ip))
                print(text)
                wx(text)
                print("=" * 80)
            else:
                text += "代理IP:" + fake_ip + "无效!" + str(type(fake_ip))
                print(text)
                wx(text)
                print("=" * 80)
        except:
            print("代理IP:" + fake_ip + "无效!" + str(type(fake_ip)))


def main():
    get_ip()
    test_ip()


def wx(text):
    pic = "https://bing.img.run/rand_uhd.php"
    tip = "https://v1.hitokoto.cn/"
    res = requests.get(tip).json()
    res = res["hitokoto"] + "    ----" + res["from"]
    wechat = WeChatPub()
    wechat.send_news(
        title='IP池',  # 标题
        description='{}\n\n{}'.format(text, res),  # 说明文案
        to_url=r"%s" % pic,  # 链接地址
        picurl=r"%s" % pic  # 图片地址
        # btntxt = '此处跳转'  https://www.picgo.net/image/ymwTq
    )




if __name__ == '__main__':
    try:
        url = "https://gitcode.net/qq_35720175/tip/-/raw/master/config.json"
        file = requests.get(url)
        User_Agent = file.json()["User-Agent"]
        host = file.json()["host"]
        user = file.json()["user"]
        pwd = file.json()["password"]
        dbs = file.json()["db"]
        db = pymysql.connect(host='%s' % host, user='%s' % user, password='%s' % pwd, port=3306, db='%s' % dbs)
        cursor = db.cursor()
        try:
            main()
        except Exception as e:
            print(e)
        cursor.close()
        db.close()
    except Exception as e:
        print(e)
