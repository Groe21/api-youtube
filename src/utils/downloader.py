import yt_dlp
import os
from flask import current_app

def download_youtube_audio(url):
    try:
        # Ruta de descargas absoluta
        output_path = os.path.abspath(current_app.config.get(
            "DOWNLOADS_PATH", "/var/www/api-youtube/downloads"
        ))
        os.makedirs(output_path, exist_ok=True)

        # Verificación de permisos tipo Nextcloud (lectura/escritura/ejecución para todos)
        os.chmod(output_path, 0o777)

        # Debug: usuario actual y directorio de trabajo
        print("Guardando en:", output_path)
        print("Usuario actual UID:", os.getuid())
        print("Directorio actual:", os.getcwd())

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
                print("No se pudo obtener información del video.")
                return None

            filename = f"{info['title']}.mp3"
            final_file = os.path.join(output_path, filename)

            # Verificación de archivo y permisos
            if os.path.exists(final_file):
                os.chmod(final_file, 0o666)
                print(f"Archivo descargado y permisos ajustados: {final_file}")
            else:
                print("El archivo no se creó correctamente.")

            return filename

    except Exception as e:
        print(f"Error al descargar: {e}")
        return None

def download_music(url):
    return download_youtube_audio(url)
