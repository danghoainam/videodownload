from flask import Flask, request, jsonify, Response, stream_with_context, render_template_string
import requests
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Downloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="url"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="url"]:focus {
            border-color: #4CAF50;
            outline: none;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #45a049;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .error {
            color: red;
            margin-top: 10px;
            padding: 10px;
            background-color: #ffebee;
            border-radius: 5px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 Video Downloader</h1>
        <form id="downloadForm">
            <div class="form-group">
                <label for="url">Nhập URL YouTube:</label>
                <input type="url" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
            </div>
            <button type="submit">📥 Tải Video</button>
        </form>
        
        <div class="loading" id="loading">
            <p>⏳ Đang xử lý, vui lòng chờ...</p>
        </div>
        
        <div class="error" id="error"></div>
    </div>

    <script>
        document.getElementById('downloadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            
            // Hiển thị loading
            loading.style.display = 'block';
            error.style.display = 'none';
            
            // Chuyển hướng đến endpoint download
            window.location.href = '/api/download?url=' + encodeURIComponent(url);
        });
    </script>
</body>
</html>
    ''')

@app.route("/api/download")
def download_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400
    
    try:
        # Cấu hình khác nhau cho từng platform
        if "tiktok.com" in url.lower():
            ydl_opts = {
                "outtmpl": "%(title)s.%(ext)s",
                "format": "best",
                "nocheckcertificate": True,
                "ignoreerrors": True,
                "no_warnings": True,
                "extract_flat": False,
                "writethumbnail": False,
                "writeinfojson": False,
                "writesubtitles": False,
                "writeautomaticsub": False,
                "embedsubtitles": False,
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                "referer": "https://www.tiktok.com/",
                "cookiesfrombrowser": None,
                "extractor_args": {
                    "tiktok": {
                        "webpage_url_basename": "video"
                    }
                },
                "headers": {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                }
            }
        else:
            ydl_opts = {
                "outtmpl": "%(title)s.%(ext)s",
                "format": "best[height<=720]/best[height<=480]/best",
                "nocheckcertificate": True,
                "ignoreerrors": True,
                "no_warnings": True,
                "extract_flat": False,
                "writethumbnail": False,
                "writeinfojson": False,
                "writesubtitles": False,
                "writeautomaticsub": False,
                "embedsubtitles": False,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "referer": "https://www.youtube.com/",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-us,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
            }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        # Kiểm tra info có hợp lệ không
        if not info:
            # Thử fallback method cho TikTok
            if "tiktok.com" in url.lower():
                try:
                    fallback_opts = {
                        "quiet": True,
                        "no_warnings": True,
                        "extract_flat": True,
                        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
                    }
                    with YoutubeDL(fallback_opts) as ydl_fallback:
                        info = ydl_fallback.extract_info(url, download=False)
                except:
                    pass
            
            if not info:
                return jsonify({"error": "Không thể lấy thông tin video. URL có thể không hợp lệ hoặc video bị hạn chế."}), 400
        
        # Lấy URL trực tiếp của video
        video_url = info.get('url')
        if not video_url:
            # Thử lấy từ formats nếu không có url trực tiếp
            formats = info.get('formats', [])
            if formats:
                # Tìm format tốt nhất có video
                for fmt in formats:
                    if fmt.get('url') and fmt.get('vcodec') != 'none':
                        video_url = fmt['url']
                        break
            
            if not video_url:
                return jsonify({"error": "Không thể lấy URL video. Video có thể bị hạn chế hoặc không có format phù hợp."}), 400
        
        # Lấy thông tin về video
        title = info.get('title', 'video')
        duration = info.get('duration', 0)
        
        # Tạo response để stream video về client
        def generate():
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.youtube.com/',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            response = requests.get(video_url, stream=True, headers=headers, timeout=30)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        # Tạo headers cho download với encoding an toàn
        import urllib.parse
        safe_filename = urllib.parse.quote(title.encode('utf-8'))
        headers = {
            'Content-Disposition': f'attachment; filename*=UTF-8\'\'{safe_filename}.mp4',
            'Content-Type': 'video/mp4'
        }
        
        return Response(
            stream_with_context(generate()),
            headers=headers,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        error_msg = str(e)
        # Xử lý các lỗi phổ biến
        if "Requested format is not available" in error_msg:
            error_msg = "Video không có format phù hợp. Thử video khác hoặc video ngắn hơn."
        elif "'NoneType' object has no attribute 'get'" in error_msg:
            error_msg = "Không thể lấy thông tin video. URL có thể không hợp lệ hoặc video bị hạn chế."
        elif "Video unavailable" in error_msg:
            error_msg = "Video không khả dụng. Có thể bị xóa hoặc hạn chế."
        elif "Private video" in error_msg:
            error_msg = "Video riêng tư. Không thể tải video này."
        elif "Unable to extract sigi state" in error_msg:
            error_msg = "TikTok đã thay đổi cấu trúc. Vui lòng thử lại sau hoặc sử dụng video khác."
        elif "TikTok" in error_msg:
            error_msg = "Lỗi TikTok: " + error_msg + ". Thử video khác hoặc chờ cập nhật."
        
        return jsonify({"error": error_msg}), 500

@app.route("/api/test")
def test_vercel():
    return jsonify({
        "status": "success",
        "message": "Vercel server đang hoạt động",
        "timestamp": str(__import__('datetime').datetime.now())
    })

# Vercel serverless handler
def handler(request):
    return app(request.environ, lambda *args: None)
