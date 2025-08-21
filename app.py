from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from utils.downloader import download_and_convert_to_mp3

app = Flask(__name__)
DOWNLOADS_PATH = os.path.join(os.path.dirname(__file__), "downloads")

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
            message = "Ocurrió un error al descargar."
    musicas = [f for f in os.listdir(DOWNLOADS_PATH) if f.endswith('.mp3')]
    return render_template('index.html', musicas=musicas, message=message)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOADS_PATH, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)