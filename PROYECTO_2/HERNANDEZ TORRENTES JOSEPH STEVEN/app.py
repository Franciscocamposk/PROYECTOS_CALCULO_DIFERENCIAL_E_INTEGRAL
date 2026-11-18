
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
from io import BytesIO

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
def cargar_proyecto(archivo_excel: bytes | None = None):
    """
    Carga el Excel original o uno proporcionado por el usuario.

    Parámetros:
        archivo_excel: contenido binario de un Excel opcional.

    Retorna:
        registros procesados, convertidores y baterías.

    No modifica ningún archivo de entrada.
    """
    if archivo_excel is None:
        origen = RUTA_EXCEL
    else:
        origen = BytesIO(archivo_excel)

    hojas = pd.read_excel(origen, sheet_name=None)

    hojas_obligatorias = {
        "Registros_oleaje",
        "Opciones_convertidor",
        "Opciones_bateria",
        "Parametros",
        "Muestra_elevacion",
        "Diccionario",
    }

    faltantes = hojas_obligatorias - set(hojas)

    if faltantes:
        raise ValueError(
            "Faltan hojas obligatorias: "
            + ", ".join(sorted(faltantes))
        )

    registros = preparar_energia_oleaje(
        hojas["Registros_oleaje"]
    )

    return (
        registros,
        hojas["Opciones_convertidor"],
        hojas["Opciones_bateria"],
    )


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


# ============================================================
# SELECCIÓN DE LA FUENTE DE DATOS
# ============================================================

st.subheader("Fuente de datos")

archivo_subido = st.file_uploader(
    "Cargar otro archivo Excel con la misma estructura",
    type=["xlsx"],
    help=(
        "Si no se selecciona un archivo, se utilizará "
        "automáticamente el Excel original del Proyecto 8."
    ),
)

if archivo_subido is None:
    contenido_excel = None
    st.caption(
        "Fuente activa: P08_C-04_HERNANDEZ.xlsx"
    )
else:
    contenido_excel = archivo_subido.getvalue()
    st.caption(
        f"Fuente activa: {archivo_subido.name}"
    )

try:
    registros, convertidores, baterias = cargar_proyecto(
        contenido_excel
    )

except (
    FileNotFoundError,
    ValueError,
    KeyError,
    TypeError,
    ImportError,
) as error:
    st.error(
        f"No fue posible cargar los datos: {error}"
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

# ============================================================
# INTEGRAL DE POTENCIA: ENERGÍA GENERADA
# ============================================================

st.subheader("Integral de potencia y energía acumulada")

st.write(
    "La energía generada corresponde al área bajo "
    "la curva de potencia eléctrica respecto al tiempo."
)

st.latex(
    r"E_g = \int_{t_0}^{t_f} P_g(t)\,dt"
)

# Cada registro representa un intervalo de una hora.
dt_horas = 1.0

# Integración discreta de la potencia horaria.
energia_total_wh = (
    simulacion["potencia_generada_w"].sum()
    * dt_horas
)

energia_total_kwh = energia_total_wh / 1000.0

# Energía requerida durante todas las horas analizadas.
energia_requerida_kwh = (
    float(consumo_w)
    * len(simulacion)
    * dt_horas
    / 1000.0
)

c1, c2 = st.columns(2)

c1.metric(
    "Energía eléctrica generada",
    f"{energia_total_kwh:,.2f} kWh",
)

c2.metric(
    "Energía requerida por la estación",
    f"{energia_requerida_kwh:,.2f} kWh",
)

# Preparar datos para mostrar el área bajo P(t).
datos_integral = simulacion[
    ["fecha_hora", "potencia_generada_w"]
].copy()

# Área sombreada que representa la integral.
area_potencia = (
    alt.Chart(datos_integral)
    .mark_area(
        color="#4DA3E2",
        opacity=0.30,
    )
    .encode(
        x=alt.X(
            "fecha_hora:T",
            title="Tiempo",
        ),
        y=alt.Y(
            "potencia_generada_w:Q",
            title="Potencia eléctrica (W)",
        ),
        tooltip=[
            alt.Tooltip(
                "fecha_hora:T",
                title="Fecha",
            ),
            alt.Tooltip(
                "potencia_generada_w:Q",
                title="Potencia (W)",
                format=".2f",
            ),
        ],
    )
)

linea_potencia = (
    alt.Chart(datos_integral)
    .mark_line(
        color="#1261A0",
        strokeWidth=1.5,
    )
    .encode(
        x="fecha_hora:T",
        y="potencia_generada_w:Q",
    )
)

grafico_integral = (
    (area_potencia + linea_potencia)
    .properties(
        height=350,
        title="Área bajo la curva de generación eléctrica",
    )
    .interactive()
)

st.altair_chart(
    grafico_integral,
    width="stretch",
)

st.caption(
    "El área sombreada representa la energía eléctrica "
    "generada. La integración discreta utiliza intervalos "
    "de una hora y supone potencia constante dentro "
    "de cada intervalo."
)


# ============================================================
# ENERGÍA ACUMULADA Y BALANCE ENERGÉTICO
# ============================================================

st.subheader("Energía eléctrica acumulada")

st.write(
    "Este gráfico compara la energía total generada "
    "y la energía requerida por la estación a lo largo "
    "de las 960 horas."
)

st.latex(
    r"E(t)=\int_{t_0}^{t}P(u)\,du"
)

# Cada observación representa una hora de generación.
dt_horas = 1.0

datos_acumulados = simulacion[
    ["fecha_hora", "potencia_generada_w"]
].copy()

# Integral acumulada usando intervalos horarios.
datos_acumulados["generada_kwh"] = (
    datos_acumulados["potencia_generada_w"]
    .cumsum()
    * dt_horas
    / 1000.0
)

# Consumo eléctrico acumulado.
datos_acumulados["requerida_kwh"] = (
    pd.Series(
        range(1, len(datos_acumulados) + 1),
        index=datos_acumulados.index,
        dtype=float,
    )
    * float(consumo_w)
    * dt_horas
    / 1000.0
)

# Convertir a formato apropiado para Altair.
datos_grafico_acumulado = datos_acumulados.melt(
    id_vars="fecha_hora",
    value_vars=[
        "generada_kwh",
        "requerida_kwh",
    ],
    var_name="tipo_energia",
    value_name="energia_kwh",
)

grafico_acumulado = (
    alt.Chart(datos_grafico_acumulado)
    .mark_line(strokeWidth=2)
    .encode(
        x=alt.X(
            "fecha_hora:T",
            title="Fecha",
        ),
        y=alt.Y(
            "energia_kwh:Q",
            title="Energía acumulada (kWh)",
        ),
        color=alt.Color(
            "tipo_energia:N",
            title="Tipo de energía",
            scale=alt.Scale(
                domain=[
                    "generada_kwh",
                    "requerida_kwh",
                ],
                range=[
                    "#1677C8",
                    "#E67E22",
                ],
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "fecha_hora:T",
                title="Fecha",
            ),
            alt.Tooltip(
                "tipo_energia:N",
                title="Serie",
            ),
            alt.Tooltip(
                "energia_kwh:Q",
                title="Energía (kWh)",
                format=".2f",
            ),
        ],
    )
    .properties(
        height=350,
        title="Generación y consumo acumulados",
    )
    .interactive()
)

st.altair_chart(
    grafico_acumulado,
    width="stretch",
)

# Valores finales.
generada_final = float(
    datos_acumulados["generada_kwh"].iloc[-1]
)

requerida_final = float(
    datos_acumulados["requerida_kwh"].iloc[-1]
)

diferencia_energia = (
    generada_final - requerida_final
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Generación acumulada",
    f"{generada_final:,.2f} kWh",
)

c2.metric(
    "Demanda acumulada",
    f"{requerida_final:,.2f} kWh",
)

c3.metric(
    "Diferencia generación - demanda",
    f"{diferencia_energia:+,.2f} kWh",
)

st.caption(
    "La diferencia acumulada no representa directamente "
    "la energía disponible en la batería. Parte de la "
    "generación puede desperdiciarse al alcanzar su "
    "capacidad máxima. La disponibilidad real del modelo "
    "se determina con la simulación horaria."
)




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
