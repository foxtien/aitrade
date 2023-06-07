import QuantLib as ql
import numpy as np
import datetime
import matplotlib.pyplot as plt

# 設定計算日期和日曆
calculation_date = ql.Date(27, 3, 2023)
expiry_date = ql.Date(31, 12, 2023)
ql.Settings.instance().evaluationDate = calculation_date
calendar = ql.China()

# 設定收益率曲線
risk_free_rate = 0.02
option_right = 'call'
day_count = ql.Actual365Fixed()
risk_free_curve = ql.FlatForward(calculation_date, ql.QuoteHandle(ql.SimpleQuote(risk_free_rate)), day_count)

# 繪製收益率曲線
dates = [calculation_date + ql.Period(i, ql.Years) for i in range(11)]
rates = [risk_free_curve.zeroRate(date, day_count, ql.Continuous).rate() for date in dates]
fig, axs = plt.subplots(3, 1, figsize=(10, 10))
x_values = [date.to_date() for date in dates] # 這邊要先將QuantLib日期轉換成Python datetime日期
axs[0].plot(x_values, rates)
axs[0].set_title("Risk-Free Curve")
axs[0].set_xlabel("Date")
axs[0].set_ylabel("Rate")

# 設定股票價格、股息率和波動率
underlying_price = 100
dividend_rate = 0.02
volatility = 0.2

# 設定股息曲線和波動率曲線
dividend_curve = ql.FlatForward(calculation_date, ql.QuoteHandle(ql.SimpleQuote(dividend_rate)), day_count)
volatility_curve = ql.BlackConstantVol(calculation_date, calendar, ql.QuoteHandle(ql.SimpleQuote(volatility)), day_count)

# 設定選擇權
option_type = ql.Option.Call
exercise_date = calculation_date + ql.Period(6, ql.Months)
exercise = ql.EuropeanExercise(expiry_date)
strike_price = 110
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
exercise = ql.EuropeanExercise(exercise_date)
option = ql.VanillaOption(payoff, exercise)
option_type = ql.Option.Call
 
# 計算選擇權價格
underlying_price_quote = ql.SimpleQuote(underlying_price)
underlying_price_handle = ql.QuoteHandle(underlying_price_quote)
payoff = ql.PlainVanillaPayoff(option_right, strike_price) 
option = ql.VanillaOption(payoff, exercise)
process = ql.BlackScholesProcess(underlying_price_handle, 
                                    ql.YieldTermStructureHandle(dividend_curve), 
                                    ql.YieldTermStructureHandle(risk_free_rate),
                                    ql.BlackVolTermStructureHandle(volatility))
engine = ql.AnalyticEuropeanEngine(process)
option.setPricingEngine(engine)
option_price = option.NPV()

print(f"Option price: {option_price:.2f}")

# 繪製股息率曲線
dividends = [dividend_curve.forwardRate(date, date, day_count, ql.Continuous, ql.Annual).rate() for date in dates]
axs[1].plot(x_values, dividends)
axs[1].set_title("Dividend Yield Curve")
axs[1].set_xlabel("Date")
axs[1].set_ylabel("Rate")

# 繪製波動率曲線
volatilities = [volatility_curve.blackVol(date, underlying_price) for date in dates]
axs[2].plot(x_values, volatilities)
axs[2].set_title("Volatility Curve")
axs[2].set_xlabel("Date")
axs[2].set_ylabel("Volatility")

# 在選擇權價格的位置標記出現在價值
option_date = ql.Date_todaysDate()
x_value = datetime.date(option_date.year(), option_date.month(), option_date.dayOfMonth())
y_value = option.NPV()
axs[2].annotate(f"Option Price: {y_value:.2f}", xy=(x_value, y_value), xytext=(-70, 30),
                textcoords='offset points', arrowprops=dict(arrowstyle="->"))

plt.tight_layout()
plt.show()
