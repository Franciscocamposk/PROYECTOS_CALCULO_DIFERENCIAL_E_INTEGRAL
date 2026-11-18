
"""Pruebas de varianza de elevación y altura significativa."""

import pandas as pd
import pytest

from src.calculos_oleaje import (
    calcular_altura_significativa,
    calcular_por_registro,
)


def test_altura_significativa_trapecio():
    """Elevación constante de 2 m: sigma²=4, Hs=8 m."""
    resultado = calcular_altura_significativa(
        [0, 1, 2],
        [2, 2, 2],
        metodo="trapecio",
    )

    assert resultado["varianza_m2"] == pytest.approx(4)
    assert resultado["altura_significativa_m"] == pytest.approx(8)


def test_altura_significativa_simpson():
    """Simpson debe integrar exactamente una elevación constante."""
    resultado = calcular_altura_significativa(
        [0, 1, 2],
        [2, 2, 2],
        metodo="simpson",
    )

    assert resultado["altura_significativa_m"] == pytest.approx(8)


def test_rechazar_metodo_desconocido():
    """Solo se aceptan los dos métodos implementados."""
    with pytest.raises(ValueError):
        calcular_altura_significativa(
            [0, 1, 2],
            [1, 2, 3],
            metodo="otro",
        )


def test_calcular_registros_separados():
    """Cada registro debe procesarse de forma independiente."""
    muestras = pd.DataFrame({
        "registro": [1, 1, 1, 2, 2, 2],
        "tiempo_s": [0, 1, 2, 0, 1, 2],
        "elevacion_m": [1, 1, 1, 2, 2, 2],
    })

    resultados = calcular_por_registro(muestras)

    assert len(resultados) == 2
    assert resultados.iloc[0]["altura_significativa_m"] == pytest.approx(4)
    assert resultados.iloc[1]["altura_significativa_m"] == pytest.approx(8)


def test_rechazar_columnas_faltantes():
    """Los registros deben contener las columnas necesarias."""
    muestras = pd.DataFrame({"registro": [1], "tiempo_s": [0]})

    with pytest.raises(ValueError):
        calcular_por_registro(muestras)
