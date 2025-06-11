import json
from main import process_video

# point these at a local squat video and an output folder
INPUT_VIDEO = "/Users/quentin/Desktop/test.mp4"
OUTPUT_DIR  = "outputs"

if __name__ == "__main__":
    result = process_video(input_path=INPUT_VIDEO, output_dir=OUTPUT_DIR)
    # pretty-print the JSON so you can see if 'tips' is there for each segment
    print(json.dumps(result, indent=2))