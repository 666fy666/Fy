#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实现百度贴吧签到
API：
一键签到 POST https://tieba.baidu.com/tbmall/onekeySignin1
逐个签到 POST https://tieba.baidu.com/sign/add

注意事项：
1、百度贴吧0点到1点是不能够使用一键签到的，所以要逐个贴吧进行签到
"""

import os
from wx import WeChatPub

import requests
import re
import time
import json
import random

# 请求头信息，定义为全局方便重用
headers = {
    "User-Agent": "Firefox/92.0",  # 替换为你的UA
    "Referer": "https://tieba.baidu.com/",
    "Cookie": os.getenv("tieba"),  # 替换为你的cookie
}


# 从HTML中获取tbs参数和贴吧关注列表
def getTiebaInfo():
    try:
        url = "https://tieba.baidu.com/"

        # 发送请求，下载贴吧HTML页面
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        html = response.text

        # 从HTML中提取tbs参数
        tbs = getTbs(html)

        # 从HTML中提取贴吧关注列表
        forums = getAllForums(html)

        return {"forums": forums, "tbs": tbs}
    except Exception as e:
        print("获取贴吧数据失败，原因:", e)
        return None


# 用正则表达示从HTML中提取参数 tbs 的值
def getTbs(html):
    # 正则表达式学得不太好，用得有点呆板，凑合用
    match = re.search(r'PageData.tbs = "(.*)";PageData.is_iPad', html)
    if match:
        tbs = match.group(0).split('"')[1]
        return tbs
    return None


# 获取关注的贴吧列表
def getAllForums(html):
    #  _.Module.use('spage/widget/forumDirectory', {"forums": [...],"directory": {}})
    match = re.search(r'{"forums":\[.*\],"directory"', html)
    if match:
        data = match.group(0)
        forums = json.loads(data[data.find('['):data.rfind("]") + 1])
        return forums
    return None


# 逐个吧签到
def tiebaSigninOneByOne(tiebaInfo):
    # 签到接口
    signin_url = "https://tieba.baidu.com/sign/add"
    tbs = tiebaInfo.get("tbs")

    # 统计结果
    success_count = 0
    fail_count = 0

    # 签到
    for forum in tiebaInfo.get("forums"):
        # 跳过已经签到的贴吧，减少请求次数，防止验证码
        is_sign = forum.get("is_sign")
        forum_name = forum.get("forum_name")
        if is_sign == 1:
            print("{}吧已经签到,跳过".format(forum_name))
            continue

        # 构建请求数据
        sigin_data = {
            "ie": "utf-8",
            "kw": forum_name,
            "tbs": tbs,
        }

        try:
            # 发送请求签到
            response = requests.post(
                url=signin_url, data=sigin_data, headers=headers)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            content = response.json()

            # 判断签到结果，打印消息
            if content.get("no") == 0:
                success_count += 1
                print("{}吧签到成功".format(forum_name))
            else:
                fail_count += 1
                print("{}吧签到失败，失败原因：{}".format(
                    forum_name, content.get("error")))
        except Exception as e:
            fail_count += 1
            print("Error: {}吧签到发生错误，{}".format(forum_name, e))

        # 随机睡眠1-5秒，防止弹验证码，自动化不追求速度，一切求稳
        second = random.randint(1, 5)
        time.sleep(second)

    print("本次签到成功%d个，失败%d个" % (success_count, fail_count))
    info = "本次签到成功%d个，失败%d个" % (success_count, fail_count)
    tip = "https://v1.hitokoto.cn/"
    res = requests.get(tip).json()
    res = res["hitokoto"] + "    ----" + res["from"]
    wechat = WeChatPub()
    wechat.send_text(
        title='百度贴吧签到提醒(*￣▽￣*)ブ',  # 标题
        message='\n{}\n\n{}'.format(info, res),  # 内容
        purl="https://tieba.baidu.com/index.html"
    )


# 主方法
def main():
    print("-----------百度贴吧开始签到-------------")
    tiebaInfo = getTiebaInfo()
    if tiebaInfo:
        tiebaSigninOneByOne(tiebaInfo)
    else:
        print("签到失败")
    print("-----------百度贴吧签到结束-------------")


if __name__ == "__main__":
    main()
