import requests
import json
import time

while True:
    try:
        response = requests.get('http://localhost:5000/api/stock_price')  # 發送HTTP GET請求
        data = json.loads(response.text)  # 解析JSON格式的API返回資料
        print(data)  # 打印即時股票資訊
    except:
        pass

    time.sleep(1)  # 暫停1秒，等待下一次更新
