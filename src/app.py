from flask import Flask, render_template
from src.routes import routes

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Registrar blueprint de rutas
    app.register_blueprint(routes)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)