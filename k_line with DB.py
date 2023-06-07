#%%
import backtrader as bt
import pandas as pd 
import mysql.connector as mariadb 
import numpy as np  
import talib 
import mplfinance as mpf
import matplotlib.font_manager as fm 
import matplotlib.pyplot as plt

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)
  
# query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE 1=1 and stockid in {condition} "
query = f"SELECT date,open,high,low,close,volume, `Adj Close` FROM twstockprice  where stockid= '2330.tw' and date >= '2021/01/01' "
df = pd.read_sql_query(sql=query,con=conn,index_col='date')
my_color = mpf.make_marketcolors ( up = 'r', 
                                 down = 'g',
                                 edge = 'inherit',
                                 wick ='inherit',
                                 volume = 'inherit')
my_style = mpf.make_mpf_style( marketcolors = my_color,
                              figcolor ='(0.82,0.83,0.85)',
                              gridcolor = '(0.82,0.83,0.85)'
                                )
plot_data = df.iloc[100:-1]
last_data = plot_data.iloc[-1]

fig = mpf.figure(style = my_style, figsize = (12,8), facecolor = (0.82,0.83,0.85))

ax1 = fig.add_axes([0.06,0.25,0.88,0.60])
ax2 = fig.add_axes([0.06,0.15,0.88,0.10], sharex = ax1)
ax3 = fig.add_axes([0.06,0.05,0.88,0.10], sharex = ax1)

ax1.set_ylabel('price')
ax2.set_ylabel('volume')
ax3.set_ylabel('macd')

# 繪製回測結果圖表
font_path = 'C:\\ta-lib x64\\TaipeiSansTCBeta-Regular_1.ttf'  # 請將路徑替換成你儲存字型檔案的路徑
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

fig.text(0.50,0.94,'台灣上市股票: 2330.tw')
fig.text(0.12,0.90,'開/收:')
fig.text(0.16,0.90, f'{np.round(last_data["open"],3)}/{np.round(last_data["close"],3)}' )
fig.text(0.14,0.86, 'last_data["change"]???????')
fig.text(0.22,0.86, 'pct_chage???????')
fig.text(0.12,0.86, 'last_data.name.date')
fig.text(0.40,0.90, '高:')
fig.text(0.45,0.90, f'{last_data["high"]}')
fig.text(0.40,0.86, '低:')
fig.text(0.45,0.86, f'{last_data["low"]}')
 
    

plot_data['MA5'] = talib.MA(plot_data.loc[:,"close"], 5)
plot_data['MA10'] =  talib.MA(plot_data.loc[:,"close"], 10)
plot_data['MA20'] =  talib.MA(plot_data.loc[:,"close"], 20)
plot_data['MA60'] =  talib.MA(plot_data.loc[:,"close"], 60)
 

ap_df = plot_data.loc[:,['MA5','MA10','MA20','MA60']]


ap=[] 
ap.append(mpf.make_addplot(ap_df,ax = ax1))
 
macd, signal, hist = talib.MACD(plot_data.loc[:,"close"], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
plot_data['macd-m'] =  macd
plot_data['macd-s'] =  signal
plot_data['macd-h'] = hist

macd_df = plot_data.loc[:,['macd-m','macd-s']]
 
ap.append(mpf.make_addplot(macd_df,ax = ax3))

bar_r = np.where(plot_data['macd-h'] >0 , plot_data['macd-h'],0)
bar_g = np.where(plot_data['macd-h'] <= 0 , plot_data['macd-h'],0)
ap.append(mpf.make_addplot(bar_r,type='bar',color = 'red', ax =  ax3  ))
ap.append(mpf.make_addplot(bar_g,type='bar',color = 'green', ax =  ax3  ))


mpf.plot( plot_data,
         ax = ax1,
         volume = ax2,
         addplot = ap ,
         type ='candle',
         style = my_style
)  
fig.show() 
#%%