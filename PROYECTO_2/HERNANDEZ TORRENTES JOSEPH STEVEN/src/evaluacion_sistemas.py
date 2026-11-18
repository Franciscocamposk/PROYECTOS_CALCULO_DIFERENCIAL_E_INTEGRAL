
"""
Evaluación de combinaciones de convertidor y batería.

Analiza las 12 combinaciones disponibles en el Excel.
Calcula disponibilidad horaria y costo de adquisición.

No modifica los datos originales ni incluye todavía
el escenario de oleaje reducido.
"""

import pandas as pd

from src.convertidores import calcular_generacion_convertidor
from src.baterias import simular_bateria, resumir_simulacion


def evaluar_combinaciones(
    registros: pd.DataFrame,
    convertidores: pd.DataFrame,
    baterias: pd.DataFrame,
    consumo_w: float = 300.0,
) -> pd.DataFrame:
    """Evalúa cada combinación y devuelve una tabla comparativa."""

    resultados = []

    for _, convertidor in convertidores.iterrows():
        generacion = calcular_generacion_convertidor(
            registros, convertidor
        )

        for _, bateria in baterias.iterrows():
            simulacion = simular_bateria(
                generacion,
                capacidad_kwh=float(bateria["capacidad_kWh"]),
                consumo_w=consumo_w,
                carga_inicial=1.0,
            )

            resumen = resumir_simulacion(simulacion)

            costo_total = (
                int(convertidor["costo_colones"])
                + int(bateria["costo_colones"])
            )

            resultados.append({
                "convertidor": convertidor["convertidor"],
                "bateria": bateria["bateria"],
                "capacidad_kwh": float(bateria["capacidad_kWh"]),
                "costo_total_colones": costo_total,
                "horas_cubiertas": resumen["horas_cubiertas"],
                "horas_sin_cobertura": resumen["horas_sin_cobertura"],
                "disponibilidad_pct": resumen["disponibilidad_pct"],
                "energia_no_servida_wh": resumen["energia_no_servida_wh"],
                "cumple_99_pct": resumen["cumple_99_pct"],
            })

    return pd.DataFrame(resultados).sort_values(
        ["costo_total_colones", "convertidor", "bateria"]
    ).reset_index(drop=True)
