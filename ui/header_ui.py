"""
header_ui.py
===========
Header principal de la aplicación INDICADORES ALS.
Barra compacta: Logo + Título + Fecha de evaluación.
"""

from datetime import datetime, timedelta
import os

import pandas as pd
import streamlit as st

from config import COLOR_PRINCIPAL


# ─────────────────────────────────────────────────────────────────────────────
# INIT SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def _init_session_state():
    defaults = {
        "df_forma9_raw":          None,
        "df_bd_raw":              None,
        "df_forma9_calculated":   None,
        "df_bd_calculated":       None,
        "reporte_runes":          None,
        "reporte_run_life":       None,
        "reporte_fallas":         None,
        "df_trabajo":             None,
        "verificaciones":         None,
        "unique_pozos":           [],
        "unique_als":             [],
        "unique_activos":         [],
        "fecha_evaluacion_state": datetime.now().date(),
        "fecha_inicio_state":     datetime.now().date() - timedelta(days=365),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# CSS — inyectado una sola vez
# ─────────────────────────────────────────────────────────────────────────────

_HEADER_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700;8..60,900&display=swap');

/* ── Barra principal ── */
.als-header-bar {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 18px;
    background: linear-gradient(180deg, #ffffff 0%, #FCFDFA 100%);
    border: 1px solid #DCE2D8;
    border-top: 3px solid #2E7D46;
    border-radius: 13px;
    margin-bottom: 0px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(31,70,32,0.05), 0 4px 12px rgba(126,143,124,0.13), inset 0 1px 0 rgba(255,255,255,0.9);
    transition: box-shadow 0.24s ease, border-color 0.24s ease;
    width: 100% !important;
    box-sizing: border-box;
}

.als-header-bar:hover {
    box-shadow: 0 2px 5px rgba(31,70,32,0.07), 0 14px 32px rgba(126,143,124,0.22);
    border-color: rgba(46, 125, 70, 0.35);
}

/* ── Logo / ícono ── */
.als-logo-wrap {
    flex-shrink: 0;
    width: 36px; height: 36px;
    border: 1px solid rgba(46, 125, 70, 0.25);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #EEF3EA 0%, #d8ebd2 100%);
    font-size: 1.15rem;
    box-shadow: 0 2px 6px rgba(46, 125, 70, 0.12);
}

/* ── Título + subtítulo ── */
.als-title-block { flex-shrink: 0; }
.als-title {
    font-family: 'Source Serif 4', Georgia, serif !important;
    font-weight: 700;
    font-size: 1.05rem;
    letter-spacing: -0.2px;
    color: #1F4620;
    line-height: 1.15;
    margin: 0;
}
.als-subtitle {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.60rem;
    font-weight: 700;
    color: #707070;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 2px 0 0 0;
}

/* ── Separador vertical ── */
.als-vdivider {
    width: 1px; height: 26px;
    background: linear-gradient(180deg, transparent, rgba(46, 125, 70, 0.22), transparent);
    flex-shrink: 0;
}

/* ── Badge de fecha ── */
.als-date-badge {
    display: flex; flex-direction: column; align-items: flex-end;
    flex-shrink: 0;
    margin-left: auto;
}
.als-date-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.54rem; font-weight: 800;
    color: #707070; letter-spacing: 1px; text-transform: uppercase;
}
.als-date-value {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.74rem; font-weight: 700;
    color: #1F4620;
    letter-spacing: 0.2px;
    background: rgba(46, 125, 70, 0.08);
    padding: 3px 9px;
    border-radius: 8px;
    border: 1px solid rgba(46, 125, 70, 0.15);
    margin-top: 3px;
    display: inline-block;
}

/* ── Quitar padding extra de Streamlit sobre el header ── */
div[data-testid="stVerticalBlock"] > div:first-child {
    padding-top: 0.5rem !important;
}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def render_header(titulo_pagina: str = "INDICADORES ALS", fecha_eval=None, df_bd_filtered=None):
    """
    Header compacto: Logo + Título + Fecha de evaluación.
    """
    _init_session_state()

    fecha_ini = st.session_state.get('fecha_inicio_state')

    # ── Fecha ──────────────────────────────────────────────────────────────
    try:
        fecha_eval_dt = pd.to_datetime(fecha_eval or datetime.now())
        f_eval_display = fecha_eval_dt.strftime("%d %b %Y").upper()
    except Exception:
        fecha_eval_dt = pd.to_datetime(datetime.now())
        f_eval_display = "N/D"

    try:
        fecha_ini_dt = pd.to_datetime(fecha_ini or (datetime.now() - timedelta(days=365)))
        f_ini_display = fecha_ini_dt.strftime("%d %b %Y").upper()
    except Exception:
        f_ini_display = "N/D"

    f_display = f"{f_ini_display} - {f_eval_display}"

    # Logo
    if os.path.exists("logo.png"):
        logo_inner = '<img src="logo.png" style="width:24px;height:24px;object-fit:contain;">'
    else:
        logo_inner = "ALS"

    # HTML + CSS completo del header
    st.markdown(_HEADER_CSS + f"""
<div class="als-header-bar">

  <!-- Logo -->
  <div class="als-logo-wrap" aria-hidden="true">{logo_inner}</div>

  <!-- Título -->
  <div class="als-title-block">
    <p class="als-title">{titulo_pagina}</p>
    <p class="als-subtitle">ALS · Artificial Lift Systems · Parex Resources (Frontera)</p>
  </div>

  <!-- Separador -->
  <div class="als-vdivider"></div>

  <!-- Fecha evaluación -->
  <div class="als-date-badge">
    <span class="als-date-label">Periodo eval.</span>
    <span class="als-date-value">{f_display}</span>
  </div>

</div>
""", unsafe_allow_html=True)