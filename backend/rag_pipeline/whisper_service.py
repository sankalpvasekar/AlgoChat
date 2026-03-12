import os
import yt_dlp
from groq import Groq
from dotenv import load_dotenv

# Use absolute path to .env relative to this file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env')
load_dotenv(env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_whisper_transcript(video_id):
    """
    Downloads audio from YouTube and transcribes it using Groq Whisper.
    Returns the transcript text or None if failed.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_base = f"audio_{video_id}"
    
    # Updated options for better compatibility and NO requirement for ffmpeg
    ydl_opts_m4a = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': output_base + ".m4a",
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'extractor_args': {'youtube': {'player_client': ['web', 'android', 'ios', 'mweb']}},
        'force_ipv4': True,
    }
    
    audio_file = None
    
    try:
        print(f"DEBUG: Attempting to download audio for {video_id}...")
        
        # Download M4A directly (usually doesn't need ffmpeg)
        with yt_dlp.YoutubeDL(ydl_opts_m4a) as ydl:
            ydl.download([url])
            
        if os.path.exists(f"{output_base}.m4a"):
            audio_file = f"{output_base}.m4a"
                
        if not audio_file:
            print("DEBUG: Failed to download audio.")
            return None

        file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
        print(f"DEBUG: Downloaded {audio_file} ({file_size_mb:.2f} MB)")
        
        if file_size_mb > 25:
            # We don't have ffmpeg installed to compress, so we must warn
            print("CRITICAL: File size exceeds 25MB limit and ffmpeg is not available for compression.")
            return "Error: Video audio is too large ( > 25MB) for transcription fallback. Please try a shorter video or one with captions."

        with open(audio_file, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file, file.read()),
                model="whisper-large-v3",
                response_format="json",
            )
            return transcription.text
            
    except Exception as e:
        print(f"Whisper transcription error for {video_id}: {str(e)}")
        return None
    finally:
        if audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except Exception as e:
                print(f"DEBUG: Failed to remove temporary file {audio_file}: {e}")

if __name__ == "__main__":
    # Test with a known short video ID
    test_id = "vNp_6Y7G094" # A short test video
    print("Testing Whisper Service...")
    text = get_whisper_transcript(test_id)
    print(f"Result: {text[:200]}..." if text else "Failed.")
