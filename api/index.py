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
        .result { margin-top: 20px; padding: 15px; background-color: #f0f8ff; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 Video Downloader</h1>
        <form id="form">
            <input type="url" id="url" placeholder="https://www.youtube.com/watch?v=..." required>
            <button type="submit">📥 Tải Video</button>
        </form>
        <div id="result"></div>
    </div>
    <script>
        document.getElementById('form').addEventListener('submit', function(e) {
            e.preventDefault();
            const url = document.getElementById('url').value;
            const button = document.querySelector('button');
            const result = document.getElementById('result');
            
            button.textContent = '⏳ Đang xử lý...';
            button.disabled = true;
            result.innerHTML = '';
            
            fetch('/download?url=' + encodeURIComponent(url))
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        result.innerHTML = '<div style="color: red; padding: 10px; background-color: #ffebee; border-radius: 5px;">❌ Lỗi: ' + data.error + '</div>';
                    } else {
                        result.innerHTML = `
                            <div class="result">
                                <h3>✅ Thành công!</h3>
                                <p><strong>Tiêu đề:</strong> ${data.title}</p>
                                <p><strong>Thời lượng:</strong> ${Math.floor(data.duration/60)}:${(data.duration%60).toString().padStart(2, '0')}</p>
                                <a href="${data.url}" download="${data.title}.mp4" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">📥 Tải Video</a>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    result.innerHTML = '<div style="color: red; padding: 10px; background-color: #ffebee; border-radius: 5px;">❌ Lỗi: ' + error.message + '</div>';
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
        ydl_opts = {
            "format": "best[height<=480]/best",
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "no_warnings": True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if not info:
            return jsonify({"error": "Không thể lấy thông tin video"}), 400
        
        video_url = info.get('url')
        if not video_url:
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
        
        if duration > 600:
            return jsonify({"error": "Video quá dài. Thử video ngắn hơn."}), 400
        
        return jsonify({
            "title": title,
            "url": video_url,
            "duration": duration,
            "message": "Click vào link để tải video"
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