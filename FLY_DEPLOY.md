# 🚀 Hướng dẫn Deploy lên Fly.io

## 📋 **Chuẩn bị**

### Files cần có:

- ✅ `download.py` - File chính
- ✅ `requirements.txt` - Dependencies
- ✅ `Dockerfile` - Docker configuration
- ✅ `fly.toml` - Fly.io configuration
- ✅ `README.md` - Hướng dẫn

## 🎯 **Bước 1: Cài đặt Fly.io CLI**

### **Windows:**

```bash
# Tải và cài đặt từ https://fly.io/docs/hands-on/install-flyctl/
# Hoặc sử dụng PowerShell
iwr https://fly.io/install.ps1 -useb | iex
```

### **macOS:**

```bash
curl -L https://fly.io/install.sh | sh
```

### **Linux:**

```bash
curl -L https://fly.io/install.sh | sh
```

## 🎯 **Bước 2: Đăng nhập Fly.io**

```bash
fly auth login
```

## 🎯 **Bước 3: Tạo app trên Fly.io**

```bash
fly launch
```

**Cấu hình:**

- **App name**: `video-downloader` (hoặc tên khác)
- **Region**: `sin` (Singapore) hoặc `nrt` (Tokyo)
- **Dockerfile**: `./Dockerfile`
- **Port**: `8080`

## 🎯 **Bước 4: Deploy**

```bash
fly deploy
```

## 🎯 **Bước 5: Kiểm tra**

```bash
fly status
fly logs
```

## 🎯 **Bước 6: Mở app**

```bash
fly open
```

## ⚡ **Ưu điểm Fly.io:**

- ✅ **Không sleep mode** (khác Render)
- ✅ **Global CDN** - tốc độ nhanh
- ✅ **Auto-scaling** - tự động scale
- ✅ **HTTPS tự động**
- ✅ **Custom domain miễn phí**
- ✅ **Không có lỗi issubclass** (khác Vercel)

## 🔧 **Commands hữu ích:**

### **Quản lý app:**

```bash
fly status          # Kiểm tra trạng thái
fly logs            # Xem logs
fly ssh console     # SSH vào container
fly restart         # Restart app
```

### **Deploy:**

```bash
fly deploy          # Deploy mới
fly deploy --no-cache  # Deploy không cache
```

### **Monitoring:**

```bash
fly dashboard       # Mở dashboard web
fly metrics         # Xem metrics
```

## 💰 **Pricing:**

- **Free tier**: 3 apps, 256MB RAM, shared CPU
- **Paid**: $1.94/tháng cho 256MB RAM
- **Bandwidth**: Miễn phí

## 🔧 **Troubleshooting:**

### **Lỗi thường gặp:**

1. **Build failed**: Kiểm tra Dockerfile
2. **App crashed**: Xem logs với `fly logs`
3. **Timeout**: Tăng timeout trong fly.toml

### **Debug:**

```bash
fly logs --follow   # Theo dõi logs real-time
fly ssh console     # SSH để debug
```

## 📱 **Cách sử dụng:**

### **Endpoints:**

- `GET /` - Giao diện web
- `GET /download?url=VIDEO_URL` - Tải video
- `GET /info?url=VIDEO_URL` - Thông tin video
- `GET /test` - Test server

### **Ví dụ:**

```
https://video-downloader.fly.dev/download?url=https://youtube.com/watch?v=VIDEO_ID
```

## 🚀 **Auto Deploy:**

Fly.io tự động deploy khi:

- Push code lên GitHub
- Chạy `fly deploy`

## 💡 **Tips:**

1. **Sử dụng Fly.io CLI**:

   ```bash
   fly auth login
   fly launch
   fly deploy
   ```

2. **Custom domain**:

   ```bash
   fly certs add yourdomain.com
   ```

3. **Environment variables**:
   ```bash
   fly secrets set KEY=value
   ```

## 📞 **Support:**

- [Fly.io Docs](https://fly.io/docs)
- [Fly.io Community](https://community.fly.io)
- [Docker Guide](https://fly.io/docs/getting-started/dockerfile/)
