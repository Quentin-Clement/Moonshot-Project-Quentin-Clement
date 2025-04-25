import cv2
import os
import shutil
import argparse
from uuid import uuid4
from mediapipe_detection import mediapipe_detection, initialize_mediapipe
from gesture_detection import (
    SquatCounter,
    is_depth_sufficient,
    is_knee_cave,
    are_knees_over_toes,
)
from process_frame import process_frame


def process_video(input_path: str, output_dir: str) -> dict:
    # Prepare directories
    os.makedirs(output_dir, exist_ok=True)
    snippets_dir = os.path.join(output_dir, 'snippets')
    thumbs_dir = os.path.join(output_dir, 'thumbnails')
    os.makedirs(snippets_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)

    # Initialize MediaPipe and counter
    holistic = initialize_mediapipe()
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open {input_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    counter = SquatCounter()
    frame_idx = 0
    # First pass: detect rep intervals
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        timestamp = frame_idx / fps
        _, results = mediapipe_detection(frame, holistic)
        process_frame(results)
        counter.update(results, timestamp)
        frame_idx += 1
    cap.release()

    times = counter.get_times()  # list of (start_sec, end_sec)

    # Copy full video and save thumbnail
    full_out = os.path.join(output_dir, 'full.mp4')
    shutil.copyfile(input_path, full_out)
    cap_full = cv2.VideoCapture(full_out)
    ret, thumb_frame = cap_full.read()
    cap_full.release()
    if ret:
        full_thumb = os.path.join(thumbs_dir, 'full.jpg')
        cv2.imwrite(full_thumb, thumb_frame)

    original = {
        'url': '/outputs/full.mp4',
        'thumbnailUrl': '/outputs/thumbnails/full.jpg'
    }

    # Second pass: split snippets and analyze correctness
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    segments = []

    for idx, (start, end) in enumerate(times, start=1):
        start_f = int(start * fps)
        end_f = int(end * fps)
        snippet_path = os.path.join(snippets_dir, f'squat_{idx}.mp4')
        writer = cv2.VideoWriter(snippet_path, fourcc, fps, (width, height))

        # Write snippet frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)
        for f in range(start_f, end_f + 1):
            ret, frm = cap.read()
            if not ret:
                break
            writer.write(frm)
        writer.release()

        # Extract thumbnail for snippet
        cap_snip = cv2.VideoCapture(snippet_path)
        ret2, frm2 = cap_snip.read()
        cap_snip.release()
        thumb_path = os.path.join(thumbs_dir, f'squat_{idx}.jpg')
        if ret2:
            cv2.imwrite(thumb_path, frm2)

        # Analyze correctness: depth, knee cave, and knees over toes
        cap_an = cv2.VideoCapture(snippet_path)
        depth_ok = True
        knees_ok = True
        toes_ok = True
        while True:
            ret3, frame3 = cap_an.read()
            if not ret3:
                break
            _, res_snip = mediapipe_detection(frame3, holistic)
            # depth
            if not is_depth_sufficient(res_snip):
                depth_ok = False
            # knee cave
            if is_knee_cave(res_snip):
                knees_ok = False
            # knees over toes
            if are_knees_over_toes(res_snip):
                toes_ok = False
        cap_an.release()

        is_correct = depth_ok and knees_ok and toes_ok
        # For future detail, include individual checks
        segments.append({
            'id': str(uuid4()),
            'segmentNumber': idx,
            'url': f'/outputs/snippets/squat_{idx}.mp4',
            'thumbnailUrl': f'/outputs/thumbnails/squat_{idx}.jpg',
            'startTime': start,
            'endTime': end,
            'isCorrect': is_correct,
            'depth_ok': depth_ok,
            'knees_ok': knees_ok,
            'toes_ok': toes_ok
        })

    cap.release()

    return {
        'originalVideo': original,
        'videoSegments': segments
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Process a squat video into per-rep snippets'
    )
    parser.add_argument('input', help='Path to input video file')
    parser.add_argument(
        '--output_dir',
        default='outputs',
        help='Base directory for outputs (snippets, thumbnails, etc.)'
    )
    args = parser.parse_args()

    result = process_video(args.input, args.output_dir)
    print("✅  Processing complete.")
    print(result)
