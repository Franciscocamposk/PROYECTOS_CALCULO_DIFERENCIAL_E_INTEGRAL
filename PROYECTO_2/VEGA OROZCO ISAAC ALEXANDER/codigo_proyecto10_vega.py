# -*- coding: utf-8 -*-
"""
PROYECTO 10: RUIDO DE EMBARCACIONES Y BALLENAS JOROBADAS EN EL GOLFO DULCE
Curso: MA-0321 Cálculo Diferencial e Integral (Cálculo II)
Estudiante: Vega Orozco Isaac Alexander (Código: C-08)
Universidad de Costa Rica - Sede del Sur

Script principal verificable: lee el Excel entregado (datos/P10_C-08_VEGA.xlsx),
ejecuta la limpieza, calibración acústica, validación numérica de integrales,
balance de la temporada, evaluación de escenarios y análisis de sensibilidad.
"""

from pathlib import Path

from src.limpieza import cargar_datos, extraer_parametros, limpiar_pasos
from src.modelo import (
    ModeloAcusticoGolfo,
    energia_paso,
    energia_temporada,
    estimar_fuente,
    p2_teorico,
    simpson_propio,
    trapecio_propio,
    validar_modelo,
)
from src.escenarios import analizar_escenarios, evaluar_medida


def ejecutar_demostracion_completa(ruta_excel: Path | None = None) -> None:
    """Ejecuta el flujo completo leyendo directamente la base de datos Excel."""
    base_dir = Path(__file__).resolve().parent
    if ruta_excel is None:
        ruta_excel = base_dir / "datos" / "P10_C-08_VEGA.xlsx"

    datos = cargar_datos(ruta_excel)
    params = extraer_parametros(datos["Parametros"])

    print("=" * 88)
    print("PROYECTO 10 (C-08 VEGA): RUIDO DE EMBARCACIONES Y BALLENAS JOROBADAS EN GOLFO DULCE")
    print("=" * 88)

    # 1. Exploración y limpieza de datos
    df_limpio, resumen_limp = limpiar_pasos(datos["Pasos_embarcaciones"])
    print("\n[1] EXPLORACIÓN Y LIMPIEZA DE DATOS (Hoja: Pasos_embarcaciones)")
    print(f"  • Total de registros observados (jul-oct): {resumen_limp['total_registros']}")
    print(f"  • Velocidades faltantes (NaN):             {resumen_limp['n_vel_faltantes']} (IDs: {resumen_limp['ids_vel_faltantes']})")
    print(f"  • Velocidades físicamente imposibles:      {resumen_limp['n_vel_imposibles']} (IDs: {resumen_limp['ids_vel_imposibles']})")
    print(f"  • Distancias mínimas faltantes (NaN):      {resumen_limp['n_dist_faltantes']} (IDs: {resumen_limp['ids_dist_faltantes']})")
    print("  • Tratamiento: Imputación mediante la mediana válida por tipo de embarcación.")

    # 2. Calibración con el hidrófono usando la clase ModeloAcusticoGolfo
    modelo = ModeloAcusticoGolfo(
        fondo_pa2=params["fondo_pa2"],
        v_ref_nudos=params["v_ref_nudos"],
        p_ref_pa=params["p_ref_pa"],
    )
    cal = modelo.calibrar(datos["Hidrofono"])

    print("\n[2] CALIBRACIÓN ACÚSTICA CON HIDRÓFONO (Hoja: Hidrofono)")
    print(f"  • Ruido ambiental restado (p0²):           {params['fondo_pa2']:.6f} Pa²")
    for p in cal["pases"]:
        print(
            f"  • Pase {p['pase']} (v={p['v_nudos']:.0f} kts, d={p['d_m']:.0f} m): "
            f"Integral Trapecio = {p['E_trapecio_Pa2s']:.4f} Pa²·s  =>  S{p['pase']} = {p['S_Pa2m2']:,.2f} Pa²·m²"
        )
    print(f"  • Exponente de velocidad n = ln(S2/S1)/ln(v2/v1): {cal['n']:.4f}")
    print(f"  • Constante de fuente S0 (a v0 = {params['v_ref_nudos']:.0f} nudos):     {cal['S0']:,.2f} Pa²·m²")

    # 3. Validación matemática obligatoria
    val = validar_modelo()
    print("\n[3] VALIDACIÓN MATEMÁTICA OBLIGATORIA (S=1, d=100 m, v=5 m/s, T=2000 s, h=0.5 s)")
    print(f"  • Integral numérica Trapecio propio:       {val['trapecio_Pa2s']:.8f} Pa²·s")
    print(f"  • Integral numérica Simpson 1/3 propio:    {val['simpson_Pa2s']:.8f} Pa²·s")
    print(f"  • Fórmula analítica truncada (arctan):     {val['truncada_Pa2s']:.8f} Pa²·s")
    print(f"  • Error relativo |Trapecio - Truncada|:    {val['error_relativo_pct']:.8f}% (< 0.1% exigido)")
    print(f"  • Integral impropia exacta pi*S/(d*v):     {val['impropia_Pa2s']:.8f} Pa²·s (cobertura: {val['cobertura_pct']:.2f}%)")

    # 4. Balance acústico de la temporada
    e_total, nivel_db, desglose = modelo.evaluar_temporada(df_limpio)
    print(f"\n[4] BALANCE ACÚSTICO DE LA TEMPORADA BASE ({len(df_limpio):,} PASOS)")
    print(f"  • Energía sonora acumulada (E_temp):       {e_total:,.2f} Pa²·s")
    print(f"  • Nivel de exposición en decibelios:       {nivel_db:.2f} dB (re 1 µPa²·s)")
    print("\n  Desglose por tipo de embarcación:")
    for _, row in desglose.iterrows():
        print(
            f"    - {row['tipo']:<18} | Pasos: {int(row['viajes']):>3} | "
            f"Vel. media: {row['velocidad_media_nudos']:>4.1f} kts | "
            f"Aporte: {row['aporte_pct']:>5.2f}% | Nivel: {row['nivel_dB']:>6.2f} dB"
        )

    # 5. Evaluación comparativa de opciones
    df_res, decision = analizar_escenarios(
        df_limpio, datos["Opciones"], params, cal["S0"], cal["n"]
    )
    opt_base = decision["optima_meta_base"]
    opt_60 = decision["optima_meta_mas10"]

    print(f"\n[5] EVALUACIÓN COMPARATIVA DE OPCIONES (Meta mínima: >= {params['meta_pct']:.1f}% de reducción)")
    for _, r in df_res.iterrows():
        etiqueta = "[CUMPLE (ÓPTIMA)]" if opt_base and r["opcion"] == opt_base["opcion"] else ("[CUMPLE]" if r["cumple_meta"] else "[NO CUMPLE]")
        print(
            f"  • Opción {r['opcion']} ({r['descripcion']:<49}): "
            f"Reducción = {r['reduccion_pct']:>5.2f}% ({r['delta_dB']:>+5.2f} dB) | "
            f"Horas extra = {r['horas_extra']:>5.1f} h | Costo Total = CRC {r['costo_total_CRC']:>10,.0f} | {etiqueta}"
        )

    # 6. Recomendación y sensibilidad  
    print(f"\n[6] RECOMENDACIÓN Y SENSIBILIDAD (+10 PUNTOS PORCENTUALES -> {params['meta_pct'] + 10:.0f}%)")
    if opt_base:
        print(f"  • Medida recomendada: Opción {opt_base['opcion']} ({opt_base['descripcion']})")
        print(f"  • Reducción lograda:  {opt_base['reduccion_pct']:.2f}% ({opt_base['delta_dB']:+.2f} dB)")
        print(
            f"  • Costo total:        CRC {opt_base['costo_total_CRC']:,.0f} "
            f"(CRC {opt_base['costo_fijo_CRC']:,.0f} fijo + CRC {opt_base['costo_operacion_CRC']:,.0f} por {opt_base['horas_extra']:.1f} h)"
        )
        cambia_txt = "SÍ" if decision["cambia_decision"] else f"NO (Opción {opt_60['opcion']} logra {opt_60['reduccion_pct']:.2f}% > {params['meta_pct'] + 10:.0f}%)"
        print(f"  • ¿Cambia la decisión si la meta sube a {params['meta_pct'] + 10:.0f}%?: {cambia_txt}")
    print("=" * 88)


if __name__ == "__main__":
    ejecutar_demostracion_completa()
