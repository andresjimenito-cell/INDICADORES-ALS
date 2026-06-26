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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Barra principal ── */
.als-header-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 8px 18px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.98) 0%, 
        rgba(252, 254, 253, 0.99) 100%
    );
    border: 1px solid rgba(19, 118, 89, 0.16);
    border-top: 3px solid #137659;
    border-radius: 12px;
    margin-bottom: 0px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(19, 118, 89, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
    transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.als-header-bar:hover {
    box-shadow: 0 6px 24px rgba(19, 118, 89, 0.07), 0 2px 4px rgba(0, 0, 0, 0.02);
    border-color: rgba(19, 118, 89, 0.25);
}

/* ── Logo / ícono ── */
.als-logo-wrap {
    flex-shrink: 0;
    width: 32px; height: 32px;
    border: 1px solid rgba(19, 118, 89, 0.25);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #e8f5ee 0%, #c5e8d5 100%);
    font-size: 1.1rem;
    box-shadow: 0 2px 6px rgba(19, 118, 89, 0.08);
}

/* ── Título + subtítulo ── */
.als-title-block { flex-shrink: 0; }
.als-title {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800;
    font-size: 0.95rem;
    letter-spacing: 0.5px;
    background: linear-gradient(135deg, #137659 0%, #1db87b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin: 0;
}
.als-subtitle {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.58rem;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 2px 0 0 0;
}

/* ── Separador vertical ── */
.als-vdivider {
    width: 1px; height: 26px;
    background: linear-gradient(180deg, transparent, rgba(19, 118, 89, 0.22), transparent);
    flex-shrink: 0;
}

/* ── Badge de fecha ── */
.als-date-badge {
    display: flex; flex-direction: column; align-items: flex-start;
    flex-shrink: 0;
}
.als-date-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.52rem; font-weight: 800;
    color: #64748b; letter-spacing: 1px; text-transform: uppercase;
}
.als-date-value {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem; font-weight: 700;
    color: #137659;
    letter-spacing: 0.2px;
    background: rgba(19, 118, 89, 0.05);
    padding: 2px 8px;
    border-radius: 6px;
    border: 1px solid rgba(19, 118, 89, 0.1);
    margin-top: 3px;
    display: inline-block;
}

/* ── KPI chips ── */
.als-kpi-row {
    display: flex; gap: 8px;
    margin-left: auto;
    flex-shrink: 0;
    align-items: center;
}
.als-kpi-chip {
    display: flex; flex-direction: column; align-items: center;
    padding: 4px 10px;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1.5px solid rgba(19, 118, 89, 0.12);
    border-radius: 8px;
    min-width: 58px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.als-kpi-chip:hover {
    transform: translateY(-1.5px);
    border-color: rgba(19, 118, 89, 0.28);
    box-shadow: 0 4px 10px rgba(19, 118, 89, 0.08);
}
.als-kpi-chip-label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.48rem; font-weight: 800;
    letter-spacing: 1px; text-transform: uppercase;
    color: #64748b; white-space: nowrap;
}
.als-kpi-chip-value {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem; font-weight: 900;
    line-height: 1.1;
    margin-top: 1px;
}

/* ── Dot pulsante de "live" ── */
.als-live-badge {
    display: flex; align-items: center; gap: 6px;
    flex-shrink: 0;
    background: rgba(19, 118, 89, 0.06);
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid rgba(19, 118, 89, 0.12);
}
.als-live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #137659;
    box-shadow: 0 0 6px rgba(19, 118, 89, 0.6);
    animation: pulse-dot 2s ease-in-out infinite;
    display: inline-block;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.75); }
}
.als-live-text {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.55rem; font-weight: 800;
    color: #137659; letter-spacing: 1.5px; text-transform: uppercase;
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
            + chip("TOTAL",    str(total),    "#455a72")
            + chip("ON",       str(activos),  "#137659")
            + chip("FALLAS",   str(fallados), "#c62828")
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
    <p class="als-subtitle">ALS · Artificial Lift Systems · Parex Resources (Frontera)</p>
  </div>

  <!-- Separador -->
  <div class="als-vdivider"></div>

  <!-- Fecha evaluación -->
  <div class="als-date-badge">
    <span class="als-date-label">Periodo eval.</span>
    <span class="als-date-value">{f_display}</span>
  </div>

  <!-- KPI chips (solo si hay datos) -->
  {chips_html}

  <!-- Dot LIVE -->
  <div class="als-live-badge" style="margin-left:{'8px' if hay_datos else 'auto'};">
    <span class="als-live-dot"></span>
    <span class="als-live-text">{'LIVE' if hay_datos else 'STAND·BY'}</span>
  </div>

</div>
""", unsafe_allow_html=True)