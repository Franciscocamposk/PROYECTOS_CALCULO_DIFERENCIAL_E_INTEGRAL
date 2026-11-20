"""Pruebas del procesamiento energético completo."""

import numpy as np
import pandas as pd
import pytest

from src.procesamiento_oleaje import preparar_energia_oleaje


def crear_registros():
    """Genera datos horarios de ejemplo con un faltante aislado."""
    return pd.DataFrame(
        {
            "fecha_hora": pd.date_range("2026-05-01", periods=5, freq="h"),
            "altura_significativa_m": [1.0, 1.2, np.nan, 1.6, 1.8],
            "periodo_pico_s": [8.0] * 5,
            "direccion_grados": [200] * 5,
        }
    )


def test_interpolar_y_calcular_todas_las_horas():
    """Debe calcular energía para todas las horas válidas."""
    resultado = preparar_energia_oleaje(crear_registros())

    assert len(resultado) == 5
    assert resultado["flujo_energia_w_m"].notna().all()


def test_identificar_altura_estimada():
    """Solo la altura originalmente faltante queda marcada."""
    resultado = preparar_energia_oleaje(crear_registros())

    assert resultado["altura_estimada"].sum() == 1
    assert bool(resultado.loc[2, "altura_estimada"])
    assert resultado.loc[2, "altura_significativa_m"] == pytest.approx(1.4)


def test_conservar_datos_originales():
    """La función no debe modificar el DataFrame recibido."""
    registros = crear_registros()
    original = registros.copy(deep=True)

    preparar_energia_oleaje(registros)

    pd.testing.assert_frame_equal(registros, original)


def test_flujo_calculado_correctamente():
    """Comprueba que el flujo conserva las unidades W/m."""
    resultado = preparar_energia_oleaje(crear_registros())

    esperado = 1025 * 9.81**2 / (64 * np.pi) * 1.0**2 * 7.2

    assert resultado.loc[0, "flujo_energia_w_m"] == pytest.approx(esperado)


def test_rechazar_columnas_faltantes():
    """Rechaza tablas sin las columnas requeridas."""
    with pytest.raises(ValueError):
        preparar_energia_oleaje(pd.DataFrame({"fecha_hora": ["2026-05-01"]}))
