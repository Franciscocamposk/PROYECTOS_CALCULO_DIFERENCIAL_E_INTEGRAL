"""
app.py
---------------------------------------------------------------
Proyecto 5 - Simulador de Ahorro
MA-0321 Calculo Diferencial e Integral - UCR - II Ciclo 2026

Interfaz grafica (Streamlit) que consume EXCLUSIVAMENTE las
funciones ya definidas y validadas en modelo_ahorro.py.
Esta capa no recalcula ni redefine matematica: solo la muestra.

Streamlit vuelve a ejecutar este archivo COMPLETO de arriba a
abajo cada vez que el usuario mueve un control en la barra
lateral. Por eso no hay un main(): todo el codigo de nivel
superior (fuera de funciones) es, en la practica, lo que se
corre en cada refresco de la pagina.

Para ejecutar desde VS Code:
    pip install streamlit plotly
    streamlit run app.py

Se abre en el navegador en http://localhost:8501
---------------------------------------------------------------
"""

import numpy as np                    # malla de tiempos para las graficas
import pandas as pd                   # tablas (DataFrame)
import plotly.graph_objects as go     # graficas interactivas
import streamlit as st                # framework de la interfaz web

import modelo_ahorro as mod           # todas las formulas viven aqui

# ==============================================================
# CONFIGURACION DE LA PAGINA
# ==============================================================

# Configura el titulo de la pestaña del navegador, el icono y usa
# todo el ancho de pantalla disponible (layout="wide") en vez del
# angosto por defecto de Streamlit.
st.set_page_config(
    page_title="Simulador de Ahorro | MA-0321",
    page_icon="💰",
    layout="wide",
)

MONEDA = "₡"  # simbolo de colones, usado en la funcion moneda() de abajo

# --- Estilos propios (encima del tema por defecto de Streamlit) ---
# CSS inyectado como HTML crudo. Define tres clases:
#   .bloque-metrica -> tarjetas blancas de las 4 metricas del encabezado
#   .recomendacion  -> cuadro verde para un mensaje de exito (no se usa
#                      en esta version del archivo, queda definido por
#                      si se agrega la seccion de recomendacion en texto)
#   .no-viable      -> cuadro rojo para el caso "meta no alcanzable"
# Se aplican mas abajo con st.markdown(..., unsafe_allow_html=True).
st.markdown("""
<style>
    .bloque-metrica {
        background: #ffffff;
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .recomendacion {
        background: #eef7ee;
        border-left: 4px solid #2e7d32;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        white-space: pre-line;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .no-viable {
        background: #fdecea;
        border-left: 4px solid #c62828;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        white-space: pre-line;
        font-size: 0.95rem;
    }
    h1, h2, h3 { font-family: "Segoe UI", sans-serif; }
</style>
""", unsafe_allow_html=True)

# Colores fijos por serie: asi un mismo metodo (o escenario de
# tasa) se dibuja siempre con el mismo color en ambas graficas
# (grafica 1 usa las 3 primeras llaves; grafica 2 usa las 3 ultimas).
PALETA = {
    "Interes simple": "#4C78A8",
    "Interes compuesto": "#F28E2B",
    "Capitalizacion continua": "#59A14F",
    "Tasa baja (ahorro regular)": "#4C78A8",
    "Tasa media (ahorro premium)": "#F28E2B",
    "Tasa alta (CDP a 12 meses)": "#E15759",
}


def moneda(valor):
    """
    Formatea un numero como monto en colones: separador de miles,
    sin decimales, con el simbolo ₡ al frente.
    Ejemplo: moneda(1234567.8) -> "₡1,234,568".
    """
    # f"{valor:,.0f}" -> separa miles con coma y redondea a 0
    # decimales; se le antepone el simbolo de moneda.
    return f"{MONEDA}{valor:,.0f}"


# ==============================================================
# BARRA LATERAL - PARAMETROS (conectados directo al modelo)
# ==============================================================
# Cada control de la barra lateral es la version interactiva de
# una llave del diccionario PARAMETROS que usa main.py: aqui no
# hay un diccionario fijo desde el inicio, sino que Streamlit
# guarda el valor actual de cada control y ese valor se vuelve a
# leer en cada refresco de la pagina.

st.sidebar.header("Parametros del modelo")
st.sidebar.caption("Modifique los valores; todo el simulador se recalcula al instante.")

# Capital inicial P: campo numerico entero, con limites razonables
# (min 1,000, max 100 millones) y el valor por defecto justificado
# en el texto de ayuda (help=...).
capital_inicial = st.sidebar.number_input(
    "Capital inicial P (colones)", min_value=1_000, max_value=100_000_000,
    value=500_000, step=10_000, format="%d",
    help="El valor por defecto (₡500,000) es el saldo minimo real que exige "
         "una cuenta de ahorro premium en Costa Rica para generar intereses.",
)
# Tasa anual r: deslizador con paso de 0.5% (0.005) entre 0.5% y 10%.
tasa_anual = st.sidebar.slider(
    "Tasa de interes anual r", min_value=0.005, max_value=0.10,
    value=0.0295, step=0.005, format="%.3f",
    help="El valor por defecto (2.95%) corresponde a la tasa real de una "
         "cuenta de ahorro premium en colones en Costa Rica (2026).",
)
# Frecuencia de capitalizacion n: lista desplegable con las
# opciones tipicas (anual, semestral, trimestral, mensual,
# semanal, diaria). format_func traduce el numero crudo (1,2,4,...)
# a una etiqueta legible en el menu.
frecuencia = st.sidebar.selectbox(
    "Frecuencia de capitalizacion n (veces por anio)",
    options=[1, 2, 4, 12, 52, 365],
    index=3,  # selecciona "12" (mensual) por defecto
    format_func=lambda n: {1: "Anual", 2: "Semestral", 4: "Trimestral",
                            12: "Mensual", 52: "Semanal", 365: "Diaria"}[n],
)
# Meta financiera M: campo numerico entero.
meta = st.sidebar.number_input(
    "Meta financiera (colones)", min_value=10_000, max_value=1_000_000_000,
    value=1_000_000, step=50_000, format="%d",
)
# Horizonte T: cuantos años se grafican/calculan hacia adelante.
horizonte = st.sidebar.slider(
    "Horizonte a graficar (años)", min_value=1, max_value=40, value=25,
    help="Dominio razonable para un horizonte de ahorro personal: 0 a 30 años.",
)

# Diccionario "espejo" del PARAMETROS de main.py, armado con los
# valores actuales de los controles de la barra lateral. No se usa
# mas abajo en esta version de la app (cada pestaña vuelve a leer
# las variables sueltas capital_inicial/tasa_anual/etc.), pero se
# deja disponible por si se necesita pasar todo el conjunto de
# parametros de una sola vez a alguna funcion futura.
parametros = {
    "capital_inicial": capital_inicial,
    "tasa_anual": tasa_anual,
    "frecuencia": frecuencia,
    "meta": meta,
    "horizonte": horizonte,
}

# Escenarios anclados a productos reales de ahorro en Costa Rica
# (El Financiero, 2026), independientes del slider de tasa_anual:
# representan alternativas reales, no simplemente +/- unos puntos
# alrededor del valor elegido por el usuario.
escenarios_tasa = {
    "Tasa baja (ahorro regular)": 0.01,
    "Tasa media (ahorro premium)": 0.0295,
    "Tasa alta (CDP a 12 meses)": 0.04,
}

# ==============================================================
# ENCABEZADO
# ==============================================================

st.title("💰 Simulador de Ahorro")
st.caption(
    "MA-0321 Calculo Diferencial e Integral · Universidad de Costa Rica · "
    "Proyecto 5 — comparacion de alternativas de ahorro"
)

# Cuatro tarjetas resumen (capital, tasa, meta, horizonte) en
# cuatro columnas del mismo ancho, usando la clase CSS
# ".bloque-metrica" definida arriba y la funcion moneda() para
# formatear los montos en colones.
col_a, col_b, col_c, col_d = st.columns(4)
col_a.markdown(f'<div class="bloque-metrica"><b>Capital inicial</b><br>'
                f'<span style="font-size:1.4rem">{moneda(capital_inicial)}</span></div>',
                unsafe_allow_html=True)
col_b.markdown(f'<div class="bloque-metrica"><b>Tasa anual</b><br>'
                f'<span style="font-size:1.4rem">{tasa_anual:.1%}</span></div>',
                unsafe_allow_html=True)
col_c.markdown(f'<div class="bloque-metrica"><b>Meta</b><br>'
                f'<span style="font-size:1.4rem">{moneda(meta)}</span></div>',
                unsafe_allow_html=True)
col_d.markdown(f'<div class="bloque-metrica"><b>Horizonte</b><br>'
                f'<span style="font-size:1.4rem">{horizonte} años</span></div>',
                unsafe_allow_html=True)

st.write("")  # espacio en blanco antes de las pestañas

# ==============================================================
# PESTANIAS
# ==============================================================
# Las cuatro pestañas son el equivalente, en la interfaz grafica,
# de las secciones que main.py imprime en consola en orden fijo:
# tabla comparativa, graficas, escenarios de tasa y validacion.
# Aqui el usuario puede saltar libremente entre ellas.

tab_resumen, tab_graficas, tab_escenarios, tab_validacion = st.tabs(
    ["📊 Tabla comparativa", "📈 Graficas", "🎯 Escenarios de tasa", "✅ Validacion"]
)

# --------------------------------------------------------------
# TAB 1 - Tabla comparativa + recomendacion
# --------------------------------------------------------------
# Version en Streamlit de construir_tabla() en main.py: arma una
# fila por metodo llamando siempre a las funciones de
# modelo_ahorro.py, y la muestra con formato de moneda.
with tab_resumen:
    # Se vuelven a leer los valores actuales de la barra lateral en
    # variables de una letra, para que coincidan con la notacion
    # matematica (P, r, n, M, T) usada en el resto del proyecto.
    P, r, n, M, T = capital_inicial, tasa_anual, frecuencia, meta, horizonte

    filas = []
    # Se recorren las 3 alternativas como tuplas
    # (clave interna, nombre para mostrar, monto ya calculado).
    # La clave interna ("simple"/"compuesto"/"continua") es la que
    # espera mod.tiempo_para_meta como parametro "metodo".
    for metodo_clave, metodo_nombre, monto in [
        ("simple", "Interes simple", mod.interes_simple(P, r, T)),
        ("compuesto", "Interes compuesto", mod.interes_compuesto(P, r, T, n)),
        ("continua", "Capitalizacion continua", mod.capitalizacion_continua(P, r, T)),
    ]:
        filas.append({
            "Metodo": metodo_nombre,
            "Monto final": monto,
            "Ganancia": mod.ganancia(monto, P),
            "Años para la meta": mod.tiempo_para_meta(P, r, M, metodo_clave, n),
        })
    tabla = pd.DataFrame(filas)

    st.subheader("Comparacion de las tres alternativas")
    # st.dataframe muestra la tabla en pantalla; .style.format
    # define, columna por columna, como se formatea cada valor
    # numerico (moneda para montos, 2 decimales para los años).
    st.dataframe(
        tabla.style.format({
            "Monto final": lambda x: moneda(x),
            "Ganancia": lambda x: moneda(x),
            "Años para la meta": "{:.2f}",
        }),
        use_container_width=True, hide_index=True,
    )

    # Boton de descarga: convierte la tabla a texto CSV
    # (tabla.to_csv), lo codifica a bytes (.encode("utf-8")) porque
    # Streamlit espera bytes para el contenido descargable, y le
    # asigna un nombre de archivo y tipo MIME.
    st.download_button(
        "⬇️ Descargar tabla (CSV)",
        tabla.to_csv(index=False).encode("utf-8"),
        file_name="tabla_comparativa.csv", mime="text/csv",
    )

# --------------------------------------------------------------
# TAB 2 - Graficas interactivas
# --------------------------------------------------------------
# Version interactiva (Plotly) de grafica_crecimiento() y
# grafica_efecto_tasa() de main.py. En vez de guardar un PNG con
# matplotlib, se arma una figura de Plotly que el usuario puede
# recorrer con el mouse y leer valores exactos en un tooltip,
# directamente en el navegador.
with tab_graficas:
    P, r, n, M, T = capital_inicial, tasa_anual, frecuencia, meta, horizonte
    # Malla de 400 puntos entre 0 y T años, igual que en main.py.
    t = np.linspace(0, T, 400)

    st.subheader("Grafica 1 — Crecimiento del capital")
    # Version vectorizada de las tres formulas de A(t) (las mismas
    # que interes_simple / interes_compuesto / capitalizacion_
    # continua en modelo_ahorro.py), evaluadas para toda la malla
    # de tiempos "t" de una sola vez con numpy.
    a_simple = P * (1 + r * t)
    a_compuesto = P * (1 + r / n) ** (n * t)
    a_continua = P * np.exp(r * t)

    # Se arma una figura vacia de Plotly y se le agregan tres
    # "trazos" (Scatter), uno por curva, cada uno con su color fijo
    # tomado de PALETA y su propio nombre para la leyenda.
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=t, y=a_simple, name="Interes simple",
                               line=dict(color=PALETA["Interes simple"], width=3)))
    fig1.add_trace(go.Scatter(x=t, y=a_compuesto, name=f"Interes compuesto (n={n})",
                               line=dict(color=PALETA["Interes compuesto"], width=3)))
    fig1.add_trace(go.Scatter(x=t, y=a_continua, name="Capitalizacion continua",
                               line=dict(color=PALETA["Capitalizacion continua"],
                                         width=3, dash="dash")))  # linea punteada
    # Linea horizontal punteada en A = M, con una anotacion de
    # texto fija en la esquina superior izquierda del punto donde
    # cruza el eje Y.
    fig1.add_hline(y=M, line_dash="dot", line_color="crimson",
                   annotation_text=f"Meta = {moneda(M)}", annotation_position="top left")
    # Configuracion general del layout: titulos de ejes, leyenda
    # horizontal debajo del grafico, alto fijo en pixeles y margen
    # superior reducido.
    fig1.update_layout(
        xaxis_title="Tiempo t (años)", yaxis_title=f"Monto acumulado A(t) ({MONEDA})",
        legend=dict(orientation="h", y=-0.2), height=450,
        margin=dict(t=20),
    )
    # Renderiza la figura de Plotly dentro de la app de Streamlit,
    # usando todo el ancho disponible del contenedor.
    st.plotly_chart(fig1, use_container_width=True)
    st.caption(
        "Interpretacion: el interes simple crece en linea recta porque los "
        "intereses no generan nuevos intereses. Las otras dos curvas son "
        "exponenciales y casi se superponen, porque la capitalizacion continua "
        "es el limite del interes compuesto cuando n tiende a infinito."
    )

    st.subheader("Grafica 2 — Efecto de la tasa de interes")
    # Una curva de interes compuesto por cada escenario de tasa
    # (baja/media/alta), manteniendo P y n fijos (los de la barra
    # lateral): asi se aisla el efecto de cambiar solo r.
    fig2 = go.Figure()
    for nombre, r_esc in escenarios_tasa.items():
        a_esc = P * (1 + r_esc / n) ** (n * t)
        fig2.add_trace(go.Scatter(x=t, y=a_esc, name=f"{nombre} (r={r_esc:.1%})",
                                   line=dict(color=PALETA[nombre], width=3)))
    fig2.add_hline(y=M, line_dash="dot", line_color="crimson",
                   annotation_text=f"Meta = {moneda(M)}", annotation_position="top left")
    fig2.update_layout(
        xaxis_title="Tiempo t (años)", yaxis_title=f"Monto acumulado A(t) ({MONEDA})",
        legend=dict(orientation="h", y=-0.2), height=450,
        margin=dict(t=20),
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
        "Interpretacion: con el mismo capital inicial, una tasa mayor no solo "
        "produce un monto final mas alto, sino que acelera cuanto antes se "
        "alcanza la meta. La brecha entre curvas crece con el tiempo, lo cual "
        "es consistente con que la derivada del monto es proporcional al monto "
        "mismo en capitalizacion continua."
    )

# --------------------------------------------------------------
# TAB 3 - Escenarios de tasa (tabla + capital necesario)
# --------------------------------------------------------------
# Version en Streamlit de construir_tabla_escenarios() en
# main.py: siempre con interes compuesto, calcula para cada
# escenario el monto proyectado, el tiempo para la meta y el
# capital necesario hoy (valor presente) para llegar a esa misma
# meta en el mismo plazo.
with tab_escenarios:
    # Aqui no se usa la tasa "r" de la barra lateral: cada
    # escenario trae su propia tasa (r_esc), por eso solo se
    # desempaquetan P, n, M y T.
    P, n, M, T = capital_inicial, frecuencia, meta, horizonte
    filas = []
    for nombre, r_esc in escenarios_tasa.items():
        monto = mod.interes_compuesto(P, r_esc, T, n)
        filas.append({
            "Escenario": nombre,
            "Tasa anual": r_esc,
            f"Monto a {T} años": monto,
            "Años para la meta": mod.tiempo_para_meta(P, r_esc, M, "compuesto", n),
            # Valor presente: capital que habria que depositar hoy
            # para llegar a la meta en el mismo plazo T, a esta tasa.
            "Capital necesario hoy": mod.capital_para_meta(M, r_esc, T, "compuesto", n),
        })
    tabla_esc = pd.DataFrame(filas)

    st.subheader("Comparacion de escenarios de tasa")
    st.dataframe(
        tabla_esc.style.format({
            "Tasa anual": "{:.1%}",
            f"Monto a {T} años": lambda x: moneda(x),
            "Años para la meta": "{:.2f}",
            "Capital necesario hoy": lambda x: moneda(x),
        }),
        use_container_width=True, hide_index=True,
    )
    st.caption(
        "La columna 'Capital necesario hoy' responde la segunda mitad de la "
        "pregunta de decision del proyecto: con que aporte inicial se llega a "
        "la meta en el mismo plazo, segun la tasa disponible."
    )

    st.download_button(
        "⬇️ Descargar escenarios (CSV)",
        tabla_esc.to_csv(index=False).encode("utf-8"),
        file_name="tabla_escenarios.csv", mime="text/csv",
    )

# --------------------------------------------------------------
# TAB 4 - Validacion matematica
# --------------------------------------------------------------
# Version en Streamlit de validar() en main.py: las mismas tres
# comprobaciones (derivada analitica vs. numerica, limite del
# interes compuesto cuando n -> infinito, y coherencia del despeje
# de t), pero mostradas como metricas (st.metric) y tablas en vez
# de texto plano de consola.
with tab_validacion:
    P, r, n, M, T = capital_inicial, tasa_anual, frecuencia, meta, horizonte

    st.subheader("1. Derivada analitica vs. derivada numerica")
    # Derivada "analitica": formula cerrada A'(t) = P r e^(rt)
    # (mod.derivada_continua). Derivada "numerica": aproximacion
    # por diferencia centrada [A(t+h) - A(t-h)] / (2h), con h muy
    # pequeño. Si el modelo esta bien derivado, deben coincidir.
    h = 1e-6
    # min(10, T) evita evaluar en un t0 mayor al horizonte elegido
    # por el usuario; si T=0 (caso limite), se usa t0=1 en su lugar.
    t0 = min(10, T) if T > 0 else 1
    analitica = mod.derivada_continua(P, r, t0)
    numerica = (mod.capitalizacion_continua(P, r, t0 + h)
                - mod.capitalizacion_continua(P, r, t0 - h)) / (2 * h)
    # Tres columnas con una metrica cada una: valor analitico,
    # valor numerico y la diferencia absoluta entre ambos.
    c1, c2, c3 = st.columns(3)
    c1.metric("Derivada analitica A'(t)", moneda(analitica))
    c2.metric("Derivada numerica", moneda(numerica))
    c3.metric("Diferencia", f"{abs(analitica - numerica):.6f}")

    st.subheader("2. Limite del interes compuesto cuando n → ∞")

    # Se evalua interes_compuesto con valores de n cada vez mas
    # grandes y se muestra como el resultado se acerca al valor
    # teorico de capitalizacion continua P*e^(rt).

    continua = mod.capitalizacion_continua(P, r, T)
    valores_n = [1, 12, 365, 10_000, 1_000_000]

    # Se arma una tabla de 2 columnas: n y el monto correspondiente
    # (una comprension de lista evalua interes_compuesto para cada
    # valor de n en valores_n, sin necesidad de un for explicito).

    tabla_limite = pd.DataFrame({
        "n": valores_n,
        "A con interes compuesto": [mod.interes_compuesto(P, r, T, ni) for ni in valores_n],
    })
    st.dataframe(
        tabla_limite.style.format({"A con interes compuesto": lambda x: moneda(x)}),
        use_container_width=True, hide_index=True,
    )
    st.info(f"Valor teorico de capitalizacion continua P·e^(rt) = **{moneda(continua)}**. "
            f"La sucesion se acerca a ese valor a medida que n crece: el limite queda confirmado.")

    st.subheader("3. Coherencia del despeje de t (tiempo para la meta)")

    # Se toma el t que devuelve tiempo_para_meta() y se vuelve a
    # evaluar interes_compuesto en ese t: si el despeje algebraico
    # es correcto, el monto resultante debe coincidir con la meta M.

    t_meta = mod.tiempo_para_meta(P, r, M, "compuesto", n)
    monto_en_t_meta = mod.interes_compuesto(P, r, t_meta, n)
    c1, c2, c3 = st.columns(3)

    # Si t_meta es infinito (r=0 y meta > capital), se muestra "∞"
    # y un guion en vez de intentar formatear infinito como moneda.
    
    c1.metric("t calculado (años)", f"{t_meta:.4f}" if t_meta != float("inf") else "∞")
    c2.metric("A(t) evaluado en ese t", moneda(monto_en_t_meta) if t_meta != float("inf") else "—")
    c3.metric("Meta solicitada", moneda(M))