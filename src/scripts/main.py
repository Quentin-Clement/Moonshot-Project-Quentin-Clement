import cv2
import time
import argparse
import os
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
from process_frame import process_frame
from gesture_detection import SquatCounter
import mediapipe as mp

# Initialize MediaPipe drawing utilities
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Main function
def main():
    # Parse input video path
    parser = argparse.ArgumentParser(description='Squat counter and snippet generator for an MP4 video')
    parser.add_argument('input', help='Path to input video file (e.g., .mp4)')
    parser.add_argument('--output_dir', default='snippets', help='Directory to save squat snippets')
    args = parser.parse_args()

    # Set up MediaPipe
    holistic = initialize_mediapipe()
    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        print(f"Error opening video file: {args.input}")
        return

    # Video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize squat counter
    counter = SquatCounter()

    # Countdown for 5 seconds before starting
    print("Get ready in 5 seconds...")
    time.sleep(5)

    window_name = 'Squat Counter'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 540)

    # Process video frames for counting
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Timestamp in seconds
        timestamp = frame_idx / fps

        # Run MediaPipe detection
        image, results = mediapipe_detection(frame, holistic)

        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )

        # Optional: additional processing
        process_frame(results)

        # Update squat counter
        counter.update(results, timestamp)

        # Overlay rep count
        count = counter.get_count()
        cv2.putText(image,
                    f"Reps: {count}",
                    (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (255, 0, 0),
                    3)

        # Display
        cv2.imshow(window_name, image)
        if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
            break

        frame_idx += 1

    # After processing, retrieve rep intervals
    times = counter.get_times()  # list of (start_sec, end_sec)
    total_reps = counter.get_count()
    print(f"Total squats performed: {total_reps}")

    # Reset capture for snippet extraction
    cap.release()
    cap = cv2.VideoCapture(args.input)

    # Generate a snippet video for each rep
    for i, (start_sec, end_sec) in enumerate(times, 1):
        start_frame = int(start_sec * fps)
        end_frame = int(end_sec * fps)
        snippet_path = os.path.join(args.output_dir, f"squat_{i}.mp4")
        writer = cv2.VideoWriter(snippet_path, fourcc, fps, (width, height))

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        for f in range(start_frame, end_frame + 1):
            ret, frame = cap.read()
            if not ret:
                break
            writer.write(frame)
        writer.release()
        print(f"Saved snippet {i}: frames {start_frame}-{end_frame} to {snippet_path}")

        # Optional: process snippet individually
        # snippet_cap = cv2.VideoCapture(snippet_path)
        # while snippet_cap.isOpened():
        #     ret, sframe = snippet_cap.read()
        #     if not ret:
        #         break
        #     _, sresults = mediapipe_detection(sframe, holistic)
        #     process_frame(sresults)
        # snippet_cap.release()

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
