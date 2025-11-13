# 🎬 YouTube Channel Statistics Dashboard

Một ứng dụng dashboard trực quan giúp theo dõi **hiệu suất kênh YouTube** theo thời gian thực.  
Dữ liệu được hiển thị bằng **biểu đồ Chart.js**, cho phép lọc, gán nhãn và phân tích nhanh các kênh.

---

## 🚀 Tính năng chính

### 📊 1. Biểu đồ thống kê
- Hiển thị **Top/Bottom N kênh** có:
  - Lượt xem cao/thấp nhất  
  - Lượng người đăng ký cao/thấp nhất  
- Có thể nhập **số kênh muốn xem (N)** tùy ý, sau đó bấm nút **Toggle** để đổi giữa *Top* và *Bottom*.

### 🏷️ 2. Bảng danh sách kênh
- Hiển thị danh sách tất cả các kênh và nhãn phân loại (Final Label):
  - 🟢 **Viral** – Tăng trưởng mạnh, lan truyền tốt  
  - 🔵 **Trend** – Hiệu suất vượt xa trung bình  
  - 🟡 **Developing** – Đăng ký cao, lượt xem đang phát triển  
  - 🔴 **NotViral** – Lượt xem thấp hơn trung bình  
- Có thể lọc kênh theo thể loại (Music, Tech, Kid, Food, …)

### 🧩 3. Bộ lọc nhãn động
- Các nút filter `Viral`, `Trend`, `Developing`, `NotViral` cho phép:
  - Làm nổi bật hàng tương ứng trong bảng
  - Làm mờ các dòng còn lại
- Mỗi nhãn có màu riêng biệt, giúp quan sát nhanh xu hướng kênh.

### 💬 4. Hướng dẫn trực tiếp
- Nút **"?"** nằm trong tiêu đề cột `Final Label` hiển thị bảng giải thích nhãn qua **message box**.

---

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|-------------|------------|
| **Frontend** | HTML5, CSS3, JavaScript (Chart.js) |
| **Backend** | Python Flask |
| **Database** | SQLite / CSV Dataset |
| **Visualization** | Chart.js 4.x |
| **Template Engine** | Jinja2 |

---

## 📂 Cấu trúc thư mục

📁 my_flask_app/
│
├── venv
│
├── .env
│
├── api_youtube.py
│
├── app.py # Flask server chính
│
├── templates/
  └── index.html # Giao diện chính (Dashboard)
│
├── static/
│ ├── styles.css # File CSS
│ └── js/
│ └── dashboard.js # Script xử lý biểu đồ, filter, toggle
│
├── channel.json # Dataset kênh YouTube
│
├── database/
│ ├──__init__.py
│ └── database.py
│
├── youtube_stats.db
│
├── models.py
│
├── youtube_prediction_result.csv 
│
├── requirements.txt
│
└── README.md # Tài liệu hướng dẫn

## ⚙️ Cách chạy dự án

### 1️⃣ Cài đặt môi trường
```bash
pip install flask

python app.py

Truy cập:
👉 http://127.0.0.1:5000/