"""
Simulación horaria de baterías para el Proyecto 8.

Modelo energético:
- Cada registro representa una hora.
- La estación consume 300 W = 300 Wh por hora.
- La batería inicia completamente cargada.
- Se supone eficiencia ideal de carga y descarga.
- La energía almacenada nunca supera la capacidad.
- Se contabilizan horas cubiertas, déficit y excedentes.

No modifica los datos originales.
"""

import numpy as np
import pandas as pd


def simular_bateria(
    registros: pd.DataFrame,
    capacidad_kwh: float,
    consumo_w: float = 300.0,
    carga_inicial: float = 1.0,
) -> pd.DataFrame:
    """Simula el balance energético durante horas consecutivas."""

    if "potencia_generada_w" not in registros.columns:
        raise ValueError("Falta la columna potencia_generada_w.")

    parametros = [capacidad_kwh, consumo_w, carga_inicial]

    if not all(np.isfinite(v) for v in parametros):
        raise ValueError("Los parámetros deben ser finitos.")

    if capacidad_kwh <= 0 or consumo_w < 0:
        raise ValueError("Capacidad y consumo inválidos.")

    if not 0 <= carga_inicial <= 1:
        raise ValueError("La carga inicial debe estar entre 0 y 1.")

    datos = registros.copy(deep=True)

    if "fecha_hora" in datos.columns:
        datos["fecha_hora"] = pd.to_datetime(datos["fecha_hora"], errors="raise")
        datos = datos.sort_values("fecha_hora").reset_index(drop=True)

        if datos["fecha_hora"].duplicated().any():
            raise ValueError("Existen fechas duplicadas.")

        diferencias = datos["fecha_hora"].diff().dropna()

        if not (diferencias == pd.Timedelta(hours=1)).all():
            raise ValueError("Los registros deben ser horarios consecutivos.")

    potencias = pd.to_numeric(datos["potencia_generada_w"], errors="raise")

    if potencias.isna().any() or not np.isfinite(potencias).all():
        raise ValueError("Hay potencias faltantes o no finitas.")

    if (potencias < 0).any():
        raise ValueError("La potencia generada no puede ser negativa.")

    capacidad_wh = capacidad_kwh * 1000.0
    energia = capacidad_wh * carga_inicial
    demanda_wh = consumo_w  # Cada intervalo dura exactamente una hora.

    resultados = []

    for potencia in potencias:
        energia_inicial = energia
        generacion_wh = float(potencia)

        # Atender primero la demanda mediante generación directa.
        generacion_utilizada = min(generacion_wh, demanda_wh)
        deficit = demanda_wh - generacion_utilizada

        # La batería cubre el déficit disponible.
        descarga = min(energia, deficit)
        energia -= descarga

        energia_servida = generacion_utilizada + descarga
        energia_no_servida = demanda_wh - energia_servida

        # El excedente puede almacenarse sin superar la capacidad.
        excedente = generacion_wh - generacion_utilizada
        carga = min(excedente, capacidad_wh - energia)

        energia += carga
        energia_vertida = excedente - carga

        # Una hora se considera cubierta solo si recibe
        # toda la energía solicitada.
        cubierta = energia_no_servida <= 1e-9

        resultados.append(
            {
                "energia_bateria_inicio_wh": energia_inicial,
                "energia_generada_wh": generacion_wh,
                "energia_servida_wh": energia_servida,
                "energia_no_servida_wh": max(0.0, energia_no_servida),
                "energia_vertida_wh": max(0.0, energia_vertida),
                "energia_bateria_final_wh": energia,
                "hora_cubierta": bool(cubierta),
            }
        )

    return pd.concat(
        [datos, pd.DataFrame(resultados)],
        axis=1,
    )


def resumir_simulacion(simulacion: pd.DataFrame) -> dict:
    """Resume disponibilidad, déficit y energía final."""

    if simulacion.empty:
        raise ValueError("La simulación no puede estar vacía.")

    total = len(simulacion)
    cubiertas = int(simulacion["hora_cubierta"].sum())

    return {
        "horas_totales": total,
        "horas_cubiertas": cubiertas,
        "horas_sin_cobertura": total - cubiertas,
        "disponibilidad_pct": 100.0 * cubiertas / total,
        "energia_no_servida_wh": float(simulacion["energia_no_servida_wh"].sum()),
        "energia_final_wh": float(simulacion["energia_bateria_final_wh"].iloc[-1]),
        "cumple_99_pct": cubiertas / total >= 0.99,
    }


class Bateria:
    """Batería con capacidad y energía almacenada en Wh."""

    def __init__(
        self,
        capacidad_kwh: float,
        carga_inicial: float = 1.0,
    ):
        """Inicializa la batería; carga_inicial es una fracción de 0 a 1."""
        valores = [capacidad_kwh, carga_inicial]
        if not all(np.isfinite(v) for v in valores):
            raise ValueError("Los parámetros deben ser finitos.")
        if capacidad_kwh <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        if not 0 <= carga_inicial <= 1:
            raise ValueError("La carga inicial debe estar entre 0 y 1.")

        self.capacidad_wh = capacidad_kwh * 1000.0
        self.energia_wh = self.capacidad_wh * carga_inicial

    def simular(
        self,
        Pg,
        Pc: float,
        dt: float = 1.0,
    ) -> pd.DataFrame:
        """
        Simula generación, consumo y almacenamiento.

        Pg: secuencia de potencias generadas (W).
        Pc: potencia consumida constante (W).
        dt: duración de cada intervalo (horas).

        Devuelve un DataFrame con balances energéticos en Wh.
        Conserva el estado final de la batería.
        """
        potencias = np.asarray(Pg, dtype=float)

        if potencias.ndim != 1 or potencias.size == 0:
            raise ValueError("Pg debe ser una secuencia no vacía.")
        if not np.isfinite(potencias).all() or (potencias < 0).any():
            raise ValueError("Pg debe contener potencias finitas no negativas.")
        if not np.isfinite(Pc) or Pc < 0:
            raise ValueError("Pc debe ser finita y no negativa.")
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("dt debe ser positivo y finito.")

        resultados = []

        for potencia in potencias:
            inicial = self.energia_wh
            generada = float(potencia) * dt
            demanda = Pc * dt

            # La generación alimenta primero el consumo.
            directa = min(generada, demanda)
            faltante = demanda - directa

            # La batería cubre lo que pueda del faltante.
            descarga = min(self.energia_wh, faltante)
            self.energia_wh -= descarga

            servida = directa + descarga
            no_atendida = max(0.0, demanda - servida)

            # El excedente carga la batería hasta su capacidad.
            excedente = generada - directa
            carga = min(
                excedente,
                self.capacidad_wh - self.energia_wh,
            )
            self.energia_wh += carga
            desperdiciada = max(0.0, excedente - carga)

            resultados.append(
                {
                    "energia_inicial_wh": inicial,
                    "energia_generada_wh": generada,
                    "energia_consumida_wh": demanda,
                    "energia_servida_wh": servida,
                    "energia_no_servida_wh": no_atendida,
                    "energia_vertida_wh": desperdiciada,
                    "energia_bateria_final_wh": self.energia_wh,
                    "hora_cubierta": no_atendida <= 1e-9,
                }
            )

        return pd.DataFrame(resultados)
