import mysql.connector
import requests
import pandas as pd
from datetime import datetime, timedelta
 
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine

# 設置數據庫連接信息
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'twstockdb'
USERNAME = 'tester001'
PASSWORD = 'pass1234'


def crawl_stock_history(start_date, end_date, n, m ):
    # 建立MySQL連線
    
    engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}")
    
    # 計算需要執行的迴圈次數
    myconn= engine.connect()
    mytoken= 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyMy0wMy0yNiAyMTo0OToxMCIsInVzZXJfaWQiOiJmb3h0aWVuIiwiaXAiOiIxLjIwMC43NS4xMjUifQ.AhXehQDUZnuhAsU3PqcegpneEAPvV2vq0L_6nC3730Q'
    cursor =  myconn.exec_driver_sql("SELECT COUNT(DISTINCT stock_id) FROM taiwanstockinfo ")
    
    results = cursor.fetchone()[0]
    num_loops = (results + n - 1) // n
    
    # 建立新的表格存放爬取的歷史資料
    sqlstr= "CREATE TABLE IF NOT EXISTS tawianstockprice \
                   (`date` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',\
                   	`stock_id` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_general_ci',\
                    `Trading_Volume` BIGINT(20) NULL DEFAULT NULL, 	`Trading_money` BIGINT(20) NULL DEFAULT NULL,\
                   	`open` DOUBLE NULL DEFAULT NULL, 	`max` DOUBLE NULL DEFAULT NULL,\
                   	`min` DOUBLE NULL DEFAULT NULL, 	`close` DOUBLE NULL DEFAULT NULL,\
                 	`spread` DOUBLE NULL DEFAULT NULL, 	`Trading_turnover` BIGINT(20) NULL DEFAULT NULL )\
                    COLLATE='utf8mb4_general_ci' ENGINE=InnoDB;"
    print(sqlstr)
    myconn.exec_driver_sql(sqlstr)
    
                   
    # 建立迴圈，每次取得n筆股票代號
    for i in range(num_loops):
        offset = i * n
        
        # 取得股票代號列表
        cursor=myconn.exec_driver_sql("SELECT DISTINCT stock_id FROM taiwanstockinfo LIMIT %s OFFSET %s", (n, offset))
        stock_ids = [row[0] for row in cursor.fetchall()]
        
        # 迴圈處理每一支股票
        for stock_id in stock_ids:
            print(f'start process: Stockid : {stock_id}')
            # 設定起始日期和結束日期
            current_start = start_date             
            current_end = (datetime.strptime(current_start, "%Y-%m-%d") + relativedelta(months=m)).strftime("%Y-%m-%d")

            if datetime.strptime(current_end, "%Y-%m-%d")> datetime.strptime(end_date, "%Y-%m-%d"):
                current_end = end_date
            while current_start != current_end:
                print (f" current_date:{current_start} , end_date: {current_end}")
                url = "https://api.finmindtrade.com/api/v4/data"
                payload = {
                        "dataset": "TaiwanStockPrice",
                        "data_id": stock_id ,
                        "start_date": current_start,
                        "end_date": current_end,
                        "token": mytoken, # 參考登入，獲取金鑰
                        }
                                
                # 透過API取得歷史資料
                response = requests.get(url, params=payload)
                
                # 將歷史資料轉換為DataFrame
                data = response.json()["data"]
                df = pd.DataFrame(data, columns=["date", "stock_id", "Trading_Volume", "Trading_money", \
                                                 "open", "max","min","close","spread","Trading_turnover"])
                                
                # 將歷史資料存入新的表格
                df.to_sql("taiwanstockprice", con=engine, if_exists="append", index=False)
                print(f"processd records: {len(df)}")
                # 將起始日期和結束日期加上m個月
                current_start = current_end
                current_end = (datetime.strptime(current_start, "%Y-%m-%d") + relativedelta(months=m)).strftime("%Y-%m-%d")
                if datetime.strptime(current_end, "%Y-%m-%d")> datetime.strptime(end_date, "%Y-%m-%d"):
                    current_end = end_date

                
if __name__ == '__main__':
    crawl_stock_history('1990-01-01', '2000-03-25', 20, 60 )
         