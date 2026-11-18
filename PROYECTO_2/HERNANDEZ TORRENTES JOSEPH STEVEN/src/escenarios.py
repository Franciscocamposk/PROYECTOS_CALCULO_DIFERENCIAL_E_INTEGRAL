
"""
Escenarios de oleaje y selección del sistema de menor costo.

Escenario base: alturas originales.
Escenario reducido: altura significativa disminuida un 20 %.

Como J es proporcional a Hs², el flujo se multiplica por 0.64
cuando Hs se multiplica por 0.80 y Tp permanece constante.
"""

import numpy as np
import pandas as pd

from src.evaluacion_sistemas import evaluar_combinaciones


def reducir_oleaje(registros: pd.DataFrame, reduccion=0.20):
    """Crea una copia con altura y flujo energético reducidos."""

    if not np.isfinite(reduccion) or not 0 <= reduccion < 1:
        raise ValueError("La reducción debe estar entre 0 y 1.")

    columnas = {"altura_significativa_m", "flujo_energia_w_m"}

    if not columnas.issubset(registros.columns):
        raise ValueError("Faltan las columnas de altura y flujo.")

    resultado = registros.copy(deep=True)
    factor = 1.0 - reduccion

    resultado["altura_significativa_m"] *= factor
    resultado["flujo_energia_w_m"] *= factor**2

    return resultado


def comparar_escenarios(
    registros: pd.DataFrame,
    convertidores: pd.DataFrame,
    baterias: pd.DataFrame,
    consumo_w=300.0,
    reduccion=0.20,
):
    """Evalúa todas las opciones en ambos escenarios."""

    base = evaluar_combinaciones(
        registros, convertidores, baterias, consumo_w
    )

    reducidos = reducir_oleaje(registros, reduccion)

    adverso = evaluar_combinaciones(
        reducidos, convertidores, baterias, consumo_w
    )

    claves = ["convertidor", "bateria"]

    adverso = adverso[claves + [
        "horas_sin_cobertura",
        "disponibilidad_pct",
        "cumple_99_pct",
    ]].rename(columns={
        "horas_sin_cobertura": "horas_sin_cobertura_reducido",
        "disponibilidad_pct": "disponibilidad_reducido_pct",
        "cumple_99_pct": "cumple_reducido",
    })

    comparacion = base.merge(
        adverso, on=claves, validate="one_to_one"
    )

    comparacion = comparacion.rename(columns={
        "disponibilidad_pct": "disponibilidad_base_pct",
        "cumple_99_pct": "cumple_base",
    })

    comparacion["cumple_ambos"] = (
        comparacion["cumple_base"]
        & comparacion["cumple_reducido"]
    )

    return comparacion.sort_values(
        "costo_total_colones"
    ).reset_index(drop=True)


def seleccionar_menor_costo(comparacion: pd.DataFrame):
    """Devuelve la opción más económica que cumple ambos escenarios."""

    opciones = comparacion.loc[comparacion["cumple_ambos"]]

    if opciones.empty:
        return None

    return opciones.sort_values(
        "costo_total_colones"
    ).iloc[0]
