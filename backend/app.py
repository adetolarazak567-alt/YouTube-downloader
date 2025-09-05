from flask import Flask, request, send_file, jsonify, Response
from yt_dlp import YoutubeDL
from io import BytesIO

app = Flask(__name__)

ydl_opts_info = {
    'quiet': True,
    'skip_download': True,
    'format': 'mp4',
}

ydl_opts_preview = {
    'quiet': True,
    'format': 'mp4',
    'noplaylist': True,
    'max_filesize': 10_000_000,  # ~10MB preview
    'outtmpl': '-',               # stream to stdout
}

ydl_opts_download = {
    'quiet': True,
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': '-',               # stream to stdout
}

@app.route('/video_info')
def video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        with YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'thumbnail': info.get('thumbnail'),
                'title': info.get('title')
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/video_preview')
def video_preview():
    url = request.args.get('url')
    if not url:
        return 'No URL provided', 400
    try:
        def generate():
            ydl_opts = ydl_opts_preview.copy()
            ydl_opts['outtmpl'] = '-'
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        return Response(generate(), mimetype='video/mp4')
    except Exception as e:
        return str(e), 500

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return 'No URL provided', 400
    try:
        def generate():
            ydl_opts = ydl_opts_download.copy()
            ydl_opts['outtmpl'] = '-'
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        return Response(generate(), mimetype='video/mp4',
                        headers={"Content-Disposition": "attachment; filename=video.mp4"})
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
