# Music Downloader - YouTube Batch Downloader

Aplicación web Flask para descargar música de YouTube en lotes organizadas por géneros.

## Características

- ✅ Descarga múltiples canciones de YouTube a la vez
- 📁 Organización automática por géneros musicales
- 🎵 Conversión automática a MP3
- 🔍 Detección de duplicados
- 📊 Visualización de colección por género
- 🗑️ Gestión de archivos (descargar/eliminar)

## Instalación

### Requisitos
- Python 3.8+
- FFmpeg
- spotdl (opcional)

### En Ubuntu Server

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git ffmpeg

# Clonar repositorio
cd /var/www
sudo git clone https://github.com/Groe21/api-youtube.git
cd api-youtube

# Dar permisos
sudo chown -R $USER:$USER /var/www/api-youtube

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
pip install -r requirements.txt

# Crear directorios
mkdir -p batch_downloads
```

## Configuración con Nginx y Systemd

### Crear servicio systemd
```bash
sudo nano /etc/systemd/system/youtube-api.service
```

Contenido:
```ini
[Unit]
Description=YouTube API Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/api-youtube
Environment="PATH=/var/www/api-youtube/venv/bin"
ExecStart=/var/www/api-youtube/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl start youtube-api
sudo systemctl enable youtube-api
```

### Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/youtube-api
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu_ip_o_dominio;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/api-youtube/static;
    }

    location /downloads {
        alias /var/www/api-youtube/batch_downloads;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/youtube-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Uso

1. Accede a la aplicación en tu navegador: `http://tu_ip`
2. Ingresa las URLs de YouTube (una por línea)
3. Selecciona un género existente o crea uno nuevo
4. Haz clic en "Descargar Todo"
5. Las canciones se descargarán y organizarán automáticamente

## Estructura del Proyecto

```
api-youtube/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── templates/
│   └── index.html        # Interfaz web
├── static/
│   └── css/
│       └── bootstrap.min.css
├── utils/
│   └── batch_downloader.py  # Lógica de descarga por lotes
└── batch_downloads/       # Archivos descargados organizados por género
    ├── Rock/
    ├── Pop/
    └── ...
```

## Licencia

MIT
