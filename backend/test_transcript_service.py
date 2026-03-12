from rag_pipeline.transcript_service import get_transcript, extract_video_id
import sys

test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = extract_video_id(test_url)

print(f"Testing get_transcript for video_id: {video_id}...")
try:
    transcript = get_transcript(video_id)
    if transcript:
        print("SUCCESS! Transcript extracted.")
        print(f"Length: {len(transcript)} characters.")
        print(f"Start: {transcript[:200]}...")
    else:
        print("FAILED: Transcript returned None.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
