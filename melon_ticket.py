"""
Author: Fy
cron: */20 * * * * ?
new Env('melon抢票');
"""
import json
import threading

import requests


class MeLon:
    def __init__(self, id):
        self.uid = id
        self.session = requests.session()
        self.headers = {
            "User-Agent": User_Agent,
            "Cookie": Cookie,
        }
        params = {
            "pocCode": "SC0002",
            "prodId": self.uid,
            "scheduleNo": 100001,
            "sellTypeCode": "ST0001",
            "sellCondNo": "",
            "perfDate": ""
        }
        r = self.session.post("https://tkglobal.melon.com/tktapi/product/informProdSch.json?v=1", headers=self.headers,
                              params=params)
        # 检查演唱会信息，获取日期和场次
        self.name = r.json()["prodInform"]["perfMainName"]
        print(self.name)
        self.scheduleNo_list = []
        self.sellTypeCode_list = []
        self.pocCode_list = []
        self.time_list = []
        for t in range(len(r.json()["schList"])):
            self.scheduleNo_list.append(r.json()["schList"][t]["scheduleNo"])
            self.sellTypeCode_list.append(r.json()["schList"][t]["sellTypeCode"])
            self.pocCode_list.append(r.json()["schList"][t]["pocCode"])
            self.time_list.append(r.json()["schList"][t]["perfStartDay"])
        for i in range(len(r.json()["schList"])):
            print(i + 1, self.scheduleNo_list[i], self.sellTypeCode_list[i], self.pocCode_list[i], self.time_list[i])
        print("-" * 80)

    def main(self):
        # 检查同个演唱会不同场次
        i = int(input("共%s个场次,请输入序号（回车确认）：" % len(self.scheduleNo_list)))
        try:
            num_list = self.area(i - 1)
            threads = []
            for z in range(len(num_list)):
                thread = threading.Thread(target=self.mutli, args=(i - 1, num_list[z]))
                threads.append(thread)
                thread.start()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()
        except:
            self.single(i - 1)
        print("=" * 80)

    def main1(self):
        # 全部循环，暂时不用，，检查同个演唱会不同场次
        for i in range(len(self.scheduleNo_list)):
            print("开始检索第%s个场次" % int(i + 1))
            try:
                num_list = self.area(i)
                threads = []
                for z in range(len(num_list)):
                    thread = threading.Thread(target=self.mutli, args=(i, num_list[z]))
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to finish
                for thread in threads:
                    thread.join()
            except:
                self.single(i)
            print("=" * 80)

    def area(self, i):
        # 如果有区域，先检查区域总数
        params = {
            "pocCode": self.pocCode_list[i],
            "prodId": self.uid,
            "scheduleNo": self.scheduleNo_list[i]
        }
        r = self.session.post(
            "https://tkglobal.melon.com/tktapi/glb/product/getAreaMap.json?v=1&callback=getBlockGradeSeatMapCallBack",
            headers=self.headers,
            params=params)
        res = self.extract_outer_parentheses(r.text)[1:][:-1]
        json_data = json.loads(res)
        res = json_data["seatData"]["st"]
        num_list = []
        for u in range(len(res)):
            num_list.append(res[u]["sbid"])
        return num_list

    def mutli(self, i, num_list):
        try:
            # 获取到区域总数之后，检查单个区域
            params = {
                "pocCode": self.pocCode_list[i],
                "sntv": "",
                "blockTypeCode": "",
                "areaNo": "",
                "seatGradeNo": ""
            }
            r = self.session.post("https://tkglobal.melon.com/tktapi/product/seat/seatMapList.json?v=1&prodId={}"
                                  "&scheduleNo={}&blockId={}&callback=getSeatListCallBack".format(self.uid,
                                                                                                  self.scheduleNo_list[
                                                                                                      i], num_list),
                                  headers=self.headers,
                                  params=params,
                                  timeout=2)
            res = self.extract_outer_parentheses(r.text)[1:][:-1]
            json_data = json.loads(res)
            res = json_data["seatData"]["st"]
            res_list = []
            all = 0
            for x in range(len(res)):
                for y in range(len(res[x]["ss"])):
                    all += 1
                    if res[x]["ss"][y]["sl"] == "Y":
                        res_list.append(res[x]["ss"][y]["sid"])
            print(res_list)
            print("区域{}，共{}张票，共{}张余票".format(num_list, all, len(res_list)))
            if len(res_list) != 0:
                self.pushplus("区域{}，共{}张票，共{}张余票".format(num_list, all, len(res_list)))
                print("success")
            # self.buy(i, res_list)
        except:
            pass

    def single(self, i):
        try:
            # 不用选区域，全场
            params = {
                "pocCode": self.pocCode_list[i],
                "sntv": "",
                "blockTypeCode": "",
                "areaNo": ""
            }
            r = self.session.post("https://tkglobal.melon.com/tktapi/product/seat/seatMapList.json?v=1&prodId={}"
                                  "&scheduleNo={}&blockId=&callback=getSeatListCallBack".format(self.uid,
                                                                                                self.scheduleNo_list[
                                                                                                    i]),
                                  headers=self.headers,
                                  params=params,
                                  timeout=2)
            res = self.extract_outer_parentheses(r.text)[1:][:-1]
            json_data = json.loads(res)
            res = json_data["seatData"]["st"]
            res_list = []
            all = 0
            for x in range(len(res)):
                for y in range(len(res[x]["ss"])):
                    all += 1
                    if res[x]["ss"][y]["sl"] == "Y":
                        res_list.append(res[x]["ss"][y]["sid"])
            print(res_list)
            print("共{}张票，共{}张余票".format(all, len(res_list)))
            if len(res_list) != 0:
                self.pushplus("共{}张票，共{}张余票".format(all, len(res_list)))
                print("success")
            # self.buy(i, res_list)
        except:
            pass

    def buy(self, i, res_list):
        for k in range(len(res_list)):
            params = {
                "langCd": "CN",
                "prodId": self.uid,
                "pocCode": self.pocCode_list[i],
                "perfTypeCode": "GN0001",
                "perfDate": self.time_list[i],
                "scheduleNo": self.scheduleNo_list[i],
                "sellTypeCode": self.sellTypeCode_list[i],
                "sellCondNo": "",
                "perfMainName": self.name,
                "seatGradeNo": "",
                "seatGradeName": "",
                "blockId": "",
                "sntv": "",
                "blockTypeCode": "",
                "floorNo": "",
                "floorName": "",
                "areaNo": "",
                "areaName": "",
                "prodTypeCode": "PT0001",
                "flplanTypeCode": "DR0001",
                "scheduleTypeCode": "SG0001",
                "seatTypeCode": "SE0001",
                "jType": "I",
                "cardGroupId": "",
                "cardBpId": "",
                "cardMid": "",
                "rsrvStep": "",
                "zamEnabled": "0",
                "zamKey": "",
                "trafficCtrlYn": "N",
                "netfunnel_key": "",
                "stvn_view_list": "",
                "mapClickYn": "N",
                "seatId": res_list[k]
            }
            r = self.session.post(
                "https://tkglobal.melon.com/tktapi/glb/product/tickettype.json?v=1&callback=jQuery36007017432040574858_1709279692893",
                headers=self.headers,
                params=params)
            res = self.extract_outer_parentheses(r.text)[1:][:-1]
            json_data = json.loads(res)
            # print(json_data["seatGradeList"])
            data = ('[{"priceNo":10067,"seatId":"%s","clipSeatId":null,"gradeNm":"전석","seatNm":"I+열+20+번+",'
                    '"basePrice":130000,"priceName":"기본가","sejongPriceCode":null}]' % res_list[k])
            params = {
                "langCd": "CN",
                "prodId": self.uid,
                "pocCode": self.pocCode_list[i],
                "perfTypeCode": "GN0001",
                "perfDate": self.time_list[i],
                "scheduleNo": self.scheduleNo_list[i],
                "sellTypeCode": self.sellTypeCode_list[i],
                "sellCondNo": "",
                "perfMainName": self.name,
                "seatGradeNo": "",
                "seatGradeName": "",
                "blockId": "",
                "sntv": "",
                "blockTypeCode": "",
                "floorNo": "",
                "floorName": "",
                "areaNo": "",
                "areaName": "",
                "prodTypeCode": "PT0001",
                "flplanTypeCode": "DR0001",
                "scheduleTypeCode": "SG0001",
                "seatTypeCode": "SE0001",
                "jType": "I",
                "cardGroupId": "",
                "cardBpId": "",
                "cardMid": "",
                "rsrvStep": "",
                "zamEnabled": "0",
                "zamKey": "",
                "trafficCtrlYn": "N",
                "netfunnel_key": "",
                "stvn_view_list": "",
                "mapClickYn": "N",
                "seatId": res_list[k],
                "firstSeatId": res_list[k],
                "delvyTypeCode": "DV0002",
                "userName": "Feng Yu",
                "tel": 16601750698,
                "email": "fy16601750698@163.com",
                "rd2": 2,
                "bassDestntYn": "N",
                "delvyCategory": 0,
                "recv_delvy_price": 0,
                "payMethodCode": "AP0001",
                "cardCode": "FOREIGN_VISA",
                "cardCodeName": "VISA",
                "autheTypeCode": "AT0005",
                "cardQuota": 12,
                "quota": 00,
                "cashReceiptIssueCode": 0,
                "cashReceiptRegType": 0,
                "cashReceiptRegType2": 10,
                "cashReceiptRegTelNo1": "010",
                "chkAgreeAll": "on",
                "chkAgree": "on",
                "rsrvVolume": 1,
                "payAmt": 132000,
                "priceNo": 10067,
                "seatInfoListWithPriceType": data,
                "chkcapt": "g7ikPRZbz8vayTffWV/yZ7+aqm1QbaMdt7Kv9QI15BU="
            }

            r = self.session.post(
                "https://tkglobal.melon.com/tktapi/glb/reservation/save.json?v=1&callback=saveHandler",
                headers=self.headers,
                params=params)
            res = self.extract_outer_parentheses(r.text)[1:][:-1]
            json_data = json.loads(res)
            print(json_data)

    def pushplus(self, text):
        token = '982fe9bccbaf48cca752eb7f5ff1d976'  # 在pushpush网站中可以找到
        title = self.name  # 改成你要的标题内容
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

    def extract_outer_parentheses(self, res):
        # 格式化json文档
        count = 0
        start_index = None
        for i, char in enumerate(res):
            if char == '(':
                count += 1
                if count == 1:
                    start_index = i
            elif char == ')':
                count -= 1
                if count == 0:
                    return res[start_index:i + 1]
        return None


def man():
    while True:
        try:
            uid = int(input("输入演唱会prodId（回车确认）:"))
            melon = MeLon(uid)
            melon.main()
        except Exception as e:
            print(e)
            print("请输入正确prodId")

    # uid = 209431
    # uid = 209533


def auto():
    for p in range(len(uid_list)):
        try:
            melon = MeLon(uid_list[p])
            melon.main1()
        except Exception as e:
            print(e)
            print("请输入正确prodId")


if __name__ == '__main__':
    User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    Cookie = '_fwb=97CPfnmSvy5ioJe2OSyvt4.1709190982515; PCID=17091909827509437076476; TKT_POC_ID=WP19; i18next=CN; MAC_T="7dAW22rFM+FWhiEoWk88WOzwZPQipRqHJZhplYj7zzKeT10qd4LjZw9NKaLX/QS2hVIXI847gu2K+cD+UIRagQ=="; keyCookie_T=1000457631; JSESSIONID=6FCE2B88B5D6381F5857945E2FDF1D62; wcs_bt=s_322bdbd6fd48:1709199013; NetFunnel_ID=WP15'
    uid_list = ["209371", "209491"]  # iu
    # man() #手动输id
    auto()  # 自动
