
"""
Preparación integral de registros de oleaje.

Proyecto 8: energía de las olas frente a Pavones.

Conecta:
1. Interpolación de alturas faltantes.
2. Identificación de valores estimados.
3. Cálculo horario del flujo energético.

Nunca modifica el DataFrame original.
"""

import pandas as pd

from src.limpieza import interpolar_alturas
from src.energia_oleaje import calcular_flujo_por_hora


def preparar_energia_oleaje(
    registros: pd.DataFrame,
    densidad_kg_m3: float = 1025.0,
    gravedad_m_s2: float = 9.81,
    relacion_periodos: float = 0.90,
) -> pd.DataFrame:
    """
    Prepara registros horarios para el modelo energético.

    Los valores faltantes de altura se interpolan utilizando
    la función de limpieza previamente implementada.

    Conserva una marca 'altura_estimada' para distinguir
    mediciones originales de valores interpolados.

    Los valores atípicos no se sustituyen automáticamente.

    Retorna:
        DataFrame independiente con datos preparados,
        periodo energético y flujo de energía en W/m.
    """
    if not isinstance(registros, pd.DataFrame):
        raise TypeError("Los registros deben ser un DataFrame.")

    columnas = {
        "fecha_hora",
        "altura_significativa_m",
        "periodo_pico_s",
    }

    if not columnas.issubset(registros.columns):
        raise ValueError("Faltan columnas necesarias de oleaje.")

    # Copia independiente: no modificar registros originales.
    datos = registros.copy(deep=True)

    # Identificar faltantes antes de interpolarlos.
    faltantes_originales = datos["altura_significativa_m"].isna()

    # Reutilizar la limpieza validada en etapas anteriores.
    datos = interpolar_alturas(datos)

    # Identificar explícitamente las alturas estimadas.
    # Se conserva una columna de auditoría para el análisis.
    datos["altura_estimada"] = faltantes_originales.to_numpy()

    # Comprobar que la interpolación quedó completa.
    if datos["altura_significativa_m"].isna().any():
        raise ValueError(
            "Persisten alturas faltantes después de interpolar."
        )

    # Calcular el flujo energético sobre los datos preparados.
    resultados = calcular_flujo_por_hora(
        datos,
        densidad_kg_m3=densidad_kg_m3,
        gravedad_m_s2=gravedad_m_s2,
        relacion_periodos=relacion_periodos,
    )

    return resultados
