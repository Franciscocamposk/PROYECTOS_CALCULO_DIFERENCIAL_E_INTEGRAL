"""
main.py
---------------------------------------------------------------
Proyecto 5 - Simulador de Ahorro
MA-0321 Calculo Diferencial e Integral - UCR - II Ciclo 2026

Este archivo ejecuta el simulador:
  - arma la tabla comparativa
  - compara escenarios de tasa
  - genera las dos graficas obligatorias
  - emite la recomendacion automatica
  - valida resultados analiticos contra Python

Toda la matematica (formulas, derivadas, despejes) vive en
modelo_ahorro.py. Este archivo solo la ORQUESTA: arma tablas,
dibuja graficas y arma los mensajes de texto.

Para ejecutar desde VS Code:
    python main.py
---------------------------------------------------------------
"""

import math                     # no se usa directamente aqui, pero
                                 # queda disponible si se necesita en
                                 # pruebas rapidas (inf, isnan, etc.)
import numpy as np              # malla de tiempos para las graficas
import pandas as pd             # tablas (DataFrame) y exportar a CSV
import matplotlib
matplotlib.use("Agg")           # backend sin interfaz grafica: permite
                                 # guardar PNG en un servidor/consola
                                 # que no tiene pantalla
import matplotlib.pyplot as plt # dibujar y guardar las graficas

import modelo_ahorro as mod     # todas las formulas viven aqui

# ==============================================================
# PARAMETROS MODIFICABLES
# ==============================================================
# Estos valores ya NO son supuestos arbitrarios: estan anclados a
# datos reales del mercado de ahorro costarricense, consultados
# en El Financiero Costa Rica durante 2026 (fuentes completas en
# las referencias APA del informe):
#
#   - Cuenta de ahorro regular en colones: intereses entre 0% y
#     1.75% anual (El Financiero, 12 marzo 2026).
#   - Cuenta de ahorro premium en colones: hasta 2.95% anual,
#     requiere saldo minimo de 500,000 colones para generar
#     intereses (El Financiero, 25 junio 2026).
#   - Certificado de Deposito a Plazo (CDP): Tasa Pasiva Negociada
#     promedio de 4.02% en agosto 2026 (El Financiero, agosto 2026).
#
# El capital inicial de 500,000 colones NO es arbitrario: coincide
# con el saldo minimo real que exige una cuenta premium para
# generar intereses en Costa Rica. La tasa base (2.95%) corresponde
# a ese mismo producto.
#
# Se pueden cambiar sin tocar el resto del programa: todas las
# funciones de abajo leen sus valores de este diccionario.

PARAMETROS = {
    "capital_inicial": 500_000,   # colones (saldo minimo real de cuenta premium)
    "tasa_anual": 0.0295,         # 2.95% anual - cuenta de ahorro premium
    "frecuencia": 12,             # capitalizaciones por año (mensual)
    "meta": 1_000_000,            # colones
    "horizonte": 25,              # años a graficar (dominio razonable: 0-30)
}

# Escenarios de tasa: cada uno representa un producto real de ahorro
# en Costa Rica, no niveles arbitrarios de "bajo/medio/alto". Se usa
# en la tabla de escenarios y en la segunda grafica.
ESCENARIOS_TASA = {
    "Tasa baja (ahorro regular)": 0.01,     # dentro del rango 0%-1.75%
    "Tasa media (ahorro premium)": 0.0295,  # tasa maxima documentada
    "Tasa alta (CDP a 12 meses)": 0.04,     # cercano al TPN de 4.02%
}

MONEDA = "colones"  # etiqueta de unidad usada en todos los mensajes impresos


# ==============================================================
# 1. TABLA COMPARATIVA DE LAS TRES ALTERNATIVAS
# ==============================================================

def construir_tabla(parametros):
    """
    Arma un DataFrame con una fila por alternativa (simple,
    compuesto, continua): capital, tasa, frecuencia, plazo, monto
    final, ganancia, años para la meta y velocidad final A'(t).

    Reutiliza directamente las funciones de modelo_ahorro.py; no
    calcula nada por su cuenta, solo organiza los resultados.
    """
    # Se desempaquetan los 5 parametros del diccionario en
    # variables sueltas de una sola letra (P, r, n, M, T), para que
    # las formulas de abajo se vean igual que en la notacion
    # matematica del enunciado.
    P = parametros["capital_inicial"]
    r = parametros["tasa_anual"]
    n = parametros["frecuencia"]
    M = parametros["meta"]
    t = parametros["horizonte"]

    filas = []  # aqui se va acumulando un dict por cada alternativa

    # --- Interes simple ---
    # Se calcula el monto final una sola vez y se reutiliza tanto
    # para "Monto final" como para calcular la ganancia.
    monto = mod.interes_simple(P, r, t)
    filas.append({
        "Metodo": "Interes simple",
        "Capital inicial": P,
        "Tasa anual": r,
        "Frecuencia (n)": "No aplica",       # el interes simple no capitaliza por periodos
        "Plazo (años)": t,
        "Monto final": monto,
        "Ganancia": mod.ganancia(monto, P),  # monto - capital inicial
        "Años para la meta": mod.tiempo_para_meta(P, r, M, "simple"),
        "Velocidad final A'(t)": mod.derivada_simple(P, r),  # constante, no depende de t
    })

    # --- Interes compuesto ---
    monto = mod.interes_compuesto(P, r, t, n)
    filas.append({
        "Metodo": "Interes compuesto",
        "Capital inicial": P,
        "Tasa anual": r,
        "Frecuencia (n)": n,                 # aqui si importa cuantas veces se capitaliza
        "Plazo (años)": t,
        "Monto final": monto,
        "Ganancia": mod.ganancia(monto, P),
        "Años para la meta": mod.tiempo_para_meta(P, r, M, "compuesto", n),
        "Velocidad final A'(t)": mod.derivada_compuesta(P, r, t, n),  # evaluada en t=horizonte
    })

    # --- Capitalizacion continua ---
    monto = mod.capitalizacion_continua(P, r, t)
    filas.append({
        "Metodo": "Capitalizacion continua",
        "Capital inicial": P,
        "Tasa anual": r,
        "Frecuencia (n)": "Infinita",        # limite de n -> infinito
        "Plazo (años)": t,
        "Monto final": monto,
        "Ganancia": mod.ganancia(monto, P),
        "Años para la meta": mod.tiempo_para_meta(P, r, M, "continua"),
        "Velocidad final A'(t)": mod.derivada_continua(P, r, t),
    })

    # Se convierte la lista de 3 diccionarios en un DataFrame de
    # pandas: cada dict se vuelve una fila, cada llave una columna.
    return pd.DataFrame(filas)


# ==============================================================
# 2. TABLA DE ESCENARIOS DE TASA
# ==============================================================

def construir_tabla_escenarios(parametros, escenarios):
    """
    Para cada escenario de tasa calcula, siempre con interes
    compuesto: el monto al final del horizonte, los años para la
    meta y el capital necesario hoy (valor presente) para llegar a
    esa meta en el mismo plazo.
    """
    # De "parametros" solo interesan P, n, M y T; la tasa r viene
    # de cada escenario del diccionario "escenarios", no de aqui.
    P = parametros["capital_inicial"]
    n = parametros["frecuencia"]
    M = parametros["meta"]
    t = parametros["horizonte"]

    filas = []
    # Se recorre cada par (nombre_del_escenario, tasa_del_escenario).
    for nombre, r in escenarios.items():
        monto = mod.interes_compuesto(P, r, t, n)
        filas.append({
            "Escenario": nombre,
            "Tasa anual": r,
            f"Monto a {t} años": monto,
            "Años para la meta": mod.tiempo_para_meta(P, r, M, "compuesto", n),
            # Valor presente: cuanto habria que depositar hoy para
            # llegar a M en el mismo plazo t, a esta tasa r.
            "Capital necesario hoy": mod.capital_para_meta(M, r, t, "compuesto", n),
        })
    return pd.DataFrame(filas)


# ==============================================================
# 3. GRAFICA 1 - Crecimiento del capital (tres alternativas)
# ==============================================================

def grafica_crecimiento(parametros, archivo="grafica1_crecimiento.png"):
    """
    Dibuja las tres curvas A(t) (simple, compuesto, continua)
    sobre el mismo eje, marca la meta con una linea horizontal y
    anota en que instante cruza cada curva esa meta. Guarda el
    resultado como PNG y devuelve la ruta del archivo.
    """
    P = parametros["capital_inicial"]
    r = parametros["tasa_anual"]
    n = parametros["frecuencia"]
    M = parametros["meta"]
    T = parametros["horizonte"]

    # Malla de 400 puntos entre 0 y T años: suficientemente fina
    # para que las curvas se vean suaves al graficarlas.
    t = np.linspace(0, T, 400)

    # Se evaluan las tres formulas de forma VECTORIZADA (numpy
    # aplica la formula a los 400 valores de t de una sola vez, en
    # vez de llamar 400 veces a las funciones de modelo_ahorro.py).
    # Son las mismas formulas que interes_simple / interes_compuesto
    # / capitalizacion_continua, escritas con operadores de numpy.
    a_simple = P * (1 + r * t)
    a_compuesto = P * (1 + r / n) ** (n * t)
    a_continua = P * np.exp(r * t)

    # Tamaño de la figura en pulgadas (ancho x alto).
    plt.figure(figsize=(9, 5.5))
    # Se dibuja cada curva con su propia etiqueta (para la leyenda).
    plt.plot(t, a_simple, label="Interes simple", linewidth=2)
    plt.plot(t, a_compuesto, label=f"Interes compuesto (n={n})", linewidth=2)
    # linestyle="--" dibuja la curva continua punteada, para
    # distinguirla visualmente aunque casi se superponga con la
    # de interes compuesto.
    plt.plot(t, a_continua, label="Capitalizacion continua", linewidth=2, linestyle="--")

    # Linea horizontal roja punteada en A = M, con su propia
    # etiqueta de leyenda mostrando el valor de la meta.
    plt.axhline(M, color="red", linestyle=":", linewidth=1.8,
                label=f"Meta = {M:,.0f} {MONEDA}")

    # "desplazamientos" controla que tanto se separa verticalmente
    # cada anotacion de texto respecto a la linea de la meta, para
    # que las tres etiquetas (simple/compuesto/continua) no queden
    # unas encima de otras.
    desplazamientos = {"simple": 0.16, "compuesto": 0.10, "continua": 0.04}
    for metodo, etiqueta in [("simple", "Simple"),
                             ("compuesto", "Compuesto"),
                             ("continua", "Continua")]:
        # Se reutiliza el mismo despeje analitico de tiempo_para_meta
        # que usan las tablas, para que el punto marcado en la
        # grafica sea exacto (no una lectura visual aproximada).
        t_meta = mod.tiempo_para_meta(P, r, M, metodo, n)
        # Solo se marca el cruce si ocurre dentro del horizonte
        # graficado; si t_meta > T, la curva ni siquiera llega a
        # cruzar la meta dentro de la ventana visible.
        if t_meta <= T:
            # Punto negro en el cruce (t_meta, M).
            plt.plot(t_meta, M, "o", color="black", markersize=6)
            # Texto con flecha apuntando al punto, desplazado segun
            # "desplazamientos" para evitar solapamientos.
            plt.annotate(
                f"{etiqueta}: {t_meta:.2f} años",
                xy=(t_meta, M),
                xytext=(t_meta - T * 0.22, M * (1 + desplazamientos[metodo])),
                fontsize=9,
                arrowprops=dict(arrowstyle="->", lw=0.9, color="gray"),
            )

    # Titulo con los parametros usados, para que la grafica sea
    # auto-explicativa aunque se vea fuera de contexto.
    plt.title(f"Crecimiento del capital segun la modalidad de capitalizacion\n"
              f"P = {P:,.0f} {MONEDA}, r = {r:.1%} anual")

    # Margen superior dinamico: se toma el limite actual del eje Y
    # y se compara contra M*1.22 (un 22% por encima de la meta),
    # usando el que sea mayor.
    _, top_actual = plt.ylim()
    plt.ylim(top=max(top_actual, M * 1.22))
    plt.xlabel("Tiempo t (años)")
    plt.ylabel(f"Monto acumulado A(t) ({MONEDA})")
    plt.grid(True, linestyle="--", alpha=0.5)  # cuadricula tenue de fondo
    plt.legend()
    plt.tight_layout()          # ajusta margenes para que no se corte nada
    plt.savefig(archivo, dpi=150)  # guarda el PNG con buena resolucion
    plt.close()                 # libera la figura de memoria
    return archivo


# ==============================================================
# 4. GRAFICA 2 - Efecto de modificar la tasa de interes
# ==============================================================

def grafica_efecto_tasa(parametros, escenarios,
                        archivo="grafica2_efecto_tasa.png"):
    """
    Dibuja, con interes compuesto y el mismo capital inicial P,
    una curva A(t) por cada escenario de tasa (baja/media/alta),
    para ver como cambia el monto acumulado solo por variar r.
    Guarda el resultado como PNG y devuelve la ruta del archivo.
    """
    P = parametros["capital_inicial"]
    n = parametros["frecuencia"]
    M = parametros["meta"]
    T = parametros["horizonte"]

    # Misma malla de tiempos que en la grafica 1.
    t = np.linspace(0, T, 400)

    plt.figure(figsize=(9, 5.5))
    # Una curva por escenario: se recalcula el interes compuesto
    # con la tasa r de cada escenario, manteniendo P y n fijos, de
    # modo que la unica variable que cambia entre curvas es r.
    for nombre, r in escenarios.items():
        a = P * (1 + r / n) ** (n * t)
        plt.plot(t, a, linewidth=2, label=f"{nombre} (r = {r:.1%})")

    # Misma linea de meta que en la grafica 1.
    plt.axhline(M, color="red", linestyle=":", linewidth=1.8,
                label=f"Meta = {M:,.0f} {MONEDA}")

    plt.title(f"Efecto de la tasa de interes sobre el capital acumulado\n"
              f"Interes compuesto, P = {P:,.0f} {MONEDA}, n = {n}")
    plt.xlabel("Tiempo t (años)")
    plt.ylabel(f"Monto acumulado A(t) ({MONEDA})")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(archivo, dpi=150)
    plt.close()
    return archivo


# ==============================================================
# 5. RECOMENDACION AUTOMATICA
# ==============================================================

def recomendar(parametros):
    """
    Arma el texto de recomendacion final comparando las tres
    alternativas con los parametros actuales.

    LOGICA (para poder explicarla en la defensa):
    Paso 1. Tiempo para la meta de cada alternativa.
    Paso 2. Se descartan las que no llegan dentro del horizonte.
    Paso 3. Entre las viables, se elige la de MENOR tiempo.
    Paso 4. Se cuantifica cuanto se gana frente a la peor.
    Paso 5. Se calcula la sensibilidad a la tasa (diferencial).
    """
    P = parametros["capital_inicial"]
    r = parametros["tasa_anual"]
    n = parametros["frecuencia"]
    M = parametros["meta"]
    T = parametros["horizonte"]

    # --- Paso 1 ---
    # Se calcula, para cada una de las tres alternativas, el
    # tiempo que tardaria en llegar a la meta y el monto que
    # tendria acumulado al final del horizonte T.
    opciones = {
        "Interes simple": {
            "tiempo": mod.tiempo_para_meta(P, r, M, "simple"),
            "monto": mod.interes_simple(P, r, T),
        },
        "Interes compuesto": {
            "tiempo": mod.tiempo_para_meta(P, r, M, "compuesto", n),
            "monto": mod.interes_compuesto(P, r, T, n),
        },
        "Capitalizacion continua": {
            "tiempo": mod.tiempo_para_meta(P, r, M, "continua"),
            "monto": mod.capitalizacion_continua(P, r, T),
        },
    }

    # --- Paso 2 ---
    # Se filtran solo las alternativas cuyo tiempo para la meta
    # cabe dentro del horizonte T (las demas no son "viables" en
    # el plazo que el usuario esta dispuesto a esperar).
    viables = {k: v for k, v in opciones.items() if v["tiempo"] <= T}

    if not viables:
        # Ninguna alternativa llega a tiempo: en vez de solo decir
        # "no se puede", se busca cual de las tres es la MENOS mala
        # (la de menor tiempo, aunque se pase del horizonte) y se
        # calcula cuanto le falta para llegar a la meta en T años.
        mejor = min(opciones, key=lambda k: opciones[k]["tiempo"])
        faltante = M - opciones[mejor]["monto"]
        mensaje = (
            f"Ninguna alternativa alcanza la meta de {M:,.0f} {MONEDA} "
            f"dentro de {T} años con un capital de {P:,.0f} {MONEDA} "
            f"y una tasa de {r:.1%}.\n"
            f"La mas cercana es {mejor}, que necesitaria "
            f"{opciones[mejor]['tiempo']:.1f} años y al cabo de {T} años "
            f"acumularia {opciones[mejor]['monto']:,.0f} {MONEDA}, "
            f"es decir {faltante:,.0f} {MONEDA} por debajo de la meta.\n"
            f"Se recomienda aumentar el capital inicial o negociar una tasa mayor."
        )
        # Se corta aqui (return): no tiene sentido calcular
        # "mejor vs. peor" ni sensibilidad si nada es viable.
        return {"decision": mejor, "viable": False, "mensaje": mensaje,
                "opciones": opciones}

    # --- Paso 3 ---
    # De las alternativas viables, "mejor" es la de menor tiempo
    # para la meta y "peor" la de mayor tiempo (la mas lenta, pero
    # que igual llega dentro del horizonte).
    mejor = min(viables, key=lambda k: viables[k]["tiempo"])
    peor = max(viables, key=lambda k: viables[k]["tiempo"])

    # --- Paso 4 ---
    # Diferencia en tiempo (años que se ahorra eligiendo "mejor" en
    # vez de "peor") y diferencia en monto acumulado a los T años.
    dif_tiempo = viables[peor]["tiempo"] - viables[mejor]["tiempo"]
    dif_monto = viables[mejor]["monto"] - viables[peor]["monto"]

    # --- Paso 5 ---
    # Se le pregunta al modelo: si la tasa subiera medio punto
    # porcentual (delta_r=0.005), cuanto cambiaria el monto final,
    # tanto por la aproximacion del diferencial como por el calculo
    # exacto (para poder comparar ambos en el mensaje).
    sens = mod.efecto_cambio_tasa(P, r, T, n, delta_r=0.005)

    # Se arma el mensaje final interpolando todos los numeros ya
    # calculados arriba (nada de esto es texto fijo/generico).
    mensaje = (
        f"RECOMENDACION\n"
        f"Con un capital inicial de {P:,.0f} {MONEDA} y una tasa anual de "
        f"{r:.1%}, la alternativa recomendada es: {mejor}.\n\n"
        f"- Alcanza la meta de {M:,.0f} {MONEDA} en "
        f"{viables[mejor]['tiempo']:.2f} años "
        f"({viables[mejor]['tiempo'] * 12:.0f} meses).\n"
        f"- A los {T} años acumularia {viables[mejor]['monto']:,.0f} {MONEDA}.\n"
        f"- Frente a {peor}, llega a la meta {dif_tiempo:.2f} años antes "
        f"y acumula {dif_monto:,.0f} {MONEDA} mas en el mismo plazo.\n\n"
        f"Sensibilidad a la tasa: un aumento de medio punto porcentual "
        f"(de {r:.1%} a {r + 0.005:.1%}) incrementaria el monto final en "
        f"aproximadamente {sens['aproximado']:,.0f} {MONEDA} segun el "
        f"diferencial, contra {sens['exacto']:,.0f} {MONEDA} de cambio real.\n"
        f"Negociar la tasa tiene, por tanto, un efecto medible sobre el resultado."
    )

    return {"decision": mejor, "viable": True, "mensaje": mensaje,
            "opciones": opciones, "sensibilidad": sens}


# ==============================================================
# 6. VALIDACION: comprobar la matematica con Python
# ==============================================================

def validar(parametros):
    """
    Corre tres comprobaciones numericas de resultados analiticos y
    devuelve un texto (str) con los tres bloques, listo para
    imprimir en consola:
      1) derivada analitica vs. numerica,
      2) limite del interes compuesto cuando n -> infinito,
      3) coherencia del despeje de t (tiempo_para_meta).
    """
    P = parametros["capital_inicial"]
    r = parametros["tasa_anual"]
    n = parametros["frecuencia"]
    M = parametros["meta"]
    T = parametros["horizonte"]

    lineas = []  # cada bloque de texto se agrega aqui y al final se unen

    # --- Validacion 1: derivada analitica vs derivada numerica ---
    # Definicion de derivada (diferencia centrada):
    #   A'(t) ~= [A(t+h) - A(t-h)] / (2h)
    # con h muy pequeño (1e-6), evaluada en t0=10 (o el horizonte,
    # si fuera menor).
    h = 1e-6
    t0 = 10
    # "Analitica": formula cerrada de la derivada (modelo_ahorro.py).
    analitica = mod.derivada_continua(P, r, t0)
    # "Numerica": se evalua A(t) muy cerca de t0 por ambos lados y
    # se aplica la formula de diferencia centrada.
    numerica = (mod.capitalizacion_continua(P, r, t0 + h)
                - mod.capitalizacion_continua(P, r, t0 - h)) / (2 * h)
    lineas.append(
        f"1) Derivada de A(t)=Pe^(rt) en t={t0}:\n"
        f"   Analitica  A'(t) = P*r*e^(rt) = {analitica:,.4f}\n"
        f"   Numerica   (diferencia centrada) = {numerica:,.4f}\n"
        f"   Diferencia = {abs(analitica - numerica):.6f}  -> coinciden."
    )

    # --- Validacion 2: limite n -> infinito del interes compuesto ---
    # Teoricamente  lim P(1+r/n)^(nt) = P*e^(rt)  cuando n -> infinito.
    continua = mod.capitalizacion_continua(P, r, T)
    lineas.append("\n2) Limite del interes compuesto cuando n -> infinito:")
    # Se prueba con valores de n cada vez mas grandes para mostrar
    # que la sucesion se va acercando al valor teorico "continua".
    for n_prueba in [1, 12, 365, 10_000, 1_000_000]:
        valor = mod.interes_compuesto(P, r, T, n_prueba)
        lineas.append(f"   n = {n_prueba:>9,}  ->  A = {valor:,.2f}")
    lineas.append(f"   Valor teorico P*e^(rt)  =  {continua:,.2f}")
    lineas.append("   La sucesion se acerca al valor continuo. Limite confirmado.")

    # --- Validacion 3: el tiempo para la meta devuelve la meta ---
    # Se calcula t con el despeje algebraico (tiempo_para_meta) y
    # se vuelve a meter ese t en la formula original de A(t): si el
    # despeje es correcto, el resultado debe coincidir con M.
    t_meta = mod.tiempo_para_meta(P, r, M, "compuesto", n)
    monto_en_t_meta = mod.interes_compuesto(P, r, t_meta, n)
    lineas.append(
        f"\n3) Coherencia del despeje de t:\n"
        f"   t calculado = {t_meta:.6f} años\n"
        f"   A(t) evaluado en ese tiempo = {monto_en_t_meta:,.2f} {MONEDA}\n"
        f"   Meta solicitada = {M:,.2f} {MONEDA}\n"
        f"   Diferencia = {abs(monto_en_t_meta - M):.6f}  -> el despeje es correcto."
    )

    # Se unen los tres bloques con saltos de linea entre ellos.
    return "\n".join(lineas)


# ==============================================================
# PROGRAMA PRINCIPAL
# ==============================================================

def main():
    """
    Punto de entrada del script. Orquesta, en orden, todo lo que
    hace el programa: imprime parametros, arma y muestra las dos
    tablas, corre las validaciones, imprime la recomendacion,
    genera las graficas y guarda tablas/graficas en disco.
    """
    # Formato global de pandas: numeros con separador de miles y
    # 2 decimales (para que se vea igual de prolijo en toda tabla
    # que se imprima), y ancho de consola de 200 caracteres para
    # que las tablas no se corten al imprimirlas.
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
    pd.set_option("display.width", 200)

    print("=" * 70)
    print("SIMULADOR DE AHORRO - Proyecto 5 - MA-0321")
    print("=" * 70)
    print("\nFUENTE DE DATOS: tasas ancladas a productos reales de ahorro en")
    print("Costa Rica (El Financiero, 2026). Vease el encabezado de este")
    print("archivo para el detalle de cada fuente.\n")

    # Se listan los 5 parametros actuales (capital, tasa,
    # frecuencia, meta, horizonte) tal como estan en PARAMETROS.
    print("Parametros actuales:")
    for clave, valor in PARAMETROS.items():
        print(f"   {clave}: {valor}")

    # --- Tabla 1: comparacion de alternativas ---
    print("\n" + "-" * 70)
    print("TABLA 1 - Comparacion de las tres alternativas")
    print("-" * 70)
    tabla = construir_tabla(PARAMETROS)
    # to_string(index=False) imprime la tabla completa sin la
    # columna de indices numericos que agrega pandas por defecto.
    print(tabla.to_string(index=False))

    # --- Tabla 2: escenarios de tasa ---
    print("\n" + "-" * 70)
    print("TABLA 2 - Escenarios de tasa")
    print("-" * 70)
    tabla_esc = construir_tabla_escenarios(PARAMETROS, ESCENARIOS_TASA)
    print(tabla_esc.to_string(index=False))

    # --- Validacion matematica ---
    print("\n" + "-" * 70)
    print("VALIDACION MATEMATICA")
    print("-" * 70)
    print(validar(PARAMETROS))

    # --- Recomendacion ---
    print("\n" + "-" * 70)
    resultado = recomendar(PARAMETROS)
    print(resultado["mensaje"])

    # --- Graficas: se generan y se guardan como archivos PNG en
    # el directorio actual; grafica_crecimiento y grafica_efecto_tasa
    # devuelven el nombre del archivo que acaban de guardar. ---
    g1 = grafica_crecimiento(PARAMETROS)
    g2 = grafica_efecto_tasa(PARAMETROS, ESCENARIOS_TASA)
    print("\n" + "-" * 70)
    print(f"Graficas guardadas: {g1} y {g2}")

    # --- Tablas: se guardan como CSV para poder pegarlas en el
    # informe escrito sin tener que copiar la salida de consola. ---
    tabla.to_csv("tabla_comparativa.csv", index=False)
    tabla_esc.to_csv("tabla_escenarios.csv", index=False)
    print("Tablas guardadas: tabla_comparativa.csv y tabla_escenarios.csv")


# Este bloque solo se ejecuta cuando el archivo se corre
# directamente (python main.py), NO cuando se importa desde otro
# script (por ejemplo, si alguien hiciera "import main" no
# arrancaria main() automaticamente).
if __name__ == "__main__":
    main()