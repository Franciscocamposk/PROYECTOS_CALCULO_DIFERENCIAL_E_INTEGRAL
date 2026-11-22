# -*- coding: utf-8 -*-
"""
Módulo de modelación matemática, integración numérica propia y calibración acústica.
"""

from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd

NUDOS_A_MS: float = 1852.0 / 3600.0


def trapecio_propio(x: np.ndarray, y: np.ndarray) -> float:
    """Calcula la integral definida mediante la regla del trapecio compuesta desde cero.

    Entradas:
        x: Vector creciente de abscisas (por ejemplo, tiempo en s).
        y: Vector de ordenadas f(x) (por ejemplo, presión cuadrática en Pa²).
    Salidas:
        Aproximación numérica de la integral definida (en unidades de x * y, ej. Pa²·s).
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if len(x_arr) < 2:
        return 0.0
    dx = np.diff(x_arr)
    return float(np.sum(0.5 * (y_arr[:-1] + y_arr[1:]) * dx))


def simpson_propio(x: np.ndarray, y: np.ndarray) -> float:
    """Calcula la integral definida mediante la regla de Simpson 1/3 compuesta desde cero.

    Entradas:
        x: Vector creciente de abscisas (por ejemplo, tiempo en s).
        y: Vector de ordenadas f(x) (por ejemplo, presión cuadrática en Pa²).
    Salidas:
        Aproximación numérica de la integral definida (en unidades de x * y, ej. Pa²·s).
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    n = len(x_arr)
    if n < 3:
        return trapecio_propio(x_arr, y_arr)

    h = np.diff(x_arr)
    if (n - 1) % 2 == 0 and np.allclose(h, h[0]):
        delta = h[0]
        return float(
            delta / 3.0 * (y_arr[0] + y_arr[-1] + 4.0 * np.sum(y_arr[1:-1:2]) + 2.0 * np.sum(y_arr[2:-1:2]))
        )

    total = 0.0
    m = n - 1
    limite = m if (m % 2 == 0) else m - 1
    for i in range(0, limite, 2):
        h0 = x_arr[i + 1] - x_arr[i]
        h1 = x_arr[i + 2] - x_arr[i + 1]
        h_sum = h0 + h1
        if h_sum > 0:
            total += (h_sum / 6.0) * (
                (2.0 - h1 / h0) * y_arr[i]
                + ((h_sum ** 2) / (h0 * h1)) * y_arr[i + 1]
                + (2.0 - h0 / h1) * y_arr[i + 2]
            )
    if m % 2 != 0:
        total += 0.5 * (y_arr[-2] + y_arr[-1]) * (x_arr[-1] - x_arr[-2])
    return float(total)


def p2_teorico(t: Union[float, np.ndarray], S: float, d: float, v: float) -> Union[float, np.ndarray]:
    """Calcula la presión acústica al cuadrado p²(t) = S / (d² + v²·t²).

    Entradas:
        t: Tiempo respecto del punto más cercano (s).
        S: Intensidad de la fuente sonora (Pa²·m²).
        d: Distancia mínima a la ballena (m).
        v: Velocidad de la embarcación (m/s).
    Salidas:
        Presión acústica al cuadrado p²(t) (Pa²).
    """
    return S / (d ** 2 + (v * t) ** 2)


def energia_paso(S: float, d: float, v: float, T: Optional[float] = None) -> float:
    """Calcula la energía sonora (exposición) de un paso completo o truncado en [-T, T].

    Entradas:
        S: Intensidad de la fuente sonora (Pa²·m²).
        d: Distancia mínima de paso (m, > 0).
        v: Velocidad de la embarcación (m/s, > 0).
        T: Semiventana temporal de integración (s). Si es None, calcula la integral impropia en (-∞, +∞).
    Salidas:
        Energía sonora acumulada E (Pa²·s).
    """
    if np.any(np.asarray(d) <= 0) or np.any(np.asarray(v) <= 0) or np.any(np.asarray(S) < 0):
        raise ValueError("Los parámetros d y v deben ser positivos y S no negativo.")
    if T is None:
        return float(np.pi * S / (d * v))
    return float((2.0 * S / (d * v)) * np.arctan(v * T / d))


def estimar_fuente(hidrofono: pd.DataFrame, fondo: float, v_ref_nudos: float = 10.0) -> Dict[str, Any]:
    """Calibra la ley de potencia S(v) = S0*(v/v0)^n a partir de los pases del hidrófono.

    Procedimiento:
        1. Resta el ruido ambiental 'fondo' a 'presion_cuadratica_Pa2' (recortando negativos a 0).
        2. Integra cada pase en [-T, T] con trapecio_propio.
        3. Corrige el truncamiento usando la relación: E_trunc = (2*S/(d*v)) * arctan(v*T/d).
        4. Obtiene el exponente n = ln(S2/S1) / ln(v2/v1) y S0 en la velocidad de referencia.

    Entradas:
        hidrofono: DataFrame de la hoja Hidrofono.
        fondo: Ruido ambiental sin embarcaciones (Pa²).
        v_ref_nudos: Velocidad de referencia v0 (nudos).
    Salidas:
        Diccionario con S0 (Pa²·m²), n (adimensional) y detalle por pase.
    """
    pases_info = []
    for pase_id, grupo in hidrofono.groupby("pase"):
        g = grupo.sort_values("tiempo_s")
        t = g["tiempo_s"].to_numpy(dtype=float)
        p2_neta = np.maximum(g["presion_cuadratica_Pa2"].to_numpy(dtype=float) - float(fondo), 0.0)

        v_kts = float(g["velocidad_nudos"].iloc[0])
        v_ms = v_kts * NUDOS_A_MS
        d_m = float(g["distancia_minima_m"].iloc[0])
        T_val = float(np.max(np.abs(t)))

        e_trap = trapecio_propio(t, p2_neta)
        e_simp = simpson_propio(t, p2_neta)
        factor_trunc = (2.0 / (d_m * v_ms)) * np.arctan(v_ms * T_val / d_m)
        S_est = e_trap / factor_trunc

        pases_info.append({
            "pase": int(pase_id),
            "v_nudos": v_kts,
            "v_ms": v_ms,
            "d_m": d_m,
            "T_s": T_val,
            "E_trapecio_Pa2s": e_trap,
            "E_simpson_Pa2s": e_simp,
            "S_Pa2m2": S_est,
        })

    if len(pases_info) < 2:
        raise ValueError("Se requieren al menos dos pases en la hoja Hidrofono para estimar n y S0.")

    pases_info.sort(key=lambda x: x["v_nudos"])
    p1, p2 = pases_info[0], pases_info[-1]
    n_exp = float(np.log(p2["S_Pa2m2"] / p1["S_Pa2m2"]) / np.log(p2["v_nudos"] / p1["v_nudos"]))
    S0_ref = float(p1["S_Pa2m2"] * ((v_ref_nudos / p1["v_nudos"]) ** n_exp))

    return {
        "S0": S0_ref,
        "n": n_exp,
        "v_ref_nudos": float(v_ref_nudos),
        "pases": pases_info,
    }


def energia_temporada(
    df: pd.DataFrame,
    S0: float,
    n: float,
    v_ref_nudos: float = 10.0,
    p_ref_pa: float = 1e-6,
) -> Tuple[float, float, pd.DataFrame]:
    """Calcula la energía sonora total de la temporada, su nivel en dB y el desglose por tipo.

    Entradas:
        df: DataFrame limpio de pasos (velocidad_nudos en nudos, distancia_minima_m en m).
        S0: Intensidad de fuente a velocidad de referencia (Pa²·m²).
        n: Exponente de velocidad de la fuente (adimensional).
        v_ref_nudos: Velocidad de referencia v0 (nudos).
        p_ref_pa: Presión de referencia para escala en decibelios (Pa, por defecto 1 µPa = 1e-6 Pa).
    Salidas:
        Tupla (energia_total_Pa2s, nivel_dB, df_desglose_por_tipo).
    """
    v_kts = df["velocidad_nudos"].to_numpy(dtype=float)
    v_ms = v_kts * NUDOS_A_MS
    d_m = df["distancia_minima_m"].to_numpy(dtype=float)

    S_vec = S0 * (v_kts / v_ref_nudos) ** n
    E_vec = (np.pi * S_vec) / (d_m * v_ms)

    df_calc = df.copy()
    df_calc["energia_Pa2s"] = E_vec

    e_total = float(np.sum(E_vec))
    ref_e = p_ref_pa ** 2
    nivel_db = float(10.0 * np.log10(e_total / ref_e)) if e_total > 0 else 0.0

    desglose = (
        df_calc.groupby("tipo", as_index=False)
        .agg(
            viajes=("tipo", "count"),
            velocidad_media_nudos=("velocidad_nudos", "mean"),
            distancia_media_m=("distancia_minima_m", "mean"),
            energia_Pa2s=("energia_Pa2s", "sum"),
        )
        .sort_values("energia_Pa2s", ascending=False)
        .reset_index(drop=True)
    )
    desglose["aporte_pct"] = (desglose["energia_Pa2s"] / e_total) * 100.0
    desglose["nivel_dB"] = 10.0 * np.log10(desglose["energia_Pa2s"] / ref_e)

    return e_total, nivel_db, desglose


def validar_modelo() -> Dict[str, float]:
    """Ejecuta la validación numérica obligatoria (S=1, d=100 m, v=5 m/s, T=2000 s, dt=0.5 s).

    Salidas:
        Diccionario con valores de Trapecio, Simpson, fórmula truncada, impropia y error relativo (%).
    """
    S_val, d_val, v_val, T_val, dt_val = 1.0, 100.0, 5.0, 2000.0, 0.5
    t_grid = np.arange(-T_val, T_val + dt_val, dt_val)
    p2_grid = p2_teorico(t_grid, S=S_val, d=d_val, v=v_val)

    i_trap = trapecio_propio(t_grid, p2_grid)
    i_simp = simpson_propio(t_grid, p2_grid)
    i_trunc = energia_paso(S=S_val, d=d_val, v=v_val, T=T_val)
    i_imp = energia_paso(S=S_val, d=d_val, v=v_val, T=None)
    err_pct = abs(i_trap - i_trunc) / i_trunc * 100.0

    return {
        "trapecio_Pa2s": i_trap,
        "simpson_Pa2s": i_simp,
        "truncada_Pa2s": i_trunc,
        "impropia_Pa2s": i_imp,
        "error_relativo_pct": err_pct,
        "cobertura_pct": (i_trunc / i_imp) * 100.0,
    }


class ModeloAcusticoGolfo:
    """Clase principal que encapsula la calibración acústica y el balance de la temporada."""

    def __init__(self, fondo_pa2: float, v_ref_nudos: float = 10.0, p_ref_pa: float = 1e-6) -> None:
        self.fondo_pa2 = float(fondo_pa2)
        self.v_ref_nudos = float(v_ref_nudos)
        self.p_ref_pa = float(p_ref_pa)
        self.S0: Optional[float] = None
        self.n: Optional[float] = None
        self.calibracion_: Optional[Dict[str, Any]] = None

    def calibrar(self, df_hidrofono: pd.DataFrame) -> Dict[str, Any]:
        """Ajusta S0 y n a partir de los registros del hidrófono."""
        res = estimar_fuente(df_hidrofono, self.fondo_pa2, self.v_ref_nudos)
        self.S0 = res["S0"]
        self.n = res["n"]
        self.calibracion_ = res
        return res

    def evaluar_temporada(self, df_pasos: pd.DataFrame) -> Tuple[float, float, pd.DataFrame]:
        """Evalúa la energía acumulada y dB de los pasos entregados usando los parámetros calibrados."""
        if self.S0 is None or self.n is None:
            raise RuntimeError("Debe ejecutar calibrar(df_hidrofono) antes de evaluar la temporada.")
        return energia_temporada(df_pasos, self.S0, self.n, self.v_ref_nudos, self.p_ref_pa)
