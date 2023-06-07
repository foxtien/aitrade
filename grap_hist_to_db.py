import pandas as pd
from sqlalchemy import create_engine
import yfinance as yf
import datetime 

from pandas_datareader import data

 

yf.pdr_override()


# 設置數據庫連接信息
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'twstockdb'
USERNAME = 'tester001'
PASSWORD = 'pass1234'

# 創建數據庫引擎
engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}")
#stocklist  =['1101.TW', '1102.TW', '1103.TW', '1104.TW', '1108.TW', '1109.TW', '1110.TW', '1201.TW', '1203.TW', '1210.TW', '1213.TW', '1215.TW', '1216.TW', '1217.TW', '1218.TW', '1219.TW', '1220.TW', '1225.TW', '1227.TW']


 

 
target_table_name = 'twstockprice' 

myconn= engine.connect()
 
# 設定每頁的筆數
page_size = 20
start_date ="2023-03-22"
end_date   ="2023-03-24"

# 設定起始頁碼
page_number = 1
while True:
    # 計算起始資料的索引
   
    start_index = (page_number - 1) * page_size

    # 建立query
    query = f"SELECT id_tw FROM twstock_list LIMIT {start_index}, {page_size}"
    print(page_number ,query )
    # 執行query 
    cursor = myconn.exec_driver_sql(query)

    results = cursor.fetchall()

    # 如果沒有查詢結果就停止迴圈
    if len(results) == 0:
        break
     

    for xstockid in results:
            stockname = xstockid[0]
            df= data.get_data_yahoo(f'{stockname}',start=start_date,end=end_date)
            df["stockid"]=stockname

            df = df.reset_index(level=[0])

            df.index = df['Date']
            # 將DataFrame寫入MariaDB數據庫中
            df.to_sql(name=f'{target_table_name}', con=engine, if_exists='append', index=False)     
    page_number += 1

    