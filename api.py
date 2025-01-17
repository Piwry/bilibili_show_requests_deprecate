# -*- coding: UTF-8 -*-
import json
import os
import time
from shutil import copyfile

import requests
from requests.exceptions import Timeout

session = requests.session()


import pyttsx3
engine = pyttsx3.init()
def voice(message):
    engine.setProperty('volume', 1.0)
    engine.say(message)
    engine.runAndWait()
    engine.stop()


# 初始化
# 不想重新登录但是想改展次场次票种的话可以去 config.json 手改
# projectId 展次 screennum 场次 skunum 票种
# url 购票链接
def initConfig():
    print("让我们配置一下脚本, 请跟随提示进行操作, 如果操作失误可按Ctrl+C退出, 然后重新进入\n")
    print("首先请动手登录一次B站, 登录完成后请按回车继续\n")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-logging")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    WebDriver = webdriver.Chrome(options=options)
    WebDriver.get("https://show.bilibili.com/platform/home.html")
    WebDriver.find_element(By.CLASS_NAME, "nav-header-register").click()
    input("登录完成后请按回车继续\n")
    config["cookie"] = WebDriver.get_cookies()
    WebDriver.quit()
    print("cookie已保存")
    print(config["cookie"])
    config["bid"] = int(input("请输入该账户的UID 如10000\n"))
    config["url"] = input(
        "请输入购票链接并按回车继续, 格式例如 https://show.bilibili.com/platform/detail.html?id=72320\n"
    )
    config["projectId"] = int(config["url"][50:55])
    print("接下来输入所有想要抢的票次")
#    config["tickcnt"] =int(input("先输入总票次数量，注意超过 1 的票次请勿使用多线程\n"))
    config["tickcnt"] =int(input("先输入总票次数量，注意所有票次的购票人要求统一\n"))
    config["screennum"] =[0]*config["tickcnt"]
    config["skunum"] =[0]*config["tickcnt"]
    print(config["screennum"])
    for ii in range(config["tickcnt"]):
        print("接下来输入场次和价格的横向顺序, 输入数字, 例如第一个场次和第一个价格即为 1 1")
        config["screennum"][ii] = int(input("请输入场次顺序并按回车继续, 格式例如 1\n"))
        config["skunum"][ii] = int(input("请输入价格顺序并按回车继续, 格式例如 1\n"))
    config["count"] = int(input("请输入购票数量并按回车继续, 购票人必须提前设置且设置的人数与你填的相符, 如 1\n"))
    config["timeout"] = int(input("请输入请求超时时间并按回车继续 如 1\n"))
    config["process"] = int(input("请输入计划使用的进程数并按回车继续 如 1\n"))
    print("初始化成功\n")
    config["init"] = 1
    with open("./config.json", "w") as f:
        json.dump(config, f, indent=2)


# 配置载入
if os.path.exists("./config.json"):
    with open("./config.json", "r") as f:
        config = json.load(f)
    if config["init"] == 0:
        initConfig()
else:
    copyfile("./config_example.json", "./config.json")
    with open("./config.json", "r") as f:
        config = json.load(f)
    initConfig()


def sessionInit():
    headers = {
        "x-risk-header": "platform/pc uid/" + str(config["bid"]) +
        " deviceId/C4B85792-D2E6-44FD-83EE-A23CF2839DA0167634infoc",
        "sec-ch-ua":
        '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        "Content-Type": "application/x-www-form-urlencoded",
        "DNT": "1",
        "sec-ch-ua-mobile": "?0",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }
    session.get("https://show.bilibili.com/platform/home.html")
    cookie = requests.cookies.RequestsCookieJar()    # type: ignore
    for i in config["cookie"]:
        cookie.set(domain=i["domain"],
                   name=i["name"],
                   value=i["value"],
                   path=i["path"])
    session.cookies.update(cookie)
    session.headers.update(headers)
    print("Session初始化完成")

tot =config["tickcnt"]

def orderInfo():
    # 获取订单信息
    url = "https://show.bilibili.com/api/ticket/project/get?version=134&id=" + str(config[
        "projectId"]) + "&project_id=" + str(config["projectId"])

    response = session.request("GET", url, timeout=config["timeout"])
    #print(response.json())
    #a =input()

    config["screen_id"] =[0]*tot
    config["sku_id"] =[0]*tot
    config["pay_money"] =[0]*tot
    for ii in range(tot):
        data = response.json()
        config["screen_id"][ii] = int(data["data"]["screen_list"][config["screennum"][ii] -1]["id"])
        config["sku_id"][ii] = int(data["data"]["screen_list"][config["screennum"][ii] -1]["ticket_list"][config["skunum"][ii] -1]["id"])
        config["pay_money"][ii] = int(data["data"]["screen_list"][config["screennum"][ii] - 1]["ticket_list"][config["skunum"][ii] - 1]["price"])
    #print(config["pay_money"])
    #a =input()

    print("订单信息获取成功")
    # 获取购票人
    url = "https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId=" + str(config["projectId"])

    response = session.request("GET", url, timeout=config["timeout"])
    data = response.json()

    for i in range(0, config["count"]):
        data["data"]["list"][i]["isBuyerInfoVerified"] = True
        data["data"]["list"][i]["isBuyerValid"] = True
        config["buyer"] = data["data"]["list"]
    print("购票人信息获取成功")


def tokenGet(ii):
    # 获取token
    url = "https://show.bilibili.com/api/ticket/order/prepare?project_id=" + str(config[
        "projectId"])

    payload = "count=" + str(config["count"]) + "&order_type=1&project_id=" + str(config[
        "projectId"]) + "&screen_id=" + str(config["screen_id"][ii]) + "&sku_id=" + str(config["sku_id"][ii]) + "&token="

    response = session.request("POST",
                               url,
                               data=payload,
                               timeout=config["timeout"])
    
    #print(type(response))
    #print(response)
    #a =input()

    data = response.json()

    print(data)
    while(data["errno"] != 0):
        time.sleep(1)
        response = session.request("POST",
                               url,
                               data=payload,
                               timeout=config["timeout"])
        data = response.json()

    config["token"][ii] = data["data"]["token"]
    print("Token获取成功")


def orderCreate(ii):
    # 创建订单
    url = "https://show.bilibili.com/api/ticket/order/createV2?project_id=" + str(config["projectId"])
    print("step1") #

    #print(config)
    #a =input()

    payload = {
        "project_id": config["projectId"],
        "screen_id": config["screen_id"],
        "count": config["count"],
        "pay_money": config["pay_money"][ii] * config["count"],
        "order_type": 1,
        "timestamp": int(round(time.time() * 1000)),
        "id_bind" : 2,#
        "need_contact": 0,#
        "sku_id": config["sku_id"][ii],
        "coupon_code": "",#
        "again" : 0,#
        "token": config["token"][ii],
        "deviceId": "",
        "buyer_info": json.dumps(config["buyer"]) #
    }
 #       "buyer_info": "[{"+
 #           "\"id\":" +str(config["buyer"][0]["id"]) +","
 #           "\"name\":" +"\"" +config["buyer"][0]["name"] +"\"" +","
 #           "\"tel\":" +"\"" +config["buyer"][0]["tel"] +"\"" +","
 #           "\"personal_id\":" +"\"" +config["buyer"][0]["personal_id"] +"\"" +","
 #           "\"id_type\":" +str(config["buyer"][0]["id_type"])
 #       +"}]"
 #   }
    print(payload) #
    print("step2") #
    #a =input()
    response = session.request("POST",
                               url,
                               data=payload,
                               timeout=config["timeout"])
    
    data = response.json()
    print(data)
    print("step3") #
    if data["errno"] == 0:
        print("已成功抢到票, 请尽快支付 https://show.bilibili.com/orderlist")
        #for i in range(114):
        for i in range(11):
            voice('已抢到票, 票次为 '+str(ii+1))
        exit(0)
    elif data["errno"] == 100050:    # Token过期
        print("Token已过期! 正在重新获取")
        tokenGet()
    """
    elif data["errno"] == ?: # 验证, 具体code我忘了, 等再次遇到再加上:)
        print("请打开该下面网页, 进行手动验证!")
        tokenGet()
        print(data["data"]["shield"]["naUrl"])
        time.sleep(10)
    """
    #100079 购买人存在待付款订单，请前往支付或者取消后重新下单
    #209002, 本项目为实名观演项目，请选择购买人


def flow():
    sessionInit()
    if config["pay_money"] == 0:
        print("获取订单信息")
        orderInfo()

    config["token"] =[""]*tot
    while True:
        for ii in range(tot):
            time.sleep(0.3) # 改太快会被 ban
            #time.sleep(1)
            print("----------------------------------------------------------------")
            print("当前票次："+str(ii))
            if config["token"][ii] == "":
                print("获取token中")
            tokenGet(ii)
            print("创建订单")
            try:
                orderCreate(ii)
            except Timeout:
                print("请求超时, 可能是服务器炸了, 也有可能是你网络不好\n")
                continue
            except Exception as e:
                print(e)
                continue


# 线程
if config["process"] == 1:
    print("单线程模式")
    flow()
else:
    print("多线程模式")
    process_list = []
    exec("from multiprocessing import Process")
    for i in range(1, config["process"] + 1):
        exec("p%d = Process(target=flow)" % i)
    if __name__ == "__main__":
        for i in range(1, config["process"] + 1):
            exec("p%d.start() " % (i))
            exec("process_list.append(p%d) " % (i))
        for t in process_list:
            t.join()
