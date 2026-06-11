from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)

# Conectar a MongoDB usando la variable de entorno
mongo_url = os.environ.get('DB_URL', 'mongodb://localhost:27017/')
client = MongoClient(mongo_url)
db = client['eventos']

@app.route('/')
def home():
    return 'Sistema de Gestión de Eventos Académicos - OK'

@app.route('/health')
def health():
    try:
        # Verificar conexión a la DB
        client.admin.command('ping')
        return 'App funcionando + DB conectada', 200
    except:
        return 'App funcionando pero DB no disponible', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)