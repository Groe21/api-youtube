from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from utils.batch_downloader import download_multiple_songs, get_genres_and_songs
import time

app = Flask(__name__)
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
    
    return render_template('index.html', 
                         message=message, 
                         genres_data=genres_data,
                         downloaded=downloaded,
                         failed=failed,
                         skipped=skipped)

@app.route('/downloads/<genre>/<filename>')
def download_file(genre, filename):
    genre_path = os.path.join(BATCH_DOWNLOADS_PATH, genre)
    return send_from_directory(genre_path, filename, as_attachment=True)

@app.route('/delete/<genre>/<filename>', methods=['POST'])
def delete_file(genre, filename):
    file_path = os.path.join(BATCH_DOWNLOADS_PATH, genre, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)