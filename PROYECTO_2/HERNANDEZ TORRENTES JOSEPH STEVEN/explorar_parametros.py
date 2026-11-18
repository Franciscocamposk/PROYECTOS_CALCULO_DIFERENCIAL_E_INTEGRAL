
import pandas as pd

# Ruta del archivo Excel original
ruta_excel = "datos/P08_C-04_HERNANDEZ.xlsx"

# Leer únicamente las tres hojas necesarias
parametros = pd.read_excel(
    ruta_excel,
    sheet_name="Parametros"
)

convertidores = pd.read_excel(
    ruta_excel,
    sheet_name="Opciones_convertidor"
)

baterias = pd.read_excel(
    ruta_excel,
    sheet_name="Opciones_bateria"
)

# Mostrar el contenido de cada hoja
print("\nPARAMETROS")
print("-" * 40)
print(parametros.to_string(index=False))

print("\nOPCIONES DE CONVERTIDOR")
print("-" * 40)
print(convertidores.to_string(index=False))

print("\nOPCIONES DE BATERIA")
print("-" * 40)
print(baterias.to_string(index=False))

# Mostrar las dimensiones
print("\nDIMENSIONES")
print("Parametros:", parametros.shape)
print("Convertidores:", convertidores.shape)
print("Baterias:", baterias.shape)
