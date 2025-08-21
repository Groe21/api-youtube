import yt_dlp
import os
from flask import current_app

def download_music(url):
    try:
        output_path = os.path.abspath(current_app.config.get("DOWNLOADS_PATH", "/var/www/api-youtube/downloads"))
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ignoreerrors': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                print("No se pudo extraer info del video.")
                return None

            # Busca el archivo MP3 generado
            base_title = info['title']
            mp3_file = f"{base_title}.mp3"
            mp3_path = os.path.join(output_path, mp3_file)

            if os.path.exists(mp3_path):
                print(f"Descarga completada: {mp3_file}")
                return mp3_file
            else:
                print("No se generó el archivo MP3.")
                return None

    except Exception as e:
        print(f"Error en la descarga: {e}")
        return None
