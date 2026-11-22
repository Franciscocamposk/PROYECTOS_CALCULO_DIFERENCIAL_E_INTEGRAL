# -*- coding: utf-8 -*-
"""
Script de generación reproducible de tablas y figuras en resultados/.
Ejecución: python -m src.reporte
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from src.limpieza import cargar_datos, extraer_parametros, limpiar_pasos
from src.modelo import ModeloAcusticoGolfo, validar_modelo
from src.escenarios import analizar_escenarios


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    ruta_excel = base_dir / "datos" / "P10_C-08_VEGA.xlsx"
    out_dir = base_dir / "resultados"
    out_dir.mkdir(exist_ok=True)

    datos = cargar_datos(ruta_excel)
    params = extraer_parametros(datos["Parametros"])
    df_limpio, resumen_limp = limpiar_pasos(datos["Pasos_embarcaciones"])

    modelo = ModeloAcusticoGolfo(
        fondo_pa2=params["fondo_pa2"],
        v_ref_nudos=params["v_ref_nudos"],
        p_ref_pa=params["p_ref_pa"],
    )
    cal = modelo.calibrar(datos["Hidrofono"])
    e_base, db_base, desglose = modelo.evaluar_temporada(df_limpio)
    df_escenarios, decision = analizar_escenarios(
        df_limpio, datos["Opciones"], params, cal["S0"], cal["n"]
    )
    val = validar_modelo()

    # Guardar tablas CSV reproducibles
    desglose.to_csv(out_dir / "desglose_flota.csv", index=False)
    df_escenarios.to_csv(out_dir / "evaluacion_opciones.csv", index=False)

    # Figura 1: Histograma de velocidades y distancias
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), dpi=200)
    axes[0].hist(df_limpio["velocidad_nudos"], bins=22, color="#23529A", edgecolor="white", alpha=0.9)
    axes[0].axvline(10.0, color="#9E4B3E", linestyle="--", linewidth=2, label="Límite Opción A (10 nudos)")
    axes[0].set_title("Distribución de velocidades (1,100 pasos)")
    axes[0].set_xlabel("Velocidad (nudos)")
    axes[0].set_ylabel("Cantidad de viajes")
    axes[0].legend()

    axes[1].hist(df_limpio["distancia_minima_m"], bins=22, color="#5CB2B9", edgecolor="white", alpha=0.9)
    axes[1].axvline(300.0, color="#9E4B3E", linestyle="--", linewidth=2, label="Mínimo Opción C (300 m)")
    axes[1].set_title("Distribución de distancias mínimas")
    axes[1].set_xlabel("Distancia mínima (m)")
    axes[1].set_ylabel("Cantidad de viajes")
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(out_dir / "histogramas_flota.png", dpi=200)
    plt.close(fig)

    # Figura 2: Comparación de opciones
    fig, ax1 = plt.subplots(figsize=(8.5, 4.5), dpi=200)
    x = np.arange(len(df_escenarios))
    colores = ["#4B5D2A" if c else "#9E4B3E" for c in df_escenarios["cumple_meta"]]
    ax1.bar(x - 0.18, df_escenarios["reduccion_pct"], width=0.35, color=colores, label="Reducción ruido (%)")
    ax1.axhline(params["meta_pct"], color="#23529A", linestyle="--", label=f"Meta {params['meta_pct']:.0f}%")
    ax1.axhline(params["meta_pct"] + 10, color="#9E4B3E", linestyle=":", label=f"Meta {params['meta_pct']+10:.0f}%")
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"Opción {o}" for o in df_escenarios["opcion"]])
    ax1.set_ylabel("Reducción de energía sonora (%)")
    ax1.set_ylim(0, 105)

    ax2 = ax1.twinx()
    ax2.bar(x + 0.18, df_escenarios["costo_total_CRC"] / 1e6, width=0.35, color="#5CB2B9", label="Costo (Millones CRC)")
    ax2.set_ylabel("Costo total (Millones CRC)")

    ax1.set_title("Comparación de opciones: Reducción (%) vs Costo total")
    fig.tight_layout()
    fig.savefig(out_dir / "comparacion_opciones.png", dpi=200)
    plt.close(fig)

    print("Reporte generado en:", out_dir)
    print(f"Limpieza: {resumen_limp['n_vel_faltantes']} vel NaN, {resumen_limp['n_vel_imposibles']} vel imposibles, {resumen_limp['n_dist_faltantes']} dist NaN")
    print(f"Calibración: S0 = {cal['S0']:.2f} Pa²·m², n = {cal['n']:.4f}")
    print(f"Temporada base: E = {e_base:.2f} Pa²·s ({db_base:.2f} dB)")
    print(f"Validación trapecio: error = {val['error_relativo_pct']:.8f}%")
    print(f"Decisión óptima: Opción {decision['optima_meta_base']['opcion']} | Cambia al 60%: {decision['cambia_decision']}")


if __name__ == "__main__":
    main()
