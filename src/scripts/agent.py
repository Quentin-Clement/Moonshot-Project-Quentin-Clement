import os
import sys
from mistralai import Mistral

# 1) load the LLM client
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("Please set MISTRAL_API_KEY in your environment.")
llm = Mistral(api_key=api_key)
MODEL = "mistral-large-latest"


def get_feedback_for_rep(idx: int, depth_ok: bool, knees_ok: bool, toes_ok: bool) -> str:
    prompt = (
        f"You are a fitness coach analyzing squat rep #{idx}.\n"
        f"- Depth OK? {depth_ok}\n"
        f"- Knee cave detected? {not knees_ok}\n"
        f"- Knees over toes? {not toes_ok}\n\n"
        "Give concise, actionable tips to improve form."
    )
    resp = llm.chat.complete(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an expert fitness coach."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def main(video_path: str, output_dir: str):
    # 2) import and run the video‐processing logic
    sys.path.append(os.getcwd())  # ensure Python can see main.py
    from main import process_video

    result = process_video(video_path, output_dir)

    # 3) for each segment, call the LLM
    for seg in result["videoSegments"]:
        fb = get_feedback_for_rep(
            seg["segmentNumber"],
            seg["depth_ok"],
            seg["knees_ok"],
            seg["toes_ok"]
        )
        seg["feedback"] = fb
        print(f"Rep {seg['segmentNumber']} feedback:\n{fb}\n")

    # 4) optionally: dump the full enriched JSON
    print("All reps with feedback:")
    print(result)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Run squat‐snippet processor + LLM feedback"
    )
    parser.add_argument("input", help="Path to input video file")
    parser.add_argument(
        "--output_dir", "-o",
        default="outputs",
        help="Where to write snippets & thumbnails"
    )
    args = parser.parse_args()
    main(args.input, args.output_dir)
