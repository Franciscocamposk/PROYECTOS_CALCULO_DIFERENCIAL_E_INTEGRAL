
import pandas as pd


def validar_columnas(oleaje: pd.DataFrame) -> bool:
    """
    Verifica las columnas necesarias de Registros_oleaje.

    Entrada:
        oleaje: tabla de pandas con los registros.

    Salida:
        True si todas las columnas existen.

    Unidades:
        No realiza calculos con unidades fisicas.
    """

    columnas_necesarias = [
        "fecha_hora",
        "altura_significativa_m",
        "periodo_pico_s",
        "direccion_grados",
    ]

    for columna in columnas_necesarias:
        if columna not in oleaje.columns:
            raise ValueError(
                f"Falta la columna obligatoria: {columna}"
            )

    return True



def detectar_faltantes(
    datos: pd.DataFrame
) -> pd.Series:
    """
    Cuenta los valores faltantes de cada columna.

    Entrada:
        datos: tabla de pandas que se desea revisar.

    Salida:
        Serie de pandas con la cantidad de valores
        faltantes por columna.

    Unidades:
        Cantidad de registros faltantes.
    """

    faltantes = datos.isna().sum()

    return faltantes



def detectar_atipicos(
    datos: pd.DataFrame,
    columna: str
) -> pd.DataFrame:
    """
    Detecta posibles valores atipicos mediante IQR.

    Entradas:
        datos: tabla de pandas.
        columna: nombre de la variable numerica.

    Salida:
        DataFrame con las filas consideradas atipicas.

    Unidades:
        Los limites conservan la unidad de la columna.
        IQR conserva esa misma unidad.

    No modifica los datos originales.
    """

    # Comprobar que la columna existe
    if columna not in datos.columns:
        raise ValueError(
            f"No existe la columna: {columna}"
        )

    # Comprobar que sea numerica
    if not pd.api.types.is_numeric_dtype(datos[columna]):
        raise TypeError(
            f"La columna no es numerica: {columna}"
        )

    # Calcular cuartiles
    q1 = datos[columna].quantile(0.25)
    q3 = datos[columna].quantile(0.75)

    # Calcular rango intercuartilico
    iqr = q3 - q1

    # Calcular limites
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    # Seleccionar posibles valores atipicos
    mascara = (
        (datos[columna] < limite_inferior)
        | (datos[columna] > limite_superior)
    )

    atipicos = datos.loc[mascara].copy()
    """.loc[mascara] selecciona las filas que cumplen nuestra condición,
      mientras que .copy() crea una copia independiente de esas filas.
    Así evitamos que operaciones posteriores sobre el resultado modifiquen
    accidentalmente nuestra tabla de trabajo."""


    return atipicos



def preparar_copia(
    datos: pd.DataFrame
) -> pd.DataFrame:
    """
    Crea una copia independiente de los datos.

    Entrada:
        datos: DataFrame original de pandas.

    Salida:
        DataFrame independiente con los mismos valores.

    Unidades:
        Conserva las unidades originales de cada columna.

    No modifica el DataFrame recibido.
    """

    # Crear una copia independiente
    copia = datos.copy(deep=True)
    """crea un nuevo DataFrame con sus propios datos, independiente del DataFrame 
    original para las operaciones habituales que realizaremos.

    Esto permite modificar posteriormente las columnas de la 
    copia sin alterar las del DataFrame original.

    Hay una aclaración técnica: en pandas, deep=True no duplica 
    recursivamente todos los objetos de Python que pudieran encontrarse dentro de una celda. Para nuestras columnas actuales, que contienen fechas como texto y valores numéricos, es apropiado."""
    return copia



def interpolar_alturas(
    datos: pd.DataFrame
) -> pd.DataFrame:
    """
    Estima alturas faltantes mediante interpolacion lineal.

    Entrada:
        datos: DataFrame de registros de oleaje.

    Salida:
        Copia del DataFrame con alturas estimadas.

    Unidades:
        altura_significativa_m se expresa en metros.
        fecha_hora representa fecha y hora.

    Requisitos:
        Fechas validas, unicas y separadas cada hora.
        Los faltantes deben ser interiores y aislados.

    No modifica el DataFrame recibido.
    """

    # Validar las columnas obligatorias
    validar_columnas(datos)

    # Crear una copia independiente
    copia = preparar_copia(datos)

    # Convertir fechas a valores temporales
    fechas = pd.to_datetime(
        copia["fecha_hora"],
        errors="coerce"
    )

    # Verificar fechas validas
    if fechas.isna().any():
        raise ValueError("Existen fechas invalidas")

    # Verificar fechas ordenadas y sin duplicados
    if not fechas.is_monotonic_increasing:
        raise ValueError("Las fechas no estan ordenadas")

    if fechas.duplicated().any():
        raise ValueError("Existen fechas duplicadas")

    # Verificar intervalos de una hora
    intervalos = fechas.diff().dropna()  #Obtiene la separacion entre fechas consecutivas

    if not intervalos.eq(pd.Timedelta(hours=1)).all():
        raise ValueError(
            "Los registros no tienen intervalos horarios"
        )

    # Identificar las alturas faltantes
    faltantes = copia["altura_significativa_m"].isna()

    # Registrar cuales alturas necesitan estimacion
    copia["altura_estimada"] = faltantes.copy()

    

    # Rechazar faltantes al inicio o al final
    if len(copia) == 0:
        raise ValueError("La tabla de oleaje esta vacia")

    if faltantes.iloc[0] or faltantes.iloc[-1]:
        raise ValueError(
            "Hay alturas faltantes en los extremos"
        )

    # Rechazar valores faltantes consecutivos
    if (faltantes & faltantes.shift(fill_value=False)).any():  #Shift, Desplaza los valores de una columna
        raise ValueError(
            "Existen alturas faltantes consecutivas"
        )

    # Calcular solamente las alturas estimadas
    alturas_estimadas = copia[
        "altura_significativa_m"
    ].interpolate(method="linear", limit_area="inside")

    # Sustituir los valores faltantes solo en la copia
    copia.loc[
        faltantes, "altura_significativa_m"
    ] = alturas_estimadas.loc[faltantes]

    return copia


