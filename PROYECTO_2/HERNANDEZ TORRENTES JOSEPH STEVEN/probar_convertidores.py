
"""
Evalúa los tres convertidores con los 960 registros horarios.

No modifica el archivo Excel original.
No realiza todavía simulaciones de baterías.
"""

from pathlib import Path

import pandas as pd

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.convertidores import calcular_generacion_convertidor


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def main():
    """Calcula la potencia horaria y resume cada convertidor."""
    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    convertidores = hojas["Opciones_convertidor"]

    print("\nGENERACION ELECTRICA POR CONVERTIDOR")
    print("-" * 75)

    for _, convertidor in convertidores.iterrows():
        resultado = calcular_generacion_convertidor(
            registros, convertidor
        )

        potencia = resultado["potencia_generada_w"]

        print(f"\nConvertidor: {convertidor['convertidor']}")
        print(f"Potencia nominal: {convertidor['potencia_nominal_W']} W")
        print(f"Potencia media: {potencia.mean():.3f} W")
        print(f"Potencia minima: {potencia.min():.3f} W")
        print(f"Potencia maxima: {potencia.max():.3f} W")
        print(f"Horas con generacion >= 300 W: {(potencia >= 300).sum()}")
        print(f"Total de horas analizadas: {len(potencia)}")


if __name__ == "__main__":
    main()
