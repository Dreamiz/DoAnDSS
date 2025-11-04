import sqlite3
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

# Kết nối DB
conn = sqlite3.connect("youtube_stats.db")
df = pd.read_sql_query("SELECT name, views, subscribers FROM Channel_Stats", conn)
conn.close()

# -----------------------------
# 1️⃣ Tiền xử lý
# -----------------------------
# Dùng log10 để giảm scale lệch (ví dụ 34 tỷ -> ~10.5)
df['log_views'] = np.log10(df['views'])
df['log_subs'] = np.log10(df['subscribers'])

# -----------------------------
# 2️⃣ Gắn nhãn thủ công riêng cho views và subs
# -----------------------------

n = len(df)
high_n = int(n / 3)      # khoảng 1/3 số kênh
low_n = int(n / 3)

df = df.sort_values('views', ascending=False)
df['ViewLabel'] = None
df.loc[df.nlargest(high_n, 'views').index, 'ViewLabel'] = 'HighView'
df.loc[df.nsmallest(low_n, 'views').index, 'ViewLabel'] = 'LowView'

df = df.sort_values('subscribers', ascending=False)
df['SubLabel'] = None
df.loc[df.nlargest(high_n, 'subscribers').index, 'SubLabel'] = 'HighSub'
df.loc[df.nsmallest(low_n, 'subscribers').index, 'SubLabel'] = 'LowSub'

# -----------------------------
# 3️⃣ Huấn luyện GaussianNB
# -----------------------------
X = df[['views', 'subscribers']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model_view = GaussianNB()
model_sub = GaussianNB()

# chỉ huấn luyện với mẫu có nhãn
mask_view = df['ViewLabel'].notnull()
model_view.fit(X_scaled[mask_view], df.loc[mask_view, 'ViewLabel'])
df['Pred_View'] = model_view.predict(X_scaled)

mask_sub = df['SubLabel'].notnull()
model_sub.fit(X_scaled[mask_sub], df.loc[mask_sub, 'SubLabel'])
df['Pred_Sub'] = model_sub.predict(X_scaled)

# -----------------------------
# 4️⃣ Kết hợp điều kiện cuối cùng
# -----------------------------
def combine_labels(row):
    if row['Pred_View'] == 'HighView' and row['Pred_Sub'] == 'HighSub':
        return 'Viral'
    elif row['Pred_View'] == 'HighView' and row['Pred_Sub'] == 'LowSub':
        return 'Trend'   # trend tạm thời
    elif row['Pred_View'] == 'LowView' and row['Pred_Sub'] == 'HighSub':
        return 'OutMeta'
    else:
        return 'NotViral'


df['FinalLabel'] = df.apply(combine_labels, axis=1)

# -----------------------------
# 5️⃣ Xuất kết quả
# -----------------------------
result = df[['name', 'views', 'subscribers', 'Pred_View', 'Pred_Sub', 'FinalLabel']]
print(result.sort_values('FinalLabel'))
result.to_csv("youtube_prediction_result.csv", index=False)
