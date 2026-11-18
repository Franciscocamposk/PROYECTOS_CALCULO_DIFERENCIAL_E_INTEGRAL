
"""
Compara la altura significativa calculada con:
1. Trapecio compuesto.
2. Simpson 1/3 combinado con trapecio.

Lee el Excel original sin modificarlo.
"""

from pathlib import Path

import pandas as pd

from src.calculos_oleaje import calcular_por_registro


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def main():
    """Calcula y compara los métodos en cada registro."""
    muestras = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="Muestra_elevacion",
    )

    trapecio = calcular_por_registro(muestras, metodo="trapecio")
    hibrido = calcular_por_registro(muestras, metodo="hibrido")

    comparacion = pd.DataFrame({
        "registro": trapecio["registro"],
        "Hs_trapecio_m": trapecio["altura_significativa_m"],
        "Hs_hibrido_m": hibrido["altura_significativa_m"],
    })

    comparacion["diferencia_m"] = (
        comparacion["Hs_hibrido_m"]
        - comparacion["Hs_trapecio_m"]
    )

    print("\nCOMPARACION DE METODOS DE INTEGRACION")
    print("-" * 65)
    print(comparacion.to_string(index=False, float_format="%.6f"))


if __name__ == "__main__":
    main()
