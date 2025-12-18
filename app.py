from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import os
import json
import subprocess
import hmac
import hashlib
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

@app.route('/delete/<genre>/<filename>', methods=['POST'])
def delete_file(genre, filename):
    file_path = os.path.join(BATCH_DOWNLOADS_PATH, genre, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))

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