# -*- coding: utf-8 -*-
"""
Módulo de simulación de escenarios de manejo, sensibilidad y recomendación.
"""

from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd

from src.modelo import NUDOS_A_MS, energia_temporada


def evaluar_medida(
    df: pd.DataFrame,
    medida: Dict[str, Any],
    parametros: Dict[str, float],
    S0: float,
    n: float,
) -> Dict[str, Any]:
    """Evalúa una medida de manejo sobre la flota: reducción de ruido, horas extra y costo total.

    Entradas:
        df: DataFrame limpio de Pasos_embarcaciones.
        medida: Diccionario o fila de Opciones ('opcion', 'descripcion', 'limite_nudos',
                'distancia_minima_m', 'costo_fijo_temporada_colones').
        parametros: Diccionario extraído de la hoja Parametros ('longitud_km', 'costo_hora',
                    'meta_pct', 'v_ref_nudos', 'p_ref_pa').
        S0: Constante de intensidad de fuente (Pa²·m²).
        n: Exponente de velocidad (adimensional).
    Salidas:
        Diccionario con energía nueva (Pa²·s), reducción (% y dB), horas extra (h),
        costo adicional (CRC), costo total (CRC) y cumplimiento de la meta.
    """
    e_base, db_base, _ = energia_temporada(
        df, S0, n, parametros["v_ref_nudos"], parametros["p_ref_pa"]
    )

    df_mod = df.copy()
    v_orig_kts = df_mod["velocidad_nudos"].to_numpy(dtype=float)
    d_orig_m = df_mod["distancia_minima_m"].to_numpy(dtype=float)

    lim_kts = medida.get("limite_nudos")
    if lim_kts is not None and not pd.isna(lim_kts):
        v_nueva_kts = np.minimum(v_orig_kts, float(lim_kts))
    else:
        v_nueva_kts = v_orig_kts

    d_min = medida.get("distancia_minima_m")
    if d_min is not None and not pd.isna(d_min):
        d_nueva_m = np.maximum(d_orig_m, float(d_min))
    else:
        d_nueva_m = d_orig_m

    df_mod["velocidad_nudos"] = v_nueva_kts
    df_mod["distancia_minima_m"] = d_nueva_m

    e_nueva, db_nueva, _ = energia_temporada(
        df_mod, S0, n, parametros["v_ref_nudos"], parametros["p_ref_pa"]
    )

    reduccion_pct = ((e_base - e_nueva) / e_base) * 100.0
    delta_db = db_nueva - db_base

    L_m = parametros["longitud_km"] * 1000.0
    v_orig_ms = v_orig_kts * NUDOS_A_MS
    v_nueva_ms = v_nueva_kts * NUDOS_A_MS
    horas_extra = float(np.sum((L_m / v_nueva_ms - L_m / v_orig_ms) / 3600.0))

    costo_fijo = float(medida["costo_fijo_temporada_colones"])
    costo_op = horas_extra * float(parametros["costo_hora"])
    costo_total = costo_fijo + costo_op

    meta_base = float(parametros["meta_pct"])
    return {
        "opcion": str(medida["opcion"]),
        "descripcion": str(medida["descripcion"]),
        "limite_nudos": None if pd.isna(lim_kts) else float(lim_kts),
        "distancia_minima_m": None if pd.isna(d_min) else float(d_min),
        "energia_Pa2s": e_nueva,
        "nivel_dB": db_nueva,
        "reduccion_pct": reduccion_pct,
        "delta_dB": delta_db,
        "horas_extra": horas_extra,
        "costo_fijo_CRC": costo_fijo,
        "costo_operacion_CRC": costo_op,
        "costo_total_CRC": costo_total,
        "cumple_meta": reduccion_pct >= meta_base,
        "cumple_meta_mas10": reduccion_pct >= (meta_base + 10.0),
    }


def analizar_escenarios(
    df_pasos: pd.DataFrame,
    df_opciones: pd.DataFrame,
    parametros: Dict[str, float],
    S0: float,
    n: float,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Evalúa todas las opciones oficiales y determina la opción óptima para meta base y +10%.

    Salidas:
        Tupla (df_resultados, resumen_decision).
    """
    resultados = [
        evaluar_medida(df_pasos, row.to_dict(), parametros, S0, n)
        for _, row in df_opciones.iterrows()
    ]
    df_res = pd.DataFrame(resultados)

    cumplen_base = df_res[df_res["cumple_meta"]].sort_values("costo_total_CRC")
    cumplen_60 = df_res[df_res["cumple_meta_mas10"]].sort_values("costo_total_CRC")

    opt_base = cumplen_base.iloc[0].to_dict() if not cumplen_base.empty else None
    opt_60 = cumplen_60.iloc[0].to_dict() if not cumplen_60.empty else None

    resumen = {
        "optima_meta_base": opt_base,
        "optima_meta_mas10": opt_60,
        "cambia_decision": (
            opt_base is not None and opt_60 is not None and opt_base["opcion"] != opt_60["opcion"]
        ),
    }
    return df_res, resumen
