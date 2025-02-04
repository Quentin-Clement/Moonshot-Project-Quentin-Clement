import cv2
import time
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
from process_frame import process_frame
from gesture_detection import are_keypoints_detected, has_squat_began, is_depth_sufficient, is_knee_cave, is_standing_up
import mediapipe as mp

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Main function
def main():
    holistic = initialize_mediapipe()
    cap = cv2.VideoCapture(0)
    
    window_name = 'Gesture Detection'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    squat_in_progress = False
    sufficient_depth_detected = False
    knee_cave_detected = False

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

        if has_squat_began(results):
            if not squat_in_progress:
                # Reset flags for the next squat cycle
                squat_in_progress = True
                print("New squat detected, resetting results...")
                sufficient_depth_detected = False
                knee_cave_detected = False
                squat_results_ready = False
            print("Squat started...")

        if squat_in_progress:
            # Process frame to check squat depth and knee cave
            process_frame(results)
            
            # Monitor sufficient depth and knee cave states
            sufficient_depth_detected = is_depth_sufficient(results)
            knee_cave_detected = is_knee_cave(results)

            # Check if squat is finished
            if is_standing_up(results):
                squat_in_progress = False
                squat_results_ready = True

        # Display results when squat ends and until the next squat starts
        if squat_results_ready:
            result_text_depth = f"Depth: {'Sufficient' if sufficient_depth_detected else 'Insufficient'}"
            result_text_knee_cave = f"Knee Cave: {'Detected' if knee_cave_detected else 'Not detected'}"
            
            # Display results on the image
            cv2.putText(image, result_text_depth, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, result_text_knee_cave, (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Print in in the command line as well
            print(result_text_depth)
            print(result_text_knee_cave)

        # Display current state message
        if squat_in_progress:
            current_message = "Squat in progress"
        else:
            current_message = "Awaiting squat"

        cv2.putText(image, current_message, (30, 600), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Draw landmarks on the frame
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp.solutions.holistic.POSE_CONNECTIONS)

            # Display missing keypoints messages on the frame if any
            if keypoints_detection_message:
                y_offset = 150  # Starting y-coordinate for text display
                for line in keypoints_detection_message:
                    cv2.putText(image, line, (30, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
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