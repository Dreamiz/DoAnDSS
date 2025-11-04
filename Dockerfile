# Sử dụng image Python chính thức
FROM python:3.11-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép toàn bộ project vào container
COPY . /app

# Cài đặt các gói cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Mở cổng Flask mặc định
EXPOSE 5000

# Lệnh chạy ứng dụng Flask
CMD ["python", "app.py"]
