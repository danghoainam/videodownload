# 🚀 Hướng dẫn Deploy lên Vercel

## 📋 **Chuẩn bị**

### Files cần có:

- ✅ `api/index.py` - File chính (serverless function)
- ✅ `vercel.json` - Cấu hình Vercel
- ✅ `requirements.txt` - Dependencies (đơn giản)
- ✅ `runtime.txt` - Python version
- ✅ `.vercelignore` - Ignore files

## 🎯 **Bước 1: Tạo tài khoản Vercel**

1. Truy cập [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Chọn **"Continue with GitHub"** (khuyến nghị)
4. Authorize Vercel truy cập GitHub

## 🎯 **Bước 2: Upload code lên GitHub**

1. Tạo repository mới trên GitHub
2. Upload tất cả files vào repository:
   ```
   ├── download.py
   ├── vercel.json
   ├── requirements.txt
   └── README.md
   ```
3. Đảm bảo repository là **public**

## 🎯 **Bước 3: Deploy trên Vercel**

1. Truy cập [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Chọn **"Import Git Repository"**
4. Chọn repository vừa tạo
5. Cấu hình:
   - **Framework Preset**: `Other`
   - **Root Directory**: `./` (để trống)
   - **Build Command**: `pip install -r requirements.txt`
   - **Output Directory**: `./` (để trống)
6. Click **"Deploy"**

## 🎯 **Bước 4: Cấu hình Environment Variables**

Trong Vercel dashboard:

1. Vào **Settings** → **Environment Variables**
2. Thêm (nếu cần):
   - `PYTHONPATH`: `.`
   - `PORT`: `5000`

## 🎯 **Bước 5: Test Deployment**

Sau khi deploy thành công:

1. Lấy URL từ Vercel dashboard
2. Test các endpoints:
   ```
   GET https://your-app.vercel.app/
   GET https://your-app.vercel.app/test
   GET https://your-app.vercel.app/download?url=VIDEO_URL
   ```

## ⚠️ **Lưu ý Vercel**

### **Ưu điểm:**

- ✅ Không sleep mode
- ✅ Global CDN
- ✅ Auto-scaling
- ✅ HTTPS tự động
- ✅ Custom domain miễn phí

### **Giới hạn:**

- ⚠️ **Serverless functions**: 10 giây timeout
- ⚠️ **Bandwidth**: 100GB/tháng
- ⚠️ **Requests**: 100,000/tháng
- ⚠️ **Cold start**: Lần đầu có thể chậm

### **Tối ưu cho Vercel:**

- Sử dụng serverless functions
- Tối ưu code để chạy nhanh
- Tránh long-running processes

## 🔧 **Troubleshooting**

### **Lỗi thường gặp:**

1. **Build failed**: Kiểm tra requirements.txt
2. **Function timeout**: Tối ưu code
3. **Import error**: Kiểm tra dependencies

### **Debug:**

- Xem logs trong Vercel dashboard
- Check **Functions** tab
- Test local với `vercel dev`

## 📱 **Cách sử dụng**

### **Endpoints:**

- `GET /` - Giao diện web
- `GET /download?url=VIDEO_URL` - Tải video
- `GET /info?url=VIDEO_URL` - Thông tin video
- `GET /debug?url=VIDEO_URL` - Debug URL
- `GET /test` - Test server

### **Ví dụ:**

```
https://your-app.vercel.app/download?url=https://youtube.com/watch?v=VIDEO_ID
```

## 🚀 **Auto Deploy**

Vercel tự động deploy khi:

- Push code lên GitHub
- Merge pull request
- Thay đổi branch

## 💡 **Tips**

1. **Sử dụng Vercel CLI**:

   ```bash
   npm i -g vercel
   vercel login
   vercel --prod
   ```

2. **Custom domain**:

   - Vào Settings → Domains
   - Thêm domain của bạn

3. **Environment variables**:
   - Production: Settings → Environment Variables
   - Local: `.env.local` file

## 📞 **Support**

- [Vercel Docs](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
