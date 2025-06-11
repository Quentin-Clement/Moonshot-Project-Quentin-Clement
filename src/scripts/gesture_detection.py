import mediapipe as mp
import math

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
    hips_height = ((left_hip.y + right_hip.y) / 2) + 0.05  # Subtract a small value to allow for some margin
    knees_height = (left_knee.y + right_knee.y) / 2
    
    return hips_height > knees_height

def is_knee_cave(results):
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
    right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
    hips_width = abs(left_hip.x - right_hip.x) + 0.05
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

# Utility to compute the angle between three points
def compute_angle(a, b, c):
    """
    Computes the angle at point b formed by points a-b-c in degrees.
    a, b, c: objects with .x, .y, .z
    """
    # Convert to vectors
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)
    # Dot product and magnitudes
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])
    if mag_ba * mag_bc == 0:
        return 0.0
    # Compute angle
    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    angle = math.degrees(math.acos(cos_angle))
    return angle

class SquatCounter:
    """
    Counts squat repetitions and marks start/end times with calibration.
    It waits for a stable 'up' position before beginning count.
    Usage:
        counter = SquatCounter()
        for each frame:
            counter.update(results, timestamp)
        total = counter.get_count()
        start_end_pairs = counter.get_times()
    """
    def __init__(self, down_threshold=140, depth_threshold=90, up_threshold=160,
                 calib_frames=30):
        # Thresholds in degrees
        self.down_threshold = down_threshold
        self.depth_threshold = depth_threshold
        self.up_threshold = up_threshold
        # Calibration: require several frames of full extension
        self.calib_frames = calib_frames
        self.calib_count = 0
        self.calibrated = False
        # FSM state: 'up' or 'down'
        self.state = 'up'
        self.depth_reached = False
        self.count = 0
        self.start_times = []
        self.end_times = []

    def update(self, results, timestamp):
        """
        Call this for each frame with pose estimation results and current timestamp (in seconds).
        Will ignore frames until calibration achieved.
        """
        if not results.pose_landmarks:
            return
        lm = results.pose_landmarks.landmark
        # Compute average knee angle
        left_hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee = lm[mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = lm[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        angle_left = compute_angle(left_hip, left_knee, left_ankle)
        angle_right = compute_angle(right_hip, right_knee, right_ankle)
        knee_angle = (angle_left + angle_right) / 2.0

        # Calibration stage: ensure user starts in full extension
        if not self.calibrated:
            if knee_angle > self.up_threshold:
                self.calib_count += 1
            else:
                self.calib_count = 0
            if self.calib_count >= self.calib_frames:
                self.calibrated = True
                print("Calibration complete. Starting squat detection.")
            return

        # FSM transitions after calibration
        if self.state == 'up':
            # Squat begins when knee bends below down_threshold
            if knee_angle < self.down_threshold:
                self.state = 'down'
                self.depth_reached = False
                self.start_times.append(timestamp)
        elif self.state == 'down':
            # Mark depth if below deeper threshold
            if knee_angle < self.depth_threshold:
                self.depth_reached = True
            # Squat ends when knee extends above up_threshold
            if knee_angle > self.up_threshold:
                self.state = 'up'
                self.end_times.append(timestamp)
                if self.depth_reached:
                    self.count += 1
                # ready for next rep
                self.depth_reached = False

    def get_count(self):
        return self.count

    def get_times(self):
        """Returns paired lists of (start_times, end_times) in seconds."""
        return list(zip(self.start_times, self.end_times))