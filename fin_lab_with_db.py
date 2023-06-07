import pandas as pd
import yfinance as yf
import mysql.connector as mariadb
import mplfinance as mpf
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from finlab import dataframe
from finlab import backtest

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)
 
condition = ('2330.tw', '0050.tw','1101.tw')
query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE stockid in {condition} "

print(query)

df = pd.read_sql_query(sql=query,con=conn,index_col='date')

df_pivot = pd.pivot_table(df, values='Adj Close', index='date', columns='stockid')

close = dataframe.FinlabDataFrame(df_pivot)
position = close >= close.rolling(300).max()
backtest.sim(position, resample='M')

'''
sma  = close.average(20)

close.loc['2330.tw'].plot()
sma.loc['2330.tw'].plot()
plt.legend(['close', 'sma' ])
'''

 
