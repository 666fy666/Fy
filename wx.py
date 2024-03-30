"""
Author: Fy
new Env('企业微信推送');
"""
import json
import os
import time

import requests


class WeChatPub:
    s = requests.session()

    def __init__(self):
        self.corpid = 'wwa721a143a22ceed4'
        self.secret = 'OZwYUc5FABoqJVonBioH3DekVeuvlf5pjkxLTdaHJus'  # 企业微信应用后台查看
        self.token = self.get_token()

        # print('init_token',self.token)

    def get_token(self):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.secret}&debug=1"
        rep = self.s.get(url)
        # print('rep_token', rep.content)
        if rep.status_code != 200:
            print('get token failed')
            return
        return json.loads(rep.content)['access_token']

    def get_media_url(self):  # 上传到图片素材 图片url
        num = 1
        while 1 == 1:
            url = "https://bing.img.run/rand_1366x768.php"
            header = {
                "Content-Type": "application/json"
            }
            img_name = 'code.png'
            # 发送请求
            res = requests.get(url, headers=header)
            with open(img_name, 'wb') as file_obj:
                # 保存图片、音频之类 会使用content-->以二进制写入去响应对象里面取
                file_obj.write(res.content)
            img_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image" % self.token
            files = {"media": open(img_name, "rb")}
            try:
                r =self.s.post(img_url, files=files, timeout=5)
                print("第%s次上传,成功" % num)
                return r.json()["media_id"]
            except:
                num = num + 1
                continue

    def send_news(self, title, description, to_url, picurl, btntxt='阅读全文'):# 跳转为链接
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        # python 字典若要转json，千万不能用单引号，要用双引号~@@双引号~~~！！！
        form_data = {
            "touser": "FengYu",
            "msgtype": "news",
            "agentid": "1000002",
            "news": {
                "articles": [
                    {
                        "title": title,
                        "description": description,
                        "url": to_url,
                        "author": "FengYu",
                        "picurl": picurl,
                        "btntxt": btntxt
                    }
                ]
            },
            "enable_id_trans": 0,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        print(form_data, type(form_data))
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        if rep.status_code != 200:
            print("request failed")
            return
        return json.loads(rep.content)

    def send_text(self, title, message, purl): # 跳转为文本
        header = {
            "Content-Type": "application/json"
        }
        media_id = self.get_media_url()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        send_values = {
            "touser": "FengYu",
            "msgtype": "mpnews",
            "agentid": "1000002",
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "FengYu",
                        "content_source_url": purl,
                        "content": message.replace("\n", "<br/>").replace(" ", "&nbsp;"),
                        "digest": message,
                    }
                ]
            },
        }
        print(send_values, type(send_values))
        rep = self.s.post(url, data=json.dumps(send_values).encode('utf-8'), headers=header)
        if rep.status_code != 200:
            print("request failed")
            return
        return json.loads(rep.content)

    def send_markdown(self, ms):# 跳转为链接
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {
            "Content-Type": "application/json"
        }
        # python 字典若要转json，千万不能用单引号，要用双引号~@@双引号~~~！！！
        form_data = {
            "touser": "FengYu",
            "msgtype": "markdown",
            "agentid": "1000002",
            "markdown": {
                "content": ms
            },
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        print(form_data, type(form_data))
        rep = self.s.post(url, data=json.dumps(form_data).encode('utf-8'), headers=header)
        if rep.status_code != 200:
            print("request failed")
            return
        return json.loads(rep.content)




if __name__ == '__main__':
    # 图片消息模板
    # title,description,url,picurl,btntxt='阅读全文'
    wechat = WeChatPub()

    wechat.send_news(
        title='iKuuu机场签到提醒(*￣▽￣*)ブ',  # 标题
        description='\n{}\n\n{}',  # 说明文案
        to_url=r"https://ikuuu.pw/",  # 链接地址
        picurl=r"https://bing.img.run/rand_uhd.php"  # 图片地址
        # btntxt = '此处跳转'  https://www.picgo.net/image/ymwTq
    )

    wechat.send_text(title='iKuuu机场签到提醒', message='\n{}\n\n{}', url="")  # 说明文案

    # <img src="https://bing.img.run/rand_uhd.php" alt="随机获取Bing历史壁纸UHD超高清原图" />
    # <img src="https://bing.img.run/rand.php" alt="随机获取Bing历史壁纸1080P高清" />
    # <img src="https://bing.img.run/rand_1366x768.php" alt="随机获取Bing历史壁纸普清" />
    # <img src="https://bing.img.run/rand_m.php" alt="随机获取Bing历史壁纸手机版1080P高清" />
    # <img src="https://bing.img.run/uhd.php" alt="Bing每日壁纸UHD超高清原图" />
    # <img src="https://bing.img.run/1920x1080.php" alt="Bing每日壁纸1080P高清" />
    # <img src="https://bing.img.run/1366x768.php" alt="Bing每日壁纸普清" />
    # <img src="https://bing.img.run/m.php" alt="Bing每日壁纸手机版1080P高清" />
