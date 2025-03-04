import cv2
import time
import numpy as np
import threading
import mediapipe as mp
from fastapi import FastAPI, Request
import uvicorn

# Import custom detection modules
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
from gesture_detection import are_keypoints_detected, is_depth_sufficient, is_knee_cave

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils

# Time tracking variables for status display
depth_detected_time = None
knee_cave_detected_time = None
DISPLAY_DURATION = 3  # seconds

# Global variables
latest_frame = None
frame_lock = threading.Lock()

# Set your expected frame resolution
WIDTH = 1280
HEIGHT = 720

# Initialize FastAPI app
app = FastAPI()

# Global flags for depth and knee cave detection
sufficient_depth_detected = False
knee_cave_detected = False

def process_frame_for_pose(results):
    """
    Process frame to update depth and knee cave status
    """
    global sufficient_depth_detected, knee_cave_detected

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Check if squat depth is sufficient
        if all(landmarks[i].visibility > 0.5 for i in [11, 12, 13, 14]):  # Hips and knees
            sufficient_depth_detected = is_depth_sufficient(results)

        # Check for knee cave
        if all(landmarks[i].visibility > 0.5 for i in [11, 12, 13, 14, 15, 16]):  # Hips, knees, ankles
            knee_cave_detected = is_knee_cave(results)

@app.post("/frame")
async def process_frame(request: Request):
    """
    Endpoint to receive frames via HTTP
    """
    global latest_frame
    frame_bytes = await request.body()

    # Convert the raw bytes to a NumPy array
    frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
    
    expected_size = WIDTH * HEIGHT * 3  # 3 channels for RGB
    if frame_array.size != expected_size:
        print(f"Unexpected frame size: {frame_array.size}, expected: {expected_size}")
        return {"status": "error", "message": "Unexpected frame size."}

    # Reshape the array into (height, width, channels)
    frame = frame_array.reshape((HEIGHT, WIDTH, 3))

    # Update the global latest_frame variable safely
    with frame_lock:
        latest_frame = frame

    return {"status": "success"}

def process_and_display_frames():
    """
    Main processing loop for frame analysis and display
    """
    global depth_detected_time, knee_cave_detected_time

    # Initialize MediaPipe
    holistic = initialize_mediapipe()
    
    # Create window
    window_name = 'Gesture Detection'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        # Acquire the latest frame
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None

        if frame is not None:
            # Process the frame with MediaPipe and gesture checks
            image, results = mediapipe_detection(frame, holistic)
            
            # Detect keypoints and prepare detection messages
            keypoints_detection_message = []
            are_keypoints_detected(results, keypoints_detection_message)

            # Process frame for pose estimation
            process_frame_for_pose(results)

            # Draw landmarks on the frame
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)

                # Manage depth detection display
                if sufficient_depth_detected:
                    if depth_detected_time is None:
                        depth_detected_time = time.time()
                else:
                    depth_detected_time = None

                # Manage knee cave detection display
                if knee_cave_detected:
                    if knee_cave_detected_time is None:
                        knee_cave_detected_time = time.time()
                else:
                    knee_cave_detected_time = None

                # Display depth status
                if depth_detected_time and (time.time() - depth_detected_time) < DISPLAY_DURATION:
                    color = (0, 255, 0)  # Green for True
                    cv2.putText(image, "Depth Sufficient: True", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                else:
                    color = (0, 255, 0) if sufficient_depth_detected else (0, 0, 255)
                    cv2.putText(image, f"Depth Sufficient: {sufficient_depth_detected}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                # Display knee cave status
                if knee_cave_detected_time and (time.time() - knee_cave_detected_time) < DISPLAY_DURATION:
                    color = (0, 0, 255)  # Red for True
                    cv2.putText(image, "Knee Cave Detected: True", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                else:
                    color = (0, 0, 255) if knee_cave_detected else (0, 255, 0)
                    cv2.putText(image, f"Knee Cave Detected: {knee_cave_detected}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                # Display missing keypoints messages
                if keypoints_detection_message:
                    y_offset = 50
                    for line in keypoints_detection_message:
                        cv2.putText(image, line, (1250, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                        y_offset += 30

            # Convert frame from RGB to BGR for OpenCV display
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Show the frame
            cv2.imshow(window_name, image_bgr)

        # Check for quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cv2.destroyAllWindows()

def main():
    # Run the FastAPI server in a background thread
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000),
        daemon=True
    )
    server_thread.start()

    # Run the frame processing and display loop
    process_and_display_frames()

if __name__ == "__main__":
    main()