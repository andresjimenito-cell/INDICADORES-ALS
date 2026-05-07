"""
INDICADORES.py
==============
Orquestador principal de la aplicación de Indicadores ALS.
Módulo centralizado que integra configuración, estilos, UI y lógica modularizada.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Importar módulos locales de configuración y estilos
from config import COLOR_PRINCIPAL
from styles import apply_all_styles

# Importar módulos de UI y carga
from header_ui import render_header
from sidebar_ui import render_sidebar
from upload_ui import render_upload_section
from data_loader import load_cached_data

# Importar módulos de Tabs
from tabs.tab_resumen import render_tab_resumen
from tabs.tab_performance import render_tab_performance
from tabs.tab_mtbf import render_tab_mtbf
from tabs.tab_fallas import render_tab_fallas
from tabs.tab_indices import render_tab_indices

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="INDICADORES ALS | FRONTERA",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- APLICAR ESTILOS ---
apply_all_styles()

# --- CARGAR CACHÉ AL INICIO ---
if st.session_state.get('reporte_runes') is None:
    cached_data = load_cached_data()
    if cached_data:
        st.session_state['df_bd_calculated']     = cached_data['df_bd']
        st.session_state['df_forma9_calculated'] = cached_data['df_forma9']
        st.session_state['fecha_evaluacion_state'] = cached_data['fecha_evaluacion']
        st.session_state['reporte_runes']        = cached_data['reporte_runes']
        st.session_state['historico_run_life']   = cached_data['historico_run_life']
        st.session_state['reporte_fallas']       = cached_data['reporte_fallas']
        # Re-inicializar filtros si es necesario
        st.toast("Caché cargado correctamente.", icon="✅")

# --- RENDERIZAR SIDEBAR Y OBTENER FILTROS ---
filters = render_sidebar()

# --- RENDERIZAR HEADER ---
render_header()

# --- SECCIÓN DE CARGA ---
render_upload_section()

# --- LÓGICA DE FILTRADO Y RENDERIZADO DE TABS ---
if st.session_state.get('reporte_runes') is not None:
    # Obtener data calculada de session_state
    df_bd_calc     = st.session_state['df_bd_calculated'].copy()
    df_forma9_calc  = st.session_state['df_forma9_calculated'].copy()
    fecha_eval      = st.session_state['fecha_evaluacion_state']
    
    # Aplicar filtros globales
    if filters['selected_activo'] != 'TODOS' and 'ACTIVO' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['ACTIVO'] == filters['selected_activo']]
    
    if filters['selected_bloque'] != 'TODOS' and 'BLOQUE' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['BLOQUE'] == filters['selected_bloque']]
        
    if filters['selected_campo'] != 'TODOS' and 'CAMPO' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['CAMPO'] == filters['selected_campo']]
        
    if filters['selected_als'] != 'TODOS' and 'ALS' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['ALS'] == filters['selected_als']]
        
    if filters['selected_proveedor'] != 'TODOS' and 'PROVEEDOR' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['PROVEEDOR'] == filters['selected_proveedor']]
        
    if filters['selected_nick'] != 'TODOS' and 'NICK' in df_bd_calc.columns:
        df_bd_calc = df_bd_calc[df_bd_calc['NICK'] == filters['selected_nick']]

    # Filtrar Forma 9 según los pozos resultantes de BD
    pozos_en_bd = df_bd_calc['POZO'].unique()
    df_forma9_filtered = df_forma9_calc[df_forma9_calc['POZO'].isin(pozos_en_bd)].copy()

    # Recalcular reporte RUNES para la vista filtrada (opcional, o pasar filtrado)
    reporte_runes = st.session_state['reporte_runes'] 

    # --- DEFINICIÓN DE TABS ---
    tab_resumen, tab_performance, tab_mtbf, tab_fallas, tab_indices = st.tabs([
        "📊 RESUMEN", 
        "⚡ PERFORMANCE", 
        "🕒 TMEF (MTBF)", 
        "🚨 FALLAS", 
        "📈 ÍNDICES & DATA"
    ])

    with tab_resumen:
        render_tab_resumen(
            df_bd_calc, 
            df_forma9_filtered, 
            reporte_runes, 
            fecha_eval, 
            filters['selected_activo']
        )

    with tab_performance:
        render_tab_performance(
            df_bd_calc, 
            df_forma9_filtered, 
            fecha_eval
        )

    with tab_mtbf:
        render_tab_mtbf(
            df_bd_calc, 
            df_forma9_filtered, 
            fecha_eval, 
            st.session_state.get('verificaciones', {}), 
            filters['selected_activo']
        )

    with tab_fallas:
        render_tab_fallas(
            df_bd_calc, 
            fecha_eval
        )

    with tab_indices:
        render_tab_indices(
            df_bd_calc, 
            df_forma9_filtered, 
            fecha_eval, 
            filters['selected_activo']
        )
else:
    st.info("👋 Bienvenid@. Por favor, carga los archivos FORMA 9 y BD o usa las URLs por defecto para comenzar los cálculos.")
    st.image("https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png", width=200)
