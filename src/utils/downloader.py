import yt_dlp

def download_youtube_audio(url, output_path='downloads'):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return f"Descarga completada: {info['title']}.mp3"
    except Exception as e:
        return f"Ocurrió un error: {str(e)}"

def download_music(url):
    return download_youtube_audio(url)