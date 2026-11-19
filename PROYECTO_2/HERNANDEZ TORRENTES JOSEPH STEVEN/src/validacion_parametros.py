import pandas as pd


def validar_columnas_parametros(datos: pd.DataFrame) -> bool:
    """
    Comprueba que la hoja Parametros contenga
    las tres columnas obligatorias.
    """

    columnas_obligatorias = [
        "parametro",
        "valor",
        "unidad",
    ]

    columnas_faltantes = [
        columna for columna in columnas_obligatorias if columna not in datos.columns
    ]

    if columnas_faltantes:
        raise ValueError(
            "Faltan columnas en Parametros: " + ", ".join(columnas_faltantes)
        )

    return True


def validar_nombres_parametros(datos: pd.DataFrame) -> bool:
    """
    Verifica que la hoja Parametros contenga los seis
    parámetros obligatorios y que no existan nombres
    duplicados o vacíos.

    Args:
        datos: DataFrame de la hoja Parametros.

    Returns:
        True si todos los nombres son válidos.

    Raises:
        ValueError: Si faltan parámetros, existen
        nombres duplicados o hay nombres vacíos.
    """

    # Comprobar primero la estructura de columnas.
    validar_columnas_parametros(datos)

    parametros_obligatorios = {
        "Consumo de la estación",
        "Densidad del agua de mar",
        "Gravedad",
        "Periodo energético / periodo pico",
        "Máximo de horas sin energía",
        "Carga inicial de la batería",
    }

    # Rechazar nombres vacíos o formados solo por espacios.
    nombres = datos["parametro"]

    if nombres.isna().any():
        raise ValueError("Existen nombres de parámetros vacíos")

    if not nombres.map(
        lambda nombre: isinstance(nombre, str) and bool(nombre.strip())
    ).all():
        raise ValueError("Existen nombres de parámetros inválidos")

    # Detectar nombres repetidos.
    duplicados = nombres[nombres.duplicated()]

    if not duplicados.empty:
        raise ValueError(
            "Existen parámetros duplicados: "
            + ", ".join(duplicados.astype(str).unique())
        )

    # Detectar parámetros obligatorios ausentes.
    faltantes = parametros_obligatorios - set(nombres)

    if faltantes:
        raise ValueError(
            "Faltan parámetros obligatorios: " + ", ".join(sorted(faltantes))
        )

    return True


def validar_valores_parametros(datos: pd.DataFrame) -> bool:
    """
    Valida los valores y unidades de los seis parámetros
    necesarios para el modelo energético.

    Reglas:
    - Todos los valores deben ser numéricos y finitos.
    - Consumo, densidad y gravedad deben ser positivos.
    - La relación entre periodos debe estar entre 0 y 1.
    - El porcentaje máximo de horas sin energía debe
      encontrarse entre 0 y 100.
    - La carga inicial debe encontrarse entre 0 y 100.
    - Cada parámetro debe tener su unidad correspondiente.

    No modifica el DataFrame recibido.

    Args:
        datos: DataFrame de la hoja Parametros.

    Returns:
        True cuando todos los valores son válidos.

    Raises:
        ValueError: Cuando algún valor, unidad o rango
        incumple las reglas de validación.
    """
    import math
    from numbers import Real

    # Verificar primero las columnas y los nombres.
    validar_nombres_parametros(datos)

    # Unidades exactas registradas en el Excel original.
    unidades_esperadas = {
        "Consumo de la estación": "W",
        "Densidad del agua de mar": "kg/m³",
        "Gravedad": "m/s²",
        "Periodo energético / periodo pico": "fracción",
        "Máximo de horas sin energía": "% de las horas",
        "Carga inicial de la batería": "%",
    }

    # Rangos de validación.
    # (valor_minimo, valor_maximo, minimo_incluido)
    rangos = {
        "Consumo de la estación": (0, None, False),
        "Densidad del agua de mar": (0, None, False),
        "Gravedad": (0, None, False),
        "Periodo energético / periodo pico": (0, 1, False),
        "Máximo de horas sin energía": (0, 100, True),
        "Carga inicial de la batería": (0, 100, True),
    }

    for _, fila in datos.iterrows():
        nombre = fila["parametro"]
        valor = fila["valor"]
        unidad = fila["unidad"]

        # Rechazar valores vacíos, textos y números infinitos.
        if (
            isinstance(valor, bool)
            or not isinstance(valor, Real)
            or not math.isfinite(valor)
        ):
            raise ValueError(f"Valor numérico inválido para: {nombre}")

        # Comprobar que la unidad sea la esperada.
        if unidad != unidades_esperadas[nombre]:
            raise ValueError(
                f"Unidad incorrecta para '{nombre}': "
                f"se esperaba '{unidades_esperadas[nombre]}'"
            )

        minimo, maximo, minimo_incluido = rangos[nombre]

        if minimo_incluido:
            minimo_invalido = valor < minimo
        else:
            minimo_invalido = valor <= minimo

        if minimo_invalido:
            raise ValueError(f"Valor fuera de rango para: {nombre}")

        if maximo is not None and valor > maximo:
            raise ValueError(f"Valor fuera de rango para: {nombre}")

    return True


def validar_convertidores(datos: pd.DataFrame) -> bool:
    """
    Valida la estructura y los datos de Opciones_convertidor.

    Reglas:
    - Todas las columnas obligatorias deben existir.
    - Cada convertidor debe tener un identificador único.
    - Los valores numéricos deben ser finitos.
    - El ancho de captura debe ser positivo (m).
    - La eficiencia debe estar entre 0 y 1 (fracción).
    - La potencia nominal debe ser positiva (W).
    - El costo debe ser positivo (colones).

    No modifica el DataFrame original.
    """

    import numpy as np

    columnas = [
        "convertidor",
        "ancho_captura_m",
        "eficiencia",
        "potencia_nominal_W",
        "costo_colones",
    ]

    faltantes = [columna for columna in columnas if columna not in datos.columns]

    if faltantes:
        raise ValueError(
            "Faltan columnas en Opciones_convertidor: " + ", ".join(faltantes)
        )

    if datos.empty:
        raise ValueError("No existen convertidores registrados")

    identificadores = datos["convertidor"]

    if identificadores.isna().any():
        raise ValueError("Existen convertidores sin identificador")

    if not identificadores.map(
        lambda valor: isinstance(valor, str) and bool(valor.strip())
    ).all():
        raise ValueError("Existen identificadores inválidos")

    if identificadores.duplicated().any():
        raise ValueError("Existen convertidores duplicados")

    columnas_numericas = [
        "ancho_captura_m",
        "eficiencia",
        "potencia_nominal_W",
        "costo_colones",
    ]

    for columna in columnas_numericas:
        valores = datos[columna]

        # No aceptar datos vacíos, textos ni infinitos.
        if (
            not pd.api.types.is_numeric_dtype(valores)
            or pd.api.types.is_bool_dtype(valores)
            or valores.isna().any()
        ):
            raise ValueError(f"Valores inválidos en {columna}")

        if not np.isfinite(valores.to_numpy(dtype=float)).all():
            raise ValueError(f"Valores no finitos en {columna}")

    if (datos["ancho_captura_m"] <= 0).any():
        raise ValueError("Ancho de captura inválido")

    if ((datos["eficiencia"] <= 0) | (datos["eficiencia"] > 1)).any():
        raise ValueError("Eficiencia fuera de rango")

    if (datos["potencia_nominal_W"] <= 0).any():
        raise ValueError("Potencia nominal inválida")

    if (datos["costo_colones"] <= 0).any():
        raise ValueError("Costo de convertidor inválido")

    return True


def validar_baterias(datos: pd.DataFrame) -> bool:
    """
    Valida los datos de la hoja Opciones_bateria.

    Comprueba:
    - Existencia de las columnas obligatorias.
    - Identificadores de batería válidos y únicos.
    - Capacidad positiva, expresada en kWh.
    - Costo positivo, expresado en colones.
    - Ausencia de valores numéricos vacíos o infinitos.

    Args:
        datos: DataFrame de opciones de batería.

    Returns:
        True si todas las validaciones se cumplen.

    Raises:
        ValueError: Si existen datos inválidos.

    No modifica el DataFrame recibido.
    """
    import numpy as np

    columnas_obligatorias = [
        "bateria",
        "capacidad_kWh",
        "costo_colones",
    ]

    # Comprobar las columnas requeridas.
    faltantes = [
        columna for columna in columnas_obligatorias if columna not in datos.columns
    ]

    if faltantes:
        raise ValueError("Faltan columnas en Opciones_bateria: " + ", ".join(faltantes))

    if datos.empty:
        raise ValueError("No existen baterías registradas")

    # Comprobar identificadores.
    identificadores = datos["bateria"]

    if identificadores.isna().any():
        raise ValueError("Existen baterías sin identificador")

    if not identificadores.map(
        lambda valor: isinstance(valor, str) and bool(valor.strip())
    ).all():
        raise ValueError("Existen identificadores de batería inválidos")

    if identificadores.duplicated().any():
        raise ValueError("Existen baterías duplicadas")

    # Validar capacidad y costo.
    columnas_numericas = [
        "capacidad_kWh",
        "costo_colones",
    ]

    for columna in columnas_numericas:
        valores = datos[columna]

        if (
            not pd.api.types.is_numeric_dtype(valores)
            or pd.api.types.is_bool_dtype(valores)
            or valores.isna().any()
        ):
            raise ValueError(f"Valores numéricos inválidos en {columna}")

        if not np.isfinite(valores.to_numpy(dtype=float)).all():
            raise ValueError(f"Valores no finitos en {columna}")

        if (valores <= 0).any():
            raise ValueError(f"Los valores de {columna} deben ser positivos")

    return True
