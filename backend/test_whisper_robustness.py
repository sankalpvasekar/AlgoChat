from rag_pipeline.whisper_service import get_whisper_transcript
import sys

video_id = "dQw4w9WgXcQ" # Available video

print(f"Testing Whisper download for video_id: {video_id}...")
try:
    text = get_whisper_transcript(video_id)
    if text:
        print("SUCCESS! Whisper transcription received.")
        print(f"Transcript: {text[:200]}...")
    else:
        print("FAILED: Whisper returned None.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
