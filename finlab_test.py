from finlab import dataframe 

import pandas as pd
import yfinance as yf
import mysql.connector as mariadb
import mplfinance as mpf
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from finlab import dataframe
from finlab import backtest
from finlab import analysis
from finlab import report

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)
 
condition = ('2330.tw', '0050.tw','1101.tw')
# query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE stockid in {condition} "
query = f"SELECT date, `Adj Close`, stockid FROM twstockprice  "
 

# df = pd.read_sql_query(sql=query,con=conn,index_col='date')

#df_pivot = pd.pivot_table(df, values='Adj Close', index='date', columns='stockid')

# df = dataframe.FinlabDataFrame(df_pivot) 

#  bFI/lFNisvDdxa4e3BmvWWWd/hPdv1M9m55Q0s5t+TqtRhnvThCuYRHBdzJscR6q#free
''' 
close = data.get('price:收盤價')
position = close >= close.rolling(300).max()

report = backtest.sim(position, resample='M')
report 
'''


def get(dataset: str, save_to_storage: bool = True):
    '''下載歷史資料

    請至[歷史資料目錄](https://ai.finlab.tw/database) 來獲得所有歷史資料的名稱，即可使用此函式來獲取歷史資料。
    假設 `save_to_storage` 為 `True` 則，程式會自動在本地複製一份，以避免重複下載大量數據。

    Args:
        dataset (str): The name of dataset.
        save_to_storage (bool): Whether to save the dataset to storage for later use.

    Returns:
        (pd.DataFrame): financial data

    Examples:

        欲下載所有上市上櫃之收盤價歷史資料，只需要使用此函式即可:

        ``` py
        from finlab import data
        close = data.get('price:收盤價')
        close
        ```

        | date       |   0015 |   0050 |   0051 |   0052 |   0053 |
        |:-----------|-------:|-------:|-------:|-------:|-------:|
        | 2007-04-23 |   9.54 |  57.85 |  32.83 |  38.4  |    nan |
        | 2007-04-24 |   9.54 |  58.1  |  32.99 |  38.65 |    nan |
        | 2007-04-25 |   9.52 |  57.6  |  32.8  |  38.59 |    nan |
        | 2007-04-26 |   9.59 |  57.7  |  32.8  |  38.6  |    nan |
        | 2007-04-27 |   9.55 |  57.5  |  32.72 |  38.4  |    nan |

    ''' 

    global universe_stocks
    global _storage

    not_available_universe_stocks = [
        'benchmark_return', 'institutional_investors_trading_all_market_summary',
        'margin_balance', 'intraday_trading_stat',
        'stock_index_price', 'stock_index_vol',
        'taiex_total_index', 'broker_info',
        'rotc_monthly_revenue', 'rotc_price',
        'world_index', 'rotc_broker_trade_record',
        'us_price', 'us_sp500',
        'us_tickers', 'security_categories',
        ]

    def refine_stock_id(ret):         
        return ret

    


    df = pd.read_sql_query(sql=query,con=conn)

    # set date as index
    if 'date' in df:
        df.set_index('date', inplace=True)

        table_name = dataset.split(':')[0]
        if table_name in ['tw_total_pmi', 'tw_total_nmi', 'tw_industry_nmi', 'tw_industry_pmi']:
            if isinstance(df.index[0], pd.Timestamp):
                close = get('price:收盤價')
                df.index = df.index.map(
                    lambda d: d if len(close.loc[d:]) == 0 or d < close.index[0] else close.loc[d:].index[0])

        # if column is stock name
        if (df.columns.str.find(' ') != -1).all():

            # remove stock names
            df.columns = df.columns.str.split(' ').str[0]

            # combine same stock history according to sid
            check_numeric_dtype = pd.api.types.is_numeric_dtype(df.values)
            if check_numeric_dtype:
                df = df.transpose().groupby(level=0).mean().transpose()
            else:
                df = df.fillna(np.nan).transpose().groupby(
                    level=0).last().transpose()
        df_pivot = pd.pivot_table(df, values='Adj Close', index='date', columns='stockid')
        df = dataframe.FinlabDataFrame(df_pivot)
        
        if table_name in ['monthly_revenue', 'rotc_monthly_revenue']:
            df = df._index_date_to_str_month()
        elif table_name in ['financial_statement', 'fundamental_features']:
            df = df._index_date_to_str_season()
 
    return refine_stock_id(df)
 

close_subset = get('price:收盤價')
print(close_subset)
