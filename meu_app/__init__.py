from flask import Flask
from .rotas import registrar_rotas

app = Flask(__name__)
app.secret_key = "chave-secreta-super-segura"

# Registrar todas as rotas
registrar_rotas(app)
