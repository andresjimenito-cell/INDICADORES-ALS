"""
styles.py
=========
Centraliza TODA la inyección de CSS de la aplicación con estética HUD Premium.
Implementa Estrategia "Zero Space Waste" y componentes de alta densidad.
Ahora con soporte para DataTables (Filtros, Ordenamiento y Copiado) en tablas HUD.
"""

import html as html_module
import streamlit as st
import json
import tema
from config import (
    COLOR_PRINCIPAL, COLOR_FUENTE, COLOR_FONDO_OSCURO, COLOR_FONDO_CONTENEDOR,
    COLOR_MAGENTA_NEON, COLOR_AZUL_CIBER, COLOR_GLOW_SUAVE,
)

def _apply_styles_internal():
    """Lógica central de inyección de estilos HUD."""
    st.markdown(f"""
    <style>

        
        /* DataTables HUD Theme Integration */
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        @import url('https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css');

        [data-testid="stAppViewContainer"] {{ 
            padding: 0 !important; 
            margin: 0 !important; 
            background-color: #060a1e !important;
        }}
        [data-testid="stMainBlockContainer"] {{ 
            padding: 0rem 1rem !important; 
            max-width: 100% !important;
        }}

        /* FORZAR SIDEBAR ABIERTO (styles.py) */
        [data-testid="stSidebar"] {{
            left: 0 !important;
            transform: none !important;
            visibility: visible !important;
            min-width: 220px !important;
            max-width: 220px !important;
            display: block !important;
        }}
        [data-testid="stAppViewContainer"] {{
            display: flex !important;
            flex-direction: row !important;
        }}
        [data-testid="stAppViewContainer"] > section:nth-child(2) {{
            margin-left: 220px !important;
            min-width: calc(100% - 220px) !important;
        }}
        
        /* Ocultar elementos de Streamlit para ganar espacio */
        header[data-testid="stHeader"] {{ display: none !important; }}
        footer {{ display: none !important; }}
        #MainMenu {{ display: none !important; }}
        
        /* Reducir espacio entre bloques de Streamlit */
        div.block-container {{
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
        }}
        div[data-testid="stVerticalBlock"] > div {{
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
        }}
        div[data-testid="stVerticalBlock"] {{
            gap: 0.15rem !important;
        }}
        
        /* Espacio superior de los contenidos de las pestañas */
        div[data-testid="stTabContent"] {{
            padding-top: 0rem !important;
        }}
        
        /* Eliminar márgenes de los widgets de Streamlit */
        .stMarkdown, .stMetric, .stSelectbox {{
            margin-bottom: 0rem !important;
        }}
        
        .stApp {{
            background-color: #060a1e !important;
            font-family: 'Arial', sans-serif !important;
        }}

        /* --- Sidebar Selectbox Premium Style --- */
        [data-testid="stSidebar"] .stSelectbox {{
            margin-top: 0px !important;
        }}
        [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
            gap: 0rem !important;
        }}
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(0, 217, 255, 0.15) !important;
            border-radius: 8px !important;
            color: #fff !important;
        }}
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {{
            border-color: #00f2ff !important;
            box-shadow: 0 0 10px rgba(0, 242, 255, 0.1) !important;
        }}
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {{
            color: #fff !important;
            font-size: 0.85rem !important;
        }}

        .kpi-card {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.6), rgba(2, 6, 23, 0.85));
            border: 1px solid rgba(0, 242, 255, 0.15);
            border-radius: 12px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            backdrop-filter: blur(4px);
            margin-bottom: 10px;
            font-family: 'Arial', sans-serif !important;
        }}
        .kpi-label {{
            font-size: 0.65rem;
            color: #94a3b8;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: 800;
            line-height: 1.2;
        }}
        .kpi-icon {{
            font-size: 1.2rem;
            margin-bottom: 8px;
        }}
        
        /* --- DataTables HUD Customization --- */
        .dataTables_wrapper {{
            color: #fff !important;
            font-family: 'Arial', sans-serif !important;
        }}
        .dataTables_filter input {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid #00f2ff !important;
            color: #fff !important;
            border-radius: 5px !important;
            padding: 4px 10px !important;
            outline: none !important;
        }}
        
        /* Estilo para el botón de Copiar HUD */
        button.dt-button, div.dt-button, a.dt-button {{
            background: rgba(0, 242, 255, 0.1) !important;
            border: 1px solid rgba(0, 242, 255, 0.4) !important;
            color: #00f2ff !important;
            font-family: 'Arial', sans-serif !important;
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            padding: 4px 12px !important;
            border-radius: 4px !important;
            transition: all 0.3s !important;
            margin-bottom: 10px !important;
        }}
        button.dt-button:hover {{
            background: #00f2ff !important;
            color: #000 !important;
            box-shadow: 0 0 15px rgba(0, 242, 255, 0.4) !important;
        }}

        table.dataTable thead th {{
            background: rgba(0, 242, 255, 0.1) !important;
            color: #00f2ff !important;
            font-family: 'Orbitron', sans-serif !important;
            border-bottom: 1px solid #00f2ff !important;
        }}
        table.dataTable tbody td {{
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        }}
        
        .dataTables_paginate .paginate_button {{
            color: #94a3b8 !important;
        }}
        .dataTables_paginate .paginate_button.current {{
            background: rgba(0, 242, 255, 0.2) !important;
            border-color: #00f2ff !important;
            color: #00f2ff !important;
        }}

        /* --- HUD Upload Section Styles --- */
        .upload-container {{
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(0, 217, 255, 0.1);
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
            backdrop-filter: blur(8px);
        }}
        .compact-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .compact-card span {{
            font-family: 'Orbitron', sans-serif;
            font-size: 0.65rem;
            font-weight: 700;
            color: #00D9FF;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .upload-area {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px dashed rgba(0, 217, 255, 0.2);
            border-radius: 8px;
            padding: 4px;
            transition: all 0.3s;
        }}
        .upload-area:hover {{
            border-color: #00D9FF;
            background: rgba(0, 217, 255, 0.05);
        }}
        
        /* Ajustes para inputs de Streamlit dentro de tarjetas */
        .stTextInput input, .stDateInput input {{
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #fff !important;
            font-size: 0.8rem !important;
        }}
        .stTextInput label, .stDateInput label {{
            font-size: 0.6rem !important;
            color: #64748B !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }}
        
        .fecha-alerta {{
            background: linear-gradient(90deg, rgba(255, 0, 255, 0.1), transparent);
            border-left: 3px solid #FF00FF;
            padding: 8px 12px;
            border-radius: 4px;
            margin-top: 8px;
        }}

        /* Estilo para el Popover de Configuración (Botón Engranaje en Header) */
        div[data-testid="stPopover"] > button {{
            background: rgba(0, 217, 255, 0.1) !important;
            border: 1px solid rgba(0, 217, 255, 0.4) !important;
            color: #00D9FF !important;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            min-height: 30px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 1rem !important;
            transition: all 0.3s !important;
            margin: 0 !important;
            box-shadow: 0 0 10px rgba(0, 217, 255, 0.1) !important;
        }}
        div[data-testid="stPopover"] > button:hover {{
            box-shadow: 0 0 15px rgba(0, 217, 255, 0.3) !important;
            transform: rotate(45deg);
        }}

        /* Contenedor para controles de gráfica (Overlay) */
        div.chart-controls-wrapper {{
            position: relative;
            width: 100%;
        }}
        div.chart-controls-overlay {{
            position: absolute;
            top: 8px;
            right: 45px;
            z-index: 1001;
            pointer-events: none;
        }}
        div.chart-controls-overlay > div {{
            pointer-events: auto;
        }}
        div.chart-controls-overlay .stDownloadButton button {{
            background: rgba(15, 23, 42, 0.9) !important;
            border: 1px solid rgba(0, 242, 255, 0.4) !important;
            color: #00f2ff !important; /* Más visible */
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
            box-shadow: 0 0 5px rgba(0, 242, 255, 0.1) !important;
        }}
        div.chart-controls-overlay .stDownloadButton button:hover {{
            background: rgba(0, 242, 255, 0.1) !important;
            border-color: #00f2ff !important;
            color: #00f2ff !important;
        }}

        /* ── HUD FLOATING NAVIGATION (ESPECÍFICO PARA TABLIST) ── */
        div[data-testid="stTabs"] {{
            display: flex !important;
            flex-direction: column !important;
        }}

        div[data-testid="stTabs"] [role="tablist"] {{
            position: fixed !important;
            bottom: 30px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            z-index: 999999 !important;
            background: rgba(8, 12, 28, 0.9) !important;
            backdrop-filter: blur(15px) !important;
            padding: 5px 25px !important;
            border-radius: 50px !important;
            border: 1px solid rgba(0, 242, 255, 0.4) !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.8), 0 0 20px rgba(0, 242, 255, 0.2) !important;
            width: auto !important;
            min-width: 500px !important;
            display: flex !important;
            justify-content: center !important;
            gap: 15px !important;
            order: 2 !important; /* Mueve la barra al final del flujo */
        }}

        /* Asegurar que el contenido de los tabs NO se mueva con la barra y esté arriba */
        div[data-testid="stTabContent"] {{
            order: 1 !important;
            background: transparent !important;
            border: none !important;
            padding-top: 0px !important;
            width: 100% !important;
        }}

        /* Quitar la línea inferior por defecto de los tabs */
        div[data-testid="stTabs"] [role="tablist"] {{
            border: none !important;
        }}

        /* Estilo de cada botón de tab */
        div[data-testid="stTabs"] button[data-baseweb="tab"] {{
            background: transparent !important;
            border: none !important;
            padding: 8px 18px !important;
            color: #94a3b8 !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 0.7rem !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
            transition: all 0.3s !important;
            border-radius: 20px !important;
            height: auto !important;
        }}
        
        div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {{
            color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.05) !important;
        }}
        
        /* Tab seleccionado (Estado Activo) */
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.15) !important;
            border: 1px solid rgba(0, 242, 255, 0.3) !important;
            box-shadow: 0 0 15px rgba(0, 242, 255, 0.2) !important;
        }}

        /* Esconder la barra naranja/azul debajo del tab seleccionado */
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
            display: none !important;
        }}

        /* Remover el radio antiguo si quedara */
        div.stRadio.floating-nav-wrapper {{
            display: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    

def inject_custom_css():
    _apply_styles_internal()

def render_hud_table(df, table_id="hud_table"):
    """Renderiza un DataFrame como una tabla HTML con estilo HUD, DataTables y botón Copiar."""
    if df.empty:
        st.info("Sin datos para mostrar.")
        return

    # Convertir a HTML
    html_table = df.to_html(index=False, table_id=table_id, classes='display nowrap hud-table')
    
    st.components.v1.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;600&display=swap');
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        @import url('https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css');
        
        body {{ background: transparent; color: #fff; font-family: 'Rajdhani', sans-serif; }}
        .dataTables_wrapper {{ color: #fff !important; }}
        .dataTables_filter input {{ background: rgba(255,255,255,0.05); border: 1px solid #00f2ff; color: #fff; border-radius: 5px; padding: 5px; }}
        
        /* Botón HUD */
        button.dt-button {{
            background: rgba(0, 242, 255, 0.1) !important;
            border: 1px solid rgba(0, 242, 255, 0.5) !important;
            color: #00f2ff !important;
            font-family: 'Orbitron' !important;
            font-size: 10px !important;
            padding: 5px 15px !important;
            border-radius: 20px !important;
            text-transform: uppercase !important;
            cursor: pointer;
            transition: 0.3s;
        }}
        button.dt-button:hover {{
            background: #00f2ff !important;
            color: #000 !important;
            box-shadow: 0 0 10px #00f2ff;
        }}

        table.dataTable thead th {{ background: rgba(0, 242, 255, 0.1); color: #00f2ff; font-family: 'Orbitron'; font-size: 11px; }}
        table.dataTable tbody td {{ border-bottom: 1px solid rgba(255,255,255,0.05); padding: 8px; font-size: 13px; }}
        .dataTables_info, .dataTables_paginate {{ color: #94a3b8 !important; font-size: 11px; }}
    </style>
    
    <div style="background: rgba(6,10,30,0.8); padding:10px; border:1px solid rgba(0,242,255,0.3); border-radius:10px;">
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
        <div style="background:rgba(0,255,157,0.1); border-left:5px solid #00ff9d; padding:15px; border-radius:8px; margin:10px 0;">
            <div style="color:#00ff9d; font-family:'Orbitron'; font-size:0.7rem; letter-spacing:2px;">SISTEMA ONLINE</div>
            <div style="color:#fff; font-size:0.85rem; margin-top:5px;">{safe_msg}</div>
        </div>
    """, unsafe_allow_html=True)
