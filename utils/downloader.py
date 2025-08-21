import yt_dlp
import os
import subprocess

def download_and_convert_to_mp3(url, output_path):
    os.makedirs(output_path, exist_ok=True)
    temp_file = os.path.join(output_path, "temp_audio.webm")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_file,
        'ignoreerrors': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            return None
        mp3_filename = f"{info['title']}.mp3"
        mp3_path = os.path.join(output_path, mp3_filename)
        result = subprocess.run([
            "ffmpeg", "-y", "-i", temp_file, "-vn", "-ab", "192k", "-ar", "44100", "-f", "mp3", mp3_path
        ], capture_output=True, text=True)
        os.remove(temp_file)
        if result.returncode != 0:
            return None
        return mp3_filename