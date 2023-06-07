import pandas as pd
import numpy as np
import mysql.connector as mariadb
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

# 下載股票價格數據




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

df = pd.read_sql_query("SELECT * FROM twstock where stockid = '1101.TW' ", conn)
df.index = df['Date']

# df = pd.read_csv('https://query1.finance.yahoo.com/v7/finance/download/TSM?period1=1262322000&period2=1611550800&interval=1d&events=history&includeAdjustedClose=true')

# 選擇日期和調整後的收盤價
df = df[['Date', 'Adj Close']]

# 設置日期作為索引並進行排序
df = df.set_index('Date')
df.index = pd.to_datetime(df.index)
df = df.sort_index()

# 繪製股票收盤價圖表
plt.plot(df['Adj Close'])
plt.xlabel('Date')
plt.ylabel('Adjusted Close Price')
plt.show()

# 將數據集拆分為訓練集和測試集
training_data = df.iloc[:int(0.8*len(df)), :]
test_data = df.iloc[int(0.8*len(df)):, :]

# 將數據集進行歸一化處理
scaler = MinMaxScaler()
training_data = scaler.fit_transform(training_data)
test_data = scaler.transform(test_data)

# 定義函數以創建時間序列數據集
def create_dataset(data, sequence_length):
    X = []
    y = []
    for i in range(len(data)-sequence_length-1):
        X.append(data[i:(i+sequence_length), 0])
        y.append(data[i+sequence_length, 0])
    return np.array(X), np.array(y)

# 定義時間序列的長度
sequence_length = 30

# 創建訓練集和測試集的時間序列數據集
X_train, y_train = create_dataset(training_data, sequence_length)
X_test, y_test = create_dataset(test_data, sequence_length)

# 轉換數據集的形狀以便於LSTM模型使用
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# 定義LSTM模型
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    tf.keras.layers.LSTM(50),
    tf.keras.layers.Dense(1)
])

# 編譯模型
model.compile(loss='mean_squared_error', optimizer='adam')

# 訓練模型
history = model.fit(X_train, y_train, epochs=50, batch_size=64, validation_split=0.1)

# 繪製訓練和驗證損失
plt.plot(history.history['loss'], label='Training Loss')

plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# 使用模型對測試集進行預測
y_pred = model.predict(X_test)

# 將預測結果進行反歸一化處理
y_pred = scaler.inverse_transform(y_pred)
y_test = scaler.inverse_transform([y_test])

# 計算模型的RMSE值
rmse = np.sqrt(np.mean(((y_pred - y_test)**2)))
print('Root Mean Squared Error: ', rmse)

# 繪製測試集的實際和預測值
plt.plot(y_test[0], label='Actual Price')
plt.plot(y_pred, label='Predicted Price')
plt.xlabel('Day')
plt.ylabel('Adjusted Close Price')
plt.legend()
plt.show()
