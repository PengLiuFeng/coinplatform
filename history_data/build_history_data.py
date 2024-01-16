import http.client
from typing import Any

import requests
import csv
from datetime import datetime
import time


def getData() -> None:
    request_map = {
        "instId":"LINK-USD",
        "after": "",
        "before": "",
        "bar": "",
        "limit": "100",
    }
    host = "https://www.okx.com"
    path = "/api/v5/market/history-index-candles?instId={}&limit={}".format(request_map["instId"],request_map["limit"])
    # 文件存储地址，配置就可以了，不需要创建文件
    file_path = "./{}_file.csv".format(request_map["instId"])
    mothed = "GET"
    length = 1
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        header = ["开始时间", "开盘价格", "最高价格","最低价格","收盘价格","K线状态","时间utc"]  # 替换为实际的列名
        csv_writer.writerow(header)

    while(True):
        print(f"程序第{length}次执行 , path :{path}")
        responseData = httpRequest(host,path,mothed)
        lastData = responseData[-1]
        if len(responseData) == 0:
            print("program is over")
            return
        if "after" in path :
            path = path[:-13] + lastData[0]
        else:
            path = path + "&after=" + lastData[0]
        length += 1
        for child in responseData:
            child.append(datetime.fromtimestamp(int(child[0])/1000).strftime("%Y-%m-%d %H:%M:%S"))
        with open(file_path, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(responseData)



def httpRequest(host: str ,path: str, mothed: str ) -> list:
    try:
        response = requests.get(host+path)
        if response.status_code != 200 :
            print(f"请求失败，开始休眠10秒钟:----------------")
            time.sleep(10)
            response = requests.get(host + path)
        return response.json()["data"]
    except Exception as e:
        print(f"Response 出现异常: {e}")
        print(f"请求失败 path {path}")
        print(f"请求失败，开始休眠10秒钟:----------------")
        time.sleep(10)
        response = requests.get(host + path)
        return response.json()["data"]




if __name__ == "__main__":
    print("program is start")
    getData()



