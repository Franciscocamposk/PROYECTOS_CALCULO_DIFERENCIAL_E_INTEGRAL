
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



def comparar_tres_escenarios(
    registros: pd.DataFrame,
    convertidores: pd.DataFrame,
    baterias: pd.DataFrame,
    consumo_w: float = 300.0,
) -> pd.DataFrame:
    """
    Evalúa 12 combinaciones bajo tres condiciones de oleaje.

    Escenarios:
        Normal: Hs original.
        Moderado: Hs reducida un 10 %.
        Adverso: Hs reducida un 20 %.

    Retorna una tabla con costo, disponibilidad,
    horas sin cobertura y cumplimiento del 99 %.
    """

    escenarios = {
        "normal": 0.00,
        "moderado": 0.10,
        "adverso": 0.20,
    }

    resultado = None
    claves = ["convertidor", "bateria"]

    for nombre, reduccion in escenarios.items():
        if reduccion == 0:
            datos = registros.copy(deep=True)
        else:
            datos = reducir_oleaje(registros, reduccion)

        evaluacion = evaluar_combinaciones(
            datos,
            convertidores,
            baterias,
            consumo_w,
        )

        columnas = claves + [
            "disponibilidad_pct",
            "horas_sin_cobertura",
            "cumple_99_pct",
        ]

        if resultado is None:
            columnas.append("costo_total_colones")

        evaluacion = evaluacion[columnas].rename(
            columns={
                "disponibilidad_pct": f"disponibilidad_{nombre}_pct",
                "horas_sin_cobertura": f"horas_sin_cobertura_{nombre}",
                "cumple_99_pct": f"cumple_{nombre}",
            }
        )

        if resultado is None:
            resultado = evaluacion
        else:
            resultado = resultado.merge(
                evaluacion,
                on=claves,
                validate="one_to_one",
            )

    resultado["cumple_tres"] = (
        resultado["cumple_normal"]
        & resultado["cumple_moderado"]
        & resultado["cumple_adverso"]
    )

    return resultado.sort_values(
        "costo_total_colones"
    ).reset_index(drop=True)
