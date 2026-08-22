"""
tabs/tab_tablero.py  —  v4.2 Ultra Refined Minimalist Dashboard
==============================================================
Tablero Ejecutivo de Alto Impacto con estética industrial Parex.
Presenta 3 columnas simétricas de 480px de altura:
1. Resumen de Operaciones: Tarjeta premium con KPIs en fondo, pills ALS, estados operativos, activos, inactivos y barras de progreso.
2. Índice de Falla (IF < 1500 RLE): Velocímetro minimalista de precisión + Historial mensual de pozos y tasa IF (con degradados y sombras de área).
3. Desempeño y Vida Útil: Velocímetros limpios de MTBF y RunLife + Distribución de longevidad de pozos activos (con degradados y etiquetas flotantes).
"""

import json, calendar
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

import mtbf as mtbf_mod
from calculations import clasificar_runlife

# ── Paleta Corporativa Parex ─────────────────────────────────────────────────
_G   = "#2E7D46"        # Verde principal
_G2  = "#1F4620"        # Verde oscuro
_G3  = "#EEF3EA"        # Verde muy claro (fondo)
_R   = "#C0392B"        # Rojo falla
_R2  = "#FBE8E6"        # Rojo claro fondo
_Y   = "#C98A2C"        # Dorado acento
_Y2  = "#FDF6E9"        # Dorado fondo
_T   = "#262626"        # Texto oscuro
_T2  = "#707070"        # Texto suave
_W   = "#ffffff"
_N   = "#223A5E"        # Azul petróleo (serie secundaria / metas)
_BR  = "#DCE2D8"        # Borde hairline de tarjeta
_BG  = "#F7F8F5"        # Fondo tenue

# Tipografía ejecutiva: sans para etiquetas, serif para cifras
_FS  = "'Inter', 'Segoe UI', Calibri, Arial, sans-serif"
_FN  = "'Source Serif 4', Cambria, Georgia, 'Times New Roman', serif"
_FONTS_URL = ("https://fonts.googleapis.com/css2?"
              "family=Inter:wght@400;500;600;700;800&"
              "family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap")

# ── Sistema de elevación ─────────────────────────────────────────────────────
# Tres capas por tarjeta: sombra de contacto (nítida y corta), sombra ambiental
# (amplia y difusa) y una luz de borde superior que simula iluminación cenital.
_SH1 = ("0 1px 2px rgba(31,70,32,0.05), 0 4px 12px rgba(126,143,124,0.13), "
        "inset 0 1px 0 rgba(255,255,255,0.9)")
_SH2 = ("0 2px 5px rgba(31,70,32,0.07), 0 14px 32px rgba(126,143,124,0.22), "
        "inset 0 1px 0 rgba(255,255,255,0.9)")

# Tarjeta base: degradado casi imperceptible que aclara el borde superior
_CARD = (f"background:linear-gradient(180deg,#ffffff 0%,#FCFDFA 100%);"
         f"border:1px solid {_BR};border-radius:18px;box-shadow:{_SH1};")


def _fmt(n, dec=0):
    """Formato es-CO: punto para miles, coma para decimales."""
    entero, _, dec_str = f"{n:,.{dec}f}".partition(".")
    entero = entero.replace(",", ".")
    return f"{entero},{dec_str}" if dec_str else entero


def _glow(color, alpha=0.10):
    """Resplandor de esquina en el color semántico de la tarjeta."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return (f"radial-gradient(135% 150% at 0% 0%, rgba({r},{g},{b},{alpha}) 0%, "
            f"rgba({r},{g},{b},0) 58%)")


def _halo(color):
    """Anillo suave + sombra proyectada bajo un icono circular."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return (f"0 0 0 5px rgba({r},{g},{b},0.10), 0 5px 12px rgba({r},{g},{b},0.34), "
            f"inset 0 1px 0 rgba(255,255,255,0.28)")

META_IF   = 7.5
META_MTBF = 2190
META_RL   = 1500
ALS_TIPOS = ['ESP', 'PCP', 'EPCP', 'BM', 'BH']

def _css():
    st.markdown(f"""
<style>
@import url('{_FONTS_URL}');

/* ══════════════════════════════════════════════════════════════════
   ENCABEZADO EJECUTIVO
   ══════════════════════════════════════════════════════════════════ */
.tbl-hero {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 22px;
    background:
        radial-gradient(120% 180% at 0% 0%, rgba(76,164,106,0.42) 0%, rgba(31,70,32,0) 55%),
        linear-gradient(110deg, {_G2} 0%, #17381A 45%, {_G2} 100%);
    border-radius: 14px;
    padding: 15px 24px;
    overflow: hidden;
    box-shadow:
        0 2px 5px rgba(31,70,32,0.13),
        0 16px 38px rgba(31,70,32,0.24),
        inset 0 1px 0 rgba(255,255,255,0.16),
        inset 0 -1px 0 rgba(0,0,0,0.14);
}}

.tbl-hero::after {{
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
    background-size: 26px 26px;
    pointer-events: none;
}}

/* Haz de luz cenital que cruza el encabezado */
.tbl-hero::before {{
    content: '';
    position: absolute;
    top: -60%;
    left: 6%;
    width: 44%;
    height: 220%;
    background: linear-gradient(100deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 72%);
    transform: rotate(14deg);
    pointer-events: none;
    z-index: 0;
}}

.tbl-hero-brand {{
    display: flex;
    align-items: center;
    gap: 14px;
    position: relative;
    z-index: 1;
    flex-shrink: 0;
}}

.tbl-hero-mark {{
    width: 44px;
    height: 44px;
    border-radius: 11px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.24);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.30), 0 4px 12px rgba(0,0,0,0.18);
}}

.tbl-hero-title {{
    font-family: {_FN};
    font-size: 21px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 3px;
}}



.tbl-hero-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #6FD08C;
    box-shadow: 0 0 0 3px rgba(111,208,140,0.22);
}}

.tbl-hero-ctx {{
    display: flex;
    align-items: stretch;
    position: relative;
    z-index: 1;
    flex: 1;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 0;
}}

.tbl-hero-item {{
    padding: 0 18px;
    border-left: 1px solid rgba(255,255,255,0.15);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 3px;
    min-width: 0;
}}

.tbl-hero-item:last-child {{ padding-right: 2px; }}

.tbl-hero-k {{
    font-family: {_FS};
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.55);
    white-space: nowrap;
}}

.tbl-hero-v {{
    font-family: {_FS};
    font-size: 13px;
    font-weight: 600;
    color: #ffffff;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* ══════════════════════════════════════════════════════════════════
   COLUMNA IZQUIERDA — TARJETAS DE KPI
   ══════════════════════════════════════════════════════════════════ */
.tbl-panel-lateral {{
    margin: 7px;
    height: 506px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

/* Tarjeta genérica */
.tbl-card-base {{
    {_CARD}
    box-sizing: border-box;
    min-width: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 12px;
    text-align: center;
    position: relative;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}

.tbl-card-base {{
    transition: box-shadow 0.24s cubic-bezier(0.4,0,0.2,1),
                transform 0.24s cubic-bezier(0.4,0,0.2,1),
                border-color 0.24s ease;
}}

.tbl-card-base:hover {{
    border-color: rgba(46,125,70,0.30);
    box-shadow: {_SH2};
    transform: translateY(-2px);
}}

/* ── Encabezado icono + rótulo (patrón común) ── */
.tbl-head-row {{
    display: flex;
    align-items: center;
    gap: 9px;
    width: 100%;
    min-width: 0;
}}

.tbl-head-row .tbl-lbl {{
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.tbl-icon {{
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.tbl-icon.lg {{ width: 44px; height: 44px; }}
.tbl-icon.md {{ width: 36px; height: 36px; }}
.tbl-icon.sm {{ width: 28px; height: 28px; }}

.tbl-icon.green  {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%);  box-shadow: {_halo(_G)}; }}
.tbl-icon.dark   {{ background: linear-gradient(160deg, {_G} 0%, {_G2} 100%);      box-shadow: {_halo(_G2)}; }}
.tbl-icon.red    {{ background: linear-gradient(160deg, #D9584A 0%, {_R} 100%);   box-shadow: {_halo(_R)}; }}
.tbl-icon.slate  {{ background: linear-gradient(160deg, #7A8992 0%, #5C6B73 100%); box-shadow: {_halo('#5C6B73')}; }}

.tbl-card-base:hover .tbl-icon {{ transform: scale(1.05); }}
.tbl-icon {{ transition: transform 0.24s cubic-bezier(0.4,0,0.2,1); }}

.tbl-lbl {{
    font-family: {_FS};
    font-weight: 700;
    color: {_G2};
    letter-spacing: 0.6px;
    text-transform: uppercase;
    text-align: left;
    line-height: 1.2;
}}

.tbl-lbl.xl {{ font-size: 14px; }}
.tbl-lbl.lg {{ font-size: 13px; }}
.tbl-lbl.md {{ font-size: 11.5px; }}

/* ── Cifras ── */
.tbl-num {{
    font-family: {_FN};
    font-weight: 700;
    color: {_T};
    line-height: 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.5px;
}}

.tbl-num.xxl {{ font-size: 44px; }}
.tbl-num.xl  {{ font-size: 40px; }}
.tbl-num.lg  {{ font-size: 34px; }}
.tbl-num.md  {{ font-size: 30px; }}

.tbl-num.red   {{ color: {_R}; }}
.tbl-num.green {{ color: {_G}; }}
.tbl-num.gold  {{ color: {_Y}; }}

/* ── Tarjeta ALS EN FONDO ── */
.tbl-kpi-fondo-card {{
    {_CARD}
    background: {_glow(_G, 0.13)}, linear-gradient(180deg, {_G3} 0%, #ffffff 62%);
    padding: 12px 18px;
    border-left: 3px solid {_G2};
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    height: 142px;
    box-sizing: border-box;
}}

.tbl-fondo-left {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 4px;
    flex: 0 0 auto;
    max-width: 40%;
}}

/* ── Barras por sistema ALS ── */
.tbl-als-panel {{
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: center;
    gap: 6px;
    flex: 1 1 auto;
    min-width: 0;
}}

.tbl-mini-chart-container {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 12px;
    height: 96px;
}}

.tbl-mini-bar-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1 1 0;
    min-width: 0;
    height: 100%;
}}

.tbl-mini-bar-val {{
    font-family: {_FN};
    font-size: 12px;
    font-weight: 700;
    color: {_T};
    margin-bottom: 4px;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
    line-height: 1;
}}

.tbl-mini-bar-sub {{
    font-family: {_FS};
    font-size: 8.5px;
    font-weight: 600;
    color: {_T2};
    margin-top: 1px;
    white-space: nowrap;
}}

/* El hueco fija la línea base; la pila crece desde abajo */
.tbl-mini-bar-slot {{
    flex: 1;
    width: 100%;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    min-height: 0;
}}

.tbl-mini-bar-stack {{
    width: 100%;
    height: 100%;
    max-width: 78px;
    display: flex;
    flex-direction: column;
    border-radius: 5px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(31,70,32,0.16), inset 0 1px 0 rgba(255,255,255,0.35);
    min-height: 4px;
}}

.tbl-mini-bar-stack .seg {{ width: 100%; }}
.tbl-mini-bar-stack .seg.on   {{ background: linear-gradient(180deg, #4CA46A 0%, {_G} 100%); }}
.tbl-mini-bar-stack .seg.off  {{ background: #93A29A; }}
.tbl-mini-bar-stack .seg.fall {{ background: {_R}; }}

.tbl-mini-bar-label {{
    font-family: {_FS};
    font-size: 11px;
    font-weight: 700;
    color: {_G2};
    margin-top: 5px;
    letter-spacing: 0.3px;
    line-height: 1.1;
}}

/* Leyenda de la composición */
.tbl-als-leg {{
    display: flex;
    justify-content: center;
    gap: 13px;
    font-family: {_FS};
    font-size: 8.5px;
    font-weight: 600;
    color: {_T2};
    text-transform: uppercase;
    letter-spacing: 0.3px;
}}

.tbl-als-leg span {{ display: inline-flex; align-items: center; gap: 4px; }}

.tbl-als-leg i {{
    width: 8px;
    height: 8px;
    border-radius: 2px;
    display: inline-block;
}}

.tbl-als-leg i.on   {{ background: {_G}; }}
.tbl-als-leg i.off  {{ background: #93A29A; }}
.tbl-als-leg i.fall {{ background: {_R}; }}

/* ── Fila media: fallados | disponibles + activos/inactivos ── */
.tbl-grid-bottom {{
    display: flex;
    gap: 12px;
    height: 216px;
}}

.tbl-card-fallados {{
    background: {_glow(_R, 0.10)}, linear-gradient(180deg,#ffffff 0%,#FFFCFC 100%);
    width: 46%;
    height: 100%;
    justify-content: space-between;
    align-items: flex-start;
    padding: 12px 14px;
    border-color: rgba(192,57,43,0.24);
    border-left: 3px solid {_R};
    gap: 0;
    overflow: hidden;
    box-sizing: border-box;
}}

.tbl-card-fallados:hover {{ border-color: rgba(192,57,43,0.40); }}

.tbl-fallados-note {{
    font-family: {_FS};
    font-size: 8.5px;
    font-weight: 700;
    color: {_G2};
    line-height: 1.25;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin: 1px 0 2px;
}}

.tbl-fallados-atrib {{
    border-top: 1px solid {_BR};
    padding-top: 4px;
    margin-top: 4px;
    width: 100%;
    text-align: left;
}}

/* El último bloque no debe rozar el borde inferior de la tarjeta */
.tbl-fallados-atrib:last-child {{ padding-bottom: 2px; }}

.tbl-fallados-atrib-lbl {{
    font-family: {_FS};
    font-size: 8.5px;
    font-weight: 600;
    color: {_T2};
    text-transform: uppercase;
    letter-spacing: 0.4px;
    line-height: 1;
}}

.tbl-fallados-atrib-val {{
    font-family: {_FN};
    font-size: 16px;
    font-weight: 700;
    color: {_T};
    font-variant-numeric: tabular-nums;
    margin-top: 1px;
    line-height: 1.1;
}}

.tbl-col-operativos {{
    width: 54%;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
    height: 100%;
}}

.tbl-card-operativos {{
    background: {_glow(_G, 0.10)}, linear-gradient(180deg,#ffffff 0%,#FCFDFA 100%);
    height: 96px;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 12px 17px;
    gap: 12px;
    border-left: 3px solid {_G};
}}

.tbl-row-act-inact {{
    display: flex;
    gap: 12px;
    flex: 1;
}}

.tbl-card-sub .tbl-head-row {{
    flex-direction: column;
    align-items: flex-start;
    gap: 7px;
}}

.tbl-card-sub .tbl-lbl {{
    overflow: visible;
    text-overflow: clip;
}}

.tbl-card-sub {{
    flex: 1 1 0;
    min-width: 0;
    align-items: stretch;
    justify-content: center;
    padding: 13px 15px;
    gap: 8px;
}}

.tbl-card-sub .tbl-num {{ text-align: right; }}

/* ── Fila de medidores: disponibilidad y uso ── */
.tbl-row-meters {{
    display: flex;
    gap: 12px;
    height: 116px;
}}

.tbl-card-meter {{
    background: {_glow(_G2, 0.07)}, linear-gradient(180deg,#ffffff 0%,#FCFDFA 100%);
    flex: 1 1 0;
    min-width: 0;
    align-items: stretch;
    justify-content: center;
    padding: 14px 17px;
    gap: 10px;
    overflow: hidden;
}}

.tbl-meter-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}}

.tbl-meter-lbl {{
    font-family: {_FS};
    font-size: 12.5px;
    font-weight: 700;
    color: {_G2};
    letter-spacing: 0.6px;
    text-transform: uppercase;
    text-align: left;
    line-height: 1.2;
}}

.tbl-meter-pct {{
    font-family: {_FN};
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
    letter-spacing: -1px;
}}

.tbl-meter-track {{
    width: 100%;
    height: 14px;
    background: #E7E9E4;
    border-radius: 7px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(31,70,32,0.13);
}}

.tbl-meter-fill {{
    height: 100%;
    border-radius: 7px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.42);
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}}

.tbl-meter-fill.g {{ background: {_G}; }}
.tbl-meter-fill.y {{ background: {_Y}; }}
.tbl-meter-fill.r {{ background: {_R}; }}

/* ══════════════════════════════════════════════════════════════════
   TABLA DE FALLAS DEL MES
   ══════════════════════════════════════════════════════════════════ */
.tbl-fallas-panel {{
    {_CARD}
    margin: 7px;
    padding: 14px 16px;
    height: 316px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
}}

.tbl-fallas-head {{
    text-align: center;
    padding-bottom: 7px;
    margin-bottom: 7px;
    border-bottom: 1px solid {_BR};
}}

.tbl-fallas-title {{
    font-family: {_FS};
    font-size: 12.5px;
    font-weight: 700;
    color: {_G2};
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

.tbl-fallas-sub {{
    font-family: {_FS};
    font-size: 10px;
    font-weight: 500;
    color: {_T2};
    margin-top: 4px;
}}

.tbl-fallas-sub b {{
    font-family: {_FN};
    font-size: 14px;
    color: {_R};
}}

.tbl-ft {{
    width: 100%;
    border-collapse: collapse;
    font-family: {_FS};
    flex: 1;
}}

.tbl-ft th {{
    font-size: 10px;
    font-weight: 700;
    color: {_T2};
    text-transform: uppercase;
    letter-spacing: 0.4px;
    text-align: center;
    white-space: nowrap;
    padding: 0 4px 5px;
    border-bottom: 1px solid {_BR};
}}

.tbl-ft th.et {{ text-align: left; }}

.tbl-ft td {{
    font-family: {_FN};
    font-size: 17px;
    font-weight: 700;
    color: {_T2};
    text-align: center;
    padding: 3px 6px;
    font-variant-numeric: tabular-nums;
}}

.tbl-ft td .v {{
    display: inline-block;
    min-width: 34px;
    padding: 2px 8px;
    border-radius: 20px;
    line-height: 1.25;
}}

.tbl-ft td .v.hit {{
    color: {_R};
    background: {_R2};
}}

.tbl-ft td.et {{
    font-family: {_FS};
    font-size: 12px;
    font-weight: 700;
    color: {_G2};
    text-align: left;
    white-space: nowrap;
}}

.tbl-ft td.et span {{
    display: block;
    font-size: 8.5px;
    font-weight: 500;
    color: {_T2};
    margin-top: 1px;
}}

.tbl-ft tr.alt td {{ background: #F6F8F3; }}

.tbl-ft tr.tot td {{
    border-top: 1.5px solid {_BR};
    color: {_T};
    padding-top: 5px;
}}

.tbl-ft tr.tot td.et {{
    font-size: 12px;
    color: {_G2};
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

.tbl-fallas-foot {{
    font-family: {_FS};
    font-size: 8.5px;
    font-style: italic;
    color: {_T2};
    text-align: center;
    margin-top: 4px;
}}

/* ── Entrada suave de las cifras ── */
@keyframes tblFadeUp {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.tbl-num, .tbl-meter-pct {{
    animation: tblFadeUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) both;
}}
</style>
""", unsafe_allow_html=True)


# ── Taxonomía compartida de fallas ───────────────────────────────────────────
# Etapas de Run Life: se reutiliza el criterio canónico de core/calculations.py
# (Infantil <=30d, Prematura <=90d, En Garantía <=1100d, Sin Garantía >1100d)
RL_ETAPAS = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía']
RL_ETAPA_EJE = ['&lt; 30 d', '30 – 90 d', '90 – 1100 d', '&gt; 1100 d']
TIPOS_FALLA = ['ALS', 'No ALS', 'Pend Pulling']
TIPO_COLOR = {'ALS': _G, 'No ALS': _N, 'Pend Pulling': '#9FB6C9'}


def _pozos_on(df_f9, fecha):
    """Conjunto de pozos que reportaron días trabajados y producción de fluido > 0 en el mes de `fecha`."""
    if df_f9 is None or df_f9.empty or 'FECHA_FORMA9' not in df_f9.columns:
        return set()
    f9 = df_f9.copy()
    f9['_F9'] = pd.to_datetime(f9['FECHA_FORMA9'], errors='coerce')
    mask = (f9['_F9'].dt.month == fecha.month) & (f9['_F9'].dt.year == fecha.year)
    if 'DIAS TRABAJADOS' in f9.columns:
        mask = mask & (pd.to_numeric(f9['DIAS TRABAJADOS'], errors='coerce').fillna(0) > 0)
    
    fluid_cols = [c for c in f9.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
    if fluid_cols:
        mask_fluid = pd.Series(False, index=f9.index)
        for fc in fluid_cols:
            mask_fluid = mask_fluid | (pd.to_numeric(f9[fc], errors='coerce').fillna(0) > 0)
        mask = mask & mask_fluid

    return set(f9[mask]['POZO'].astype(str).str.strip().unique())


def _balance_pozos(df_bd, df_f9, fecha_ini, fecha_fin):
    """
    Balance de pozos ON entre dos cortes mensuales.

    La identidad Base + Nuevos + Reactivados − Fallados − Apagados = Final
    se cumple por construcción: los pozos que entran y salen del conjunto ON
    se clasifican de forma excluyente.
      · Nuevos      → entran y su primera corrida arranca dentro del periodo
      · Reactivados → entran y ya existían antes del periodo
      · Fallados    → salen y registran falla dentro del periodo
      · Apagados    → salen sin falla registrada
    """
    on_ini = _pozos_on(df_f9, fecha_ini)
    on_fin = _pozos_on(df_f9, fecha_fin)

    entrantes = on_fin - on_ini
    salientes = on_ini - on_fin

    primera_corrida, con_falla = {}, set()
    if df_bd is not None and not df_bd.empty and 'POZO' in df_bd.columns:
        bd = df_bd.copy()
        bd['_P'] = bd['POZO'].astype(str).str.strip()
        if 'FECHA_RUN' in bd.columns:
            primera_corrida = bd.groupby('_P')['FECHA_RUN'].min().to_dict()
        if 'FECHA_FALLA' in bd.columns:
            fallas = bd[bd['FECHA_FALLA'].notna()]
            fallas = fallas[
                (fallas['FECHA_FALLA'].dt.normalize() >= fecha_ini) &
                (fallas['FECHA_FALLA'].dt.normalize() <= fecha_fin)
            ]
            con_falla = set(fallas['_P'].unique())

    nuevos = {p for p in entrantes
              if pd.notna(primera_corrida.get(p)) and primera_corrida[p] >= fecha_ini}
    reactivados = entrantes - nuevos
    fallados = {p for p in salientes if p in con_falla}
    apagados = salientes - fallados

    return {
        'base':        len(on_ini),
        'nuevos':      len(nuevos),
        'reactivados': len(reactivados),
        'fallados':    len(fallados),
        'apagados':    len(apagados),
        'final':       len(on_fin),
    }


def _clasificar_fallas(df_bd, fecha_ini, fecha_fin):
    """
    Devuelve los eventos de falla del periodo con sus atributos:
      · ETAPA     → etapa de Run Life al momento de la falla (taxonomía del proyecto)
      · ES_ALS    → True si es falla imputable al sistema ALS (INDICADOR_MTBF == 1)
      · PEND_PULL → True si aún no se ha realizado la extracción a la fecha de corte (FECHA_PULL > fecha_fin o NaT)
    """
    vacio = pd.DataFrame(columns=['POZO', 'ETAPA', 'ES_ALS', 'PEND_PULL'])
    if df_bd is None or df_bd.empty or 'FECHA_FALLA' not in df_bd.columns:
        return vacio

    ev = df_bd[df_bd['FECHA_FALLA'].notna()].copy()
    ev = ev[
        (ev['FECHA_FALLA'].dt.normalize() >= fecha_ini) &
        (ev['FECHA_FALLA'].dt.normalize() <= fecha_fin)
    ]
    if ev.empty:
        return vacio

    rl_col = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in ev.columns), None)
    ev['ETAPA'] = (ev[rl_col].map(clasificar_runlife) if rl_col else 'N/A')

    # Pull realizado a la fecha de corte (fecha_fin)
    if 'FECHA_PULL' in ev.columns:
        pull_ok = ev['FECHA_PULL'].notna() & (ev['FECHA_PULL'].dt.normalize() <= fecha_fin)
    else:
        pull_ok = pd.Series(False, index=ev.index)

    es_als = (ev['INDICADOR_MTBF'] == 1) if 'INDICADOR_MTBF' in ev.columns else pd.Series(False, index=ev.index)

    ev['ES_ALS'] = es_als
    ev['PEND_PULL'] = ~pull_ok

    return ev[['POZO', 'ETAPA', 'ES_ALS', 'PEND_PULL']]


def _matriz_fallas(df_ev):
    """
    Matriz etapa × tipo de falla:
      · 'ALS': Total de fallas ALS (con o sin pull)
      · 'No ALS': Total de fallas No ALS (con o sin pull)
      · 'Pend Pulling': Cuántas de esas fallas todavía no tienen fecha de pull
    """
    matriz = {et: {'ALS': 0, 'No ALS': 0, 'Pend Pulling': 0} for et in RL_ETAPAS}
    if df_ev is None or df_ev.empty:
        return matriz
    for et in RL_ETAPAS:
        sub = df_ev[df_ev['ETAPA'] == et]
        if not sub.empty:
            matriz[et]['ALS'] = int((sub['ES_ALS'] == True).sum())
            matriz[et]['No ALS'] = int((sub['ES_ALS'] == False).sum())
            matriz[et]['Pend Pulling'] = int((sub['PEND_PULL'] == True).sum())
    return matriz


def render_tab_tablero(
    df_bd_filtered,
    df_forma9_filtered,
    reporte_runes_filtered,
    fecha_evaluacion,
    selected_activo,
):
    _css()

    fecha_eval_dt   = pd.to_datetime(fecha_evaluacion)
    fecha_eval_date = fecha_eval_dt.normalize()
    mes_eval        = fecha_eval_dt.month
    anio_eval       = fecha_eval_dt.year

    # Definir los filtros del sidebar para usarlos globalmente
    _filtros = {
        'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
        'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
        'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
        'PROVEEDOR': st.session_state.get('general_proveedor_filter', 'TODOS'),
        'NICK':      st.session_state.get('general_nick_filter',      'TODOS'),
    }

    # ── Ignorar fecha_ini y usar sólo fecha_evaluacion para el Tablero ──────
    df_raw = st.session_state.get('df_bd_calculated')
    if df_raw is not None:
        df_resumen = df_raw.copy()
        EXCLUIDOS = {
            'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
            'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
            'MAPACHE/PERICO', 'MAPACHE-PERICO',
            'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
            'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
            'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE'
        }
        for col_filter in ('ACTIVO', 'BLOQUE', 'CAMPO'):
            if col_filter in df_resumen.columns and EXCLUIDOS:
                df_resumen = df_resumen[~df_resumen[col_filter].astype(str).str.upper().str.strip().isin(EXCLUIDOS)]
        for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col in df_resumen.columns:
                df_resumen[col] = pd.to_datetime(df_resumen[col], errors='coerce')
        df_resumen = df_resumen[df_resumen['FECHA_RUN'].dt.normalize() <= fecha_eval_date].copy()
        df_resumen.loc[df_resumen['FECHA_FALLA'].dt.normalize() > fecha_eval_date, 'FECHA_FALLA'] = pd.NaT
        
        # Aplicar filtros del sidebar
        for col, val in _filtros.items():
            if val != 'TODOS' and col in df_resumen.columns:
                df_resumen = df_resumen[df_resumen[col] == val]
    else:
        df_resumen = df_bd_filtered.copy()
        for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col in df_resumen.columns:
                df_resumen[col] = pd.to_datetime(df_resumen[col], errors='coerce')

    df = df_resumen.copy()
    df['_RUN']  = df['FECHA_RUN'].dt.normalize()
    df['_FALL'] = df['FECHA_FALLA'].dt.normalize() if 'FECHA_FALLA' in df.columns else pd.Series(pd.NaT, index=df.index)
    df['_PULL'] = df['FECHA_PULL'].dt.normalize()  if 'FECHA_PULL'  in df.columns else pd.Series(pd.NaT, index=df.index)

    # ── ALS en fondo ─────────────────────────────────────────────────────────
    mask_fondo = (df['_RUN'] <= fecha_eval_date) & (df['_PULL'].isna() | (df['_PULL'] > fecha_eval_date))
    df_fondo = df[mask_fondo]
    als_fondo = df_fondo['POZO'].nunique() if 'POZO' in df_fondo.columns else 0

    # ── Fallados y operativos ────────────────────────────────────────────────
    df_falla = df_fondo[df_fondo['_FALL'].notna() & (df_fondo['_FALL'] <= fecha_eval_date)]
    als_fallados  = df_falla['POZO'].nunique() if 'POZO' in df_falla.columns else 0
    als_operativos = df_fondo[df_fondo['_FALL'].isna() | (df_fondo['_FALL'] > fecha_eval_date)]['POZO'].nunique() if 'POZO' in df_fondo.columns else 0

    # ── Activos / Inactivos ────
    df_f9_raw = st.session_state.get('df_forma9_calculated')
    if df_f9_raw is not None:
        df_forma9_untr = df_f9_raw.copy()
        df_forma9_untr['FECHA_FORMA9'] = pd.to_datetime(df_forma9_untr['FECHA_FORMA9'], errors='coerce')
        pozos_en_resumen = df_resumen['POZO'].unique() if 'POZO' in df_resumen.columns else []
        df_forma9_untr = df_forma9_untr[df_forma9_untr['POZO'].isin(pozos_en_resumen)].copy()
    else:
        df_forma9_untr = df_forma9_filtered.copy()

    df_f9 = df_forma9_untr.copy()
    df_f9 = df_f9[(df_f9['FECHA_FORMA9'].dt.month == mes_eval) & (df_f9['FECHA_FORMA9'].dt.year == anio_eval)]

    activos = inactivos = 0
    if not df_f9.empty and 'FECHA_FORMA9' in df_f9.columns:
        df_f9['_F9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
        dias_col  = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9.columns else None
        mask_on   = (df_f9['_F9'].dt.month == mes_eval) & (df_f9['_F9'].dt.year == anio_eval)
        if dias_col:
            mask_on = mask_on & (pd.to_numeric(df_f9[dias_col], errors='coerce').fillna(0) > 0)
        
        fluid_cols = [c for c in df_f9.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
        if fluid_cols:
            mask_fluid = pd.Series(False, index=df_f9.index)
            for fc in fluid_cols:
                mask_fluid = mask_fluid | (pd.to_numeric(df_f9[fc], errors='coerce').fillna(0) > 0)
            mask_on = mask_on & mask_fluid

        pozos_on  = set(df_f9[mask_on]['POZO'].astype(str).str.strip().unique())
        
        activos   = len(pozos_on)
        inactivos = max(0, als_operativos - activos)
    else:
        pozos_on  = set()
        activos   = als_operativos
        inactivos = 0

    # ── Composición por tipo de ALS ──────────────────────────────────────────
    # Cada sistema se descompone en encendidos (reportan días trabajados en el
    # mes), apagados (operativos pero sin producción) y fallados en fondo.
    als_breakdown = {}
    if 'ALS' in df_fondo.columns and 'POZO' in df_fondo.columns:
        for t in ALS_TIPOS:
            sub = df_fondo[df_fondo['ALS'].astype(str).str.strip().str.upper() == t]
            pozos_t = set(sub['POZO'].astype(str).str.strip().unique())
            fallados_t = set(
                sub[sub['_FALL'].notna() & (sub['_FALL'] <= fecha_eval_date)]['POZO']
                .astype(str).str.strip().unique()
            )
            operativos_t = pozos_t - fallados_t
            on_t  = len(operativos_t & pozos_on)
            off_t = len(operativos_t) - on_t
            als_breakdown[t] = {
                'total': len(pozos_t),
                'on':    on_t,
                'off':   off_t,
                'fall':  len(fallados_t),
            }
    else:
        als_breakdown = {t: {'total': 0, 'on': 0, 'off': 0, 'fall': 0} for t in ALS_TIPOS}

    total_pozos  = max(activos + inactivos, 1)
    disp_oper    = activos   / total_pozos * 100
    uso_oper     = als_operativos / max(als_fondo, 1) * 100

    # ── Serie IF mensual ─
    if_cats, if_vals, if_tot_vals, on_vals, off_vals = [], [], [], [], []
    if_actual = 0.0

    try:
        from indice_falla import calcular_indice_falla_anual
        _, df_mensual_if = calcular_indice_falla_anual(
            df.copy(), df_forma9_untr.copy(), fecha_evaluacion, st.session_state.get('fecha_inicio_state')
        )

        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        df_yr = df_mensual_if.tail(12).copy()

        for _, row in df_yr.iterrows():
            m_str = row['Mes']
            m_idx = int(m_str[5:7]) - 1
            label = f"{_MESES[m_idx]}-{m_str[2:4]}"
            if_cats.append(label)
            on_m   = int(row.get('Pozos ON', 0))
            if_roll = float(row.get('Indice_Falla_Rolling_ALS_ON_1500', row.get('Indice_Falla_Rolling_ALS_Total', 0.0))) * 100.0
            if_vals.append(if_roll)
            
            if_tot_roll = float(row.get('Indice_Falla_Rolling_ON_1500', row.get('Indice_Falla_Rolling_Total', 0.0))) * 100.0
            if_tot_vals.append(if_tot_roll)
            
            on_vals.append(on_m)
            off_m  = max(int(row.get('Pozos Operativos', on_m)) - on_m, 0)
            off_vals.append(off_m)

        last_row = df_mensual_if.tail(1)
        if not last_row.empty:
            if_actual = float(last_row['Indice_Falla_Rolling_ALS_ON_1500'].iloc[0]) * 100.0
        elif if_vals:
            if_actual = if_vals[-1]

    except Exception as _e_if:
        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        from dateutil.relativedelta import relativedelta
        start_m = fecha_eval_dt - relativedelta(months=11)
        for i in range(12):
            curr_date = start_m + relativedelta(months=i)
            m = curr_date.month
            y = curr_date.year
            last_day = calendar.monthrange(y, m)[1]
            end_m_ts = pd.Timestamp(year=y, month=m, day=last_day).normalize()
            fallas_m = int(df[
                (df['_FALL'].dt.month == m) & (df['_FALL'].dt.year == y)
            ].shape[0])
            fallas_als_m = int(df[
                (df['_FALL'].dt.month == m) & (df['_FALL'].dt.year == y) & (df['INDICADOR_MTBF'] == 1)
            ].shape[0]) if 'INDICADOR_MTBF' in df.columns else fallas_m
            
            on_m = 0
            if not df_forma9_untr.empty and 'FECHA_FORMA9' in df_forma9_untr.columns:
                df_f9c = df_forma9_untr.copy()
                df_f9c['_F9'] = pd.to_datetime(df_f9c['FECHA_FORMA9'], errors='coerce').dt.normalize()
                dias_c = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9c.columns else None
                mm = (df_f9c['_F9'].dt.month == m) & (df_f9c['_F9'].dt.year == y)
                if dias_c:
                    mm = mm & (pd.to_numeric(df_f9c[dias_c], errors='coerce').fillna(0) > 0)
                fluid_cols_c = [c for c in df_f9c.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
                if fluid_cols_c:
                    mask_f_c = pd.Series(False, index=df_f9c.index)
                    for fc in fluid_cols_c:
                        mask_f_c = mask_f_c | (pd.to_numeric(df_f9c[fc], errors='coerce').fillna(0) > 0)
                    mm = mm & mask_f_c
                on_m = int(df_f9c[mm]['POZO'].nunique())
            op_m = int(df[
                (df['_RUN'] <= end_m_ts) &
                (df['_FALL'].isna() | (df['_FALL'] > end_m_ts)) &
                (df['_PULL'].isna() | (df['_PULL'] > end_m_ts))
            ]['POZO'].nunique()) if 'POZO' in df.columns else 0
            if_cats.append(f"{_MESES[m - 1]}-{str(y)[2:4]}")
            
            if_m = (fallas_als_m / max(op_m, 1)) * 100.0
            if_vals.append(if_m)
            
            if_tot_m = (fallas_m / max(op_m, 1)) * 100.0
            if_tot_vals.append(if_tot_m)
            
            on_vals.append(on_m)
            off_vals.append(max(op_m - on_m, 0))
        if_actual = if_vals[-1] if if_vals else 0.0

    if_max = max(max(if_vals + if_tot_vals) * 1.3, META_IF * 2, 20) if (if_vals and if_tot_vals) else 20

    # ── MTBF ─────────────────────────────────────────────────────────────────
    try:
        mtbf_val, _ = mtbf_mod.calcular_mtbf(df, fecha_evaluacion)
        mtbf_val = float(mtbf_val) if mtbf_val and not np.isnan(mtbf_val) else 0.0
    except Exception:
        mtbf_val = 0.0

    # ── RunLife promedio ──────────────────────────────────────────────────────
    rl_col = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in df.columns), None)
    rl_val = float(df[rl_col].dropna().mean()) if rl_col else 0.0
    if np.isnan(rl_val):
        rl_val = 0.0

    # ── Calcular metas dinámicas para el Campo/Activo seleccionado ──────────
    anio_prev = anio_eval - 1
    fecha_prev_fin = pd.to_datetime(f"{anio_prev}-12-31").normalize()

    mtbf_prev_val = 0.0
    rl_prev_val = 0.0

    df_raw = st.session_state.get('df_bd_calculated')
    if df_raw is not None:
        df_prev = df_raw.copy()
        EXCLUIDOS = {
            'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
            'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
            'MAPACHE/PERICO', 'MAPACHE-PERICO',
            'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
            'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
            'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE'
        }
        for col_filter in ('ACTIVO', 'BLOQUE', 'CAMPO'):
            if col_filter in df_prev.columns and EXCLUIDOS:
                df_prev = df_prev[~df_prev[col_filter].astype(str).str.upper().str.strip().isin(EXCLUIDOS)]
        for col_dt in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col_dt in df_prev.columns:
                df_prev[col_dt] = pd.to_datetime(df_prev[col_dt], errors='coerce')
        
        # Filtro hasta el último día del año anterior
        df_prev = df_prev[df_prev['FECHA_RUN'].dt.normalize() <= fecha_prev_fin].copy()
        df_prev.loc[df_prev['FECHA_FALLA'].dt.normalize() > fecha_prev_fin, 'FECHA_FALLA'] = pd.NaT
        
        # Aplicar los mismos filtros que en la pestaña actual
        for col_f, val_f in _filtros.items():
            if val_f != 'TODOS' and col_f in df_prev.columns:
                df_prev = df_prev[df_prev[col_f] == val_f]
        
        # Calcular MTBF a fecha_prev_fin
        try:
            mtbf_p, _ = mtbf_mod.calcular_mtbf(df_prev, f"{anio_prev}-12-31")
            mtbf_prev_val = float(mtbf_p) if mtbf_p and not np.isnan(mtbf_p) else 0.0
        except Exception:
            mtbf_prev_val = 0.0
            
        # Calcular Run Life de los pozos fallados a fecha_prev_fin
        df_prev_fallados = df_prev[df_prev['FECHA_FALLA'].notna()]
        rl_col_prev = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in df_prev.columns), None)
        if not df_prev_fallados.empty and rl_col_prev:
            rl_prev_val = float(df_prev_fallados[rl_col_prev].dropna().mean())
        else:
            df_fallados_all = df_resumen[df_resumen['FECHA_FALLA'].notna()] if df_resumen is not None else pd.DataFrame()
            rl_col_res = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in df_fallados_all.columns), None)
            rl_prev_val = float(df_fallados_all[rl_col_res].dropna().mean()) if not df_fallados_all.empty and rl_col_res else float(META_RL)
        if np.isnan(rl_prev_val) or rl_prev_val <= 0:
            rl_prev_val = float(META_RL)

    meta_mtbf_calc = round(mtbf_prev_val) if mtbf_prev_val > 0 else META_MTBF
    meta_rl_calc = round(rl_prev_val) if rl_prev_val > 0 else META_RL

    # ── Correlación de Producción vs Longevidad (para el gráfico de desempeño en Columna 3) ──
    rl_bins   = ['< 2 años', '2 – 4 años', '4 – 6 años', '> 6 años']
    pozos_perf_data = [0, 0, 0, 0]
    bopd_perf_data = [0.0, 0.0, 0.0, 0.0]
    try:
        df_f9_perf = df_forma9_untr.copy()
        df_f9_perf['FECHA_FORMA9'] = pd.to_datetime(df_f9_perf.get('FECHA_FORMA9'), errors='coerce')
        df_month_perf = df_f9_perf[
            (df_f9_perf['FECHA_FORMA9'].dt.year == anio_eval) & 
            (df_f9_perf['FECHA_FORMA9'].dt.month == mes_eval)
        ].copy()
        
        bopd_col = next((c for c in df_month_perf.columns if 'BOPD' in str(c).upper() or 'PETROLEO DIA' in str(c).upper() or 'PETROLEO_DIA' in str(c).upper()), None)
        dias_c_perf = next((c for c in df_month_perf.columns if 'DIAS' in str(c).upper()), None)
        mask_dias_perf = (pd.to_numeric(df_month_perf[dias_c_perf], errors='coerce').fillna(0) > 0) if dias_c_perf else pd.Series(True, index=df_month_perf.index)
        fluid_cols_perf = [c for c in df_month_perf.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
        if fluid_cols_perf:
            mask_f_perf = pd.Series(False, index=df_month_perf.index)
            for fc in fluid_cols_perf:
                mask_f_perf = mask_f_perf | (pd.to_numeric(df_month_perf[fc], errors='coerce').fillna(0) > 0)
        else:
            mask_f_perf = pd.Series(True, index=df_month_perf.index)

        df_on_perf = df_month_perf[mask_dias_perf & mask_f_perf].copy()
        if bopd_col and not df_on_perf.empty:
            df_on_perf[bopd_col] = pd.to_numeric(df_on_perf[bopd_col], errors='coerce').fillna(0)
            df_sum_perf = df_on_perf.groupby('POZO', as_index=False).agg({bopd_col: 'mean'}) 
            df_sum_perf.rename(columns={bopd_col: 'BOPD'}, inplace=True)
        else:
            df_sum_perf = pd.DataFrame(columns=['POZO', 'BOPD'])
        
        bd_perf = df_resumen.copy()
        
        results_perf = []
        for _, row in df_sum_perf.iterrows():
            pozo = row['POZO']
            bopd = row['BOPD']
            pozo_data = bd_perf[bd_perf['POZO'] == pozo].sort_values('FECHA_RUN', ascending=False)
            if not pozo_data.empty:
                rl = pozo_data.iloc[0].get('RUN LIFE', 0)
                years = rl / 365.25 if rl else 0
                if years < 2: rango = '< 2 años'
                elif years < 4: rango = '2 – 4 años'
                elif years < 6: rango = '4 – 6 años'
                else: rango = '> 6 años'
                results_perf.append({'POZO': pozo, 'BOPD': bopd, 'RUN_LIFE': rl, 'RANGO': rango})

        if results_perf:
            df_perf_res = pd.DataFrame(results_perf)
            df_range_perf = df_perf_res.groupby('RANGO').agg({'POZO': 'count', 'BOPD': 'sum'}).reindex(rl_bins).fillna(0)
            pozos_perf_data = [int(x) for x in df_range_perf['POZO'].tolist()]
            bopd_perf_data = [round(float(x), 1) for x in df_range_perf['BOPD'].tolist()]
    except Exception as _e_perf:
        pass

    # Construir datos coloreados para mantener la estética de barra individual anterior
    # Rampa semántica plana por rango de RunLife (verde = joven, rojo = longevo)
    _RL_COLORS = [_G, _G2, _Y, _R]
    pozos_perf_colored = [
        {
            "value": pozos_perf_data[i],
            "itemStyle": {"color": _RL_COLORS[i], "borderRadius": [5, 5, 0, 0],
                          "shadowBlur": 8, "shadowOffsetY": 3,
                          "shadowColor": "rgba(31,70,32,0.22)"}
        }
        for i in range(4)
    ]

    mtbf_max = max(mtbf_val * 1.4, meta_mtbf_calc * 1.5, 3000)
    rl_max   = max(rl_val   * 1.4, meta_rl_calc * 1.5, 2500)

    # ── Ventana del periodo (usada por el encabezado y los paneles inferiores) ─
    fecha_ini_str = st.session_state.get('fecha_inicio_state')
    if fecha_ini_str is not None:
        fecha_ini_dt = pd.to_datetime(fecha_ini_str).normalize()
    else:
        fecha_ini_dt = fecha_eval_date - pd.DateOffset(years=1)

    # ── Balance de pozos ON del periodo (waterfall) ───────────────────────────
    try:
        balance = _balance_pozos(df_resumen, df_forma9_untr, fecha_ini_dt, fecha_eval_date)
    except Exception:
        balance = {'base': 0, 'nuevos': 0, 'reactivados': 0,
                   'fallados': 0, 'apagados': 0, 'final': 0}

    # ── Fallas del periodo y del mes en curso, por etapa y tipo ───────────────
    try:
        ev_periodo = _clasificar_fallas(df_resumen, fecha_ini_dt, fecha_eval_date)
    except Exception:
        ev_periodo = pd.DataFrame(columns=['POZO', 'ETAPA', 'TIPO'])
    try:
        ini_mes = pd.Timestamp(year=anio_eval, month=mes_eval, day=1).normalize()
        ev_mes = _clasificar_fallas(df_resumen, ini_mes, fecha_eval_date)
    except Exception:
        ev_mes = pd.DataFrame(columns=['POZO', 'ETAPA', 'TIPO'])

    mat_periodo = _matriz_fallas(ev_periodo)
    mat_mes     = _matriz_fallas(ev_mes)

    # Series apiladas para el gráfico de fallas por antigüedad
    series_antig = {t: [mat_periodo[et][t] for et in RL_ETAPAS] for t in TIPOS_FALLA}
    tot_mes      = {t: sum(mat_mes[et][t] for et in RL_ETAPAS) for t in TIPOS_FALLA}

    _MESES_LARGO = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
                    'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    fecha_corte_lbl = f"{fecha_eval_dt.day} de {_MESES_LARGO[mes_eval - 1]} de {anio_eval}"
    mes_curso_lbl   = f"{_MESES_LARGO[mes_eval - 1].capitalize()} {anio_eval}"

    # Migas de pan con los filtros activos del sidebar
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"

    # ── Alcance del análisis (contexto que no se repite en ningún panel) ──────
    def _n_unicos(col):
        return int(df_resumen[col].nunique()) if col in df_resumen.columns else 0

    n_bloques  = _n_unicos('BLOQUE')
    n_campos   = _n_unicos('CAMPO')
    n_corridas = int(len(df_resumen))

    _MES_CORTO = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
                  'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
    periodo_lbl = (f"{_MES_CORTO[fecha_ini_dt.month - 1]} {fecha_ini_dt.year} — "
                   f"{_MES_CORTO[mes_eval - 1]} {anio_eval}")

    # ═════════════════════════════════════════════════════════════════════════
    # ENCABEZADO EJECUTIVO
    # Sólo contexto y alcance: las cifras de KPI viven en sus propios paneles y
    # no se repiten aquí.
    # ═════════════════════════════════════════════════════════════════════════
    hero_html = f"""
<div class="tbl-hero">
  <div class="tbl-hero-brand">
    <div class="tbl-hero-mark">
      <svg viewBox="0 0 100 100" width="27" height="27" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="73" width="80" height="6" fill="#ffffff" opacity="0.95"/>
        <path d="M35 73 L47.5 30 L52.5 30 L65 73 H59 L50 42 L41 73 Z" fill="#ffffff" opacity="0.95"/>
        <path d="M27.5 20.5 L73 31.5 L71.5 36.5 L26 25.5 Z" fill="#ffffff" opacity="0.8"/>
        <path d="M72 31.5 C75 22.5 83 23 85 32 C86.5 38 85.5 45.5 84 52.5 L79.5 52.5 C81.5 46.5 81.5 37 77.5 33 Z" fill="#ffffff" opacity="0.8"/>
        <line x1="27" y1="23" x2="11" y2="52" stroke="#ffffff" stroke-width="2.4" opacity="0.8"/>
        <circle cx="27" cy="23" r="3" fill="#ffffff"/>
      </svg>
    </div>
    <div>
      <div class="tbl-hero-kicker">Levantamiento Artificial · Parex</div>
      <div class="tbl-hero-title">Tablero Ejecutivo ALS</div>
    </div>
  </div>

  <div class="tbl-hero-ctx">
    <div class="tbl-hero-item">
      <span class="tbl-hero-k">Alcance</span>
      <span class="tbl-hero-v"><span class="tbl-hero-dot"></span>{_activos_lbl}</span>
    </div>
    <div class="tbl-hero-item">
      <span class="tbl-hero-k">Periodo evaluado</span>
      <span class="tbl-hero-v">{periodo_lbl}</span>
    </div>
    <div class="tbl-hero-item">
      <span class="tbl-hero-k">Cobertura</span>
      <span class="tbl-hero-v">{n_bloques} bloques · {n_campos} campos</span>
    </div>
    <div class="tbl-hero-item">
      <span class="tbl-hero-k">Corridas analizadas</span>
      <span class="tbl-hero-v">{_fmt(n_corridas)}</span>
    </div>
    <div class="tbl-hero-item">
      <span class="tbl-hero-k">Fecha de corte</span>
      <span class="tbl-hero-v">{fecha_corte_lbl}</span>
    </div>
  </div>
</div>
""".replace("\n", " ")

    st.markdown(hero_html, unsafe_allow_html=True)
    # ═════════════════════════════════════════════════════════════════════════
    # LAYOUT DE 3 COLUMNAS SIMÉTRICAS
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1, 1], gap="medium")

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 1: KPIs OPERATIVOS (RENDERIZADO HTML COMPLETO)
    # ─────────────────────────────────────────────────────────────────────────
    with col_l:
        fallas_als = int((df_resumen['INDICADOR_MTBF'] == 1).sum()) if df_resumen is not None else 0
        
        if df_resumen is not None and not df_resumen.empty:
            df_period = df_resumen[
                (df_resumen['FECHA_FALLA'].notna()) &
                (df_resumen['FECHA_FALLA'].dt.normalize() >= fecha_ini_dt) &
                (df_resumen['FECHA_FALLA'].dt.normalize() <= fecha_eval_date)
            ]
            fallas_totales = int(df_period.shape[0])
            pozos_fallados_periodo = int(df_period['POZO'].nunique()) if not df_period.empty else 0
            
            limit_365 = fecha_eval_date - pd.Timedelta(days=365)
            df_recent = df_resumen[df_resumen['FECHA_FALLA'] >= limit_365]
            pozos_fallados_rec = df_recent['POZO'].nunique() if not df_recent.empty else 0
            idx_sev = (len(df_recent) / pozos_fallados_rec) if pozos_fallados_rec > 0 else 0.0
        else:
            fallas_totales = 0
            pozos_fallados_periodo = 0
            idx_sev = 0.0

        # ── Barras por sistema ALS: encendidos / apagados / fallados ─────────
        # Cada barra ocupa el alto completo y muestra la COMPOSICIÓN del sistema.
        # Escalarlas por tamaño absoluto no sirve: ESP tiene ~1.000 pozos y EPCP
        # puede tener 1, con lo que las pequeñas desaparecerían.
        _tipos_vis = [t for t in ALS_TIPOS if als_breakdown.get(t, {}).get('total', 0) > 0]

        mini_bars_html = ""
        for t in _tipos_vis:
            bd = als_breakdown[t]
            tot = bd['total']
            pct = lambda n: (n / tot * 100) if tot else 0
            mini_bars_html += (
                f'<div class="tbl-mini-bar-col">'
                f'<div class="tbl-mini-bar-val">{_fmt(bd["on"])}</div>'
                f'<div class="tbl-mini-bar-slot">'
                f'<div class="tbl-mini-bar-stack" '
                f'title="{t} · {_fmt(tot)} pozos: {bd["on"]} encendidos, '
                f'{bd["off"]} apagados, {bd["fall"]} fallados">'
                f'<div class="seg fall" style="height:{pct(bd["fall"]):.1f}%;"></div>'
                f'<div class="seg off"  style="height:{pct(bd["off"]):.1f}%;"></div>'
                f'<div class="seg on"   style="height:{pct(bd["on"]):.1f}%;"></div>'
                f'</div>'
                f'</div>'
                f'<div class="tbl-mini-bar-label">{t}</div>'
                f'<div class="tbl-mini-bar-sub">de {_fmt(tot)}</div>'
                f'</div>'
            )

        _leyenda_als = (
            '<div class="tbl-als-leg">'
            '<span><i class="on"></i>Encendidos</span>'
            '<span><i class="off"></i>Apagados</span>'
            '<span><i class="fall"></i>Fallados</span>'
            '</div>'
        )

        # Color del medidor según cumplimiento
        _disp_cls = 'g' if disp_oper >= 80 else ('y' if disp_oper >= 60 else 'r')
        _uso_cls  = 'g' if uso_oper  >= 80 else ('y' if uso_oper  >= 60 else 'r')
        _disp_col = _G if disp_oper >= 80 else (_Y if disp_oper >= 60 else _R)
        _uso_col  = _G if uso_oper  >= 80 else (_Y if uso_oper  >= 60 else _R)

        _SVG_ALERTA = ('<svg viewBox="0 0 24 24" width="22" height="22">'
                       '<polygon points="12,3 22,20 2,20" fill="none" stroke="#fff" stroke-width="1.9" stroke-linejoin="round"/>'
                       '<line x1="12" y1="9.5" x2="12" y2="14.5" stroke="#fff" stroke-width="1.9" stroke-linecap="round"/>'
                       '<circle cx="12" cy="17.3" r="1.1" fill="#fff"/></svg>')
        _SVG_CHECK  = ('<svg viewBox="0 0 24 24" width="20" height="20">'
                       '<circle cx="12" cy="12" r="9.3" fill="none" stroke="#fff" stroke-width="1.9"/>'
                       '<path d="M8 12.4l2.6 2.6 5.4-5.4" fill="none" stroke="#fff" stroke-width="2" '
                       'stroke-linecap="round" stroke-linejoin="round"/></svg>')
        _SVG_PLAY   = ('<svg viewBox="0 0 24 24" width="17" height="17">'
                       '<circle cx="12" cy="12" r="9.3" fill="none" stroke="#fff" stroke-width="2"/>'
                       '<path d="M10 8.4l6.2 3.6-6.2 3.6z" fill="#fff"/></svg>')
        _SVG_PAUSA  = ('<svg viewBox="0 0 24 24" width="17" height="17">'
                       '<circle cx="12" cy="12" r="9.3" fill="none" stroke="#fff" stroke-width="2"/>'
                       '<rect x="9" y="8.4" width="2.2" height="7.2" fill="#fff"/>'
                       '<rect x="12.8" y="8.4" width="2.2" height="7.2" fill="#fff"/></svg>')

        kpi_panel_html = f"""
<div class="tbl-panel-lateral">

  <!-- ALS EN FONDO -->
  <div class="tbl-kpi-fondo-card">
    <div class="tbl-fondo-left">
      <div class="tbl-head-row">
        <div class="tbl-icon lg dark">
          <svg viewBox="0 0 100 100" width="27" height="27" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="73" width="80" height="6" fill="#ffffff"/>
            <path d="M35 73 L47.5 30 L52.5 30 L65 73 H59 L50 42 L41 73 Z" fill="#ffffff"/>
            <path d="M27.5 20.5 L73 31.5 L71.5 36.5 L26 25.5 Z" fill="#ffffff" opacity="0.85"/>
            <path d="M72 31.5 C75 22.5 83 23 85 32 C86.5 38 85.5 45.5 84 52.5 L79.5 52.5 C81.5 46.5 81.5 37 77.5 33 Z" fill="#ffffff" opacity="0.85"/>
            <line x1="27" y1="23" x2="11" y2="52" stroke="#ffffff" stroke-width="2.6" opacity="0.85"/>
            <circle cx="27" cy="23" r="3.2" fill="#ffffff"/>
          </svg>
        </div>
        <div class="tbl-lbl xl">ALS en fondo</div>
      </div>
      <div class="tbl-num xxl">{_fmt(als_fondo)}</div>
    </div>

    <div class="tbl-als-panel">
      <div class="tbl-mini-chart-container">
        {mini_bars_html}
      </div>
      {_leyenda_als}
    </div>
  </div>

  <div class="tbl-grid-bottom">

    <!-- ALS FALLADOS -->
    <div class="tbl-card-base tbl-card-fallados">
      <div class="tbl-head-row">
        <div class="tbl-icon md red">{_SVG_ALERTA}</div>
        <div class="tbl-lbl lg">ALS fallados</div>
      </div>
      <div class="tbl-num xl red" style="margin: 2px 0; font-size: 32px; line-height: 1;">{_fmt(als_fallados)}</div>
      <div class="tbl-fallados-note">Pozos en fondo a espera de pull</div>

      <div class="tbl-fallados-atrib">
        <div class="tbl-fallados-atrib-lbl">Fallas / pozos fallados</div>
        <div class="tbl-fallados-atrib-val">{fallas_totales} / {pozos_fallados_periodo}</div>
      </div>
      <div class="tbl-fallados-atrib">
        <div class="tbl-fallados-atrib-lbl">Índice de severidad</div>
        <div class="tbl-fallados-atrib-val">{_fmt(idx_sev, 2)}</div>
      </div>
    </div>

    <!-- DISPONIBLES / ACTIVOS / INACTIVOS -->
    <div class="tbl-col-operativos">

      <div class="tbl-card-base tbl-card-operativos">
        <div class="tbl-head-row" style="width:auto;">
          <div class="tbl-icon md green">{_SVG_CHECK}</div>
          <div class="tbl-lbl lg">ALS disponibles</div>
        </div>
        <div class="tbl-num lg">{_fmt(als_operativos)}</div>
      </div>

      <div class="tbl-row-act-inact">

        <div class="tbl-card-base tbl-card-sub">
          <div class="tbl-head-row">
            <div class="tbl-icon sm green">{_SVG_PLAY}</div>
            <div class="tbl-lbl md">Activos</div>
          </div>
          <div class="tbl-num md">{_fmt(activos)}</div>
        </div>

        <div class="tbl-card-base tbl-card-sub">
          <div class="tbl-head-row">
            <div class="tbl-icon sm slate">{_SVG_PAUSA}</div>
            <div class="tbl-lbl md">Inactivos</div>
          </div>
          <div class="tbl-num md">{_fmt(inactivos)}</div>
        </div>

      </div>

    </div>

  </div>

  <!-- DISPONIBILIDAD / USO OPERATIVO -->
  <div class="tbl-row-meters">

    <div class="tbl-card-base tbl-card-meter">
      <div class="tbl-meter-top">
        <div class="tbl-meter-lbl">Disponibilidad<br/>operacional</div>
        <div class="tbl-meter-pct" style="color:{_disp_col};">{disp_oper:.0f}%</div>
      </div>
      <div class="tbl-meter-track">
        <div class="tbl-meter-fill {_disp_cls}" style="width:{min(disp_oper, 100):.0f}%;"></div>
      </div>
    </div>

    <div class="tbl-card-base tbl-card-meter">
      <div class="tbl-meter-top">
        <div class="tbl-meter-lbl">Uso<br/>operativo</div>
        <div class="tbl-meter-pct" style="color:{_uso_col};">{uso_oper:.0f}%</div>
      </div>
      <div class="tbl-meter-track">
        <div class="tbl-meter-fill {_uso_cls}" style="width:{min(uso_oper, 100):.0f}%;"></div>
      </div>
    </div>

  </div>

</div>
""".replace("\n", " ")

        st.markdown(kpi_panel_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 2: GAUGE IF + TENDENCIA ANUAL
    # ─────────────────────────────────────────────────────────────────────────
    with col_c:
        col2_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('{_FONTS_URL}');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: {_FS};
            overflow: hidden;
            padding: 7px;
        }}
        .tbl-panel {{
            {_CARD}
            padding: 18px;
            height: 506px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-sec-title {{
            font-family: {_FS};
            font-size: 14px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid {_BR};
        }}
        .tbl-live-dot {{
            flex: 1;
            height: 2px;
            background: {_G};
            opacity: 0.20;
            border-radius: 2px;
        }}
        .chart-container {{
            width: 100%;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Índice de Falla (I.F. ALS &lt;1500) <span class="tbl-live-dot"></span></div>
        <div id="gauge_if" class="chart-container" style="height: 192px;"></div>
        <div id="chart_if_anual" class="chart-container" style="height: 234px;"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var value = {if_actual};
            var meta = {META_IF};
            var maxVal = {if_max};
            var metaPct = meta / maxVal;
            
            var arcColors = [[metaPct, "{_G}"], [1.0, "{_R}"]];
            var valColor = (value <= meta) ? "{_G}" : "{_R}";
            
            var gaugeOpt = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 1200,
                animationEasing: "cubicOut",
                series: [{{
                    type: "gauge",
                    startAngle: 205,
                    endAngle: -25,
                    min: 0,
                    max: maxVal,
                    center: ["50%", "58%"],
                    radius: "90%",
                    splitNumber: 4,
                    axisLine: {{
                        roundCap: true,
                        lineStyle: {{
                            width: 22,
                            color: arcColors
                        }}
                    }},
                    progress: {{
                        show: false
                    }},
                    pointer: {{
                        itemStyle: {{ color: "{_T}" }},
                        width: 5,
                        length: "66%"
                    }},
                    axisTick: {{ show: false }},
                    splitLine: {{ show: false }},
                    axisLabel: {{ show: false }},
                    anchor: {{
                        show: true,
                        showAbove: true,
                        size: 8,
                        itemStyle: {{
                            borderWidth: 2,
                            borderColor: "{_T}",
                            color: "#fff"
                        }}
                    }},
                    detail: {{
                        valueAnimation: true,
                        formatter: function(val) {{ return val.toFixed(2).replace(".", ",") + "%"; }},
                        color: valColor,
                        fontSize: 38,
                        fontWeight: "700",
                        fontFamily: "Source Serif 4, Cambria, Georgia, serif",
                        offsetCenter: [0, "22%"],
                        borderRadius: 4,
                        padding: [4, 8]
                    }},
                    title: {{
                        show: true,
                        offsetCenter: [0, "52%"],
                        color: "{_T2}",
                        fontSize: 13,
                        fontWeight: "700",
                        fontFamily: "Inter, Segoe UI, sans-serif"
                    }},
                    data: [{{ value: value, name: "Meta IF: ≤ {_fmt(META_IF, 1)}%" }}]
                }}]
            }};
            
            var chartG = echarts.init(document.getElementById('gauge_if'));
            chartG.setOption(gaugeOpt);

            var trendOpt = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 900,
                animationEasing: "cubicOut",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "cross", crossStyle: {{ color: "rgba(46,125,70,0.3)" }} }},
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(46,125,70,0.2)",
                    borderWidth: 1,
                    borderRadius: 10,
                    padding: [8, 12],
                    textStyle: {{ color: "{_T}", fontSize: 12.5, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    extraCssText: "box-shadow: 0 4px 16px rgba(46,125,70,0.12);"
                }},
                legend: {{
                    data: ["Pozos ON", "Pozos OFF", "IF ALS", "IF Total"],
                    bottom: 0,
                    itemHeight: 8,
                    itemWidth: 14,
                    itemGap: 16,
                    textStyle: {{ color: "{_T2}", fontSize: 11.5, fontFamily: "Inter, Segoe UI, sans-serif" }}
                }},
                grid: {{ top: "16%", left: "3%", right: "9%", bottom: "18%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(if_cats)},
                    axisLabel: {{ color: "{_T2}", fontSize: 11, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: [
                    {{
                        type: "value",
                        name: "Pozos",
                        nameTextStyle: {{ color: "{_T2}", fontSize: 10.5 }},
                        axisLabel: {{ color: "{_T2}", fontSize: 11,
                            formatter: function(v) {{ return v.toLocaleString("es-CO"); }} }},
                        splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }}
                    }},
                    {{
                        type: "value",
                        name: "IF %",
                        nameTextStyle: {{ color: "{_R}", fontSize: 10.5 }},
                        axisLabel: {{ color: "{_R}", fontSize: 11 }},
                        splitLine: {{ show: false }},
                        min: 0
                    }}
                ],
                series: [
                    {{
                        name: "Pozos ON",
                        type: "bar",
                        stack: "pozos",
                        data: {json.dumps(on_vals)},
                        barMaxWidth: 16,
                        itemStyle: {{
                            color: {{
                                type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    {{ offset: 0, color: "#4CA46A" }},
                                    {{ offset: 1, color: "{_G}" }}
                                ]
                            }},
                            borderRadius: [3, 3, 0, 0],
                            shadowBlur: 6,
                            shadowColor: "rgba(46,125,70,0.28)",
                            shadowOffsetY: 2
                        }}
                    }},
                    {{
                        name: "Pozos OFF",
                        type: "bar",
                        stack: "pozos",
                        data: {json.dumps(off_vals)},
                        barMaxWidth: 16,
                        itemStyle: {{
                            color: "{_R2}",
                            borderRadius: [3, 3, 0, 0]
                        }}
                    }},
                    {{
                        name: "IF ALS",
                        type: "line",
                        yAxisIndex: 1,
                        data: {json.dumps(if_vals)},
                        smooth: 0.5,
                        symbol: "circle",
                        symbolSize: 6,
                        tooltip: {{
                            valueFormatter: function(val) {{
                                return val != null ? val.toFixed(2).replace(".", ",") + "%" : "-";
                            }}
                        }},
                        lineStyle: {{ color: "{_R}", width: 2.4 }},
                        itemStyle: {{ color: "{_R}", borderColor: "#fff", borderWidth: 2 }},
                        areaStyle: {{
                            color: {{
                                type: "linear",
                                x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    {{ offset: 0, color: "rgba(192,57,43,0.15)" }},
                                    {{ offset: 1, color: "rgba(192,57,43,0.01)" }}
                                ]
                            }}
                        }},
                        markLine: {{
                            silent: true,
                            lineStyle: {{ color: "{_G}", type: "dashed", width: 1.5, opacity: 0.7 }},
                            data: [{{ yAxis: meta, name: "Meta" }}],
                            label: {{
                                formatter: "Meta {_fmt(META_IF, 1)}%",
                                color: "{_G}",
                                fontSize: 10,
                                fontWeight: "700",
                                position: "insideEndTop",
                                backgroundColor: "rgba(255,255,255,0.85)",
                                padding: [2, 4],
                                borderRadius: 3
                            }}
                        }}
                    }},
                    {{
                        name: "IF Total",
                        type: "line",
                        yAxisIndex: 1,
                        data: {json.dumps(if_tot_vals)},
                        smooth: 0.5,
                        symbol: "circle",
                        symbolSize: 6,
                        tooltip: {{
                            valueFormatter: function(val) {{
                                return val != null ? val.toFixed(2).replace(".", ",") + "%" : "-";
                            }}
                        }},
                        lineStyle: {{ color: "{_N}", width: 2.4, type: "dashed" }},
                        itemStyle: {{ color: "{_N}", borderColor: "#fff", borderWidth: 2 }},
                        areaStyle: {{
                            color: {{
                                type: "linear",
                                x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    {{ offset: 0, color: "rgba(34,58,94,0.10)" }},
                                    {{ offset: 1, color: "rgba(34,58,94,0.01)" }}
                                ]
                            }}
                        }}
                    }}
                ]
            }};
            
            var chartT = echarts.init(document.getElementById('chart_if_anual'));
            chartT.setOption(trendOpt);

            window.addEventListener('resize', function() {{
                chartG.resize();
                chartT.resize();
            }});
        }})();
    </script>
</body>
</html>
"""
        components.html(col2_html, height=520, scrolling=False)

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 3: GAUGES MTBF + RUNLIFE + CORRELACIÓN PRODUCCIÓN VS LONGEVIDAD
    # ─────────────────────────────────────────────────────────────────────────
    with col_r:

        # MTBF no tiene meta punitiva -> siempre en verde
        _mtbf_col = _G
        _ESC = 82.0
        _mtbf_w = min(max(mtbf_val / 2000.0 * _ESC, 35), 100) if mtbf_val else 0

        # Meta de Run Life basada en pozos fallados
        _rl_pct = (rl_val / meta_rl_calc * 100) if meta_rl_calc else 0
        _rl_col = _G if rl_val >= meta_rl_calc else _R
        _rl_w = min(rl_val / meta_rl_calc * _ESC, 100) if meta_rl_calc else 0

        def _rango_de(dias):
            """Rango de la distribución en el que cae una meta dada en días."""
            anios = dias / 365.25
            if anios < 2: return rl_bins[0]
            if anios < 4: return rl_bins[1]
            if anios < 6: return rl_bins[2]
            return rl_bins[3]

        _pie_metas = f"Meta RL Fallados ({_fmt(meta_rl_calc)} d) cae en «{_rango_de(meta_rl_calc)}» · MTBF: {_fmt(mtbf_val)} d"

        # Etiquetas del gráfico de distribución: % y BOPD dentro de cada barra
        _tot_pozos_perf = max(sum(pozos_perf_data), 1)
        _dist_labels = [
            f"{p / _tot_pozos_perf * 100:.0f}%\n{b:,.0f}".replace(",", ".")
            for p, b in zip(pozos_perf_data, bopd_perf_data)
        ]

        col3_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('{_FONTS_URL}');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: {_FS};
            overflow: hidden;
            padding: 7px;
        }}
        .tbl-panel {{
            {_CARD}
            padding: 18px;
            height: 506px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .metas-row {{
            display: flex;
            gap: 18px;
            flex-shrink: 0;
        }}
        .meta-col {{ flex: 1; }}
        .meta-title {{
            font-size: 14px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
        }}
        .meta-val {{
            font-family: {_FN};
            font-size: 40px;
            font-weight: 700;
            color: {_T};
            line-height: 1.05;
            margin: 3px 0 9px;
            font-variant-numeric: tabular-nums;
            letter-spacing: -1px;
        }}
        .meta-val .u {{
            font-family: {_FS};
            font-size: 14px;
            font-weight: 600;
            color: {_T2};
            margin-left: 4px;
            letter-spacing: 0;
        }}
        .meta-track {{
            position: relative;
            width: 100%;
            height: 20px;
            background: #E7E9E4;
            border-radius: 5px;
            overflow: hidden;
        }}
        .meta-fill {{
            height: 100%;
            border-radius: 5px;
        }}
        .meta-mark {{
            position: absolute;
            top: -3px;
            bottom: -3px;
            width: 2.5px;
            background: {_N};
            border-radius: 2px;
        }}
        .meta-cap {{
            font-size: 12px;
            font-weight: 600;
            color: {_T2};
            margin-top: 7px;
        }}
        .meta-cap b {{
            font-family: {_FN};
            font-size: 13px;
            color: {_T};
        }}
        .sec-divider {{
            border-top: 1px solid {_BR};
            margin: 15px 0 10px;
        }}
        .tbl-sec-title {{
            font-size: 14px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-bottom: 2px;
        }}
        .chart-container {{ width: 100%; flex: 1; }}
        .foot-note {{
            font-size: 10.5px;
            font-style: italic;
            color: {_T2};
            text-align: center;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">

        <div class="metas-row">
            <div class="meta-col">
                <div class="meta-title">MTBF</div>
                <div class="meta-val">{_fmt(mtbf_val)}<span class="u">días</span></div>
                <div class="meta-track">
                    <div class="meta-fill" style="width:{_mtbf_w:.1f}%;background:{_mtbf_col};"></div>
                </div>
                <div class="meta-cap">Tiempo medio entre fallas operacionales</div>
            </div>
            <div class="meta-col">
                <div class="meta-title">Run Life</div>
                <div class="meta-val">{_fmt(rl_val)}<span class="u">días</span></div>
                <div class="meta-track">
                    <div class="meta-fill" style="width:{_rl_w:.1f}%;background:{_rl_col};"></div>
                    <div class="meta-mark" style="left:{_ESC}%;"></div>
                </div>
                <div class="meta-cap">Meta RL (Fallados): <b>{_fmt(meta_rl_calc)} d</b> · {_rl_pct:.0f}%</div>
            </div>
        </div>

        <div class="sec-divider"></div>
        <div class="tbl-sec-title">Distribución por Run Life</div>
        <div id="chart_rl" class="chart-container"></div>
        <div class="foot-note">Dentro de cada barra: % del total y BOPD · {_pie_metas}</div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var distOpt = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 900,
                animationEasing: "cubicOut",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "shadow" }},
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(46,125,70,0.2)",
                    borderWidth: 1,
                    borderRadius: 10,
                    padding: [8, 12],
                    textStyle: {{ color: "{_T}", fontSize: 12, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    formatter: function(params) {{
                        var i = params[0].dataIndex;
                        var bopd = {json.dumps(bopd_perf_data)}[i];
                        return '<b>' + params[0].name + '</b><br/>' +
                               params[0].value + ' pozos<br/>' +
                               bopd.toLocaleString('es-CO') + ' BOPD';
                    }}
                }},
                grid: {{ top: "22%", left: "4%", right: "4%", bottom: "4%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(rl_bins)},
                    axisLabel: {{
                        color: "{_T2}",
                        fontSize: 11.5,
                        fontWeight: "bold",
                        fontFamily: "Inter, Segoe UI, sans-serif",
                        interval: 0
                    }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: {{
                    type: "value",
                    name: "POZOS",
                    nameTextStyle: {{ color: "{_T2}", fontSize: 10.5 }},
                    axisLabel: {{ color: "{_T2}", fontSize: 10.5 }},
                    splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }},
                    maxValueSpan: null,
                    scale: false
                }},
                series: [
                    {{
                        name: "Pozos",
                        type: "bar",
                        barMaxWidth: 74,
                        data: {json.dumps(pozos_perf_colored)},
                        label: {{
                            show: true,
                            position: "top",
                            fontFamily: "Source Serif 4, Cambria, Georgia, serif",
                            fontSize: 17,
                            fontWeight: "700",
                            color: "{_T}"
                        }},
                    }},
                    {{
                        name: "detalle",
                        type: "bar",
                        barGap: "-100%",
                        barMaxWidth: 74,
                        silent: true,
                        itemStyle: {{ color: "transparent" }},
                        data: {json.dumps(pozos_perf_data)},
                        label: {{
                            show: true,
                            position: "inside",
                            lineHeight: 16,
                            fontFamily: "Inter, Segoe UI, sans-serif",
                            fontSize: 12.5,
                            fontWeight: "bold",
                            color: "#ffffff",
                            formatter: function(p) {{
                                return {json.dumps(_dist_labels)}[p.dataIndex];
                            }}
                        }}
                    }}
                ]
            }};

            var chartDist = echarts.init(document.getElementById('chart_rl'));
            chartDist.setOption(distOpt);
            window.addEventListener('resize', function() {{ chartDist.resize(); }});
        }})();
    </script>
</body>
</html>
"""
        components.html(col3_html, height=520, scrolling=False)

    # ─────────────────────────────────────────────────────────────────────────
    # FILA 2: BALANCE DE POZOS · FALLAS POR ANTIGÜEDAD · FALLAS DEL MES
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1], gap="medium")

    # ── 1. Balance de pozos ON (waterfall) ───────────────────────────────────
    with col_b1:
        _wf_pasos = [
            ('Base',        balance['base'],        'total'),
            ('Nuevos',      balance['nuevos'],      'pos'),
            ('Reactivados', balance['reactivados'], 'pos'),
            ('Fallados',    -balance['fallados'],   'neg'),
            ('Apagados',    -balance['apagados'],   'neg'),
            ('Final',       balance['final'],       'total'),
        ]
        # Pedestal invisible que levanta cada barra intermedia hasta su nivel
        _base_wf, _delta_wf, _acum = [], [], 0
        for _lbl, _v, _kind in _wf_pasos:
            if _kind == 'total':
                _base_wf.append(0)
                _delta_wf.append(_v)
                _acum = _v
            elif _v >= 0:
                _base_wf.append(_acum)
                _delta_wf.append(_v)
                _acum += _v
            else:
                _acum += _v
                _base_wf.append(_acum)
                _delta_wf.append(-_v)

        _wf_colors = [_G2 if k == 'total' else (_G if k == 'pos' else _R)
                      for _, _, k in _wf_pasos]
        _wf_labels = [(("+" if v > 0 else "-") + _fmt(abs(v)) if k != 'total' else _fmt(v))
                      for _, v, k in _wf_pasos]
        _wf_cats   = [l for l, _, _ in _wf_pasos]
        _wf_data   = [{"value": d,
                       "itemStyle": {"color": c, "borderRadius": [3, 3, 0, 0],
                                     "shadowBlur": 7, "shadowOffsetY": 2,
                                     "shadowColor": "rgba(31,70,32,0.20)"}}
                      for d, c in zip(_delta_wf, _wf_colors)]

        wf_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('{_FONTS_URL}');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: {_FS};
            overflow: hidden;
            padding: 7px;
        }}
        .tbl-panel {{
            {_CARD}
            padding: 16px;
            height: 316px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-sec-title {{
            font-family: {_FS};
            font-size: 13px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid {_BR};
        }}
        .tbl-live-dot {{
            flex: 1;
            height: 2px;
            background: {_G};
            opacity: 0.20;
            border-radius: 2px;
        }}
        .chart-container {{ width: 100%; flex: 1; }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Balance de pozos ON · último año <span class="tbl-live-dot"></span></div>
        <div id="chart_wf" class="chart-container"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var etiquetas = {json.dumps(_wf_labels)};
            var option = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 900,
                animationEasing: "cubicOut",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "shadow" }},
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(46,125,70,0.2)",
                    borderWidth: 1,
                    borderRadius: 10,
                    padding: [8, 12],
                    textStyle: {{ color: "{_T}", fontSize: 12.5, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    formatter: function(params) {{
                        var i = params[0].dataIndex;
                        return '<b>' + params[0].name + '</b><br/>' + etiquetas[i] + ' pozos';
                    }}
                }},
                grid: {{ top: "16%", left: "3%", right: "3%", bottom: "8%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(_wf_cats)},
                    axisLabel: {{ color: "{_T2}", fontSize: 11.5, fontFamily: "Inter, Segoe UI, sans-serif", interval: 0 }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: {{
                    type: "value",
                    axisLabel: {{ color: "{_T2}", fontSize: 11 }},
                    splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }}
                }},
                series: [
                    {{
                        name: "pedestal",
                        type: "bar",
                        stack: "wf",
                        silent: true,
                        barMaxWidth: 42,
                        itemStyle: {{ color: "transparent" }},
                        emphasis: {{ itemStyle: {{ color: "transparent" }} }},
                        data: {json.dumps(_base_wf)}
                    }},
                    {{
                        name: "Pozos",
                        type: "bar",
                        stack: "wf",
                        barMaxWidth: 42,
                        data: {json.dumps(_wf_data)},
                        label: {{
                            show: true,
                            position: "top",
                            fontFamily: "Source Serif 4, Cambria, Georgia, serif",
                            fontSize: 16,
                            fontWeight: "700",
                            color: "{_T}",
                            formatter: function(p) {{ return etiquetas[p.dataIndex]; }}
                        }}
                    }}
                ]
            }};
            var chart = echarts.init(document.getElementById('chart_wf'));
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();
    </script>
</body>
</html>
"""
        components.html(wf_html, height=330, scrolling=False)

    # ── 2. Fallas del último año por etapa de Run Life ───────────────────────
    with col_b2:
        _tot_antig = sum(mat_periodo[et]['ALS'] + mat_periodo[et]['No ALS'] for et in RL_ETAPAS)
        _pila_max = max((series_antig['ALS'][i] + series_antig['No ALS'][i]
                         for i in range(len(RL_ETAPAS))), default=0)
        _umbral = _pila_max * 0.07
        _series_antig_js = [
            {
                "name": t,
                "type": "bar",
                "stack": "fallas",
                "barMaxWidth": 52,
                "data": [
                    {"value": series_antig[t][i], "label": {"show": bool(series_antig[t][i] > 0 and series_antig[t][i] >= _umbral)}}
                    for i in range(len(RL_ETAPAS))
                ],
                "itemStyle": {"color": TIPO_COLOR[t], "borderRadius": [2, 2, 0, 0]},
                "label": {
                    "show": True,
                    "color": "#ffffff",
                    "fontSize": 12,
                    "fontWeight": "bold",
                    "formatter": "{c}",
                },
            }
            for t in ['ALS', 'No ALS']
        ]

        fa_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('{_FONTS_URL}');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: {_FS};
            overflow: hidden;
            padding: 7px;
        }}
        .tbl-panel {{
            {_CARD}
            padding: 16px;
            height: 316px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-sec-title {{
            font-family: {_FS};
            font-size: 13px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid {_BR};
        }}
        .tbl-live-dot {{
            flex: 1;
            height: 2px;
            background: {_G};
            opacity: 0.20;
            border-radius: 2px;
        }}
        .tbl-count {{
            font-family: {_FN};
            font-size: 16px;
            font-weight: 700;
            color: {_T};
            letter-spacing: 0;
            text-transform: none;
        }}
        .chart-container {{ width: 100%; flex: 1; }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">
            Fallas por etapa · último año
            <span class="tbl-live-dot"></span>
            <span class="tbl-count">{_fmt(_tot_antig)}</span>
        </div>
        <div id="chart_fa" class="chart-container"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var option = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 900,
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "shadow" }},
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(46,125,70,0.2)",
                    borderWidth: 1,
                    borderRadius: 10,
                    padding: [8, 12],
                    textStyle: {{ color: "{_T}", fontSize: 12.5, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    formatter: function(params) {{
                        var i = params[0].dataIndex;
                        var als = {json.dumps(series_antig['ALS'])}[i];
                        var noAls = {json.dumps(series_antig['No ALS'])}[i];
                        var pend = {json.dumps(series_antig['Pend Pulling'])}[i];
                        return '<b>' + params[0].name + '</b><br/>' +
                               'Total: <b>' + (als + noAls) + ' fallas</b><br/>' +
                               '<span style="color:{_G};">●</span> ALS: ' + als + '<br/>' +
                               '<span style="color:{_N};">●</span> No ALS: ' + noAls + '<br/>' +
                               '<span style="color:#9FB6C9;">●</span> Pendientes de pull: ' + pend;
                    }}
                }},
                legend: {{
                    data: ["ALS", "No ALS"],
                    bottom: 0,
                    icon: "circle",
                    itemHeight: 7,
                    itemGap: 14,
                    textStyle: {{ color: "{_T2}", fontSize: 11.5, fontFamily: "Inter, Segoe UI, sans-serif" }}
                }},
                grid: {{ top: "10%", left: "3%", right: "3%", bottom: "20%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(RL_ETAPAS)},
                    axisLabel: {{
                        color: "{_T2}",
                        fontSize: 8.5,
                        fontFamily: "Inter, Segoe UI, sans-serif",
                        interval: 0,
                        formatter: function(v, i) {{
                            return v + '\\n' + {json.dumps(RL_ETAPA_EJE)}[i].replace('&lt;', '<').replace('&gt;', '>');
                        }},
                        lineHeight: 13
                    }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: {{
                    type: "value",
                    name: "FALLAS",
                    nameTextStyle: {{ color: "{_T2}", fontSize: 10.5 }},
                    axisLabel: {{ color: "{_T2}", fontSize: 11 }},
                    splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }}
                }},
                series: {json.dumps(_series_antig_js)}
            }};
            var chart = echarts.init(document.getElementById('chart_fa'));
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();
    </script>
</body>
</html>
"""
        components.html(fa_html, height=330, scrolling=False)

    # ── 3. Tabla de fallas del mes en curso ──────────────────────────────────
    with col_b3:
        _filas = ""
        for _i, (_et, _eje) in enumerate(zip(RL_ETAPAS, RL_ETAPA_EJE)):
            _celdas = "".join(
                f'<td><span class="v {"hit" if mat_mes[_et][t] > 0 else ""}">'
                f'{mat_mes[_et][t]}</span></td>'
                for t in TIPOS_FALLA
            )
            _filas += (f'<tr class="{"alt" if _i % 2 == 0 else ""}">'
                       f'<td class="et">{_et}<span>{_eje}</span></td>{_celdas}</tr>')

        _tot_row = "".join(f'<td><span class="v">{tot_mes[t]}</span></td>'
                           for t in TIPOS_FALLA)
        _tot_mes_all = tot_mes['ALS'] + tot_mes['No ALS']
        _resumen_mes = f"ALS: {tot_mes['ALS']} · No ALS: {tot_mes['No ALS']} · Pend. pull: {tot_mes['Pend Pulling']}"

        tabla_html = f"""
<div class="tbl-fallas-panel">
  <div class="tbl-fallas-head">
    <div class="tbl-fallas-title">Fallas de {mes_curso_lbl}</div>
    <div class="tbl-fallas-sub"><b>{_resumen_mes}</b></div>
  </div>
  <table class="tbl-ft">
    <thead>
      <tr>
        <th class="et">Categoría</th>
        <th>ALS</th>
        <th>No ALS</th>
        <th>Pend. P.</th>
      </tr>
    </thead>
    <tbody>
      {_filas}
      <tr class="tot"><td class="et">Total ({_tot_mes_all})</td>{_tot_row}</tr>
    </tbody>
  </table>
  <div class="tbl-fallas-foot">Fallas clasificadas por causa · Pend. P. indica eventos aún sin fecha de extracción</div>
</div>
""".replace("\n", " ")

        st.markdown(tabla_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # FILA 3: TENDENCIA DE PRODUCCIÓN & CURVAS DE SUPERVIVENCIA
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    col_bl, col_br = st.columns([2, 1], gap="medium")

    # 1. Calcular curvas de supervivencia (Kaplan-Meier) por tipo de ALS
    curves_data = {}
    colors_map = {
        'ESP': '#2E7D46',   # Verde principal
        'PCP': '#C98A2C',   # Dorado acento
        'EPCP': '#1F4620',  # Verde oscuro
        'BM': '#C0392B',    # Rojo falla
        'BH': '#707070'     # Gris suave
    }
    
    if df_resumen is not None and not df_resumen.empty:
        for als in ALS_TIPOS:
            sub = df_resumen[df_resumen['ALS'].astype(str).str.strip().str.upper() == als].copy()
            ended = sub[sub['FECHA_FALLA'].notna() | sub['FECHA_PULL'].notna()].copy()
            if ended.empty:
                continue
            rl = ended['RUN LIFE'].dropna().sort_values().values
            n = len(rl)
            surv = 1.0
            xs = [0.0]
            ys = [100.0]
            for i, t in enumerate(rl):
                surv *= (n - i - 1) / (n - i) if (n - i) > 0 else 0
                xs.append(float(t))
                ys.append(round(surv * 100, 1))
            
            # Submuestreo si hay demasiados puntos para mejorar rendimiento
            if len(xs) > 100:
                step = len(xs) // 100
                xs = xs[::step]
                ys = ys[::step]
                
            curves_data[als] = {
                'x': xs,
                'y': ys,
                'color': colors_map.get(als, '#8A9A8C')
            }

    series_survival = []
    for als, cdata in curves_data.items():
        points = [[x, y] for x, y in zip(cdata['x'], cdata['y'])]
        series_survival.append({
            "name": als,
            "type": "line",
            "data": points,
            "showSymbol": False,
            "smooth": True,
            "lineStyle": {"width": 2.5, "color": cdata['color']},
            "itemStyle": {"color": cdata['color']}
        })

    # 2. Calcular tendencia mensual de producción (BOPD, BWPD, BFPD & Pozos ON)
    prod_months = []
    prod_oil = []
    prod_water = []
    prod_fluid = []
    prod_pozos = []
    
    try:
        df_f9_p = df_forma9_untr.copy()
        df_f9_p['FECHA_FORMA9'] = pd.to_datetime(df_f9_p['FECHA_FORMA9'], errors='coerce')
        df_f9_p['MES_STR'] = df_f9_p['FECHA_FORMA9'].dt.strftime('%Y-%m')
        
        petr_col = next((c for c in df_f9_p.columns if 'PETROLEO DIA' in c or 'BOPD' in c), None)
        water_col = next((c for c in df_f9_p.columns if 'AGUA DIARIA' in c or 'BWPD' in c or 'AGUA DIA' in c), None)
        
        meses_a_evaluar = []
        if 'if_cats' in locals() and if_cats:
            _MES_REV = {'Ene':1,'Feb':2,'Mar':3,'Abr':4,'May':5,'Jun':6,'Jul':7,'Ago':8,'Sep':9,'Oct':10,'Nov':11,'Dic':12}
            for cat in if_cats:
                p_mes, p_yr = cat.split('-')
                mes_num = _MES_REV.get(p_mes, 1)
                yr_num = 2000 + int(p_yr)
                meses_a_evaluar.append(f"{yr_num}-{mes_num:02d}")
        else:
            from dateutil.relativedelta import relativedelta
            start_m = fecha_eval_dt - relativedelta(months=11)
            meses_a_evaluar = [(start_m + relativedelta(months=i)).strftime('%Y-%m') for i in range(12)]
            
        for mes_str in meses_a_evaluar:
            df_m = df_f9_p[df_f9_p['MES_STR'] == mes_str]
            if not df_m.empty:
                dias_col_p = next((c for c in df_m.columns if 'DIAS' in str(c).upper()), None)
                mask_p_on = (pd.to_numeric(df_m[dias_col_p], errors='coerce').fillna(0) > 0) if dias_col_p else pd.Series(True, index=df_m.index)
                fluid_cols_p = [c for c in df_m.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
                if fluid_cols_p:
                    mask_f_p = pd.Series(False, index=df_m.index)
                    for fc in fluid_cols_p:
                        mask_f_p = mask_f_p | (pd.to_numeric(df_m[fc], errors='coerce').fillna(0) > 0)
                    mask_p_on = mask_p_on & mask_f_p
                df_on = df_m[mask_p_on].copy()
                oil_sum = float(pd.to_numeric(df_on[petr_col], errors='coerce').fillna(0).sum()) if petr_col else 0.0
                water_sum = float(pd.to_numeric(df_on[water_col], errors='coerce').fillna(0).sum()) if water_col else 0.0
                fluid_sum = oil_sum + water_sum
                pozos_on = int(df_on['POZO'].nunique())
            else:
                oil_sum = 0.0
                water_sum = 0.0
                fluid_sum = 0.0
                pozos_on = 0
                
            y_str = mes_str[2:4]
            m_idx = int(mes_str[5:7]) - 1
            _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            prod_months.append(f"{_MESES[m_idx]}-{y_str}")
            prod_oil.append(round(oil_sum, 1))
            prod_water.append(round(water_sum, 1))
            prod_fluid.append(round(fluid_sum, 1))
            prod_pozos.append(pozos_on)
    except Exception as e:
        pass

    # 3. Renderizar Panel Derecho: Curva de Supervivencia
    with col_br:
        bl_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('{_FONTS_URL}');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: {_FS};
            overflow: hidden;
            padding: 7px;
        }}
        .tbl-panel {{
            {_CARD}
            padding: 16px;
            height: 316px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-sec-title {{
            font-family: {_FS};
            font-size: 13px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid {_BR};
        }}
        .tbl-live-dot {{
            flex: 1;
            height: 2px;
            background: {_G};
            opacity: 0.20;
            border-radius: 2px;
        }}
        .chart-container {{
            width: 100%;
            flex: 1;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Curvas de Supervivencia ALS <span class="tbl-live-dot"></span></div>
        <div id="chart_survival" class="chart-container"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var chart = echarts.init(document.getElementById('chart_survival'));
            var option = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 1000,
                tooltip: {{
                    trigger: "axis",
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(46,125,70,0.2)",
                    borderWidth: 1,
                    textStyle: {{ color: "{_T}", fontSize: 12.5, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    formatter: function(params) {{
                        var html = '<div style="font-weight:bold;margin-bottom:4px;">Run Life: ' + Math.round(params[0].value[0]) + ' días</div>';
                        params.forEach(function(item) {{
                            html += '<span style="color:' + item.color + '">●</span> ' + item.seriesName + ': <b>' + item.value[1].toFixed(1) + '%</b><br/>';
                        }});
                        return html;
                    }}
                }},
                legend: {{
                    data: {json.dumps(list(curves_data.keys()))},
                    textStyle: {{ color: "{_T2}", fontSize: 11.5, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    bottom: 0,
                    icon: "circle"
                }},
                grid: {{ top: "14%", left: "5%", right: "8%", bottom: "16%", containLabel: true }},
                xAxis: {{
                    type: "value",
                    name: "DÍAS",
                    nameTextStyle: {{ color: "{_T2}", fontSize: 10.5 }},
                    axisLabel: {{ color: "{_T2}", fontSize: 11 }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }}
                }},
                yAxis: {{
                    type: "value",
                    name: "SUPERVIVENCIA (%)",
                    min: 0,
                    max: 100,
                    nameTextStyle: {{ color: "{_T2}", fontSize: 10.5 }},
                    axisLabel: {{ color: "{_T2}", fontSize: 11, formatter: '{{value}}%' }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }}
                }},
                series: {json.dumps(series_survival)}
            }};
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();
    </script>
</body>
</html>
"""
        components.html(bl_html, height=330, scrolling=False)

    # 4. Renderizar Panel Izquierdo: Tendencia de Producción Mensual (BOPD, BWPD, BFPD & Pozos ON)
    with col_bl:
        br_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('{_FONTS_URL}');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: {_FS};
            overflow: hidden;
            padding: 7px;
        }}
        .tbl-panel {{
            {_CARD}
            padding: 16px;
            height: 316px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-sec-title {{
            font-family: {_FS};
            font-size: 13px;
            font-weight: 700;
            color: {_G2};
            letter-spacing: 0.8px;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-bottom: 8px;
            margin-bottom: 8px;
            border-bottom: 1px solid {_BR};
        }}
        .tbl-live-dot {{
            flex: 1;
            height: 2px;
            background: {_G};
            opacity: 0.20;
            border-radius: 2px;
        }}
        .chart-container {{
            width: 100%;
            flex: 1;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Tendencia de Producción &amp; Pozos ON <span class="tbl-live-dot"></span></div>
        <div id="chart_production" class="chart-container"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var chart = echarts.init(document.getElementById('chart_production'));
            var option = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 1000,
                tooltip: {{
                    trigger: "axis",
                    backgroundColor: "rgba(255,255,255,0.97)",
                    borderColor: "{_G}",
                    borderWidth: 1,
                    textStyle: {{ color: "{_T}", fontSize: 12.5, fontFamily: "Inter, Segoe UI, sans-serif" }}
                }},
                legend: {{
                    data: ["BOPD (Crudo)", "BWPD (Agua)", "BFPD (Fluido)", "Pozos ON"],
                    textStyle: {{ color: "{_T2}", fontSize: 11.5, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    bottom: 0,
                    icon: "circle"
                }},
                grid: {{ top: "12%", left: "5%", right: "5%", bottom: "15%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(prod_months)},
                    axisLabel: {{ color: "{_T2}", fontSize: 11, fontFamily: "Inter, Segoe UI, sans-serif" }},
                    axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: [
                    {{
                        type: "value",
                        name: "PRODUCCIÓN (BPD)",
                        nameTextStyle: {{ color: "{_T2}", fontSize: 10.5 }},
                        axisLabel: {{ color: "{_T2}", fontSize: 11 }},
                        axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                        splitLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.06)", type: "dashed" }} }}
                    }},
                    {{
                        type: "value",
                        name: "Pozos ON",
                        position: "right",
                        nameTextStyle: {{ color: "{_Y}", fontSize: 10.5 }},
                        axisLabel: {{ color: "{_Y}", fontSize: 8 }},
                        axisLine: {{ lineStyle: {{ color: "rgba(46,125,70,0.12)" }} }},
                        splitLine: {{ show: false }}
                    }}
                ],
                series: [
                    {{
                        name: "BOPD (Crudo)",
                        type: "line",
                        smooth: true,
                        data: {json.dumps(prod_oil)},
                        lineStyle: {{ width: 2.5, color: "{_G}" }},
                        itemStyle: {{ color: "{_G}" }},
                        symbol: "circle",
                        symbolSize: 5
                    }},
                    {{
                        name: "BWPD (Agua)",
                        type: "line",
                        smooth: true,
                        data: {json.dumps(prod_water)},
                        lineStyle: {{ width: 2, color: "#0ea5e9" }},
                        itemStyle: {{ color: "#0ea5e9" }},
                        symbol: "circle",
                        symbolSize: 5
                    }},
                    {{
                        name: "BFPD (Fluido)",
                        type: "line",
                        smooth: true,
                        data: {json.dumps(prod_fluid)},
                        lineStyle: {{ width: 2, color: "#707070" }},
                        itemStyle: {{ color: "#707070" }},
                        symbol: "circle",
                        symbolSize: 5
                    }},
                    {{
                        name: "Pozos ON",
                        type: "bar",
                        yAxisIndex: 1,
                        data: {json.dumps(prod_pozos)},
                        barWidth: "40%",
                        itemStyle: {{
                            color: {{
                                type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    {{ offset: 0, color: "#4CA46A" }},
                                    {{ offset: 1, color: "{_G}" }}
                                ]
                            }},
                            borderRadius: [4, 4, 0, 0],
                            shadowBlur: 6,
                            shadowColor: "rgba(46,125,70,0.26)",
                            shadowOffsetY: 2
                        }}
                    }}
                ]
            }};
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();
    </script>
</body>
</html>
"""
        components.html(br_html, height=330, scrolling=False)

    # ── CÁLCULO DE MÉTRICAS DE PRODUCCIÓN PARA EL TICKER ─────────────────────────
    total_bopd = 0.0
    promedio_bopd = 0.0
    total_bfpd = 0.0
    promedio_bsw = 0.0
    total_gas = 0.0
    
    try:
        df_f9_temp = df_forma9_filtered.copy()
        df_f9_temp['FECHA_FORMA9'] = pd.to_datetime(df_f9_temp.get('FECHA_FORMA9'), errors='coerce')
        
        df_month_f9 = df_f9_temp[
            (df_f9_temp['FECHA_FORMA9'].dt.year == anio_eval) & 
            (df_f9_temp['FECHA_FORMA9'].dt.month == mes_eval)
        ].copy()
        
        # BOPD (Crudo)
        bopd_col = next((c for c in df_month_f9.columns if 'BOPD' in str(c).upper() or 'PETROLEO DIA' in str(c).upper() or 'PETROLEO_DIA' in str(c).upper()), None)
        if bopd_col:
            df_month_f9[bopd_col] = pd.to_numeric(df_month_f9[bopd_col], errors='coerce').fillna(0)
            df_on_f9 = df_month_f9[df_month_f9[bopd_col] > 0].copy()
            total_bopd = float(df_on_f9[bopd_col].sum())
            promedio_bopd = float(df_on_f9[bopd_col].mean()) if not df_on_f9.empty else 0.0
            
        # BFPD (Fluido Total)
        bfpd_col = next((c for c in df_month_f9.columns if 'BFPD' in str(c).upper() or 'FLUID' in str(c).upper()), None)
        if bfpd_col:
            df_month_f9[bfpd_col] = pd.to_numeric(df_month_f9[bfpd_col], errors='coerce').fillna(0)
            total_bfpd = float(df_month_f9[bfpd_col].sum())
            
        # BSW % (Corte de Agua)
        bsw_col = next((c for c in df_month_f9.columns if 'BSW' in str(c).upper()), None)
        if bsw_col:
            df_month_f9[bsw_col] = pd.to_numeric(df_month_f9[bsw_col], errors='coerce').fillna(0)
            df_active_bsw = df_month_f9[df_month_f9[bsw_col] > 0]
            promedio_bsw = float(df_active_bsw[bsw_col].mean()) if not df_active_bsw.empty else float(df_month_f9[bsw_col].mean())
            
        # GAS (Gas producido)
        gas_col = next((c for c in df_month_f9.columns if 'GAS' in str(c).upper()), None)
        if gas_col:
            df_month_f9[gas_col] = pd.to_numeric(df_month_f9[gas_col], errors='coerce').fillna(0)
            total_gas = float(df_month_f9[gas_col].sum())
    except Exception:
        pass

    # ── TICKER HORIZONTAL DE DATOS (TELEPROMPTER / MARQUEE STYLE) ────────────────
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    
    # Construcción dinámica de items para el ticker
    ticker_items = []
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">ALS EN FONDO:</span><span class="ticker-val">{_fmt(als_fondo)} POZOS</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">ACTIVOS OPERATIVOS:</span><span class="ticker-val">{_fmt(als_operativos)} POZOS ({(als_operativos/max(1,als_fondo)*100):.1f}%)</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">DISPONIBILIDAD:</span><span class="ticker-val">{disp_oper:.1f}%</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">UTILIZACIÓN:</span><span class="ticker-val">{uso_oper:.1f}%</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">PROD. CRUDO TOTAL:</span><span class="ticker-val warning">{total_bopd:,.0f} BOPD</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">PROD. CRUDO PROM:</span><span class="ticker-val warning">{promedio_bopd:.1f} BOPD/POZO</span></span>')
    
    if total_bfpd > 0:
        ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">PROD. FLUIDO TOTAL:</span><span class="ticker-val">{total_bfpd:,.0f} BFPD</span></span>')
    if promedio_bsw > 0:
        ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">BSW PROMEDIO:</span><span class="ticker-val warning">{promedio_bsw:.1f}%</span></span>')
    if total_gas > 0:
        ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">PROD. GAS TOTAL:</span><span class="ticker-val">{total_gas:,.0f} MSCFD</span></span>')
        
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">ALS FALLADOS:</span><span class="ticker-val danger">{_fmt(als_fallados)} POZOS ({(als_fallados/max(1,als_fondo)*100):.1f}%)</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">FALLAS PERIODO:</span><span class="ticker-val danger">{fallas_totales} EVENTOS</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">MTBF EFECTIVO:</span><span class="ticker-val warning">{mtbf_val:.1f} DÍAS</span></span>')
    ticker_items.append(f'<span class="ticker-item"><span class="ticker-label">RUN LIFE PROMEDIO:</span><span class="ticker-val">{rl_val:.1f} DÍAS</span></span>')
    
    track_html = "".join(ticker_items)
    
    ticker_html = f"""
    <style>
    @import url('{_FONTS_URL}');

    body {{
        margin: 0;
        padding: 0;
        background: transparent;
        overflow: hidden;
    }}
    
    .ticker-wrapper {{
        width: 100%;
        background: linear-gradient(90deg, rgba(255,255,255,0.98) 0%, rgba(248,253,251,0.99) 50%, rgba(255,255,255,0.98) 100%);
        border: 1px solid rgba(46, 125, 70, 0.14);
        border-radius: 10px;
        padding: 6px 14px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(46, 125, 70, 0.04);
        display: flex;
        align-items: center;
        box-sizing: border-box;
        height: 38px;
    }}
    
    .ticker-title {{
        font-family: {_FS};
        font-size: 0.6rem;
        font-weight: 700;
        color: {_G2};
        text-transform: uppercase;
        letter-spacing: 1.6px;
        border-right: 1px solid {_BR};
        padding-right: 12px;
        margin-right: 12px;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;
    }}
    
    .ticker-content-container {{
        overflow: hidden;
        white-space: nowrap;
        width: 100%;
        position: relative;
        display: flex;
        -webkit-mask-image: linear-gradient(90deg, transparent 0%, #000 3%, #000 97%, transparent 100%);
        mask-image: linear-gradient(90deg, transparent 0%, #000 3%, #000 97%, transparent 100%);
    }}
    
    .ticker-marquee {{
        display: flex;
        flex-wrap: nowrap;
        width: max-content;
        animation: marquee 50s linear infinite;
    }}
    
    .ticker-track {{
        display: flex;
        flex-wrap: nowrap;
        flex-shrink: 0;
    }}
    
    .ticker-item {{
        display: flex;
        align-items: baseline;
        font-family: {_FN};
        font-size: 0.76rem;
        font-weight: 700;
        color: {_T};
        margin-right: 44px;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }}
    
    .ticker-label {{
        font-family: {_FS};
        color: {_T2};
        font-weight: 600;
        font-size: 0.6rem;
        margin-right: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .ticker-val {{
        color: {_G2};
    }}
    
    .ticker-val.warning {{
        color: #C98A2C;
    }}
    
    .ticker-val.danger {{
        color: #C0392B;
    }}
    
    @keyframes marquee {{
        0%   {{ transform: translate3d(0, 0, 0); }}
        100% {{ transform: translate3d(-25%, 0, 0); }}
    }}

    @keyframes tblTickerPulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(46,125,70,0.5); }}
        70%  {{ box-shadow: 0 0 0 5px rgba(46,125,70,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(46,125,70,0); }}
    }}

    .ticker-pulse {{
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: {_G};
        display: inline-block;
        animation: tblTickerPulse 2.4s ease-out infinite;
    }}
    </style>
    
    <div class="ticker-wrapper">
        <div class="ticker-title"><span class="ticker-pulse"></span> ESTADO ALS</div>
        <div class="ticker-content-container">
            <div class="ticker-marquee">
                <div class="ticker-track">{track_html}</div>
                <div class="ticker-track">{track_html}</div>
                <div class="ticker-track">{track_html}</div>
                <div class="ticker-track">{track_html}</div>
            </div>
        </div>
    </div>
    """
    components.html(ticker_html, height=45, scrolling=False)