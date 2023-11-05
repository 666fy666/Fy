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
                name = "载运工具运用工程"
                local = "D314"
                timing = "15:00"
                return name, local, timing
        if self.week == 2:
            if self.hour == 9 and self.minute == 45:
                name = "交通运输前沿课程"
                local = "D214"
                timing = "10.15"
                return name, local, timing
        if self.week == 3:
            if self.hour == 12 and self.minute == 50:
                name = "交通运输工程学"
                local = "D303"
                timing = "13:20"
                return name, local, timing
            if self.hour == 14 and self.minute == 30:
                name = "机器学习"
                local = "C306"
                timing = "15:00"
                return name, local, timing
        if self.week == 4:
            if self.hour == 9 and self.minute == 25:
                name = "新思想"
                local = "J302"
                timing = "9:55"
                return name, local, timing
            if self.hour == 14 and self.minute == 30:
                name = "英语课"
                local = "D203或训2323"
                timing = "15:00"
                return name, local, timing
        if self.week == 5:
            if self.hour == 7 and self.minute == 45:
                name = "矩阵论"
                local = "F320"
                timing = "8:15"
                return name, local, timing
            if self.hour == 12 and self.minute == 50:
                name = "车辆动力学"
                local = "C202"
                timing = "13:20"
                return name, local, timing


if __name__ == '__main__':
    app = Lesson()
    app.main()
