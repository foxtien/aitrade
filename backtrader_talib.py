#%%
import backtrader as bt
import pandas as pd 
import mysql.connector as mariadb 
import numpy as np  
import talib 
import mplfinance as mpf
import matplotlib.font_manager as fm 
import matplotlib.pyplot as plt
import backtrader.analyzers as bta
import argparse

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)

stock_id = '0050.tw'
# query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE 1=1 and stockid in {condition} "
query = f"SELECT date,open,high,low,close,volume, `Adj Close` FROM twstockprice  where stockid= '{stock_id}' and date >= '2020/01/01'  and date < '2022/04/01' "
df = pd.read_sql_query(sql=query,con=conn,index_col='date')

   
class MyStrategy(bt.Strategy):

    params = (
        ('sma1', 5),
        ('sma2', 12),
        ('ma_period', 5),
        ('hold_position_days', 10 )
        
    )
    
    def __init__(self):
        self.days_in_position = 0 
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high 
        
        # self.sma = bt.indicators.SimpleMovingAverage(self.data,timeperiod=self.params.ma_period)
        self.dataclose_np = np.array(self.data_close) 
        #self.sma1 = talib.SMA(self.dataclose_np, timeperiod=self.params.sma1)
        #self.sma2 = talib.SMA(self.dataclose_np, timeperiod=self.params.sma2)
        self.ma = talib.MA(self.dataclose_np, timeperiod=self.params.ma_period)
        self.rsi = talib.RSI(self.dataclose_np, timeperiod=14)
        self.trade_analyzer = bt.analyzers.TradeAnalyzer()   
        self.sharpe_analyzer = bt.analyzers.SharpeRatio_A() 
    
        
    def next(self):
        '''
        if self.sma1[-1] > self.sma2[-1]:
            self.buy()
        elif self.sma1[-1] < self.sma2[-1]:
            self.sell()
        
        if self.rsi[-1] < 25:
            self.buy()
        elif self.rsi[-1] > 60:
            self.sell()
           
        # 當收盤價格高於移動平均線時買入
        if self.data.close[0] > self.sma[0]:
            self.buy()

        # 當收盤價格低於移動平均線時賣出
        elif self.data.close[0] < self.sma[0]:
            self.sell()
        
        # 當收盤價格高於移動平均線時買入
        if self.data.close[0] > self.ma[0]:
            self.buy()

        # 當收盤價格低於移動平均線時賣出
        elif self.data.close[0] < self.ma[0]:
            self.sell()
        ''' 

        if self.days_in_position == 0 and self.data_close[-1] <= 112:
        #if self.days_in_position == 0 and self.data_close[-2] == self.data_high[-3]:  # 前一日收盤價等於最高價時買進
            self.buy()

        elif self.days_in_position == self.params.hold_position_days :  # 持有n天後賣出
            self.sell()
            self.days_in_position = 0

        if self.position:  # 如果持有倉位，天數加1
            self.days_in_position += 1
            
            
    def stop(self):
        
        # 計算年化報酬率
        returns = self.broker.get_value() / self.broker.startingcash - 1
        trading_days = (self.datas[0].datetime.date(-1) - self.datas[0].datetime.date(0)).days
        annual_returns = (1 + returns) ** (365 / trading_days) - 1
        print('年化報酬率: {:.2%}'.format(annual_returns))
        
        # 更新交易分析器
        self.trade_analyzer.next()         
            
        # 獲取交易結果的各種統計數據
        trade_stats = self.trade_analyzer.get_analysis()
        
         
        # 輸出交易結果的各種統計數據
         
        win_times = trade_stats.get('won', {}).get('total', 0)
        lost_times = trade_stats.get('lost', {}).get('total', 0)
        total_trade= trade_stats['total']['total']
        long_trade= trade_stats.get('long', {}).get('total', 0)
        short_trade  = trade_stats.get('short', {}).get('total', 0)
        avg_pnl = trade_stats.get('pnl', {}).get('average', 0)
        
        print("Total trades:", total_trade)
        print("Number of winning trades:",  win_times)
        
        print("Number of losing trades:",   lost_times)
        if total_trade >0 :
            print("Win Rate % :",  f'{ (win_times / total_trade) * 100 }  %')
        else:
            print("Win Rate % : 0 %" )
                  
        print("Long trades:", long_trade )
        print("Short trades:", short_trade ) 
        print("Average PnL:", avg_pnl)
        
        # 获取分析结果
        sharpe_results = self.sharpe_analyzer.get_analysis() 
        # 获取年化夏普比率
        
        try:
            sharpe_ratio = sharpe_results['sharperatio']
            # 打印年化夏普比率
            print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
        except KeyError:
            sharpe_ratio = None
            print("Unable to calculate Sharpe ratio")
     
             
class My_50_Strategy(bt.Strategy):

    def __init__(self):
        # 設置移動平均線指標
        #self.sma = bt.indicators.SimpleMovingAverage(self.data,timeperiod = 5 )
        self.sma = bt.indicators.SimpleMovingAverage(self.data   )
        self.trade_analyzer = bt.analyzers.TradeAnalyzer()   
        self.sharpe_analyzer = bt.analyzers.SharpeRatio_A() 
         
        #self.addanalyzer(self.trade_analyzer) 
        

    def next(self):
        
       
        # 通知交易信息
        if self.position:
            # 如果有持仓，则通知平仓交易信息
            if self.position.size < 0:
                # 如果当前持仓是卖出，则通知平买交易信息
                trade = self.sell(size=abs(self.position.size))
                self.notify_trade(trade)
            elif self.position.size > 0:
                # 如果当前持仓是买入，则通知平卖交易信息
                trade = self.buy(size=abs(self.position.size))
                self.notify_trade(trade)
        else:
            # 當收盤價格高於移動平均線時買入
            if self.data.close[0] > self.sma[0]:
                self.notify_trade(trade)
                self.buy()

            # 當收盤價格低於移動平均線時賣出
            elif self.data.close[0] < self.sma[0]:
                self.notify_trade(trade)
                self.sell()

    def notify_trade(self, trade):
        self.trade_analyzer.notify_trade(trade)

    def stop(self):
        # 更新交易分析器
        trade_stats = self.trade_analyzer.get_analysis()
        print('交易次数:', trade_stats.total.closed)
        print('盈利次数:', trade_stats.won.total)
        print('亏损次数:', trade_stats.lost.total)
        print('胜率:', trade_stats.won.total / trade_stats.total.closed)
        print('平均获利:', trade_stats.won.pnl.average)
        print('平均亏损:', trade_stats.lost.pnl.average)
        print('最大获利:', trade_stats.won.pnl.max)
        print('最大亏损:', trade_stats.lost.pnl.max)

        # 获取分析结果
        sharpe_results = self.sharpe_analyzer.get_analysis() 
        # 获取年化夏普比率
        
        try:
            sharpe_ratio = sharpe_results['sharperatio']
            # 打印年化夏普比率
            print(f"Annualized Sharpe Ratio: {sharpe_ratio:.2f}")
        except KeyError:
            sharpe_ratio = None
            print("Unable to calculate Sharpe ratio")
        
                
class TestStrategy(bt.Strategy):
    
    def __init__(self):
        # 紀錄收盤價
        self.data_close = self.datas[0].close
        # 創建5日均線指標
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=30)
        # 創建交易分析器
        self.trade_analyzer = bt.analyzers.TradeAnalyzer()
        self.sharpe_analyzer = bt.analyzers.SharpeRatio() 

        self.returns_analyzer = bt.analyzers.AnnualReturn()
        #self.analyzers = [self.returns_analyzer,self.trade_analyzer, self.sharpe_analyzer]

    def notify_trade(self, trade):
        self.trade_analyzer.notify_trade(trade)    
        self.sharpe_analyzer.notify_trade(trade)  

    def next(self):
        # 當前沒有持倉
        if not self.position:
            # 價格上漲且在均線之上
            if self.data_close[0] > self.sma[0]:
                # 買入
                self.buy()
        # 已經持有多單
        else:
            # 價格下跌且在均線之下
            if self.data_close[0] < self.sma[0]:
                # 賣出
                self.sell()

    def stop(self):
        # 獲取交易結果的各種統計數據
        trade_stats = self.trade_analyzer.get_analysis()       

         # 獲取分析结果
        sharpe_results = self.sharpe_analyzer.get_analysis() 

        print('交易次数:', trade_stats.total.closed)
        print('盈利次数:', trade_stats.won.total)
        print('亏损次数:', trade_stats.lost.total)
        print('胜率:', (trade_stats.won.total / trade_stats.total.closed)* 100 )  
        
        # print("勝率：{:.2f}%".format(trade_stats.won.percentage))
        print("盈虧比：{:.2f}".format(trade_stats.won.pnl.average / -trade_stats.lost.pnl.average))
        
        print('平均获利:', trade_stats.won.pnl.average)
        print('平均亏损:', trade_stats.lost.pnl.average)
        print('最大获利:', trade_stats.won.pnl.max)
        print('最大亏损:', trade_stats.lost.pnl.max)
        print('最大連續獲利次數:', trade_stats.streak.won.longest)
        print('最大連續虧損次數:', trade_stats.streak.lost.longest)
        

        #print('夏普比率:', sharpe_results['sharperatio'])

        
                
class SimpleHold(bt.Strategy):
    
    def __init__(self, sma_period):
        params = (
        ('sma1', 5),
        ('sma2', 12),
        ('ma_period', 60),
        ('hold_position_days', 10 )
        )
        # 紀錄收盤價
        self.buy_price = None
        
        # 創建5日均線指標 
        '''
        TODO: bt.indicators 跟  talib.SMA 跑出結果不同 需查找 , 目前還是先用內建的
        '''
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=sma_period)
        self.dataclose_np = np.array(self.datas[0]) 
        self.tasma = talib.SMA(self.dataclose_np, timeperiod=sma_period)

        # 創建交易分析器
        self.trade_analyzer = bt.analyzers.TradeAnalyzer()

        self.sharpe_analyzer = bt.analyzers.SharpeRatio_A() 
        self.returns_analyzer = bt.analyzers.AnnualReturn()
        self.drawdown_analyzer = bt.analyzers.DrawDown()

        
        self.days_in_position = 0
        
    def notify_trade(self, trade):
        self.trade_analyzer.notify_trade(trade)    
        self.sharpe_analyzer.notify_trade(trade)
        self.returns_analyzer.notify_trade(trade)
        self.drawdown_analyzer.notify_trade(trade)

    def next(self):         
        #(self.data.close[0] > 100 or
        if  self.data.close[0] > self.sma[0] and self.buy_price is None:
            self.buy_price = self.data.close[0]
            self.days_in_position = 0
            self.buy()

        elif self.days_in_position >= 30 and self.data.close[0]> self.buy_price :
            self.sell(price=self.data.close[0])
            self.days_in_position =  0 
            self.buy_price = None            
        elif self.buy_price is not None:
            self.days_in_position += 1
            

    def stop(self):
        # 獲取交易結果的各種統計數據
        trade_stats = self.trade_analyzer.get_analysis()       

         # 获取分析结果
        sharpe_results = self.sharpe_analyzer.get_analysis() 
        # returns_result = self.returns_analyzer.get_analysis()
        drawdown_results = self.drawdown_analyzer.get_analysis()
        ''' 要加入try expet
        '''
        print('交易次數:', trade_stats.total.closed)
        print('盈利次數(越高越好):', trade_stats.won.total)
        print('虧損次數(越低越好):', trade_stats.lost.total)
        print("勝率(越高越好)：{:.2f}%".format(trade_stats.won.total / trade_stats.total.closed* 100 ))  
        print("盈虧比(越高越好)：{:.2f}".format(trade_stats.won.pnl.average / -trade_stats.lost.pnl.average))
        
        print('平均獲利(越高越好):{:.2f}'.format(trade_stats.won.pnl.average))
        print('平均虧損(越低越好):{:.2f}'.format(trade_stats.lost.pnl.average))
        print('最大獲利(越高越好):{:.2f}'.format(trade_stats.won.pnl.max))
        print('最大虧損(越低越好):{:.2f}'.format(trade_stats.lost.pnl.max))
        print('最大連續獲利次數(越高越好):', trade_stats.streak.won.longest)
        print('最大連續虧損次數(越低越好):', trade_stats.streak.lost.longest)
        #print('最大回撤：' , drawdown_results.drawdown)
        #print('最大回撤：' , drawdown_results.max.drawdown)
        for key, value in sharpe_results.items():
            print(key, value)

        #print('夏普比率:', sharpe_results.sharperatio)
        
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Backtrader SMA Strategy')
    parser.add_argument('--sma', type=int, default=30, help='SMA period')
    args = parser.parse_args()

    cerebro = bt.Cerebro()
    
    # 將dataframe轉換成backtrader的資料源
    data_feed = bt.feeds.PandasData(dataname=df)
     
    cerebro.adddata(data_feed)
    

    cerebro.addanalyzer(bta.SharpeRatio, _name='sharpe')

    # 加入策略
    cerebro.addstrategy(SimpleHold , sma_period=args.sma)
    
    # 設定初始資金和手續費
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    # 開始回測
    cerebro.run()
    
    cerebro.plot(style='candle', barup='red', bardown='green', **{'buy':dict(color='blue'), 'sell':dict(color='black')})
    #cerebro.plot()  
