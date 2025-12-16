import os
import yt_dlp
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

def download_multiple_songs(urls, output_path, genre="General"):
    """
    Descarga múltiples canciones y las agrupa por género
    """
    os.makedirs(output_path, exist_ok=True)
    genre_folder = os.path.join(output_path, genre)
    os.makedirs(genre_folder, exist_ok=True)
    
    # Obtener lista de canciones ya descargadas
    existing_files = set([f for f in os.listdir(genre_folder) if f.endswith('.mp3')])
    
    downloaded_files = []
    failed_urls = []
    skipped_files = []
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(genre_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiesfrombrowser': ('chrome',),
        'quiet': True,
        'no_warnings': True,
    }
    
    for url in urls:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Primero extrae info sin descargar
                info = ydl.extract_info(url, download=False)
                mp3_filename = f"{info['title']}.mp3"
                
                # Verificar si ya existe
                if mp3_filename in existing_files:
                    skipped_files.append(mp3_filename)
                    print(f"⚠️ Ya existe: {mp3_filename}")
                    continue
                
                # Descargar si no existe
                ydl.download([url])
                
                # Agregar metadatos de género
                mp3_path = os.path.join(genre_folder, mp3_filename)
                if os.path.exists(mp3_path):
                    try:
                        audio = EasyID3(mp3_path)
                        audio['genre'] = genre
                        audio.save()
                    except:
                        pass
                
                downloaded_files.append(mp3_filename)
                
        except Exception as e:
            print(f"Error al descargar {url}: {e}")
            failed_urls.append(url)
    
    return downloaded_files, failed_urls, skipped_files

def get_genres_and_songs(output_path):
    """
    Obtiene todos los géneros y sus canciones
    """
    genres = {}
    if not os.path.exists(output_path):
        return genres
    
    for genre in os.listdir(output_path):
        genre_path = os.path.join(output_path, genre)
        if os.path.isdir(genre_path):
            songs = [f for f in os.listdir(genre_path) if f.endswith('.mp3')]
            genres[genre] = songs
    
    return genres