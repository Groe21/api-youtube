import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from routes import routes
from flask import Flask, render_template

def create_app():
    # Crear la app Flask
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Registrar blueprint de rutas
    app.register_blueprint(routes)

    # Configurar carpeta de descargas (funciona en local y en servidor)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DOWNLOADS_PATH = os.path.join(BASE_DIR, "downloads")
    os.makedirs(DOWNLOADS_PATH, exist_ok=True)

    # Guardamos en la config de Flask para usar en cualquier parte
    app.config["DOWNLOADS_PATH"] = DOWNLOADS_PATH

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
