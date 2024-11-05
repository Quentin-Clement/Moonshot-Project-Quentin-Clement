import cv2
import mediapipe as mp
import time

# Initialize MediaPipe holistic model
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Function to process the frames using MediaPipe
def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR to RGB
    image.flags.writeable = False                   # Image is no longer writeable
    results = model.process(image)                  # Make prediction
    image.flags.writeable = True                    # Image is now writeable
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # COLOR COVERSION RGB to BGR
    return image, results

# Function to check if feet positions are stable within a threshold
def is_feet_stable(current_left_foot, current_right_foot, initial_left_foot, initial_right_foot, threshold=0.05):
    left_foot_movement = abs(current_left_foot.x - initial_left_foot.x) + abs(current_left_foot.y - initial_left_foot.y)
    right_foot_movement = abs(current_right_foot.x - initial_right_foot.x) + abs(current_right_foot.y - initial_right_foot.y)
    return left_foot_movement < threshold and right_foot_movement < threshold

# Function to check if the squat depth is sufficient
def is_depth_sufficient(results):
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    hips_height = (left_hip.y + right_hip.y) / 2
    knees_height = (left_knee.y + right_knee.y) / 2
    return hips_height > knees_height

# Function to check if there is knee cave
def is_knee_cave(results):
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
    right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
    hips_width = abs(left_hip.x - right_hip.x)
    knees_width = abs(left_knee.x - right_knee.x)
    ankles_width = abs(left_ankle.x - right_ankle.x)
    return knees_width < hips_width and knees_width < ankles_width

# Function to check if the knees are over toes
def are_knees_over_toes(results):
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_foot_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
    right_foot_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
    knees_z_mean = (left_knee.z + right_knee.z) / 2
    foot_z_mean = (left_foot_index.z + right_foot_index.z) / 2
    return knees_z_mean < foot_z_mean

# Variables for squat start detection
initial_hips_height = None
initial_left_foot = None
initial_right_foot = None
consecutive_hip_lowering_frames = 0
SQUAT_START_THRESHOLD = 10  # Number of consecutive frames with lowering hips
FEET_STABILITY_THRESHOLD = 0.05  # Tolerance for feet to stay in the same zone

# Initialize variables for gesture detection
sufficient_depth_detected = False
knee_cave_detected = False
knees_over_toes_detected = False

consecutive_sufficient_depth_count = 0
consecutive_knee_cave_count = 0
consecutive_knees_over_toes_count = 0

CONSECUTIVE_THRESHOLD = 4
CHECK_DURATION = 5  # 5 seconds duration for checking conditions

# Flags to track if required keypoints were detected at least once during the check
depth_keypoints_detected = False
knee_cave_keypoints_detected = False
knees_over_toes_keypoints_detected = False

# Process each frame
def process_frame(results):
    global initial_hips_height, initial_left_foot, initial_right_foot
    global consecutive_sufficient_depth_count, consecutive_knee_cave_count, consecutive_knees_over_toes_count
    global sufficient_depth_detected, knee_cave_detected, knees_over_toes_detected
    global depth_keypoints_detected, knee_cave_keypoints_detected, knees_over_toes_keypoints_detected

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        # Check for depth: requires hips and knees
        if all(landmarks[i].visibility > 0.5 for i in [mp_pose.PoseLandmark.LEFT_HIP,
                                                        mp_pose.PoseLandmark.RIGHT_HIP,
                                                        mp_pose.PoseLandmark.LEFT_KNEE,
                                                        mp_pose.PoseLandmark.RIGHT_KNEE]):
            depth_keypoints_detected = True  # Mark keypoints as detected at least once
            if is_depth_sufficient(results):
                consecutive_sufficient_depth_count += 1
                if consecutive_sufficient_depth_count >= CONSECUTIVE_THRESHOLD:
                    sufficient_depth_detected = True
            else:
                consecutive_sufficient_depth_count = 0

        # Check for knee cave: requires hips, knees, and ankles
        if all(landmarks[i].visibility > 0.5 for i in [mp_pose.PoseLandmark.LEFT_HIP,
                                                        mp_pose.PoseLandmark.RIGHT_HIP,
                                                        mp_pose.PoseLandmark.LEFT_KNEE,
                                                        mp_pose.PoseLandmark.RIGHT_KNEE,
                                                        mp_pose.PoseLandmark.LEFT_ANKLE,
                                                        mp_pose.PoseLandmark.RIGHT_ANKLE]):
            knee_cave_keypoints_detected = True  # Mark keypoints as detected at least once
            if is_knee_cave(results):
                consecutive_knee_cave_count += 1
                if consecutive_knee_cave_count >= CONSECUTIVE_THRESHOLD:
                    knee_cave_detected = True
            else:
                consecutive_knee_cave_count = 0

        # Check for knees over toes: requires knees and feet
        if all(landmarks[i].visibility > 0.5 for i in [mp_pose.PoseLandmark.LEFT_KNEE,
                                                        mp_pose.PoseLandmark.RIGHT_KNEE,
                                                        mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
                                                        mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]):
            knees_over_toes_keypoints_detected = True  # Mark keypoints as detected at least once
            if are_knees_over_toes(results):
                consecutive_knees_over_toes_count += 1
                if consecutive_knees_over_toes_count >= CONSECUTIVE_THRESHOLD:
                    knees_over_toes_detected = True
            else:
                consecutive_knees_over_toes_count = 0

def main():
    global initial_hips_height, initial_left_foot, initial_right_foot  # Declare these as global to modify them here
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        cap = cv2.VideoCapture(0)
        squat_started = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame
            image, results = mediapipe_detection(frame, holistic)

            if results.pose_landmarks:

                # Draw landmarks
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
                
                # Extract current positions
                left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
                left_foot = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
                right_foot = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
                hips_height = (left_hip.y + right_hip.y) / 2

                # Set initial positions for reference
                if initial_hips_height is None:
                    initial_hips_height = hips_height
                if initial_left_foot is None:
                    initial_left_foot = left_foot
                if initial_right_foot is None:
                    initial_right_foot = right_foot

                # Check for squat start conditions
                feet_stable = is_feet_stable(left_foot, right_foot, initial_left_foot, initial_right_foot, FEET_STABILITY_THRESHOLD)
                hips_lowering = hips_height > initial_hips_height

                # Count frames of lowering hips if feet are stable
                if feet_stable and hips_lowering:
                    consecutive_hip_lowering_frames += 1
                else:
                    consecutive_hip_lowering_frames = 0

                # Start squat if conditions met for consecutive frames
                if consecutive_hip_lowering_frames >= SQUAT_START_THRESHOLD:
                    squat_started = True
                    start_time = time.time()  # Begin 5-second check period

                # If squat has started, check conditions for 5 seconds
                if squat_started:
                    process_frame(results)

                    # Stop checking after CHECK_DURATION seconds
                    if (time.time() - start_time) > CHECK_DURATION:
                        break

            # Show frame
            cv2.imshow('Gesture Detection', image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()

        # Print results
        if depth_keypoints_detected:
            print("Sufficient squat depth detected." if sufficient_depth_detected else "Sufficient squat depth not detected.")
        else:
            print("Depth keypoints (hips and knees) not detected during the 5 seconds.")

        if knee_cave_keypoints_detected:
            print("Knee cave detected." if knee_cave_detected else "Knee cave not detected.")
        else:
            print("Knee cave keypoints (hips, knees, and ankles) not detected during the 5 seconds.")

        if knees_over_toes_keypoints_detected:
            print("Knees over toes detected." if knees_over_toes_detected else "Knees over toes not detected.")
        else:
            print("Knees-over-toes keypoints (knees and feet) not detected during the 5 seconds.")

if __name__ == "__main__":
    main()