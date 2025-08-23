from flask import Flask

def create_app():
    app = Flask(__name__)

    from meu_app.rotas import bp as rotas_bp
    app.register_blueprint(rotas_bp)

    return app
