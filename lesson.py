"""
Author: Fy
cron: 0 0 7,8,9,10,11,12,13,14,15,16,17,18 * * ?
new Env('课表');
"""
import datetime
from wx import WeChatPub


class Lesson:

    def __init__(self):
        now = datetime.datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))
        day = int(now.strftime("%d"))
        week = datetime.date(year, month, day).isoweekday()
        self.week = week
        print("今天是星期%s" % self.week)
        hour = int(now.strftime("%H"))
        minute = int(now.strftime("%M"))
        self.hour = hour
        self.minute = minute
        print(self.hour, self.minute)

    def main(self):
        try:
            name, local, timing = self.check_date()
            now = datetime.datetime.now()
            wechat = WeChatPub()
            wechat.send_text(
                title='{} 即将上课'.format(name),  # 标题
                message='详情👇\n教室: {}\n时间: {}\nweek: {}\n{}'.format
                (local, timing, "星期%s" % self.week, now.strftime("%Y-%m-%d %H:%M:%S")),  # 说明文案
                purl=r""  # 链接地址
            )
        except:
            print("该时间段无课")

    def check_date(self):
        if self.week == 1:
            if self.hour == 14 and self.minute == 30:
                name = "数据挖掘与交通大数据"
                local = "8A412"
                timing = "15:00"
                return name, local, timing
        if self.week == 3:
            if self.hour == 7 and self.minute == 40:
                name = "交通安全理论"
                local = "A403"
                timing = "8:15"
                return name, local, timing
            if self.hour == 17 and self.minute == 40:
                name = "现代检测技术"
                local = "B202"
                timing = "18:10"
                return name, local, timing
        if self.week == 4:
            if self.hour == 7 and self.minute == 40:
                name = "数据挖掘与交通大数据"
                local = "8A412"
                timing = "8:15"
                return name, local, timing


if __name__ == '__main__':
    app = Lesson()
    app.main()
