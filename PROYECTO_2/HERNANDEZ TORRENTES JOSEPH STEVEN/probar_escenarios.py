
"""Compara las 12 combinaciones con oleaje normal y reducido."""

from pathlib import Path

import pandas as pd

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.escenarios import (
    comparar_escenarios,
    seleccionar_menor_costo,
)


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def main():
    """Evalúa los escenarios y muestra la opción más económica válida."""

    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    resultados = comparar_escenarios(
        registros,
        hojas["Opciones_convertidor"],
        hojas["Opciones_bateria"],
        consumo_w=300.0,
        reduccion=0.20,
    )

    columnas = [
        "convertidor",
        "bateria",
        "costo_total_colones",
        "disponibilidad_base_pct",
        "disponibilidad_reducido_pct",
        "cumple_ambos",
    ]

    print("\nCOMPARACION DE ESCENARIOS")
    print("-" * 95)

    print(resultados[columnas].to_string(
        index=False, float_format="%.2f"
    ))

    mejor = seleccionar_menor_costo(resultados)

    print("\nSELECCION FINAL SEGUN EL MODELO ACTUAL")

    if mejor is None:
        print("Ninguna combinación cumple ambos escenarios.")
    else:
        print("Convertidor:", mejor["convertidor"])
        print("Batería:", mejor["bateria"])
        print("Costo total (CRC):", mejor["costo_total_colones"])
        print(
            "Disponibilidad normal (%):",
            round(mejor["disponibilidad_base_pct"], 2)
        )
        print(
            "Disponibilidad reducida (%):",
            round(mejor["disponibilidad_reducido_pct"], 2)
        )


if __name__ == "__main__":
    main()
