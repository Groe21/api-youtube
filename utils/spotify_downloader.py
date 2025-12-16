import os
import subprocess

def download_spotify_mp3(url, output_path):
    os.makedirs(output_path, exist_ok=True)
    # Usa spotdl para descargar el archivo en la carpeta indicada
    try:
        result = subprocess.run([
            "spotdl", url, "--output", output_path
        ], capture_output=True, text=True)
        # Busca el archivo mp3 descargado
        files = [f for f in os.listdir(output_path) if f.endswith('.mp3')]
        if files:
            return files[-1]  # Retorna el nombre del último archivo descargado
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None