import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

# Enable CORS so your frontend can access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change "*" to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Global counters
# --------------------
page_views = 0
downloads = 0

# --------------------
# Routes
# --------------------
@app.post("/download")
async def download_video(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided")

    try:
        # Extract info from YouTube without downloading
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "video")
            formats = info.get("formats", [])
            # Pick best mp4 with filesize info
            best_format = next((f for f in formats if f.get("ext") == "mp4" and f.get("filesize")), None)
            if not best_format:
                best_format = formats[-1]  # fallback
            video_url = best_format.get("url")

        return JSONResponse(content={"title": title, "video_url": video_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------
# Admin / Counter Endpoints
# --------------------
@app.get("/counts")
async def get_counts():
    return {"pageViews": page_views, "downloads": downloads}

@app.post("/incrementPageView")
async def increment_page_view():
    global page_views
    page_views += 1
    return "", 204

@app.post("/incrementDownload")
async def increment_download():
    global downloads
    downloads += 1
    return "", 204

@app.post("/resetCounts")
async def reset_counts():
    global page_views, downloads
    page_views = 0
    downloads = 0
    return "", 204

# --------------------
# Start server
# --------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # <-- use Render’s port
    uvicorn.run(app, host="0.0.0.0", port=port)
