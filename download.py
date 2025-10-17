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
            window.location.href = '/download?url=' + encodeURIComponent(url);
        });
    </script>
</body>
</html>
    ''')

@app.route("/download")
def download_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400
    
    try:
        ydl_opts = {
            "outtmpl": "%(title)s.%(ext)s",
            "format": "best[height<=720]/best[height<=480]/best",  # Thử nhiều format
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "no_warnings": True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        # Kiểm tra info có hợp lệ không
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
            response = requests.get(video_url, stream=True)
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
        
        return jsonify({"error": error_msg}), 500

@app.route("/info")
def get_video_info():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400
    
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        # Kiểm tra info có hợp lệ không
        if not info:
            return jsonify({"error": "Không thể lấy thông tin video. URL có thể không hợp lệ hoặc video bị hạn chế."}), 400
        
        # Lấy thông tin cơ bản
        title = info.get('title', 'Unknown')
        duration = info.get('duration', 0)
        uploader = info.get('uploader', 'Unknown')
        
        # Lấy danh sách format có sẵn
        formats = info.get('formats', [])
        available_formats = []
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('url'):
                available_formats.append({
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'resolution': fmt.get('resolution'),
                    'height': fmt.get('height'),
                    'filesize': fmt.get('filesize')
                })
        
        return jsonify({
            "title": title,
            "duration": duration,
            "uploader": uploader,
            "available_formats": available_formats[:5]  # Chỉ hiển thị 5 format đầu
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug")
def debug_url():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Thiếu URL"}), 400
    
    try:
        # Thử với cấu hình đơn giản nhất
        ydl_opts = {
            "quiet": False,
            "no_warnings": False,
            "extract_flat": True  # Chỉ lấy thông tin cơ bản
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        if info:
            return jsonify({
                "status": "success",
                "title": info.get('title', 'Unknown'),
                "uploader": info.get('uploader', 'Unknown'),
                "duration": info.get('duration', 0),
                "view_count": info.get('view_count', 0),
                "is_live": info.get('is_live', False)
            })
        else:
            return jsonify({"status": "failed", "error": "Không thể lấy thông tin"})
            
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e),
            "url": url
        })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)