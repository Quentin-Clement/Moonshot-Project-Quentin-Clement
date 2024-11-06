import mediapipe as mp

mp_pose = mp.solutions.pose

def is_depth_sufficient(results):
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    hips_height = (left_hip.y + right_hip.y) / 2
    knees_height = (left_knee.y + right_knee.y) / 2
    return hips_height > knees_height

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

def are_knees_over_toes(results):
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_foot_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
    right_foot_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
    knees_z_mean = (left_knee.z + right_knee.z) / 2
    foot_z_mean = (left_foot_index.z + right_foot_index.z) / 2
    return knees_z_mean < foot_z_mean

def are_keypoints_detected(results, keypoints_detection_message):
    landmarks = results.pose_landmarks.landmark if results.pose_landmarks else []

    # Create separate lists for each body part category
    knees_message = []
    hips_message = []
    ankles_message = []
    feet_message = []

    # Check the visibility of each keypoint and append the message to the respective list
    if not landmarks or landmarks[mp_pose.PoseLandmark.LEFT_KNEE].visibility <= 0.5:
        knees_message.append("Left knee not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].visibility <= 0.5:
        knees_message.append("Right knee not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.LEFT_HIP].visibility <= 0.5:
        hips_message.append("Left hip not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.RIGHT_HIP].visibility <= 0.5:
        hips_message.append("Right hip not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].visibility <= 0.5:
        ankles_message.append("Left ankle not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].visibility <= 0.5:
        ankles_message.append("Right ankle not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX].visibility <= 0.5:
        feet_message.append("Left foot not detected.")
    if not landmarks or landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].visibility <= 0.5:
        feet_message.append("Right foot not detected.")

    # Combine messages with newline characters to display them on separate lines
    if knees_message:
        keypoints_detection_message.append(" ".join(knees_message))
    if hips_message:
        keypoints_detection_message.append(" ".join(hips_message))
    if ankles_message:
        keypoints_detection_message.append(" ".join(ankles_message))
    if feet_message:
        keypoints_detection_message.append(" ".join(feet_message))