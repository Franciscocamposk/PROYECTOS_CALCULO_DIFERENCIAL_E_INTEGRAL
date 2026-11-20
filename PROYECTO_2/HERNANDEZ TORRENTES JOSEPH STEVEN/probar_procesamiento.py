
"""
Comprueba el procesamiento energético de los 960 registros.

Lee el Excel original y trabaja únicamente en memoria.
No modifica ni guarda cambios en el archivo del profesor.
"""

from pathlib import Path

import pandas as pd

from src.procesamiento_oleaje import preparar_energia_oleaje


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def main():
    """Procesa los registros y muestra un resumen verificable."""
    registros = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="Registros_oleaje",
    )

    resultados = preparar_energia_oleaje(registros)

    print("\nPROCESAMIENTO ENERGETICO DEL OLEAJE")
    print("-" * 60)
    print("Registros originales:", len(registros))
    print(
        "Alturas originalmente faltantes:",
        registros["altura_significativa_m"].isna().sum(),
    )
    print(
        "Alturas estimadas:",
        resultados["altura_estimada"].sum(),
    )
    print(
        "Flujos calculados:",
        resultados["flujo_energia_w_m"].notna().sum(),
    )
    print(
        "Flujo medio (W/m):",
        round(resultados["flujo_energia_w_m"].mean(), 4),
    )

    print("\nREGISTROS INTERPOLADOS")
    columnas = [
        "fecha_hora",
        "altura_significativa_m",
        "altura_estimada",
        "flujo_energia_w_m",
    ]

    print(
        resultados.loc[
            resultados["altura_estimada"], columnas
        ].to_string(index=False)
    )

    # Verificar que el DataFrame original siga intacto.
    assert registros["altura_significativa_m"].isna().sum() == 4


if __name__ == "__main__":
    main()
