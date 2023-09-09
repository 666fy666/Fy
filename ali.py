#!/usr/bin/python
# coding=utf-8
"""
Author: Fy
cron: 0 10 0 * * ?
new Env('阿里云盘9月自动签到');
"""
import os
import traceback
from wx import WeChatPub

import requests


def post_msg(url: str, data: dict) -> bool:
    response = requests.post(url, data=data)
    code = response.status_code
    if code == 200:
        return True
    else:
        return False


def PushPlus_send(token, title: str, desp: str = '', template: str = 'markdown') -> bool:
    url = 'http://www.pushplus.plus/send'
    data = {
        'token': token,  # 用户令牌
        'title': title,  # 消息标题
        'content': desp,  # 具体消息内容，根据不同template支持不同格式
        'template': template,  # 发送消息模板
    }

    return post_msg(url, data)


def ServerChan_send(sendkey, title: str, desp: str = '') -> bool:
    url = 'https://sctapi.ftqq.com/{0}.send'.format(sendkey)
    data = {
        'title': title,  # 消息标题，必填。最大长度为 32
        'desp': desp  # 消息内容，选填。支持 Markdown语法 ，最大长度为 32KB ,消息卡片截取前 30 显示
    }

    return post_msg(url, data)


def get_access_token(token):
    access_token = ''
    try:
        url = "https://auth.aliyundrive.com/v2/account/token"

        data_dict = {
            "refresh_token": token,
            "grant_type": "refresh_token"
        }
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.aliyundrive.com",
            "pragma": "no-cache",
            "referer": "https://www.aliyundrive.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        resp = requests.post(url, json=data_dict, headers=headers)
        resp_json = resp.json()
        token = {}
        token['access_token'] = resp_json.get('access_token', "")
        token['refresh_token'] = resp_json.get('refresh_token', "")
        token['expire_time'] = resp_json.get('expire_time', "")
        print(
            f"获取得到新的access_token={token['access_token'][:10]}......,新的refresh_token={token['refresh_token']},过期时间={token['expire_time']}")
        access_token = token['access_token']
    except:
        print(f"获取异常:{traceback.format_exc()}")
    return access_token


class ALiYunPan(object):
    def __init__(self, access_token):
        # 获取JSON.parse(localStorage.getItem("token")).access_token
        # 请自行更新填写access_token，有效期7200s
        self.access_token = access_token

    def sign_in(self):
        sign_in_days_lists = []
        not_sign_in_days_lists = []

        try:
            token = self.access_token
            url = 'https://member.aliyundrive.com/v1/activity/sign_in_list'
            headers = {
                "Content-Type": "application/json",
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 D/C501C6D2-FAF6-4DA8-B65B-7B8B392901EB"
            }
            body = {}

            resp = requests.post(url, json=body, headers=headers)
            resp_text = resp.text
            resp_json = resp.json()

            # 未登录
            # {"code":"AccessTokenInvalid","message":"not login","requestId":"0a0080e216757311048316214ed958"}
            code = resp_json.get('code', '')
            if code == "AccessTokenInvalid":
                print(f"请检查token是否正确")
                self.wx_pro(f"请检查token是否正确")

            elif code is None:
                # success = resp_json.get('success', '')
                # logger.debug(f"success={success}")

                result = resp_json.get('result', {})
                sign_in_logs_list = result.get("signInLogs", [])
                sign_in_count = result.get("signInCount", 0)
                title = '阿里云盘签到提醒'
                msg = ''

                if len(sign_in_logs_list) > 0:
                    for i, sign_in_logs_dict in enumerate(sign_in_logs_list, 1):

                        status = sign_in_logs_dict.get('status', '')
                        day = sign_in_logs_dict.get('day', '')
                        isReward = sign_in_logs_dict.get('isReward', 'false')
                        if status == "":
                            print(
                                f"sign_in_logs_dict={sign_in_logs_dict}")
                            print(f"签到信息获取异常:{resp_text}")
                            self.wx_pro(f"签到信息获取异常:{resp_text}")
                        elif status == "miss":
                            # logger.warning(f"第{day}天未打卡")
                            not_sign_in_days_lists.append(day)
                        elif status == "normal":
                            reward = {}
                            if not isReward:  # 签到但未领取奖励
                                reward = self.get_reward(day)
                            else:
                                reward = sign_in_logs_dict.get('reward', {})
                            # 获取签到奖励内容
                            if reward:
                                name = reward.get('name', '')
                                description = reward.get('description', '')
                            else:
                                name = '无奖励'
                                description = ''
                            today_info = '✅' if day == sign_in_count else '☑'
                            log_info = f"{today_info}打卡第{day}天，获得奖励：**[{name}->{description}]**"
                            print(log_info)
                            msg = log_info + '\n\n' + msg
                            sign_in_days_lists.append(day)

                    log_info = f"🔥打卡进度:{sign_in_count}/{len(sign_in_logs_list)}"
                    print(log_info)
                    msg = log_info + '\n\n' + msg
                    self.wx_pro(msg)
                    if PUSH_KEY:
                        ServerChan_send(PUSH_KEY, title, msg)
                    if PUSH_PLUS_TOKEN:
                        PushPlus_send(PUSH_PLUS_TOKEN, title, msg)
                else:
                    print(f"resp_json={resp_json}")
                    self.wx_pro(resp_json)
            else:
                print(f"resp_json={resp_json}")
                # logger.debug(f"code={code}")
                self.wx_pro(resp_json)
        except:
            print(f"签到异常={traceback.format_exc()}")
            self.wx_pro(f"签到异常={traceback.format_exc()}")

    def get_reward(self, day):
        try:
            token = self.access_token
            url = 'https://member.aliyundrive.com/v1/activity/sign_in_reward'
            headers = {
                "Content-Type": "application/json",
                "Authorization": token,
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 D/C501C6D2-FAF6-4DA8-B65B-7B8B392901EB"
            }
            body = {
                'signInDay': day
            }

            resp = requests.post(url, json=body, headers=headers)
            resp_text = resp.text
            print(f"resp_json={resp_text}")

            resp_json = resp.json()
            result = resp_json.get('result', {})
            name = result.get('name', '')
            description = result.get('description', '')
            return {'name': name, 'description': description}
        except:
            print(f"获取签到奖励异常={traceback.format_exc()}")

        return {'name': 'null', 'description': 'null'}

    def wx_pro(self, info):
        tip = "https://v1.hitokoto.cn/"
        res = requests.get(tip).json()
        res = res["hitokoto"] + "    ----" + res["from"]
        wechat = WeChatPub()
        wechat.send_text(
            title='阿里云盘签到提醒(*￣▽￣*)ブ',  # 标题
            message='\n{}\n{}'.format(info, res),  # 说明文案
            purl="https://www.aliyundrive.com/sign/in?spm=aliyundrive.index.0.0.2d836f603j2wJa"
        )


def main():
    if ',' in refresh_token:
        tokens = refresh_token.split(',')
    elif '，' in refresh_token:
        tokens = refresh_token.split('，')
    else:
        tokens = [refresh_token]
    for token in tokens:
        access_token = get_access_token(token)
        if access_token:
            ali = ALiYunPan(access_token)
            ali.sign_in()
        else:
            ali = ALiYunPan(access_token)
            ali.wx_pro("refresh_token似乎过期了\n")


if __name__ == '__main__':
    PUSH_PLUS_TOKEN = ''  # push+ 微信推送的用户令牌
    # server 酱的 PUSH_KEY，兼容旧版与 Turbo 版
    PUSH_KEY = ''
    if os.getenv('PUSH_PLUS_TOKEN'):
        PUSH_PLUS_TOKEN = os.getenv('PUSH_PLUS_TOKEN')
    if os.getenv('PUSH_KEY'):
        PUSH_KEY = os.getenv('PUSH_KEY')
    # 请在阿里云盘网页端获取：JSON.parse(localStorage.getItem("token")).refresh_token
    refresh_token = os.getenv('ali_refresh_token')
    if os.getenv('ali_refresh_token'):
        refresh_token = os.getenv('ali_refresh_token')
    else:
        refresh_token = "696fdba91bfd4b3ca37b4957965934e9"
    main()
    try:
        os.remove("code.png")
    except:
        pass
