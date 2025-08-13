# Mini Flask YouTube Downloader

Este proyecto es una mini aplicación web construida con Flask que permite a los usuarios descargar música de YouTube en formato MP3. Simplemente proporciona la URL del video y la aplicación se encargará del resto.

## Estructura del Proyecto

```
api-youtube
├── src
│   ├── app.py                 # Punto de entrada de la aplicación Flask
│   ├── downloads/             # Carpeta donde se guardan los MP3 descargados
│   ├── routes/
│   │   └── __init__.py        # Definición de las rutas de la aplicación
│   ├── static/
│   │   └── style.css          # Estilos personalizados
│   ├── templates/
│   │   └── index.html         # Plantilla principal de la app
│   └── utils/
│       └── downloader.py      # Funciones para descargar música de YouTube
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación del proyecto
```

## Requisitos

- Python 3.x
- pip
- ffmpeg (para conversión a MP3)

## Instalación en Ubuntu (paso a paso)

1. **Actualiza los paquetes e instala ffmpeg:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

2. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Groe21/api-youtube.git
   cd api-youtube
   ```

3. **Crea un entorno virtual (opcional pero recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instala las dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecuta la aplicación:**
   ```bash
   python src/app.py
   ```

La aplicación estará disponible en [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Uso

1. Abre tu navegador y ve a `http://127.0.0.1:5000`.
2. Ingresa la URL del video de YouTube que deseas descargar.
3. Haz clic en el botón de descarga y espera a que se complete el proceso.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto, siéntete libre de abrir un issue o enviar un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.