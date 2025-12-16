import os
import yt_dlp

def download_and_convert_to_mp3(url, output_path):
    os.makedirs(output_path, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiesfrombrowser': ('chrome',),  # Usa cookies del navegador
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            # Cambia la extensión a .mp3
            mp3_filename = os.path.splitext(os.path.basename(filename))[0] + '.mp3'
            return mp3_filename
    except Exception as e:
        print(f"Error al descargar: {e}")
        return None