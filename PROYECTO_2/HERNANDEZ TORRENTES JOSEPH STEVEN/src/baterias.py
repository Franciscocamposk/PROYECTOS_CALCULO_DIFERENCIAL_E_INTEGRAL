
"""
Simulación horaria de baterías para el Proyecto 8.

Modelo energético:
- Cada registro representa una hora.
- La estación consume 300 W = 300 Wh por hora.
- La batería inicia completamente cargada.
- Se supone eficiencia ideal de carga y descarga.
- La energía almacenada nunca supera la capacidad.
- Se contabilizan horas cubiertas, déficit y excedentes.

No modifica los datos originales.
"""

import numpy as np
import pandas as pd


def simular_bateria(
    registros: pd.DataFrame,
    capacidad_kwh: float,
    consumo_w: float = 300.0,
    carga_inicial: float = 1.0,
) -> pd.DataFrame:
    """Simula el balance energético durante horas consecutivas."""

    if "potencia_generada_w" not in registros.columns:
        raise ValueError("Falta la columna potencia_generada_w.")

    parametros = [capacidad_kwh, consumo_w, carga_inicial]

    if not all(np.isfinite(v) for v in parametros):
        raise ValueError("Los parámetros deben ser finitos.")

    if capacidad_kwh <= 0 or consumo_w < 0:
        raise ValueError("Capacidad y consumo inválidos.")

    if not 0 <= carga_inicial <= 1:
        raise ValueError("La carga inicial debe estar entre 0 y 1.")

    datos = registros.copy(deep=True)

    if "fecha_hora" in datos.columns:
        datos["fecha_hora"] = pd.to_datetime(
            datos["fecha_hora"], errors="raise"
        )
        datos = datos.sort_values("fecha_hora").reset_index(drop=True)

        if datos["fecha_hora"].duplicated().any():
            raise ValueError("Existen fechas duplicadas.")

        diferencias = datos["fecha_hora"].diff().dropna()

        if not (diferencias == pd.Timedelta(hours=1)).all():
            raise ValueError("Los registros deben ser horarios consecutivos.")

    potencias = pd.to_numeric(
        datos["potencia_generada_w"], errors="raise"
    )

    if potencias.isna().any() or not np.isfinite(potencias).all():
        raise ValueError("Hay potencias faltantes o no finitas.")

    if (potencias < 0).any():
        raise ValueError("La potencia generada no puede ser negativa.")

    capacidad_wh = capacidad_kwh * 1000.0
    energia = capacidad_wh * carga_inicial
    demanda_wh = consumo_w  # Cada intervalo dura exactamente una hora.

    resultados = []

    for potencia in potencias:
        energia_inicial = energia
        generacion_wh = float(potencia)

        # Atender primero la demanda mediante generación directa.
        generacion_utilizada = min(generacion_wh, demanda_wh)
        deficit = demanda_wh - generacion_utilizada

        # La batería cubre el déficit disponible.
        descarga = min(energia, deficit)
        energia -= descarga

        energia_servida = generacion_utilizada + descarga
        energia_no_servida = demanda_wh - energia_servida

        # El excedente puede almacenarse sin superar la capacidad.
        excedente = generacion_wh - generacion_utilizada
        carga = min(excedente, capacidad_wh - energia)

        energia += carga
        energia_vertida = excedente - carga

        # Una hora se considera cubierta solo si recibe
        # toda la energía solicitada.
        cubierta = energia_no_servida <= 1e-9

        resultados.append({
            "energia_bateria_inicio_wh": energia_inicial,
            "energia_generada_wh": generacion_wh,
            "energia_servida_wh": energia_servida,
            "energia_no_servida_wh": max(0.0, energia_no_servida),
            "energia_vertida_wh": max(0.0, energia_vertida),
            "energia_bateria_final_wh": energia,
            "hora_cubierta": bool(cubierta),
        })

    return pd.concat(
        [datos, pd.DataFrame(resultados)],
        axis=1,
    )


def resumir_simulacion(simulacion: pd.DataFrame) -> dict:
    """Resume disponibilidad, déficit y energía final."""

    if simulacion.empty:
        raise ValueError("La simulación no puede estar vacía.")

    total = len(simulacion)
    cubiertas = int(simulacion["hora_cubierta"].sum())

    return {
        "horas_totales": total,
        "horas_cubiertas": cubiertas,
        "horas_sin_cobertura": total - cubiertas,
        "disponibilidad_pct": 100.0 * cubiertas / total,
        "energia_no_servida_wh": float(
            simulacion["energia_no_servida_wh"].sum()
        ),
        "energia_final_wh": float(
            simulacion["energia_bateria_final_wh"].iloc[-1]
        ),
        "cumple_99_pct": cubiertas / total >= 0.99,
    }
