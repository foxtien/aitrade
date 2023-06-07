import pandas as pd
import yfinance as yf
import mysql.connector as mariadb
import mplfinance as mpf
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)

# 下載股價數據
# symbol = 'AAPL'
#start_date = '2015-01-01'
#end_date = '2023-03-14'
# df = yf.download(symbol, start=start_date, end=end_date)

stockid = '0050.TW'
df = pd.read_sql_query(f"SELECT * FROM twstockprice where stockid = '{stockid}'  ", conn)

df.index = df['Date']

# 定義交易成本
buy_cost = 0.01  # 買入成本 1%
sell_cost = 0.01  # 賣出成本 1%

# 計算每日股價變化率
df['daily_return'] = df['Adj Close'].pct_change()

# 定義買賣點策略
def trading_strategy(df):
    # 計算短期和長期移動平均線
    short_ma = df['Adj Close'].rolling(window=50).mean()
    long_ma = df['Adj Close'].rolling(window=200).mean()
    
    # 找出黃金交叉和死亡交叉點
    signals = pd.Series(0, index=df.index)
    signals[50:] = np.where(short_ma[50:] > long_ma[50:], 1, 0)
    signals[50:] = np.where(short_ma[50:] < long_ma[50:], -1, signals[50:])
    
    # 計算交易信號，即買入或賣出股票
    positions = signals.diff()
    
    return positions

# 計算每日持倉量
positions = trading_strategy(df)
positions = positions.fillna(0)  # 將 NaN 值填充為 0
positions = positions.astype(int)

# 計算每筆交易的成本
buy_sell = positions.diff()
buy_cost = buy_sell[buy_sell == 1] * (1 + buy_cost)  # 買入成本
sell_cost = buy_sell[buy_sell == -1] * (1 - sell_cost)  # 賣出成本
trade_cost = buy_cost + sell_cost

# 計算每日持股的收益
df['position'] = positions
df['position'] = df['position'].fillna(method='ffill')
df['returns'] = df['daily_return'] * df['position']

# 計算策略的累積收益
cumulative_returns = ((df['returns'] - trade_cost).fillna(0) + 1).cumprod()

# 計算基準的累積收益
benchmark_returns = (df['daily_return'] + 1).cumprod()

# 繪製回測結果圖表
font_path = 'C:\\ta-lib x64\\TaipeiSansTCBeta-Regular_1.ttf'  # 請將路徑替換成你儲存字型檔案的路徑
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()


plt.plot(cumulative_returns)
plt.plot(benchmark_returns)
plt.legend(['基準收益','策略收益'])
plt.title(f'{stockid}  買賣策略回測含買賣成本')
plt.xlabel('日期')
plt.ylabel('累積收益')
plt.show()
