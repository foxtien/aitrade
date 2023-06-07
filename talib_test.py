import pandas as pd 
import talib
import yfinance as yf
from pandas_datareader import data
import matplotlib.pyplot as plt

yf.pdr_override()

#df= data.get_data_yahoo("2330.tw",start="2023-01-01",end="2023-03-12")
df= data.get_data_yahoo("AAPL",start="2022-01-01",end="2023-03-12")
df = df.reset_index(level=[0])


df.index = df['Date']

print(df) 


 
sma = talib.SMA(df["Close"], 60)      # 簡單移動平均線 
ema = talib.EMA(df["Close"], 60)      # 指數移動平均線 
wma = talib.WMA(df["Close"], 60)      # 加權移動平均線 
trima = talib.TRIMA(df["Close"], 60)  # 三角移動平均線

plt.figure(figsize=(12,6)) 
plt.plot(df["Close"],label="close") 
plt.plot(sma,label="sma") 
plt.plot(ema,label="ema") 
plt.plot(wma,label="wma") 
plt.plot(trima,label="trima") 
plt.legend() 
plt.show()