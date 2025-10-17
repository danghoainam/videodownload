# Video Downloader

Ứng dụng tải video từ YouTube, TikTok, Facebook và Instagram.

## 🚀 Deploy lên Render Free

### Bước 1: Chuẩn bị code

1. Đảm bảo có các file:
   - `download.py` (file chính)
   - `requirements.txt`
   - `Dockerfile`

### Bước 2: Tạo repository trên GitHub

1. Tạo repository mới trên GitHub
2. Upload code lên repository
3. Đảm bảo repository là public

### Bước 3: Deploy trên Render

1. Truy cập [render.com](https://render.com)
2. Đăng ký/đăng nhập tài khoản
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Cấu hình:
   - **Name**: video-downloader
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT download:app`
   - **Plan**: Free

### Bước 4: Cấu hình Environment Variables

Trong Render dashboard, thêm:

- `PORT`: 5000 (tự động)

### Bước 5: Deploy

1. Click "Create Web Service"
2. Chờ build và deploy (5-10 phút)
3. Lấy URL từ Render dashboard

## 📱 Cách sử dụng

### Endpoints:

- `GET /` - Giao diện web
- `GET /download?url=VIDEO_URL` - Tải video
- `GET /info?url=VIDEO_URL` - Thông tin video
- `GET /debug?url=VIDEO_URL` - Debug URL

### Ví dụ:

```
https://your-app.onrender.com/download?url=https://youtube.com/watch?v=VIDEO_ID
```

## ⚠️ Lưu ý Render Free

- **Sleep mode**: App sẽ sleep sau 15 phút không hoạt động
- **Cold start**: Lần đầu truy cập sau sleep sẽ chậm (30-60s)
- **Bandwidth**: Giới hạn 100GB/tháng
- **Build time**: Giới hạn 750 giờ/tháng

## 🔧 Troubleshooting

### Lỗi thường gặp:

1. **Build failed**: Kiểm tra requirements.txt
2. **App crashed**: Kiểm tra logs trong Render dashboard
3. **Timeout**: Tăng timeout trong gunicorn config

### Logs:

- Xem logs trong Render dashboard
- Check "Logs" tab để debug

## 📁 Cấu trúc file

```
├── download.py          # File chính
├── requirements.txt     # Dependencies
├── Dockerfile          # Docker config
└── README.md           # Hướng dẫn
```
