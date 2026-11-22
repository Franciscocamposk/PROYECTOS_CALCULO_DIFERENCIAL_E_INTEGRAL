# -*- coding: utf-8 -*-
"""
Módulo de carga, validación y limpieza de datos para el Proyecto 10.
"""

from pathlib import Path
from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd


HOJAS_REQUERIDAS = ("Pasos_embarcaciones", "Hidrofono", "Opciones", "Parametros")
COLUMNAS_PASOS = ("id_paso", "fecha_hora", "tipo", "velocidad_nudos", "distancia_minima_m")
COLUMNAS_HIDROFONO = ("pase", "velocidad_nudos", "distancia_minima_m", "tiempo_s", "presion_cuadratica_Pa2")


def cargar_datos(ruta_excel: str | Path) -> Dict[str, pd.DataFrame]:
    """Lee el archivo Excel del proyecto y valida hojas y columnas obligatorias.

    Entradas:
        ruta_excel: Ruta al archivo Excel (.xlsx). Unidades: N/A.
    Salidas:
        Diccionario {nombre_hoja: DataFrame} con todas las hojas del libro. Unidades: según hoja.
    """
    ruta = Path(ruta_excel)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de datos: {ruta}")

    datos = pd.read_excel(ruta, sheet_name=None)
    for hoja in HOJAS_REQUERIDAS:
        if hoja not in datos:
            raise ValueError(f"Falta la hoja obligatoria '{hoja}' en {ruta.name}.")

    for col in COLUMNAS_PASOS:
        if col not in datos["Pasos_embarcaciones"].columns:
            raise ValueError(f"Falta la columna '{col}' en la hoja Pasos_embarcaciones.")

    for col in COLUMNAS_HIDROFONO:
        if col not in datos["Hidrofono"].columns:
            raise ValueError(f"Falta la columna '{col}' en la hoja Hidrofono.")

    return datos


def extraer_parametros(df_parametros: pd.DataFrame) -> Dict[str, float]:
    """Convierte la hoja Parametros en un diccionario clave -> valor numérico.

    Entradas:
        df_parametros: DataFrame de la hoja Parametros con columnas 'parametro' y 'valor'.
    Salidas:
        Diccionario con claves normalizadas ('fondo_pa2', 'longitud_km', 'meta_pct',
        'costo_hora', 'v_ref_nudos', 'p_ref_pa').
    """
    mapa = dict(zip(df_parametros["parametro"].astype(str).str.strip(), df_parametros["valor"].astype(float)))
    return {
        "fondo_pa2": float(mapa["Ruido ambiental sin embarcaciones"]),
        "longitud_km": float(mapa["Longitud de la zona de ballenas"]),
        "meta_pct": float(mapa["Reducción mínima de la energía sonora"]),
        "costo_hora": float(mapa["Costo por hora adicional de navegación"]),
        "v_ref_nudos": float(mapa["Velocidad de referencia"]),
        "p_ref_pa": float(mapa["Presión de referencia"]),
    }


def limpiar_pasos(df: pd.DataFrame, vel_max_fisica: float = 45.0) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Detecta e imputa velocidades imposibles o faltantes y distancias faltantes por tipo de bote.

    Criterio:
        - Velocidades <= 0, NaN o > vel_max_fisica (45 nudos) se consideran erróneas.
        - Distancias <= 0 o NaN se consideran erróneas.
        - Cada dato inválido se reemplaza por la mediana válida de su mismo 'tipo' de embarcación.

    Entradas:
        df: DataFrame de la hoja Pasos_embarcaciones (velocidad en nudos, distancia en m).
        vel_max_fisica: Límite físico superior razonable para embarcaciones en el golfo (nudos).
    Salidas:
        Tupla (df_limpio, resumen_limpieza) donde df_limpio conserva todas las filas corregidas
        y resumen_limpieza documenta los IDs tratados y las medianas usadas.
    """
    df_limpio = df.copy()

    vel_nan_mask = df_limpio["velocidad_nudos"].isna()
    vel_imp_mask = (~vel_nan_mask) & (
        (df_limpio["velocidad_nudos"] <= 0)
        | (df_limpio["velocidad_nudos"] > vel_max_fisica)
        | ((df_limpio["tipo"] == "Velero") & (df_limpio["velocidad_nudos"] > 15.0))
    )
    dist_nan_mask = df_limpio["distancia_minima_m"].isna() | (df_limpio["distancia_minima_m"] <= 0)

    ids_vel_nan = df_limpio.loc[vel_nan_mask, "id_paso"].tolist() if "id_paso" in df_limpio.columns else []
    ids_vel_imp = df_limpio.loc[vel_imp_mask, "id_paso"].tolist() if "id_paso" in df_limpio.columns else []
    ids_dist_nan = df_limpio.loc[dist_nan_mask, "id_paso"].tolist() if "id_paso" in df_limpio.columns else []

    vel_validas = df_limpio.loc[~(vel_nan_mask | vel_imp_mask)].groupby("tipo")["velocidad_nudos"].median()
    dist_validas = df_limpio.loc[~dist_nan_mask].groupby("tipo")["distancia_minima_m"].median()

    mask_vel_mala = vel_nan_mask | vel_imp_mask
    if mask_vel_mala.any():
        df_limpio.loc[mask_vel_mala, "velocidad_nudos"] = df_limpio.loc[mask_vel_mala, "tipo"].map(vel_validas)

    if dist_nan_mask.any():
        df_limpio.loc[dist_nan_mask, "distancia_minima_m"] = df_limpio.loc[dist_nan_mask, "tipo"].map(dist_validas)

    resumen: Dict[str, Any] = {
        "total_registros": int(len(df_limpio)),
        "n_vel_faltantes": int(vel_nan_mask.sum()),
        "ids_vel_faltantes": ids_vel_nan,
        "n_vel_imposibles": int(vel_imp_mask.sum()),
        "ids_vel_imposibles": ids_vel_imp,
        "n_dist_faltantes": int(dist_nan_mask.sum()),
        "ids_dist_faltantes": ids_dist_nan,
        "medianas_velocidad_nudos": {str(k): float(v) for k, v in vel_validas.items()},
        "medianas_distancia_m": {str(k): float(v) for k, v in dist_validas.items()},
    }
    return df_limpio, resumen
