from flask import Flask, request, jsonify
import os
import tempfile
import cv2
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
    results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame using the existing logic
        frame_result = upload_process_frame.process(frame, pose)
        results.append(frame_result)

    cap.release()
    os.remove(temp_video.name)

    # Summarize the results
    feedback = summarize_results(results)
    
    return jsonify({'feedback': feedback})

def summarize_results(results):
    # Summarize the frame-by-frame results (placeholder logic)
    return "Processed video successfully"

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True)
