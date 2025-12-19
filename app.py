from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import os
import json
import subprocess
import hmac
import hashlib
import yt_dlp
from utils.batch_downloader import download_multiple_songs, get_genres_and_songs
import time

app = Flask(__name__)
BATCH_DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), "batch_downloads")
PLAYLISTS_FILE = os.path.join(os.path.dirname(__file__), "playlists.json")
LIKES_FILE = os.path.join(os.path.dirname(__file__), "likes.json")

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

@app.route('/api/delete/<genre>/<filename>', methods=['DELETE'])
def delete_file(genre, filename):
    """Eliminar archivo de música"""
    try:
        file_path = os.path.join(BATCH_DOWNLOADS_PATH, genre, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            # Invalidar cache
            genres_cache['timestamp'] = 0
            return jsonify({'success': True, 'message': 'Archivo eliminado'})
        else:
            return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/genre/<genre>', methods=['DELETE'])
def delete_genre(genre):
    """Eliminar género completo (solo si está vacío)"""
    try:
        genre_path = os.path.join(BATCH_DOWNLOADS_PATH, genre)
        
        if not os.path.exists(genre_path):
            return jsonify({'success': False, 'error': 'Género no encontrado'}), 404
        
        # Verificar que esté vacío
        files = [f for f in os.listdir(genre_path) if f.endswith('.mp3')]
        if files:
            return jsonify({'success': False, 'error': 'El género contiene canciones'}), 400
        
        # Eliminar carpeta
        os.rmdir(genre_path)
        
        # Invalidar cache
        genres_cache['timestamp'] = 0
        
        return jsonify({'success': True, 'message': 'Género eliminado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API para streaming/reproducción
@app.route('/stream/<genre>/<filename>')
def stream_file(genre, filename):
    """Endpoint para streaming de audio"""
    genre_path = os.path.join(BATCH_DOWNLOADS_PATH, genre)
    return send_from_directory(genre_path, filename)

# API para playlists
def load_playlists():
    if os.path.exists(PLAYLISTS_FILE):
        with open(PLAYLISTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_playlists(playlists):
    with open(PLAYLISTS_FILE, 'w') as f:
        json.dump(playlists, f, indent=2)

@app.route('/api/playlists', methods=['GET', 'POST'])
def manage_playlists():
    if request.method == 'GET':
        return jsonify(load_playlists())
    elif request.method == 'POST':
        data = request.json
        playlists = load_playlists()
        playlist_name = data.get('name')
        if playlist_name:
            playlists[playlist_name] = []
            save_playlists(playlists)
            return jsonify({'success': True, 'playlists': playlists})
        return jsonify({'success': False})

@app.route('/api/playlists/<playlist_name>/songs', methods=['POST', 'DELETE'])
def manage_playlist_songs(playlist_name):
    playlists = load_playlists()
    data = request.json
    
    if request.method == 'POST':
        # Agregar canción a playlist
        if playlist_name not in playlists:
            playlists[playlist_name] = []
        song = {
            'genre': data.get('genre'),
            'filename': data.get('filename')
        }
        if song not in playlists[playlist_name]:
            playlists[playlist_name].append(song)
            save_playlists(playlists)
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        # Remover canción de playlist
        if playlist_name in playlists:
            song = {
                'genre': data.get('genre'),
                'filename': data.get('filename')
            }
            if song in playlists[playlist_name]:
                playlists[playlist_name].remove(song)
                save_playlists(playlists)
        return jsonify({'success': True})

# API para likes
def load_likes():
    if os.path.exists(LIKES_FILE):
        with open(LIKES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_likes(likes):
    with open(LIKES_FILE, 'w') as f:
        json.dump(likes, f, indent=2)

@app.route('/api/likes', methods=['GET', 'POST', 'DELETE'])
def manage_likes():
    likes = load_likes()
    
    if request.method == 'GET':
        return jsonify(likes)
    
    elif request.method == 'POST':
        data = request.json
        song = {
            'genre': data.get('genre'),
            'filename': data.get('filename')
        }
        if song not in likes:
            likes.append(song)
            save_likes(likes)
        return jsonify({'success': True, 'likes': likes})
    
    elif request.method == 'DELETE':
        data = request.json
        song = {
            'genre': data.get('genre'),
            'filename': data.get('filename')
        }
        if song in likes:
            likes.remove(song)
            save_likes(likes)
        return jsonify({'success': True, 'likes': likes})

# YouTube Search API
@app.route('/api/search', methods=['POST'])
def search_youtube():
    """Buscar videos en YouTube"""
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
            videos = []
            if result and 'entries' in result:
                for entry in result['entries']:
                    if entry and entry.get('id'):
                        # Formatear duración
                        duration = entry.get('duration', 0)
                        if duration:
                            minutes = int(duration) // 60
                            seconds = int(duration) % 60
                            duration_str = f"{minutes}:{seconds:02d}"
                        else:
                            duration_str = "N/A"
                        
                        # Obtener mejor thumbnail
                        thumbnails = entry.get('thumbnails', [])
                        thumbnail_url = ''
                        if thumbnails:
                            thumbnail_url = thumbnails[-1].get('url', '')
                        elif entry.get('thumbnail'):
                            thumbnail_url = entry.get('thumbnail')
                        else:
                            thumbnail_url = f"https://img.youtube.com/vi/{entry.get('id')}/mqdefault.jpg"
                        
                        videos.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Sin título'),
                            'channel': entry.get('uploader', entry.get('channel', 'Desconocido')),
                            'thumbnail': thumbnail_url,
                            'duration': duration_str,
                            'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                        })
            
            return jsonify({'success': True, 'results': videos})
            
    except Exception as e:
        print(f"Error en búsqueda: {str(e)}")  # Para debugging
        return jsonify({'error': str(e)}), 500

# Download from search
@app.route('/api/download-from-search', methods=['POST'])
def download_from_search():
    """Descargar video desde búsqueda de YouTube"""
    data = request.get_json()
    url = data.get('url', '')
    genre = data.get('genre', 'General')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Crear carpeta del género si no existe
        genre_folder = os.path.join(BATCH_DOWNLOADS_PATH, genre)
        os.makedirs(genre_folder, exist_ok=True)
        
        # Opciones para yt-dlp con FFmpeg
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(genre_folder, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'keepvideo': False,
            'writethumbnail': False,
            'overwrites': True,
            'ffmpeg_location': '/usr/bin/ffmpeg',  # Ubicación de FFmpeg
        }
        
        print(f"Descargando en: {genre_folder}")
        print(f"URL: {url}")
        
        # Descargar
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Descarga completada: {info.get('title', 'Unknown')}")
        
        # Invalidar cache
        genres_cache['timestamp'] = 0
        
        return jsonify({'success': True, 'message': 'Download completed'})
        
    except Exception as e:
        print(f"Error en descarga: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Webhook para auto-deployment
@app.route('/webhook/deploy', methods=['POST'])
def deploy():
    """Endpoint para auto-deployment desde GitHub"""
    
    # Opcional: Verificar secreto de GitHub para seguridad
    # secret = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
    # if secret:
    #     signature = request.headers.get('X-Hub-Signature-256')
    #     if signature:
    #         mac = hmac.new(secret.encode(), request.data, hashlib.sha256)
    #         if not hmac.compare_digest('sha256=' + mac.hexdigest(), signature):
    #             return jsonify({'error': 'Invalid signature'}), 403
    
    try:
        # Ejecutar git pull
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Reiniciar servicio si estamos en producción
        if os.path.exists('/var/www/api-youtube'):
            subprocess.run(['sudo', 'systemctl', 'restart', 'youtube-api'], timeout=10)
        
        return jsonify({
            'success': True,
            'message': 'Deployment successful',
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }), 200
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Deployment timeout'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)