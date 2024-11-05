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

# Initialize variables
sufficient_depth_detected = False
knee_cave_detected = False
knees_over_toes_detected = False

consecutive_sufficient_depth_count = 0
consecutive_knee_cave_count = 0
consecutive_knees_over_toes_count = 0

CONSECUTIVE_THRESHOLD = 4
RUN_DURATION = 10  # seconds duration

# Flags to track if required keypoints were detected at least once during the 10 seconds
depth_keypoints_detected = False
knee_cave_keypoints_detected = False
knees_over_toes_keypoints_detected = False

# Process each frame
def process_frame(results):
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

# Main function to open camera and detect gesture
def main():
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        cap = cv2.VideoCapture(0)
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process the frame
            image, results = mediapipe_detection(frame, holistic)
            process_frame(results)

            # Draw landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            # Show the frame
            cv2.imshow('Gesture Detection', image)

            # Stop after RUN_DURATION seconds or if 'q' is pressed
            if (time.time() - start_time) > RUN_DURATION or cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release resources
        cap.release()
        cv2.destroyAllWindows()

        # Print only one message per check, based on keypoint detection status
        if depth_keypoints_detected:
            print("Sufficient squat depth detected." if sufficient_depth_detected else "Sufficient squat depth not detected.")
        else:
            print("Depth keypoints (hips and knees) not detected during the 10 seconds.")

        if knee_cave_keypoints_detected:
            print("Knee cave detected." if knee_cave_detected else "Knee cave not detected.")
        else:
            print("Knee cave keypoints (hips, knees, and ankles) not detected during the 10 seconds.")

        if knees_over_toes_keypoints_detected:
            print("Knees over toes detected." if knees_over_toes_detected else "Knees over toes not detected.")
        else:
            print("Knees-over-toes keypoints (knees and feet) not detected during the 10 seconds.")

if __name__ == "__main__":
    main()