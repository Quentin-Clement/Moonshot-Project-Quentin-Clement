
from flask import Flask, request, jsonify
import os
import tempfile
import cv2
import json  # Importing json to handle JSON file reading and writing
from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds

# Create a Flask app
app = Flask(__name__)

# Initialize the processing components
thresholds = get_thresholds()
upload_process_frame = ProcessFrame(thresholds=thresholds)
pose = get_mediapipe_pose()

@app.route('/')
def index():
    return "Welcome to the Flask Video Processing API. Upload a video at /analyze."

@app.route('/analyze', methods=['POST'])
def analyze():
    # Ensure the video is uploaded
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    video_file = request.files['video']
    
    # Save the uploaded video to a temporary file
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    video_file.save(temp_video.name)

    # Open the video file using OpenCV
    cap = cv2.VideoCapture(temp_video.name)
    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame and log errors
        upload_process_frame.process(frame, pose, frame_number)
        frame_number += 1

    cap.release()
    os.remove(temp_video.name)

    # After processing, return the content of the JSON error log
    try:
        with open(upload_process_frame.json_file_path, 'r') as json_file:
            error_log = json.load(json_file)
            # Ensure we always return a non-null response
            if not error_log.get("errors"):
                error_log["errors"] = []
    except FileNotFoundError:
        # In case the JSON file is not found (no errors detected), return a default structure
        error_log = {"errors": []}

    return jsonify(error_log)

if __name__ == "__main__":
    app.run(debug=True)
