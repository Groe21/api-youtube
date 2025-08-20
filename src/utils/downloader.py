import yt_dlp
import os
from flask import current_app

def download_youtube_audio(url):
    try:
        # Usamos la ruta absoluta de la app
        output_path = current_app.config.get("DOWNLOADS_PATH", "downloads")
        os.makedirs(output_path, exist_ok=True)  # por si no existe

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
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
