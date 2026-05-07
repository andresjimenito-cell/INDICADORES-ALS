"""
sidebar_ui.py
=============
Renderiza el sidebar completo: logo, navegación, filtros globales y metadata.
Expone render_sidebar() que retorna un dict con los filtros seleccionados.
"""

import os
from datetime import datetime

import pandas as pd
import streamlit as st

import tema
from config import COLOR_PRINCIPAL
from styles import inject_custom_css


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def open_module_from_indicadores(module_name: str):
    """Establece la sesión para abrir un módulo desde INDICADORES."""
    full_path = os.path.abspath(module_name)
    st.session_state['launch_module_path']              = full_path
    st.session_state['launch_module_name']              = os.path.splitext(os.path.basename(full_path))[0]
    st.session_state['launch_module_resolved_filename'] = os.path.basename(module_name)
    st.rerun()


def _unique_options(df_calc: pd.DataFrame, col: str) -> list:
    """Retorna ['TODOS'] + valores únicos ordenados de una columna."""
    if df_calc is None or df_calc.empty or col not in df_calc.columns:
        return ['TODOS']
    try:
        opts = sorted(df_calc[col].dropna().astype(str).unique().tolist())
        return ['TODOS'] + opts
    except Exception:
        return ['TODOS']


def _ensure(options: list, key_name: str) -> list:
    """Asegura que la selección actual permanezca en la lista de opciones."""
    cur = str(st.session_state.get(key_name, 'TODOS') or 'TODOS')
    if cur != 'TODOS' and cur not in options:
        options = options + [cur]
    return options


def _mark_change(key=None):
    st.session_state['filters_last_change'] = datetime.now().isoformat()


def _select_with_index(label: str, options: list, key: str):
    """Muestra un selectbox preservando el índice de la selección actual."""
    cur = str(st.session_state.get(key, 'TODOS') or 'TODOS')
    try:
        idx = options.index(cur) if cur in options else 0
    except Exception:
        idx = 0
    return st.selectbox(label, options=options, index=idx, key=key, on_change=_mark_change)


# ---------------------------------------------------------------------------
# Renderizador principal
# ---------------------------------------------------------------------------

def render_sidebar() -> dict:
    """
    Renderiza el sidebar completo y retorna los filtros seleccionados:
    {selected_activo, selected_bloque, selected_campo, selected_als,
     selected_proveedor, selected_nick}
    """
    # --- CSS Sidebar ---
    st.sidebar.markdown(f"""
<style>
    section[data-testid="stSidebar"] > div {{
        background: transparent !important; padding-top: 2rem !important;
    }}
    .sidebar-header-unified {{
        display: flex; align-items: center; gap: 12px; margin-top: 2rem; margin-bottom: 1rem;
        padding-bottom: 0.8rem; border-bottom: 2px solid rgba(255,255,255,0.05);
    }}
    .sidebar-header-unified .icon {{ font-size: 1.1rem; line-height: 1; }}
    .sidebar-header-unified .title {{
        font-family: 'Orbitron', monospace; font-weight: 900; font-size: 0.9rem;
        background: linear-gradient(90deg, #C82B96, #00D9FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: 2px; text-transform: uppercase;
    }}
    .sidebar-link {{
        display: block; padding: 10px 16px; margin: 6px 0;
        background: linear-gradient(90deg, rgba(255,255,255,0.02), transparent);
        border-left: 3px solid rgba(255,255,255,0.1); color: #94a3b8 !important;
        text-decoration: none !important; font-size: 0.9rem; font-family: 'Rajdhani', sans-serif;
        font-weight: 600; letter-spacing: 1px; transition: all 0.3s ease;
    }}
    .sidebar-link:hover {{
        background: linear-gradient(90deg, rgba(200,43,150,0.15), transparent);
        border-left-color: #C82B96; color: #fff !important; padding-left: 20px;
        text-shadow: 0 0 10px rgba(200,43,150,0.5);
    }}
</style>
""", unsafe_allow_html=True)

    # --- Header del Sidebar ---
    st.sidebar.markdown(f"""
<div style="text-align:center; padding:2rem 0 1rem 0;">
    <div style="font-family:'Orbitron',monospace; font-weight:900; font-size:1.6rem;
                background:linear-gradient(135deg,#FF00FF 0%,#00D9FF 100%);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                letter-spacing:3px; margin-bottom:5px;
                filter:drop-shadow(0 0 15px rgba(200,43,150,0.4));">
        FRONTERA
    </div>
    <div style="font-family:'Rajdhani',sans-serif; font-size:0.8rem;
                color:#94A3B8; letter-spacing:4px; font-weight:600; text-transform:uppercase; opacity:0.8;">
        ALS SYSTEM v1.3
    </div>
</div>
""", unsafe_allow_html=True)

    # --- Navegación Principal ---
    if st.sidebar.button("🏠 DASHBOARD", key="ind_btn_dash", use_container_width=True, type="primary"):
        for key in ['launch_module_path', 'launch_module_name']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.sidebar.markdown("""
<div class="sidebar-header-unified">
    <div class="icon">💠</div>
    <div class="title">MÓDULOS</div>
</div>
""", unsafe_allow_html=True)

    if st.sidebar.button("🌍 RESUMEN PÚBLICO", key="ind_btn_resumen", use_container_width=True):
        open_module_from_indicadores("resumen_publico.py")
    if st.sidebar.button("⚙️ EVALUACIÓN ESP", key="ind_btn_eval", use_container_width=True):
        open_module_from_indicadores("evaluacion.py")
    if st.sidebar.button("🖥️ VISUALIZER", key="ind_btn_vis", use_container_width=True):
        open_module_from_indicadores("esp_visualizer.py")

    st.sidebar.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 CERRAR SESIÓN", key="ind_btn_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state['hide_main_menu_only'] = False
        st.rerun()

    st.sidebar.divider()

    # --- Metadata ---
    st.sidebar.markdown("""
<div class='sidebar-metadata'>
    <p>Módulo de Indicadores <strong>v1.2</strong></p>
    <p>Desarrollado por <strong>AJM</strong></p>
    <p style='font-size:0.7rem; opacity:0.6; margin-top:0.5rem;'>Frontera Energy © 2026</p>
</div>
""", unsafe_allow_html=True)

    # --- Inyectar CSS global ---
    inject_custom_css()

    # --- Filtros Globales (solo si hay datos) ---
    if st.session_state.get('reporte_runes') is None:
        return {
            'selected_activo': 'TODOS', 'selected_bloque': 'TODOS',
            'selected_campo': 'TODOS', 'selected_als': 'TODOS',
            'selected_proveedor': 'TODOS', 'selected_nick': 'TODOS',
        }

    df_calc = st.session_state.get('df_bd_calculated', pd.DataFrame())

    with st.sidebar:
        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,242,255,0.1),rgba(255,0,255,0.05));
            padding:20px; border-radius:15px; border:1px solid rgba(0,242,255,0.2);
            margin-bottom:25px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
    <div style="font-size:2rem; margin-bottom:10px;">🛡️</div>
    <div style="font-family:'Outfit',sans-serif; font-weight:900; color:#fff; letter-spacing:2px; font-size:0.9rem;">
        CONTROL DE COMANDO
    </div>
    <div style="font-family:'Inter',sans-serif; font-size:0.6rem; color:#00f2ff; opacity:0.8; margin-top:5px; text-transform:uppercase;">
        System Ready • Filter Mode Active
    </div>
</div>
<div style="height:1px; background:linear-gradient(90deg,transparent,rgba(0,242,255,0.3),transparent); margin-bottom:20px;"></div>
""", unsafe_allow_html=True)

        # Construir opciones
        activo_opts   = _ensure(_unique_options(df_calc, 'ACTIVO'),   'general_activo_filter')
        bloque_opts   = _ensure(_unique_options(df_calc, 'BLOQUE'),   'general_bloque_filter')
        campo_opts    = _ensure(_unique_options(df_calc, 'CAMPO'),    'general_campo_filter')
        als_opts      = _ensure(_unique_options(df_calc, 'ALS'),      'general_als_filter')
        proveedor_opts = _ensure(_unique_options(df_calc, 'PROVEEDOR'), 'general_proveedor_filter')
        nick_opts     = _ensure(_unique_options(df_calc, 'NICK'),     'general_nick_filter')

        SEP = '<div style="margin-top:-15px; margin-bottom:10px; height:1px; background:rgba(0,242,255,0.05);"></div>'

        _select_with_index("🌐 Filtrar por Activo",   activo_opts,    'general_activo_filter')
        st.markdown(SEP, unsafe_allow_html=True)
        _select_with_index("🎲 Filtrar por Bloque",   bloque_opts,    'general_bloque_filter')
        st.markdown(SEP, unsafe_allow_html=True)
        _select_with_index("🎴 Filtrar por Campo",    campo_opts,     'general_campo_filter')
        st.markdown(SEP, unsafe_allow_html=True)
        _select_with_index("🔧 Filtrar por ALS",      als_opts,       'general_als_filter')
        st.markdown(SEP, unsafe_allow_html=True)
        _select_with_index("🏭 Filtrar por Proveedor", proveedor_opts, 'general_proveedor_filter')
        st.markdown(SEP, unsafe_allow_html=True)
        _select_with_index("🆔 Filtrar por Nick",     nick_opts,      'general_nick_filter')
        st.write("")

    return {
        'selected_activo':    st.session_state.get('general_activo_filter',    'TODOS'),
        'selected_bloque':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'selected_campo':     st.session_state.get('general_campo_filter',     'TODOS'),
        'selected_als':       st.session_state.get('general_als_filter',       'TODOS'),
        'selected_proveedor': st.session_state.get('general_proveedor_filter', 'TODOS'),
        'selected_nick':      st.session_state.get('general_nick_filter',      'TODOS'),
    }
