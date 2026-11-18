
"""
Generación reproducible de resultados del Proyecto 8.

Ejecutar desde la carpeta individual del proyecto:

    python -m src.reporte

Genera tablas CSV y figuras PNG en resultados/.
El archivo Excel original nunca se modifica.
"""

from pathlib import Path

import matplotlib

# Permite generar gráficos sin abrir ventanas.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.escenarios import comparar_tres_escenarios


# Directorios independientes del lugar de ejecución.
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_EXCEL = RAIZ_PROYECTO / "P08_C-04_HERNANDEZ.xlsx"
RUTA_RESULTADOS = RAIZ_PROYECTO / "resultados"


def generar_reporte() -> None:
    """
    Genera tablas y figuras usando el Excel original.

    Entradas:
        P08_C-04_HERNANDEZ.xlsx.

    Salidas:
        Archivos CSV y PNG en resultados/.

    Unidades:
        Altura: m.
        Flujo energético: W/m.
        Costo: colones.
        Disponibilidad: porcentaje.
    """
    RUTA_RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Leer directamente todas las hojas del Excel.
    hojas = pd.read_excel(
        RUTA_EXCEL,
        sheet_name=None,
    )

    # Validar las hojas utilizadas.
    obligatorias = {
        "Registros_oleaje",
        "Opciones_convertidor",
        "Opciones_bateria",
    }

    faltantes = obligatorias - set(hojas)

    if faltantes:
        raise ValueError(
            f"Faltan hojas: {sorted(faltantes)}"
        )

    # Procesar registros de oleaje.
    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    if registros.empty:
        raise ValueError(
            "No hay registros para generar el reporte."
        )

    # Evaluar 12 combinaciones en tres escenarios.
    comparacion = comparar_tres_escenarios(
        registros,
        hojas["Opciones_convertidor"],
        hojas["Opciones_bateria"],
        consumo_w=300.0,
    )

    # =====================================================
    # EXPORTAR TABLAS
    # =====================================================

    registros.to_csv(
        RUTA_RESULTADOS / "registros_procesados.csv",
        index=False,
        encoding="utf-8-sig",
    )

    comparacion.to_csv(
        RUTA_RESULTADOS / "comparacion_tres_escenarios.csv",
        index=False,
        encoding="utf-8-sig",
    )

    validas = comparacion.loc[
        comparacion["cumple_tres"]
    ].sort_values(
        "costo_total_colones"
    )

    if validas.empty:
        raise RuntimeError(
            "Ninguna combinación cumple los tres escenarios."
        )

    mejor = validas.iloc[0]

    validas.head(1).to_csv(
        RUTA_RESULTADOS / "solucion_recomendada.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # =====================================================
    # FIGURA 1: ALTURA SIGNIFICATIVA
    # =====================================================

    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        registros["fecha_hora"],
        registros["altura_significativa_m"],
        linewidth=0.9,
    )

    ax.set_title(
        "Altura significativa del oleaje frente a Pavones"
    )
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Altura significativa (m)")
    ax.grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig(
        RUTA_RESULTADOS / "altura_oleaje.png",
        dpi=180,
    )

    plt.close(fig)

    # =====================================================
    # FIGURA 2: FLUJO ENERGÉTICO
    # =====================================================

    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        registros["fecha_hora"],
        registros["flujo_energia_w_m"],
        linewidth=0.9,
    )

    ax.fill_between(
        registros["fecha_hora"],
        registros["flujo_energia_w_m"],
        0,
        alpha=0.25,
    )

    ax.set_title(
        "Flujo energético del oleaje"
    )
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Flujo energético (W/m)")
    ax.grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig(
        RUTA_RESULTADOS / "flujo_energetico.png",
        dpi=180,
    )

    plt.close(fig)

    # =====================================================
    # FIGURA 3: DISPONIBILIDAD POR ESCENARIO
    # =====================================================

    etiquetas = (
        comparacion["convertidor"].astype(str)
        + " + "
        + comparacion["bateria"].astype(str)
    )

    posiciones = list(range(len(comparacion)))
    ancho = 0.25

    fig, ax = plt.subplots(figsize=(13, 7))

    ax.barh(
        [x - ancho for x in posiciones],
        comparacion["disponibilidad_normal_pct"],
        height=ancho,
        label="Normal",
    )

    ax.barh(
        posiciones,
        comparacion["disponibilidad_moderado_pct"],
        height=ancho,
        label="Altura -10 %",
    )

    ax.barh(
        [x + ancho for x in posiciones],
        comparacion["disponibilidad_adverso_pct"],
        height=ancho,
        label="Altura -20 %",
    )

    ax.axvline(
        99,
        linestyle="--",
        color="red",
        label="Mínimo requerido: 99 %",
    )

    ax.set_yticks(posiciones)
    ax.set_yticklabels(etiquetas)
    ax.set_xlim(0, 105)
    ax.set_xlabel("Disponibilidad (%)")
    ax.set_ylabel("Convertidor + batería")
    ax.set_title(
        "Disponibilidad de las 12 combinaciones"
    )

    ax.legend()
    ax.grid(axis="x", alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        RUTA_RESULTADOS / "comparacion_disponibilidad.png",
        dpi=180,
    )

    plt.close(fig)

    # =====================================================
    # RESUMEN EN CONSOLA
    # =====================================================

    print("\nREPORTE GENERADO CORRECTAMENTE")
    print(f"Carpeta: {RUTA_RESULTADOS}")
    print(f"Registros: {len(registros)}")
    print(f"Combinaciones: {len(comparacion)}")

    print("\nSISTEMA RECOMENDADO")
    print("Convertidor:", mejor["convertidor"])
    print("Batería:", mejor["bateria"])

    print(
        "Costo: "
        f"₡{mejor['costo_total_colones']:,.0f}"
    )

    for escenario in (
        "normal",
        "moderado",
        "adverso",
    ):
        columna = f"disponibilidad_{escenario}_pct"
        print(
            f"Disponibilidad {escenario}: "
            f"{mejor[columna]:.2f}%"
        )

    print("\nArchivos generados:")

    for archivo in sorted(RUTA_RESULTADOS.iterdir()):
        if archivo.is_file():
            print(" -", archivo.name)


if __name__ == "__main__":
    generar_reporte()
