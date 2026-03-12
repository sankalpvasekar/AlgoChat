from youtube_transcript_api import YouTubeTranscriptApi
import json

video_id = "kqtD5dpn9C8"
print(f"DEBUG: Fetching for {video_id}...")

try:
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)
    snippet = fetched.snippets[0]
    print(f"Snippet type: {type(snippet)}")
    print(f"Snippet dir: {dir(snippet)}")
    if hasattr(snippet, 'text'):
        print(f"SUCCESS: snippet.text = {snippet.text[:50]}")
    else:
        print("FAILED: No 'text' attribute found.")
        
    try:
        print(f"Trying subscript: {snippet['text']}")
    except Exception as e:
        print(f"Subscript failed as expected: {e}")
        
except Exception as e:
    print(f"Error: {e}")
