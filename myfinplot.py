import pandas as pd 
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from finlab.utils import logger
import itertools

import mysql.connector as mariadb 

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)

mystock_id = '2330.tw'
# query = f"SELECT date, `Adj Close`, stockid FROM twstockprice WHERE 1=1 and stockid in {condition} "
query = f"SELECT date,open,high,low,close,volume, `Adj Close` FROM twstockprice  where stockid= '{mystock_id}'  "
df = pd.read_sql_query(sql=query,con=conn,index_col='date')



"""
Candles
"""

def str_to_indicator(s, df):
    from talib import abstract
    import talib

    params = {}
    if '(' in s:
        params = 'dict(' + s.split('(')[-1][:-1] + ')'
        params = eval(params)
    s = s.split('(')[0]

    func = getattr(abstract, s)
    real_func = getattr(talib, s)

    abstract_input = list(func.input_names.values())[0]
    if isinstance(abstract_input, str):
        abstract_input = [abstract_input]

    pos_paras = [df[k] for k in abstract_input]

    
    ret = real_func(*pos_paras, **params)

    if isinstance(ret, np.ndarray):
        ret = pd.Series(ret, index=df.index)

    if isinstance(ret, pd.Series):
        return ret.to_frame(s)
    return ret


def color_generator():
    for i in itertools.cycle(px.colors.qualitative.Plotly):
        yield i


def average(series, n):
    return series.rolling(n, min_periods=int(n / 2)).mean()


def create_bias_df(df, ma_value=20, bias_multiple=2):
    bias_df = pd.DataFrame()
    ma_col_name = f'ma{ma_value}'
    bias_df[ma_col_name] = average(df['close'], ma_value)
    std = df['close'].rolling(ma_value, min_periods=int(ma_value / 2)).std()
    bias_df['upper_band'] = bias_df[ma_col_name] + std * bias_multiple
    bias_df['lower_band'] = bias_df[ma_col_name] - std * bias_multiple
    return bias_df


def create_stoch_df(df, **kwargs):
    from talib import abstract
    kd = abstract.STOCH(df['high'], df['low'], df['close'], **kwargs)
    kd = pd.DataFrame({'k': kd[0], 'd': kd[1]}, index=df.index)
    return kd


def evaluate_to_df(node, stock_id, df):
    if callable(node):
        node = node(df)

    if isinstance(node, str):
        node = str_to_indicator(node, df)

    if isinstance(node, pd.Series):
        return node.to_frame('0')

    if isinstance(node, np.ndarray):
        return pd.Series(node, df.index).to_frame('0')

    if isinstance(node, pd.DataFrame):
        if stock_id in node.columns:
            return pd.DataFrame({'0': node[stock_id]})
        else:
            return node

    if isinstance(node, list) or isinstance(node, tuple):
        new_node = {}
        ivalue = 0
        for n in node:
            if isinstance(n, str):
                new_node[n] = n
            else:
                new_node[ivalue] = n
                ivalue += 1
        node = new_node

    if isinstance(node, dict):
        dfs = []
        for name, n in node.items():
            nn = evaluate_to_df(n, stock_id, df)
            if len(nn.columns) == 1:
                nn.columns = [name]
            dfs.append(nn)

        return pd.concat(dfs, axis=1)

    assert 0


def format_indicators(indicators, stock_id, stock_df):
    if not isinstance(indicators, list):
        indicators = [indicators]

    ret = [evaluate_to_df(i, stock_id, stock_df) for i in indicators]

    return ret


def plot_candles(stock_id, close, open_, high, low, volume, recent_days=250, resample='D', overlay_func=None,
                 technical_func=None):
    c = color_generator()
    next(c)
    next(c)

    df = (pd.DataFrame({
        'close': close.values,
        'open': open_.values,
        'high': high.values,
        'low': low.values,
        'volume': volume.values}, index=close.index).iloc[-abs(recent_days):]
    )

    if resample:
        df = df.resample(resample).agg({
            'close': 'last',
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'volume': 'sum'})

    if overlay_func is None:
        overlay_func = create_bias_df(df)

    if technical_func is None:
        technical_func = create_stoch_df(df)

    overlay_indicator = format_indicators(overlay_func, stock_id, df)

    # merge overlay indicator if it has multiple plots
    if len(overlay_indicator) > 1:
        overlay_indicator = [pd.concat(overlay_indicator, axis=1)]
        overlay_indicator[0].columns = range(len(overlay_indicator[0].columns))

    technical_indicator = format_indicators(technical_func, stock_id, df)

    # truncate recent days
    for i, d in enumerate(overlay_indicator):
        o_ind = d.iloc[-abs(recent_days):]
        if resample != 'D':
            o_ind = o_ind.reindex(df.index, method='ffill')
        overlay_indicator[i] = o_ind
    for i, d in enumerate(technical_indicator):
        t_ind = d.iloc[-abs(recent_days):]
        if resample != 'D':
            t_ind = t_ind.reindex(df.index, method='ffill')
        technical_indicator[i] = t_ind

    technical_func_num = len(technical_indicator)
    index_value = close.index

    nrows = 1 + len(technical_indicator)

    fig = make_subplots(
        rows=nrows,
        specs=[[{"secondary_y": True}]] * nrows,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4] + [0.1] * (nrows - 1))

    fig.add_trace(
        go.Bar(x=df.index, y=df.volume, opacity=0.3, name="volume", marker={'color': 'gray', 'line_width': 0}),
        row=1, col=1
    )

    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df.open,
                                 high=df.high,
                                 low=df.low,
                                 close=df.close,
                                 increasing_line_color='#ff5084',
                                 decreasing_line_color='#2bbd91',
                                 legendgroup='1',
                                 name='candle',
                                 ), row=1, col=1, secondary_y=True)

    # overlay plot
    if overlay_indicator:
        fig_overlay = px.line(overlay_indicator[0])
        for o in fig_overlay.data:
            fig.add_trace(go.Scatter(x=o['x'], y=o['y'], name=o['name'], line=dict(color=next(c)), legendgroup="1"),
                          row=1, col=1, secondary_y=True)

    fig_titles = []

    for num, tech_ind in enumerate(technical_indicator):
        fig_tech = px.line(tech_ind)
        for t in fig_tech.data:
            color = next(c)

            fig.add_trace(
                go.Scatter(x=t['x'], y=t['y'], name=t['name'], line=dict(color=color),
                           legendgroup=str(2 + num),

                           ),
                row=2 + num, col=1)

        fig_titles.append(" , ".join([t.name for t in fig_tech.data]))

    # hide holiday
    if resample == 'D':
        dt_all = pd.date_range(start=index_value[0], end=index_value[-1])
        # retrieve the dates that are in the original dataset
        dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(index_value)]
        # define dates with missing values
        dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if d not in dt_obs]
        # hide dates with no values
        fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    fig.update_layout(
        height=600 + 100 * technical_func_num,
    )

    fig.update_layout(
        yaxis1=dict(
            title="volume",
            titlefont=dict(
                color="#777"
            ),
            tickfont=dict(
                color="#777"
            ),
            range=[df.volume.min(), df.volume.max() * 2]
        ),
        yaxis2=dict(
            title="price",
            titlefont=dict(
                color="#777"
            ),
            tickfont=dict(
                color="#777"
            ),
            showgrid=False
        ),
        hovermode='x unified',
    )

    fig.update_layout(**{
        'xaxis1_rangeslider_visible': False,
        f'xaxis': dict(
            rangeselector=dict(
                buttons=list([
                    #                 dict(count=3,
                    #                      label="3m",
                    #                      step="month",
                    #                      stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
        ),
        f'xaxis{nrows}': dict(
            rangeslider=dict(
                visible=True,
                thickness=0.1,
                bgcolor='gainsboro',
            ),
            type="date",
        ),
    })

    # fig.update_traces(xaxis='x2')
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True, spikemode="across")

    fig.update_layout(showlegend=False)

    fig.update_layout({f'xaxis{i + 1}': {'title': t, 'side': 'right'} for i, t in enumerate(fig_titles)})
    fig.update_layout({f'yaxis{i * 2 + 4}': {'showticklabels': False} for i, t in enumerate(fig_titles)})
    fig.update_layout({f'yaxis{i * 2 + 4}': {'showticklabels': False} for i, t in enumerate(fig_titles)})

    fig.update_layout(plot_bgcolor="white")
    fig.update_xaxes(showline=True, linecolor='#ddd')
    fig.update_yaxes(showline=True, linecolor='#ddd')
    fig.update_yaxes(titlefont=dict(
        color="#777"
    ),
        tickfont=dict(
            color="#777"
        ))

    fig.update_layout(title={'text': f'Candlestick Plot {stock_id}', 'font': {'size': 18, 'color': 'gray'}})

    return fig


def plot_tw_stock_candles(stock_id, recent_days=400, adjust_price=False, resample='D', overlay_func=None,
                          technical_func=None):
    """繪製台股技術線圖圖組
    Args:
        stock_id (str): 台股股號，ex:`'2330'`。
        recent_days (int):取近n個交易日資料。
        adjust_price (bool):是否使用還原股價計算。
        resample (str): 技術指標價格週期，ex: `D` 代表日線, `W` 代表週線, `M` 代表月線。
        overlay_func (dict):
            K線圖輔助線，預設使用布林通道。
             ```py
             from finlab.data import indicator

             overlay_func={
                          'ema_5':indicator('EMA',timeperiod=5),
                          'ema_10':indicator('EMA',timeperiod=10),
                          'ema_20':indicator('EMA',timeperiod=20),
                          'ema_60':indicator('EMA',timeperiod=60),
                         }
             ```
        technical_func (list):
            技術指標子圖，預設使用KD技術指標單組子圖。

            設定多組技術指標：
            ```py
            from finlab.data import indicator

            k,d = indicator('STOCH')
            rsi = indicator('RSI')
            technical_func = [{'K':k,'D':d},{'RSI':rsi}]
            ```

    Returns:
        (plotly.graph_objects.Figure): 技術線圖

    Examples:
        ```py
        from finlab.plot import plot_tw_stock_candles
        from finlab.data import indicator

        overlay_func={
                      'ema_5':indicator('EMA',timeperiod=5),
                      'ema_10':indicator('EMA',timeperiod=10),
                      'ema_20':indicator('EMA',timeperiod=20),
                      'ema_60':indicator('EMA',timeperiod=60),
                     }
        k,d = indicator('STOCH')
        rsi = indicator('RSI')
        technical_func = [{'K':k,'D':d},{'RSI':rsi}]
        plot_tw_stock_candles(stock_id='2330',recent_days=600,adjust_price=False,overlay_func=overlay_func,technical_func=technical_func)
        ```
    """   
    if adjust_price:
        close = df["Adj Close"]
        
    else:
        close = df["close"] 
    open = df["open"]
    high = df["high"]
    low = df["low"]    
    volume = df["volume"]
    stock_id=mystock_id
     

    return plot_candles(stock_id, close, open, high, low, volume, recent_days=recent_days, resample=resample,
                        overlay_func=overlay_func, technical_func=technical_func)


