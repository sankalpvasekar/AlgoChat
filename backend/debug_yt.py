from youtube_transcript_api import YouTubeTranscriptApi
import sys

video_id = "dQw4w9WgXcQ"

try:
    ytt = YouTubeTranscriptApi()
    fetched_transcript = ytt.fetch(video_id)
    print(f"FetchedTranscript dir: {dir(fetched_transcript)}")
    
    if hasattr(fetched_transcript, 'snippets'):
        print("Attribute 'snippets' EXISTS.")
        print(f"Type of .snippets: {type(fetched_transcript.snippets)}")
    else:
        print("Attribute 'snippets' DOES NOT EXIST.")
    
except Exception as e:
    print(f"Error: {e}")
