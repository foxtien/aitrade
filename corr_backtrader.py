import pandas as pd
import matplotlib.pyplot as plt
import pyfolio as pf

# 股票代码列表
stocks = ['0055.TW', '0053.TW']

# 读取 CSV 文件并将其转换为 DataFrame，并将它们存储到字典中
data = {}
for stock in stocks:
    filename = stock  + '.csv'
    df = pd.read_csv(filename)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    data[stock] = df

# 计算每只股票的收益率
returns = {}
for stock in stocks:
    returns[stock] = data[stock]['close'].pct_change()

# 计算投资组合的收益率和风险
weights = [0.5, 0.5]  # 投资组合中每只股票的权重
portfolio_returns = (weights[0] * returns[stocks[0]]) + (weights[1] * returns[stocks[1]])
portfolio_returns.dropna(inplace=True)
portfolio_risk = portfolio_returns.std()

# 使用 PyFolio 计算投资组合的性能指标
pf.create_simple_tear_sheet(portfolio_returns)

# 绘制投资组合收益率曲线
portfolio_returns.plot(figsize=(10, 6))
plt.title('Portfolio Returns')
plt.xlabel('Date')
plt.ylabel('Returns')
plt.show()
