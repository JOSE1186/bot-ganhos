from app import app  # importa o Flask já configurado e com as rotas

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 