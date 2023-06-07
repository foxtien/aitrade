
import pandas as pd
 
#from finlab.plot import plot_tw_stock_candles
from myfinplot import plot_tw_stock_candles
#from myfindata import indicator 
#from finlab.data import indicator
  
import numpy as np   
 
'''
overlay_func={
              'ema_10':indicator('EMA',timeperiod=10),
              'keltner_up':indicator('EMA',timeperiod=10)+2*indicator('ATR',timeperiod=10),
              'keltner_down':indicator('EMA',timeperiod=10)-2*indicator('ATR',timeperiod=10),
                                  }
                                
technical_func={
                'atr_10':indicator('ATR',timeperiod=10),
                'atr_20':indicator('ATR',timeperiod=20)
                }
 
''' 
# plot_tw_stock_candles('6104',overlay_func=overlay_func,technical_func=technical_func)

plot_tw_stock_candles('6104'  )
#plot_tw_stock_candles('6104', technical_func=technical_func )

 