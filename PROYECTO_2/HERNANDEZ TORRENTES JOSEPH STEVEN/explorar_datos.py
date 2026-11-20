
import pandas as pd

# Ruta del archivo Excel
ruta = "datos/P08_C-04_HERNANDEZ.xlsx"

# Leer todas las hojas
hojas = pd.read_excel(ruta, sheet_name=None)

# Seleccionar los registros de oleaje
oleaje = hojas["Registros_oleaje"]

print("EXPLORACION DEL OLEAJE")
print("----------------------")

# Cantidad total de registros, len(oleaje) cuenta las filas de la tabla
print("Total de registros:", len(oleaje))

# Tipos de datos de las columnas
print("\nTIPOS DE DATOS:")
print(oleaje.dtypes)

# Contar valores faltantes o celdas vacías
print("\nVALORES FALTANTES:")
print(oleaje.isna().sum()) #cuenta los resultados por columna

# Contar filas duplicadas exactamente
print("\nFILAS DUPLICADAS:")
print(oleaje.duplicated().sum())

# Consultar fechas disponibles
print("\nPERIODO DE LOS DATOS:")
print("Fecha inicial:", oleaje["fecha_hora"].min()) #Obtiene la fecha más antigua
print("Fecha final:", oleaje["fecha_hora"].max()) #Obtiene la fecha mas reciente



# Identificar registros con altura faltante
print("\nREGISTROS CON ALTURA FALTANTE:")
print("--------------------------------")

# Seleccionar las filas donde falta la altura
faltantes = oleaje[
    oleaje["altura_significativa_m"].isna()
]

# Mostrar los registros encontrados
print(faltantes.to_string(index=False))

# Mostrar la cantidad de filas encontradas
print("\nCantidad de registros afectados:", len(faltantes))


# Investigar los valores cercanos a los faltantes
print("\nVECINOS DE LOS VALORES FALTANTES:")
print("---------------------------------")

# Obtener los indices donde falta la altura
indices_faltantes = oleaje.index[
    oleaje["altura_significativa_m"].isna()
]

# Recorrer cada indice encontrado
for indice in indices_faltantes:

    print(f"\nRegistro faltante en indice: {indice}")

    # Seleccionar una fila anterior,
    # la fila faltante y una posterior
    inicio = max(0, indice - 1)
    fin = min(len(oleaje) - 1, indice + 1)

    vecinos = oleaje.iloc[inicio:fin + 1]

    print(vecinos.to_string(index=False))



# Verificar la continuidad de las fechas
print("\nVALIDACION DE FECHAS:")
print("----------------------")

# Convertir las fechas de texto a datetime
fechas = pd.to_datetime(
    oleaje["fecha_hora"],
    errors="coerce"  #Marca como NaT las fechas que no pueden interpretarse
)

# Comprobar fechas que no se pudieron convertir
fechas_invalidas = fechas.isna().sum()

print("Fechas invalidas:", fechas_invalidas)

# Comprobar fechas repetidas
fechas_repetidas = fechas.duplicated().sum()

print("Fechas repetidas:", fechas_repetidas)

# Comprobar si las fechas estan ordenadas
print("Fechas ordenadas:", fechas.is_monotonic_increasing) #Comprueba si las fechas están ordenadas de menor a mayor

# Crear una secuencia horaria esperada
fechas_esperadas = pd.date_range(  #Genera una secuencia de fechas esperadas
    start=fechas.min(),
    end=fechas.max(),
    freq="h"
)

# Encontrar horas que no aparecen en los datos
fechas_faltantes = fechas_esperadas.difference(fechas)

print("Horas esperadas:", len(fechas_esperadas))
print("Horas sin registro:", len(fechas_faltantes))

# Mostrar las fechas faltantes, si existen
if len(fechas_faltantes) > 0:
    print("\nFechas faltantes:")
    print(fechas_faltantes)


# Estadisticas descriptivas del oleaje
print("\nESTADISTICAS DESCRIPTIVAS:")
print("--------------------------")

columnas_numericas = [
    "altura_significativa_m",
    "periodo_pico_s",
    "direccion_grados"
]

# Seleccionar solamente las columnas numericas
datos_numericos = oleaje[columnas_numericas]

# Mostrar estadisticas descriptivas
print(datos_numericos.describe().to_string())


# Detectar posibles valores atipicos con IQR
print("\nANALISIS DE VALORES ATIPICOS:")
print("-----------------------------")

# Analizar altura significativa y periodo pico
columnas_analizar = [
    "altura_significativa_m",
    "periodo_pico_s"
]

for columna in columnas_analizar:

    print(f"\nVariable: {columna}")

    # Calcular los cuartiles
    q1 = oleaje[columna].quantile(0.25)  #Calcula el primer cuartil
    q3 = oleaje[columna].quantile(0.75)   #Calcula el tercer cuartil

    # Calcular el rango intercuartilico
    iqr = q3 - q1

    # Calcular los limites
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    # Seleccionar valores fuera de los limites
    atipicos = oleaje[
        (oleaje[columna] < limite_inferior)
        | (oleaje[columna] > limite_superior)
    ]

    print(f"Limite inferior: {limite_inferior:.3f}")
    print(f"Limite superior: {limite_superior:.3f}")
    print(f"Cantidad de posibles atipicos: {len(atipicos)}")

    # Mostrar las primeras 10 filas detectadas
    print(atipicos.head(10).to_string(index=False))



# Investigar las fechas con alturas elevadas
print("\nDISTRIBUCION DE ALTURAS ELEVADAS:")
print("---------------------------------")

# Obtener los cuartiles de altura
q1_altura = oleaje["altura_significativa_m"].quantile(0.25)
q3_altura = oleaje["altura_significativa_m"].quantile(0.75)

# Calcular el limite superior del IQR
iqr_altura = q3_altura - q1_altura
limite_altura = q3_altura + 1.5 * iqr_altura

# Seleccionar las alturas superiores al limite
alturas_elevadas = oleaje[
    oleaje["altura_significativa_m"] > limite_altura
].copy()   #Crea una copia independiente de las filas seleccionadas

# Convertir las fechas para extraer el dia
alturas_elevadas["fecha"] = pd.to_datetime(
    alturas_elevadas["fecha_hora"]
).dt.date   #Extrae solamente el dia

# Contar las mediciones elevadas por dia
conteo_diario = alturas_elevadas.groupby("fecha").size()  #Agrupa los registros por día y cuenta cuantos registros hay en cada grupo

print("Mediciones elevadas por dia:")
print(conteo_diario.to_string())

# Identificar la altura maxima registrada
indice_maximo = oleaje["altura_significativa_m"].idxmax()  #Obtiene el indice de la altura maxima

print("\nREGISTRO CON ALTURA MAXIMA:")
print(oleaje.loc[indice_maximo].to_string()) #Permite consulta una fila mediante su indice



# Revisar los valores elevados aislados
print("\nREVISION DE PICOS AISLADOS:")
print("---------------------------")

# Fechas que queremos investigar
fechas_revisar = [
    "2026-05-09 06:00",
    "2026-05-11",
    "2026-05-29"
]

# Convertir las fechas originales
fechas_oleaje = pd.to_datetime(
    oleaje["fecha_hora"]
)

for fecha in fechas_revisar:

    print(f"\nFecha investigada: {fecha}")

    # Buscar registros de la fecha
    if len(fecha) == 10:
        mascara = (
            fechas_oleaje.dt.date
            == pd.to_datetime(fecha).date()
        )

        candidatos = oleaje[
            mascara
            & (oleaje["altura_significativa_m"] > limite_altura)
        ]

    else:
        candidatos = oleaje[
            fechas_oleaje == pd.to_datetime(fecha)
        ]

    # Mostrar vecinos de cada registro encontrado
    for indice in candidatos.index:

        posicion = oleaje.index.get_loc(indice)   #Obtiene la posicion de la fila que queremos investigar

        inicio = max(0, posicion - 2)
        fin = min(len(oleaje), posicion + 3)  #Establece el intervalo de cinco filas sin salir de los limites de la tabla

        vecinos = oleaje.iloc[inicio:fin]  #Selecciona esas tablas

        print("\nRegistro investigado:")
        print(vecinos.to_string(index=False))
