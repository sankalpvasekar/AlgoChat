import yt_dlp
import os

video_id = "dQw4w9WgXcQ"
url = f"https://www.youtube.com/watch?v={video_id}"
output_base = f"audio_{video_id}"

ydl_opts_m4a = {
    'format': 'm4a/bestaudio/best',
    'outtmpl': output_base + ".m4a",
    'quiet': False,
    'no_warnings': False,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'referer': 'https://www.google.com/',
    'extractor_args': {'youtube': {'player_client': ['android_web', 'web']}},
}

print(f"Testing yt-dlp download for {url}...")
try:
    with yt_dlp.YoutubeDL(ydl_opts_m4a) as ydl:
        ydl.download([url])
    
    if os.path.exists(output_base + ".m4a"):
        print("SUCCESS: Audio downloaded.")
        os.remove(output_base + ".m4a")
    else:
        print("FAILED: File not found after download.")
except Exception as e:
    print(f"ERROR: {e}")
