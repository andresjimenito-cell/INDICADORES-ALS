"""
INDICADORES.py
==============
Orquestador principal — INDICADORES ALS.
Layout profesional: header compacto, tabs con identidad visual,
estado vacío atractivo y filtrado eficiente.
Refreshed at: 2026-05-07 17:54
"""

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA - DEBE SER LA PRIMERA LLAMADA A ST
# ─────────────────────────────────────────────────────────────────────────────
try:
    st.set_page_config(
        page_title="INDICADORES ALS | PAREX RESOURCES (FRONTERA)",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

import sys
import os
import importlib

# Ajustar sys.path para soportar las subcarpetas del proyecto
base_dir = os.path.dirname(__file__)
for subfolder in ['core', 'data', 'ui', 'tabs']:
    path_dir = os.path.abspath(os.path.join(base_dir, subfolder))
    if path_dir not in sys.path:
        sys.path.append(path_dir)

# Forzar recarga de módulos locales para evitar problemas de caché con el wrapper app.py
_modules = [
    'header_ui', 'sidebar_ui', 'upload_ui', 'data_loader', 'styles', 
    'calculations', 'kpis', 'descargar',
    'tabs.tab_resumen', 'tabs.tab_performance', 'tabs.tab_mtbf', 
    'tabs.tab_fallas', 'tabs.tab_indices', 'tabs.tab_tablero', 'tabs.tab_campanas'
]
for _m in _modules:
    if _m in sys.modules:
        importlib.reload(sys.modules[_m])

import pandas as pd
from datetime import datetime
from ui import kpis

from data.config import COLOR_PRINCIPAL
from ui.styles import apply_all_styles

from ui.header_ui import render_header
from ui.sidebar_ui import render_sidebar
from ui.upload_ui import render_upload_section
from data.data_loader import load_cached_data

from tabs.tab_resumen import render_tab_resumen
from tabs.tab_performance import render_tab_performance
from tabs.tab_mtbf import render_tab_mtbf
from tabs.tab_fallas import render_tab_fallas
from tabs.tab_indices import render_tab_indices
from tabs.tab_tablero import render_tab_tablero
from tabs.tab_campanas import render_tab_campanas

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS GLOBALES + CSS PROPIO DEL ORQUESTADOR
# ─────────────────────────────────────────────────────────────────────────────

apply_all_styles()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Streamlit padding reducido ── */
.block-container { padding-top: 1rem !important; padding-bottom: 60px !important; }
section[data-testid="stSidebar"] > div { padding-top: 0.5rem !important; }

/* ── TABS CORPORATIVOS PAREX (Verde / Dorado — Tema Claro) ── */
div[data-testid="stTabs"] [role="tablist"] {
    position: fixed !important;
    bottom: 16px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 999999 !important;
    background: rgba(255, 255, 255, 0.96) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    padding: 5px 16px !important;
    border-radius: 50px !important;
    border: 1.5px solid rgba(19, 118, 89, 0.2) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(19,118,89,0.08) !important;
    width: auto !important;
    min-width: 480px !important;
    display: flex !important;
    justify-content: center !important;
    gap: 2px !important;
    order: 2 !important;
}

/* Orden: contenido primero, barra de tabs después */
div[data-testid="stTabContent"] {
    order: 1 !important;
    background: transparent !important;
    border: none !important;
    padding-top: 0px !important;
    width: 100% !important;
}

/* Tabs no seleccionados */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    padding: 6px 14px !important;
    color: #5b5c55 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.66rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.0px !important;
    text-transform: uppercase !important;
    transition: all 0.25s ease !important;
    border-radius: 30px !important;
    height: auto !important;
    white-space: nowrap !important;
}

/* Hover tab */
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: #137659 !important;
    background: rgba(19, 118, 89, 0.07) !important;
}

/* Tab activo */
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
    background: linear-gradient(135deg, #137659 0%, #0a4d34 100%) !important;
    box-shadow: 0 4px 12px rgba(19, 118, 89, 0.35) !important;
    border: none !important;
}

/* Ocultar highlight y borde por defecto */
div[data-baseweb="tab-border"],
div[data-baseweb="tab-highlight"],
[data-testid="stTabHighlight"] {
    display: none !important;
}
div[data-testid="stTabs"] {
    display: flex !important;
    flex-direction: column !important;
}

/* ── Toast notificaciones ── */
div[data-testid="stToast"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    background: rgba(255,255,255,0.97) !important;
    border: 1px solid rgba(19,118,89,0.2) !important;
    border-left: 3px solid #137659 !important;
    color: #1f221e !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
}

/* ── Scrollbar elegante ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(19,118,89,0.25); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(19,118,89,0.5); }

/* ── Toolbar buttons ── */
div[data-testid="stPopover"] > button {
    background: rgba(255,255,255,0.95) !important;
    border: 1.5px solid rgba(19, 118, 89, 0.25) !important;
    border-radius: 8px !important;
    padding: 5px 14px !important;
    font-size: 0.72rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #137659 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stPopover"] > button:hover {
    border-color: rgba(19, 118, 89, 0.45) !important;
    box-shadow: 0 2px 8px rgba(19, 118, 89, 0.1) !important;
    background: rgba(19, 118, 89, 0.04) !important;
}

/* ── Info box sin datos (tema claro) ── */
.als-empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 16px; padding: 40px 30px;
    border: 1.5px dashed rgba(19,118,89,0.2);
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(19,118,89,0.02) 0%, rgba(192,156,46,0.02) 100%);
    text-align: center; margin-top: 12px;
}
.als-empty-icon { font-size: 2.8rem; opacity: 0.7; }
.als-empty-title {
    font-family: 'Inter', sans-serif; font-size: 1.0rem; font-weight: 800;
    color: #137659; letter-spacing: 2px; text-transform: uppercase;
}
.als-empty-sub {
    font-family: 'Inter', sans-serif; font-size: 0.82rem; font-weight: 500;
    color: #5b5c55; max-width: 400px; line-height: 1.6;
}
.als-empty-steps {
    display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-top: 6px;
}
.als-step {
    display: flex; align-items: center; gap: 8px; padding: 8px 14px;
    background: rgba(19,118,89,0.04); border: 1px solid rgba(19,118,89,0.12);
    border-radius: 8px; font-family: 'Inter', sans-serif; font-size: 0.70rem;
    font-weight: 600; color: #455a72; letter-spacing: 0.5px;
}
.als-step-num {
    width: 20px; height: 20px; border-radius: 50%;
    background: rgba(19,118,89,0.1); border: 1.5px solid rgba(19,118,89,0.3);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Inter', sans-serif; font-size: 0.58rem;
    font-weight: 800; color: #137659; flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CARGAR CACHÉ AL INICIO
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.get('reporte_runes') is None:
    cached_data = load_cached_data()
    if cached_data:
        st.session_state['df_bd_calculated']      = cached_data['df_bd']
        st.session_state['df_forma9_calculated']  = cached_data['df_forma9']
        st.session_state['fecha_evaluacion_state'] = cached_data['fecha_evaluacion']
        st.session_state['fecha_inicio_state']     = cached_data.get('fecha_inicio', cached_data['fecha_evaluacion'] - pd.DateOffset(years=1))
        st.session_state['reporte_runes']         = cached_data['reporte_runes']
        st.session_state['historico_run_life']    = cached_data['historico_run_life']
        st.session_state['reporte_fallas']        = cached_data['reporte_fallas']
        st.toast("✅ Caché restaurado correctamente.", icon="✅")

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR → FILTROS
# ─────────────────────────────────────────────────────────────────────────────

filters = render_sidebar()

# ── HEADER ───────────────────────────────────────────────────────────────────
header_container = st.empty()

# ── LÓGICA PRINCIPAL ─────────────────────────────────────────────────────────

if st.session_state.get('reporte_runes') is not None:

    # ── Obtener datos calculados ───────────────────────────────────────────
    df_bd_calc    = st.session_state['df_bd_calculated'].copy()
    
    # Filtrar 'ECUADOR' (indicado por el usuario que ya no existe)
    if 'ACTIVO' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['ACTIVO'].astype(str).str.upper().str.strip() != 'ECUADOR']

    df_forma9_calc = st.session_state['df_forma9_calculated'].copy()
    fecha_eval    = st.session_state['fecha_evaluacion_state']
    fecha_ini     = st.session_state.get('fecha_inicio_state')
    if fecha_ini is None:
        fecha_ini = pd.to_datetime(fecha_eval) - pd.DateOffset(years=1)

    # ── Filtrar BD por rango de fechas ─────────────────────────────────────
    df_bd_calc['FECHA_RUN'] = pd.to_datetime(df_bd_calc['FECHA_RUN'])
    df_bd_calc['FECHA_PULL'] = pd.to_datetime(df_bd_calc['FECHA_PULL'], errors='coerce')
    df_bd_calc['FECHA_FALLA'] = pd.to_datetime(df_bd_calc['FECHA_FALLA'], errors='coerce')

    df_bd_calc = df_bd_calc[
        (df_bd_calc['FECHA_RUN'] <= pd.to_datetime(fecha_eval)) &
        (df_bd_calc['FECHA_PULL'].isna() | (df_bd_calc['FECHA_PULL'] >= pd.to_datetime(fecha_ini)))
    ].copy()

    # Limpiar fallas fuera del rango de evaluación
    df_bd_calc.loc[df_bd_calc['FECHA_FALLA'] < pd.to_datetime(fecha_ini), 'FECHA_FALLA'] = pd.NaT
    df_bd_calc.loc[df_bd_calc['FECHA_FALLA'] > pd.to_datetime(fecha_eval), 'FECHA_FALLA'] = pd.NaT

    # ── Aplicar filtros globales ───────────────────────────────────────────
    _filtros = {
        'ACTIVO':    filters['selected_activo'],
        'BLOQUE':    filters['selected_bloque'],
        'CAMPO':     filters['selected_campo'],
        'ALS':       filters['selected_als'],
        'PROVEEDOR': filters['selected_proveedor'],
        'NICK':      filters['selected_nick'],
    }
    for col, val in _filtros.items():
        if val != 'TODOS' and col in df_bd_calc.columns:
            df_bd_calc = df_bd_calc[df_bd_calc[col] == val]

    # ── Filtrar Forma 9 por rango de fechas ────────────────────────────────
    df_forma9_calc['FECHA_FORMA9'] = pd.to_datetime(df_forma9_calc['FECHA_FORMA9'])
    df_forma9_filtered = df_forma9_calc[
        (df_forma9_calc['FECHA_FORMA9'] >= pd.to_datetime(fecha_ini)) &
        (df_forma9_calc['FECHA_FORMA9'] <= pd.to_datetime(fecha_eval))
    ].copy()

    # ── Filtrar Forma 9 según pozos resultantes ────────────────────────────
    pozos_en_bd       = df_bd_calc['POZO'].unique() if 'POZO' in df_bd_calc.columns else []
    df_forma9_filtered = df_forma9_filtered[df_forma9_filtered['POZO'].isin(pozos_en_bd)].copy()

    reporte_runes = st.session_state['reporte_runes']

    # Render header with filtered data
    with header_container:
        render_header(
            titulo_pagina="INDICADORES ALS",
            fecha_eval=fecha_eval,
            df_bd_filtered=df_bd_calc
        )

    # ── NAVEGACIÓN (TABS ESTILIZADOS COMO BOTTOM BAR) ─────────────────────
    # Los estilos en styles.py se encargan de mover estos tabs a la parte inferior.
    tab_tablero, tab_resumen, tab_campanas, tab_perf, tab_fallas, tab_indices = st.tabs([
        "🗂 TABLERO",
        "◈ RESUMEN",
        "🏕 CAMPAÑAS",
        "⚡ PERFORMANCE",
        "⚠ FALLAS",
        "📊 ÍNDICES",
    ])

    with tab_tablero:
        render_tab_tablero(
            df_bd_calc,
            df_forma9_filtered,
            reporte_runes,
            fecha_eval,
            filters['selected_activo'],
        )

    with tab_resumen:
        render_tab_resumen(
            df_bd_calc,
            df_forma9_filtered,
            reporte_runes,
            fecha_eval,
            filters['selected_activo'],
        )

    with tab_campanas:
        render_tab_campanas(
            df_bd_calc,
            df_forma9_filtered,
            fecha_eval,
            filters['selected_activo'],
        )

    with tab_perf:
        col_left, col_right = st.columns(2, gap="medium")
        with col_left:
            from tabs.tab_performance import render_tab_performance
            render_tab_performance(df_bd_calc, df_forma9_filtered, fecha_eval)
        with col_right:
            from tabs.tab_mtbf import render_tab_mtbf
            render_tab_mtbf(
                df_bd_calc,
                df_forma9_filtered,
                fecha_eval,
                st.session_state.get('verificaciones', {}),
                filters['selected_activo'],
            )

    with tab_fallas:
        from tabs.tab_fallas import render_tab_fallas
        render_tab_fallas(df_bd_calc, fecha_eval)

    with tab_indices:
        from tabs.tab_indices import render_tab_indices
        render_tab_indices(
            df_bd_calc,
            df_forma9_filtered,
            fecha_eval,
            filters['selected_activo']
        )

    # ── FOOTER EXPORT ───────────────────────────────────────────────────────
    from ui.descargar import exportar_resumen_performance
    df_ms = st.session_state.get('df_monthly_summary')
    if df_ms is not None and not df_ms.empty:
        st.markdown("<hr style='border:0;height:1px;background:linear-gradient(to right,transparent,rgba(19,118,89,0.15),transparent);margin:16px 0 10px 0;'>", unsafe_allow_html=True)
        _fc1, _fc2, _fc3 = st.columns([0.3, 0.4, 0.3])
        with _fc2:
            excel_bytes = exportar_resumen_performance(df_ms)
            st.download_button(
                label="📥 DESCARGAR REPORTE EXCEL",
                data=excel_bytes,
                file_name=f"REPORTE_INDICADORES_ALS_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ─────────────────────────────────────────────────────────────────────────────
# ESTADO VACÍO — sin datos cargados
# ─────────────────────────────────────────────────────────────────────────────

else:
    with header_container:
        render_header(
            titulo_pagina="INDICADORES ALS",
            fecha_eval=st.session_state.get('fecha_evaluacion_state'),
            df_bd_filtered=None
        )
    st.markdown("""
<div class="als-empty-state">
    <div class="als-empty-icon">🛡️</div>
    <div class="als-empty-title">SISTEMA LISTO</div>
    <div class="als-empty-sub">
        Carga los archivos de datos para iniciar el análisis de indicadores
        de Artificial Lift Systems. Puedes usar las URLs por defecto
        o subir tus propios archivos desde el panel de carga.
    </div>
    <div class="als-empty-steps">
        <div class="als-step"><div class="als-step-num">1</div>FORMA 9 · Excel</div>
        <div class="als-step"><div class="als-step-num">2</div>BD · Base de datos</div>
        <div class="als-step"><div class="als-step-num">3</div>Fecha de evaluación</div>
        <div class="als-step"><div class="als-step-num">4</div>Calcular KPIs</div>
    </div>
</div>
""", unsafe_allow_html=True)