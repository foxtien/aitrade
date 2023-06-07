import pandas as pd
import mysql.connector as mariadb 
from threading import Thread

# 建立與MariaDB的連接
conn = mariadb.connect(
    user='tester001', 
    password='pass1234', 
    host='localhost', 
    database='twstockdb'
)

cursor = conn.cursor()
# 從MySQL讀取股票代碼列表
stock_code= []
sql = "SELECT stock_id FROM taiwanstockinfo  limit 5"
cursor.execute(sql)
records = cursor.fetchall()
for result in records:
    stock_codes=stock_codes.append(result['stock_id'])
# stock_codes = [result['stock_id'] for result in cursor.fetchall()]

# 從MySQL讀取收盤價數據
close_prices = pd.DataFrame()

for code in stock_codes:
    with conn.cursor() as cursor:
        sql = f"SELECT `date`, `close` FROM `taiwanstockprice` WHERE `stock_id` = '{code}'"
        cursor.execute(sql)
        data = pd.DataFrame(cursor.fetchall())
    
    data.set_index('date', inplace=True)
    data.columns = [code]
    close_prices = pd.concat([close_prices, data], axis=1)

# 定義計算相關係數矩陣的函數
def calculate_corr_matrix(df):
    return df.corr()

# 拆分數據框，以便於每個線程處理不同的子集
num_threads = 4
subset_size = len(close_prices) // num_threads

subsets = [close_prices.iloc[i*subset_size:(i+1)*subset_size,:] for i in range(num_threads-1)]
subsets.append(close_prices.iloc[(num_threads-1)*subset_size:,:])

# 定義線程列表
threads = []

# 在每個子集上啟動一個線程來計算相關係數矩陣
for subset in subsets:
    t = Thread(target=calculate_corr_matrix, args=(subset,))
    threads.append(t)
    t.start()

# 等待所有線程完成
for t in threads:
    t.join()

# 合併所有子集的相關係數矩陣
corr_matrices = [t.result() for t in threads]
corr_matrix = pd.concat(corr_matrices)

# 選擇相關係數大於0.85和小於-0.85的相關係數
corr_matrix_filtered = corr_matrix[(corr_matrix > 0.85) | (corr_matrix < -0.85)]

# 輸出相關係數矩陣
print(corr_matrix_filtered)
