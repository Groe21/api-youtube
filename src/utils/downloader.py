import yt_dlp
import os
from flask import current_app

def download_youtube_audio(url):
    try:
        output_path = os.path.abspath(current_app.config.get("DOWNLOADS_PATH", "/var/www/api-youtube/downloads"))
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'ignoreerrors': True,
            'allow_unplayable_formats': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None
            filename = f"{info['title']}.mp3"
            print(f"Guardando en: {output_path}")
            print(f"Archivo final: {os.path.join(output_path, filename)}")
            return filename
    except Exception as e:
        print(f"Error al descargar: {e}")
        return None

def download_music(url):
    return download_youtube_audio(url)
