import cv2
import numpy as np
import threading
import time
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

# Global variable to hold the latest frame and a lock for thread-safety.
latest_frame = None
frame_lock = threading.Lock()

# Set your expected frame resolution.
WIDTH = 1280
HEIGHT = 720

@app.post("/frame")
async def process_frame(request: Request):
    global latest_frame
    frame_bytes = await request.body()
    print(f"Received a new frame of size: {len(frame_bytes)} bytes")

    # Convert the raw bytes to a NumPy array.
    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    
    expected_size = WIDTH * HEIGHT * 3  # 3 channels for RGB
    if frame_array.size != expected_size:
        print(f"Unexpected frame size: {frame_array.size}, expected: {expected_size}")
        return {"status": "error", "message": "Unexpected frame size."}

    # Reshape the array into (height, width, channels).
    frame = frame_array.reshape((HEIGHT, WIDTH, 3))

    # Update the global latest_frame variable safely.
    with frame_lock:
        latest_frame = frame

    return {"status": "success"}

def display_frames():
    # Create a named window on the main thread.
    cv2.namedWindow("Received Frame", cv2.WINDOW_NORMAL)
    while True:
        # Acquire the latest frame.
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None

        if frame is not None:
            # Convert from RGB (our format) to BGR (OpenCV default) and display.
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("Received Frame", frame_bgr)
        
        # Press 'q' to quit the window.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.01)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Run the FastAPI server in a background thread.
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000),
        daemon=True
    )
    server_thread.start()

    # Run the display loop on the main thread.
    display_frames()