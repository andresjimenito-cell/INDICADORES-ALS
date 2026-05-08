"""
header_ui.py
============
Header principal de la aplicación INDICADORES ALS.
Diseño HUD futurista con uso óptimo del espacio horizontal:
  - Logo + nombre de app + badge de fecha alineados en una sola barra compacta
  - KPIs rápidos de sesión en la misma fila (pozos totales, activos, fallados)
  - Barra de estado animada en CSS puro
  - Zero vertical waste: ocupa ~72px totales
"""

from datetime import datetime
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
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# CSS — inyectado una sola vez
# ─────────────────────────────────────────────────────────────────────────────

_HEADER_CSS = """
<style>


/* ── Barra principal ── */
.als-header-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 3px 14px;
    background: linear-gradient(90deg,
        rgba(0,217,255,0.06) 0%,
        rgba(10,15,35,0.55) 40%,
        rgba(255,0,255,0.04) 100%
    );
    border: 1px solid rgba(0,217,255,0.1);
    border-radius: 8px;
    margin-bottom: 0px;
    position: relative;
    overflow: hidden;
}

/* ... (resto igual) ... */

/* ── Logo / ícono ── */
.als-logo-wrap {
    flex-shrink: 0;
    width: 28px; height: 28px;
    border: 1px solid rgba(0,217,255,0.3);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(0,217,255,0.08);
    font-size: 1rem;
}

/* ── Título + subtítulo ── */
.als-title-block { flex-shrink: 0; }
.als-title {
    font-family: 'Arial', sans-serif !important;
    font-weight: 900;
    font-size: 0.85rem;
    letter-spacing: 2px;
    background: linear-gradient(135deg, #00D9FF 0%, #FF00FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin: 0;
}
.als-subtitle {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.5rem;
    font-weight: 600;
    color: #475569;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
}

/* ── Separador vertical ── */
.als-vdivider {
    width: 1px; height: 22px;
    background: linear-gradient(180deg, transparent, rgba(0,217,255,0.25), transparent);
    flex-shrink: 0;
}

/* ── Badge de fecha ── */
.als-date-badge {
    display: flex; flex-direction: column; align-items: flex-start;
    flex-shrink: 0;
}
.als-date-label {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.45rem; font-weight: 700;
    color: #475569; letter-spacing: 1.5px; text-transform: uppercase;
}
.als-date-value {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.7rem; font-weight: 500;
    color: #00D9FF;
    letter-spacing: 1px;
}

/* ── KPI chips ── */
.als-kpi-row {
    display: flex; gap: 5px;
    margin-left: auto;
    flex-shrink: 0;
    align-items: center;
}
.als-kpi-chip {
    display: flex; flex-direction: column; align-items: center;
    padding: 2px 8px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 6px;
    min-width: 50px;
}
.als-kpi-chip-label {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.4rem; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase;
    color: #475569; white-space: nowrap;
}
.als-kpi-chip-value {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.75rem; font-weight: 700;
    line-height: 1.1;
}

/* ── Dot pulsante de "live" ── */
.als-live-dot {
    display: flex; align-items: center; gap: 5px;
    flex-shrink: 0;
}
.als-live-dot span {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00ff9d;
    box-shadow: 0 0 6px #00ff9d;
    animation: pulse-dot 2s ease-in-out infinite;
    display: inline-block;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.7); }
}
.als-live-text {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.5rem; font-weight: 700;
    color: #00ff9d; letter-spacing: 2px; text-transform: uppercase;
}

/* ── Quitar padding extra de Streamlit sobre el header ── */
div[data-testid="stVerticalBlock"] > div:first-child {
    padding-top: 0.5rem !important;
}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — leer KPIs rápidos desde session_state
# ─────────────────────────────────────────────────────────────────────────────

def _quick_kpis(fecha_eval_dt) -> tuple[int, int, int]:
    """Devuelve (total_pozos, pozos_activos, pozos_fallados) desde session_state."""
    df = st.session_state.get("df_bd_calculated")
    if df is None or df.empty:
        return 0, 0, 0

    total = df["POZO"].nunique() if "POZO" in df.columns else 0

    req = {"FECHA_RUN", "FECHA_PULL", "FECHA_FALLA"}
    if req.issubset(df.columns):
        mask_on = (
            (df["FECHA_RUN"] <= fecha_eval_dt) &
            (df["FECHA_PULL"].isna() | (df["FECHA_PULL"] > fecha_eval_dt)) &
            (df["FECHA_FALLA"].isna() | (df["FECHA_FALLA"] > fecha_eval_dt))
        )
        mask_fail = (
            (df["FECHA_RUN"] <= fecha_eval_dt) &
            (df["FECHA_FALLA"].notna()) &
            (df["FECHA_FALLA"] <= fecha_eval_dt) &
            (df["FECHA_PULL"].isna() | (df["FECHA_PULL"] > fecha_eval_dt))
        )
        activos  = df[mask_on]["POZO"].nunique()   if "POZO" in df.columns else 0
        fallados = df[mask_fail]["POZO"].nunique() if "POZO" in df.columns else 0
    else:
        activos, fallados = 0, 0

    return total, activos, fallados


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def render_header(titulo_pagina: str = "INDICADORES ALS", fecha_eval=None):
    """
    Header compacto de alta densidad.

    Layout (todo en una sola barra horizontal):
      [Logo] [Título + subtítulo] [│] [Fecha eval] [│] [KPI×3] [●LIVE]
    """
    _init_session_state()

    # ── Fecha ──────────────────────────────────────────────────────────────
    if fecha_eval:
        try:
            fecha_eval_dt = pd.to_datetime(fecha_eval)
            f_display = fecha_eval_dt.strftime("%d %b %Y").upper()
        except Exception:
            fecha_eval_dt = pd.to_datetime(datetime.now())
            f_display = "N/D"
    else:
        fecha_eval_dt = pd.to_datetime(datetime.now())
        f_display = fecha_eval_dt.strftime("%d %b %Y").upper()

    # ── KPIs rápidos ───────────────────────────────────────────────────────
    total, activos, fallados = _quick_kpis(fecha_eval_dt)

    hay_datos = st.session_state.get("reporte_runes") is not None

    # KPI chips HTML
    def chip(label: str, value: str, color: str) -> str:
        return (
            f'<div class="als-kpi-chip">'
            f'  <span class="als-kpi-chip-label">{label}</span>'
            f'  <span class="als-kpi-chip-value" style="color:{color};">{value}</span>'
            f'</div>'
        )

    chips_html = ""
    if hay_datos:
        chips_html = (
            f'<div class="als-kpi-row">'
            f'  <div class="als-vdivider"></div>'
            + chip("TOTAL",    str(total),    "#00D9FF")
            + chip("ON",       str(activos),  "#00FF9D")
            + chip("FALLAS",   str(fallados), "#FF3E3E")
            + f'</div>'
        )

    # Logo
    if os.path.exists("logo.png"):
        # Si existe el logo PNG, lo insertamos con st.image en columna aparte
        logo_inner = '<img src="logo.png" style="width:24px;height:24px;object-fit:contain;">'
    else:
        logo_inner = "🛡️"

    # HTML completo del header
    st.markdown(_HEADER_CSS, unsafe_allow_html=True)
    st.markdown(f"""
<div class="als-header-bar">

  <!-- Logo -->
  <div class="als-logo-wrap" aria-hidden="true">{logo_inner}</div>

  <!-- Título -->
  <div class="als-title-block">
    <p class="als-title">{titulo_pagina}</p>
    <p class="als-subtitle">ALS · Artificial Lift Systems · Frontera Energy</p>
  </div>

  <!-- Separador -->
  <div class="als-vdivider"></div>

  <!-- Fecha evaluación -->
  <div class="als-date-badge">
    <span class="als-date-label">Fecha eval.</span>
    <span class="als-date-value">{f_display}</span>
  </div>

  <!-- KPI chips (solo si hay datos) -->
  {chips_html}

  <!-- Dot LIVE -->
  <div class="als-live-dot" style="margin-left:{'8px' if hay_datos else 'auto'};">
    <span></span>
    <span class="als-live-text">{'LIVE' if hay_datos else 'STAND·BY'}</span>
  </div>

</div>
""", unsafe_allow_html=True)