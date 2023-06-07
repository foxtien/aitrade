 
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import yfinance as yf
import mplfinance as mpf

#設定爬蟲股票代號
sid = '0050'
#設定爬蟲時間
start = datetime.datetime.now() - datetime.timedelta(days=180)
end = datetime.date.today()

from pandas_datareader import data
# 與yahoo請求，套件路徑因版本不同 
yf.pdr_override()

#df= data.get_data_yahoo("2330.tw",start="2023-01-01",end="2023-03-12")
df= data.get_data_yahoo("AAPL",start="2022-01-01",end="2023-03-12")
df = df.reset_index(level=[0])

df.index = df['Date']

print(df)

# 取adjClose至adjOpen的欄位資料
 
df_adj =  df.iloc[:,[0,1,2,3,4,6]]

my_color = mpf.make_marketcolors( up = 'r',
down = 'g',
edge = 'inherit',
wick = 'inherit',
volume   = 'inherit')
my_style  = mpf.make_mpf_style( marketcolors = my_color,figcolor ='(0.82,0.83,0.85)',gridcolor ='(0.82,0.83,0.85)')

last_data= df_adj.iloc[-1]
fig= mpf.figure(style = my_style, figsize =(12,8), facecolor =(0.82,0.83,0.85))

#print(last_data)
ax1 = fig.add_axes([0.06,0.25,0.88,0.60])
ax2 = fig.add_axes([0.06,0.15,0.88,0.10],sharex=ax1)
ax3 = fig.add_axes([0.06,0.05,0.88,0.60],sharex=ax1)
ax1.set_ylabel('price')
ax2.set_ylabel('volume')
ax3.set_ylabel('macd')
fig.text(0.50,0.94,'XXXX')
fig.text(0.12,0.90,'open/close')
#fig.text(0.14,0.89,f'{np.round(last_data["Open"],3)} / {np.round(last_data["Close"],3)}')
#fig.text(0.14,0.86,f'{last_data["Volume"]}')

mpf.plot(df_adj,type='candle',volume =True, style =my_style,mav=(5,10,20,30)) 
#mpf.plot(df_adj,ax=ax1,volume= ax2  ,type='candle' , style =my_style,mav=(5,10,20,30))
#fig.show()



