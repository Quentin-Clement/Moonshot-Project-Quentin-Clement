from gesture_detection import is_depth_sufficient, is_knee_cave

def process_frame(results):
    global sufficient_depth_detected, knee_cave_detected

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Check if squat depth is sufficient
        if all(landmarks[i].visibility > 0.5 for i in [11, 12, 13, 14]):  # Hips and knees
            if is_depth_sufficient(results):
                sufficient_depth_detected = True
            else:
                sufficient_depth_detected = False

        # Check for knee cave
        if all(landmarks[i].visibility > 0.5 for i in [11, 12, 13, 14, 15, 16]):  # Hips, knees, ankles
            if is_knee_cave(results):
                knee_cave_detected = True
            else:
                knee_cave_detected = False