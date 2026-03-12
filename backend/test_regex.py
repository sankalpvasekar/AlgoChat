import re

def extract_video_id(url):
    # More robust regex
    regex = r"(?:v=|\/|embed\/|shorts\/|youtu\.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
    "https://www.youtube.com/watch?index=1&v=dQw4w9WgXcQ",
    "youtube.com/v/dQw4w9WgXcQ"
]

for url in urls:
    print(f"URL: {url} -> ID: {extract_video_id(url)}")
