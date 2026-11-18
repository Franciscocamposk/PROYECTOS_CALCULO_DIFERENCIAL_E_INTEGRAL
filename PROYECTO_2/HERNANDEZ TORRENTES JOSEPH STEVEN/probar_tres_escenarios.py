
"""Comprueba los tres escenarios con el Excel original."""

from src.lectura_datos import cargar_datos
from src.procesamiento_oleaje import preparar_energia_oleaje
from src.escenarios import comparar_tres_escenarios

# Cargar las seis hojas originales sin modificar el Excel.
hojas = cargar_datos("P08_C-04_HERNANDEZ.xlsx")

# Preparar los 960 registros horarios.
registros = preparar_energia_oleaje(
    hojas["Registros_oleaje"]
)

# Evaluar las 12 combinaciones bajo tres escenarios.
resultado = comparar_tres_escenarios(
    registros,
    hojas["Opciones_convertidor"],
    hojas["Opciones_bateria"],
)

columnas = [
    "convertidor",
    "bateria",
    "costo_total_colones",
    "disponibilidad_normal_pct",
    "disponibilidad_moderado_pct",
    "disponibilidad_adverso_pct",
    "cumple_tres",
]

print("\nCOMPARACIÓN DE LOS TRES ESCENARIOS")
print(resultado[columnas].to_string(index=False))

# Elegir la alternativa de menor costo que cumple los tres.
validas = resultado.loc[resultado["cumple_tres"]]

if validas.empty:
    print("\nNinguna combinación cumple los tres escenarios.")
else:
    mejor = validas.sort_values("costo_total_colones").iloc[0]

    print("\nSISTEMA RECOMENDADO")
    print("Convertidor:", mejor["convertidor"])
    print("Batería:", mejor["bateria"])
    print(f"Costo: ₡{mejor['costo_total_colones']:,.0f}")
    print(
        "Disponibilidad normal:",
        f"{mejor['disponibilidad_normal_pct']:.2f}%",
    )
    print(
        "Disponibilidad moderada:",
        f"{mejor['disponibilidad_moderado_pct']:.2f}%",
    )
    print(
        "Disponibilidad adversa:",
        f"{mejor['disponibilidad_adverso_pct']:.2f}%",
    )
