import requests
import json
import concurrent.futures
import redis
import sys
from dateutil.relativedelta import relativedelta
import mariadb
from datetime import datetime, timedelta
import pandas as pd 


# 設置數據庫連接信息
HOSTNAME = 'localhost'
PORT = 3306
DATABASE = 'twstockdb'
USERNAME = 'tester001'
PASSWORD = 'pass1234'

redis_client = None 
__start_date='2022-01-01'
__end_date = '2023-03-25'
__target_table_name = 'TaiwanStockPrice'
__mytoken= 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMy0wMy0yNiAyMTo0OToxMCIsInVzZXJfaWQiOiJmb3h0aWVuIiwiaXAiOiIxLjIwMC43NS4xMjUifQ.AhXehQDUZnuhAsU3PqcegpneEAPvV2vq0L_6nC3730Q'
   

# 股票代號列表

# 定義從 MySQL 中取得股票代號的函數
def get_stocks(start_index, limit): 
     # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOSTNAME,
            port=PORT,
            database=DATABASE
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)  
    # Get Cursor
    cur = conn.cursor()     
    cur.execute(f"SELECT stock_id FROM taiwanstockinfo LIMIT {start_index}, {limit}")    
    rows = cur.fetchall()
    stocks = [row[0] for row in rows]
    conn.close 
    return stocks


# 定義爬取股票歷史股價的函數
def fetch_stock_history(stock):
    

    target_table_name = __target_table_name
    stockid = stock
    mytoken= __mytoken

    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": target_table_name,
        "data_id": stockid,
        "start_date": __start_date,
        "end_date": __end_date,
        "token": mytoken, # 參考登入，獲取金鑰
    }
    
    url = "https://api.finmindtrade.com/api/v4/data"
    response = requests.get(url, params=parameter)
    if response.status_code == 200:
        history =  response.json()["data"] 
        #print(history)
        for data in history:
            # 將每筆歷史股價資訊存入 Redis
             
            key = f"{data['stock_id']}_{data['date']}"
            value = {
                'Trading_Volume': data['Trading_Volume'],
                'Trading_money': data['Trading_money'],
                'open': data['open'],
                'max': data['max'],
                'min': data['min'],
                'close': data['close'],
                'spread': data['spread'],
                'Trading_turnover': data['Trading_turnover']
            }
            redis_client.set(key, json.dumps(value))
        print(f'{stock} history has been fetched and stored in Redis.')
    else:
        print(f'Failed to fetch {stock} history.')

def write_stock_history_to_mysql(stock):
    # 取出 Redis 中所有與 stock_id 相關的資料
    



    stock_id = stock 
    keys = redis_client.keys(f"{stock_id}_*")
    values = []
    i = 0 
    if len(keys) >0:
        try:
            threadconn = mariadb.connect(
                user=USERNAME,
                password=PASSWORD,
                host=HOSTNAME,
                port=PORT,
                database=DATABASE
            )
            cur = threadconn.cursor()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        for key in keys:
             # Connect to MariaDB Platform
            
           

            i = i+1 
            value = json.loads(redis_client.get(key))
            value['date'] = key.decode('utf-8').split('_')[1]
            values.append(value)
            date_obj = datetime.strptime(value['date'], '%Y-%m-%d').date()

            end_date_obj = date_obj + timedelta(days=1)
            # 將資料寫入 MySQL    
            sql = f"DELETE FROM {__target_table_name.lower()} WHERE stock_id = '{stock_id}' AND date = '{date_obj}'  "
            cur.execute(sql)
            reccnt = cur.rowcount
            #print(f"stock_id : {stock_id} , DateStart: {date_obj} , DateEnd: {end_date_obj} , Deleted: {reccnt}")
            sql = f"INSERT INTO {__target_table_name.lower()} (stock_id, date, Trading_Volume, Trading_money, open, max, min, close, spread, Trading_turnover) VALUES "
            str_tuple = (str(stock_id),value["date"],str(value["Trading_Volume"]),str(value["Trading_money"]),str(value["open"]),str(value["max"]),str(value["min"]),str(value["close"]),str(value["spread"]),str(value["Trading_turnover"]))
            sql = sql + " (" + ", ".join("'" + s + "'" for s in str_tuple)  + ")"
            
            cur.execute(sql)
            #print(sql)
            reccnt = cur.rowcount 
            #print(f"stock_id : {stock_id} , DateStart: {date_obj} , DateEnd: {end_date_obj} , Inserted: {reccnt}")
            threadconn.commit() 
        print(f'{stock_id} history has been written to MySQL.')
        threadconn.close()


 


def concurrent_fetch_2_redis():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交爬取任務
        futures = []
        for stock in stocks:
            futures.append(executor.submit(fetch_stock_history, stock))
        
        # 等待任務完成
        for future in concurrent.futures.as_completed(futures):
            pass

def concurrent_fetch_redis_2_db():
    # 使用多線程寫入歷史股價資訊
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交爬取任務
        futures = []
        for stock in stocks:
            futures.append(executor.submit(write_stock_history_to_mysql, stock))
        
        # 等待任務完成
        for future in concurrent.futures.as_completed(futures):
            pass

if __name__ == '__main__':
    
# 創建 Redis 客戶端
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    # engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}")

   

            
    # 每次取n筆股票代號進行爬取
    page_size =  100
    # 設定起始頁碼
    page_number = 1
     
    dflist=[]
    # 從 MySQL 中取得股票代號
    while True:
        start_index = (page_number - 1) * page_size
        stocks = get_stocks(start_index, page_size)  
        dflist.append({"page_number":page_number,"stocks":stocks})
        #print(stocks)
        if len(stocks) == 0:
            break
        else:
            #concurrent_fetch_2_redis()
            concurrent_fetch_redis_2_db()
            None
        page_number += 1
    df = pd.Series(dflist)
    
    print(df)
    


    #print(stocks) 
