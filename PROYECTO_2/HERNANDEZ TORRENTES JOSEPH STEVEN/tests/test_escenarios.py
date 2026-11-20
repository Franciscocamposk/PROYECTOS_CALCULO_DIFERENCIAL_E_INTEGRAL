"""Pruebas del escenario de oleaje reducido."""

import pandas as pd
import pytest

from src.escenarios import (
    comparar_escenarios,
    reducir_oleaje,
    seleccionar_menor_costo,
)


def test_reduccion_altura_y_flujo():
    """Reducir Hs un 20 % reduce J un 36 %."""
    datos = pd.DataFrame(
        {
            "altura_significativa_m": [2.0],
            "flujo_energia_w_m": [1000.0],
        }
    )

    resultado = reducir_oleaje(datos)

    assert resultado.loc[0, "altura_significativa_m"] == pytest.approx(1.6)
    assert resultado.loc[0, "flujo_energia_w_m"] == pytest.approx(640)


def test_no_modificar_original():
    """El escenario adverso trabaja sobre una copia."""
    datos = pd.DataFrame(
        {
            "altura_significativa_m": [2.0],
            "flujo_energia_w_m": [1000.0],
        }
    )
    original = datos.copy(deep=True)

    reducir_oleaje(datos)

    pd.testing.assert_frame_equal(datos, original)


def test_rechazar_reduccion_invalida():
    """No se aceptan reducciones fuera del intervalo válido."""
    datos = pd.DataFrame(
        {
            "altura_significativa_m": [1.0],
            "flujo_energia_w_m": [1000.0],
        }
    )

    with pytest.raises(ValueError):
        reducir_oleaje(datos, reduccion=1.5)


def test_comparar_y_seleccionar():
    """La alternativa económica que cumple ambos debe seleccionarse."""
    registros = pd.DataFrame(
        {
            "fecha_hora": pd.date_range("2026-05-01", periods=3, freq="h"),
            "altura_significativa_m": [2.0] * 3,
            "flujo_energia_w_m": [10000.0] * 3,
        }
    )

    convertidores = pd.DataFrame(
        [
            {
                "convertidor": "Prueba",
                "ancho_captura_m": 1.0,
                "eficiencia": 0.5,
                "potencia_nominal_W": 900,
                "costo_colones": 100000,
            }
        ]
    )

    baterias = pd.DataFrame(
        [
            {"bateria": "B2", "capacidad_kWh": 2, "costo_colones": 20000},
            {"bateria": "B5", "capacidad_kWh": 5, "costo_colones": 40000},
        ]
    )

    comparacion = comparar_escenarios(registros, convertidores, baterias)

    assert len(comparacion) == 2
    assert comparacion["cumple_ambos"].all()

    mejor = seleccionar_menor_costo(comparacion)

    assert mejor["bateria"] == "B2"
    assert mejor["costo_total_colones"] == 120000
