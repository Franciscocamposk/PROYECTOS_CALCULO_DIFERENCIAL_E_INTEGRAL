"""
Lectura centralizada del archivo Excel del Proyecto 8.

Permite cargar y verificar las hojas necesarias sin
modificar el archivo original.
"""

from pathlib import Path

import pandas as pd

from src.limpieza import validar_columnas
from src.validacion_parametros import (
    validar_baterias,
    validar_convertidores,
    validar_valores_parametros,
)

HOJAS_OBLIGATORIAS = {
    "Registros_oleaje",
    "Muestra_elevacion",
    "Opciones_convertidor",
    "Opciones_bateria",
    "Parametros",
    "Diccionario",
}

COLUMNAS_MUESTRA = {
    "registro",
    "fecha_hora",
    "tiempo_s",
    "elevacion_m",
}

COLUMNAS_DICCIONARIO = {
    "hoja",
    "columna",
    "descripcion",
    "unidad",
}


def cargar_datos(ruta: str | Path) -> dict[str, pd.DataFrame]:
    """
    Lee y valida las hojas del Excel asignado.

    Args:
        ruta: Ruta del archivo .xlsx.

    Returns:
        Diccionario de DataFrames, uno por hoja.

    Raises:
        FileNotFoundError: Si el Excel no existe.
        ValueError: Si faltan hojas o columnas obligatorias.

    La lectura es de solo lectura. No modifica el Excel.
    """

    ruta = Path(ruta)

    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo Excel: {ruta}")

    # Leer todas las hojas en una sola operación.
    hojas = pd.read_excel(ruta, sheet_name=None)

    # Comprobar la presencia de las seis hojas.
    faltantes = HOJAS_OBLIGATORIAS - set(hojas)

    if faltantes:
        raise ValueError("Faltan hojas obligatorias: " + ", ".join(sorted(faltantes)))

    # Validar las columnas de los registros de oleaje.
    validar_columnas(hojas["Registros_oleaje"])

    # Validar las opciones y los parámetros.
    validar_valores_parametros(hojas["Parametros"])
    validar_convertidores(hojas["Opciones_convertidor"])
    validar_baterias(hojas["Opciones_bateria"])

    # Validar la estructura de la muestra de elevación.
    faltantes_muestra = COLUMNAS_MUESTRA - set(hojas["Muestra_elevacion"].columns)

    if faltantes_muestra:
        raise ValueError(
            "Faltan columnas en Muestra_elevacion: "
            + ", ".join(sorted(faltantes_muestra))
        )

    # Validar la estructura del diccionario de datos.
    faltantes_diccionario = COLUMNAS_DICCIONARIO - set(hojas["Diccionario"].columns)

    if faltantes_diccionario:
        raise ValueError(
            "Faltan columnas en Diccionario: "
            + ", ".join(sorted(faltantes_diccionario))
        )

    return hojas
