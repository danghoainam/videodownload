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
            window.location.href = '/download?url=' + encodeURIComponent(url);
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
            "format": "best",
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
            return jsonify({"error": "Không thể lấy URL video"}), 400
        
        title = info.get('title', 'video')
        
        def generate():
            response = requests.get(video_url, stream=True, timeout=30)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        from flask import Response, stream_with_context
        return Response(
            stream_with_context(generate()),
            headers={'Content-Disposition': f'attachment; filename="{title}.mp4"'},
            mimetype='video/mp4'
        )
        
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