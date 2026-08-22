"""
sidebar_ui.py
=============
Sidebar fijo (no colapsable) corporativo en tema claro de Parex Resources.
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

EXCLUIDOS_SIDEBAR = {
    'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
    'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
    'MAPACHE/PERICO', 'MAPACHE-PERICO',
    'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
    'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
    'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE'
}

def _unique_options(df_calc: pd.DataFrame, col: str) -> list:
    if df_calc is None or df_calc.empty or col not in df_calc.columns:
        return ['TODOS']
    try:
        opts = sorted(df_calc[col].dropna().astype(str).unique().tolist())
        opts = [o for o in opts if o.strip().upper() not in EXCLUIDOS_SIDEBAR]
        return ['TODOS'] + opts
    except Exception:
        return ['TODOS']


def _ensure(options: list, key_name: str) -> list:
    """Asegura que el valor actual en session_state esté en las opciones.
    Si no está (ej. datos recargados), resetea a 'TODOS'."""
    cur = str(st.session_state.get(key_name, 'TODOS') or 'TODOS')
    if cur != 'TODOS' and cur not in options:
        # Valor obsoleto -> resetear
        st.session_state[key_name] = 'TODOS'
        return ['TODOS'] + [o for o in options if o != 'TODOS']
    return options


def _mark_change():
    st.session_state['filters_last_change'] = datetime.now().isoformat()


def _select(label: str, icon: str, options: list, key: str, disabled: bool = False):
    cur = str(st.session_state.get(key, 'TODOS') or 'TODOS')
    try:
        idx = options.index(cur) if cur in options else 0
    except Exception:
        idx = 0

    return st.sidebar.selectbox(
        f"{icon} {label}", options=options, index=idx, key=key,
        on_change=_mark_change, label_visibility="visible", disabled=disabled
    )


# ---------------------------------------------------------------------------
# CSS: sidebar fijo, tema claro Parex
# ---------------------------------------------------------------------------

SIDEBAR_CSS = """
<style>
/* SIDEBAR: fondo y estilos */

[data-testid="stSidebar"] {
    background: #eaf4ef !important;
    border-right: 1px solid rgba(19, 118, 89, 0.15) !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.03) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: transparent !important;
}

/* Scrollbar */
section[data-testid="stSidebar"] ::-webkit-scrollbar { width: 3px; }
section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: rgba(19, 118, 89, 0.25);
    border-radius: 3px;
}

/* SELECTBOXES */
section[data-testid="stSidebar"] .stSelectbox { margin-bottom: 4px !important; }
section[data-testid="stSidebar"] .stSelectbox label { 
    display: block !important; 
    color: #137659 !important; 
    font-size: 0.72rem !important; 
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-family: 'Montserrat', sans-serif !important;
    padding-left: 10px !important;
    border-left: 2px solid #c09c2e !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
    background: #ffffff !important;
    border: 1px solid rgba(19, 118, 89, 0.2) !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
    background: #ffffff !important;
    padding: 3px 8px !important;
    min-height: 26px !important;
    font-size: 0.72rem !important;
    font-family: 'Montserrat', sans-serif !important;
    color: #1f221e !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg {
    fill: #1f221e !important;
    color: #1f221e !important;
}

/* BOTÓN LOGOUT */
section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.65rem !important;
    letter-spacing: 1.5px !important;
    padding: 5px 0 !important;
    background: rgba(217,119,6,0.05) !important;
    border: 1px solid rgba(217,119,6,0.2) !important;
    color: #d97706 !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #d97706 !important;
    color: #ffffff !important;
}

/* POPOVER en sidebar — separación clara */
section[data-testid="stSidebar"] div[data-testid="stPopover"] {
    margin-top: 6px !important;
    margin-bottom: 6px !important;
}
section[data-testid="stSidebar"] div[data-testid="stPopover"] > button {
    width: 100% !important;
    height: auto !important;
    min-height: 36px !important;
    padding: 6px 12px !important;
}
</style>
"""

# ---------------------------------------------------------------------------
# Componentes HTML del sidebar
# ---------------------------------------------------------------------------

def _header_html(logo_tag: str) -> str:
    return f'<div style="background:rgba(19, 118, 89, 0.04); border-bottom:1px solid rgba(19, 118, 89, 0.08); padding:18px 16px 14px 16px; text-align:center; position:relative;"><div style="position:absolute; top:0; left:16px; right:16px; height:1px; background:#137659; opacity:0.2;"></div>{logo_tag}<div style="font-family:\'Montserrat\', sans-serif !important; font-weight:800; font-size:0.9rem; letter-spacing:3px; margin-top:8px; color:#137659; text-transform:uppercase;">PAREX RESOURCES (FRONTERA)</div><div style="font-family:\'Montserrat\', sans-serif !important; font-size:0.45rem; color:#5b5c55; letter-spacing:2px; text-transform:uppercase; margin-top:3px;">ALS · PANEL DE CONTROL</div></div>'


def _section_header(text: str, color: str = "#137659") -> str:
    return f'<div style="font-family:\'Montserrat\', sans-serif !important; font-size:0.48rem; color:{color}; letter-spacing:3px; text-transform:uppercase; padding:10px 16px 4px 16px; opacity:0.6;">{text}</div>'


def _divider(color: str = "rgba(19, 118, 89, 0.08)") -> str:
    return f'<div style="height:1px; background:{color}; margin:8px 16px;"></div>'


def _no_data_box() -> str:
    return '<div style="margin:8px 16px; padding:10px; background:rgba(19, 118, 89, 0.02); border:1px dashed rgba(19, 118, 89, 0.1); border-radius:4px; text-align:center; font-family:\'Montserrat\', sans-serif !important; font-size:0.6rem; color:#5b5c55; letter-spacing:1px;">⏳ SIN DATOS</div>'


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
    """Sidebar fijo con estética corporativa Parex. Retorna dict de filtros."""

    inject_custom_css()
    st.sidebar.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    # ── Encabezado ──────────────────────────────────────────────────────────
    logo_tag = get_logo_img_tag(
        width=52,
        style="filter:drop-shadow(0 0 5px rgba(19, 118, 89, 0.15)); display:block; margin:0 auto;"
    )
    st.sidebar.markdown(_header_html(logo_tag), unsafe_allow_html=True)

    # ── Bloque de filtros ────────────────────────────────────────────────────
    st.sidebar.markdown(_section_header("FILTROS"), unsafe_allow_html=True)

    df_calc = st.session_state.get('df_bd_calculated')
    has_data = df_calc is not None and not df_calc.empty
    is_loading = st.session_state.get('_sidebar_loading', False)

    st.sidebar.markdown('<div style="padding: 0 10px;">', unsafe_allow_html=True)

    filter_cols = ('ACTIVO', 'BLOQUE', 'CAMPO', 'ALS', 'PROVEEDOR', 'NICK')
    
    if not has_data:
        # Mostrar placeholders deshabilitados
        for col in filter_cols:
            _select(_FILTER_LABELS[col], _FILTER_ICONS[col], ['TODOS'], _FILTER_KEYS[col], disabled=True)
        if is_loading:
            st.sidebar.markdown(
                '<div style="margin:8px 16px; padding:10px; background:rgba(19,118,89,0.08); '
                'border:1px solid rgba(19,118,89,0.15); border-radius:6px; '
                'text-align:center; font-family:\'Montserrat\', sans-serif !important; '
                'font-size:0.6rem; color:#137659; letter-spacing:1px;">'
                '⏳ Cargando datos...</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown(_no_data_box(), unsafe_allow_html=True)
    else:
        for col in filter_cols:
            opts = _ensure(_unique_options(df_calc, col), _FILTER_KEYS[col])
            _select(_FILTER_LABELS[col], _FILTER_ICONS[col], opts, _FILTER_KEYS[col])

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # ── Separador + Herramientas (Upload en popover) ─────────────────────────
    st.sidebar.markdown(_divider(), unsafe_allow_html=True)

    st.sidebar.markdown(_section_header("HERRAMIENTAS"), unsafe_allow_html=True)
    st.sidebar.markdown('<div style="padding: 4px 10px 8px 10px;">', unsafe_allow_html=True)

    # Upload en popover (único botón)
    from upload_ui import render_upload_section

    with st.sidebar.popover("⚙️ CARGAR DATOS / CONFIGURACIÓN", use_container_width=True):
        render_upload_section(sidebar=False)  # sidebar=False: siempre usa st.*, no st.sidebar.*

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # ── Separador + estado de filtros activos ────────────────────────────────
    st.sidebar.markdown(_divider(), unsafe_allow_html=True)

    # Contador de filtros activos
    active_keys = [k for k in _FILTER_KEYS.values()
                   if st.session_state.get(k, 'TODOS') != 'TODOS']
    n_active = len(active_keys)

    if n_active > 0:
        active_labels = []
        for col, key in _FILTER_KEYS.items():
            val = st.session_state.get(key, 'TODOS')
            if val != 'TODOS':
                active_labels.append(f"{_FILTER_ICONS[col]} {_FILTER_LABELS[col]}: <b>{val}</b>")
        
        st.sidebar.markdown(
            f'<div style="margin:0 10px 6px 10px; padding:8px 10px; '
            f'background:rgba(21,128,61,0.06); border:1px solid rgba(21,128,61,0.15); '
            f'border-left:3px solid #15803d; border-radius:6px; '
            f'font-family:\'Montserrat\', sans-serif !important; font-size:0.55rem; '
            f'color:#15803d; font-weight:700; letter-spacing:1px; line-height:1.6;">'
            f'◈ {n_active} FILTRO{"S" if n_active > 1 else ""} ACTIVO{"S" if n_active > 1 else ""}<br/>'
            f'<span style="font-weight:500; font-size:0.5rem; opacity:0.8;">{" · ".join(active_labels)}</span>'
            f'</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            '<div style="margin:0 10px 6px 10px; padding:8px 10px; '
            'background:rgba(19,118,89,0.04); border:1px dashed rgba(19,118,89,0.12); '
            'border-radius:6px; font-family:\'Montserrat\', sans-serif !important; '
            'font-size:0.55rem; color:#5b5c55; font-weight:600; text-align:center; '
            'letter-spacing:1px;">Sin filtros activos</div>', unsafe_allow_html=True)

    # ── Botón recargar datos ─────────────────────────────────────────────────
    st.sidebar.markdown('<div style="padding: 4px 10px 8px 10px;">', unsafe_allow_html=True)
    if st.sidebar.button("🔄 RECARGAR DATOS", key="btn_reload_data", use_container_width=True, help="Recalcula indicadores con los archivos actuales"):
        st.session_state['_sidebar_loading'] = True
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith('df_') or k in ('reporte_runes', 'historico_run_life', 'reporte_fallas', 'df_trabajo', 'verificaciones')]
        for k in keys_to_clear:
            st.session_state.pop(k, None)
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # ── Separador + Logout ───────────────────────────────────────────────────
    st.sidebar.markdown(_divider(), unsafe_allow_html=True)
    st.sidebar.markdown('<div style="padding:4px 10px 10px 10px;">', unsafe_allow_html=True)
    if st.sidebar.button("⏻  CERRAR SESIÓN", key="ind_btn_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.markdown(f'<div style="padding:6px 0 8px 0; text-align:center; font-family:\'Montserrat\', sans-serif !important; font-size:0.42rem; color:#5b5c55; letter-spacing:2px;">v2.0 · ALS MONITOR</div>', unsafe_allow_html=True)

    return {
        'selected_activo':    st.session_state.get('general_activo_filter',    'TODOS'),
        'selected_bloque':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'selected_campo':     st.session_state.get('general_campo_filter',     'TODOS'),
        'selected_als':       st.session_state.get('general_als_filter',       'TODOS'),
        'selected_proveedor': st.session_state.get('general_proveedor_filter', 'TODOS'),
        'selected_nick':      st.session_state.get('general_nick_filter',      'TODOS'),
    }