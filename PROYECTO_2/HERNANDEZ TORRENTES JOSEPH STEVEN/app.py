
"""
Aplicación web del Proyecto 8.

Energía de las olas para una boya frente a Pavones.

Funciones:
- Comparar 12 combinaciones de convertidores y baterías.
- Evaluar tres escenarios de oleaje.
- Modificar el consumo eléctrico de la estación.
- Visualizar potencia generada y almacenamiento.
- Descargar resultados en formato CSV.
- Recomendar la alternativa de menor costo que cumple el 99 %.

El Excel original se utiliza únicamente para lectura.
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.procesamiento_oleaje import preparar_energia_oleaje
from src.escenarios import (
    comparar_tres_escenarios,
    reducir_oleaje,
)
from src.convertidores import calcular_generacion_convertidor
from src.baterias import simular_bateria, resumir_simulacion


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

RUTA_EXCEL = (
    Path(__file__).resolve().parent
    / "P08_C-04_HERNANDEZ.xlsx"
)

st.set_page_config(
    page_title="Proyecto 8 | Energía de las olas",
    page_icon="🌊",
    layout="wide",
)


# ============================================================
# CARGA Y PREPARACIÓN DE DATOS
# ============================================================

@st.cache_data
def cargar_proyecto():
    """
    Lee todas las hojas del Excel original.

    Prepara los registros del oleaje sin modificar
    el archivo proporcionado por el profesor.
    """
    hojas = pd.read_excel(
        RUTA_EXCEL,
        sheet_name=None,
    )

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    return (
        registros,
        hojas["Opciones_convertidor"],
        hojas["Opciones_bateria"],
    )


@st.cache_data
def generar_csv(datos: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a CSV codificado en UTF-8."""
    return datos.to_csv(index=False).encode("utf-8-sig")


# ============================================================
# ENCABEZADO
# ============================================================

st.title("🌊 Energía de las olas frente a Pavones")

st.write(
    "Proyecto 8 — Cálculo Diferencial e Integral. "
    "Evaluación energética y económica de convertidores "
    "y baterías para una boya oceanográfica."
)

st.caption(
    "Simulación de 960 registros horarios. "
    "Se considera una batería inicialmente cargada "
    "al 100 % y una eficiencia ideal de almacenamiento."
)


# ============================================================
# LEER DATOS
# ============================================================

try:
    registros, convertidores, baterias = cargar_proyecto()

except (FileNotFoundError, ValueError, KeyError) as error:
    st.error(
        f"No fue posible cargar los datos originales: {error}"
    )
    st.stop()


# ============================================================
# PARÁMETRO DE CONSUMO
# ============================================================

st.subheader("Configuración de la demanda eléctrica")

consumo_w = st.slider(
    "Consumo de la estación (W)",
    min_value=100,
    max_value=600,
    value=300,
    step=25,
    help=(
        "El consumo de referencia del proyecto es 300 W. "
        "Modificarlo permite estudiar la sensibilidad "
        "de la recomendación."
    ),
)

if consumo_w != 300:
    st.info(
        f"Se está evaluando un consumo alternativo de "
        f"{consumo_w} W. El consumo original es 300 W."
    )


# ============================================================
# COMPARACIÓN DE LOS TRES ESCENARIOS
# ============================================================

st.subheader("Evaluación de alternativas")

with st.spinner("Evaluando las 12 combinaciones..."):
    comparacion = comparar_tres_escenarios(
        registros,
        convertidores,
        baterias,
        consumo_w=float(consumo_w),
    )

# Seleccionar únicamente las combinaciones que cumplen
# el 99 % en los tres escenarios.
validas = comparacion.loc[
    comparacion["cumple_tres"]
]

# La tabla ya se encuentra ordenada por costo,
# pero se ordena explícitamente por seguridad.
mejor = (
    validas.sort_values(
        "costo_total_colones"
    ).iloc[0]
    if not validas.empty
    else None
)


# ============================================================
# SISTEMA RECOMENDADO
# ============================================================

st.subheader("🏆 Sistema recomendado")

if mejor is None:
    st.warning(
        "Ninguna combinación alcanza el 99 % "
        "de disponibilidad en los tres escenarios "
        "con el consumo seleccionado."
    )

else:
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Convertidor",
        str(mejor["convertidor"]),
    )

    c2.metric(
        "Batería",
        str(mejor["bateria"]),
    )

    c3.metric(
        "Costo total",
        f"₡{int(mejor['costo_total_colones']):,}",
    )

    c4.metric(
        "Disponibilidad adversa",
        f"{mejor['disponibilidad_adverso_pct']:.2f} %",
    )

    st.success(
        "Esta es la combinación de menor costo "
        "que cumple el requisito del 99 % "
        "en los tres escenarios evaluados."
    )


# ============================================================
# TABLA COMPARATIVA
# ============================================================

st.subheader("Comparación de las 12 combinaciones")

columnas = [
    "convertidor",
    "bateria",
    "costo_total_colones",
    "disponibilidad_normal_pct",
    "disponibilidad_moderado_pct",
    "disponibilidad_adverso_pct",
    "cumple_tres",
]

tabla_comparativa = comparacion[columnas].copy()

st.dataframe(
    tabla_comparativa,
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
        "disponibilidad_normal_pct": st.column_config.NumberColumn(
            "Normal (%)",
            format="%.2f",
        ),
        "disponibilidad_moderado_pct": st.column_config.NumberColumn(
            "Moderado -10 % (%)",
            format="%.2f",
        ),
        "disponibilidad_adverso_pct": st.column_config.NumberColumn(
            "Adverso -20 % (%)",
            format="%.2f",
        ),
        "cumple_tres": st.column_config.CheckboxColumn(
            "Cumple los tres"
        ),
    },
)

st.download_button(
    label="📥 Descargar comparación en CSV",
    data=generar_csv(comparacion),
    file_name="proyecto8_comparacion_escenarios.csv",
    mime="text/csv",
)


# ============================================================
# EXPLORACIÓN INTERACTIVA
# ============================================================

st.subheader("Explorar un sistema")

st.write(
    "Seleccione un convertidor, una batería y un escenario "
    "para observar su comportamiento durante las 960 horas."
)

col1, col2, col3 = st.columns(3)

lista_convertidores = convertidores[
    "convertidor"
].tolist()

lista_baterias = baterias[
    "bateria"
].tolist()

with col1:
    nombre_convertidor = st.selectbox(
        "Convertidor",
        lista_convertidores,
        index=(
            lista_convertidores.index("WEC-150")
            if "WEC-150" in lista_convertidores
            else 0
        ),
    )

with col2:
    nombre_bateria = st.selectbox(
        "Batería",
        lista_baterias,
        index=(
            lista_baterias.index("B20")
            if "B20" in lista_baterias
            else 0
        ),
    )

with col3:
    escenario = st.selectbox(
        "Escenario de oleaje",
        [
            "Normal",
            "Oleaje reducido 10 %",
            "Oleaje reducido 20 %",
        ],
    )


# ============================================================
# SELECCIÓN DE EQUIPOS
# ============================================================

convertidor = convertidores.loc[
    convertidores["convertidor"] == nombre_convertidor
].iloc[0]

bateria = baterias.loc[
    baterias["bateria"] == nombre_bateria
].iloc[0]


# ============================================================
# APLICAR ESCENARIO
# ============================================================

factores_reduccion = {
    "Normal": 0.0,
    "Oleaje reducido 10 %": 0.10,
    "Oleaje reducido 20 %": 0.20,
}

reduccion = factores_reduccion[escenario]

if reduccion == 0:
    datos_escenario = registros.copy(deep=True)

else:
    datos_escenario = reducir_oleaje(
        registros,
        reduccion=reduccion,
    )


# ============================================================
# CALCULAR GENERACIÓN
# ============================================================

generacion = calcular_generacion_convertidor(
    datos_escenario,
    convertidor,
)


# ============================================================
# SIMULAR BATERÍA
# ============================================================

simulacion = simular_bateria(
    generacion,
    capacidad_kwh=float(
        bateria["capacidad_kWh"]
    ),
    consumo_w=float(consumo_w),
    carga_inicial=1.0,
)

resumen = resumir_simulacion(simulacion)


# ============================================================
# INDICADORES DEL SISTEMA SELECCIONADO
# ============================================================

st.subheader("Resultados del sistema seleccionado")

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
    f"{resumen['energia_no_servida_wh']:,.2f} Wh",
)

if resumen["cumple_99_pct"]:
    st.success(
        "El sistema seleccionado cumple el requisito "
        "del 99 % en este escenario."
    )

else:
    st.warning(
        "El sistema seleccionado no alcanza el 99 % "
        "en este escenario."
    )


# ============================================================
# GRÁFICO DE POTENCIA GENERADA
# ============================================================

st.subheader("Potencia eléctrica generada")

# Crear una copia independiente para el gráfico.
potencia = simulacion[
    ["fecha_hora", "potencia_generada_w"]
].copy()

potencia["consumo_estacion_w"] = float(consumo_w)

potencia = potencia.set_index("fecha_hora")

st.line_chart(
    potencia,
    x_label="Fecha",
    y_label="Potencia eléctrica (W)",
    width="stretch",
)

st.caption(
    "La gráfica compara la potencia generada "
    "con la demanda eléctrica de la estación."
)


# ============================================================
# GRÁFICO DE ALMACENAMIENTO
# ============================================================

st.subheader("Energía almacenada en la batería")

energia = simulacion[
    [
        "fecha_hora",
        "energia_bateria_final_wh",
    ]
].copy()

# Convertir Wh a kWh para facilitar la interpretación.
energia["energia_bateria_final_kwh"] = (
    energia["energia_bateria_final_wh"] / 1000.0
)

inicio = energia["fecha_hora"].min()
fin = energia["fecha_hora"].max()

capacidad = float(
    bateria["capacidad_kWh"]
)

grafico_bateria = (
    alt.Chart(energia)
    .mark_line(
        color="#1677C8",
        strokeWidth=2,
    )
    .encode(
        x=alt.X(
            "fecha_hora:T",
            title="Fecha",
            scale=alt.Scale(
                domain=[inicio, fin]
            ),
            axis=alt.Axis(
                format="%d/%m"
            ),
        ),
        y=alt.Y(
            "energia_bateria_final_kwh:Q",
            title="Energía almacenada (kWh)",
            scale=alt.Scale(
                domain=[0, capacidad]
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "fecha_hora:T",
                title="Fecha",
            ),
            alt.Tooltip(
                "energia_bateria_final_kwh:Q",
                title="Energía (kWh)",
                format=".3f",
            ),
        ],
    )
    .properties(
        height=350
    )
    .interactive(
        bind_y=False
    )
)

st.altair_chart(
    grafico_bateria,
    width="stretch",
)

st.caption(
    f"Capacidad máxima: {capacidad:g} kWh. "
    "La batería comienza la simulación "
    "completamente cargada."
)


# ============================================================
# DESCARGAR SIMULACIÓN HORARIA
# ============================================================

st.subheader("Descargar los resultados horarios")

st.download_button(
    label="📥 Descargar simulación en CSV",
    data=generar_csv(simulacion),
    file_name=(
        f"proyecto8_{nombre_convertidor}_"
        f"{nombre_bateria}_"
        f"{int(reduccion * 100)}pct.csv"
    ),
    mime="text/csv",
)


# ============================================================
# INFORMACIÓN GENERAL DE LOS REGISTROS
# ============================================================

st.subheader("Resumen de los datos procesados")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Horas procesadas",
    len(registros),
)

c2.metric(
    "Alturas interpoladas",
    int(
        registros["altura_estimada"].sum()
    ),
)

c3.metric(
    "Flujo energético medio",
    (
        f"{registros['flujo_energia_w_m'].mean():,.2f} W/m"
    ),
)


# ============================================================
# SUPUESTOS Y LIMITACIONES
# ============================================================

st.info(
    "Los resultados corresponden a una simulación académica "
    "basada en datos proporcionados por el profesor. "
    "Se supone una batería inicialmente cargada al 100 %, "
    "sin pérdidas adicionales ni degradación. "
    "La disponibilidad calculada no constituye una garantía "
    "de funcionamiento real."
)
