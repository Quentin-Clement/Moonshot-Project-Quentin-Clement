from gesture_detection import is_depth_sufficient, is_knee_cave, are_knees_over_toes

# Initialize variables
sufficient_depth_detected = False
knee_cave_detected = False
knees_over_toes_detected = False

consecutive_sufficient_depth_count = 0
consecutive_knee_cave_count = 0
consecutive_knees_over_toes_count = 0
CONSECUTIVE_THRESHOLD = 4

def process_frame(results):
    global consecutive_sufficient_depth_count, consecutive_knee_cave_count, consecutive_knees_over_toes_count
    global sufficient_depth_detected, knee_cave_detected, knees_over_toes_detected

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Check if squat depth is sufficient
        if all(landmarks[i].visibility > 0.5 for i in [11, 12, 13, 14]):  # Hips and knees
            if is_depth_sufficient(results):
                consecutive_sufficient_depth_count += 1
                if consecutive_sufficient_depth_count >= CONSECUTIVE_THRESHOLD:
                    sufficient_depth_detected = True
            else:
                consecutive_sufficient_depth_count = 0

        # Check for knee cave and knees over toes
        if all(landmarks[i].visibility > 0.5 for i in [11, 12, 13, 14, 15, 16]):  # Hips, knees, ankles
            if is_knee_cave(results):
                consecutive_knee_cave_count += 1
                if consecutive_knee_cave_count >= CONSECUTIVE_THRESHOLD:
                    knee_cave_detected = True
            else:
                consecutive_knee_cave_count = 0

        if all(landmarks[i].visibility > 0.5 for i in [13, 14, 31, 32]):  # Knees and feet
            if are_knees_over_toes(results):
                consecutive_knees_over_toes_count += 1
                if consecutive_knees_over_toes_count >= CONSECUTIVE_THRESHOLD:
                    knees_over_toes_detected = True
            else:
                consecutive_knees_over_toes_count = 0