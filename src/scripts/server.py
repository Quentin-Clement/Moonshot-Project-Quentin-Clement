from fastapi import FastAPI, File

app = FastAPI()

@app.post("/frame")
async def process_frame(frame: bytes = File(...)):
    # Print a message every time a new frame is received
    print(f"Received a new frame of size: {len(frame)} bytes")
    
    # Here you could add additional processing, e.g., decoding the image with OpenCV or Pillow.
    return {"status": "success"}