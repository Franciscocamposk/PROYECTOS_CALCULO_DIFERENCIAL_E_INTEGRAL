
import pandas as pd

from src.validacion_parametros import validar_columnas_parametros


from pathlib import Path

# Localizar el Excel original junto a este archivo Python.
# Funciona aunque el proyecto se copie a otra computadora.
CARPETA_PROYECTO = Path(__file__).resolve().parent
ruta_excel = CARPETA_PROYECTO / "P08_C-04_HERNANDEZ.xlsx"

parametros = pd.read_excel(
    ruta_excel,
    sheet_name="Parametros"
)

# Comprobar las columnas obligatorias
resultado = validar_columnas_parametros(parametros)

print("VALIDACION DE COLUMNAS DE PARAMETROS")
print("-" * 40)

print("Columnas encontradas:")
print(parametros.columns.tolist())

print("\nResultado de la validacion:")
print(resultado)


# --------------------------------------------------
# VALIDACIÓN DE NOMBRES DE PARÁMETROS
# --------------------------------------------------

from src.validacion_parametros import validar_nombres_parametros

resultado_nombres = validar_nombres_parametros(parametros)

print("\nVALIDACION DE NOMBRES DE PARAMETROS")
print("-" * 40)
print("Cantidad de parámetros:", len(parametros))
print("Nombres obligatorios y únicos:", resultado_nombres)



# --------------------------------------------------
# VALIDACIÓN DE VALORES Y UNIDADES
# --------------------------------------------------

from src.validacion_parametros import validar_valores_parametros

resultado_valores = validar_valores_parametros(parametros)

print("\nVALIDACION DE VALORES Y UNIDADES")
print("-" * 40)
print("Parametros analizados:", len(parametros))
print("Valores y unidades correctos:", resultado_valores)



# --------------------------------------------------
# VALIDACIÓN DE OPCIONES DE CONVERTIDOR
# --------------------------------------------------

from src.validacion_parametros import validar_convertidores

# Leer los datos originales sin modificarlos.
convertidores = pd.read_excel(
    ruta_excel,
    sheet_name="Opciones_convertidor"
)

resultado_convertidores = validar_convertidores(convertidores)

print("\nVALIDACION DE CONVERTIDORES")
print("-" * 40)
print("Convertidores analizados:", len(convertidores))
print("Datos de convertidores correctos:", resultado_convertidores)



# --------------------------------------------------
# VALIDACIÓN DE OPCIONES DE BATERÍA
# --------------------------------------------------

from src.validacion_parametros import validar_baterias

# Leer la hoja original sin modificar el Excel.
baterias = pd.read_excel(
    ruta_excel,
    sheet_name="Opciones_bateria"
)

resultado_baterias = validar_baterias(baterias)

print("\nVALIDACION DE BATERIAS")
print("-" * 40)
print("Baterías analizadas:", len(baterias))
print("Datos de baterías correctos:", resultado_baterias)
