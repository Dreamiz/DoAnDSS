import sqlite3
import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

# -----------------------------
# 1️⃣ Kết nối DB và đọc dữ liệu
# -----------------------------
conn = sqlite3.connect("youtube_stats.db")
df = pd.read_sql_query("""
    SELECT name, category, views, subscribers
    FROM Channel_Stats
    WHERE views IS NOT NULL AND subscribers IS NOT NULL AND category IS NOT NULL
""", conn)
conn.close()

# Nếu có dòng nào dữ liệu âm hoặc 0 thì bỏ (tránh lỗi log10)
df = df[(df['views'] > 0) & (df['subscribers'] > 0)]

# Log-scale để giảm chênh lệch
df['log_views'] = np.log10(df['views'])
df['log_subs'] = np.log10(df['subscribers'])

# -----------------------------
# 2️⃣ Chạy phân tích cho từng category
# -----------------------------
all_results = []

for cat, group in df.groupby('category'):
    print(f"\n🚀 Đang xử lý category: {cat} (n={len(group)})")

    n = len(group)
    if n < 6:
        print("⚠️ Bỏ qua — dữ liệu quá ít để train")
        continue

    high_n = int(n / 3)
    low_n = int(n / 3)

    g = group.copy()
    # Gắn nhãn view
    g = g.sort_values('views', ascending=False)
    g['ViewLabel'] = None
    g.loc[g.nlargest(high_n, 'views').index, 'ViewLabel'] = 'HighView'
    g.loc[g.nsmallest(low_n, 'views').index, 'ViewLabel'] = 'LowView'

    # Gắn nhãn sub
    g = g.sort_values('subscribers', ascending=False)
    g['SubLabel'] = None
    g.loc[g.nlargest(high_n, 'subscribers').index, 'SubLabel'] = 'HighSub'
    g.loc[g.nsmallest(low_n, 'subscribers').index, 'SubLabel'] = 'LowSub'

    # Chuẩn hóa & train model
    X = g[['views', 'subscribers']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model_view = GaussianNB()
    model_sub = GaussianNB()

    mask_view = g['ViewLabel'].notnull()
    mask_sub = g['SubLabel'].notnull()

    model_view.fit(X_scaled[mask_view], g.loc[mask_view, 'ViewLabel'])
    model_sub.fit(X_scaled[mask_sub], g.loc[mask_sub, 'SubLabel'])

    g['Pred_View'] = model_view.predict(X_scaled)
    g['Pred_Sub'] = model_sub.predict(X_scaled)

    # Kết hợp nhãn
    def combine_labels(row):
        if row['Pred_View'] == 'HighView' and row['Pred_Sub'] == 'HighSub':
            return 'Viral'
        elif row['Pred_View'] == 'HighView' and row['Pred_Sub'] == 'LowSub':
            return 'Trend'
        elif row['Pred_View'] == 'LowView' and row['Pred_Sub'] == 'HighSub':
            return 'Developing'
        else:
            return 'NotViral'

    g['FinalLabel'] = g.apply(combine_labels, axis=1)
    all_results.append(g)

# -----------------------------
# 3️⃣ Gộp kết quả toàn bộ
# -----------------------------
final_df = pd.concat(all_results, ignore_index=True)
final_df = final_df[['name', 'category', 'views', 'subscribers', 'Pred_View', 'Pred_Sub', 'FinalLabel']]
final_df.to_csv("youtube_prediction_result.csv", index=False)

print("\n✅ Đã tạo xong file youtube_prediction_result.csv")
print(final_df.head(10))
