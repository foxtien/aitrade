import asyncio
import websockets
import csv
import random
from datetime import datetime
import json

# 讀取股票報價數據
tick_data = []

csv_path = "C:\\one_drive_repository\\OneDrive - xn tw\\01 Fox 工作區\\10 Python 學習\\AITrade\\2330_tick.csv"
with open(csv_path) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        tick_data.append(row)


# 模擬即時股票報價數據
async def get_stock_price(websocket, path):
    #for row in tick_data:
    while True: 
        
        # 從股票報價數據列表中隨機選擇一行數據 
        row = random.choice(tick_data)
        bid_price = float(row['deal_price'])
        ask_price = round(bid_price + 0.5, 2)
        last_price = round(bid_price + (ask_price - bid_price) * random.random(), 2)
        volume = int(row['volume'])
        stock_id = row["stock_id"]
        #timestamp = row['date'] + ' ' + row['Time']
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        stock_price = {
            'stock_id' : stock_id,
            'bid': bid_price,
            'ask': ask_price,
            'last': last_price,
            'volume': volume,
            'timestamp': timestamp
        }
        # 發送股票報價數據給所有連接的客戶端
        await websocket.send(json.dumps(stock_price))
        # 暫停一段時間（例如1秒鐘），以便下一次生成新的股票報價數據
        await asyncio.sleep(0.1)

# 啟動WebSocket服務器
start_server = websockets.serve(get_stock_price, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
