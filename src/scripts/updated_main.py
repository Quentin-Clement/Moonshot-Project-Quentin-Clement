import cv2
import time
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
from process_frame import process_frame
from gesture_detection import are_keypoints_detected, has_squat_began, is_depth_sufficient, is_knee_cave, is_standing_up
import mediapipe as mp

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def initialize_camera(window_name):
    """
    Initializes the camera and the display window.
    """
    cap = cv2.VideoCapture(0)
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    return cap

def display_countdown(cap, window_name):
    """
    Displays a countdown before starting the main loop.
    """
    initial_wait_start = time.time()
    while time.time() - initial_wait_start < 5:
        ret, frame = cap.read()
        if not ret:
            return False
        countdown = 5 - int(time.time() - initial_wait_start)
        cv2.putText(frame, f"Starting in: {countdown}", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow(window_name, frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            return False
    return True

def process_frame_and_check_squat(frame, holistic, squat_state):
    """
    Processes the frame and updates the squat state.
    """
    image, results = mediapipe_detection(frame, holistic)
    keypoints_detection_message = []
    are_keypoints_detected(results, keypoints_detection_message)

    if has_squat_began(results):
        if not squat_state['in_progress']:
            squat_state.update({
                'in_progress': True,
                'sufficient_depth': False,
                'knee_cave': False,
                'results_ready': False
            })
            print("New squat detected, resetting results...")
    
    if squat_state['in_progress']:
        process_frame(results)
        squat_state['sufficient_depth'] = is_depth_sufficient(results)
        squat_state['knee_cave'] = is_knee_cave(results)

        if is_standing_up(results):
            squat_state.update({
                'in_progress': False,
                'results_ready': True
            })

    return image, results, keypoints_detection_message

def display_results(image, results, squat_state, keypoints_detection_message):
    """
    Displays results and messages on the frame.
    """
    if squat_state['results_ready']:
        result_text_depth = f"Depth: {'Sufficient' if squat_state['sufficient_depth'] else 'Insufficient'}"
        result_text_knee_cave = f"Knee Cave: {'Detected' if squat_state['knee_cave'] else 'Not detected'}"
        cv2.putText(image, result_text_depth, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, result_text_knee_cave, (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        print(result_text_depth)
        print(result_text_knee_cave)

    current_message = "Squat in progress" if squat_state['in_progress'] else "Awaiting squat"
    cv2.putText(image, current_message, (30, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)

    if keypoints_detection_message:
        y_offset = 150
        for line in keypoints_detection_message:
            cv2.putText(image, line, (30, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            y_offset += 30

    return image

def main():
    """
    Main function to initialize and run the application.
    """
    window_name = 'Gesture Detection'
    holistic = initialize_mediapipe()
    cap = initialize_camera(window_name)
    if not display_countdown(cap, window_name):
        cap.release()
        cv2.destroyAllWindows()
        return

    squat_state = {'in_progress': False, 'sufficient_depth': False, 'knee_cave': False, 'results_ready': False}
    print("Starting detection...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image, results, keypoints_detection_message = process_frame_and_check_squat(frame, holistic, squat_state)
        image = display_results(image, results, squat_state, keypoints_detection_message)
        cv2.imshow(window_name, image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()