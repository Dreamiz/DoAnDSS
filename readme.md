# 🎯 HỆ HỖ TRỢ RA QUYẾT ĐỊNH CHO NHÀ SÁNG TẠO NỘI DUNG SỐ
*(Decision Support System for Digital Content Creators)*

## 🧩 Giới thiệu
Dự án này được xây dựng nhằm hỗ trợ **nhà sáng tạo nội dung số (YouTuber, streamer, vlogger...)** theo dõi, phân tích và đưa ra **quyết định chiến lược** dựa trên dữ liệu thực tế từ YouTube API.

Hệ thống cung cấp:
- 📊 Dashboard trực quan để so sánh **50 kênh YouTube**
- 📈 Theo dõi tăng trưởng về **subscribers, views, likes, comments**
- 🤖 Phân tích và gợi ý xu hướng dựa trên **machine learning**
- ⚙️ Tự động thu thập dữ liệu định kỳ từ YouTube API

---

## 🏗️ Kiến trúc tổng quan

+---------------------+
| YouTube Data API v3 |
+---------------------+
↓
[api_youtube.py] → Thu thập dữ liệu kênh/video
↓
[database/database.py + models] → Lưu vào SQLite
↓
[Flask API] → Cung cấp dữ liệu JSON cho frontend
↓
[HTML / JS / Chart.js] → Hiển thị dashboard phân tích

yaml
Sao chép mã

---

## 📁 Cấu trúc thư mục

my_flask_app/
│
├── app.py # Flask entry point
├── api_youtube.py # Lấy dữ liệu từ YouTube API
├── requirements.txt
│
├── database/
│ ├── init.py
│ ├── database.py # Kết nối, Session, Base, Định nghĩa bảng ChannelStats
│
├── templates/
│ └── index.html # Dashboard chính
│
├── static/
│ ├── styles.css # Giao diện
│ └── js/
│ └── dashboard.js # Vẽ biểu đồ Chart.js
│
└── youtube_stats.db # CSDL SQLite

---

## 🧱 Cấu trúc bảng `ChannelStats`

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| `id` | Integer (PK) | Khóa chính |
| `channel_id` | String | ID duy nhất của kênh |
| `name` | String | Tên kênh |
| `subscribers` | Integer | Tổng số người đăng ký |
| `views` | Integer | Tổng lượt xem |
| `videos` | Integer | Tổng số video |
| `likes` | Integer | Tổng lượt thích (hoặc trung bình) |
| `comments` | Integer | Tổng bình luận |
| `timestamp` | DateTime | Thời điểm thu thập |
| `daily_subs_change` | Integer | Tăng giảm người đăng ký |
| `engagement_rate` | Float | (likes + comments) / views |
| `daily_views_change` | Integer | Tăng giảm lượt xem |

---

## ⚙️ Cài đặt & chạy thử

### 1️⃣ Cài môi trường
```bash
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
2️⃣ Thiết lập API key
Tạo file .env trong thư mục gốc:

bash
Sao chép mã
YOUTUBE_API_KEY=YOUR_API_KEY_HERE
3️⃣ Khởi tạo cơ sở dữ liệu
bash
Sao chép mã
python
>>> from database.database import init_db
>>> init_db()
4️⃣ Chạy Flask server
bash
Sao chép mã
python app.py
Mở trình duyệt tại:
👉 http://127.0.0.1:5000

📊 Giao diện dashboard
Biểu đồ tăng trưởng: subscribers & views theo thời gian

Top Channels: xếp hạng 10 kênh có hiệu suất tốt nhất

So sánh trực quan: nhiều kênh cùng lúc bằng radar chart hoặc line chart

Chỉ số hiệu quả: engagement rate, tần suất đăng video

(ảnh minh họa)

🤖 Phân tích & Machine Learning (định hướng)
Mục tiêu	Phương pháp gợi ý
Dự đoán tăng trưởng subscribers	Linear Regression / Prophet
Phân cụm kênh theo hiệu suất	K-Means Clustering
Phân loại nội dung hiệu quả cao	Decision Tree / Random Forest
Gợi ý chiến lược đăng video	Rule-based recommendation

🧠 Ý nghĩa thực tế
Hệ thống này giúp nhà sáng tạo:

Xác định thời điểm, chủ đề, và chiến lược đăng tải hiệu quả

So sánh hiệu suất giữa nhiều kênh khác nhau

Đưa ra quyết định dựa trên dữ liệu thay vì cảm tính

🚀 Hướng phát triển tương lai
 Tích hợp thêm TikTok / Instagram API

 Cho phép người dùng đăng nhập & chọn kênh cá nhân

 Xây dựng mô hình AI tự động gợi ý nội dung

 Tối ưu giao diện UI/UX với React hoặc Vue.js

 Tự động cập nhật dữ liệu qua cronjob