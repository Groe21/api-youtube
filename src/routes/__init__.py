from flask import Blueprint, request, render_template, send_from_directory, redirect, url_for
from utils.downloader import download_music
import os

routes = Blueprint('routes', __name__)

def convert_music_url(url):
    import re
    if "music.youtube.com" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
        if match:
            video_id = match.group(1)
            # Solo el ID, sin parámetros extra
            return f"https://www.youtube.com/watch?v={video_id}", True
    elif "youtube.com" in url:
        # Si el enlace tiene parámetros extra, quítalos
        match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/watch?v={video_id}", False
    return url, False

@routes.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return render_template('index.html', message="URL es requerida", message_type="danger")
    
    converted_url, was_music = convert_music_url(url)
    messages = []
    if was_music:
        messages.append("Enlace de YouTube Music detectado.")
        messages.append("Convirtiendo a enlace estándar de YouTube...")
    
    try:
        messages.append("Procediendo con la descarga...")
        filename = download_music(converted_url)
        if filename and filename.endswith('.mp3'):
            download_url = f"/downloads/{filename}"
            messages.append(f"Descarga completada: <a href='{download_url}' download class='btn btn-success'>Guardar en tu dispositivo</a>")
        else:
            messages.append(filename if filename else "Ocurrió un error al descargar.")
        return render_template('index.html', message="<br>".join(messages), message_type="success")
    except Exception as e:
        messages.append(f"Error con el enlace: {converted_url}. Detalle: {str(e)}")
        return render_template('index.html', message="<br>".join(messages), message_type="danger")

@routes.route('/downloads/<path:filename>')
def serve_download(filename):
    downloads_dir = os.path.join(os.path.dirname(__file__), '..', 'downloads')
    return send_from_directory(downloads_dir, filename, as_attachment=True)

@routes.route('/musicas')
def musicas():
    import os
    downloads_dir = os.path.join(os.path.dirname(__file__), '..', 'downloads')
    archivos = [f for f in os.listdir(downloads_dir) if f.endswith('.mp3')]
    return render_template('musicas.html', musicas=archivos)

@routes.route('/eliminar/<path:filename>', methods=['POST'])
def eliminar_musica(filename):
    import os
    downloads_dir = os.path.join(os.path.dirname(__file__), '..', 'downloads')
    file_path = os.path.join(downloads_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(request.referrer or url_for('routes.musicas'))