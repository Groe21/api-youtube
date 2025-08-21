import yt_dlp
import os
import subprocess
from flask import current_app

def convert_webm_to_mp3(webm_path, mp3_path):
    try:
        # Convierte usando ffmpeg
        subprocess.run([
            "ffmpeg", "-y", "-i", webm_path, "-vn", "-ab", "192k", "-ar", "44100", "-f", "mp3", mp3_path
        ], check=True)
        return True
    except Exception as e:
        print(f"Error al convertir a mp3: {e}")
        return False

def download_youtube_audio(url):
    try:
        output_path = os.path.abspath(current_app.config.get("DOWNLOADS_PATH", "/var/www/api-youtube/downloads"))
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'ignoreerrors': True,
            'allow_unplayable_formats': True,
            'quiet': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return None
            # Detecta el archivo descargado
            base_title = info['title']
            webm_file = None
            for ext in ['webm', 'm4a', 'mp4']:
                candidate = f"{base_title}.{ext}"
                candidate_path = os.path.join(output_path, candidate)
                if os.path.exists(candidate_path):
                    webm_file = candidate_path
                    break
            if webm_file:
                mp3_file = os.path.join(output_path, f"{base_title}.mp3")
                print(f"Convirtiendo {webm_file} a {mp3_file} ...")
                if convert_webm_to_mp3(webm_file, mp3_file):
                    print(f"Convertido a mp3: {mp3_file}")
                    return f"{base_title}.mp3"
                else:
                    print("No se pudo convertir a mp3.")
                    return None
            else:
                print("No se encontró archivo descargado para convertir.")
                return None
    except Exception as e:
        print(f"Error al descargar: {e}")
        return None

def download_music(url):
    return download_youtube_audio(url)
