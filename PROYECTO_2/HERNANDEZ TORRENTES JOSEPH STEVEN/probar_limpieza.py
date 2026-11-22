
import pandas as pd

from src.limpieza import validar_columnas


# Leer el archivo Excel
ruta = "datos/P08_C-04_HERNANDEZ.xlsx"

hojas = pd.read_excel(ruta, sheet_name=None)

# Seleccionar la hoja de oleaje
oleaje = hojas["Registros_oleaje"]

# Validar las columnas
resultado = validar_columnas(oleaje)

print("VALIDACION DE COLUMNAS")
print("----------------------")
print("Columnas correctas:", resultado)




import pandas as pd

from src.limpieza import (
    validar_columnas,
    detectar_faltantes,
    detectar_atipicos,
    preparar_copia,
    interpolar_alturas,
)

# Leer todas las hojas del Excel
ruta = "datos/P08_C-04_HERNANDEZ.xlsx"

hojas = pd.read_excel(ruta, sheet_name=None)

# Seleccionar los registros de oleaje
oleaje = hojas["Registros_oleaje"]


# PRUEBA 1: validar las columnas
print("VALIDACION DE COLUMNAS")
print("----------------------")

resultado = validar_columnas(oleaje)

print("Columnas correctas:", resultado)


# PRUEBA 2: detectar valores faltantes
print("\nDETECCION DE VALORES FALTANTES")
print("-----------------------------")

faltantes = detectar_faltantes(oleaje)

print(faltantes.to_string())



# PRUEBA 3: detectar posibles valores atipicos
print("\nDETECCION DE VALORES ATIPICOS")
print("----------------------------")

# Analizar altura significativa
atipicos_altura = detectar_atipicos(
    oleaje,
    "altura_significativa_m"
)

print(
    "Posibles atipicos de altura:",
    len(atipicos_altura)
)

# Analizar periodo pico
atipicos_periodo = detectar_atipicos(
    oleaje,
    "periodo_pico_s"
)

print(
    "Posibles atipicos de periodo:",
    len(atipicos_periodo)
)

print("\nVERIFICACION DE DATOS ORIGINALES")
print("--------------------------------")

print("Total de registros:", len(oleaje))

print(
    "Alturas faltantes:",
    oleaje["altura_significativa_m"].isna().sum()
)



# PRUEBA 4: preparar una copia independiente
print("\nPRUEBA DE COPIA DE DATOS")
print("------------------------")

# Crear copia de trabajo
oleaje_copia = preparar_copia(oleaje)

# Comprobar cantidad de registros
print("Registros originales:", len(oleaje))
print("Registros en copia:", len(oleaje_copia))

# Comprobar igualdad antes de realizar cambios
print(
    "Datos inicialmente iguales:",
    oleaje.equals(oleaje_copia)
)

# Modificar temporalmente la copia en memoria
valor_original = oleaje.loc[0, "altura_significativa_m"]

oleaje_copia.loc[0, "altura_significativa_m"] = 999.0

# Comprobar los valores
print("\nVALORES DESPUES DE MODIFICAR LA COPIA")
print("-------------------------------------")

print(
    "Valor original:",
    oleaje.loc[0, "altura_significativa_m"]
)

print(
    "Valor en copia:",
    oleaje_copia.loc[0, "altura_significativa_m"]
)

print(
    "Original conservado:",
    oleaje.loc[0, "altura_significativa_m"] == valor_original
)

# Descartar la copia de prueba
del oleaje_copia



# PRUEBA 5: interpolar alturas faltantes
print("\nPRUEBA DE INTERPOLACION")
print("-----------------------")

# Crear una copia con alturas estimadas
oleaje_interpolado = interpolar_alturas(oleaje)

# Identificar los registros originalmente faltantes
mascara_faltantes = oleaje[
    "altura_significativa_m"
].isna()

# Mostrar solamente las cuatro alturas estimadas
print("\nALTURAS ESTIMADAS:")
print(
    oleaje_interpolado.loc[
        mascara_faltantes,
        ["fecha_hora", "altura_significativa_m"]
    ].to_string(index=False)
)

# Comprobar valores faltantes
print("\nVALORES FALTANTES:")
print(
    "Original:",
    oleaje["altura_significativa_m"].isna().sum()
)

print(
    "Copia interpolada:",
    oleaje_interpolado[
        "altura_significativa_m"
    ].isna().sum()
)

# Comprobar que la tabla original no cambio
print(
    "\nOriginal sin modificaciones:",
    oleaje.equals(hojas["Registros_oleaje"])
)

# Comprobar registros conservados
print("Registros originales:", len(oleaje))
print("Registros interpolados:", len(oleaje_interpolado))

# Verificar que solo cambiaron las alturas faltantes
columnas_sin_cambios = oleaje.drop(
    columns=["altura_significativa_m"]
).equals(
    oleaje_interpolado.drop(
        columns=["altura_significativa_m"]
    )
)

alturas_validas_iguales = oleaje.loc[
    ~mascara_faltantes, "altura_significativa_m"
].equals(
    oleaje_interpolado.loc[
        ~mascara_faltantes, "altura_significativa_m"
    ]
)

print(
    "Otras columnas conservadas:",
    columnas_sin_cambios
)

print(
    "Alturas validas conservadas:",
    alturas_validas_iguales
)



# PRUEBA 6: verificar identificacion de estimaciones
print("\nVERIFICACION DE ALTURAS ESTIMADAS")
print("---------------------------------")

# Crear la copia interpolada actualizada
oleaje_interpolado = interpolar_alturas(oleaje)

# Contar los valores identificados como estimados
cantidad_estimados = oleaje_interpolado[
    "altura_estimada"
].sum()

print("Cantidad de alturas estimadas:", cantidad_estimados)

# Mostrar los registros estimados
registros_estimados = oleaje_interpolado[
    oleaje_interpolado["altura_estimada"]
]

print("\nREGISTROS ESTIMADOS:")
print(
    registros_estimados[
        [
            "fecha_hora",
            "altura_significativa_m",
            "altura_estimada",
        ]
    ].to_string(index=False)
)

# Verificar que la columna no existe en el original
print(
    "\nColumna agregada al original:",
    "altura_estimada" in oleaje.columns
)

# Verificar cantidad de registros
print(
    "Total de registros:",
    len(oleaje_interpolado)
)
