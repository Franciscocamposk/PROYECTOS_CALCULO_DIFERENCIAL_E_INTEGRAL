# -*- coding: utf-8 -*-
"""
Pruebas automáticas con pytest para el Proyecto 10 (C-08 VEGA).
Verifica integrales conocidas, unidades, balances, limpieza, calibración y escenarios.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.limpieza import cargar_datos, extraer_parametros, limpiar_pasos
from src.modelo import (
    ModeloAcusticoGolfo,
    NUDOS_A_MS,
    energia_paso,
    energia_temporada,
    estimar_fuente,
    p2_teorico,
    simpson_propio,
    trapecio_propio,
    validar_modelo,
)
from src.escenarios import analizar_escenarios, evaluar_medida

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_EXCEL = BASE_DIR / "datos" / "P10_C-08_VEGA.xlsx"


def test_trapecio_y_simpson_funcion_cuadratica():
    """Integral de x^2 en [0, 3] debe ser 9.0."""
    x = np.linspace(0.0, 3.0, 301)
    y = x ** 2
    assert np.isclose(trapecio_propio(x, y), 9.0, rtol=1e-4)
    assert np.isclose(simpson_propio(x, y), 9.0, rtol=1e-8)


def test_trapecio_y_simpson_funcion_seno():
    """Integral de sin(x) en [0, pi] debe ser 2.0."""
    x = np.linspace(0.0, np.pi, 401)
    y = np.sin(x)
    assert np.isclose(trapecio_propio(x, y), 2.0, rtol=1e-4)
    assert np.isclose(simpson_propio(x, y), 2.0, rtol=1e-7)


def test_validacion_obligatoria_menor_0_1_porciento():
    """Para S=1, d=100 m, v=5 m/s, T=2000 s, dt=0.5 s el error debe ser < 0.1%."""
    val = validar_modelo()
    assert val["error_relativo_pct"] < 0.1
    assert np.isclose(val["trapecio_Pa2s"], val["truncada_Pa2s"], rtol=1e-5)
    assert val["truncada_Pa2s"] < val["impropia_Pa2s"]


def test_energia_paso_convergencia_impropia():
    """Cuando T crece, la fórmula truncada tiende a pi*S/(d*v)."""
    e_trunc = energia_paso(S=1.0, d=100.0, v=5.0, T=1e6)
    e_imp = energia_paso(S=1.0, d=100.0, v=5.0, T=None)
    assert np.isclose(e_trunc, e_imp, rtol=1e-4)


def test_energia_paso_casos_limite_error():
    """Parámetros no físicos (d <= 0, v <= 0, S < 0) deben lanzar ValueError."""
    with pytest.raises(ValueError):
        energia_paso(S=1.0, d=0.0, v=5.0)
    with pytest.raises(ValueError):
        energia_paso(S=1.0, d=100.0, v=-2.0)
    with pytest.raises(ValueError):
        energia_paso(S=-1.0, d=100.0, v=5.0)


def test_carga_y_limpieza_excel_real():
    """Verifica carga directa del Excel y corrección de los 11 registros anómalos."""
    datos = cargar_datos(RUTA_EXCEL)
    df_limpio, resumen = limpiar_pasos(datos["Pasos_embarcaciones"])
    assert resumen["total_registros"] == 1100
    assert resumen["n_vel_faltantes"] == 1
    assert resumen["n_vel_imposibles"] == 4
    assert resumen["n_dist_faltantes"] == 6
    assert df_limpio["velocidad_nudos"].isna().sum() == 0
    assert df_limpio["distancia_minima_m"].isna().sum() == 0


def test_calibracion_hidrofono_clase_modelo():
    """Verifica que la clase ModeloAcusticoGolfo calibre S0 y n positivos desde Hidrofono."""
    datos = cargar_datos(RUTA_EXCEL)
    params = extraer_parametros(datos["Parametros"])
    modelo = ModeloAcusticoGolfo(params["fondo_pa2"], params["v_ref_nudos"], params["p_ref_pa"])
    cal = modelo.calibrar(datos["Hidrofono"])
    assert cal["S0"] > 0
    assert cal["n"] > 2.0
    assert len(cal["pases"]) == 2


def test_balance_energia_temporada_suma_igual_total():
    """El acumulado por tipo de embarcación debe sumar exactamente la energía total."""
    datos = cargar_datos(RUTA_EXCEL)
    params = extraer_parametros(datos["Parametros"])
    df_limpio, _ = limpiar_pasos(datos["Pasos_embarcaciones"])
    cal = estimar_fuente(datos["Hidrofono"], params["fondo_pa2"], params["v_ref_nudos"])
    e_total, db_total, desglose = energia_temporada(df_limpio, cal["S0"], cal["n"])
    assert np.isclose(desglose["energia_Pa2s"].sum(), e_total, rtol=1e-9)
    assert np.isclose(desglose["aporte_pct"].sum(), 100.0, rtol=1e-9)
    assert db_total > 0


def test_evaluar_medida_sin_cambios_da_cero_costo_operacion():
    """Un límite altísimo y distancia mínima 0 no debe generar horas extra ni reducción."""
    datos = cargar_datos(RUTA_EXCEL)
    params = extraer_parametros(datos["Parametros"])
    df_limpio, _ = limpiar_pasos(datos["Pasos_embarcaciones"])
    cal = estimar_fuente(datos["Hidrofono"], params["fondo_pa2"], params["v_ref_nudos"])
    medida_nula = {
        "opcion": "Z",
        "descripcion": "Sin restricción",
        "limite_nudos": 999.0,
        "distancia_minima_m": 0.0,
        "costo_fijo_temporada_colones": 0.0,
    }
    res = evaluar_medida(df_limpio, medida_nula, params, cal["S0"], cal["n"])
    assert np.isclose(res["reduccion_pct"], 0.0, atol=1e-9)
    assert np.isclose(res["horas_extra"], 0.0, atol=1e-9)
    assert np.isclose(res["costo_total_CRC"], 0.0, atol=1e-9)


def test_escenarios_y_sensibilidad_opcion_a_ganadora():
    """La Opción A debe cumplir tanto el 50% como el 60% con el menor costo total."""
    datos = cargar_datos(RUTA_EXCEL)
    params = extraer_parametros(datos["Parametros"])
    df_limpio, _ = limpiar_pasos(datos["Pasos_embarcaciones"])
    cal = estimar_fuente(datos["Hidrofono"], params["fondo_pa2"], params["v_ref_nudos"])
    df_res, decision = analizar_escenarios(df_limpio, datos["Opciones"], params, cal["S0"], cal["n"])
    assert len(df_res) == 4
    assert decision["optima_meta_base"]["opcion"] == "A"
    assert decision["optima_meta_mas10"]["opcion"] == "A"
    assert decision["cambia_decision"] is False
