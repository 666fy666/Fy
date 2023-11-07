"""
Author: Fy
cron: 0 30 7,11,16,23 * * ?
new Env('和风天气');
"""
import re
import requests
from datetime import datetime
from wx import WeChatPub


def getData(address):
    key = 'f4b02e3de1034876ac83b188e8b553f9'
    if address == "浦东新" or address == "双鸭" or address == "宝山":
        address = "上海"
    else:
        pass
    url = f'https://geoapi.qweather.com/v2/city/lookup?location={address}&key={key}'
    datas = requests.get(url).json()
    # print(data)
    # print(type(datas))
    for data in datas['location']:
        if data['name'] == address:
            ID = data['id']
    url = f'https://devapi.qweather.com/v7/weather/now?location={ID}&key={key}'
    datas = requests.get(url).json()
    data_time = datas['now']['obsTime']  # 观测时间
    data_time = re.findall(r'\d+', str(data_time))
    time = re.findall(r'\d+', str(data_time))
    time = time[0] + time[1] + time[2]
    data_feelsLike = datas['now']['feelsLike']  # 体感温度
    data_text = datas['now']['text']  # 温度状态描述
    url_sun = f'https://devapi.qweather.com/v7/astronomy/sun?location={ID}&date={time}&key={key}'
    data_sun = requests.get(url_sun).json()
    data_sunrise = data_sun['sunrise']  # 日出
    data_sunrise = re.findall(r'\d+', str(data_sunrise))
    data_sunset = data_sun['sunset']  # 日落
    data_sunset = re.findall(r'\d+', str(data_sunset))
    data_sunrise[3] = list(data_sunrise[3])
    if data_sunrise[3][0] == "0":
        data_sunrise[3][0] = ""
    else:
        pass
    data_sunrise[3] = ''.join(data_sunrise[3])
    data_sunrise = data_sunrise[3] + '点' + data_sunrise[4] + '分'
    data_sunset = data_sunset[3] + '点' + data_sunset[4] + '分'
    data_time = data_time[1] + '月' + data_time[2] + '日' + data_time[3] + '点' + data_time[4] + '分'  # 观测时间
    url_daily = f'https://devapi.qweather.com/v7/air/now?location={ID}&key={key}'
    datas_daily = requests.get(url_daily).json()
    data_daily = datas_daily['now']['category']
    url_tip = f'https://devapi.qweather.com/v7/indices/1d?type=0&location={ID}&key={key}'
    datas_tip = requests.get(url_tip).json()
    data_tip = datas_tip['daily'][0]['text']
    # print(address + '  观测时间：' + data_time)
    a = address
    # print('目前天气：' + data_text.replace('雪', '雪❄').replace('雷', '雷⚡').replace('沙尘', '沙尘🌪').replace('雾',
    # '雾🌫').replace(
    # '冰雹', '冰雹🌨').replace('多云', '多云☁').replace('小雨', '小雨🌧').replace('阴', '阴🌥').replace('晴', '晴🌤')
    # + '\n' + '体感温度：' + data_feelsLike + '℃' + " 🍀")
    b = ('目前天气：' + data_text.replace('雪', '雪❄').replace('雷', '雷⚡').replace('大雨', '大雨🌧').replace('沙尘',
                                                                                                            '沙尘🌪').replace(
        '雾',
        '雾🌫').replace(
        '冰雹', '冰雹🌨').replace('多云', '多云☁').replace('小雨', '小雨🌧').replace('中雨', '中雨🌧').replace('阴',
                                                                                                            '阴🌥').replace(
        '晴',
        '晴🌤')
         + '\n' + '体感温度：' + data_feelsLike + '℃' + " 🍀")
    # print('空气质量：' + data_daily)
    c = '空气质量：' + data_daily.replace('优', '优⭐').replace('良', '良▲')
    # print('日出：' + '凌晨' + data_sunrise + '☀' + '\n' + '日落：' + '傍晚' + data_sunset + '🌙')
    d = '日出：' + '凌晨' + data_sunrise + '☀' + '\n' + '日落：' + '傍晚' + data_sunset + '🌙'
    # print(data_tip)
    e = data_tip
    now = datetime.now()
    now.isoformat()
    message = a + '\n' + str(now) + '\n' + b + '\n' + c + '\n' + d + '\n' + e
    return message


def wx_pro(info):
    tip = "https://v1.hitokoto.cn/"
    res = requests.get(tip).json()
    res = res["hitokoto"] + "    ----" + res["from"]
    wechat = WeChatPub()
    wechat.send_text(
        title='和风天气',  # 标题
        message='\n{}\n\n{}'.format(info, res),  # 内容
        purl="https://tianqi.qq.com/"
    )


def main():
    info = getData('上海')
    wx_pro(info)


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    main()
