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

# ========================================
# CÓDIGO AGREGADO PARA EL TP7 - TESTING
# ========================================

class Calculadora:
    """Clase calculadora para pruebas unitarias"""

    def sumar(self, a: int, b: int) -> int:
        return a + b

    def restar(self, a: int, b: int) -> int:
        return a - b

    def dividir(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("No se puede dividir por cero")
        return a / b

    def multiplicar(self, a: int, b: int) -> int:
        return a * b


class Usuario:
    """Clase usuario para pruebas"""

    def __init__(self, nombre: str, email: str, edad: int):
        self.nombre = nombre
        self.email = email
        self.edad = edad

    def es_mayor_de_edad(self) -> bool:
        return self.edad >= 18

    def get_saludo(self) -> str:
        return f"Hola, soy {self.nombre}"


class ServicioUsuario:
    def __init__(self):
        self.usuarios = []

    def registrar_usuario(self, usuario: Usuario) -> bool:  # ← DEBE SER registrar_usuario
        if not usuario:
            return False
        if not usuario.email or usuario.email.strip() == "":
            return False
        if not usuario.es_mayor_de_edad():
            return False
        self.usuarios.append(usuario)
        return True

    def buscar_por_email(self, email: str):
        for u in self.usuarios:
            if u.email == email:
                return u
        return None

    def obtener_todos(self):
        return self.usuarios