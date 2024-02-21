"""
Author: Fy
cron: 0 */10 * * * ?
new Env('服务器检测');
"""

import socket
import requests
import json


def test_port(host, port):
    # 创建连接服务对象
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接超时10秒
    sk.settimeout(10)
    try:
        # 连接服务器ip或域名，端口
        # ip/域名为字符串类型str，端口为数字类型int
        # connect(),内为元组类型
        sk.connect((host, int(port)))
        print(host, port, "is ok")
    # 捕捉异常（即连接失败）
    except Exception:
        text = host, port, "is close"
        print(text)
        push(text)
    # 关闭连接
    sk.close()


def push(text):
    token = '982fe9bccbaf48cca752eb7f5ff1d976'  # 在pushpush网站中可以找到
    title = text  # 改成你要的标题内容
    content = text  # 改成你要的正文内容
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    requests.post(url, data=body, headers=headers)


if __name__ == '__main__':
    port = 8096
    host = "e5914m9946.oicp.vip"
    test_port(host, port)
    port = 8081
    test_port(host, port)
