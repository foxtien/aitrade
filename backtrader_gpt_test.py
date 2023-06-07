import backtrader as bt
import pandas as pd 
import mysql.connector as mariadb 
import numpy as np  
 

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)
  
# query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE 1=1 and stockid in {condition} "
query = f"SELECT date,open,high,low,close,volume, `Adj Close` FROM twstockprice  where stockid= '0050.tw' and date >= '2021/01/01' "
df = pd.read_sql_query(sql=query,con=conn,index_col='date')

class MyStrategy(bt.Strategy):

    def __init__(self):
        # 設置移動平均線指標
        self.sma = bt.indicators.SimpleMovingAverage(self.data)

    def next(self):
        # 當收盤價格高於移動平均線時買入
        if self.data.close[0] > self.sma[0]:
            self.buy()

        # 當收盤價格低於移動平均線時賣出
        elif self.data.close[0] < self.sma[0]:
            self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    # 讀取歷史股價數據
    
    data = bt.feeds.PandasData(dataname=df)
    
    #df.replace([np.nan, np.inf, -np.inf], 1, inplace=True)
    #df.fillna(method='ffill', inplace=True)
    
    
    # 將股票數據添加到回測框架中
    cerebro.adddata(data)

    # 設置交易策略
    cerebro.addstrategy(MyStrategy)

    # 設置初始資金
    cerebro.broker.setcash(100000.0)

    # 設置交易手續費
    cerebro.broker.setcommission(commission=0.001)

    # 開始回測
    report = cerebro.run()
    
    # 繪製收益曲線圖
    cerebro.plot()
 


