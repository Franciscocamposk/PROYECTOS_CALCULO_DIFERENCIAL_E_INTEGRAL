"""
Modelo de generación eléctrica de convertidores de oleaje.

Proyecto 8: energía de las olas frente a Pavones.

P_generada = min(P_nominal, eficiencia * ancho * flujo)

Unidades:
    Flujo: W/m
    Ancho de captura: m
    Potencia generada: W

La potencia siempre está limitada por la capacidad nominal.
"""

import numpy as np
import pandas as pd


def calcular_potencia_generada(
    flujo_w_m,
    ancho_captura_m,
    eficiencia,
    potencia_nominal_w,
):
    """Calcula la potencia eléctrica para una hora y un convertidor."""
    valores = [
        flujo_w_m,
        ancho_captura_m,
        eficiencia,
        potencia_nominal_w,
    ]

    if not all(np.isfinite(valor) for valor in valores):
        raise ValueError("Todos los valores deben ser finitos.")

    if flujo_w_m < 0:
        raise ValueError("El flujo de energía no puede ser negativo.")

    if ancho_captura_m <= 0:
        raise ValueError("El ancho de captura debe ser positivo.")

    if not 0 < eficiencia <= 1:
        raise ValueError("La eficiencia debe estar entre 0 y 1.")

    if potencia_nominal_w <= 0:
        raise ValueError("La potencia nominal debe ser positiva.")

    potencia_disponible = eficiencia * ancho_captura_m * flujo_w_m

    return float(min(potencia_nominal_w, potencia_disponible))


def calcular_generacion_convertidor(registros, convertidor):
    """
    Calcula la generación horaria de un convertidor.

    Parámetros:
        registros: DataFrame con la columna flujo_energia_w_m.
        convertidor: fila de Opciones_convertidor.

    Retorna:
        Copia de los registros con potencia_generada_w.
    """
    if "flujo_energia_w_m" not in registros.columns:
        raise ValueError("Falta la columna flujo_energia_w_m.")

    campos = {
        "convertidor",
        "ancho_captura_m",
        "eficiencia",
        "potencia_nominal_W",
    }

    if not campos.issubset(convertidor.index):
        raise ValueError("Faltan parámetros del convertidor.")

    resultado = registros.copy(deep=True)

    ancho = float(convertidor["ancho_captura_m"])
    eficiencia = float(convertidor["eficiencia"])
    nominal = float(convertidor["potencia_nominal_W"])

    # Validar los parámetros incluso si no hay registros.
    calcular_potencia_generada(0, ancho, eficiencia, nominal)

    flujo = pd.to_numeric(resultado["flujo_energia_w_m"], errors="raise")

    if flujo.isna().any() or not np.isfinite(flujo).all():
        raise ValueError("El flujo energético debe estar completo.")

    if (flujo < 0).any():
        raise ValueError("El flujo energético no puede ser negativo.")

    resultado["potencia_generada_w"] = np.minimum(
        nominal,
        eficiencia * ancho * flujo,
    )

    resultado["convertidor"] = str(convertidor["convertidor"])

    return resultado
