"""
Pruebas automáticas del módulo de validación de parámetros.

Las pruebas utilizan datos de ejemplo creados en memoria.
No modifican ni dependen del Excel original.
"""

import pandas as pd
import pytest

from src.validacion_parametros import (
    validar_baterias,
    validar_columnas_parametros,
    validar_convertidores,
    validar_nombres_parametros,
    validar_valores_parametros,
)


@pytest.fixture
def parametros_validos():
    """Genera los seis parámetros con sus unidades correctas."""
    return pd.DataFrame(
        {
            "parametro": [
                "Consumo de la estación",
                "Densidad del agua de mar",
                "Gravedad",
                "Periodo energético / periodo pico",
                "Máximo de horas sin energía",
                "Carga inicial de la batería",
            ],
            "valor": [300.0, 1025.0, 9.81, 0.90, 1.0, 100.0],
            "unidad": [
                "W",
                "kg/m³",
                "m/s²",
                "fracción",
                "% de las horas",
                "%",
            ],
        }
    )


def test_columnas_parametros_validas(parametros_validos):
    """Comprueba la presencia de las columnas obligatorias."""
    assert validar_columnas_parametros(parametros_validos) is True


def test_nombres_parametros_validos(parametros_validos):
    """Comprueba que los seis parámetros estén presentes."""
    assert validar_nombres_parametros(parametros_validos) is True


def test_rechazar_parametro_duplicado(parametros_validos):
    """Rechaza identificadores de parámetros repetidos."""
    datos = parametros_validos.copy(deep=True)

    datos.loc[1, "parametro"] = datos.loc[0, "parametro"]

    with pytest.raises(ValueError, match="duplicados"):
        validar_nombres_parametros(datos)


def test_valores_parametros_validos(parametros_validos):
    """Comprueba valores, rangos y unidades correctos."""
    assert validar_valores_parametros(parametros_validos) is True


def test_rechazar_unidad_incorrecta(parametros_validos):
    """Rechaza una unidad que no corresponde al parámetro."""
    datos = parametros_validos.copy(deep=True)

    datos.loc[0, "unidad"] = "kWh"

    with pytest.raises(ValueError, match="Unidad incorrecta"):
        validar_valores_parametros(datos)


def test_rechazar_consumo_negativo(parametros_validos):
    """El consumo de la estación debe ser positivo."""
    datos = parametros_validos.copy(deep=True)

    datos.loc[0, "valor"] = -300.0

    with pytest.raises(ValueError, match="fuera de rango"):
        validar_valores_parametros(datos)


def test_convertidores_validos():
    """Comprueba que las opciones de convertidor sean válidas."""
    datos = pd.DataFrame(
        {
            "convertidor": ["WEC-50", "WEC-100", "WEC-150"],
            "ancho_captura_m": [0.5, 1.0, 1.5],
            "eficiencia": [0.088, 0.081, 0.099],
            "potencia_nominal_W": [500, 900, 1400],
            "costo_colones": [3210000, 5970000, 8660000],
        }
    )

    assert validar_convertidores(datos) is True


def test_rechazar_eficiencia_invalida():
    """La eficiencia no puede superar el valor 1."""
    datos = pd.DataFrame(
        {
            "convertidor": ["WEC-50"],
            "ancho_captura_m": [0.5],
            "eficiencia": [1.5],
            "potencia_nominal_W": [500],
            "costo_colones": [3210000],
        }
    )

    with pytest.raises(ValueError, match="Eficiencia fuera de rango"):
        validar_convertidores(datos)


def test_baterias_validas():
    """Comprueba capacidades y costos positivos."""
    datos = pd.DataFrame(
        {
            "bateria": ["B2", "B5", "B10", "B20"],
            "capacidad_kWh": [2, 5, 10, 20],
            "costo_colones": [960000, 1940000, 4080000, 7330000],
        }
    )

    assert validar_baterias(datos) is True


def test_rechazar_capacidad_negativa():
    """Rechaza una batería con capacidad negativa."""
    datos = pd.DataFrame(
        {
            "bateria": ["B2"],
            "capacidad_kWh": [-2.0],
            "costo_colones": [960000],
        }
    )

    with pytest.raises(ValueError, match="deben ser positivos"):
        validar_baterias(datos)
