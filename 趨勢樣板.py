import pandas as pd
import yfinance as yf
import mysql.connector as mariadb
import mplfinance as mpf
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from finlab import dataframe
from finlab import backtest
from finlab import data



# 設置數據庫連接信息
HOSTNAME = 'localhost'
PORT = 3306
DATABASE = 'twstockdb'
USERNAME = 'tester001'
PASSWORD = 'pass1234'

# 建立與MariaDB的連接
conn = mariadb.connect(
    user=USERNAME,
    password=PASSWORD,
    host=HOSTNAME,
    port=PORT,
    database=DATABASE
)
 
condition = ('2330.tw', '0050.tw','1101.tw')
#query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE stockid in {condition} "
query = f"SELECT date, `Adj Close`, stockid FROM twstockprice  "
print(query)

df = pd.read_sql_query(sql=query,con=conn,index_col='date')

df_pivot = pd.pivot_table(df, values='Adj Close', index='date', columns='stockid')

close = dataframe.FinlabDataFrame(df_pivot) 



# 技術面選股(趨勢樣板) 
cond1 = ((close > close.average(200)) & (close > close.average(150)))
cond2 = (close.average(150) > close.average(200))
cond3 = close.average(200) > close.average(200).shift(25)
cond4 = ((close.average(50) > close.average(200)) & (close.average(50) > close.average(150)))
cond5 = close > close.rolling(250).min()*1.25
cond6 = close > close.rolling(250).max()*0.75
rs = close / close.shift(250)
cond7 = rs > rs.quantile_row(0.7)
cond8 = (close > close.average(50))

all_conds = [cond1 , cond2 , cond3 , cond4 , cond5 , cond6 , cond7 , cond8]

scores = sum([c.astype(int) for c in all_conds], 0)
latest_scores = scores.iloc[-1]

# 繪製回測結果圖表
font_path = 'C:\\ta-lib x64\\TaipeiSansTCBeta-Regular_1.ttf'  # 請將路徑替換成你儲存字型檔案的路徑
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.legend(['策略收益'])
 


for s in latest_scores[latest_scores == 8].index[::10]:
  print('股票代號', s)
  close[s].plot()
  plt.xlabel('日期')
  plt.ylabel('累積收益')
  plt.title(f'股票代號 {s} :   套用 finlab 超級趨勢樣板 收盤價')
  plt.show()
 

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
