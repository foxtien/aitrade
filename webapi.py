from flask import Flask, jsonify
import random
from datetime import datetime

app = Flask(__name__)

# 模擬即時股票報價資訊
def get_stock_price():
    # 在實際應用中，此處應當通過某種方式獲取即時股票報價資訊
    # 這裡我們只是隨機生成一些股票價格和成交量資訊
    bid_price = round(300 + 10 * (0.5 - random.random()), 2)
    ask_price = round(bid_price + 0.5, 2)
    last_price = round(bid_price + (ask_price - bid_price) * random.random(), 2)
    volume = round(1000 + 500 * (0.5 - random.random()))
    # 加入當下時間
    now =datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')

    return {
        'bid': bid_price,
        'ask': ask_price,
        'last': last_price,
        'volume': volume,
        'timestamp': timestamp
    }

# 定義Web API的路由
@app.route('/api/stock_price')
def stock_price():
    stock_price = get_stock_price()
    return jsonify(stock_price)

# 啟動Flask應用
if __name__ == '__main__':
    app.run()