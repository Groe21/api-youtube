# Mini Flask YouTube Downloader

Este proyecto es una mini aplicación web construida con Flask que permite a los usuarios descargar música de YouTube en formato MP3. Simplemente proporciona la URL del video y la aplicación se encargará del resto.

## Estructura del Proyecto

```
mini-flask-youtube-downloader
├── src
│   ├── app.py               # Punto de entrada de la aplicación Flask
│   ├── routes
│   │   └── __init__.py      # Definición de las rutas de la aplicación
│   └── utils
│       └── downloader.py     # Funciones para descargar música de YouTube
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Documentación del proyecto
```

## Requisitos

Asegúrate de tener Python instalado en tu sistema. Este proyecto utiliza las siguientes dependencias:

- Flask
- [Biblioteca para descargar videos de YouTube] (especificar la biblioteca en requirements.txt)

## Instalación

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd mini-flask-youtube-downloader
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Ejecución

Para ejecutar la aplicación, utiliza el siguiente comando:

```
python src/app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`.

## Uso

1. Abre tu navegador y ve a `http://127.0.0.1:5000`.
2. Ingresa la URL del video de YouTube que deseas descargar.
3. Haz clic en el botón de descarga y espera a que se complete el proceso.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto, siéntete libre de abrir un issue o enviar un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.