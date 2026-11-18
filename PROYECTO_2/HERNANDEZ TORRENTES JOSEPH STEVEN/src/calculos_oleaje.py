
"""
Cálculos físicos iniciales del oleaje para el Proyecto 8.

Calcula la varianza de elevación y la altura significativa
a partir de muestras de elevación de la superficie del mar.

La integración utiliza los métodos implementados en
src/integracion.py, sin modificar los datos originales.
"""

import numpy as np
import pandas as pd

from src.integracion import trapecio_compuesto, simpson_compuesto


def calcular_altura_significativa(tiempo_s, elevacion_m, metodo="trapecio"):
    """
    Calcula la altura significativa Hs = 4 * sqrt(sigma²).

    sigma² = (1/T) * integral[eta(t)² dt]

    Parámetros:
        tiempo_s: tiempos de la muestra, en segundos.
        elevacion_m: elevaciones del agua, en metros.
        metodo: 'trapecio' o 'simpson'.

    Retorna:
        Diccionario con duración, varianza y altura significativa.
    """
    tiempo = np.asarray(tiempo_s, dtype=float)
    elevacion = np.asarray(elevacion_m, dtype=float)

    if len(tiempo) != len(elevacion):
        raise ValueError("Tiempo y elevación deben tener igual longitud.")

    if len(tiempo) < 2:
        raise ValueError("Se necesitan al menos dos mediciones.")

    if not np.all(np.isfinite(elevacion)):
        raise ValueError("Las elevaciones deben ser valores finitos.")

    duracion = tiempo[-1] - tiempo[0]

    if duracion <= 0:
        raise ValueError("La duración de la muestra debe ser positiva.")

    elevacion_cuadrada = elevacion ** 2

    if metodo == "trapecio":
        integral = trapecio_compuesto(tiempo, elevacion_cuadrada)

        
    elif metodo == "simpson":
        integral = simpson_compuesto(tiempo, elevacion_cuadrada)

    elif metodo == "hibrido":
        # Simpson requiere una cantidad par de subintervalos.
        # Si es impar, aplicamos Simpson en todos excepto
        # el último, que se integra mediante trapecio.
        n = len(tiempo) - 1

        if n % 2 == 0:
            integral = simpson_compuesto(tiempo, elevacion_cuadrada)
        elif n >= 3:
            integral = (
                simpson_compuesto(tiempo[:-1], elevacion_cuadrada[:-1])
                + trapecio_compuesto(tiempo[-2:], elevacion_cuadrada[-2:])
            )
        else:
            # Con un solo subintervalo solo procede trapecio.
            integral = trapecio_compuesto(tiempo, elevacion_cuadrada)

    else:



        raise ValueError("Método desconocido. Use 'trapecio' o 'simpson'.")

    varianza = integral / duracion
    altura_significativa = 4 * np.sqrt(varianza)

    return {
        "duracion_s": float(duracion),
        "varianza_m2": float(varianza),
        "altura_significativa_m": float(altura_significativa),
        "metodo": metodo,
    }


def calcular_por_registro(muestras, metodo="trapecio"):
    """
    Calcula Hs independientemente para cada registro.

    Requiere las columnas:
    registro, tiempo_s, elevacion_m.

    Retorna un DataFrame de resultados.
    """
    columnas = {"registro", "tiempo_s", "elevacion_m"}

    if not columnas.issubset(muestras.columns):
        raise ValueError("Faltan columnas necesarias en las muestras.")

    resultados = []

    for registro, grupo in muestras.groupby("registro", sort=True):
        grupo = grupo.sort_values("tiempo_s")

        calculo = calcular_altura_significativa(
            grupo["tiempo_s"].to_numpy(),
            grupo["elevacion_m"].to_numpy(),
            metodo=metodo,
        )

        resultados.append({
            "registro": registro,
            **calculo,
        })

    return pd.DataFrame(resultados)
