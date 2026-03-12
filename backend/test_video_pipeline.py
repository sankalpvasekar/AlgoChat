from rag_pipeline.rag_qa import process_video_transcript
import json

transcript = "[♪♪♪] ♪ We're no strangers to love ♪ ♪ You know the rules and so do I ♪ ♪ A full commitment's what I'm thinking of ♪ ♪ You wouldn't get this from any other guy ♪ ♪ I just wanna tell you how I'm feelin..."

print("Testing process_video_transcript...")
try:
    steps = process_video_transcript(transcript)
    print(f"SUCCESS! Generated {len(steps)} steps.")
    print(json.dumps(steps, indent=2))
except Exception as e:
    print(f"ERROR: {e}")
