from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import os

from main import process_video

app = FastAPI()

# Allow your React origin (and adjust in prod as needed)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", "capacitor://localhost"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2) mount static files
app.mount('/outputs', StaticFiles(directory=OUTPUT_DIR), name='outputs')

@app.post('/api/process-video')
async def process_video_endpoint(video: UploadFile = File(...)):
    if not video.filename.lower().endswith(('.mp4','.mov','.avi')):
        raise HTTPException(400, 'Unsupported video format')

    uid         = str(uuid4())
    save_name   = f"{uid}_{video.filename}"
    upload_path = os.path.join(UPLOAD_DIR, save_name)
    with open(upload_path, 'wb') as f:
        f.write(await video.read())

    try:
        result = process_video(input_path=upload_path, output_dir=OUTPUT_DIR)
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {e}")

    # 3) rewrite any absolute paths into URLs that clients can fetch
    def to_url(p):
        fn = os.path.basename(p)
        return f"/outputs/{fn}"

    # if your helper stored them under keys "snippets" & "thumbnails":
    result["snippets"]   = [to_url(p) for p in result.get("snippets",[])]
    result["thumbnails"] = [to_url(p) for p in result.get("thumbnails",[])]

    return JSONResponse(content=result)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)