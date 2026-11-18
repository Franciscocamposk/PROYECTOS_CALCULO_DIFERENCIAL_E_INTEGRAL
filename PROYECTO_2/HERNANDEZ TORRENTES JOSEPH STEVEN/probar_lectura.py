
"""
Verificación de la lectura centralizada del Excel.

Muestra las hojas y dimensiones sin alterar el archivo.
"""

from src.lectura_datos import cargar_datos


RUTA_EXCEL = "P08_C-04_HERNANDEZ.xlsx"

def main() -> None:
    """Carga el Excel e informa las dimensiones."""

    hojas = cargar_datos(RUTA_EXCEL)

    print("\nLECTURA CENTRALIZADA DEL EXCEL")
    print("-" * 45)

    for nombre, datos in hojas.items():
        print(f"{nombre}: {datos.shape}")

    print("\nValidación de hojas y columnas: CORRECTA")


if __name__ == "__main__":
    main()
