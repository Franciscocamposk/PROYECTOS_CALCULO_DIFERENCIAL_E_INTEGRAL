
"""
Aplicación web del Proyecto 8.

Energía de las olas para una boya frente a Pavones.

Permite:
- Comparar las 12 combinaciones.
- Consultar escenarios de oleaje.
- Visualizar generación eléctrica y almacenamiento.
- Identificar la solución de menor costo que cumple 99 %.

Todos los cálculos utilizan los módulos del proyecto.
El Excel original solo se lee; nunca se modifica.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.escenarios import (
    comparar_escenarios,
    reducir_oleaje,
    seleccionar_menor_costo,
)
from src.convertidores import calcular_generacion_convertidor
from src.baterias import simular_bateria, resumir_simulacion


RUTA_EXCEL = Path(__file__).resolve().parent / "P08_C-04_HERNANDEZ.xlsx"

st.set_page_config(
    page_title="Proyecto 8 | Energía de las olas",
    page_icon="🌊",
    layout="wide",
)


@st.cache_data
def cargar_proyecto():
    """Lee el Excel y prepara los registros una sola vez."""
    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    return (
        registros,
        hojas["Opciones_convertidor"],
        hojas["Opciones_bateria"],
    )


st.title("🌊 Energía de las olas frente a Pavones")

st.write(
    "Proyecto 8 — Cálculo Diferencial e Integral. "
    "Evaluación de convertidores y baterías para una boya marina."
)

st.caption(
    "Modelo horario de 960 registros. Consumo de 300 W, "
    "batería inicialmente cargada al 100 % y eficiencia "
    "ideal de almacenamiento."
)

try:
    registros, convertidores, baterias = cargar_proyecto()
except (FileNotFoundError, ValueError, KeyError) as error:
    st.error(f"No fue posible cargar los datos: {error}")
    st.stop()


# Comparación en ambos escenarios
comparacion = comparar_escenarios(
    registros,
    convertidores,
    baterias,
    consumo_w=300.0,
    reduccion=0.20,
)

mejor = seleccionar_menor_costo(comparacion)


st.subheader("Sistema recomendado")



if mejor is None:
    st.warning(
        "Ninguna combinación alcanza el 99 % "
        "en ambos escenarios."
    )
else:
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Convertidor", mejor["convertidor"])
    c2.metric("Batería", mejor["bateria"])
    c3.metric(
        "Costo total",
        f"₡{int(mejor['costo_total_colones']):,}",
    )
    c4.metric(
        "Disponibilidad reducida",
        f"{mejor['disponibilidad_reducido_pct']:.2f} %",
    )


st.subheader("Comparación de las 12 combinaciones")

columnas = [
    "convertidor",
    "bateria",
    "costo_total_colones",
    "disponibilidad_base_pct",
    "disponibilidad_reducido_pct",
    "cumple_ambos",
]


# Tabla comparativa con encabezados y unidades comprensibles.
st.dataframe(
    comparacion[columnas],
    hide_index=True,
    width="stretch",
    column_config={
        "convertidor": st.column_config.TextColumn(
            "Convertidor"
        ),
        "bateria": st.column_config.TextColumn(
            "Batería"
        ),
        "costo_total_colones": st.column_config.NumberColumn(
            "Costo total (₡)",
            format="₡%d",
        ),
        "disponibilidad_base_pct": st.column_config.NumberColumn(
            "Disponibilidad normal (%)",
            format="%.2f",
        ),
        "disponibilidad_reducido_pct": st.column_config.NumberColumn(
            "Disponibilidad reducida (%)",
            format="%.2f",
        ),
        "cumple_ambos": st.column_config.CheckboxColumn(
            "Cumple ambos escenarios"
        ),
    },
)



st.subheader("Explorar un sistema")

col1, col2, col3 = st.columns(3)

with col1:
    nombre_convertidor = st.selectbox(
        "Convertidor",
        convertidores["convertidor"].tolist(),
        index=2,
    )

with col2:
    nombre_bateria = st.selectbox(
        "Batería",
        baterias["bateria"].tolist(),
        index=3,
    )

with col3:
    escenario = st.selectbox(
        "Escenario",
        ["Normal", "Oleaje reducido 20 %"],
    )


convertidor = convertidores.loc[
    convertidores["convertidor"] == nombre_convertidor
].iloc[0]

bateria = baterias.loc[
    baterias["bateria"] == nombre_bateria
].iloc[0]


if escenario == "Normal":
    datos_escenario = registros
else:
    datos_escenario = reducir_oleaje(
        registros,
        reduccion=0.20,
    )


generacion = calcular_generacion_convertidor(
    datos_escenario,
    convertidor,
)

simulacion = simular_bateria(
    generacion,
    capacidad_kwh=float(bateria["capacidad_kWh"]),
    consumo_w=300.0,
    carga_inicial=1.0,
)

resumen = resumir_simulacion(simulacion)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Disponibilidad",
    f"{resumen['disponibilidad_pct']:.2f} %",
)
c2.metric(
    "Horas cubiertas",
    str(resumen["horas_cubiertas"]),
)
c3.metric(
    "Horas sin cobertura",
    str(resumen["horas_sin_cobertura"]),
)
c4.metric(
    "Energía no servida",
    f"{resumen['energia_no_servida_wh']:.2f} Wh",
)

if resumen["cumple_99_pct"]:
    st.success("Este sistema cumple el 99 % en el escenario seleccionado.")
else:
    st.warning("Este sistema no cumple el 99 % en este escenario.")


# Visualizaciones horarias
graficos = simulacion.set_index("fecha_hora")

st.subheader("Potencia eléctrica generada")

potencia = graficos[["potencia_generada_w"]].copy()
potencia["consumo_estacion_w"] = 300.0

st.line_chart(potencia, y_label="Potencia (W)")



st.subheader("Energía almacenada en la batería")

# Preparar valores en kWh con fechas reales del registro.
energia = simulacion[
    ["fecha_hora", "energia_bateria_final_wh"]
].copy()

energia["energia_bateria_final_kwh"] = (
    energia["energia_bateria_final_wh"] / 1000.0
)

# Limitar el eje horizontal al intervalo observado.
inicio = energia["fecha_hora"].min()
fin = energia["fecha_hora"].max()
capacidad = float(bateria["capacidad_kWh"])

grafico_bateria = (
    alt.Chart(energia)
    .mark_line(color="#1677C8", strokeWidth=2)
    .encode(
        x=alt.X(
            "fecha_hora:T",
            title="Fecha",
            scale=alt.Scale(domain=[inicio, fin]),
            axis=alt.Axis(format="%d/%m"),
        ),
        y=alt.Y(
            "energia_bateria_final_kwh:Q",
            title="Energía almacenada (kWh)",
            scale=alt.Scale(domain=[0, capacidad]),
        ),
        tooltip=[
            alt.Tooltip("fecha_hora:T", title="Fecha"),
            alt.Tooltip(
                "energia_bateria_final_kwh:Q",
                title="Energía (kWh)",
                format=".3f",
            ),
        ],
    )
    .properties(height=350)
    .interactive(bind_y=False)
)

st.altair_chart(
    grafico_bateria,
    width="stretch",
)

st.caption(
    f"Capacidad máxima: {capacidad:g} kWh. "
    "La simulación comienza con la batería al 100 %."
)


c1, c2, c3 = st.columns(3)

c1.metric("Horas procesadas", len(registros))
c2.metric(
    "Alturas interpoladas",
    int(registros["altura_estimada"].sum()),
)
c3.metric(
    "Flujo medio",
    f"{registros['flujo_energia_w_m'].mean():,.2f} W/m",
)

st.info(
    "Los resultados representan una simulación con los datos "
    "y supuestos del proyecto. No constituyen una garantía "
    "de funcionamiento en condiciones reales."
)
