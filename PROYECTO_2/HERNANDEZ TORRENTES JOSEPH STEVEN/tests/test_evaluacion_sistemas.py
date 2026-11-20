"""Pruebas de evaluación de combinaciones energéticas."""

import pandas as pd
import pytest

from src.evaluacion_sistemas import evaluar_combinaciones


def crear_datos():
    """Crea un caso pequeño de evaluación reproducible."""
    registros = pd.DataFrame(
        {
            "fecha_hora": pd.date_range("2026-05-01", periods=3, freq="h"),
            "flujo_energia_w_m": [1000.0, 1000.0, 1000.0],
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
            {
                "bateria": "B2",
                "capacidad_kWh": 2,
                "costo_colones": 20000,
            },
            {
                "bateria": "B5",
                "capacidad_kWh": 5,
                "costo_colones": 40000,
            },
        ]
    )

    return registros, convertidores, baterias


def test_evaluar_todas_las_combinaciones():
    """Una opción de convertidor por dos baterías genera dos resultados."""
    registros, convertidores, baterias = crear_datos()

    resultado = evaluar_combinaciones(registros, convertidores, baterias)

    assert len(resultado) == 2


def test_costos_correctos():
    """El costo total suma convertidor y batería."""
    registros, convertidores, baterias = crear_datos()

    resultado = evaluar_combinaciones(registros, convertidores, baterias)

    assert resultado["costo_total_colones"].tolist() == [120000, 140000]


def test_disponibilidad_completa():
    """Si la generación supera el consumo, todas las horas se cubren."""
    registros, convertidores, baterias = crear_datos()

    resultado = evaluar_combinaciones(registros, convertidores, baterias)

    assert resultado["disponibilidad_pct"].tolist() == pytest.approx([100.0, 100.0])
    assert resultado["cumple_99_pct"].all()


def test_conservar_registros_originales():
    """La evaluación no altera los datos recibidos."""
    registros, convertidores, baterias = crear_datos()
    original = registros.copy(deep=True)

    evaluar_combinaciones(registros, convertidores, baterias)

    pd.testing.assert_frame_equal(registros, original)
