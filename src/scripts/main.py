import cv2
import time
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
from process_frame import process_frame
from gesture_detection import are_keypoints_detected
import mediapipe as mp

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils

# Main function
def main():
    holistic = initialize_mediapipe()
    cap = cv2.VideoCapture(0)
    
    window_name = 'Gesture Detection'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Countdown for 5 seconds
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
    start_time = time.time()

    # Process frames for 5 seconds
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

        # Display missing keypoints messages on the frame if any
        if keypoints_detection_message:
            y_offset = 50  # Starting y-coordinate for text display
            for line in keypoints_detection_message:
                cv2.putText(image, line, (30, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                y_offset += 30

        # Show the frame with keypoints and any missing message
        cv2.imshow(window_name, image)

        # Stop after 5 seconds or if 'q' is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()