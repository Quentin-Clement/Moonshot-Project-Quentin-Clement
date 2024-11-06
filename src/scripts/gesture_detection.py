import mediapipe as mp

mp_pose = mp.solutions.pose

# Initialize variables for squat detection
initial_down_hips_height = None
consecutive_down_frames = 0
THRESHOLD = 10  # Number of consecutive frames needed for the squat to be detected as started

def has_squat_began(results):
    global initial_down_hips_height, consecutive_down_frames

    if not results.pose_landmarks:
        # Reset the counter if no landmarks are detected
        consecutive_down_frames = 0
        return False

    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

    # Calculate the average y-position of the hips to track height
    current_hips_height = (left_hip.y + right_hip.y) / 2

    # Initialize the positions if this is the first frame
    if initial_down_hips_height is None:
        initial_down_hips_height = current_hips_height
        return False  # We cannot detect a squat on the first frame

    # Check if hips are lowering (y-position increasing means going lower)
    hips_lowering = current_hips_height > initial_down_hips_height

    # Increment the counter only if both conditions are met
    if hips_lowering:
        consecutive_down_frames += 1
        # If hips have been lowering and feet stable for the required number of frames, detect squat start
        if consecutive_down_frames >= THRESHOLD:
            return True
    else:
        # Reset the counter if either condition fails
        consecutive_down_frames = 0

    # Update initial hips height for tracking in the next frame
    initial_down_hips_height = current_hips_height

    return False

initial_up_hips_height = None
consecutive_up_frames = 0

def is_standing_up(results):
    global initial_up_hips_height, consecutive_up_frames

    if not results.pose_landmarks:
        # Reset the counter if no landmarks are detected
        consecutive_up_frames = 0
        return False

    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

    # Calculate the average y-position of the hips to track height
    current_hips_height = (left_hip.y + right_hip.y) / 2

    # Initialize the positions if this is the first frame
    if initial_up_hips_height is None:
        initial_up_hips_height = current_hips_height
        return False  # We cannot detect a squat on the first frame

    # Check if hips are lowering (y-position increasing means going lower)
    hips_lowering = current_hips_height < initial_up_hips_height

    # Increment the counter only if both conditions are met
    if hips_lowering:
        consecutive_up_frames += 1
        # If hips have been lowering and feet stable for the required number of frames, detect squat start
        if consecutive_up_frames >= THRESHOLD:
            return True
    else:
        # Reset the counter if either condition fails
        consecutive_up_frames = 0

    # Update initial hips height for tracking in the next frame
    initial_up_hips_height = current_hips_height

    return False

def is_depth_sufficient(results):
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    hips_height = (left_hip.y + right_hip.y) / 2
    knees_height = (left_knee.y + right_knee.y) / 2
    
    # Debug print to compare hip and knee heights
    print(f"Hips height: {hips_height}, Knees height: {knees_height}, Depth sufficient: {hips_height > knees_height}")
    
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
    
    # Debug print to check knee cave conditions
    print(f"Hips width: {hips_width}, Knees width: {knees_width}, Ankles width: {ankles_width}, Knee cave: {knees_width < hips_width and knees_width < ankles_width}")
    
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