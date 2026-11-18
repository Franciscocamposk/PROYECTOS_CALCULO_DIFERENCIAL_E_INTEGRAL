
"""Pruebas del balance horario de energía de las baterías."""

import pandas as pd
import pytest

from src.baterias import simular_bateria, resumir_simulacion


def crear_datos(potencias):
    """Genera registros horarios consecutivos de prueba."""
    return pd.DataFrame({
        "fecha_hora": pd.date_range(
            "2026-05-01", periods=len(potencias), freq="h"
        ),
        "potencia_generada_w": potencias,
    })


def test_bateria_cubre_deficit():
    """Una batería cargada puede cubrir una hora sin generación."""
    resultado = simular_bateria(crear_datos([0]), 2)

    assert bool(resultado.loc[0, "hora_cubierta"])
    assert resultado.loc[0, "energia_bateria_final_wh"] == pytest.approx(
        1700
    )


def test_bateria_se_agota():
    """Registra déficit cuando no queda suficiente energía."""
    resultado = simular_bateria(crear_datos([0] * 8), 2)
    resumen = resumir_simulacion(resultado)

    assert resumen["horas_cubiertas"] == 6
    assert resumen["horas_sin_cobertura"] == 2
    assert resumen["energia_no_servida_wh"] == pytest.approx(400)


def test_recarga_limitada_por_capacidad():
    """No permite almacenar más que la capacidad disponible."""
    resultado = simular_bateria(crear_datos([0, 900]), 2)

    assert resultado.loc[1, "energia_bateria_final_wh"] == pytest.approx(
        2000
    )
    assert resultado.loc[1, "energia_vertida_wh"] == pytest.approx(300)


def test_generacion_directa_suficiente():
    """No descarga la batería si la generación cubre el consumo."""
    resultado = simular_bateria(crear_datos([300, 300]), 2)

    assert resultado["hora_cubierta"].all()
    assert resultado["energia_bateria_final_wh"].tolist() == pytest.approx(
        [2000, 2000]
    )


def test_balance_de_energia():
    """Energía inicial más generación igual a usos y energía final."""
    resultado = simular_bateria(crear_datos([100, 600, 0, 900]), 2)

    for _, fila in resultado.iterrows():
        entradas = (
            fila["energia_bateria_inicio_wh"]
            + fila["energia_generada_wh"]
        )
        salidas = (
            fila["energia_servida_wh"]
            + fila["energia_vertida_wh"]
            + fila["energia_bateria_final_wh"]
        )
        assert entradas == pytest.approx(salidas)


def test_no_modificar_datos_originales():
    """La simulación no modifica el DataFrame recibido."""
    datos = crear_datos([100, 200, 300])
    original = datos.copy(deep=True)

    simular_bateria(datos, 2)

    pd.testing.assert_frame_equal(datos, original)


def test_rechazar_capacidad_negativa():
    """La capacidad debe ser positiva."""
    with pytest.raises(ValueError):
        simular_bateria(crear_datos([100]), -2)


def test_rechazar_saltos_horarios():
    """Una simulación horaria necesita intervalos consecutivos."""
    datos = crear_datos([100, 200, 300])
    datos.loc[2, "fecha_hora"] += pd.Timedelta(hours=2)

    with pytest.raises(ValueError):
        simular_bateria(datos, 2)
