from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from utils.downloader import download_and_convert_to_mp3
# Importa tu función de descarga de Spotify
from utils.spotify_downloader import download_spotify_mp3
from utils.batch_downloader import download_multiple_songs, get_genres_and_songs
import time

app = Flask(__name__)
DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), "downloads")
SPOTIFY_DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), "spotify_downloads")
BATCH_DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), "batch_downloads")

# Variable global para cache
genres_cache = {'data': {}, 'timestamp': 0}
CACHE_DURATION = 60  # segundos

def get_genres_cached(output_path):
    """Obtiene géneros con cache de 60 segundos"""
    current_time = time.time()
    
    # Si el cache es válido, retornar datos en cache
    if current_time - genres_cache['timestamp'] < CACHE_DURATION:
        return genres_cache['data']
    
    # Si no, actualizar cache
    genres_data = get_genres_and_songs(output_path)
    genres_cache['data'] = genres_data
    genres_cache['timestamp'] = current_time
    
    return genres_data

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    converted = False
    url = ""
    if request.method == 'POST':
        url = request.form.get('url')
        if url and "music.youtube.com" in url:
            url = url.replace("music.youtube.com", "www.youtube.com")
            converted = True
        filename = download_and_convert_to_mp3(url, DOWNLOADS_PATH)
        if filename:
            if converted:
                message = f"Enlace de YouTube Music convertido a YouTube normal. Descarga completada: {filename}"
            else:
                message = f"Descarga completada: {filename}"
        else:
            if converted:
                message = "Enlace de YouTube Music convertido a YouTube normal. Ocurrió un error al descargar."
            else:
                message = "Ocurrió un error al descargar."
    musicas = [f for f in os.listdir(DOWNLOADS_PATH) if f.endswith('.mp3')]
    musicas.sort(key=lambda x: os.path.getmtime(os.path.join(DOWNLOADS_PATH, x)), reverse=True)  # Ordena por fecha de modificación, más reciente primero
    return render_template('index.html', musicas=musicas, message=message)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOADS_PATH, filename, as_attachment=True)

@app.route('/spotify', methods=['GET', 'POST'])
def spotify():
    SPOTIFY_DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), "spotify_downloads")
    os.makedirs(SPOTIFY_DOWNLOADS_PATH, exist_ok=True)  # <-- CREA LA CARPETA SI NO EXISTE
    message = None
    if request.method == 'POST':
        url = request.form.get('url')
        filename = download_spotify_mp3(url, SPOTIFY_DOWNLOADS_PATH)
        if filename:
            message = f"Descarga completada: {filename}"
        else:
            message = "Ocurrió un error al descargar."
    musicas = [f for f in os.listdir(SPOTIFY_DOWNLOADS_PATH) if f.endswith('.mp3')]
    return render_template('spotify.html', musicas=musicas, message=message)

@app.route('/spotify_downloads/<filename>')
def download_spotify_file(filename):
    return send_from_directory(SPOTIFY_DOWNLOADS_PATH, filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(DOWNLOADS_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))

@app.route('/delete_spotify/<filename>', methods=['POST'])
def delete_spotify_file(filename):
    file_path = os.path.join(SPOTIFY_DOWNLOADS_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('spotify'))

@app.route('/batch', methods=['GET', 'POST'])
def batch():
    message = None
    downloaded = []
    failed = []
    skipped = []
    
    if request.method == 'POST':
        urls_text = request.form.get('urls')
        genre = request.form.get('genre', 'General')
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if urls:
            downloaded, failed, skipped = download_multiple_songs(urls, BATCH_DOWNLOADS_PATH, genre)
            
            msg_parts = []
            if downloaded:
                msg_parts.append(f"✅ {len(downloaded)} nuevas")
            if skipped:
                msg_parts.append(f"⚠️ {len(skipped)} omitidas")
            if failed:
                msg_parts.append(f"❌ {len(failed)} fallaron")
            
            message = ". ".join(msg_parts) + "."
            
            # Invalidar cache después de descargar
            genres_cache['timestamp'] = 0
    
    # Usar cache para cargar géneros
    genres_data = get_genres_cached(BATCH_DOWNLOADS_PATH)
    
    return render_template('batch.html', 
                         message=message, 
                         genres_data=genres_data,
                         downloaded=downloaded,
                         failed=failed,
                         skipped=skipped)

@app.route('/batch_downloads/<genre>/<filename>')
def download_batch_file(genre, filename):
    genre_path = os.path.join(BATCH_DOWNLOADS_PATH, genre)
    return send_from_directory(genre_path, filename, as_attachment=True)

@app.route('/delete_batch/<genre>/<filename>', methods=['POST'])
def delete_batch_file(genre, filename):
    file_path = os.path.join(BATCH_DOWNLOADS_PATH, genre, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('batch'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)