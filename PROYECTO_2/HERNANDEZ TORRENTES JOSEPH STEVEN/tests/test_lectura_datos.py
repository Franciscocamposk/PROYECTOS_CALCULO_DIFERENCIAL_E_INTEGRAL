
"""
Pruebas automáticas de la lectura centralizada del Excel.

Se utilizan archivos temporales para comprobar que:
- El Excel válido se carga correctamente.
- Un archivo inexistente genera un error claro.
- Se detectan hojas obligatorias faltantes.
- Se detectan columnas obligatorias faltantes.

No se modifica el archivo Excel original.
"""

from pathlib import Path

import pandas as pd
import pytest

from src.lectura_datos import cargar_datos


@pytest.fixture
def hojas_validas():
    """
    Genera seis hojas de ejemplo con la estructura
    necesaria para verificar la lectura centralizada.
    """

    return {
        "Registros_oleaje": pd.DataFrame({
            "fecha_hora": ["2026-05-01 00:00"],
            "altura_significativa_m": [1.2],
            "periodo_pico_s": [8.0],
            "direccion_grados": [210],
        }),
        "Muestra_elevacion": pd.DataFrame({
            "registro": [1],
            "fecha_hora": ["2026-05-01 00:00"],
            "tiempo_s": [0],
            "elevacion_m": [0.2],
        }),
        "Opciones_convertidor": pd.DataFrame({
            "convertidor": ["WEC-50"],
            "ancho_captura_m": [0.5],
            "eficiencia": [0.088],
            "potencia_nominal_W": [500],
            "costo_colones": [3210000],
        }),
        "Opciones_bateria": pd.DataFrame({
            "bateria": ["B2"],
            "capacidad_kWh": [2],
            "costo_colones": [960000],
        }),
        "Parametros": pd.DataFrame({
            "parametro": [
                "Consumo de la estación",
                "Densidad del agua de mar",
                "Gravedad",
                "Periodo energético / periodo pico",
                "Máximo de horas sin energía",
                "Carga inicial de la batería",
            ],
            "valor": [
                300.0, 1025.0, 9.81, 0.90, 1.0, 100.0
            ],
            "unidad": [
                "W", "kg/m³", "m/s²",
                "fracción", "% de las horas", "%"
            ],
        }),
        "Diccionario": pd.DataFrame({
            "hoja": ["Registros_oleaje"],
            "columna": ["altura_significativa_m"],
            "descripcion": ["Altura significativa"],
            "unidad": ["m"],
        }),
    }


@pytest.fixture
def crear_excel(tmp_path):
    """
    Permite generar archivos Excel temporales para pruebas.

    tmp_path es una carpeta temporal administrada por pytest.
    """

    def guardar(hojas):
        ruta = tmp_path / "datos_prueba.xlsx"

        with pd.ExcelWriter(ruta, engine="openpyxl") as escritor:
            for nombre, datos in hojas.items():
                datos.to_excel(
                    escritor,
                    sheet_name=nombre,
                    index=False,
                )

        return ruta

    return guardar


def test_cargar_excel_valido(hojas_validas, crear_excel):
    """Comprueba la lectura de las seis hojas válidas."""

    ruta = crear_excel(hojas_validas)

    resultado = cargar_datos(ruta)

    assert len(resultado) == 6
    assert set(resultado) == set(hojas_validas)


def test_rechazar_archivo_inexistente(tmp_path):
    """Verifica que se rechace una ruta inexistente."""

    ruta = tmp_path / "archivo_inexistente.xlsx"

    with pytest.raises(FileNotFoundError):
        cargar_datos(ruta)


def test_rechazar_hoja_faltante(hojas_validas, crear_excel):
    """Comprueba que se detecte una hoja obligatoria faltante."""

    hojas = hojas_validas.copy()
    del hojas["Opciones_bateria"]

    ruta = crear_excel(hojas)

    with pytest.raises(ValueError, match="Faltan hojas obligatorias"):
        cargar_datos(ruta)


def test_rechazar_columna_faltante(hojas_validas, crear_excel):
    """Comprueba que se detecte una columna obligatoria faltante."""

    hojas = hojas_validas.copy()

    hojas["Muestra_elevacion"] = hojas["Muestra_elevacion"].drop(
        columns=["elevacion_m"]
    )

    ruta = crear_excel(hojas)

    with pytest.raises(ValueError, match="Faltan columnas en Muestra_elevacion"):
        cargar_datos(ruta)
