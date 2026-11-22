"""Pruebas del modelo físico de energía de las olas."""

import numpy as np
import pandas as pd
import pytest

from src.energia_oleaje import (
    calcular_flujo_energia,
    calcular_flujo_por_hora,
)


def test_flujo_energia_con_valores_conocidos():
    """Compara el cálculo contra la ecuación física."""
    esperado = 1025 * 9.81**2 / (64 * np.pi) * 1.0**2 * 7.2

    resultado = calcular_flujo_energia(1.0, 8.0)

    assert resultado == pytest.approx(esperado)


def test_altura_cero_produce_flujo_cero():
    """Sin altura de ola no hay flujo energético."""
    assert calcular_flujo_energia(0, 8) == pytest.approx(0)


def test_flujo_crece_con_cuadrado_de_altura():
    """Duplicar Hs cuadruplica el flujo, manteniendo Tp."""
    inicial = calcular_flujo_energia(1, 8)
    doble = calcular_flujo_energia(2, 8)

    assert doble == pytest.approx(4 * inicial)


def test_rechazar_valores_fisicamente_invalidos():
    """Los parámetros físicos deben ser válidos."""
    with pytest.raises(ValueError):
        calcular_flujo_energia(-1, 8)

    with pytest.raises(ValueError):
        calcular_flujo_energia(1, 0)

    with pytest.raises(ValueError):
        calcular_flujo_energia(1, 8, densidad_kg_m3=-1025)


def test_calculo_por_hora_conserva_original_y_nan():
    """El cálculo debe conservar los faltantes y el original."""
    registros = pd.DataFrame(
        {
            "fecha_hora": pd.date_range("2026-05-01", periods=2, freq="h"),
            "altura_significativa_m": [1.0, np.nan],
            "periodo_pico_s": [8.0, 9.0],
        }
    )

    original = registros.copy(deep=True)

    resultado = calcular_flujo_por_hora(registros)

    pd.testing.assert_frame_equal(registros, original)
    assert resultado.loc[0, "flujo_energia_w_m"] > 0
    assert pd.isna(resultado.loc[1, "flujo_energia_w_m"])


def test_rechazar_periodos_negativos_en_tabla():
    """La función debe rechazar periodos inválidos."""
    registros = pd.DataFrame(
        {
            "fecha_hora": ["2026-05-01"],
            "altura_significativa_m": [1.0],
            "periodo_pico_s": [-2.0],
        }
    )

    with pytest.raises(ValueError):
        calcular_flujo_por_hora(registros)
