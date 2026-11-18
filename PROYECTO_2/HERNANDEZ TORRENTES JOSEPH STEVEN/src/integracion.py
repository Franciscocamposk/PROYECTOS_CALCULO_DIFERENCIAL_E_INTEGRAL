
"""
Integración numérica para el Proyecto 8.

Implementa:
- Regla del trapecio compuesto.
- Regla de Simpson 1/3 compuesto.

Los métodos se implementan directamente, sin utilizar
integradores de scipy ni numpy.
"""

import numpy as np


def _validar_datos(x, y):
    """Valida que los datos sean numéricos, finitos y estén ordenados."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("Los datos deben ser arreglos de una dimensión.")

    if len(x) != len(y):
        raise ValueError("x e y deben tener la misma cantidad de datos.")

    if len(x) < 2:
        raise ValueError("Se necesitan al menos dos puntos.")

    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("Los datos no pueden contener NaN ni infinitos.")

    if np.any(np.diff(x) <= 0):
        raise ValueError("Los valores de x deben ser estrictamente crecientes.")

    return x, y


def trapecio_compuesto(x, y):
    """
    Calcula una integral definida mediante trapecios.

    Permite puntos igualmente espaciados o separaciones variables.

    Parámetros:
        x: coordenadas de la variable independiente.
        y: valores de la función en cada coordenada.

    Retorna:
        Aproximación numérica de la integral.
    """
    x, y = _validar_datos(x, y)

    anchos = np.diff(x)
    alturas_promedio = (y[:-1] + y[1:]) / 2

    return float(np.sum(anchos * alturas_promedio))


def simpson_compuesto(x, y):
    """
    Calcula una integral mediante Simpson 1/3 compuesto.

    Requiere:
        - Al menos tres puntos.
        - Cantidad par de subintervalos.
        - Separación uniforme entre los puntos.

    Retorna:
        Aproximación numérica de la integral.
    """
    x, y = _validar_datos(x, y)

    n = len(x) - 1

    if n < 2 or n % 2 != 0:
        raise ValueError(
            "Simpson requiere una cantidad par de subintervalos."
        )

    diferencias = np.diff(x)
    h = diferencias[0]

    if not np.allclose(diferencias, h, rtol=1e-9, atol=1e-12):
        raise ValueError(
            "Simpson requiere puntos igualmente espaciados."
        )

    suma_impares = np.sum(y[1:-1:2])
    suma_pares = np.sum(y[2:-1:2])

    resultado = (h / 3) * (
        y[0] + y[-1] + 4 * suma_impares + 2 * suma_pares
    )

    return float(resultado)
