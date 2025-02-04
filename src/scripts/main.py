import cv2
import time
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
import mediapipe as mp
from gesture_detection import are_keypoints_detected, has_squat_began, is_depth_sufficient, is_knee_cave, is_standing_up

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Time tracking variables for status display
depth_detected_time = None
knee_cave_detected_time = None
DISPLAY_DURATION = 3  # seconds

# Initialize global flags for depth and knee cave detection
sufficient_depth_detected = False
knee_cave_detected = False

# Process frame to update depth and knee cave status
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

# Main function
def main():
    global depth_detected_time, knee_cave_detected_time

    holistic = initialize_mediapipe()
    cap = cv2.VideoCapture(0)
    
    window_name = 'Gesture Detection'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Countdown for 5 seconds before starting
    initial_wait_start = time.time()
    while time.time() - initial_wait_start < 5:
        ret, frame = cap.read()
        if not ret:
            break
        countdown = 5 - int(time.time() - initial_wait_start)
        cv2.putText(frame, f"Starting in: {countdown}", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow(window_name, frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return
    
    print("Starting detection...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame with MediaPipe and gesture checks
        image, results = mediapipe_detection(frame, holistic)
        keypoints_detection_message = []
        are_keypoints_detected(results, keypoints_detection_message)

        process_frame(results)

        # Draw landmarks on the frame
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)

            # Check for depth and knee cave detection and set the display time if detected
            if sufficient_depth_detected:
                if depth_detected_time is None:
                    depth_detected_time = time.time()
            else:
                depth_detected_time = None  # Reset if no depth detected

            if knee_cave_detected:
                if knee_cave_detected_time is None:
                    knee_cave_detected_time = time.time()
            else:
                knee_cave_detected_time = None  # Reset if no knee cave detected

            # Determine colors and display the result for depth
            if depth_detected_time and (time.time() - depth_detected_time) < DISPLAY_DURATION:
                color = (0, 255, 0)  # Green for True
                cv2.putText(image, "Depth Sufficient: True", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            else:
                color = (0, 255, 0) if sufficient_depth_detected else (0, 0, 255)  # Green for True, Red for False
                cv2.putText(image, f"Depth Sufficient: {sufficient_depth_detected}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Determine colors and display the result for knee cave (reversed color logic)
            if knee_cave_detected_time and (time.time() - knee_cave_detected_time) < DISPLAY_DURATION:
                color = (0, 0, 255)  # Red for True
                cv2.putText(image, "Knee Cave Detected: True", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            else:
                color = (0, 0, 255) if knee_cave_detected else (0, 255, 0)  # Red for True, Green for False
                cv2.putText(image, f"Knee Cave Detected: {knee_cave_detected}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Display missing keypoints messages on the frame if any
            if keypoints_detection_message:
                y_offset = 50  # Starting y-coordinate for text display
                for line in keypoints_detection_message:
                    cv2.putText(image, line, (1250, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    y_offset += 30

        # Show the frame with keypoints and any messages
        cv2.imshow(window_name, image)

        # Stop if 'q' is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()