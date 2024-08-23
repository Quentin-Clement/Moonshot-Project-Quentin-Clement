
import numpy as np
import os
import json
from datetime import datetime

class ProcessFrame:
    def __init__(self, thresholds):
        self.thresholds = thresholds
        self.state_tracker = {"SQUAT_COUNT": 0, "IMPROPER_SQUAT": 0, "state_seq": [], "DISPLAY_TEXT": None}
        self.json_file_path = "squat_errors.json"
        
        # Initialize or clear the JSON file for error logging
        if os.path.exists(self.json_file_path):
            os.remove(self.json_file_path)
        
        with open(self.json_file_path, 'w') as json_file:
            json.dump({"errors": []}, json_file)

    def _log_error(self, frame_number, error_type):
        # Logs the error into a JSON file
        error_entry = {
            "frame_number": frame_number,
            "error_type": error_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(self.json_file_path, 'r+') as json_file:
            data = json.load(json_file)
            data["errors"].append(error_entry)
            json_file.seek(0)
            json.dump(data, json_file, indent=4)

    def process(self, frame: np.array, pose, frame_number: int):
        frame_height, frame_width, _ = frame.shape
        keypoints = pose.process(frame)
        play_sound = None
        
        if keypoints.pose_landmarks:
            # Placeholder for actual detection logic
            improper_squat_detected = False  
            
            # Manually triggering error detection for debugging
            if frame_number % 10 == 0:  # Log an error every 10 frames for testing
                improper_squat_detected = True
            
            # Simulate an error detection scenario
            if improper_squat_detected:
                self.state_tracker['IMPROPER_SQUAT'] += 1
                error_type = "Improper squat posture"
                
                # Log the error instead of showing feedback on screen
                print(f"Logging error for frame {frame_number}: {error_type}")
                self._log_error(frame_number, error_type)

        return frame, play_sound  # Still returning frame for any other processing
