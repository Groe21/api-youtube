from flask import Blueprint, request, render_template
from utils.downloader import download_music

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
        result = download_music(converted_url)
        messages.append(result)
        return render_template('index.html', message="<br>".join(messages), message_type="success")
    except Exception as e:
        messages.append(f"Error con el enlace: {converted_url}. Detalle: {str(e)}")
        return render_template('index.html', message="<br>".join(messages), message_type="danger")