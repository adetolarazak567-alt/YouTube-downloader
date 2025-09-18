from flask import Flask, request, jsonify, send_file
from pytube import YouTube
import os

app = Flask(__name__)

# Initialize counters
page_views = 0
downloads = 0

@app.route('/download', methods=['POST'])
def download_video():
    global downloads
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        video_path = stream.download(filename='video.mp4')
        downloads += 1
        return jsonify({'video_url': video_path, 'title': yt.title})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/counts', methods=['GET'])
def get_counts():
    global page_views
    return jsonify({'pageViews': page_views, 'downloads': downloads})

@app.route('/incrementPageView', methods=['POST'])
def increment_page_view():
    global page_views
    page_views += 1
    return '', 204

@app.route('/incrementDownload', methods=['POST'])
def increment_download():
    global downloads
    downloads += 1
    return '', 204

@app.route('/resetCounts', methods=['POST'])
def reset_counts():
    global page_views, downloads
    page_views = 0
    downloads = 0
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
