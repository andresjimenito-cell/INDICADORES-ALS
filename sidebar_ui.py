"""
sidebar_ui.py
=============
Sidebar fijo (no colapsable): panel de control dark-industrial con estética
de terminal de comando. Expone render_sidebar() → dict con filtros.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from styles import inject_custom_css
from ui_helpers import get_logo_img_tag
from upload_ui import render_upload_section


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _unique_options(df_calc: pd.DataFrame, col: str) -> list:
    if df_calc is None or df_calc.empty or col not in df_calc.columns:
        return ['TODOS']
    try:
        opts = sorted(df_calc[col].dropna().astype(str).unique().tolist())
        return ['TODOS'] + opts
    except Exception:
        return ['TODOS']


def _ensure(options: list, key_name: str) -> list:
    cur = str(st.session_state.get(key_name, 'TODOS') or 'TODOS')
    if cur != 'TODOS' and cur not in options:
        options = options + [cur]
    return options


def _mark_change():
    st.session_state['filters_last_change'] = datetime.now().isoformat()


def _select(label: str, icon: str, options: list, key: str):
    cur = str(st.session_state.get(key, 'TODOS') or 'TODOS')
    try:
        idx = options.index(cur) if cur in options else 0
    except Exception:
        idx = 0

    # Usar el label estándar de Streamlit (estilizado vía CSS) para garantizar visibilidad
    return st.sidebar.selectbox(
        f"{icon} {label}", options=options, index=idx, key=key,
        on_change=_mark_change, label_visibility="visible"
    )


# ---------------------------------------------------------------------------
# CSS: sidebar fijo, no colapsable, estética dark-industrial
# ---------------------------------------------------------------------------

SIDEBAR_CSS = """
<style>


/* SIDEBAR: dimensiones y fondo */
[data-testid="stSidebar"] {
    min-width: 220px !important;
    max-width: 220px !important;
    transform: none !important;
    transition: none !important;
    left: 0 !important;
    visibility: visible !important;
}

[data-testid="stAppViewContainer"] {
    display: flex !important;
    flex-direction: row !important;
}

[data-testid="stSidebar"] {
    background: #060a18 !important;
    border-right: 1px solid rgba(0,229,255,0.08) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.6) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: transparent !important;
}

/* Scrollbar */
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 3px; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: rgba(0,229,255,0.15);
    border-radius: 3px;
}

/* SELECTBOXES */
section[data-testid="stSidebar"] .stSelectbox { margin-bottom: 4px !important; }
section[data-testid="stSidebar"] .stSelectbox label { 
    display: block !important; 
    color: #00f2ff !important; 
    font-size: 0.72rem !important; 
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-family: 'Arial', sans-serif !important;
    padding-left: 10px !important;
    border-left: 2px solid #ff00ff !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
    background: rgba(0,229,255,0.03) !important;
    border: 1px solid rgba(0,229,255,0.1) !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
    padding: 3px 8px !important;
    min-height: 26px !important;
    font-size: 0.72rem !important;
    font-family: 'Arial', sans-serif !important;
    color: #b0bec5 !important;
}

/* BOTÓN LOGOUT */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    font-family: 'Arial', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 1.5px !important;
    padding: 5px 0 !important;
    background: rgba(255,23,68,0.05) !important;
    border: 1px solid rgba(255,23,68,0.2) !important;
    color: #ef5350 !important;
}
</style>
"""

# ---------------------------------------------------------------------------
# Componentes HTML del sidebar (Flattened for safety)
# ---------------------------------------------------------------------------

def _header_html(logo_tag: str) -> str:
    return f'<div style="background:linear-gradient(180deg, rgba(0,229,255,0.04) 0%, transparent 100%); border-bottom:1px solid rgba(0,229,255,0.08); padding:18px 16px 14px 16px; text-align:center; position:relative;"><div style="position:absolute; top:0; left:16px; right:16px; height:1px; background:linear-gradient(90deg, transparent, #00e5ff, transparent); opacity:0.4;"></div>{logo_tag}<div style="font-family:\'Arial\', sans-serif !important; font-weight:800; font-size:0.9rem; letter-spacing:4px; margin-top:8px; background:linear-gradient(135deg, #00e5ff 0%, #e040fb 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-transform:uppercase;">FRONTERA</div><div style="font-family:\'Arial\', sans-serif !important; font-size:0.45rem; color:#263238; letter-spacing:3px; text-transform:uppercase; margin-top:3px;">ALS · PANEL DE CONTROL</div></div>'


def _section_header(text: str, color: str = "#00e5ff") -> str:
    return f'<div style="font-family:\'Arial\', sans-serif !important; font-size:0.48rem; color:{color}; letter-spacing:3px; text-transform:uppercase; padding:10px 16px 4px 16px; opacity:0.5;">{text}</div>'


def _divider(color: str = "rgba(0,229,255,0.06)") -> str:
    return f'<div style="height:1px; background:{color}; margin:8px 16px;"></div>'


def _no_data_box() -> str:
    return '<div style="margin:8px 16px; padding:10px; background:rgba(0,229,255,0.02); border:1px dashed rgba(0,229,255,0.1); border-radius:4px; text-align:center; font-family:\'Arial\', sans-serif !important; font-size:0.6rem; color:#263238; letter-spacing:1px;">⏳ SIN DATOS</div>'


# Mapa icono → filtro
_FILTER_ICONS = {
    'ACTIVO':    '◈',
    'BLOQUE':    '◫',
    'CAMPO':     '◎',
    'ALS':       '⬡',
    'PROVEEDOR': '◷',
    'NICK':      '◉',
}

_FILTER_LABELS = {
    'ACTIVO':    'Activo',
    'BLOQUE':    'Bloque',
    'CAMPO':     'Campo',
    'ALS':       'ALS',
    'PROVEEDOR': 'Proveedor',
    'NICK':      'Nick',
}

_FILTER_KEYS = {
    'ACTIVO':    'general_activo_filter',
    'BLOQUE':    'general_bloque_filter',
    'CAMPO':     'general_campo_filter',
    'ALS':       'general_als_filter',
    'PROVEEDOR': 'general_proveedor_filter',
    'NICK':      'general_nick_filter',
}


# ---------------------------------------------------------------------------
# Renderizador principal
# ---------------------------------------------------------------------------

def render_sidebar() -> dict:
    """Sidebar fijo con estética dark-industrial. Retorna dict de filtros."""

    inject_custom_css()
    st.sidebar.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    # ── Encabezado ──────────────────────────────────────────────────────────
    logo_tag = get_logo_img_tag(
        width=52,
        style="filter:drop-shadow(0 0 10px rgba(0,229,255,0.4)); display:block; margin:0 auto;"
    )
    st.sidebar.markdown(_header_html(logo_tag), unsafe_allow_html=True)

    # ── Bloque de filtros ────────────────────────────────────────────────────
    st.sidebar.markdown(_section_header(""), unsafe_allow_html=True)

    df_calc = st.session_state.get('df_bd_calculated')

    # Padding lateral para los selectboxes
    st.sidebar.markdown('<div style="padding: 0 10px;">', unsafe_allow_html=True)

    if df_calc is None or df_calc.empty:
        st.sidebar.markdown(_no_data_box(), unsafe_allow_html=True)
    else:
        for col in ('ACTIVO', 'BLOQUE', 'CAMPO', 'ALS', 'PROVEEDOR', 'NICK'):
            opts = _ensure(_unique_options(df_calc, col), _FILTER_KEYS[col])
            _select(_FILTER_LABELS[col], _FILTER_ICONS[col], opts, _FILTER_KEYS[col])

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # ── Separador + estado de filtros activos ────────────────────────────────
    st.sidebar.markdown(_divider(), unsafe_allow_html=True)

    # Contador de filtros activos
    active_keys = [k for k in _FILTER_KEYS.values()
                   if st.session_state.get(k, 'TODOS') != 'TODOS']
    n_active = len(active_keys)

    if n_active > 0:
        st.sidebar.markdown(f'<div style="margin:0 10px 6px 10px; padding:5px 10px; background:rgba(0,230,118,0.04); border:1px solid rgba(0,230,118,0.15); border-left:2px solid #00e676; border-radius:4px; font-family:\'Arial\', sans-serif !important; font-size:0.55rem; color:#00e676; letter-spacing:1.5px;">◈ {n_active} FILTRO{"S" if n_active > 1 else ""} ACTIVO{"S" if n_active > 1 else ""}</div>', unsafe_allow_html=True)

    # ── Logout ───────────────────────────────────────────────────────────────
    st.sidebar.markdown('<div style="padding:4px 10px 10px 10px;">', unsafe_allow_html=True)
    if st.sidebar.button("⏻  CERRAR SESIÓN", key="ind_btn_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # ── Firma discreta ───────────────────────────────────────────────────────
    st.sidebar.markdown(f'<div style="padding:6px 0 8px 0; text-align:center; font-family:\'Arial\', sans-serif !important; font-size:0.42rem; color:#1a2332; letter-spacing:2px;">v2.0 · ALS MONITOR</div>', unsafe_allow_html=True)

    return {
        'selected_activo':    st.session_state.get('general_activo_filter',    'TODOS'),
        'selected_bloque':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'selected_campo':     st.session_state.get('general_campo_filter',     'TODOS'),
        'selected_als':       st.session_state.get('general_als_filter',       'TODOS'),
        'selected_proveedor': st.session_state.get('general_proveedor_filter', 'TODOS'),
        'selected_nick':      st.session_state.get('general_nick_filter',      'TODOS'),
    }