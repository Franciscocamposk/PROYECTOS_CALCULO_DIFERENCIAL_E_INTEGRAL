
"""
Ejecuta las 12 combinaciones sobre las 960 horas originales.

La interpolación se aplica únicamente sobre una copia.
La batería inicia al 100 % y cada registro representa 1 hora.
"""

from pathlib import Path

import pandas as pd

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.evaluacion_sistemas import evaluar_combinaciones


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def main():
    """Carga, procesa y compara las opciones del Excel."""
    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    resultados = evaluar_combinaciones(
        registros,
        hojas["Opciones_convertidor"],
        hojas["Opciones_bateria"],
    )

    columnas = [
        "convertidor",
        "bateria",
        "costo_total_colones",
        "horas_sin_cobertura",
        "disponibilidad_pct",
        "cumple_99_pct",
    ]

    print("\nEVALUACION DE LAS 12 COMBINACIONES")
    print("-" * 85)
    print(
        resultados[columnas].to_string(
            index=False,
            float_format="%.2f",
        )
    )

    cumplen = resultados[resultados["cumple_99_pct"]]

    print("\nRESULTADO DEL ESCENARIO BASE")

    if cumplen.empty:
        print("Ninguna combinación alcanza el 99 %.")
    else:
        mejor = cumplen.iloc[0]
        print("Convertidor:", mejor["convertidor"])
        print("Batería:", mejor["bateria"])
        print("Costo total (CRC):", mejor["costo_total_colones"])
        print("Disponibilidad (%):", round(mejor["disponibilidad_pct"], 2))

    print("\nCombinaciones evaluadas:", len(resultados))


if __name__ == "__main__":
    main()
