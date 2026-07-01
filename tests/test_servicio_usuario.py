import sys
import os

# Agregar la ruta del proyecto al PATH de Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import ServicioUsuario, Usuario

class TestServicioUsuario:
    """Pruebas de integración para el ServicioUsuario"""

    def setup_method(self):
        """Se ejecuta antes de cada prueba"""
        self.servicio = ServicioUsuario()
        self.usuario_valido = Usuario("Juan Perez", "juan@mail.com", 25)

    def test_registrar_usuario_valido(self):
        """Test: registro exitoso de usuario válido"""
        resultado = self.servicio.registrar_usuario(self.usuario_valido)  # ← CAMBIADO
        assert resultado == True
        assert len(self.servicio.usuarios) == 1
        assert self.servicio.usuarios[0].nombre == "Juan Perez"
        assert self.servicio.usuarios[0].email == "juan@mail.com"

    def test_registrar_usuario_menor_edad(self):
        """Test: usuario menor de edad no debe registrarse"""
        usuario = Usuario("Pedro", "pedro@mail.com", 16)
        resultado = self.servicio.registrar_usuario(usuario)  # ← CAMBIADO
        assert resultado == False
        assert len(self.servicio.usuarios) == 0

    def test_registrar_usuario_sin_email(self):
        """Test: usuario sin email no debe registrarse"""
        usuario = Usuario("Ana", "", 30)
        resultado = self.servicio.registrar_usuario(usuario)  # ← CAMBIADO
        assert resultado == False
        assert len(self.servicio.usuarios) == 0

    def test_registrar_usuario_con_email_vacio(self):
        """Test: usuario con email vacío no debe registrarse"""
        usuario = Usuario("Carlos", "   ", 30)
        resultado = self.servicio.registrar_usuario(usuario)  # ← CAMBIADO
        assert resultado == False

    def test_buscar_por_email_existente(self):
        """Test: buscar usuario por email existente"""
        self.servicio.registrar_usuario(self.usuario_valido)  # ← CAMBIADO
        encontrado = self.servicio.buscar_por_email("juan@mail.com")
        assert encontrado is not None
        assert encontrado.nombre == "Juan Perez"
        assert encontrado.edad == 25

    def test_buscar_por_email_no_existente(self):
        """Test: buscar usuario por email no existente"""
        encontrado = self.servicio.buscar_por_email("noexiste@mail.com")
        assert encontrado is None

    def test_obtener_todos_los_usuarios(self):
        """Test: obtener lista de todos los usuarios"""
        self.servicio.registrar_usuario(self.usuario_valido)  # ← CAMBIADO
        usuario2 = Usuario("Maria", "maria@mail.com", 30)
        self.servicio.registrar_usuario(usuario2)  # ← CAMBIADO
        todos = self.servicio.obtener_todos()
        assert len(todos) == 2
        assert todos[0].nombre == "Juan Perez"
        assert todos[1].nombre == "Maria"