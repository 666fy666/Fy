# 这是一个示例 Python 脚本。
import requests


# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


def go_cqhttp():
    """
    使用 go_cqhttp 推送消息。
    """
    url = "http://192.168.66.239:5700/send_group_msg"
    params = {
        "group_id": "340576690",
        "message": "what are you doing???????"
    }
    resp = requests.get(url=url, params=params)
    print(resp.text)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    go_cqhttp()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
