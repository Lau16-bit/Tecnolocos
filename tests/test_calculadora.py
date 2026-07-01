import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app import Calculadora

# Resto del código igual...
import pytest
from app import Calculadora

class TestCalculadora:
    """Pruebas unitarias para la clase Calculadora"""

    def setup_method(self):
        """Se ejecuta antes de cada prueba"""
        self.calc = Calculadora()

    def test_sumar_positivos(self):
        """Test: suma de dos números positivos"""
        # Given
        a, b = 5, 3
        # When
        resultado = self.calc.sumar(a, b)
        # Then
        assert resultado == 8

    def test_sumar_negativos(self):
        """Test: suma de números negativos"""
        assert self.calc.sumar(-2, -3) == -5

    def test_sumar_cero(self):
        """Test: suma con cero"""
        assert self.calc.sumar(5, 0) == 5

    def test_restar(self):
        """Test: resta de dos números"""
        assert self.calc.restar(5, 3) == 2

    def test_restar_negativos(self):
        """Test: resta con números negativos"""
        assert self.calc.restar(-5, -3) == -2

    def test_dividir_exacta(self):
        """Test: división exacta"""
        assert self.calc.dividir(6, 3) == 2

    def test_dividir_por_cero(self):
        """Test: división por cero debe lanzar excepción"""
        with pytest.raises(ValueError, match="No se puede dividir por cero"):
            self.calc.dividir(5, 0)

    def test_multiplicar(self):
        """Test: multiplicación de dos números"""
        assert self.calc.multiplicar(3, 5) == 15

    def test_multiplicar_por_cero(self):
        """Test: multiplicación por cero"""
        assert self.calc.multiplicar(5, 0) == 0