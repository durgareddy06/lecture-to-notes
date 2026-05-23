import os
import subprocess

def extract_audio(video_path: str, output_dir: str) -> str:
    """Extract audio from video using FFmpeg."""
    audio_path = os.path.join(output_dir, "audio.wav")
    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")
    return audio_path
