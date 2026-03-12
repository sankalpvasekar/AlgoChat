from rag_pipeline.whisper_service import get_whisper_transcript
import os

# Use a valid video ID (Mosh Python)
test_id = "kqtD5dpn9C8" 
print(f"Testing Whisper Service with valid video {test_id}...")
text = get_whisper_transcript(test_id)
if text:
    print(f"SUCCESS! Transcript length: {len(text)}")
    print(f"Sample: {text[:500]}...")
else:
    print("FAILED: No transcript generated.")
