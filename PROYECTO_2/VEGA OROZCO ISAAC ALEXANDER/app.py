# -*- coding: utf-8 -*-
"""
Proyecto 10: Ruido de embarcaciones y ballenas jorobadas en el Golfo Dulce
Cálculo Diferencial e Integral (MA-0321)
Estudiante: Isaac Alexander Vega Orozco (C-08)
"""

from pathlib import Path
import tempfile
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.limpieza import cargar_datos, extraer_parametros, limpiar_pasos
from src.modelo import ModeloAcusticoGolfo, NUDOS_A_MS
from src.escenarios import analizar_escenarios, evaluar_medida

# Configuración de página
st.set_page_config(
    page_title="Proyecto 10 · Ruido y Ballenas en Golfo Dulce",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent
RUTA_EXCEL_DEFECTO = BASE_DIR / "datos" / "P10_C-08_VEGA.xlsx"


@st.cache_data(show_spinner=False)
def procesar_excel_cacheado(ruta_str: str):
    """Carga, limpia, calibra y evalúa el archivo Excel usando caché de Streamlit."""
    datos = cargar_datos(ruta_str)
    params = extraer_parametros(datos["Parametros"])
    df_limpio, resumen_limp = limpiar_pasos(datos["Pasos_embarcaciones"])

    modelo = ModeloAcusticoGolfo(
        fondo_pa2=params["fondo_pa2"],
        v_ref_nudos=params["v_ref_nudos"],
        p_ref_pa=params["p_ref_pa"],
    )
    cal = modelo.calibrar(datos["Hidrofono"])
    e_base, db_base, desglose = modelo.evaluar_temporada(df_limpio)
    df_res, decision = analizar_escenarios(
        df_limpio, datos["Opciones"], params, cal["S0"], cal["n"]
    )
    return {
        "datos": datos,
        "params": params,
        "df_limpio": df_limpio,
        "resumen_limp": resumen_limp,
        "cal": cal,
        "e_base": e_base,
        "db_base": db_base,
        "desglose": desglose,
        "df_res": df_res,
        "decision": decision,
    }


def html_limpio(texto: str) -> str:
    """Elimina sangrías para que Markdown nunca convierta etiquetas HTML/SVG anidadas en bloques de código."""
    return "\n".join(linea.strip() for linea in texto.splitlines() if linea.strip())


def svg_tacometro_velocidad(vel_nudos: float) -> str:
    """Genera un velocímetro naval SVG dinámico cuya aguja rota según los nudos."""
    pct = max(0.0, min(1.0, (vel_nudos - 5.0) / 20.0))
    angulo = -90.0 + pct * 180.0
    color_aguja = "#34d399" if vel_nudos <= 10.5 else ("#fbbf24" if vel_nudos <= 16.0 else "#fb7185")
    estado_txt = (
        "Ballenas en Calma · Navegación Silenciosa"
        if vel_nudos <= 10.5
        else ("¡Ballenas Espantadas! · Ruido Moderado" if vel_nudos <= 16.0 else "¡Ballenas Espantadas! · Alta Cavitación")
    )
    return html_limpio(f"""
    <div class="cockpit-gauge">
        <div class="gauge-header">TACÓMETRO NAVAL DE VELOCIDAD</div>
        <svg width="190" height="118" viewBox="0 0 200 122" style="display:block;margin:0 auto;">
            <defs>
                <linearGradient id="gradArc" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#10b981"/>
                    <stop offset="45%" stop-color="#fbbf24"/>
                    <stop offset="100%" stop-color="#f43f5e"/>
                </linearGradient>
            </defs>
            <path d="M 24 100 A 76 76 0 0 1 176 100" fill="none" stroke="rgba(148,163,184,0.18)" stroke-width="14" stroke-linecap="round"/>
            <path d="M 24 100 A 76 76 0 0 1 176 100" fill="none" stroke="url(#gradArc)" stroke-width="14" stroke-linecap="round" stroke-dasharray="240" stroke-dashoffset="{240 * (1.0 - pct):.1f}" style="transition: stroke-dashoffset 0.4s ease;"/>
            <text x="14" y="116" fill="#94a3b8" font-size="10" font-weight="700">5 kts</text>
            <text x="86" y="16" fill="#34d399" font-size="10" font-weight="700">10 kts</text>
            <text x="164" y="116" fill="#fb7185" font-size="10" font-weight="700">25 kts</text>
            <g transform="translate(100,100) rotate({angulo:.1f})" style="transition: transform 0.4s cubic-bezier(0.22,1,0.36,1);">
                <polygon points="-3.5,0 0,-68 3.5,0" fill="{color_aguja}"/>
                <circle cx="0" cy="0" r="7" fill="{color_aguja}"/>
                <circle cx="0" cy="0" r="3" fill="#041326"/>
            </g>
        </svg>
        <div class="gauge-val" style="color:{color_aguja};">{vel_nudos:.1f} <span style="font-size:14px;">nudos</span></div>
        <div class="gauge-sub" style="color:{color_aguja}; font-weight:700;">{estado_txt}</div>
    </div>
    """)


def svg_silueta_madre_y_cria_lateral(dur_aleteo: float, espantada: bool = False) -> str:
    """Dibuja la sombra lateral inconfundible de una ballena jorobada madre y su cría nadando."""
    color_sombra = "#020d1d" if not espantada else "#070b18"
    borde_sombra = "rgba(56, 189, 248, 0.22)" if not espantada else "rgba(251, 113, 133, 0.38)"
    ondas_panico = (
        '<circle cx="105" cy="38" r="18" fill="none" stroke="rgba(251,113,133,0.45)" stroke-width="2">'
        '<animate attributeName="r" values="14;44" dur="0.7s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0.8;0" dur="0.7s" repeatCount="indefinite"/>'
        '</circle>'
        if espantada
        else ""
    )
    return f"""
    <svg width="260" height="150" viewBox="0 0 130 80" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g>
            <!-- Ondulación vertical natural de cetáceo al nadar (arriba y abajo) -->
            <animateTransform attributeName="transform" type="translate"
                values="0,0; 0,-7; 0,0; 0,6; 0,0" dur="{dur_aleteo * 1.3:.2f}s" repeatCount="indefinite"/>
            {ondas_panico}
            <!-- Sombra lateral de la Ballena Madre (lomo arqueado, giba dorsal, cola bifurcada de ballena y aleta pectoral inferior) -->
            <g>
                <animateTransform attributeName="transform" type="rotate"
                    values="-4 65 40; 4 65 40; -4 65 40" dur="{dur_aleteo:.2f}s" repeatCount="indefinite"/>
                <path d="M102 38 C88 21 59 19 37 29 C23 35 15 32 6 22 C4 32 9 43 20 46 C12 50 7 57 5 64 C15 61 24 53 30 46 C51 53 81 51 102 38 Z"
                    fill="{color_sombra}" fill-opacity="0.82" stroke="{borde_sombra}" stroke-width="1"/>
                <!-- Aleta pectoral larga inferior de la ballena jorobada -->
                <path d="M72 47 C65 59 54 67 42 70 C45 61 53 53 61 47 Z"
                    fill="{color_sombra}" fill-opacity="0.80"/>
                <!-- Pequeña aleta/giba dorsal superior -->
                <path d="M51 24 C47 18 43 19 40 27 Z"
                    fill="{color_sombra}" fill-opacity="0.80"/>
            </g>
            <!-- Sombra lateral de la Cría nadando debajo/junto a su madre -->
            <g>
                <animateTransform attributeName="transform" type="rotate"
                    values="5 85 58; -5 85 58; 5 85 58" dur="{max(0.35, dur_aleteo * 0.8):.2f}s" repeatCount="indefinite"/>
                <path d="M112 57 C104 48 89 47 78 52 C70 55 66 53 61 49 C60 53 63 59 69 61 C64 63 62 67 61 70 C67 68 71 64 75 61 C86 64 101 63 112 57 Z"
                    fill="{color_sombra}" fill-opacity="0.85" stroke="{borde_sombra}" stroke-width="0.9"/>
                <path d="M95 61 C91 67 85 71 79 73 C81 68 85 64 89 61 Z"
                    fill="{color_sombra}" fill-opacity="0.82"/>
            </g>
        </g>
    </svg>
    """


def render_sombras_ballenas_reactivas(vel_nudos: float) -> str:
    """Genera las sombras submarinas de ballenas madre y cría en el fondo (detrás de las tarjetas) que huyen si la velocidad es alta."""
    espantada = vel_nudos > 10.5
    if not espantada:
        # Modo Calma (<= 10.5 nudos): nadan horizontalmente, despacio y tranquilas por el fondo detrás de la información
        dur_cola = 2.4
        svg_par = svg_silueta_madre_y_cria_lateral(dur_cola, espantada=False)
        return html_limpio(f"""
        <div id="abyssal-whale-shadows">
            <div class="whale-pod calm-swim-right-1">{svg_par}</div>
            <div class="whale-pod calm-swim-left-2"><div style="transform:scaleX(-1);">{svg_par}</div></div>
            <div class="whale-pod calm-swim-right-3">{svg_par}</div>
            <div class="whale-pod calm-swim-left-4"><div style="transform:scaleX(-1);">{svg_par}</div></div>
        </div>
        """)
    else:
        # Modo Espantadas (> 10.5 nudos): el ruido del motor las asusta y huyen rápidamente hacia los bordes y el fondo
        factor_prisa = max(2.2, 7.5 - 0.21 * vel_nudos)
        dur_cola = 0.45
        svg_par = svg_silueta_madre_y_cria_lateral(dur_cola, espantada=True)
        return html_limpio(f"""
        <div id="abyssal-whale-shadows">
            <div class="acoustic-danger-waves"></div>
            <div class="whale-pod panic-flee-left-1" style="animation-duration:{factor_prisa:.2f}s;"><div style="transform:scaleX(-1) rotate(22deg);">{svg_par}</div></div>
            <div class="whale-pod panic-flee-right-2" style="animation-duration:{factor_prisa * 1.1:.2f}s;"><div style="transform:rotate(24deg);">{svg_par}</div></div>
            <div class="whale-pod panic-flee-left-3" style="animation-duration:{factor_prisa * 0.95:.2f}s;"><div style="transform:scaleX(-1) rotate(28deg);">{svg_par}</div></div>
            <div class="whale-pod panic-flee-right-4" style="animation-duration:{factor_prisa * 1.15:.2f}s;"><div style="transform:rotate(26deg);">{svg_par}</div></div>
        </div>
        """)


def svg_sonar_distancia(dist_m: int) -> str:
    """Genera un radar sonar SVG dinámico mostrando la ballena y el perímetro de resguardo."""
    radio_px = 12 + int((min(max(dist_m, 0), 500) / 500.0) * 38)
    barco_x = 100 + radio_px
    color_sonar = "#34d399" if dist_m >= 250 else ("#38bdf8" if dist_m > 0 else "#94a3b8")
    etiqueta = f"Perímetro activo: {dist_m} m" if dist_m > 0 else "Sin restricción de distancia"
    return html_limpio(f"""
    <div class="cockpit-gauge">
        <div class="gauge-header">RADAR SONAR DE RESGUARDO</div>
        <svg width="190" height="118" viewBox="0 0 200 122" style="display:block;margin:0 auto;">
            <circle cx="100" cy="62" r="52" fill="rgba(6, 34, 62, 0.75)" stroke="rgba(56,189,248,0.25)" stroke-width="1.2"/>
            <circle cx="100" cy="62" r="36" fill="none" stroke="rgba(56,189,248,0.18)" stroke-dasharray="3,3"/>
            <circle cx="100" cy="62" r="20" fill="none" stroke="rgba(56,189,248,0.18)" stroke-dasharray="3,3"/>
            <line x1="48" y1="62" x2="152" y2="62" stroke="rgba(56,189,248,0.15)"/>
            <line x1="100" y1="10" x2="100" y2="114" stroke="rgba(56,189,248,0.15)"/>
            <circle cx="100" cy="62" r="{radio_px}" fill="rgba(45,212,191,0.16)" stroke="{color_sonar}" stroke-width="2"/>
            <line x1="100" y1="62" x2="146" y2="38" stroke="rgba(45,212,191,0.65)" stroke-width="2">
                <animateTransform attributeName="transform" type="rotate" from="0 100 62" to="360 100 62" dur="4s" repeatCount="indefinite"/>
            </line>
            <path d="M108 62 C104 56 96 56 91 60 C87 62 85 60 83 58 C82 61 84 64 87 65 C93 67 102 66 108 62 Z" fill="#7dd3fc"/>
            <g transform="translate({barco_x - 8}, 55)">
                <path d="M2 8H16L14 12H4L2 8Z" fill="#fbbf24"/>
                <path d="M5 4H12L14 8H4L5 4Z" fill="#ffffff"/>
            </g>
        </svg>
        <div class="gauge-val" style="color:{color_sonar};">{dist_m} <span style="font-size:14px;">metros</span></div>
        <div class="gauge-sub">{etiqueta}</div>
    </div>
    """)


def svg_anillo_meta(meta_pct: float, logrado_pct: float) -> str:
    """Genera un medidor circular SVG comparando la reducción lograda vs la meta exigida."""
    cumple = logrado_pct >= meta_pct
    color_anillo = "#34d399" if cumple else "#fb7185"
    circ = 2.0 * np.pi * 44.0
    offset_logrado = circ * (1.0 - min(max(logrado_pct, 0.0), 100.0) / 100.0)
    ang_meta = (meta_pct / 100.0) * 360.0 - 90.0
    rad_meta = np.deg2rad(ang_meta)
    mx = 100.0 + 44.0 * np.cos(rad_meta)
    my = 62.0 + 44.0 * np.sin(rad_meta)
    return html_limpio(f"""
    <div class="cockpit-gauge">
        <div class="gauge-header">MONITOR DE META ACÚSTICA</div>
        <svg width="190" height="118" viewBox="0 0 200 122" style="display:block;margin:0 auto;">
            <circle cx="100" cy="62" r="44" fill="none" stroke="rgba(148,163,184,0.18)" stroke-width="11"/>
            <circle cx="100" cy="62" r="44" fill="none" stroke="{color_anillo}" stroke-width="11"
                stroke-linecap="round" transform="rotate(-90 100 62)"
                stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset_logrado:.1f}"/>
            <circle cx="{mx:.1f}" cy="{my:.1f}" r="5.5" fill="#fde047" stroke="#041326" stroke-width="2"/>
            <text x="100" y="60" text-anchor="middle" fill="#ffffff" font-size="16" font-weight="800">{logrado_pct:.1f}%</text>
            <text x="100" y="75" text-anchor="middle" fill="#94a3b8" font-size="9.5" font-weight="700">LOGRADO</text>
        </svg>
        <div class="gauge-val" style="color:{color_anillo};">Meta: {meta_pct:.0f}%</div>
        <div class="gauge-sub">{'Supera la meta exigida' if cumple else 'Por debajo de la meta'}</div>
    </div>
    """)


def svg_icono_embarcacion(tipo: str) -> str:
    """Devuelve una ilustración vectorial SVG personalizada para cada tipo de embarcación."""
    t = tipo.lower()
    if "lancha" in t:
        return """
        <svg width="74" height="38" viewBox="0 0 96 46" fill="none">
            <path d="M8 28H88L76 40H18L8 28Z" fill="#fb7185"/>
            <path d="M26 16H62L72 28H22L26 16Z" fill="#fff1f2"/>
            <rect x="32" y="20" width="9" height="5" rx="1.5" fill="#be123c"/>
            <rect x="45" y="20" width="9" height="5" rx="1.5" fill="#be123c"/>
            <path d="M2 36 Q 8 32, 14 36" stroke="#38bdf8" stroke-width="2.5" fill="none"/>
        </svg>"""
    if "panga" in t:
        return """
        <svg width="74" height="38" viewBox="0 0 96 46" fill="none">
            <path d="M12 27H84L74 39H20L12 27Z" fill="#fbbf24"/>
            <rect x="24" y="21" width="12" height="6" rx="1.5" fill="#fef3c7"/>
            <rect x="10" y="21" width="6" height="8" rx="1" fill="#78350f"/>
            <path d="M4 36 Q 12 33, 20 36" stroke="#38bdf8" stroke-width="2" fill="none"/>
        </svg>"""
    if "yate" in t:
        return """
        <svg width="74" height="38" viewBox="0 0 96 46" fill="none">
            <path d="M6 28H90L78 40H16L6 28Z" fill="#38bdf8"/>
            <path d="M20 18H70L76 28H16L20 18Z" fill="#f8fafc"/>
            <path d="M32 10H58L62 18H28L32 10Z" fill="#bae6fd"/>
            <rect x="28" y="21" width="36" height="4" rx="2" fill="#0284c7"/>
        </svg>"""
    return """
    <svg width="74" height="38" viewBox="0 0 64 44" fill="none">
        <path d="M32 4L50 30H32V4Z" fill="#34d399"/>
        <path d="M29 9L14 30H29V9Z" fill="#a7f3d0"/>
        <path d="M10 32H54L46 40H18L10 32Z" fill="#059669"/>
    </svg>"""


# =============================================================================
# ESTILOS CSS + CONSOLA NAVAL + TABLAS OCEÁNICAS + ANIMACIONES DE SCROLL
# =============================================================================
st.markdown(html_limpio("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        scroll-behavior: smooth;
    }

    .stApp {
        background: radial-gradient(circle at 15% 10%, rgba(14, 165, 233, 0.24) 0%, transparent 35%),
                    radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.20) 0%, transparent 40%),
                    radial-gradient(circle at 50% 85%, rgba(56, 189, 248, 0.16) 0%, transparent 45%),
                    linear-gradient(180deg, #041326 0%, #072340 35%, #0a3154 70%, #051b33 100%) !important;
        color: #f8fafc !important;
    }

    /* Centrado simétrico del contenedor principal dejando margen limpio para la sonda lateral */
    div[data-testid="stMainBlockContainer"], .block-container {
        max-width: 1340px !important;
        padding-left: 3.2rem !important;
        padding-right: 5.4rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    /* Toda la información, tarjetas, controles y gráficas quedan en capa superior (z-index: 5) */
    .hero-ocean, .ganadora-card, .scroll-section, .cockpit-gauge,
    .kpi-grid, .option-matrix-card, .fleet-card, .glass-card,
    .wave-divider, .boat-lane, div[data-testid="stSlider"],
    div[data-testid="stRadio"], div[data-testid="stExpander"],
    div[data-testid="stPlotlyChart"], div[data-testid="stDownloadButton"],
    div[data-testid="stHorizontalBlock"] {
        position: relative;
        z-index: 5 !important;
    }

    /* Capa submarina de fondo (z-index: 0): las sombras de las ballenas pasan DETRÁS de la información */
    div:has(> #abyssal-whale-shadows) {
        position: relative;
        z-index: 0 !important;
    }
    #abyssal-whale-shadows {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0 !important;
        overflow: hidden;
    }
    .whale-pod {
        position: absolute;
        filter: blur(0.8px) drop-shadow(0 12px 24px rgba(1, 7, 18, 0.85));
        will-change: transform, left, right, top;
    }
    /* Modo Calma (<= 10.5 nudos): Nado horizontal suave y continuo por detrás de las tarjetas */
    .calm-swim-right-1 {
        top: 18%;
        left: 0;
        opacity: 0.75;
        animation: whaleCalmRight 18s linear infinite;
        animation-delay: -2s;
    }
    .calm-swim-left-2 {
        top: 46%;
        left: 0;
        opacity: 0.70;
        animation: whaleCalmLeft 22s linear infinite;
        animation-delay: -9s;
    }
    .calm-swim-right-3 {
        top: 72%;
        left: 0;
        opacity: 0.74;
        animation: whaleCalmRight 16s linear infinite;
        animation-delay: -10s;
    }
    .calm-swim-left-4 {
        top: 30%;
        left: 0;
        opacity: 0.65;
        animation: whaleCalmLeft 19s linear infinite;
        animation-delay: -3s;
    }
    @keyframes whaleCalmRight {
        0%   { transform: translate3d(-220px, 0px, 0); }
        25%  { transform: translate3d(25vw, -18px, 0); }
        50%  { transform: translate3d(52vw, 6px, 0); }
        75%  { transform: translate3d(80vw, -14px, 0); }
        100% { transform: translate3d(108vw, 0px, 0); }
    }
    @keyframes whaleCalmLeft {
        0%   { transform: translate3d(108vw, 0px, 0); }
        25%  { transform: translate3d(78vw, 16px, 0); }
        50%  { transform: translate3d(48vw, -12px, 0); }
        75%  { transform: translate3d(18vw, 14px, 0); }
        100% { transform: translate3d(-240px, 0px, 0); }
    }

    /* Modo Espantadas (> 10.5 nudos): Huyen rápidamente del centro hacia las profundidades laterales */
    .panic-flee-left-1 {
        top: 22%;
        left: 0;
        opacity: 0.82;
        animation: whalePanicLeft 3.4s cubic-bezier(0.25, 0.8, 0.3, 1) infinite;
    }
    .panic-flee-right-2 {
        top: 36%;
        left: 0;
        opacity: 0.82;
        animation: whalePanicRight 3.8s cubic-bezier(0.25, 0.8, 0.3, 1) infinite;
        animation-delay: -1.1s;
    }
    .panic-flee-left-3 {
        top: 58%;
        left: 0;
        opacity: 0.80;
        animation: whalePanicLeft 3.1s cubic-bezier(0.25, 0.8, 0.3, 1) infinite;
        animation-delay: -1.8s;
    }
    .panic-flee-right-4 {
        top: 68%;
        left: 0;
        opacity: 0.80;
        animation: whalePanicRight 3.5s cubic-bezier(0.25, 0.8, 0.3, 1) infinite;
        animation-delay: -0.6s;
    }
    @keyframes whalePanicLeft {
        0%   { transform: translate3d(38vw, -20px, 0) scale(0.95); opacity: 0.88; }
        100% { transform: translate3d(-240px, 190px, 0) scale(0.82); opacity: 0.15; }
    }
    @keyframes whalePanicRight {
        0%   { transform: translate3d(52vw, -20px, 0) scale(0.95); opacity: 0.88; }
        100% { transform: translate3d(106vw, 190px, 0) scale(0.82); opacity: 0.15; }
    }
    .acoustic-danger-waves {
        position: fixed;
        top: -120px;
        left: 50%;
        transform: translateX(-50%);
        width: 550px;
        height: 550px;
        border-radius: 50%;
        border: 3px solid rgba(244, 63, 94, 0.28);
        box-shadow: 0 0 60px rgba(244, 63, 94, 0.20);
        animation: dangerWaveExpand 1.4s ease-out infinite;
    }
    @keyframes dangerWaveExpand {
        0%   { transform: translateX(-50%) scale(0.3); opacity: 0.85; }
        100% { transform: translateX(-50%) scale(2.4); opacity: 0; }
    }

    /* Personalización total de los controles de Streamlit (Cero barras rojas feas) */
    div[data-testid="stSlider"] {
        background: linear-gradient(145deg, rgba(12, 34, 61, 0.92), rgba(7, 22, 42, 0.95));
        border: 1px solid rgba(45, 212, 191, 0.35);
        border-radius: 16px;
        padding: 14px 18px 10px 18px;
        box-shadow: 0 8px 24px rgba(2, 12, 27, 0.45), inset 0 1px 0 rgba(255,255,255,0.08);
        transition: all 0.3s ease;
    }
    div[data-testid="stSlider"]:hover {
        border-color: #2dd4bf;
        box-shadow: 0 10px 28px rgba(45, 212, 191, 0.22);
        transform: translateY(-2px);
    }
    div[data-testid="stSlider"] label p {
        font-weight: 700 !important;
        color: #bae6fd !important;
        font-size: 14px !important;
        letter-spacing: 0.3px;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background: linear-gradient(135deg, #38bdf8, #10b981) !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 0 14px rgba(45, 212, 191, 0.95) !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Botones de Radio / Píldoras Tácticas */
    div[data-testid="stRadio"] > div {
        background: rgba(10, 31, 58, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.32);
        border-radius: 14px;
        padding: 10px 16px;
    }

    /* Botón de descarga oceánico */
    div[data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
        color: #ffffff !important;
        border: 1px solid #5eead4 !important;
        border-radius: 12px !important;
        padding: 10px 22px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 20px rgba(13, 148, 136, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 26px rgba(45, 212, 191, 0.55) !important;
    }

    /* Barra de navegación oceánica superior */
    #scroll-ocean-bar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 8px;
        background: rgba(15, 23, 42, 0.75);
        z-index: 999999;
        backdrop-filter: blur(6px);
    }
    #scroll-ocean-fill {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, #38bdf8, #2dd4bf, #10b981);
        box-shadow: 0 0 12px rgba(45, 212, 191, 0.8);
        transition: width 0.08s ease-out;
    }
    #scroll-boat-indicator {
        position: fixed;
        top: 4px;
        left: 12px;
        z-index: 1000000;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.6));
        transition: left 0.08s ease-out;
        pointer-events: none;
    }

    /* Sonda lateral interactiva con el barco que baja al hacer scroll */
    #depth-sonar-hud {
        position: fixed;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        width: 62px;
        height: 270px;
        background: linear-gradient(180deg, rgba(8, 47, 73, 0.90), rgba(4, 19, 38, 0.95));
        border: 1.5px solid rgba(45, 212, 191, 0.45);
        border-radius: 999px;
        z-index: 99990;
        padding: 14px 6px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6), inset 0 0 12px rgba(45, 212, 191, 0.12);
        backdrop-filter: blur(10px);
        pointer-events: none;
    }
    #depth-track {
        position: relative;
        width: 6px;
        height: 172px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.28);
        border-radius: 999px;
    }
    #depth-wake-fill {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 0%;
        background: linear-gradient(180deg, #38bdf8, #2dd4bf, #10b981);
        border-radius: 999px;
        box-shadow: 0 0 10px rgba(45, 212, 191, 0.7);
        transition: height 0.08s linear;
    }
    #depth-sub-marker {
        position: absolute;
        left: -16px;
        top: 0px;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(13, 148, 136, 0.95), rgba(8, 47, 73, 0.98));
        border: 2px solid #5eead4;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 16px rgba(45, 212, 191, 0.9);
        transition: top 0.08s linear;
    }
    #depth-label {
        font-size: 10.5px;
        font-weight: 800;
        color: #5eead4;
        text-align: center;
        line-height: 1.15;
    }

    @keyframes sailAcross {
        0% { transform: translateX(-15%) translateY(0px); }
        25% { transform: translateX(20%) translateY(-6px) rotate(1.5deg); }
        50% { transform: translateX(55%) translateY(0px) rotate(-1deg); }
        75% { transform: translateX(85%) translateY(-5px) rotate(1.5deg); }
        100% { transform: translateX(115%) translateY(0px); }
    }
    @keyframes sailSlowReverse {
        0% { transform: translateX(110%) scaleX(-1) translateY(0px); }
        50% { transform: translateX(45%) scaleX(-1) translateY(-5px); }
        100% { transform: translateX(-15%) scaleX(-1) translateY(0px); }
    }
    @keyframes sonarPulse {
        0% { transform: scale(0.7); opacity: 0.85; }
        100% { transform: scale(2.4); opacity: 0; }
    }
    @keyframes whaleGlide {
        0%, 100% { transform: translateX(0px) translateY(0px) rotate(0deg); }
        50% { transform: translateX(28px) translateY(-10px) rotate(-2deg); }
    }
    @keyframes barGrow {
        from { width: 0%; }
    }

    /* Animaciones reactivas al bajar con el scroll */
    .scroll-section {
        transition: transform 0.7s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.7s ease, filter 0.7s ease;
        will-change: transform, opacity;
    }
    .scroll-section.scroll-hidden {
        opacity: 0.08;
        transform: translateY(48px) scale(0.96);
        filter: blur(3px);
    }
    .scroll-section.scroll-visible {
        opacity: 1;
        transform: translateY(0px) scale(1);
        filter: blur(0px);
    }

    /* Gauges de la consola naval */
    .cockpit-gauge {
        background: linear-gradient(160deg, rgba(10, 32, 58, 0.92), rgba(5, 19, 36, 0.96));
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        padding: 14px 14px 12px 14px;
        text-align: center;
        margin-top: 8px;
        margin-bottom: 14px;
        box-shadow: 0 12px 28px rgba(2, 12, 27, 0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .cockpit-gauge:hover {
        transform: translateY(-4px);
        border-color: #2dd4bf;
    }
    .gauge-header {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.9px;
        color: #7dd3fc;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .gauge-val {
        font-size: 23px;
        font-weight: 800;
        margin-top: 2px;
    }
    .gauge-sub {
        font-size: 12px;
        color: #cbd5e1;
        margin-top: 2px;
    }

    /* Tablero visual de Opciones (Reemplaza la tabla negra fea) */
    .option-matrix-card {
        background: linear-gradient(145deg, rgba(11, 33, 60, 0.92), rgba(6, 21, 40, 0.96));
        border: 1px solid rgba(56, 189, 248, 0.28);
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 10px 26px rgba(2, 12, 27, 0.5);
        transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), border-color 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .option-matrix-card:hover {
        transform: translateX(6px) translateY(-2px);
        border-color: rgba(45, 212, 191, 0.75);
        box-shadow: 0 14px 32px rgba(16, 185, 129, 0.22);
    }
    .option-winner {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.88) 0%, rgba(11, 48, 72, 0.94) 100%);
        border: 2px solid #34d399;
        box-shadow: 0 12px 32px rgba(16, 185, 129, 0.28);
    }
    .option-top-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }
    .option-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 15px;
        font-weight: 800;
        color: #ffffff;
        background: rgba(14, 165, 233, 0.22);
        border: 1px solid rgba(56, 189, 248, 0.45);
        padding: 5px 14px;
        border-radius: 999px;
    }
    .status-pill-ok {
        background: rgba(16, 185, 129, 0.24);
        border: 1px solid #34d399;
        color: #a7f3d0;
        font-size: 12px;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 999px;
        letter-spacing: 0.5px;
    }
    .status-pill-fail {
        background: rgba(244, 63, 94, 0.22);
        border: 1px solid #fb7185;
        color: #fecdd3;
        font-size: 12px;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 999px;
        letter-spacing: 0.5px;
    }
    .progress-track {
        position: relative;
        width: 100%;
        height: 16px;
        background: rgba(15, 23, 42, 0.85);
        border-radius: 999px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.22);
        margin: 10px 0 14px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 999px;
        animation: barGrow 1.2s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .meta-marker {
        position: absolute;
        top: -2px;
        bottom: -2px;
        width: 3px;
        background: #fde047;
        box-shadow: 0 0 8px #fde047;
        z-index: 5;
    }
    .option-metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 10px;
    }
    .metric-chip {
        background: rgba(4, 19, 38, 0.65);
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 12px;
        padding: 8px 12px;
    }
    .metric-chip-label {
        font-size: 11px;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 700;
    }
    .metric-chip-val {
        font-size: 16px;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 2px;
    }

    /* Tarjetas visuales de la flota (Reemplaza la tabla negra de la Sección 04) */
    .fleet-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(255px, 1fr));
        gap: 18px;
        margin-top: 14px;
        margin-bottom: 24px;
    }
    .fleet-card {
        background: linear-gradient(155deg, rgba(12, 36, 66, 0.92), rgba(6, 20, 38, 0.96));
        border: 1px solid rgba(56, 189, 248, 0.32);
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 12px 30px rgba(2, 12, 27, 0.5);
        transition: transform 0.35s ease, border-color 0.35s ease;
        position: relative;
        overflow: hidden;
    }
    .fleet-card:hover {
        transform: translateY(-6px);
        border-color: #2dd4bf;
    }

    .hero-ocean {
        position: relative;
        overflow: hidden;
        border-radius: 22px;
        background: linear-gradient(135deg, #082f49 0%, #0369a1 48%, #0d9488 100%);
        border: 1px solid rgba(125, 211, 252, 0.35);
        box-shadow: 0 20px 45px rgba(2, 12, 27, 0.6), inset 0 1px 0 rgba(255,255,255,0.2);
        padding: 34px 36px 96px 36px;
        margin-bottom: 24px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.22);
        border: 1px solid #34d399;
        color: #a7f3d0 !important;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        padding: 6px 14px;
        border-radius: 999px;
        margin-bottom: 14px;
    }
    .titulo-principal {
        font-size: 34px;
        font-weight: 800;
        color: #ffffff !important;
        line-height: 1.2;
        margin-bottom: 10px;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
    }
    .subtitulo {
        font-size: 16.5px;
        color: #e0f2fe !important;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .ocean-scene {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 92px;
        overflow: hidden;
        pointer-events: none;
    }
    .sailing-boat-1 {
        position: absolute;
        bottom: 28px;
        left: 0;
        width: 100%;
        animation: sailAcross 22s linear infinite;
    }
    .sailing-boat-2 {
        position: absolute;
        bottom: 36px;
        left: 0;
        width: 100%;
        animation: sailSlowReverse 30s linear infinite;
        opacity: 0.75;
    }
    .floating-whale {
        position: absolute;
        right: 42px;
        top: 28px;
        animation: whaleGlide 6s ease-in-out infinite;
        filter: drop-shadow(0 8px 16px rgba(0,0,0,0.35));
    }

    .glass-card {
        background: linear-gradient(145deg, rgba(15, 35, 62, 0.88), rgba(10, 25, 47, 0.94));
        border: 1px solid rgba(56, 189, 248, 0.32);
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(2, 12, 27, 0.45);
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(45, 212, 191, 0.65);
    }
    .ganadora-card {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.92) 0%, rgba(15, 118, 110, 0.88) 100%);
        border: 2px solid #34d399;
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 26px;
        box-shadow: 0 14px 35px rgba(16, 185, 129, 0.25);
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 16px;
        margin: 18px 0 24px 0;
    }
    .kpi-box {
        border-radius: 16px;
        padding: 18px 20px;
        color: #ffffff;
        transition: transform 0.3s ease;
    }
    .kpi-box:hover {
        transform: translateY(-5px);
    }
    .kpi-emerald { background: linear-gradient(135deg, #065f46 0%, #047857 100%); border: 2px solid #34d399; }
    .kpi-amber   { background: linear-gradient(135deg, #78350f 0%, #b45309 100%); border: 1px solid #fbbf24; }
    .kpi-rose    { background: linear-gradient(135deg, #881337 0%, #be123c 100%); border: 1px solid #fb7185; }
    .kpi-cyan    { background: linear-gradient(135deg, #0c4a6e 0%, #0284c7 100%); border: 1px solid #38bdf8; }
    .kpi-tag { font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.7px; opacity: 0.9; margin-bottom: 6px; }
    .kpi-val { font-size: 26px; font-weight: 800; margin-bottom: 4px; }
    .kpi-sub { font-size: 13px; opacity: 0.92; line-height: 1.4; }

    .wave-divider {
        position: relative;
        height: 64px;
        margin: 28px 0;
        overflow: hidden;
        border-radius: 16px;
        background: linear-gradient(90deg, rgba(14, 165, 233, 0.12), rgba(45, 212, 191, 0.24), rgba(14, 165, 233, 0.12));
        border: 1px solid rgba(56, 189, 248, 0.32);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .wave-center-pill {
        position: relative;
        z-index: 3;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 14px;
        background: rgba(5, 23, 44, 0.78);
        border: 1px solid rgba(94, 234, 212, 0.42);
        padding: 8px 24px;
        border-radius: 999px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    }
    .bg-sail-boat {
        position: absolute;
        bottom: 6px;
        left: 0;
        width: 100%;
        animation: sailAcross 19s linear infinite;
        opacity: 0.40;
        pointer-events: none;
        z-index: 1;
    }

    .sec-header {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 24px;
        font-weight: 800;
        color: #f0f9ff !important;
        margin-bottom: 8px;
    }
    .sec-pill {
        background: linear-gradient(135deg, #0ea5e9, #10b981);
        color: #ffffff;
        font-size: 14px;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 999px;
    }

    .boat-lane {
        position: relative;
        height: 64px;
        border-radius: 14px;
        margin-bottom: 12px;
        overflow: hidden;
        display: flex;
        align-items: center;
        padding: 0 18px;
    }
    .lane-fast { background: linear-gradient(90deg, rgba(127, 29, 29, 0.75), rgba(185, 28, 28, 0.45)); border: 1px solid #f87171; }
    .lane-calm { background: linear-gradient(90deg, rgba(6, 78, 59, 0.8), rgba(5, 150, 105, 0.45)); border: 1px solid #34d399; }
    .anim-fast-boat { position: absolute; width: 100%; animation: sailAcross 6s linear infinite; pointer-events: none; }
    .anim-calm-boat { position: absolute; width: 100%; animation: sailAcross 14s linear infinite; pointer-events: none; }
    .sonar-ring-red {
        display: inline-block; width: 22px; height: 22px; border-radius: 50%;
        background: rgba(239, 68, 68, 0.55); animation: sonarPulse 1.1s ease-out infinite;
        vertical-align: middle; margin-left: -10px;
    }
    .sonar-ring-green {
        display: inline-block; width: 15px; height: 15px; border-radius: 50%;
        background: rgba(16, 185, 129, 0.45); animation: sonarPulse 2.4s ease-out infinite;
        vertical-align: middle; margin-left: -8px;
    }
</style>

<!-- Barra superior + Barco indicador de progreso -->
<div id="scroll-ocean-bar"><div id="scroll-ocean-fill"></div></div>
<div id="scroll-boat-indicator" title="Recorrido por el Golfo Dulce">
    <svg width="28" height="16" viewBox="0 0 40 22" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 13H36L31 20H9L4 13Z" fill="#38bdf8"/>
        <path d="M12 6H25L29 13H10L12 6Z" fill="#f8fafc"/>
    </svg>
</div>

<!-- Sonda Lateral: El barco va bajando conforme haces scroll hacia abajo -->
<div id="depth-sonar-hud" title="Navegación vertical por el proyecto">
    <div style="font-size:9.5px; font-weight:800; color:#7dd3fc; letter-spacing:0.6px;">GOLFO</div>
    <div id="depth-track">
        <div id="depth-wake-fill"></div>
        <div id="depth-sub-marker">
            <svg width="24" height="16" viewBox="0 0 44 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 15H40L34 23H10L4 15Z" fill="#38bdf8"/>
                <path d="M13 7H29L33 15H11L13 7Z" fill="#ffffff"/>
                <rect x="16" y="9.5" width="4.5" height="3" rx="0.8" fill="#0284c7"/>
                <rect x="23" y="9.5" width="4.5" height="3" rx="0.8" fill="#0284c7"/>
            </svg>
        </div>
    </div>
    <div id="depth-label">0%<br><span style="font-size:7.5px;color:#94a3b8;">INICIO</span></div>
</div>
"""), unsafe_allow_html=True)

# =============================================================================
# HERO BANNER
# =============================================================================
st.markdown("""
<div class="hero-ocean scroll-section">
    <div class="hero-badge">Universidad de Costa Rica · MA-0321 Cálculo Diferencial e Integral</div>
    <div class="titulo-principal">Ruido de Embarcaciones y Ballenas Jorobadas en el Golfo Dulce</div>
    <div class="subtitulo">Estudiante: <b>Isaac Alexander Vega Orozco (C-08)</b> &nbsp;|&nbsp; Consola Acústica Interactiva con Integrales y Datos Reales</div>
    <div class="floating-whale">
        <svg width="120" height="72" viewBox="0 0 120 72" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M95 38C82 22 55 20 35 30C22 36 14 33 6 24C4 33 9 43 19 46C12 50 7 56 5 62C14 59 23 52 28 46C48 52 75 50 95 38Z" fill="#7dd3fc" fill-opacity="0.88"/>
            <circle cx="80" cy="34" r="2.3" fill="#082f49"/>
            <path d="M104 54C97 46 83 45 73 50C66 53 62 51 58 47C57 51 60 56 65 58C61 60 59 63 58 66C63 64 67 61 70 58C80 61 94 60 104 54Z" fill="#a7f3d0" fill-opacity="0.9"/>
        </svg>
    </div>
    <div class="ocean-scene">
        <div class="sailing-boat-1">
            <svg width="96" height="46" viewBox="0 0 96 46" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 28H82L72 40H22L12 28Z" fill="#38bdf8"/>
                <path d="M28 16H58L66 28H24L28 16Z" fill="#f8fafc"/>
                <rect x="34" y="20" width="8" height="5" rx="1.5" fill="#0284c7"/>
                <rect x="46" y="20" width="8" height="5" rx="1.5" fill="#0284c7"/>
            </svg>
        </div>
        <div class="sailing-boat-2">
            <svg width="64" height="44" viewBox="0 0 64 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M32 6L48 30H32V6Z" fill="#fde68a"/>
                <path d="M30 10L16 30H30V10Z" fill="#fef08a"/>
                <path d="M12 32H52L46 40H18L12 32Z" fill="#fbbf24"/>
            </svg>
        </div>
        <svg viewBox="0 0 1440 90" width="100%" height="90" preserveAspectRatio="none" style="position:absolute;bottom:0;left:0;">
            <path fill="rgba(56, 189, 248, 0.25)" d="M0,42 C240,78 480,6 720,42 C960,78 1200,12 1440,42 L1440,90 L0,90 Z"></path>
            <path fill="rgba(45, 212, 191, 0.32)" d="M0,56 C320,20 640,84 960,48 C1200,24 1320,64 1440,52 L1440,90 L0,90 Z"></path>
            <path fill="#051b33" d="M0,70 C360,92 720,48 1080,72 C1260,82 1380,66 1440,74 L1440,90 L0,90 Z"></path>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# CARGA DE BASE DE DATOS EXCEL (POR DEFECTO O SUBIDA POR EL USUARIO)
# =============================================================================
with st.expander("Cargar otra base de datos Excel (.xlsx) con la misma estructura", expanded=False):
    archivo_subido = st.file_uploader(
        "Selecciona un archivo .xlsx (debe incluir Pasos_embarcaciones, Hidrofono, Opciones y Parametros):",
        type=["xlsx"]
    )

if archivo_subido is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(archivo_subido.getbuffer())
        ruta_activa = tmp.name
else:
    ruta_activa = str(RUTA_EXCEL_DEFECTO)

res = procesar_excel_cacheado(ruta_activa)
params = res["params"]
df_limpio = res["df_limpio"]
cal = res["cal"]
e_base = res["e_base"]
db_base = res["db_base"]
desglose = res["desglose"]
df_res = res["df_res"]
decision = res["decision"]
opt_a = decision["optima_meta_base"]

# =============================================================================
# RESUMEN EJECUTIVO EN 3 PUNTOS
# =============================================================================
st.markdown(f"""
<div class="ganadora-card scroll-section">
    <h3 style="margin-top:0; color:#6ee7b7; font-size:21px;">
        Resumen Ejecutivo del Proyecto en 3 Puntos
    </h3>
    <ol style="margin-bottom:0; font-size:15.5px; line-height:1.75; color:#f8fafc;">
        <li><b>El problema en el Golfo Dulce:</b> Se registraron <b>{len(df_limpio):,} viajes</b> ({e_base:,.1f} Pa²·s · {db_base:.2f} dB) por la zona de cría. El ruido de los motores rápidos tapa los llamados de las ballenas. La meta es reducir la energía sonora en al menos <b>{params['meta_pct']:.0f}%</b> al menor costo.</li>
        <li><b>La solución óptima (Opción {opt_a['opcion']}):</b> <b>{opt_a['descripcion']}</b>. Reduce el ruido en un <b>{opt_a['reduccion_pct']:.1f}%</b> ({opt_a['delta_dB']:+.2f} dB), cuesta <b>₡{opt_a['costo_total_CRC']:,.0f}</b> (la más económica) y agrega {opt_a['horas_extra']:.1f} h en toda la temporada (~8 min/viaje).</li>
        <li><b>¿Y si el refugio sube la meta al {params['meta_pct']+10:.0f}%?:</b> Como la Opción {opt_a['opcion']} ya logra <b>{opt_a['reduccion_pct']:.1f}%</b>, sigue cumpliendo sin gastar un solo colón adicional.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECCIÓN 1: CONSOLA NAVAL DE SIMULACIÓN CON TACÓMETRO, RADAR Y MONITOR SVG
# =============================================================================
st.markdown("""
<div class="scroll-section">
    <div class="sec-header"><span class="sec-pill">01</span> Consola Naval de Simulación y Comparación de Opciones</div>
    <p style="color:#cbd5e1; font-size:15.5px; margin-bottom:12px;">
        Selecciona una regulación táctica rápida o ajusta los instrumentos navales para ver cómo responden el tacómetro, el radar sonar de resguardo y el monitor de energía acústica en tiempo real:
    </p>
</div>
""", unsafe_allow_html=True)

modo_preset = st.radio(
    "Selector Táctico de Escenario del Golfo Dulce:",
    options=[
        "Opción A",
        "Opción B",
        "Opción C",
        "Opción D",
        "Modo Libre",
    ],
    horizontal=True,
)

if "Opción A" in modo_preset:
    def_vel, def_dist = 10.0, 0
elif "Opción B" in modo_preset:
    def_vel, def_dist = 6.0, 0
elif "Opción C" in modo_preset:
    def_vel, def_dist = 25.0, 300
elif "Opción D" in modo_preset:
    def_vel, def_dist = 10.0, 300
else:
    def_vel, def_dist = 12.0, 150

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
with col_ctrl1:
    sim_vel_max = st.slider("Tacómetro: Límite de velocidad (nudos)", min_value=5.0, max_value=25.0, value=float(def_vel), step=0.5)
with col_ctrl2:
    sim_dist_min = st.slider("Sonar: Distancia mínima a ballenas (m)", min_value=0, max_value=500, value=int(def_dist), step=25)
with col_ctrl3:
    sim_meta_pct = st.slider("Umbral: Meta de reducción exigida (%)", min_value=30.0, max_value=85.0, value=float(params["meta_pct"]), step=5.0)

# Renderizar las sombras submarinas reactivas a la velocidad del tacómetro
st.markdown(render_sombras_ballenas_reactivas(sim_vel_max), unsafe_allow_html=True)

params_sim = dict(params)
params_sim["meta_pct"] = sim_meta_pct
costo_fijo_sim = 2500000.0 if (sim_vel_max < 25.0 and sim_dist_min == 0) else (6800000.0 if sim_vel_max >= 25.0 and sim_dist_min > 0 else 7900000.0)
medida_sim = {
    "opcion": "Simulada",
    "descripcion": f"Máx {sim_vel_max:.1f} nudos y mín {sim_dist_min} m",
    "limite_nudos": sim_vel_max if sim_vel_max < 25.0 else None,
    "distancia_minima_m": float(sim_dist_min) if sim_dist_min > 0 else None,
    "costo_fijo_temporada_colones": costo_fijo_sim if (sim_vel_max < 25.0 or sim_dist_min > 0) else 0.0,
}
res_sim = evaluar_medida(df_limpio, medida_sim, params_sim, cal["S0"], cal["n"])

# Renderizar los 3 instrumentos navales SVG debajo de cada control
with col_ctrl1:
    st.markdown(svg_tacometro_velocidad(sim_vel_max), unsafe_allow_html=True)
with col_ctrl2:
    st.markdown(svg_sonar_distancia(sim_dist_min), unsafe_allow_html=True)
with col_ctrl3:
    st.markdown(svg_anillo_meta(sim_meta_pct, res_sim["reduccion_pct"]), unsafe_allow_html=True)

estado_sim = "CUMPLE LA META" if res_sim["cumple_meta"] else "NO CUMPLE LA META"
st.markdown(f"""
<div class="kpi-grid scroll-section">
    <div class="kpi-box kpi-cyan">
        <div class="kpi-tag">Escenario Base (Sin regla)</div>
        <div class="kpi-val">{e_base:,.0f} Pa²·s</div>
        <div class="kpi-sub">Nivel: <b>{db_base:.2f} dB</b><br>1,100 viajes registrados</div>
    </div>
    <div class="kpi-box {'kpi-emerald' if res_sim['cumple_meta'] else 'kpi-rose'}">
        <div class="kpi-tag">Tu Simulación ({estado_sim})</div>
        <div class="kpi-val">-{res_sim['reduccion_pct']:.1f}% ruido</div>
        <div class="kpi-sub">Nivel: <b>{res_sim['nivel_dB']:.2f} dB</b> ({res_sim['delta_dB']:+.2f} dB)<br>Horas extra: <b>{res_sim['horas_extra']:.1f} h</b> | Costo: <b>₡{res_sim['costo_total_CRC']:,.0f}</b></div>
    </div>
    <div class="kpi-box kpi-emerald">
        <div class="kpi-tag">Opción A (Recomendada)</div>
        <div class="kpi-val">-{opt_a['reduccion_pct']:.1f}% ruido</div>
        <div class="kpi-sub">Máximo 10 nudos<br>Costo: <b>₡{opt_a['costo_total_CRC']:,.0f}</b> (Más económica)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# TABLERO VISUAL INTERACTIVO DE OPCIONES (REEMPLAZA LA TABLA NEGRA DE STREAMLIT)
# =============================================================================
st.markdown("""
<div class="scroll-section" style="margin-top:8px; margin-bottom:10px;">
    <div style="font-size:18px; font-weight:800; color:#e0f2fe; margin-bottom:10px;">
        Matriz Comparativa de las 4 Opciones Oficiales de Manejo (con Barras de Reducción vs. Meta)
    </div>
</div>
""", unsafe_allow_html=True)

tarjetas_opciones_html = '<div class="scroll-section">'
for _, r in df_res.iterrows():
    es_ganadora = (opt_a is not None and r["opcion"] == opt_a["opcion"])
    cumple_actual = r["reduccion_pct"] >= sim_meta_pct
    clase_card = "option-matrix-card option-winner" if es_ganadora else "option-matrix-card"
    color_barra = "linear-gradient(90deg, #10b981, #34d399)" if cumple_actual else "linear-gradient(90deg, #e11d48, #fb7185)"
    if es_ganadora:
        etiqueta_estado = f'<span class="status-pill-ok">ÓPTIMA GANADORA · MENOR COSTO (≥ {sim_meta_pct:.0f}%)</span>'
    elif cumple_actual:
        etiqueta_estado = f'<span class="status-pill-ok">CUMPLE META (≥ {sim_meta_pct:.0f}%) · MAYOR COSTO</span>'
    else:
        etiqueta_estado = f'<span class="status-pill-fail">NO ALCANZA LA META DE {sim_meta_pct:.0f}%</span>'

    tarjetas_opciones_html += f"""
    <div class="{clase_card}">
        <div class="option-top-row">
            <span class="option-badge">Opción {r['opcion']}</span>
            {etiqueta_estado}
        </div>
        <div class="progress-track" title="Reducción lograda: {r['reduccion_pct']:.2f}% vs Meta: {sim_meta_pct:.0f}%">
            <div class="meta-marker" style="left:{min(max(sim_meta_pct, 0.0), 100.0):.1f}%;"></div>
            <div class="progress-fill" style="width:{min(max(r['reduccion_pct'], 0.0), 100.0):.1f}%; background:{color_barra};"></div>
        </div>
        <div class="option-metrics-grid">
            <div class="metric-chip">
                <div class="metric-chip-label">Reducción Acústica</div>
                <div class="metric-chip-val" style="color:{'#34d399' if cumple_actual else '#fb7185'};">{r['reduccion_pct']:.2f}%</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Cambio en Decibelios</div>
                <div class="metric-chip-val">{r['delta_dB']:+.2f} dB</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Energía Resultante</div>
                <div class="metric-chip-val">{r['energia_Pa2s']:,.0f} Pa²·s</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Tiempo Operativo Extra</div>
                <div class="metric-chip-val">{r['horas_extra']:.1f} h</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Costo Total Temporada</div>
                <div class="metric-chip-val" style="color:#fde047;">₡{r['costo_total_CRC']:,.0f}</div>
            </div>
        </div>
    </div>
    """
tarjetas_opciones_html += "</div>"
st.markdown(html_limpio(tarjetas_opciones_html), unsafe_allow_html=True)

csv_bytes = df_res.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Descargar resultados completos de los escenarios en CSV",
    data=csv_bytes,
    file_name="resultados_escenarios_P10_VEGA.csv",
    mime="text/csv",
)

col_g1, col_g2 = st.columns(2)
opcs = [f"Opción {o}" for o in df_res["opcion"]]
reds = df_res["reduccion_pct"].tolist()
costos_m = (df_res["costo_total_CRC"] / 1e6).tolist()
colores_red = ['#10b981' if (r >= sim_meta_pct) else '#f43f5e' for r in reds]

with col_g1:
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=opcs, y=reds,
        marker=dict(color=colores_red, line=dict(color='#ffffff', width=1.2)),
        text=[f"<b>{r:.1f}%</b>" for r in reds],
        textposition='outside', textfont=dict(color='#f8fafc', size=13)
    ))
    fig1.add_hline(y=sim_meta_pct, line_dash="dash", line_color="#fde047", annotation_text=f"Meta ({sim_meta_pct:.0f}%)", annotation_font_color="#fef08a")
    fig1.add_hline(y=sim_meta_pct + 10, line_dash="dot", line_color="#38bdf8", annotation_text=f"Meta +10% ({sim_meta_pct+10:.0f}%)", annotation_font_color="#bae6fd")
    fig1.update_layout(
        title=dict(text="<b>Reducción de ruido lograda (%)</b>", font=dict(color="#f8fafc", size=16)),
        yaxis=dict(title="Reducción (%)", range=[0, 108], gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        xaxis=dict(color="#e2e8f0"),
        paper_bgcolor="rgba(15, 35, 62, 0.75)", plot_bgcolor="rgba(15, 35, 62, 0.35)",
        height=370, margin=dict(t=50, b=35, l=45, r=25)
    )
    st.plotly_chart(fig1, width="stretch")

with col_g2:
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=opcs, y=costos_m,
        marker=dict(color=['#10b981', '#f59e0b', '#fb7185', '#38bdf8'], line=dict(color='#ffffff', width=1.2)),
        text=[f"<b>₡{c:.2f}M</b>" for c in costos_m],
        textposition='outside', textfont=dict(color='#f8fafc', size=13)
    ))
    fig2.update_layout(
        title=dict(text="<b>Costo total de la temporada (Millones ₡)</b>", font=dict(color="#f8fafc", size=16)),
        yaxis=dict(title="Millones de colones (₡)", range=[0, 13.8], gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        xaxis=dict(color="#e2e8f0"),
        paper_bgcolor="rgba(15, 35, 62, 0.75)", plot_bgcolor="rgba(15, 35, 62, 0.35)",
        height=370, margin=dict(t=50, b=35, l=45, r=25)
    )
    st.plotly_chart(fig2, width="stretch")

# Separador centrado con barcos navegando en el fondo
st.markdown("""
<div class="wave-divider scroll-section">
    <div class="bg-sail-boat">
        <svg width="56" height="26" viewBox="0 0 96 46" fill="none">
            <path d="M12 28H82L72 40H22L12 28Z" fill="#38bdf8"/>
            <path d="M28 16H58L66 28H24L28 16Z" fill="#f8fafc"/>
        </svg>
    </div>
    <div class="wave-center-pill">
        <svg width="42" height="22" viewBox="0 0 96 46" fill="none" style="vertical-align:middle;">
            <path d="M12 28H82L72 40H22L12 28Z" fill="#38bdf8"/>
            <path d="M28 16H58L66 28H24L28 16Z" fill="#f8fafc"/>
        </svg>
        <span style="font-size:13px; color:#bae6fd; font-weight:700; letter-spacing:0.3px;">
            Corredor Biológico del Golfo Dulce · Monitoreo Acústico de Flota
        </span>
        <svg width="36" height="22" viewBox="0 0 64 44" fill="none" style="vertical-align:middle;">
            <path d="M32 6L48 30H32V6Z" fill="#34d399"/>
            <path d="M12 32H52L46 40H18L12 32Z" fill="#10b981"/>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECCIÓN 2: HISTOGRAMAS DE VELOCIDAD Y DISTANCIA DE LA FLOTA
# =============================================================================
st.markdown("""
<div class="scroll-section">
    <div class="sec-header"><span class="sec-pill">02</span> Distribución de la Flota (Velocidades y Distancias)</div>
    <p style="color:#cbd5e1; font-size:15.5px; margin-bottom:14px;">
        Histograma de los 1,100 viajes limpios. Nota cómo la mayoría supera los 10 nudos, mientras que las distancias ya promedian 266 m:
    </p>
</div>
""", unsafe_allow_html=True)

col_h1, col_h2 = st.columns(2)
with col_h1:
    fig_hv = go.Figure()
    fig_hv.add_trace(go.Histogram(x=df_limpio["velocidad_nudos"], nbinsx=24, marker_color="#38bdf8", opacity=0.88))
    fig_hv.add_vline(x=sim_vel_max, line_dash="dash", line_color="#10b981", annotation_text=f"Límite simulado ({sim_vel_max:.1f} kts)", annotation_font_color="#a7f3d0")
    fig_hv.update_layout(
        title=dict(text="<b>Histograma de Velocidades (nudos)</b>", font=dict(color="#f8fafc", size=16)),
        xaxis=dict(title="Velocidad (nudos)", gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        yaxis=dict(title="Cantidad de viajes", gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        paper_bgcolor="rgba(15, 35, 62, 0.75)", plot_bgcolor="rgba(15, 35, 62, 0.35)", height=340
    )
    st.plotly_chart(fig_hv, width="stretch")

with col_h2:
    fig_hd = go.Figure()
    fig_hd.add_trace(go.Histogram(x=df_limpio["distancia_minima_m"], nbinsx=24, marker_color="#2dd4bf", opacity=0.88))
    if sim_dist_min > 0:
        fig_hd.add_vline(x=sim_dist_min, line_dash="dash", line_color="#fb7185", annotation_text=f"Mínimo ({sim_dist_min} m)", annotation_font_color="#fda4af")
    fig_hd.update_layout(
        title=dict(text="<b>Histograma de Distancias Mínimas (m)</b>", font=dict(color="#f8fafc", size=16)),
        xaxis=dict(title="Distancia mínima (m)", gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        yaxis=dict(title="Cantidad de viajes", gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        paper_bgcolor="rgba(15, 35, 62, 0.75)", plot_bgcolor="rgba(15, 35, 62, 0.35)", height=340
    )
    st.plotly_chart(fig_hd, width="stretch")

# Segundo separador centrado con ballena y barco simétricos
st.markdown("""
<div class="wave-divider scroll-section">
    <div class="bg-sail-boat" style="animation-duration: 24s;">
        <svg width="52" height="24" viewBox="0 0 96 46" fill="none">
            <path d="M12 28H82L72 40H22L12 28Z" fill="#2dd4bf"/>
            <path d="M28 16H58L66 28H24L28 16Z" fill="#f8fafc"/>
        </svg>
    </div>
    <div class="wave-center-pill">
        <svg width="46" height="26" viewBox="0 0 120 72" fill="none" style="vertical-align:middle;">
            <path d="M95 38C82 22 55 20 35 30C22 36 14 33 6 24C4 33 9 43 19 46C12 50 7 56 5 62C14 59 23 52 28 46C48 52 75 50 95 38Z" fill="#7dd3fc"/>
        </svg>
        <span style="font-size:13px; color:#a7f3d0; font-weight:700; letter-spacing:0.3px;">
            Hábitat Acústico de Megaptera novaeangliae · Integración Temporal de Presión Sonora
        </span>
        <svg width="42" height="22" viewBox="0 0 96 46" fill="none" style="vertical-align:middle;">
            <path d="M12 28H82L72 40H22L12 28Z" fill="#34d399"/>
            <path d="M28 16H58L66 28H24L28 16Z" fill="#ecfdf5"/>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SECCIÓN 3: LA INTEGRAL EXPLICADA CON GEOMETRÍA SVG Y ÁREA BAJO LA CURVA
# =============================================================================
st.markdown("""
<div class="scroll-section">
    <div class="sec-header"><span class="sec-pill">03</span> ¿Qué significa la Integral en este proyecto?</div>
    <p style="color:#cbd5e1; font-size:15.5px; margin-bottom:16px;">
        La energía sonora de un paso es la <b>integral definida de la presión cuadrática p²(t) = S / (d² + v²t²)</b>. Al hacer la sustitución <b>u = v·t / d</b>, la primitiva exacta es la función <b>arcotangente</b>:
    </p>
    <div class="boat-lane lane-fast">
        <div style="z-index:2; font-size:14px; font-weight:700; color:#fecdd3;">
            Sin regulación (23 nudos): Motor forzado → Ondas acústicas intensas que tapan a las ballenas
        </div>
        <div class="anim-fast-boat">
            <svg width="42" height="20" viewBox="0 0 96 46" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;">
                <path d="M12 28H82L72 40H22L12 28Z" fill="#fb7185"/>
                <path d="M28 16H58L66 28H24L28 16Z" fill="#fff1f2"/>
            </svg><span class="sonar-ring-red"></span>
        </div>
    </div>
    <div class="boat-lane lane-calm">
        <div style="z-index:2; font-size:14px; font-weight:700; color:#a7f3d0;">
            Con Opción A (10 nudos): Navegación suave → El área bajo la curva cae un 71.4%
        </div>
        <div class="anim-calm-boat">
            <svg width="42" height="20" viewBox="0 0 96 46" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align:middle;">
                <path d="M12 28H82L72 40H22L12 28Z" fill="#34d399"/>
                <path d="M28 16H58L66 28H24L28 16Z" fill="#ecfdf5"/>
            </svg><span class="sonar-ring-green"></span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_curva1, col_curva2 = st.columns([1.05, 1.95])
with col_curva1:
    embarcacion_ejemplo = st.radio(
        "Elige una embarcación típica del Golfo para integrar su paso:",
        options=[
            "Lancha turística rápida (22.8 nudos)",
            "Panga de pesca artesanal (17.0 nudos)",
            "Yate recreativo (15.0 nudos)",
            "Personalizar velocidad y distancia",
        ],
    )
    if "Lancha" in embarcacion_ejemplo:
        v_init, d_init = 22.8, 200
    elif "Panga" in embarcacion_ejemplo:
        v_init, d_init = 17.0, 220
    elif "Yate" in embarcacion_ejemplo:
        v_init, d_init = 15.0, 250
    else:
        v_init, d_init = 20.0, 180

    vel_prueba = st.slider("Velocidad del paso sin límite (nudos):", min_value=6.0, max_value=25.0, value=float(v_init), step=0.2)
    dist_prueba = st.slider("Distancia mínima d a la ballena (m):", min_value=100, max_value=400, value=int(d_init), step=10)

    v_prueba_ms = vel_prueba * NUDOS_A_MS
    v_lim_ms = sim_vel_max * NUDOS_A_MS
    S_prueba = cal["S0"] * ((vel_prueba / params["v_ref_nudos"]) ** cal["n"])
    S_lim = cal["S0"] * ((sim_vel_max / params["v_ref_nudos"]) ** cal["n"])

    E_prueba = (np.pi * S_prueba) / (dist_prueba * v_prueba_ms)
    E_lim = (np.pi * S_lim) / (dist_prueba * v_lim_ms)
    ahorro_pct = max(0.0, (1.0 - E_lim / E_prueba) * 100.0) if E_prueba > 0 else 0.0

    # Diagrama geométrico SVG del triángulo r²(t) = d² + (v·t)² y el resultado de la integral
    st.markdown(html_limpio(f"""
    <div class="glass-card" style="border-color:#34d399; padding:16px 18px;">
        <div style="font-size:12px; color:#7dd3fc; text-transform:uppercase; font-weight:800; letter-spacing:0.6px;">
            Geometría de la Integral: r²(t) = d² + v²t²
        </div>
        <svg width="100%" height="110" viewBox="0 0 280 105" style="margin:6px 0;">
            <line x1="20" y1="22" x2="260" y2="22" stroke="#38bdf8" stroke-dasharray="4,4" stroke-width="1.5"/>
            <line x1="140" y1="22" x2="140" y2="86" stroke="#34d399" stroke-width="2"/>
            <line x1="140" y1="86" x2="225" y2="22" stroke="#fb7185" stroke-width="2">
                <animate attributeName="x2" values="55;225;55" dur="7s" repeatCount="indefinite"/>
            </line>
            <g>
                <animateTransform attributeName="transform" type="translate" values="45,10; 215,10; 45,10" dur="7s" repeatCount="indefinite"/>
                <path d="M2 10H22L19 15H5L2 10Z" fill="#fbbf24"/>
                <path d="M7 5H16L18 10H6L7 5Z" fill="#ffffff"/>
            </g>
            <circle cx="140" cy="86" r="5" fill="#2dd4bf"/>
            <text x="148" y="92" fill="#a7f3d0" font-size="11" font-weight="700">Ballena</text>
            <text x="104" y="60" fill="#34d399" font-size="11" font-weight="700">d = {dist_prueba}m</text>
            <text x="175" y="15" fill="#bae6fd" font-size="11" font-weight="700">x(t) = v·t</text>
            <text x="192" y="64" fill="#fda4af" font-size="11" font-weight="700">r(t)</text>
        </svg>
        <div style="font-size:13px; color:#cbd5e1; margin-bottom:6px;">
            Sustitución: <b>u = (v·t)/d</b> &nbsp;→&nbsp; <b>E = (π·S)/(d·v)</b>
        </div>
        <div style="margin-top:6px; font-size:14.5px;"><span style="color:#fb7185;">●</span> Área a <b>{vel_prueba:.1f} nudos</b>: <b style="color:#fb7185;">{E_prueba:.1f} Pa²·s</b></div>
        <div style="margin-top:3px; font-size:14.5px;"><span style="color:#34d399;">●</span> Área a <b>{sim_vel_max:.1f} nudos</b>: <b style="color:#34d399;">{E_lim:.1f} Pa²·s</b></div>
        <div style="margin-top:8px; padding-top:8px; border-top:1px solid rgba(148,163,184,0.25); font-size:14.5px; color:#a7f3d0;">
            Reducción de energía en este paso: <b>{ahorro_pct:.1f}%</b>
        </div>
    </div>
    """), unsafe_allow_html=True)

with col_curva2:
    t_vals = np.linspace(-120, 120, 400)
    p2_rapida = S_prueba / (dist_prueba**2 + (v_prueba_ms * t_vals)**2)
    p2_lenta = S_lim / (dist_prueba**2 + (v_lim_ms * t_vals)**2)

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=t_vals, y=p2_rapida, mode='lines', fill='tozeroy',
        fillcolor='rgba(244, 63, 94, 0.25)', line=dict(color='#fb7185', width=3),
        name=f"Paso a {vel_prueba:.1f} nudos (Integral = {E_prueba:.1f} Pa²·s)"
    ))
    fig3.add_trace(go.Scatter(
        x=t_vals, y=p2_lenta, mode='lines', fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.35)', line=dict(color='#34d399', width=3),
        name=f"Con límite {sim_vel_max:.1f} nudos (Integral = {E_lim:.1f} Pa²·s)"
    ))
    fig3.update_layout(
        title=dict(text="<b>La Integral Definida como Área bajo la Curva p²(t)</b>", font=dict(color="#f8fafc", size=17)),
        xaxis=dict(title="Tiempo respecto del punto más cercano a la ballena t (s)", gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        yaxis=dict(title="Presión acústica al cuadrado p²(t) [Pa²]", gridcolor="rgba(148,163,184,0.18)", color="#cbd5e1"),
        paper_bgcolor="rgba(15, 35, 62, 0.75)", plot_bgcolor="rgba(15, 35, 62, 0.35)",
        height=465, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(color="#f8fafc")),
        margin=dict(t=65, b=45, l=55, r=25)
    )
    st.plotly_chart(fig3, width="stretch")

# =============================================================================
# SECCIÓN 4: TARJETAS VISUALES DE LA FLOTA (REEMPLAZA LA TABLA NEGRA FEA)
# =============================================================================
st.markdown("""
<div class="scroll-section">
    <div class="sec-header"><span class="sec-pill">04</span> Energía Acumulada por Tipo de Embarcación en el Golfo Dulce</div>
    <p style="color:#cbd5e1; font-size:15.5px; margin-bottom:10px;">
        Desglose acústico de los 1,100 viajes integrados. Las lanchas turísticas y pangas de pesca concentran el <b>87.9%</b> de toda la energía sonora debido a su alta velocidad:
    </p>
</div>
""", unsafe_allow_html=True)

colores_flota = ["#fb7185", "#fbbf24", "#38bdf8", "#34d399"]
flota_html = '<div class="fleet-grid scroll-section">'
for idx, row in desglose.iterrows():
    c_bar = colores_flota[idx % len(colores_flota)]
    icono_svg = svg_icono_embarcacion(str(row["tipo"]))
    flota_html += f"""
    <div class="fleet-card">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
            <div>
                <div style="font-size:18px; font-weight:800; color:#ffffff;">{row['tipo']}</div>
                <div style="font-size:12.5px; color:#94a3b8; font-weight:600;">{int(row['viajes'])} viajes en la temporada</div>
            </div>
            {icono_svg}
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:700; margin-bottom:4px;">
            <span style="color:#cbd5e1;">Aporte al ruido total:</span>
            <span style="color:{c_bar}; font-size:15px; font-weight:800;">{row['aporte_pct']:.2f}%</span>
        </div>
        <div class="progress-track" style="height:12px; margin:4px 0 14px 0;">
            <div class="progress-fill" style="width:{min(max(row['aporte_pct'], 2.0), 100.0):.1f}%; background:{c_bar};"></div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
            <div class="metric-chip">
                <div class="metric-chip-label">Velocidad Media</div>
                <div class="metric-chip-val">{row['velocidad_media_nudos']:.1f} kts</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Distancia Media</div>
                <div class="metric-chip-val">{row['distancia_media_m']:.0f} m</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Energía Integral</div>
                <div class="metric-chip-val" style="color:{c_bar};">{row['energia_Pa2s']:,.0f} Pa²·s</div>
            </div>
            <div class="metric-chip">
                <div class="metric-chip-label">Nivel Acústico</div>
                <div class="metric-chip-val">{row['nivel_dB']:.2f} dB</div>
            </div>
        </div>
    </div>
    """
flota_html += "</div>"
st.markdown(html_limpio(flota_html), unsafe_allow_html=True)

# Motor JavaScript de animaciones de scroll, barco vertical que desciende y aparición de secciones
components.html("""
<script>
(function() {
    const parentWin = window.parent;
    const parentDoc = parentWin.document;

    function getScrollProgress() {
        const vh = parentWin.innerHeight || parentDoc.documentElement.clientHeight || 800;
        const hero = parentDoc.querySelector('.hero-ocean');
        const fleet = parentDoc.querySelector('.fleet-grid');

        if (hero && fleet) {
            const heroRect = hero.getBoundingClientRect();
            const fleetRect = fleet.getBoundingClientRect();
            const scrolled = Math.max(0, 48 - heroRect.top);
            const totalSpan = Math.max(1, (fleetRect.bottom - heroRect.top) - vh + 110);
            const pct = Math.min(100, Math.max(0, (scrolled / totalSpan) * 100));
            return { pct: pct, scrollTop: scrolled };
        }

        // Respaldo buscando cualquier contenedor con scroll activo
        const candidates = [
            parentDoc.querySelector('[data-testid="stAppViewContainer"]'),
            parentDoc.querySelector('[data-testid="stMain"]'),
            parentDoc.querySelector('section.main'),
            parentDoc.documentElement,
            parentDoc.body
        ];
        for (const el of candidates) {
            if (el && el.scrollHeight > el.clientHeight + 20 && el.scrollTop > 0) {
                const p = Math.min(100, Math.max(0, (el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100));
                return { pct: p, scrollTop: el.scrollTop };
            }
        }
        return { pct: 0, scrollTop: 0 };
    }

    function updateScrollAnimations() {
        const info = getScrollProgress();
        const pct = info.pct;

        // 1. Barra oceánica superior y barco horizontal
        const fill = parentDoc.getElementById('scroll-ocean-fill');
        const boat = parentDoc.getElementById('scroll-boat-indicator');
        if (fill) fill.style.width = pct.toFixed(1) + '%';
        if (boat) boat.style.left = 'calc(' + pct.toFixed(1) + '% - 14px)';

        // 2. Barco lateral que va bajando por la sonda conforme haces scroll hacia abajo
        const subMarker = parentDoc.getElementById('depth-sub-marker');
        const wakeFill = parentDoc.getElementById('depth-wake-fill');
        const depthLabel = parentDoc.getElementById('depth-label');
        if (subMarker) {
            // El riel mide 172px y el círculo 36px -> recorrido máximo de 136px
            const topPx = (pct / 100) * 136;
            subMarker.style.top = topPx.toFixed(1) + 'px';
        }
        if (wakeFill) {
            wakeFill.style.height = pct.toFixed(1) + '%';
        }
        if (depthLabel) {
            const pctRound = Math.round(pct);
            const etapa = pct < 20 ? 'INICIO' : (pct < 48 ? 'SIMULADOR' : (pct < 78 ? 'INTEGRAL' : 'FLOTA'));
            depthLabel.innerHTML = pctRound + '%<br><span style="font-size:7.5px;color:#94a3b8;">' + etapa + '</span>';
        }

        // 3. Aparición animada de secciones al hacer scroll hacia abajo
        const sections = parentDoc.querySelectorAll('.scroll-section');
        const vh = parentWin.innerHeight || 800;
        sections.forEach(sec => {
            const rect = sec.getBoundingClientRect();
            if (rect.top < vh * 0.93 && rect.bottom > 30) {
                sec.classList.add('scroll-visible');
                sec.classList.remove('scroll-hidden');
            } else if (rect.top >= vh * 0.96) {
                sec.classList.add('scroll-hidden');
                sec.classList.remove('scroll-visible');
            }
        });
    }

    // capture: true captura el evento scroll de cualquier contenedor interno de Streamlit
    parentDoc.addEventListener('scroll', updateScrollAnimations, { capture: true, passive: true });
    parentWin.addEventListener('scroll', updateScrollAnimations, { capture: true, passive: true });
    parentWin.addEventListener('wheel', () => setTimeout(updateScrollAnimations, 30), { passive: true });
    setTimeout(updateScrollAnimations, 80);
    setInterval(updateScrollAnimations, 120);
})();
</script>
""", height=0)
