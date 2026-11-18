
"""Validaciones matemáticas y energéticas del Proyecto 8."""

import numpy as np
import pytest

from src.integracion import trapecio_compuesto, simpson_compuesto
from src.baterias import Bateria


def test_varianza_senoidal_trapecio():
    """Para eta = 2*sin(t), la varianza teórica es 2 m²."""
    t = np.linspace(0, 2 * np.pi, 1001)
    eta = 2 * np.sin(t)

    varianza = trapecio_compuesto(t, eta**2) / (t[-1] - t[0])

    assert varianza == pytest.approx(2.0, abs=1e-6)


def test_varianza_senoidal_simpson():
    """Compara Simpson con la varianza teórica A²/2."""
    t = np.linspace(0, 2 * np.pi, 1001)
    eta = 2 * np.sin(t)

    varianza = simpson_compuesto(t, eta**2) / (t[-1] - t[0])

    assert varianza == pytest.approx(2.0, abs=1e-6)


def test_balance_energetico_bateria():
    """Comprueba conservación de energía en cada intervalo."""
    bateria = Bateria(capacidad_kwh=2, carga_inicial=0.5)
    simulacion = bateria.simular(
        Pg=[500, 0, 300, 2000],
        Pc=300,
        dt=1.0,
    )

    for _, fila in simulacion.iterrows():
        cambio = (
            fila["energia_bateria_final_wh"]
            - fila["energia_inicial_wh"]
        )

        balance = (
            fila["energia_generada_wh"]
            - fila["energia_consumida_wh"]
            - fila["energia_vertida_wh"]
            + fila["energia_no_servida_wh"]
        )

        assert cambio == pytest.approx(balance, abs=1e-8)


def test_bateria_respeta_capacidad():
    """La carga permanece dentro de los límites físicos."""
    bateria = Bateria(capacidad_kwh=1)
    resultado = bateria.simular([5000, 0, 0], Pc=300)

    assert resultado["energia_bateria_final_wh"].between(
        0, 1000
    ).all()


def test_bateria_registra_energia_no_atendida():
    """Sin generación ni reserva debe existir déficit."""
    bateria = Bateria(capacidad_kwh=1, carga_inicial=0)
    resultado = bateria.simular([0], Pc=300)

    assert resultado["energia_no_servida_wh"].iloc[0] == pytest.approx(300)
    assert not bool(resultado["hora_cubierta"].iloc[0])


def test_bateria_rechaza_intervalo_invalido():
    """La duración del intervalo debe ser positiva."""
    bateria = Bateria(capacidad_kwh=2)

    with pytest.raises(ValueError):
        bateria.simular([300], Pc=300, dt=0)



from src.escenarios import comparar_tres_escenarios


def test_tres_escenarios_generan_columnas():
    """Comprueba las tres disponibilidades y su selección."""
    import pandas as pd

    registros = pd.DataFrame({
        "altura_significativa_m": [2.0] * 4,
        "flujo_energia_w_m": [10000.0] * 4,
    })

    convertidores = pd.DataFrame([{
        "convertidor": "PRUEBA",
        "ancho_captura_m": 1.0,
        "eficiencia": 0.10,
        "potencia_nominal_W": 500.0,
        "costo_colones": 1000,
    }])

    baterias = pd.DataFrame([{
        "bateria": "PRUEBA",
        "capacidad_kWh": 2.0,
        "costo_colones": 500,
    }])

    # Las columnas de ejemplo deben coincidir con las
    # que utiliza calcular_generacion_convertidor().
    resultado = comparar_tres_escenarios(
        registros, convertidores, baterias
    )

    assert len(resultado) == 1
    assert "disponibilidad_normal_pct" in resultado
    assert "disponibilidad_moderado_pct" in resultado
    assert "disponibilidad_adverso_pct" in resultado
    assert "cumple_tres" in resultado
    assert resultado["costo_total_colones"].iloc[0] == 1500
