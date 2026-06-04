"""
styles.py
=========
Centraliza TODA la inyección de CSS de la aplicación con la estética corporativa de Parex Resources.
Tema Claro, Fondos Limpios, Verdes y Dorados.
"""

import html as html_module
import streamlit as st
import json
import tema
from config import (
    COLOR_PRINCIPAL, COLOR_FUENTE, COLOR_FONDO_OSCURO, COLOR_FONDO_CONTENEDOR,
)

def _apply_styles_internal():
    """Lógica central de inyección de estilos Parex (Tema Claro)."""
    st.markdown("""
    <style>
        /* DataTables HUD Theme Integration */
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        @import url('https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css');

        [data-testid="stAppViewContainer"] { 
            padding: 0 !important; 
            margin: 0 !important; 
            background-color: #f5f7f6 !important;
        }
        [data-testid="stMainBlockContainer"] { 
            padding: 0rem 1rem !important; 
            max-width: 100% !important;
            background-color: #f5f7f6 !important;
        }

        /* FORZAR SIDEBAR ABIERTO */
        [data-testid="stSidebar"] {
            left: 0 !important;
            transform: none !important;
            visibility: visible !important;
            min-width: 220px !important;
            max-width: 220px !important;
            display: block !important;
            background-color: #eaf4ef !important;
            border-right: 1px solid rgba(19, 118, 89, 0.15) !important;
        }
        [data-testid="stAppViewContainer"] {
            display: flex !important;
            flex-direction: row !important;
        }
        [data-testid="stAppViewContainer"] > section:nth-child(2) {
            margin-left: 220px !important;
            min-width: calc(100% - 220px) !important;
        }
        
        /* Ocultar elementos de Streamlit para ganar espacio */
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }
        #MainMenu { display: none !important; }
        
        /* Reducir espacio entre bloques de Streamlit */
        div.block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.15rem !important;
        }
        
        /* Espacio superior de los contenidos de las pestañas */
        div[data-testid="stTabContent"] {
            padding-top: 0rem !important;
        }
        
        /* Eliminar márgenes de los widgets de Streamlit */
        .stMarkdown, .stMetric, .stSelectbox {
            margin-bottom: 0rem !important;
        }
        
        .stApp {
            background-color: #f5f7f6 !important;
            font-family: 'Montserrat', sans-serif !important;
            color: #1f221e !important;
        }

        /* --- EXPANDER LIGHT THEME OVERRIDES --- */
        div[data-testid="stExpander"],
        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] summary {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #137659 !important;
        }
        .streamlit-expanderHeader {
            font-family: 'Montserrat', sans-serif !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            color: #137659 !important;
            letter-spacing: 1px !important;
            background-color: rgba(19, 118, 89, 0.05) !important;
            background: rgba(19, 118, 89, 0.05) !important;
            border: 1px solid rgba(19, 118, 89, 0.15) !important;
            border-radius: 6px !important;
        }
        .streamlit-expanderHeader:hover {
            background-color: rgba(19, 118, 89, 0.1) !important;
            background: rgba(19, 118, 89, 0.1) !important;
            color: #137659 !important;
        }
        .streamlit-expanderContent {
            border: 1px solid rgba(19, 118, 89, 0.15) !important;
            border-top: none !important;
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #1f221e !important;
        }

        /* --- Sidebar Selectbox Style --- */
        [data-testid="stSidebar"] .stSelectbox {
            margin-top: 0px !important;
        }
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0rem !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.2) !important;
            border-radius: 8px !important;
            color: #1f221e !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1f221e !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {
            border-color: #137659 !important;
            box-shadow: 0 0 10px rgba(19, 118, 89, 0.15) !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
            color: #1f221e !important;
            background-color: #ffffff !important;
            font-size: 0.85rem !important;
        }
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] svg {
            fill: #1f221e !important;
            color: #1f221e !important;
        }

        /* Forzar tema claro en el popover de las opciones (dropdown listbox) */
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] [role="listbox"] {
            background-color: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.2) !important;
        }
        div[data-baseweb="popover"] [role="option"] {
            background-color: #ffffff !important;
            color: #1f221e !important;
            font-family: 'Montserrat', sans-serif !important;
        }
        div[data-baseweb="popover"] [role="option"]:hover,
        div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background-color: rgba(19, 118, 89, 0.1) !important;
            color: #137659 !important;
        }

        .kpi-card {
            background: #ffffff;
            border: 1px solid rgba(19, 118, 89, 0.15);
            border-radius: 12px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 10px;
            font-family: 'Montserrat', sans-serif !important;
        }
        .kpi-label {
            font-size: 0.65rem;
            color: #5b5c55;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: #1f221e;
            line-height: 1.2;
        }
        .kpi-icon {
            font-size: 1.2rem;
            margin-bottom: 8px;
        }
        
        /* --- DataTables HUD Customization --- */
        .dataTables_wrapper {
            color: #1f221e !important;
            font-family: 'Montserrat', sans-serif !important;
        }
        .dataTables_filter input {
            background: #ffffff !important;
            border: 1px solid #137659 !important;
            color: #1f221e !important;
            border-radius: 5px !important;
            padding: 4px 10px !important;
            outline: none !important;
        }
        
        /* Estilo para el botón de Copiar */
        button.dt-button, div.dt-button, a.dt-button {
            background: rgba(19, 118, 89, 0.08) !important;
            border: 1px solid rgba(19, 118, 89, 0.4) !important;
            color: #137659 !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            padding: 4px 12px !important;
            border-radius: 4px !important;
            transition: all 0.3s !important;
            margin-bottom: 10px !important;
        }
        button.dt-button:hover {
            background: #137659 !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px rgba(19, 118, 89, 0.2) !important;
        }

        table.dataTable thead th {
            background: rgba(19, 118, 89, 0.1) !important;
            color: #137659 !important;
            font-family: 'Montserrat', sans-serif !important;
            border-bottom: 1px solid #137659 !important;
        }
        table.dataTable tbody td {
            background: transparent !important;
            border-bottom: 1px solid rgba(19, 118, 89, 0.08) !important;
            color: #1f221e !important;
        }
        
        .dataTables_paginate .paginate_button {
            color: #5b5c55 !important;
        }
        .dataTables_paginate .paginate_button.current {
            background: rgba(19, 118, 89, 0.2) !important;
            border-color: #137659 !important;
            color: #137659 !important;
        }

        /* --- Upload Section Styles --- */
        .upload-container {
            background: #ffffff;
            border: 1px solid rgba(19, 118, 89, 0.15);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        }
        .compact-card {
            background: rgba(19, 118, 89, 0.05);
            border: 1px solid rgba(19, 118, 89, 0.1);
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .compact-card span {
            font-family: 'Montserrat', sans-serif;
            font-size: 0.65rem;
            font-weight: 700;
            color: #137659;
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        .upload-area {
            background: #f8faf9;
            border: 1px dashed rgba(19, 118, 89, 0.3);
            border-radius: 8px;
            padding: 4px;
            transition: all 0.3s;
        }
        .upload-area:hover {
            border-color: #137659;
            background: rgba(19, 118, 89, 0.08);
        }
        
        /* --- ESTILOS GLOBALES DE WIDGETS DE STREAMLIT PARA COMPATIBILIDAD CON TEMA CLARO --- */
        
        /* 1. Botones (Base, Descargas, Popovers, etc.) */
        button[data-testid^="stBaseButton"], 
        div.stButton > button, 
        div.stDownloadButton > button {
            background-color: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.3) !important;
            color: #137659 !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            padding: 6px 16px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        }
        button[data-testid^="stBaseButton"]:hover, 
        div.stButton > button:hover, 
        div.stDownloadButton > button:hover {
            background-color: #137659 !important;
            color: #ffffff !important;
            border-color: #137659 !important;
            box-shadow: 0 4px 12px rgba(19, 118, 89, 0.2) !important;
        }

        /* 2. Selectboxes y Dropdowns (Global) */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.25) !important;
            border-radius: 8px !important;
            color: #1f221e !important;
        }
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1f221e !important;
        }
        .stSelectbox div[data-baseweb="select"]:hover {
            border-color: #137659 !important;
            box-shadow: 0 0 8px rgba(19, 118, 89, 0.15) !important;
        }
        .stSelectbox div[data-baseweb="select"] div {
            color: #1f221e !important;
            background-color: #ffffff !important;
            font-size: 0.75rem !important;
            font-family: 'Montserrat', sans-serif !important;
        }
        .stSelectbox div[data-baseweb="select"] svg {
            fill: #1f221e !important;
            color: #1f221e !important;
        }

        /* 3. Popovers (Filtros KPIs y Configuración en Header) */
        div[data-testid="stPopover"] button,
        button[data-testid="stPopoverButton"],
        div.stPopover button {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.3) !important;
            color: #137659 !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            min-height: 30px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 0.9rem !important;
            transition: all 0.3s !important;
            margin: 0 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stPopover"] button:hover,
        button[data-testid="stPopoverButton"]:hover,
        div.stPopover button:hover {
            background-color: #137659 !important;
            background: #137659 !important;
            color: #ffffff !important;
            border-color: #137659 !important;
            box-shadow: 0 4px 12px rgba(19, 118, 89, 0.25) !important;
        }
        div[data-testid="stPopoverBody"] {
            background-color: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.2) !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
            color: #1f221e !important;
        }
        div[data-testid="stPopoverBody"] * {
            color: #1f221e !important;
        }
        
        /* 5. Carga de Archivos (File Uploader) */
        div[data-testid="stFileUploader"] {
            background-color: #ffffff !important;
            border: 1.5px dashed rgba(19, 118, 89, 0.3) !important;
            border-radius: 8px !important;
            padding: 8px !important;
        }
        div[data-testid="stFileUploader"] section {
            background-color: #ffffff !important;
        }
        div[data-testid="stFileUploader"] * {
            color: #1f221e !important;
            background-color: #ffffff !important;
        }

        /* 4. Inputs globales */
        .stTextInput input, .stDateInput input {
            background-color: #ffffff !important;
            border: 1px solid rgba(19, 118, 89, 0.25) !important;
            color: #1f221e !important;
            font-size: 0.8rem !important;
        }
        .stSelectbox label, .stTextInput label, .stDateInput label {
            color: #137659 !important;
            font-size: 0.65rem !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            font-family: 'Montserrat', sans-serif !important;
        }
        
        .fecha-alerta {
            background: linear-gradient(90deg, rgba(192, 156, 46, 0.1), transparent);
            border-left: 3px solid #c09c2e;
            padding: 8px 12px;
            border-radius: 4px;
            margin-top: 8px;
            color: #1f221e;
        }

        /* Contenedor para controles de gráfica (Overlay) */
        div.chart-controls-wrapper {
            position: relative;
            width: 100%;
        }
        div.chart-controls-overlay {
            position: absolute;
            top: 8px;
            right: 45px;
            z-index: 1001;
            pointer-events: none;
        }
        div.chart-controls-overlay > div {
            pointer-events: auto;
        }
        div.chart-controls-overlay .stDownloadButton button {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(19, 118, 89, 0.4) !important;
            color: #137659 !important; 
            font-size: 8px !important;
            padding: 0px !important;
            min-height: 16px !important;
            height: 16px !important;
            width: 16px !important;
            min-width: 16px !important;
            border-radius: 4px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s !important;
            backdrop-filter: blur(4px) !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }
        div.chart-controls-overlay .stDownloadButton button:hover {
            background: rgba(19, 118, 89, 0.1) !important;
            border-color: #137659 !important;
            color: #137659 !important;
        }

        /* ── FLOATING NAVIGATION (TABLIST) ── */
        div[data-testid="stTabs"] {
            display: flex !important;
            flex-direction: column !important;
        }

        div[data-testid="stTabs"] [role="tablist"] {
            position: fixed !important;
            bottom: 30px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 999999 !important;
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(15px) !important;
            padding: 5px 25px !important;
            border-radius: 50px !important;
            border: 1px solid rgba(19, 118, 89, 0.3) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08), 0 0 15px rgba(19, 118, 89, 0.1) !important;
            width: auto !important;
            min-width: 500px !important;
            display: flex !important;
            justify-content: center !important;
            gap: 15px !important;
            order: 2 !important; 
        }

        /* Asegurar que el contenido de los tabs NO se mueva con la barra y esté arriba */
        div[data-testid="stTabContent"] {
            order: 1 !important;
            background: transparent !important;
            border: none !important;
            padding-top: 0px !important;
            width: 100% !important;
        }

        /* Quitar la línea inferior por defecto de los tabs */
        div[data-testid="stTabs"] [role="tablist"] {
            border: none !important;
        }

        /* Estilo de cada botón de tab */
        div[data-testid="stTabs"] button[data-baseweb="tab"] {
            background: transparent !important;
            border: none !important;
            padding: 8px 18px !important;
            color: #5b5c55 !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 0.7rem !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            transition: all 0.3s !important;
            border-radius: 20px !important;
            height: auto !important;
        }
        
        div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
            color: #137659 !important;
            background: rgba(19, 118, 89, 0.05) !important;
        }
        
        /* Tab seleccionado (Estado Activo) */
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #137659 !important;
            background: rgba(19, 118, 89, 0.12) !important;
            border: 1px solid rgba(19, 118, 89, 0.25) !important;
            box-shadow: 0 0 10px rgba(19, 118, 89, 0.1) !important;
        }

        /* Esconder la barra debajo del tab seleccionado */
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
            display: none !important;
        }

        /* ── ILUMINACIÓN VERDE Y EFECTOS GLOW COMPACTO ── */
        .stExpander, div[data-testid="stForm"], .kpi-card, .upload-container, .als-header-bar {
            box-shadow: 0 0 12px rgba(19, 118, 89, 0.12) !important;
            border: 1.5px solid rgba(19, 118, 89, 0.25) !important;
            transition: all 0.3s ease !important;
        }
        .stExpander:hover, div[data-testid="stForm"]:hover, .kpi-card:hover, .upload-container:hover, .als-header-bar:hover {
            box-shadow: 0 0 20px rgba(19, 118, 89, 0.28) !important;
            border-color: #137659 !important;
        }
        
        /* Reducir espacios libres para máxima compactación de panel */
        [data-testid="stMainBlockContainer"] {
            padding: 0.2rem 0.6rem !important;
        }
        div.block-container {
            padding-top: 0.1rem !important;
            padding-bottom: 0.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    

def inject_custom_css():
    _apply_styles_internal()

def render_hud_table(df, table_id="hud_table"):
    """Renderiza un DataFrame como una tabla HTML con estilo corporativo Parex y DataTables."""
    if df.empty:
        st.info("Sin datos para mostrar.")
        return

    # Convertir a HTML
    html_table = df.to_html(index=False, table_id=table_id, classes='display nowrap hud-table')
    
    st.components.v1.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap');
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        @import url('https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css');
        
        body {{ background: transparent; color: #1f221e; font-family: 'Montserrat', sans-serif; }}
        .dataTables_wrapper {{ color: #1f221e !important; }}
        .dataTables_filter input {{ background: #ffffff; border: 1px solid #137659; color: #1f221e; border-radius: 5px; padding: 5px; }}
        
        /* Botón */
        button.dt-button {{
            background: rgba(19, 118, 89, 0.08) !important;
            border: 1px solid rgba(19, 118, 89, 0.4) !important;
            color: #137659 !important;
            font-family: 'Montserrat' !important;
            font-size: 10px !important;
            padding: 5px 15px !important;
            border-radius: 20px !important;
            text-transform: uppercase !important;
            cursor: pointer;
            transition: 0.3s;
        }}
        button.dt-button:hover {{
            background: #137659 !important;
            color: #ffffff !important;
            box-shadow: 0 0 10px rgba(19, 118, 89, 0.2);
        }}

        table.dataTable thead th {{ background: rgba(19, 118, 89, 0.1); color: #137659; font-family: 'Montserrat'; font-size: 11px; }}
        table.dataTable tbody td {{ border-bottom: 1px solid rgba(19, 118, 89, 0.08); padding: 8px; font-size: 12px; color: #1f221e; }}
        .dataTables_info, .dataTables_paginate {{ color: #5b5c55 !important; font-size: 11px; }}
    </style>
    
    <div style="background: #ffffff; padding:10px; border:1px solid rgba(19, 118, 89, 0.2); border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.03);">
        {html_table}
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('#{table_id}').DataTable({{
                "pageLength": 10,
                "order": [],
                "language": {{ "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                "dom": 'Bfrtip',
                "buttons": [
                    {{
                        extend: 'copy',
                        text: '📋 Copiar Tabla',
                        className: 'hud-copy-btn'
                    }}
                ]
            }});
        }});
    </script>
    """, height=520)

def apply_all_styles():
    _apply_styles_internal()

def show_success_box(msg: str):
    safe_msg = html_module.escape(str(msg))
    st.markdown(f"""
        <div style="background:rgba(21,128,61,0.08); border-left:5px solid #15803d; padding:15px; border-radius:8px; margin:10px 0;">
            <div style="color:#15803d; font-family:'Montserrat'; font-size:0.7rem; font-weight:700; letter-spacing:2px;">SISTEMA ONLINE</div>
            <div style="color:#1f221e; font-size:0.85rem; margin-top:5px;">{safe_msg}</div>
        </div>
    """, unsafe_allow_html=True)
