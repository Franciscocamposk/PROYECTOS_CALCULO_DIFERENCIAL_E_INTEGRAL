
"""
Modelo físico del flujo energético de las olas.

Proyecto 8: energía de las olas para una boya frente a Pavones.

J = (rho * g**2 / (64*pi)) * Hs**2 * Te
Te = relacion_periodos * Tp

Unidades:
    Hs: metros
    Tp, Te: segundos
    rho: kg/m³
    g: m/s²
    J: W/m

No calcula todavía la potencia eléctrica del convertidor.
"""

import numpy as np
import pandas as pd


def calcular_flujo_energia(
    altura_significativa_m,
    periodo_pico_s,
    densidad_kg_m3=1025.0,
    gravedad_m_s2=9.81,
    relacion_periodos=0.90,
):
    """Calcula el flujo energético J para una observación válida."""

    valores = [
        altura_significativa_m,
        periodo_pico_s,
        densidad_kg_m3,
        gravedad_m_s2,
        relacion_periodos,
    ]

    if not all(np.isfinite(v) for v in valores):
        raise ValueError("Los parámetros deben ser finitos.")

    if altura_significativa_m < 0:
        raise ValueError("La altura significativa no puede ser negativa.")

    if periodo_pico_s <= 0:
        raise ValueError("El periodo pico debe ser positivo.")

    if densidad_kg_m3 <= 0 or gravedad_m_s2 <= 0:
        raise ValueError("La densidad y la gravedad deben ser positivas.")

    if not 0 < relacion_periodos <= 1:
        raise ValueError("La relación de periodos debe estar entre 0 y 1.")

    periodo_energetico_s = relacion_periodos * periodo_pico_s

    flujo_w_m = (
        densidad_kg_m3
        * gravedad_m_s2**2
        / (64 * np.pi)
        * altura_significativa_m**2
        * periodo_energetico_s
    )

    return float(flujo_w_m)


def calcular_flujo_por_hora(
    registros,
    densidad_kg_m3=1025.0,
    gravedad_m_s2=9.81,
    relacion_periodos=0.90,
):
    """
    Agrega periodo energético y flujo W/m a una copia de los registros.

    No modifica el DataFrame recibido.
    No sustituye datos faltantes: se conservan como NaN
    para evitar fabricar resultados físicos.
    """
    columnas = {
        "fecha_hora",
        "altura_significativa_m",
        "periodo_pico_s",
    }

    if not columnas.issubset(registros.columns):
        raise ValueError("Faltan columnas necesarias de oleaje.")

    resultado = registros.copy(deep=True)

    for columna in ["altura_significativa_m", "periodo_pico_s"]:
        resultado[columna] = pd.to_numeric(
            resultado[columna], errors="raise"
        )

    # Verificar parámetros incluso si no hay registros válidos.
    calcular_flujo_energia(
        0, 1, densidad_kg_m3, gravedad_m_s2, relacion_periodos
    )

    altura = resultado["altura_significativa_m"]
    periodo = resultado["periodo_pico_s"]

    invalidos = (
        ((altura < 0) | ((periodo <= 0) & periodo.notna()))
        | np.isinf(altura)
        | np.isinf(periodo)
    )

    if invalidos.any():
        raise ValueError("Hay alturas o periodos físicamente inválidos.")

    resultado["periodo_energetico_s"] = (
        relacion_periodos * periodo
    )

    factor = densidad_kg_m3 * gravedad_m_s2**2 / (64 * np.pi)

    resultado["flujo_energia_w_m"] = (
        factor
        * altura**2
        * resultado["periodo_energetico_s"]
    )

    return resultado
