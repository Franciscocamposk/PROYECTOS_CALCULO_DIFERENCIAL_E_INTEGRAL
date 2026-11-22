

"""Verificación del flujo energético usando los registros originales."""

from pathlib import Path

import pandas as pd

from src.energia_oleaje import calcular_flujo_por_hora


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def main():
    """Lee el Excel, calcula flujos y presenta un resumen."""
    registros = pd.read_excel(
        RUTA_EXCEL,
        sheet_name="Registros_oleaje",
    )

    resultados = calcular_flujo_por_hora(registros)

    print("\nFLUJO ENERGETICO DEL OLEAJE")
    print("-" * 65)

    columnas = [
        "fecha_hora",
        "altura_significativa_m",
        "periodo_pico_s",
        "periodo_energetico_s",
        "flujo_energia_w_m",
    ]

    print(resultados[columnas].head(10).to_string(index=False))

    print("\nRESUMEN")
    print("Registros totales:", len(resultados))
    print(
        "Registros con flujo calculado:",
        resultados["flujo_energia_w_m"].notna().sum(),
    )
    print(
        "Registros con flujo pendiente:",
        resultados["flujo_energia_w_m"].isna().sum(),
    )
    print(
        "Flujo medio de registros validos (W/m):",
        round(resultados["flujo_energia_w_m"].mean(), 4),
    )


if __name__ == "__main__":
    main()
