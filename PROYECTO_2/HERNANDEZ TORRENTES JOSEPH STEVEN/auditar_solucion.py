
"""
Auditoría energética del sistema WEC-150 + B20.

Verifica los escenarios normal y reducido:
- Balance de energía en cada hora.
- Disponibilidad del suministro.
- Energía mínima y final de la batería.
- Energía no servida y excedentes.

Los cálculos se realizan en memoria.
El archivo Excel original no se modifica.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.escenarios import reducir_oleaje
from src.convertidores import calcular_generacion_convertidor
from src.baterias import simular_bateria, resumir_simulacion


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"


def auditar_escenario(nombre, registros, convertidor):
    """Simula y verifica la conservación de energía por hora."""

    generacion = calcular_generacion_convertidor(
        registros, convertidor
    )

    simulacion = simular_bateria(
        generacion,
        capacidad_kwh=20.0,
        consumo_w=300.0,
        carga_inicial=1.0,
    )

    entradas = (
        simulacion["energia_bateria_inicio_wh"]
        + simulacion["energia_generada_wh"]
    )

    salidas = (
        simulacion["energia_servida_wh"]
        + simulacion["energia_vertida_wh"]
        + simulacion["energia_bateria_final_wh"]
    )

    errores = ~np.isclose(entradas, salidas, atol=1e-7, rtol=1e-10)

    resumen = resumir_simulacion(simulacion)

    print(f"\nESCENARIO: {nombre}")
    print("-" * 55)
    print("Horas analizadas:", resumen["horas_totales"])
    print("Horas sin cobertura:", resumen["horas_sin_cobertura"])
    print("Disponibilidad (%):", round(resumen["disponibilidad_pct"], 4))
    print("Errores de balance:", int(errores.sum()))
    print(
        "Carga mínima de batería (Wh):",
        round(simulacion["energia_bateria_final_wh"].min(), 3)
    )
    print(
        "Carga final de batería (Wh):",
        round(resumen["energia_final_wh"], 3)
    )
    print(
        "Energía no servida (Wh):",
        round(resumen["energia_no_servida_wh"], 3)
    )
    print(
        "Energía vertida (Wh):",
        round(simulacion["energia_vertida_wh"].sum(), 3)
    )

    assert not errores.any(), "Se detectó un error de balance."
    assert simulacion["energia_bateria_final_wh"].between(
        -1e-8, 20000.00000001
    ).all(), "La batería salió de sus límites físicos."

    assert resumen["cumple_99_pct"], (
        f"{nombre}: disponibilidad inferior al 99 %."
    )


def main():
    """Audita la combinación ganadora en ambos escenarios."""

    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    convertidores = hojas["Opciones_convertidor"]
    seleccionado = convertidores.loc[
        convertidores["convertidor"] == "WEC-150"
    ].iloc[0]

    auditar_escenario("NORMAL", registros, seleccionado)

    reducidos = reducir_oleaje(registros, reduccion=0.20)

    auditar_escenario(
        "OLEAJE REDUCIDO 20 %",
        reducidos,
        seleccionado,
    )

    print("\nAUDITORIA ENERGETICA COMPLETADA CORRECTAMENTE")


if __name__ == "__main__":
    main()
