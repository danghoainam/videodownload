from flask import Flask, request, jsonify
import requests
from yt_dlp import YoutubeDL

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Video Downloader</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
        button { background-color: #4CAF50; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 Video Downloader</h1>
        <form id="form">
            <input type="url" id="url" placeholder="https://www.youtube.com/watch?v=..." required>
            <button type="submit">📥 Tải Video</button>
        </form>
    </div>
    <script>
        document.getElementById('form').addEventListener('submit', function(e) {
            e.preventDefault();
            const url = document.getElementById('url').value;
            
            // Hiển thị loading
            const button = document.querySelector('button');
            button.textContent = '⏳ Đang xử lý...';
            button.disabled = true;
            
            // Gọi API
            fetch('/download?url=' + encodeURIComponent(url))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert('Lỗi: ' + data.error);
                    } else {
                        // Hiển thị kết quả
                        const result = document.createElement('div');
                        result.innerHTML = `
                            <h3>✅ Thành công!</h3>
                            <p><strong>Tiêu đề:</strong> ${data.title}</p>
                            <p><strong>Thời lượng:</strong> ${Math.floor(data.duration/60)}:${(data.duration%60).toString().padStart(2, '0')}</p>
                            <a href="${data.url}" download="${data.title}.mp4" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">📥 Tải Video</a>
                        `;
                        document.querySelector('.container').appendChild(result);
                    }
                })
                .catch(error => {
                    alert('Lỗi: ' + error.message);
                })
                .finally(() => {
                    button.textContent = '📥 Tải Video';
                    button.disabled = false;
                });
        });
    </script>
</body>
</html>
    '''

@app.route("/download")
def download():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400
    
    try:
        # Cấu hình tối ưu cho Vercel
        ydl_opts = {
            "format": "best[height<=480]/best",
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "extract_flat": False,
            "writethumbnail": False,
            "writeinfojson": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "embedsubtitles": False,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if not info:
            return jsonify({"error": "Không thể lấy thông tin video"}), 400
        
        video_url = info.get('url')
        if not video_url:
            # Thử lấy từ formats
            formats = info.get('formats', [])
            if formats:
                for fmt in formats:
                    if fmt.get('url') and fmt.get('vcodec') != 'none':
                        video_url = fmt['url']
                        break
            
            if not video_url:
                return jsonify({"error": "Không thể lấy URL video"}), 400
        
        title = info.get('title', 'video')
        duration = info.get('duration', 0)
        
        # Kiểm tra video quá dài (Vercel có timeout)
        if duration > 600:  # 10 phút
            return jsonify({"error": "Video quá dài. Vercel có timeout 10 giây. Thử video ngắn hơn."}), 400
        
        # Trả về URL thay vì stream (tránh timeout)
        return jsonify({
            "title": title,
            "url": video_url,
            "duration": duration,
            "message": "Click vào link để tải video"
        })
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            error_msg = "Timeout. Thử video ngắn hơn hoặc video khác."
        elif "memory" in error_msg.lower():
            error_msg = "Không đủ memory. Thử video nhỏ hơn."
        
        return jsonify({"error": error_msg}), 500

@app.route("/info")
def info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400
    
    try:
        ydl_opts = {
            "format": "best",
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "extract_flat": True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if not info:
            return jsonify({"error": "Không thể lấy thông tin video"}), 400
        
        return jsonify({
            "title": info.get('title', 'Unknown'),
            "uploader": info.get('uploader', 'Unknown'),
            "duration": info.get('duration', 0),
            "view_count": info.get('view_count', 0),
            "description": info.get('description', '')[:200] + '...' if info.get('description') else '',
            "thumbnail": info.get('thumbnail', ''),
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test")
def test():
    return jsonify({"status": "success", "message": "Vercel server đang hoạt động"})

# Vercel handler - sửa lỗi issubclass
def handler(request):
    try:
        return app(request.environ, lambda *args: None)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }