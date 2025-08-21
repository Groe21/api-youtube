import yt_dlp
import os
import subprocess
from flask import current_app

def download_and_convert_to_mp3(url):
    try:
        output_path = os.path.abspath(current_app.config.get("DOWNLOADS_PATH", "/var/www/api-youtube/downloads"))
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/temp_audio.%(ext)s',
            'ignoreerrors': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                print("No se pudo extraer info del video.")
                return None

            temp_file = None
            for f in os.listdir(output_path):
                if f.startswith("temp_audio."):
                    temp_file = os.path.join(output_path, f)
                    break

            if not temp_file:
                print("No se encontró el archivo temporal descargado.")
                return None

            mp3_filename = f"{info['title']}.mp3"
            mp3_path = os.path.join(output_path, mp3_filename)
            print(f"Convirtiendo {temp_file} a {mp3_path} ...")
            result = subprocess.run([
                "ffmpeg", "-y", "-i", temp_file, "-vn", "-ab", "192k", "-ar", "44100", "-f", "mp3", mp3_path
            ], capture_output=True, text=True)

            # Guarda el log de ffmpeg
            with open(os.path.join(output_path, "ffmpeg_last.log"), "w") as logf:
                logf.write("STDOUT ffmpeg:\n" + result.stdout)
                logf.write("\nSTDERR ffmpeg:\n" + result.stderr)

            if result.returncode != 0:
                print(f"Error en ffmpeg: {result.stderr}")
                return None

            os.remove(temp_file)
            print(f"Convertido a mp3: {mp3_path}")
            return mp3_filename

    except Exception as e:
        print(f"Error en la descarga/conversión: {e}")
        return None

def download_music(url):
    return download_and_convert_to_mp3(url)
