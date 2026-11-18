
"""Pruebas automáticas de los métodos de integración numérica."""

import numpy as np
import pytest

from src.integracion import trapecio_compuesto, simpson_compuesto


def test_trapecio_funcion_constante():
    """Integral de 3 entre 0 y 4: resultado exacto 12."""
    x = [0, 1, 2, 3, 4]
    y = [3, 3, 3, 3, 3]

    assert trapecio_compuesto(x, y) == pytest.approx(12)


def test_trapecio_funcion_lineal():
    """Integral de 2x entre 0 y 3: resultado exacto 9."""
    x = [0, 1, 2, 3]
    y = [0, 2, 4, 6]

    assert trapecio_compuesto(x, y) == pytest.approx(9)


def test_trapecio_pasos_no_uniformes():
    """El método admite subintervalos de diferentes tamaños."""
    x = [0, 1, 3]
    y = [0, 2, 6]

    assert trapecio_compuesto(x, y) == pytest.approx(9)


def test_simpson_funcion_cuadratica():
    """Integral de x² entre 0 y 2: resultado exacto 8/3."""
    x = [0, 0.5, 1, 1.5, 2]
    y = np.array(x) ** 2

    assert simpson_compuesto(x, y) == pytest.approx(8 / 3)


def test_simpson_funcion_cubica():
    """Integral de x³ entre 0 y 2: resultado exacto 4."""
    x = [0, 0.5, 1, 1.5, 2]
    y = np.array(x) ** 3

    assert simpson_compuesto(x, y) == pytest.approx(4)


def test_simpson_rechaza_intervalos_impares():
    """Simpson 1/3 necesita un número par de subintervalos."""
    with pytest.raises(ValueError):
        simpson_compuesto([0, 1, 2, 3], [0, 1, 4, 9])


def test_simpson_rechaza_espaciado_irregular():
    """Simpson no debe aplicarse a puntos desigualmente espaciados."""
    with pytest.raises(ValueError):
        simpson_compuesto([0, 1, 3], [0, 1, 9])


def test_integracion_rechaza_valores_faltantes():
    """Ambos métodos deben rechazar datos incompletos."""
    with pytest.raises(ValueError):
        trapecio_compuesto([0, 1, 2], [1, np.nan, 3])

    with pytest.raises(ValueError):
        simpson_compuesto([0, 1, 2], [1, np.nan, 3])
