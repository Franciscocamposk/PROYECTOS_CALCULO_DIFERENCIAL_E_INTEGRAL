"""Pruebas del cálculo de potencia eléctrica."""

import pandas as pd
import pytest

from src.convertidores import (
    calcular_generacion_convertidor,
    calcular_potencia_generada,
)


def test_potencia_sin_saturacion():
    """La potencia es eficiencia por ancho por flujo."""
    resultado = calcular_potencia_generada(1000, 0.5, 0.088, 500)

    assert resultado == pytest.approx(44)


def test_potencia_limitada_por_nominal():
    """La potencia no puede superar la potencia nominal."""
    resultado = calcular_potencia_generada(20000, 0.5, 0.088, 500)

    assert resultado == pytest.approx(500)


def test_flujo_cero():
    """Sin energía de oleaje no se genera electricidad."""
    assert calcular_potencia_generada(0, 1, 0.1, 900) == pytest.approx(0)


def test_rechazar_parametros_invalidos():
    """Se rechazan eficiencias y valores físicamente inválidos."""
    with pytest.raises(ValueError):
        calcular_potencia_generada(-1, 1, 0.1, 900)

    with pytest.raises(ValueError):
        calcular_potencia_generada(100, 1, 1.5, 900)


def test_generacion_horaria_conserva_original():
    """El cálculo genera una copia y respeta el límite nominal."""
    registros = pd.DataFrame({"flujo_energia_w_m": [1000, 20000]})

    convertidor = pd.Series(
        {
            "convertidor": "WEC-50",
            "ancho_captura_m": 0.5,
            "eficiencia": 0.088,
            "potencia_nominal_W": 500,
        }
    )

    original = registros.copy(deep=True)

    resultado = calcular_generacion_convertidor(registros, convertidor)

    pd.testing.assert_frame_equal(registros, original)

    assert resultado["potencia_generada_w"].tolist() == pytest.approx([44, 500])


def test_rechazar_flujo_incompleto():
    """No se aceptan faltantes en la generación."""
    registros = pd.DataFrame({"flujo_energia_w_m": [1000, None]})

    convertidor = pd.Series(
        {
            "convertidor": "WEC-50",
            "ancho_captura_m": 0.5,
            "eficiencia": 0.088,
            "potencia_nominal_W": 500,
        }
    )

    with pytest.raises(ValueError):
        calcular_generacion_convertidor(registros, convertidor)
