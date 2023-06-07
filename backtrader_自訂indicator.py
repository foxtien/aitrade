import talib
import numpy as np 
import backtrader as bt 
import pandas as pd 
import mysql.connector as mariadb 
import numpy as np  
import talib 
import mplfinance as mpf
import matplotlib.font_manager as fm 
import matplotlib.pyplot as plt
import argparse
import backtrader.analyzers as bta


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
 
   
class AJ(bt.Indicator):
    params = dict(ema1=21, atr=17, ema2=5, ema3=2)
    lines = ("AJ", "VAR2", "VAR3", "VAR4", "VAR5", "VAR6", "AK", "AD1")
    plotinfo = dict(subplot = True)
    plotlines = dict(
        AJ = dict(ls="--"),
        VAR2 = dict(_samecolor=True),
        VAR3 = dict(_samecolor=True),
        VAR4 = dict(_samecolor=True),
        VAR5 = dict(_samecolor=True),
        VAR6 = dict(_samecolor=True),
        AK = dict(_samecolor=True),
        AD1 =  dict(_samecolor=True)
    )

    def __init__(self):
        # self.l.expo的l代表从dataframe里面抽取一列的数据
 
        
        self.l.VAR2 = (self.datas[0].close * 2 + self.datas[0].high + self.datas[0].low) / 4  
        var2 = (self.datas[0].close * 2 + self.datas[0].high + self.datas[0].low) / 4
        var3 = talib.EMA(np.array(var2), timeperiod=self.params.ema1)
        self.l.VAR3 = bt.LineBuffer(var3)  
       
        #self.l.VAR3 = bt.talib.EMA(self.l.VAR2, timeperiod=self.params.ema1)
        self.l.VAR4 = bt.talib.STDDEV(self.l.VAR2, timeperiod=self.params.ema1, nbdev = 1.0)
        self.l.VAR5 = ((self.l.VAR2 - self.l.VAR3) / self.l.VAR4 * 100 + 200) / 4
        self.l.VAR6 = (bt.talib.EMA(self.l.VAR5, timeperiod=self.params.ema2) - 25) * 1.56
        self.l.AK = bt.talib.EMA(self.l.VAR6, timeperiod=self.params.ema3)* 1.22
        self.l.AD1 = bt.talib.EMA(self.l.AK, timeperiod=self.params.ema3)
        self.l.AJ = 3 * self.l.AK - 2 * self.l.AD1


# execute
class Strategy(bt.Strategy):

    # 用于记录的模板（以后可直接copy）
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    def __init__(self):
        self.AJ = AJ()
        self.close = self.data.close

    # 比较格式化的东西，每次可以直接抄
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            # 记录一下买入的信息
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: {:.2f}, Cost: {:,.2f}, Commission: {:.2f}".format(
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm
                    )
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            # 记录一下卖出的信息
            else:
                self.log(
                    "SELL EXECUTED, Price: {:.2f}, Cost: {:,.2f}, Commission: {:.2f}".format(
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm
                    )
                )

            # 记录一下过去了几个蜡烛条，也就是几个交易周期
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Cancel/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS {:,.2f}, NET {:,.2f}'.format(trade.pnl, trade.pnlcomm))

    # 执行交易的东西！！！
    def next(self):
        if not self.position:
            if self.AJ[-1] < -40 and self.AJ[0] > -40:
                #self.order = self.order_target_percent(target=0.95)
                self.buy()
        else:
            if self.AJ[-1] > 140 and self.AJ[0] < 140:
                self.order = self.sell()

# main
if __name__ == "__main__":
    
    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()

    # 提取数据再喂数据 
    
    cerebro.adddata(data_feed)

    # 添加策略
    cerebro.addstrategy(Strategy)

    # 设定开始价格
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission = 0.0001)

    # 告诉你每次买多少的股票
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 98)


    # 加入分析
    cerebro.addanalyzer(bta.TradeAnalyzer, _name = 'trades')
    cerebro.addanalyzer(bta.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bta.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bta.Returns, _name='returns')


    # 执行交易
    print("Start Portfolio Value {:,.2f}".format(cerebro.broker.getvalue()))
    back = cerebro.run()
    print("End Portfolio Value {:,.2f}".format(cerebro.broker.getvalue()))

    # 把分析的结果搞出来
    par_list = [[x.analyzers.returns.get_analysis()['rtot'],
                 x.analyzers.returns.get_analysis()['rnorm100'],
                 x.analyzers.drawdown.get_analysis()['max']['drawdown'],
                 x.analyzers.sharpe.get_analysis()['sharperatio'],
                 x.analyzers.trades.get_analysis()['total']['closed']
                 ] for x in back]
    par_df = pd.DataFrame(par_list, columns=['Total Return', 'APR', 'Drawdown', 'SharpRatio','TotalTrade'])

    print(par_df)

    # 画图 
    cerebro.plot(style='candle', barup='red', bardown='green', **{'buy':dict(color='blue'), 'sell':dict(color='black')})