import sys
import os
import json

# Add backend to sys.path
backend_path = r'c:\Users\DDR\Documents\Django\GEN_AI_ASSISTANT\backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

from rag_pipeline.transcript_service import extract_video_id, get_transcript
from rag_pipeline.rag_qa import process_video_transcript

# Use a known educational video URL (Mosh's Python tutorial)
url = "https://www.youtube.com/watch?v=kqtD5dpn9C8"

print("--- Testing Video Learning Flow ---")

video_id = extract_video_id(url)
print(f"Extracted Video ID: {video_id}")

if video_id:
    print("Fetching transcript...")
    transcript = get_transcript(video_id)
    if transcript:
        print(f"Transcript fetched (length: {len(transcript)})")
        print("\nProcessing with Groq...")
        steps = process_video_transcript(transcript)
        
        print(f"\nGenerated {len(steps)} Learning Steps:")
        for step in steps:
            print(f"\n[Step {step.get('step')}] {step.get('title')}")
            print(f"Expl: {step.get('explanation')}")
            print(f"Q: {step.get('question')}")
            
        if len(steps) > 0:
            print("\nSUCCESS: Video processing flow verified.")
    else:
        print("FAILED: Transcript could not be fetched (no captions?)")
else:
    print("FAILED: Invalid video URL.")
