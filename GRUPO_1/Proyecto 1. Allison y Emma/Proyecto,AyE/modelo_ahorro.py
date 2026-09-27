"""
modelo_ahorro.py
---------------------------------------------------------------
Proyecto 5 - Simulador de Ahorro
MA-0321 Calculo Diferencial e Integral - UCR - II Ciclo 2026

Este modulo contiene UNICAMENTE el modelo matematico:
las funciones de monto, sus derivadas, la sensibilidad y los
despejes (tiempo para meta y capital necesario).

No imprime nada ni dibuja graficas. Eso se hace en main.py (modo
consola) o en app.py (interfaz grafica con Streamlit). Asi el
modelo se puede probar por separado, sin depender de la interfaz
que lo consuma.

Notacion usada en todo el archivo:
    P  = capital inicial (colones)
    r  = tasa de interes anual en forma decimal (0.06 = 6% anual)
    t  = tiempo en anios
    n  = cantidad de capitalizaciones por anio
    M  = meta financiera (colones)
    A  = monto acumulado (colones)
---------------------------------------------------------------
"""

import math  

# ==============================================================
# 1. VALIDACION DE PARAMETROS (funcion auxiliar)
# ==============================================================

def _validar(P, r, t=None, n=None):
    """
    Revisa que los parametros esten dentro del dominio valido
    del modelo. Si algo esta mal, detiene el programa con un
    mensaje claro en vez de devolver un numero sin sentido.

    Dominio del modelo:
        P > 0   (no se puede ahorrar un capital negativo o nulo)
        r >= 0  (no modelamos tasas negativas)
        t >= 0  (el tiempo se mide desde el momento del deposito)
        n >= 1  y entero (al menos una capitalizacion por anio)
    """
    # P siempre es obligatorio y debe ser estrictamente positivo:
    # un capital de 0 o negativo no tiene sentido financiero.
    if P <= 0:
        raise ValueError("El capital inicial P debe ser mayor que cero.")

    # r siempre es obligatorio; se permite r = 0 (tasa nula), pero
    # no tasas negativas, porque el modelo no las contempla.
    if r < 0:
        raise ValueError("La tasa r no puede ser negativa en este modelo.")

    # t es opcional: algunas funciones (como derivada_simple) no
    # lo necesitan. Solo se valida si de verdad se recibio un valor.
    if t is not None and t < 0:
        raise ValueError("El tiempo t no puede ser negativo.")

    # n tambien es opcional (solo aplica a interes compuesto).
    if n is not None:
        # Debe haber al menos una capitalizacion por año.
        if n < 1:
            raise ValueError("La frecuencia n debe ser al menos 1.")
        # n representa una CANTIDAD de periodos, asi que debe ser
        # un entero (int(n) == n compara el valor truncado contra
        # el original: si son iguales, no tenia parte decimal).
        if int(n) != n:
            raise ValueError("La frecuencia n debe ser un numero entero.")


# ==============================================================
# 2. FUNCIONES DE MONTO (los tres modelos que pide la guia)
# ==============================================================

def interes_simple(P, r, t):
    """
    Interes simple:  A(t) = P * (1 + r*t)
    Los intereses se calculan SIEMPRE sobre el capital inicial:
    no generan nuevos intereses, por eso el crecimiento es LINEAL.
    """
    # Se valida el dominio (P > 0, r >= 0, t >= 0) antes de calcular.
    _validar(P, r, t)
    # Formula cerrada del interes simple: crecimiento lineal en t.
    return P * (1 + r * t)


def interes_compuesto(P, r, t, n):
    """
    Interes compuesto:  A(t) = P * (1 + r/n)^(n*t)
    Cada periodo los intereses se suman al capital y a partir de
    ahi tambien generan intereses ("capitalizar"). Crecimiento
    EXPONENCIAL.
    """
    # Se valida P, r, t y ademas n (frecuencia de capitalizacion).
    _validar(P, r, t, n)
    # r / n          -> tasa efectiva de UN periodo de capitalizacion.
    # n * t          -> numero total de periodos capitalizados en t años.
    # (1+r/n)**(n*t) -> factor de crecimiento acumulado.
    return P * (1 + r / n) ** (n * t)


def capitalizacion_continua(P, r, t):
    """
    Capitalizacion continua:  A(t) = P * e^(r*t)
    Caso limite del interes compuesto cuando n -> infinito (los
    intereses se capitalizan a cada instante). Es la cota superior
    teorica del interes compuesto para un mismo P, r, t.
    """
    # No se pasa n: este modelo no tiene periodos discretos.
    _validar(P, r, t)
    # math.exp(r * t) calcula e^(r*t) con la libreria estandar.
    return P * math.exp(r * t)


# ==============================================================
# 3. DERIVADAS RESPECTO AL TIEMPO  (razon de crecimiento)
# ==============================================================
# A'(t) responde: "a que velocidad crece el dinero en el anio t".
# Unidades: colones por anio.

def derivada_simple(P, r, t=None):
    """
    A(t) = P(1 + r t)   =>   A'(t) = P * r
    Es CONSTANTE: no depende de t. El parametro t se acepta solo
    por simetria de firma con las otras dos derivadas; no se usa.
    """
    # No se le pasa t a _validar porque el resultado no depende de t.
    _validar(P, r)
    # Derivada de P(1 + r t) respecto a t: r*t se deriva a r, el 1
    # desaparece (derivada de constante), y queda P*r.
    return P * r


def derivada_compuesta(P, r, t, n):
    """
    A(t) = P (1 + r/n)^(n t)
    Derivada:  A'(t) = P * n * ln(1 + r/n) * (1 + r/n)^(n t)
    Crece con t: entre mas dinero acumulado, mas rapido crece.
    """
    _validar(P, r, t, n)
    # math.log(x) sin segundo argumento es logaritmo NATURAL (ln x).
    # Regla de derivacion de una exponencial de base variable:
    # d/dt[a^(kt)] = a^(kt) * k * ln(a), con a=(1+r/n) y k=n.
    return P * n * math.log(1 + r / n) * (1 + r / n) ** (n * t)


def derivada_continua(P, r, t):
    """
    A(t) = P e^(r t)   =>   A'(t) = P * r * e^(r t) = r * A(t)
    Resultado clave: la velocidad de crecimiento es proporcional
    al monto acumulado. Se usa como referencia "analitica" en la
    validacion de main.py, comparada contra una derivada numerica.
    """
    _validar(P, r, t)
    # e^(rt) se deriva a si misma por la derivada del exponente (r):
    # d/dt[e^(rt)] = r * e^(rt). Multiplicando por P: A'(t) = r*A(t).
    return P * r * math.exp(r * t)


# ==============================================================
# 4. SENSIBILIDAD RESPECTO A LA TASA  (diferenciales)
# ==============================================================
# Pregunta empresarial: si logro negociar 0.5 puntos mas de tasa,
# cuantos colones mas tengo al final?
#
# Idea del diferencial:   dA  ~=  (dA/dr) * dr

def sensibilidad_tasa_compuesto(P, r, t, n):
    """
    Derivada del monto respecto a la TASA (no al tiempo):
        A(r) = P (1 + r/n)^(n t)
        dA/dr = P * t * (1 + r/n)^(n t - 1)
    Unidades: colones por cada unidad de tasa (multiplicar por
    0.01 para el efecto de 1 punto porcentual).
    """
    _validar(P, r, t, n)
    # A se trata como funcion de r (con P, t, n fijos). Regla de la
    # potencia: d/dr[(1+r/n)^(nt)] = (nt)*(1+r/n)^(nt-1) * (1/n)
    #                               = t * (1+r/n)^(nt-1)
    # y se multiplica por P.
    return P * t * (1 + r / n) ** (n * t - 1)


def sensibilidad_tasa_continua(P, r, t):
    """
    A(r) = P e^(r t)   =>   dA/dr = P * t * e^(r t)
    Version continua de la sensibilidad a la tasa.
    """
    _validar(P, r, t)
    # d/dr[e^(rt)] = t * e^(rt) (t constante, r variable), * P.
    return P * t * math.exp(r * t)


def efecto_cambio_tasa(P, r, t, n, delta_r=0.005):
    """
    Compara el cambio aproximado (por diferencial) contra el
    cambio exacto (recalculando el modelo) que produce un
    aumento de delta_r en la tasa. delta_r=0.005 = medio punto
    porcentual.

    Devuelve un dict con delta_r, aproximado, exacto y error.
    """
    # Aproximacion por diferencial: dA ~= (dA/dr) * dr.
    aproximado = sensibilidad_tasa_compuesto(P, r, t, n) * delta_r

    # Cambio "exacto": se recalcula el monto con la tasa nueva
    # (r + delta_r) y se resta el monto con la tasa original r.
    # No usa ninguna aproximacion, es el valor real del modelo.
    exacto = interes_compuesto(P, r + delta_r, t, n) - interes_compuesto(P, r, t, n)

    # Se agrupa todo en un diccionario para que main.py lo use
    # directamente sin tener que recalcular nada.
    return {
        "delta_r": delta_r,
        "aproximado": aproximado,
        "exacto": exacto,
        "error": exacto - aproximado,
    }


# ==============================================================
# 5. TIEMPO PARA ALCANZAR LA META  (despeje de t)
# ==============================================================

def tiempo_para_meta(P, r, M, metodo="compuesto", n=12):
    """
    Calcula cuantos anios se necesitan para que el capital P
    llegue a la meta M, despejando t en cada modelo:

    SIMPLE:      M = P(1 + r t)              -> t = (M/P - 1) / r
    COMPUESTO:   M = P (1 + r/n)^(n t)        -> t = ln(M/P) / (n ln(1+r/n))
    CONTINUA:    M = P e^(r t)                -> t = ln(M/P) / r

    Casos especiales: M<=P devuelve 0; r=0 devuelve infinito.
    """
    # Se valida P, r y n (t es lo que se busca, no un dato de entrada).
    _validar(P, r, n=n)

    # La meta debe ser un valor positivo con sentido financiero.
    if M <= 0:
        raise ValueError("La meta M debe ser mayor que cero.")

    # Caso trivial: si la meta ya esta cubierta con el capital
    # inicial (o es menor), no hace falta esperar nada.
    if M <= P:
        return 0.0

    # Con tasa 0 el capital nunca crece: si M > P nunca se alcanza.
    if r == 0:
        return math.inf

    # "razon" = cuantas veces hay que multiplicar P para llegar a M
    # (M/P). Se calcula una vez porque aparece en los tres despejes.
    razon = M / P

    if metodo == "simple":
        # De M = P(1 + r t)  =>  M/P = 1 + r t  =>  t = (M/P - 1) / r
        return (razon - 1) / r
    elif metodo == "compuesto":
        # De M = P(1+r/n)^(nt), tomando ln: ln(M/P) = nt·ln(1+r/n)
        # => t = ln(M/P) / (n·ln(1+r/n))
        return math.log(razon) / (n * math.log(1 + r / n))
    elif metodo == "continua":
        # De M = P e^(rt), tomando ln: ln(M/P) = rt => t = ln(M/P)/r
        return math.log(razon) / r
    else:
        # metodo invalido: se detiene con mensaje claro.
        raise ValueError("metodo debe ser 'simple', 'compuesto' o 'continua'.")


# ==============================================================
# 6. CAPITAL NECESARIO  (despeje de P)
# ==============================================================
# La pregunta oficial del proyecto tiene dos mitades:
# "menor plazo O MENOR APORTE". Esta funcion contesta la segunda.

def capital_para_meta(M, r, t, metodo="compuesto", n=12):
    """
    Cuanto hay que depositar HOY (valor presente) para tener M
    dentro de t anios:

    SIMPLE:     P = M / (1 + r t)
    COMPUESTO:  P = M / (1 + r/n)^(n t)
    CONTINUA:   P = M / e^(r t)

    No usa _validar porque aqui P todavia no se conoce -es lo
    que se calcula-, por eso valida M y t directamente.
    """
    # Validaciones manuales de M y t.
    if M <= 0:
        raise ValueError("La meta M debe ser mayor que cero.")
    if t < 0:
        raise ValueError("El tiempo t no puede ser negativo.")

    if metodo == "simple":
        # De M = P(1 + r t)  =>  P = M / (1 + r t)
        return M / (1 + r * t)
    elif metodo == "compuesto":
        # De M = P(1+r/n)^(nt)  =>  P = M / (1+r/n)^(nt)
        return M / (1 + r / n) ** (n * t)
    elif metodo == "continua":
        # De M = P e^(rt)  =>  P = M / e^(rt)
        return M / math.exp(r * t)
    else:
        raise ValueError("metodo debe ser 'simple', 'compuesto' o 'continua'.")


# ==============================================================
# 7. FUNCION AUXILIAR: ganancia
# ==============================================================

def ganancia(monto_final, P):
    """
    Intereses ganados = monto final - capital inicial.
    Se aisla en funcion propia para que el calculo de "ganancia"
    quede definido en un solo lugar (main.py y app.py la reusan).
    """
    # Resta simple: lo que se tiene al final menos lo que se puso.
    return monto_final - P