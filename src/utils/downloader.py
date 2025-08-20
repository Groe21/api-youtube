import yt_dlp
import os
from flask import current_app

def download_youtube_audio(url):
    try:
        output_path = os.path.abspath(current_app.config.get("DOWNLOADS_PATH"))
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'ignoreerrors': True,  # Ignora errores de streams no descargables
            'allow_unplayable_formats': True,  # Permite streams que podrían no reproducirse directamente
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = f"{info['title']}.mp3"
            return filename
    except Exception as e:
        print(f"Error al descargar: {e}")
        return None

def download_music(url):
    return download_youtube_audio(url)