import pandas as pd
from sqlalchemy import create_engine
import yfinance as yf
import datetime 

from pandas_datareader import data


def is_hammer(df):
    # 檢查輸入的資料是否為pandas DataFrame
    if not isinstance(df, pd.DataFrame):
        raise ValueError('Input must be a pandas DataFrame.')
    
    # 檢查資料是否包含開盤價、收盤價、最高價和最低價這四欄位
    required_columns = ['Open', 'High', 'Low', 'Close']
    if not all(column in df.columns for column in required_columns):
        raise ValueError('Input must contain columns: Open, High, Low, Close.')
    
    # 計算K線上影線和下影線的長度
    df['upper_shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['lower_shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
    
    # 檢查是否符合低位锤形線的形態特徵
    is_hammer = (df['upper_shadow'] < 0.1 * df['Close']) & (df['lower_shadow'] >= 2 * df['upper_shadow'])
    return is_hammer



yf.pdr_override()

#設定爬蟲股票代號
sid = '0050'
#設定爬蟲時間
start = datetime.datetime.now() - datetime.timedelta(days=180)
end = datetime.date.today()


# 設置數據庫連接信息
HOSTNAME = 'localhost'
PORT = '3306'
DATABASE = 'twstockdb'
USERNAME = 'tester001'
PASSWORD = 'pass1234'

# 創建數據庫引擎
engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}")
#stocklist  =['1101.TW', '1102.TW', '1103.TW', '1104.TW', '1108.TW', '1109.TW', '1110.TW', '1201.TW', '1203.TW', '1210.TW', '1213.TW', '1215.TW', '1216.TW', '1217.TW', '1218.TW', '1219.TW', '1220.TW', '1225.TW', '1227.TW']
stocklist = ['2330.tw']
sid = '2330.tw'
#設定爬蟲時間
start = datetime.datetime.now() - datetime.timedelta(days=180)
end = datetime.date.today()


for xstockid in stocklist:
    df= data.get_data_yahoo(f'{xstockid}',start="2022-01-01",end="2023-03-14")
    df["stockid"]=xstockid

    df = df.reset_index(level=[0])

    df.index = df['Date']
    # 將DataFrame寫入MariaDB數據庫中
    df.to_sql(name='tsmc', con=engine, if_exists='replace', index=False)
    #df.to_sql(name='twstock', con=engine, if_exists='replace', index=False)
 