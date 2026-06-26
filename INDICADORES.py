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
import importlib

# Forzar recarga de módulos locales para evitar problemas de caché con el wrapper app.py
_modules = [
    'header_ui', 'sidebar_ui', 'upload_ui', 'data_loader', 'styles', 
    'calculations', 'kpis', 'processing', 'descargar',
    'tabs.tab_resumen', 'tabs.tab_performance', 'tabs.tab_mtbf', 
    'tabs.tab_fallas', 'tabs.tab_indices', 'tabs.tab_tablero'
]
for _m in _modules:
    if _m in sys.modules:
        importlib.reload(sys.modules[_m])

import pandas as pd
from datetime import datetime
import kpis

from config import COLOR_PRINCIPAL
from styles import apply_all_styles

from header_ui import render_header
from sidebar_ui import render_sidebar
from upload_ui import render_upload_section
from data_loader import load_cached_data

from tabs.tab_resumen import render_tab_resumen
from tabs.tab_performance import render_tab_performance
from tabs.tab_mtbf import render_tab_mtbf
from tabs.tab_fallas import render_tab_fallas
from tabs.tab_indices import render_tab_indices
from tabs.tab_tablero import render_tab_tablero

# ─────────────────────────────────────────────────────────────────────────────
# ESTILOS GLOBALES + CSS PROPIO DEL ORQUESTADOR
# ─────────────────────────────────────────────────────────────────────────────

apply_all_styles()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@500;600&display=swap');

/* ── TABS HUD CENTRALIZADOS Y VIBRANTES ── */
div[data-baseweb="tab-list"] {
    display: flex !important;
    justify-content: center !important;
    gap: 15px !important;
    border-bottom: none !important;
    padding: 5px 0 !important;
    margin-bottom: 0px !important; /* MINIMIZADO AL MÁXIMO */
    width: 100% !important;
}
[data-baseweb="tab"] {
    background-color: rgba(15, 23, 42, 0.95) !important;
    background-image: none !important;
    border: 1px solid rgba(0, 217, 255, 0.4) !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-family: 'Arial', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 800 !important;
    color: #94a3b8 !important;
    text-transform: uppercase !important;
    transition: all 0.3s !important;
}
[data-baseweb="tab"]:hover {
    color: #fff !important;
    background-color: rgba(0, 217, 255, 0.2) !important;
    border-color: #00D9FF !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #fff !important;
    background: linear-gradient(135deg, #00D9FF 0%, #FF00FF 100%) !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.5) !important;
}
/* Forzar visibilidad del botón en Streamlit moderno */
[data-baseweb="tab"] > div {
    background: transparent !important;
}
/* Ocultar la línea y el resalte por defecto */
div[data-baseweb="tab-border"], div[data-baseweb="tab-highlight"], [data-testid="stTabHighlight"] {
    display: none !important;
}

/* ── Toast ── */
div[data-testid="stToast"] {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
}

/* ── Scrollbar delgada ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb { background: rgba(0,217,255,0.25); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,217,255,0.5); }

/* ── Info box sin datos ── */
.als-empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 16px;
    padding: 48px 32px;
    border: 1px dashed rgba(0,217,255,0.2);
    border-radius: 14px;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,217,255,0.04) 0%, transparent 70%);
    text-align: center;
    margin-top: 24px;
}
.als-empty-icon { font-size: 3rem; opacity: 0.6; }
.als-empty-title {
    font-family: 'Arial', sans-serif; font-size: 1rem; font-weight: 700;
    background: linear-gradient(135deg, #00D9FF, #FF00FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 2px;
}
.als-empty-sub {
    font-family: 'Arial', sans-serif; font-size: 0.8rem; font-weight: 500;
    color: #475569; letter-spacing: 1px; max-width: 420px; line-height: 1.6;
}
.als-empty-steps {
    display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;
    margin-top: 4px;
}
.als-step {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 14px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(0,217,255,0.12);
    border-radius: 8px;
    font-family: 'Arial', sans-serif; font-size: 0.72rem;
    font-weight: 600; color: #64748B; letter-spacing: 1px;
}
.als-step-num {
    width: 20px; height: 20px; border-radius: 50%;
    background: rgba(0,217,255,0.12);
    border: 1px solid rgba(0,217,255,0.25);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Arial', sans-serif; font-size: 0.5rem;
    font-weight: 700; color: #00D9FF; flex-shrink: 0;
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

# ── HEADER & CONFIG ──────────────────────────────────────────────────────────
col_head, col_als, col_cfg = st.columns([0.91, 0.045, 0.045], gap="small")
with col_head:
    header_container = st.empty()

with col_als:
    st.write('<div style="margin-top:4px;"></div>', unsafe_allow_html=True)
    with st.popover("🏷️", help="Comparativa ALS en KPIs"):
        df_bd_raw = st.session_state.get('df_bd_calculated')
        if df_bd_raw is not None and not df_bd_raw.empty:
            als_opts = sorted([str(x).strip() for x in df_bd_raw['ALS'].dropna().unique() if str(x).strip() != ''])
            # Excluir 'ECUADOR'
            als_opts = [o for o in als_opts if o.upper() != 'ECUADOR']
            als_options = ['ESP'] + als_opts
            
            # Buscamos el índice actual en session state
            cur = st.session_state.get('kpis_als_filter', 'ESP')
            try:
                idx = als_options.index(str(cur)) if str(cur) in als_options else 0
            except:
                idx = 0
                
            st.selectbox(
                'Sistema a comparar:',
                als_options,
                key='kpis_als_filter',
                index=idx
            )
        else:
            st.info("Carga datos para filtrar.")

with col_cfg:
    st.write('<div style="margin-top:4px;"></div>', unsafe_allow_html=True)
    render_upload_section()

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
    tab_tablero, tab_resumen, tab_perf, tab_fallas = st.tabs([
        "🗂 TABLERO",
        "◈ RESUMEN",
        "⚡ PERFORMANCE",
        "⚠ FALLAS · ÍNDICES",
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

    with tab_perf:
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
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
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        col_fallas, col_indices = st.columns(2, gap="medium")
        with col_fallas:
            from tabs.tab_fallas import render_tab_fallas
            render_tab_fallas(df_bd_calc, fecha_eval)
        with col_indices:
            from tabs.tab_indices import render_tab_indices
            render_tab_indices(
                df_bd_calc,
                df_forma9_filtered,
                fecha_eval,
                filters['selected_activo']
            )

    # ─────────────────────────────────────────────────────────────────────────────
    # FOOTER DE EXPORTACIÓN GLOBAL
    # ─────────────────────────────────────────────────────────────────────────────
    st.markdown("<br><hr style='border:0; height:1px; background:linear-gradient(to right, transparent, rgba(0,217,255,0.1), transparent); margin: 30px 0;'>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns([0.35, 0.3, 0.35])
    with f2:
        from descargar import exportar_resumen_performance
        df_ms = st.session_state.get('df_monthly_summary')
        if df_ms is not None and not df_ms.empty:
            excel_bytes = exportar_resumen_performance(df_ms)
            st.download_button(
                label="📥 DESCARGAR REPORTE EXCEL (DASHBOARD)",
                data=excel_bytes,
                file_name=f"REPORTE_INDICADORES_ALS_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Genera un archivo Excel con todo el resumen de KPIs y Performance"
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