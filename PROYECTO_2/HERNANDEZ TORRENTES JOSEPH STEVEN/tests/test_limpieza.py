
import pandas as pd
import pytest

from src.limpieza import (
    validar_columnas,
    detectar_faltantes,
    detectar_atipicos,
    preparar_copia,
    interpolar_alturas,
)
def test_validar_columnas_correctas():
    """
    Comprueba que una tabla con las cuatro columnas
    obligatorias sea aceptada.
    """

    datos = pd.DataFrame({
        "fecha_hora": ["2026-05-01 00:00"],
        "altura_significativa_m": [1.2],
        "periodo_pico_s": [8.0],
        "direccion_grados": [210],
    })

    resultado = validar_columnas(datos)

    assert resultado is True



from src.limpieza import detectar_faltantes


def test_detectar_faltantes():
    """
    Comprueba que se cuenten correctamente
    los valores faltantes.
    """

    datos = pd.DataFrame({
        "altura_significativa_m": [
            1.2,
            None,
            1.5,
            None,
        ]
    })

    resultado = detectar_faltantes(datos)

    assert resultado["altura_significativa_m"] == 2



def test_validar_columnas_faltantes():
    """
    Verifica que se genere un error cuando
    falta una columna obligatoria.
    """

    # Crear una tabla incompleta
    datos = pd.DataFrame({
        "fecha_hora": ["2026-05-01 00:00"],
        "altura_significativa_m": [1.2],
        "periodo_pico_s": [8.0],
    })

    # Verificar que la función rechaza la tabla
    with pytest.raises(
        ValueError,
        match="direccion_grados"
    ):
        validar_columnas(datos)


def test_interpolar_fechas_duplicadas():
    """
    Comprueba que la interpolacion rechace fechas
    repetidas en los registros de oleaje.
    """

    # Crear datos de prueba con una fecha duplicada
    datos = pd.DataFrame({
        "fecha_hora": [
            "2026-05-01 00:00",
            "2026-05-01 01:00",
            "2026-05-01 01:00",
            "2026-05-01 02:00",
        ],
        "altura_significativa_m": [
            1.2,
            1.3,
            None,
            1.5,
        ],
        "periodo_pico_s": [
            8.0,
            8.2,
            8.3,
            8.5,
        ],
        "direccion_grados": [
            210,
            211,
            212,
            213,
        ],
    })

    # Esperamos que la funcion genere un error
    with pytest.raises(
        ValueError,
        match="Existen fechas duplicadas"
    ):
        interpolar_alturas(datos)



def test_interpolar_faltantes_consecutivos():
    """
    Comprueba que la interpolacion rechace
    dos alturas faltantes consecutivas.
    """

    # Crear una tabla con dos alturas faltantes
    datos = pd.DataFrame({
        "fecha_hora": [
            "2026-05-01 00:00",
            "2026-05-01 01:00",
            "2026-05-01 02:00",
            "2026-05-01 03:00",
        ],
        "altura_significativa_m": [
            1.2,
            None,
            None,
            1.5,
        ],
        "periodo_pico_s": [
            8.0,
            8.2,
            8.4,
            8.6,
        ],
        "direccion_grados": [
            210,
            211,
            212,
            213,
        ],
    })

    # Verificar que la funcion rechace estos datos
    with pytest.raises(
        ValueError,
        match="Existen alturas faltantes consecutivas"
    ):
        interpolar_alturas(datos)



def test_interpolar_conserva_original():
    """
    Comprueba que la interpolacion:
    - Estime correctamente una altura faltante.
    - Conserve las alturas registradas.
    - No modifique la tabla original.
    - Identifique la altura estimada.
    """

    # Crear datos de prueba
    datos = pd.DataFrame({
        "fecha_hora": [
            "2026-05-01 00:00",
            "2026-05-01 01:00",
            "2026-05-01 02:00",
        ],
        "altura_significativa_m": [
            1.2,
            None,
            1.4,
        ],
        "periodo_pico_s": [
            8.0,
            8.2,
            8.4,
        ],
        "direccion_grados": [
            210,
            211,
            212,
        ],
    })

    # Guardar una copia del estado original
    original = datos.copy(deep=True)

    # Ejecutar la interpolacion
    resultado = interpolar_alturas(datos)

    # Verificar la altura interpolada
    assert resultado.loc[1, "altura_significativa_m"] == (
        pytest.approx(1.3)
    )

    # Verificar las alturas que ya existian
    assert resultado.loc[0, "altura_significativa_m"] == 1.2
    assert resultado.loc[2, "altura_significativa_m"] == 1.4

    # Verificar que la tabla original no cambio
    pd.testing.assert_frame_equal(datos, original)

    # Verificar las marcas de interpolacion
    assert resultado["altura_estimada"].tolist() == [
        False,
        True,
        False,
    ]

    # Verificar que no se agregaron ni eliminaron filas
    assert len(resultado) == len(datos)

    # Verificar que las otras columnas no cambiaron
    for columna in [
        "fecha_hora",
        "periodo_pico_s",
        "direccion_grados",
    ]:
        pd.testing.assert_series_equal(
            resultado[columna],
            datos[columna],
        )



def test_interpolar_faltante_al_inicio():
    """
    Comprueba que la interpolacion rechace
    una altura faltante al inicio de los datos.
    """

    # Crear tres registros horarios
    datos = pd.DataFrame({
        "fecha_hora": [
            "2026-05-01 00:00",
            "2026-05-01 01:00",
            "2026-05-01 02:00",
        ],
        "altura_significativa_m": [
            None,
            1.2,
            1.4,
        ],
        "periodo_pico_s": [
            8.0,
            8.2,
            8.4,
        ],
        "direccion_grados": [
            210,
            211,
            212,
        ],
    })

    # Esperamos que la funcion rechace estos datos
    with pytest.raises(ValueError):
        interpolar_alturas(datos)




def test_interpolar_faltante_al_final():
    """
    Comprueba que la interpolacion rechace
    una altura faltante al final de los datos.
    """

    # Crear tres registros horarios
    datos = pd.DataFrame({
        "fecha_hora": [
            "2026-05-01 00:00",
            "2026-05-01 01:00",
            "2026-05-01 02:00",
        ],
        "altura_significativa_m": [
            1.2,
            1.4,
            None,
        ],
        "periodo_pico_s": [
            8.0,
            8.2,
            8.4,
        ],
        "direccion_grados": [
            210,
            211,
            212,
        ],
    })

    # Comprobar que se genera un error
    with pytest.raises(ValueError):
        interpolar_alturas(datos)



def test_interpolar_rechaza_salto_horario():
    """
    Comprueba que la interpolacion rechace
    registros que no tienen continuidad horaria.
    """

    # Crear datos con una hora faltante
    datos = pd.DataFrame({
        "fecha_hora": [
            "2026-05-01 00:00",
            "2026-05-01 01:00",
            "2026-05-01 03:00",
        ],
        "altura_significativa_m": [
            1.2,
            None,
            1.4,
        ],
        "periodo_pico_s": [
            8.0,
            8.2,
            8.4,
        ],
        "direccion_grados": [
            210,
            211,
            212,
        ],
    })

    # Verificar que la funcion rechaza el salto horario
    with pytest.raises(ValueError):
        interpolar_alturas(datos)



def test_detectar_atipicos():
    """
    Comprueba que el metodo IQR identifique
    una altura claramente atipica.
    """

    # Crear alturas de ejemplo
    datos = pd.DataFrame({
        "altura_significativa_m": [
            1.0,
            1.1,
            1.2,
            1.3,
            1.4,
            5.0,
        ],
    })

    # Ejecutar la deteccion de valores atipicos
    resultado = detectar_atipicos(
        datos,
        "altura_significativa_m"
    )

    # Comprobar que se detecta un solo valor
    assert len(resultado) == 1

    # Comprobar que el valor detectado es 5.0
    assert resultado.iloc[0]["altura_significativa_m"] == 5.0

    # Comprobar que los datos originales se conservan
    assert len(datos) == 6
    assert datos["altura_significativa_m"].iloc[5] == 5.0



def test_preparar_copia_independiente():
    """
    Comprueba que modificar la copia no afecte
    los datos originales.
    """

    # Crear datos originales de ejemplo
    datos = pd.DataFrame({
        "altura_significativa_m": [
            1.2,
            1.4,
        ]
    })

    # Crear una copia con nuestra funcion
    copia = preparar_copia(datos)

    # Modificar solamente la copia
    copia.loc[0, "altura_significativa_m"] = 9.9

    # Comprobar que la copia cambio
    assert copia.loc[0, "altura_significativa_m"] == 9.9

    # Comprobar que el original NO cambio
    assert datos.loc[0, "altura_significativa_m"] == 1.2

    # Comprobar que son objetos diferentes
    assert copia is not datos
