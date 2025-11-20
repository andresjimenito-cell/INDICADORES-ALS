# --- ESTILO PARA TABLAS ---
# Importar streamlit antes de usar 'st'
import streamlit as st
# ...existing code...
def mostrar_seccion_mtbf(df_bd_filtered, fecha_evaluacion):
    # ...no mostrar ids aquí, solo en el flujo principal...
    try:
        mtbf_global, mtbf_por_pozo = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        mostrar_mtbf(mtbf_global, mtbf_por_pozo, df_bd=df_bd_filtered, fecha_evaluacion=fecha_evaluacion)
    except Exception as e:
        st.warning(f"No se pudo calcular el MTBF: {e}")
def clasificar_razon_ia(razon):
    import unicodedata
    if not isinstance(razon, str):
        return 'Desconocida'
    # Normalizar acentos y pasar a minúsculas
    razon_norm = unicodedata.normalize('NFKD', razon).encode('ascii', 'ignore').decode('utf-8').lower()
    # Palabras clave ampliadas
    palabras_mecanica = ['mecanic', 'eje', 'rotura', 'desgaste', 'rodamient', 'sello', 'acople', 'engranaje', 'mecanico', 'mecanica']
    palabras_electrica = ['electri','bomba', 'cable', 'aislamiento', 'motor', 'corto', 'bobina', 'fase', 'desbalanceado', 'electrica', 'electrico', 'variador', 'tablero','aterrizado', 'control','ALS']
    palabras_tuberia = ['Tubería','casing', 'varilla','tubing', 'liner', 'fuga', 'pinchazo', 'conexion', 'tubo', 'perforacion']
    palabras_yacimiento = ['yacimiento','ABANDONO','agua','REDISEÑO','RECAÑONEO','WS','WO', 'solidos', 'arena', 'incrustacion', 'parafina', 'asfalteno', 'presion', 'flujo', 'formacion', 'economico','produccion']
    if any(word in razon_norm for word in palabras_mecanica):
        return 'Mecánica'
    if any(word in razon_norm for word in palabras_electrica):
        return 'Eléctrica'
    if any(word in razon_norm for word in palabras_tuberia):
        return 'Tubería'
    if any(word in razon_norm for word in palabras_yacimiento):
        return 'Yacimiento'
    return 'Otra'
import streamlit as st
import pandas as pd
import numpy as np
import io
from mtbf import calcular_mtbf, mostrar_mtbf
from kpis import mostrar_kpis
from indice_falla import calcular_indice_falla_anual
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import theme as _theme_mod

# =================== CONFIGURACIÓN DE TEMA Y COLORES ===================
COLOR_PRINCIPAL = getattr(_theme_mod, 'COLOR_PRINCIPAL', '#00ff99')
COLOR_FONDO_OSCURO = getattr(_theme_mod, 'COLOR_FONDO_OSCURO', '#0a0e27')
COLOR_FONDO_CONTENEDOR = getattr(_theme_mod, 'COLOR_FONDO_CONTENEDOR', 'rgba(15, 20, 40, 0.85)')
COLOR_SOMBRA = getattr(_theme_mod, 'COLOR_SOMBRA', 'rgba(0, 255, 153, 0.6)')
COLOR_FUENTE = getattr(_theme_mod, 'COLOR_FUENTE', '#E8F1F5')

# Colores adicionales para el diseño premium
COLOR_ACENTO_1 = '#00d4ff'
COLOR_ACENTO_2 = '#a855f7'
COLOR_ACENTO_3 = '#fbbf24'
COLOR_GRID = 'rgba(0, 255, 153, 0.08)'
COLOR_BORDE = 'rgba(0, 255, 153, 0.3)'

get_color_sequence = getattr(_theme_mod, 'get_color_sequence', lambda mode=None: [
    COLOR_PRINCIPAL, COLOR_ACENTO_2, COLOR_ACENTO_1, COLOR_ACENTO_3
])


def get_theme(mode: str = 'dark') -> dict:
    """
    Devuelve un diccionario con los colores y utilidades del tema.
    Si el módulo `theme` expone una función o variables, las usa; si no,
    devuelve valores por defecto ya definidos arriba.
    """
    return {
        'COLOR_PRINCIPAL': getattr(_theme_mod, 'COLOR_PRINCIPAL', COLOR_PRINCIPAL),
        'COLOR_FUENTE': getattr(_theme_mod, 'COLOR_FUENTE', COLOR_FUENTE),
        'COLOR_FONDO_OSCURO': getattr(_theme_mod, 'COLOR_FONDO_OSCURO', COLOR_FONDO_OSCURO),
        'COLOR_FONDO_CONTENEDOR': getattr(_theme_mod, 'COLOR_FONDO_CONTENEDOR', COLOR_FONDO_CONTENEDOR),
        'COLOR_SOMBRA': getattr(_theme_mod, 'COLOR_SOMBRA', COLOR_SOMBRA),
        'get_color_sequence': getattr(_theme_mod, 'get_color_sequence', lambda mode=None: [
            COLOR_PRINCIPAL, COLOR_ACENTO_2, COLOR_ACENTO_1, COLOR_ACENTO_3
        ])
    }


def get_plotly_layout(xaxis_color: str = None, yaxis_color: str = None) -> dict:
    """
    Devuelve un layout base para Plotly. Usa la implementación en `theme.py` si existe,
    de lo contrario construye un layout por defecto coherente con los colores del archivo.
    """
    try:
        # Si el módulo theme define la función, la usamos directamente
        if hasattr(_theme_mod, 'get_plotly_layout') and callable(_theme_mod.get_plotly_layout):
            return _theme_mod.get_plotly_layout(xaxis_color, yaxis_color)
    except Exception:
        # Si falla por alguna razón, seguimos con el layout por defecto
        pass

    xa = xaxis_color or COLOR_PRINCIPAL
    ya = yaxis_color or COLOR_PRINCIPAL

    borde_shape = {
        'type': 'rect',
        'xref': 'paper',
        'yref': 'paper',
        'x0': 0,
        'y0': 0,
        'x1': 1,
        'y1': 1,
        'line': {'color': COLOR_PRINCIPAL, 'width': 1},
        'layer': 'below'
    }

    return {
        'plot_bgcolor': COLOR_FONDO_OSCURO,
        'paper_bgcolor': COLOR_FONDO_OSCURO,
        'font_color': COLOR_FUENTE,
        'title_font_color': COLOR_PRINCIPAL,
        'xaxis': {'color': xa, 'gridcolor': COLOR_GRID},
        'yaxis': {'color': ya, 'gridcolor': COLOR_GRID},
        'shapes': [borde_shape]
    }

# =================== ESTILOS CSS MEJORADOS ===================
st.set_page_config(page_title="🚀 Indicadores ALS Premium", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    /* ============ FONDO PRINCIPAL CON EFECTO DE PROFUNDIDAD ============ */
    .stApp {{
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        background-attachment: fixed;
        font-family: 'Rajdhani', sans-serif;
        color: {COLOR_FUENTE};
    }}
    
    /* Grid pattern overlay para efecto tech */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(0deg, transparent 24%, {COLOR_GRID} 25%, {COLOR_GRID} 26%, transparent 27%, transparent 74%, {COLOR_GRID} 75%, {COLOR_GRID} 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, {COLOR_GRID} 25%, {COLOR_GRID} 26%, transparent 27%, transparent 74%, {COLOR_GRID} 75%, {COLOR_GRID} 76%, transparent 77%, transparent);
        background-size: 50px 50px;
        pointer-events: none;
        opacity: 0.4;
        z-index: 0;
    }}
    
    /* ============ HEADER CON EFECTO HOLOGRÁFICO ============ */
    h1, h2, h3 {{
        font-family: 'Orbitron', sans-serif !important;
        background: linear-gradient(135deg, {COLOR_PRINCIPAL} 0%, {COLOR_ACENTO_1} 50%, {COLOR_ACENTO_2} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px {COLOR_SOMBRA};
        letter-spacing: 2px;
        position: relative;
    }}
    
    h1 {{
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        margin-bottom: 0.3rem !important;
        animation: glow-pulse 3s ease-in-out infinite;
    }}
    
    @keyframes glow-pulse {{
        0%, 100% {{ filter: drop-shadow(0 0 20px {COLOR_SOMBRA}); }}
        50% {{ filter: drop-shadow(0 0 40px {COLOR_PRINCIPAL}); }}
    }}
    
    /* ============ TARJETAS PREMIUM CON GLASSMORPHISM ============ */
    div[data-testid="stMetric"] {{
        background: linear-gradient(135deg, 
            rgba(15, 20, 40, 0.7) 0%, 
            rgba(20, 30, 50, 0.5) 100%);
        backdrop-filter: blur(15px) saturate(180%);
        border: 1px solid {COLOR_BORDE};
        border-radius: 20px;
        padding: 25px 20px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1),
            0 0 20px {COLOR_SOMBRA};
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    /* Efecto de línea animada en el borde */
    div[data-testid="stMetric"]::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, {COLOR_PRINCIPAL}, transparent);
        transition: left 0.5s;
    }}
    
    div[data-testid="stMetric"]:hover::before {{
        left: 100%;
    }}
    
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-8px) scale(1.02);
        border-color: {COLOR_PRINCIPAL};
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.6),
            0 0 40px {COLOR_SOMBRA},
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }}
    
    /* Labels de métricas */
    div[data-testid="stMetric"] label {{
        color: {COLOR_ACENTO_1} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }}
    
    /* Valores de métricas */
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {COLOR_PRINCIPAL} !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        font-family: 'Orbitron', monospace !important;
        text-shadow: 0 0 15px {COLOR_SOMBRA};
    }}
    
    /* ============ CONTENEDORES Y EXPANDERS ============ */
    .element-container {{
        position: relative;
        z-index: 1;
    }}
    
    [data-testid="stExpander"] {{
        background: linear-gradient(135deg, 
            rgba(10, 15, 30, 0.9) 0%, 
            rgba(20, 25, 45, 0.7) 100%);
        border: 1px solid {COLOR_BORDE};
        border-radius: 15px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 15px 0;
    }}
    
    [data-testid="stExpander"]:hover {{
        border-color: {COLOR_PRINCIPAL};
        box-shadow: 0 8px 32px rgba(0, 255, 153, 0.2);
    }}
    
    /* ============ TABLAS ESTILIZADAS ============ */
    .stDataFrame {{
        background: rgba(10, 15, 30, 0.95) !important;
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
        border: 1px solid {COLOR_BORDE} !important;
    }}
    
    .stDataFrame table {{
        background: transparent !important;
    }}
    
    .stDataFrame thead tr th {{
        background: linear-gradient(135deg, 
            rgba(0, 255, 153, 0.2) 0%, 
            rgba(0, 212, 255, 0.1) 100%) !important;
        color: {COLOR_PRINCIPAL} !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 15px 10px !important;
        border-bottom: 2px solid {COLOR_PRINCIPAL} !important;
    }}
    
    .stDataFrame tbody tr {{
        transition: all 0.3s ease;
    }}
    
    .stDataFrame tbody tr:hover {{
        background: rgba(0, 255, 153, 0.08) !important;
        transform: scale(1.01);
    }}
    
    .stDataFrame tbody tr td {{
        color: {COLOR_FUENTE} !important;
        padding: 12px 10px !important;
        border-bottom: 1px solid rgba(0, 255, 153, 0.1) !important;
    }}
    
    /* ============ BOTONES PREMIUM ============ */
    .stButton>button {{
        background: linear-gradient(135deg, 
            rgba(0, 255, 153, 0.2) 0%, 
            rgba(0, 212, 255, 0.2) 100%);
        color: {COLOR_PRINCIPAL} !important;
        border: 2px solid {COLOR_PRINCIPAL};
        border-radius: 12px;
        padding: 15px 30px;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 255, 153, 0.3);
    }}
    
    .stButton>button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(0, 255, 153, 0.4);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }}
    
    .stButton>button:hover::before {{
        width: 300px;
        height: 300px;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, 
            {COLOR_PRINCIPAL} 0%, 
            {COLOR_ACENTO_1} 100%);
        color: {COLOR_FONDO_OSCURO} !important;
        border-color: {COLOR_PRINCIPAL};
        box-shadow: 0 8px 30px rgba(0, 255, 153, 0.6);
        transform: translateY(-3px);
    }}
    
    /* ============ INPUTS Y SELECTBOX ============ */
    .stSelectbox>div>div, 
    .stDateInput>div>input,
    .stTextInput>div>div>input,
    .stFileUploader {{
        background: rgba(15, 20, 40, 0.8) !important;
        border: 2px solid {COLOR_BORDE} !important;
        border-radius: 10px !important;
        color: {COLOR_FUENTE} !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }}
    
    .stSelectbox>div>div:focus-within,
    .stDateInput>div>input:focus,
    .stTextInput>div>div>input:focus,
    .stFileUploader:focus-within {{
        border-color: {COLOR_PRINCIPAL} !important;
        box-shadow: 0 0 20px {COLOR_SOMBRA} !important;
        background: rgba(15, 20, 40, 0.95) !important;
    }}
    
    /* ============ SIDEBAR PREMIUM ============ */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, 
            rgba(10, 15, 30, 0.98) 0%, 
            rgba(15, 20, 40, 0.95) 100%);
        border-right: 2px solid {COLOR_BORDE};
        backdrop-filter: blur(10px);
    }}
    
    [data-testid="stSidebar"] .sidebar-link {{
        background: rgba(0, 255, 153, 0.05);
        border-left: 3px solid transparent;
        border-radius: 0 10px 10px 0;
        padding: 12px 15px;
        margin: 8px 0;
        transition: all 0.3s ease;
        color: {COLOR_FUENTE} !important;
        text-decoration: none !important;
    }}
    
    [data-testid="stSidebar"] .sidebar-link:hover {{
        background: rgba(0, 255, 153, 0.15);
        border-left-color: {COLOR_PRINCIPAL};
        transform: translateX(8px);
        box-shadow: 0 4px 15px rgba(0, 255, 153, 0.3);
        color: {COLOR_PRINCIPAL} !important;
    }}
    
    /* ============ SEPARADORES CON EFECTO GLOW ============ */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            {COLOR_PRINCIPAL} 50%, 
            transparent 100%);
        box-shadow: 0 0 10px {COLOR_SOMBRA};
        margin: 3rem 0;
        opacity: 0.8;
    }}
    
    /* ============ CONTENEDORES COMPACTOS ============ */
    .compact-card {{
        background: linear-gradient(135deg, 
            rgba(15, 20, 40, 0.9) 0%, 
            rgba(20, 30, 50, 0.7) 100%);
        border: 1px solid {COLOR_BORDE};
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }}
    
    .compact-card:hover {{
        border-color: {COLOR_PRINCIPAL};
        box-shadow: 0 12px 40px rgba(0, 255, 153, 0.2);
        transform: translateY(-5px);
    }}
    
    .compact-card span {{
        color: {COLOR_PRINCIPAL};
        font-weight: 700;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }}
    
    /* ============ ALERTAS PERSONALIZADAS ============ */
    .stAlert {{
        background: linear-gradient(135deg, 
            rgba(0, 255, 153, 0.1) 0%, 
            rgba(0, 212, 255, 0.05) 100%) !important;
        border-left: 4px solid {COLOR_PRINCIPAL} !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px) !important;
        color: {COLOR_FUENTE} !important;
    }}
    
    /* ============ ANIMACIONES Y EFECTOS ============ */
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    @keyframes pulse-border {{
        0%, 100% {{ border-color: {COLOR_BORDE}; }}
        50% {{ border-color: {COLOR_PRINCIPAL}; }}
    }}
    
    /* ============ SCROLLBAR PERSONALIZADO ============ */
    ::-webkit-scrollbar {{
        width: 12px;
        height: 12px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(10, 15, 30, 0.5);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, {COLOR_PRINCIPAL} 0%, {COLOR_ACENTO_1} 100%);
        border-radius: 10px;
        border: 2px solid rgba(10, 15, 30, 0.5);
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, {COLOR_ACENTO_1} 0%, {COLOR_PRINCIPAL} 100%);
    }}
    
    /* ============ PLOTLY CHARTS PERSONALIZADOS ============ */
    .js-plotly-plot {{
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 1px solid {COLOR_BORDE};
    }}
</style>
""", unsafe_allow_html=True)

# =================== FUNCIONES AUXILIARES (mantener igual) ===================
def styled_title(text: str) -> str:
    return f"<span style=\"color:{COLOR_PRINCIPAL}; text-shadow: 0 0 5px {COLOR_SOMBRA};\">{text}</span>"
# ======================================================================================
# Funciones de Procesamiento de Datos
# ======================================================================================
@st.cache_data
def find_header(file_obj, keywords, max_rows=50):
    """
    Busca la fila del encabezado que contiene todas las palabras clave dadas.
    """
    file_obj.seek(0)
    file_type = file_obj.name.split('.')[-1]
    for i in range(max_rows):
        try:
            if file_type == 'xlsx':
                temp_df = pd.read_excel(file_obj, nrows=1, header=None, skiprows=i)
            else:
                temp_file = io.BytesIO(file_obj.getvalue())
                temp_df = pd.read_csv(temp_file, nrows=1, header=None, skiprows=i, encoding='latin1', on_bad_lines='skip')
            
            normalized_cols = [str(c).upper().strip().replace('.', '').replace('#', '') for c in temp_df.iloc[0].tolist() if pd.notna(c)]
            
            if all(any(keyword.upper().strip() in col for col in normalized_cols) for keyword in keywords):
                file_obj.seek(0)
                return i
            file_obj.seek(0)
        except Exception:
            file_obj.seek(0)
            continue
    return None

@st.cache_data
def cargar_y_limpiar_datos(forma9_file, bd_file):
    """
    Carga y limpia los DataFrames de FORMA 9 y BD, estandarizando nombres de columnas.
    """
    if forma9_file is None or bd_file is None:
        return None, None
    
    try:
        forma9_header_row = find_header(forma9_file, ['FECHA', 'DIAS', 'POZO'])
        if forma9_header_row is None:
            st.error("No se pudo encontrar el encabezado en el archivo FORMA 9. Asegúrate de que las columnas 'FECHA', 'DIAS' y 'POZO' estén presentes.")
            return None, None
        
        bd_header_row = find_header(bd_file, ['RUN', 'FECHA RUN', 'POZO'])
        if bd_header_row is None:
            st.error("No se pudo encontrar el encabezado en el archivo BD. Asegúrate de que las columnas '# RUN', 'FECHA RUN' y 'POZO' estén presentes.")
            return None, None
            
        if forma9_file.name.endswith('.csv'):
            df_forma9 = pd.read_csv(forma9_file, header=forma9_header_row, encoding='latin1', low_memory=False)
        else:
            df_forma9 = pd.read_excel(forma9_file, header=forma9_header_row)

        if bd_file.name.endswith('.csv'):
            df_bd = pd.read_csv(bd_file, header=bd_header_row, encoding='latin1', low_memory=False)
        else:
            df_bd = pd.read_excel(bd_file, header=bd_header_row)

    except Exception as e:
        st.error(f"Error al leer los archivos. Revisa que el formato sea el correcto y que no estén corruptos: {e}.")
        return None, None
    
    # --- Limpieza y estandarización en FORMA 9 ---
    df_forma9.columns = [str(col).upper().strip().replace('#', '').replace('.', '').replace('POZO NO', 'POZO') for col in df_forma9.columns]
    
    fecha_col_forma9 = next((col for col in df_forma9.columns if 'FECHA' in col), None)
    dias_col = next((col for col in df_forma9.columns if 'DIAS' in col), None)
    pozo_col_forma9 = next((col for col in df_forma9.columns if 'POZO' in col), None)
    
    df_forma9.rename(columns={fecha_col_forma9: 'FECHA_FORMA9', dias_col: 'DIAS TRABAJADOS',
                              pozo_col_forma9: 'POZO'}, inplace=True)
    df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
    df_forma9['DIAS TRABAJADOS'] = pd.to_numeric(df_forma9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
    df_forma9.dropna(subset=['FECHA_FORMA9', 'POZO'], inplace=True)

    # --- Limpieza y estandarización en BD ---
    df_bd.columns = [str(col).upper().strip().replace('#', '').replace('.', '') for col in df_bd.columns]
    
    run_col_bd = next((col for col in df_bd.columns if 'RUN' in col), None)
    fecha_run_col = next((col for col in df_bd.columns if 'FECHA RUN' in col), None)
    pozo_col_bd = next((col for col in df_bd.columns if 'POZO' in col), None)
    fecha_falla_col = next((col for col in df_bd.columns if 'FECHA FALLA' in col), None)
    fecha_pull_col = next((col for col in df_bd.columns if 'FECHA PULL' in col), None)
    operando_col = next((col for col in df_bd.columns if 'OPERANDO' in col), None)
    indicador_col = next((col for col in df_bd.columns if 'INDICADOR MTBF' in col), None)
    proveedor_col = next((col for col in df_bd.columns if 'PROVEEDOR' in col), None)
    als_col = next((col for col in df_bd.columns if 'ALS' in col), None)
    activo_col = next((col for col in df_bd.columns if 'ACTIVO' in col), None)
    severidad_col = next((col for col in df_bd.columns if 'SEVERIDAD' in col.upper() or 'SEVERIDAD' in col.upper()), None)

    df_bd.rename(columns={run_col_bd: 'RUN', fecha_run_col: 'FECHA_RUN', 
                              fecha_falla_col: 'FECHA_FALLA', fecha_pull_col: 'FECHA_PULL',
                              operando_col: 'OPERANDO_ESTADO', indicador_col: 'INDICADOR_MTBF',
                              pozo_col_bd: 'POZO', proveedor_col:'PROVEEDOR', als_col:'ALS', activo_col:'ACTIVO',
                              severidad_col:'SEVERIDAD'}, inplace=True)
    
    df_bd['FECHA_RUN'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')
    df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    df_bd['FECHA_PULL'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce')
    df_bd['INDICADOR_MTBF'] = pd.to_numeric(df_bd['INDICADOR_MTBF'], errors='coerce').fillna(0)
    
    if 'SEVERIDAD' in df_bd.columns:
        df_bd['SEVERIDAD'] = pd.to_numeric(df_bd['SEVERIDAD'], errors='coerce').fillna(0)
    else:
        st.warning("Columna 'SEVERIDAD' no encontrada en el archivo BD. Los cálculos relacionados no se mostrarán.")
        df_bd['SEVERIDAD'] = np.nan
        
    df_bd.dropna(subset=['FECHA_RUN', 'POZO'], inplace=True)
    
    return df_forma9, df_bd

def perform_initial_calculations(df_forma9, df_bd, fecha_evaluacion):
    """
    Realiza los cálculos iniciales en BD y luego en FORMA 9 de manera vectorizada y eficiente,
    basado en una fecha de evaluación.
    """
    fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
    
    df_bd['RUN LIFE'] = np.where(
        df_bd['FECHA_FALLA'].notna(),
        (df_bd['FECHA_FALLA'] - df_bd['FECHA_RUN']).dt.days,
        np.where(
            df_bd['FECHA_PULL'].notna(),
            (df_bd['FECHA_PULL'] - df_bd['FECHA_RUN']).dt.days,
            np.where(
                df_bd['FECHA_PULL'].isna(),
                (fecha_evaluacion - df_bd['FECHA_RUN']).dt.days,
                np.nan
            )
        )
    )

    df_bd['NICK'] = df_bd['POZO'].astype(str) + '-' + df_bd['RUN'].astype(str)
    
    df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'])
    
    df_forma9_copy = df_forma9.copy()
    
    df_bd_filtered = df_bd[df_bd['FECHA_RUN'] <= fecha_evaluacion].copy()

    merged_df = pd.merge(df_forma9_copy.reset_index(), df_bd_filtered[['POZO', 'RUN', 'PROVEEDOR', 'FECHA_RUN', 'FECHA_PULL']], on='POZO', how='left')
    
    merged_df['is_match'] = (merged_df['FECHA_FORMA9'] >= merged_df['FECHA_RUN']) & \
                             (merged_df['FECHA_FORMA9'] < merged_df['FECHA_PULL'].fillna(pd.to_datetime(fecha_evaluacion)))
    
    best_matches_idx = merged_df[merged_df['is_match']].groupby('index')['FECHA_RUN'].idxmax()
    
    best_matches_df = merged_df.loc[best_matches_idx]
    
    df_forma9_copy['RUN'] = best_matches_df.set_index('index')['RUN']
    df_forma9_copy['PROVEEDOR'] = best_matches_df.set_index('index')['PROVEEDOR']
    
    df_forma9_copy[['RUN', 'PROVEEDOR']] = df_forma9_copy[['RUN', 'PROVEEDOR']].fillna('NO DATA✍️')

    df_forma9_copy['NICK'] = df_forma9_copy['POZO'].astype(str) + '-' + df_forma9_copy['RUN'].astype(str)

    return df_forma9_copy, df_bd

def calcular_indicadores_finales(df_forma9, df_bd):
    run_life_operativo = df_forma9.groupby('NICK')['DIAS TRABAJADOS'].sum().reset_index()
    run_life_operativo.rename(columns={'DIAS TRABAJADOS': 'RUN LIFE OPERATIVO'}, inplace=True)
    df_bd = pd.merge(df_bd, run_life_operativo, on='NICK', how='left').fillna({'RUN LIFE OPERATIVO': 0})
    
    df_fallas = df_bd[df_bd['FECHA_FALLA'].notna()].copy()
    df_fallas['MES'] = df_fallas['FECHA_FALLA'].dt.to_period('M')
    
    fallas_mensuales = df_fallas.groupby('MES')['NICK'].count().reset_index()
    fallas_mensuales.rename(columns={'NICK': 'Numero de Fallas'}, inplace=True)
    fallas_mensuales['MES'] = fallas_mensuales['MES'].dt.to_timestamp()

    df_trabajo = df_bd.copy()
    
    return df_trabajo, fallas_mensuales

def generar_reporte_completo(df_bd, df_forma9, fecha_evaluacion):
    """
    Genera el reporte de RUNES. Todos los cálculos están anclados a la fecha de evaluación.
    """
    fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
    
    df_bd['FECHA_PULL_DATE'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce')
    df_bd['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    df_bd['FECHA_RUN_DATE'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')

    df_bd_eval = df_bd[df_bd['FECHA_RUN_DATE'].dt.date <= fecha_evaluacion.date()].copy()
    
    extraidos_count = df_bd_eval[df_bd_eval['FECHA_PULL_DATE'].dt.date <= fecha_evaluacion.date()].shape[0]

    running_count = df_bd_eval[
        (df_bd_eval['FECHA_RUN_DATE'].dt.date <= fecha_evaluacion.date()) &
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.date > fecha_evaluacion.date()))
    ].shape[0]

    fallados_count = df_bd_eval[
        (df_bd_eval['FECHA_FALLA_DATE'].dt.date <= fecha_evaluacion.date()) &
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.date > fecha_evaluacion.date()))
    ].shape[0]

    pozos_operativos = df_bd_eval[
        (df_bd_eval['FECHA_FALLA_DATE'].isna() | (df_bd_eval['FECHA_FALLA_DATE'].dt.date > fecha_evaluacion.date())) & 
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.date > fecha_evaluacion.date()))
    ].shape[0]

    df_forma9_eval = df_forma9[
        (df_forma9['FECHA_FORMA9'].dt.date >= (fecha_evaluacion.date() - timedelta(days=30))) &
        (df_forma9['FECHA_FORMA9'].dt.date <= fecha_evaluacion.date())
    ]
    pozos_on = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()

    pozos_off = abs(pozos_operativos - pozos_on)

    totales_count = extraidos_count + running_count

    reporte_runes = pd.DataFrame({
        'Categoría': ['Extraídos', 'Running', 'Fallados', 'Pozos ON', 'Pozos OFF', 'Pozos Operativos', 'Totales'],
        'Conteo': [extraidos_count, running_count, fallados_count, pozos_on, pozos_off, pozos_operativos, totales_count]
    })
    
    verificaciones = {
        'On + Off = Operativos': pozos_on + pozos_off == pozos_operativos,
        'Fallados + Operativos = Running': fallados_count + pozos_operativos == running_count,
        'Running + Extraídos = Totales': running_count + extraidos_count == totales_count
    }

    run_life_apagados_fallados = df_bd_eval[
        (df_bd_eval['FECHA_PULL_DATE'].notna()) | (df_bd_eval['FECHA_FALLA_DATE'].notna())
    ]['RUN LIFE'].mean()
    
    reporte_run_life = pd.DataFrame({
        'Categoría': ['Run Life Apagados + Fallados'],
        'Valor': [run_life_apagados_fallados]
    })
    
    return reporte_runes, reporte_run_life, verificaciones

def generar_historico_run_life(df_bd_calculated, fecha_evaluacion):
    """
    Calcula el run life promedio mensual por ACTIVO considerando todos los RUNs activos en cada mes.
    """
    end_date = pd.to_datetime(fecha_evaluacion)
    start_date = end_date - timedelta(days=365 * 3)
    meses = pd.date_range(start=start_date, end=end_date, freq='MS')
    historico = []

    for mes in meses:
        fin_mes = mes + pd.offsets.MonthEnd(0)
        activos_mes = df_bd_calculated[
            (df_bd_calculated['FECHA_RUN'] <= fin_mes) &
            (
                (df_bd_calculated['FECHA_PULL'].isna() | (df_bd_calculated['FECHA_PULL'] > fin_mes)) &
                (df_bd_calculated['FECHA_FALLA'].isna() | (df_bd_calculated['FECHA_FALLA'] > fin_mes))
            )
        ].copy()
        if not activos_mes.empty:
            activos_mes['RUN_LIFE_MES'] = (fin_mes - activos_mes['FECHA_RUN']).dt.days
            promedio = activos_mes.groupby('ACTIVO')['RUN_LIFE_MES'].mean().reset_index()
            promedio['Mes'] = fin_mes
            historico.append(promedio)
    if historico:
        df_historico = pd.concat(historico, ignore_index=True)
        df_historico = df_historico[['Mes', 'ACTIVO', 'RUN_LIFE_MES']]
        df_historico.rename(columns={'RUN_LIFE_MES': 'Run Life Promedio'}, inplace=True)
        return df_historico
    else:
        return pd.DataFrame(columns=['Mes', 'ACTIVO', 'Run Life Promedio'])


def highlight_problema(s):
    """
    Función para estilizar las filas con más de una falla.
    """
    is_problema = s['Cantidad de Fallas'] > 1
    if is_problema:
        # Personaliza aquí el color de fondo y texto
        return [f'background-color: {COLOR_PRINCIPAL}; color:{COLOR_FUENTE}; font-weight: bold;'] * len(s)
    else:
        return [''] * len(s)

st.set_page_config(page_title="🚀 Indicadores ALS", layout="wide")

# Título principal y logo grande
# ==================================================================================
# Colores provistos por `theme.py` importados arriba

st.markdown(
    f"""
    <style>
   /* Estilo general del App y Fondo (CON DEGRADADO) */
body, .stApp {{
    /* Aplicar un degradado lineal sutil de arriba (más oscuro) a abajo (menos oscuro) */
    background: linear-gradient(
        to bottom, 
        {COLOR_FONDO_OSCURO} 80%, 
        {COLOR_FONDO_CONTENEDOR} 100%
    ) !important;
    
    color: {COLOR_FUENTE} !important;
    font-family: 'Montserrat', 'Segoe UI', 'Roboto', 'Arial', sans-serif;
}}
.stApp {{
    max-width: none;
    background-color: transparent; /* Asegura que el contenedor no oculte el degradado del body */
}}
    .stApp {{max-width: none;}} /* Para aprovechar el ancho completo */
    
    /* Títulos y Encabezados */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_PRINCIPAL} !important;
        letter-spacing: 1px;
        text-shadow: 0 0 5px rgba(0, 255, 153, 0.3); /* Sombra de texto suave */
    }}
    
    /* Título Principal (h1) */
    .stMarkdown h1 {{
        font-size: 3.8rem; 
        font-weight: 700; 
        color: {COLOR_FUENTE} !important; 
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
    }}

    /* Tarjetas de Métricas (stMetric) - Glassmorphism Elegante */
    div[data-testid="stMetric"] {{
        background: {COLOR_FONDO_CONTENEDOR}; /* Fondo semi-transparente */
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4), 0 0 10px {COLOR_SOMBRA}; /* Sombra oscura + borde sutil */
        padding: 15px;
        margin-bottom: 12px;
        border-left: 5px solid {COLOR_PRINCIPAL}; /* Barra de acento lateral */
        transition: transform 0.2s;
        backdrop-filter: blur(5px); /* Efecto de vidrio (glassmorphism) */
    }}
    div[data-testid="stMetric"]:hover {{
    /* ⬆️ Efecto de elevación más notable */
    transform: scale(1.03); 
    
    /* Borde Cian Eléctrico con brillo al hacer hover */
    border: 1px solid {COLOR_PRINCIPAL};
    
    /* 💡 Sombra de brillo mejorada: eleva el panel y añade el resplandor cian */
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.7), /* Sombra oscura para profundidad */
                0 0 20px {COLOR_SOMBRA}; /* Brillo Cian fuerte */
    
    /* Transición más suave para el cambio */
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}

    /* Tablas y DataFrames - Fondo oscuro y limpio */
    .stDataFrame, .stTable {{
        background: rgba(40, 40, 60, 0.9) !important; 
        color: #e0e0e0 !important; 
        border-radius: 10px;
        border: 1px solid rgba(0, 255, 153, 0.4);
    }}
   /* Separador (hr) - Línea de Energía */
hr {{
    /* Usar tu color principal para el borde */
    border-top: 1px solid {COLOR_PRINCIPAL}; 
    /* El brillo es la clave: darle un resplandor cian */
    box-shadow: 0 0 5px {COLOR_SOMBRA}; 
    opacity: 0.8; /* Más visible que 0.5 */
    margin: 2rem 0; /* Un poco más de espacio vertical */
}}

    /* Botones - Cápsulas de Comando (Gradiente Inverso y Brillo) */
button, .stButton>button {{
    /* 💡 Nuevo Gradiente: Base oscura con un borde sutilmente cian. */
    background: linear-gradient(135deg, {COLOR_FONDO_CONTENEDOR} 30%, {COLOR_FONDO_OSCURO} 90%) !important;
    
    /* 💡 El color del texto es el color principal para alto contraste */
    color: {COLOR_PRINCIPAL} !important; 
    
    border-radius: 4px; /* Un poco más angulares */
    
    /* Borde cian sutil */
    border: 1px solid rgba(0, 255, 194, 0.5); 
    
    font-weight: 700; /* Más audaz */
    letter-spacing: 0.5px;
    padding: 10px 15px; /* Más padding para que se vean más grandes */
    transition: all 0.2s ease-in-out;
}}

/* Efecto Hover */
.stButton>button:hover {{
    /* 💡 Invertimos el color de fondo al brillo cian */
    background: linear-gradient(135deg, {COLOR_PRINCIPAL} 0%, rgba(0, 255, 194, 0.7) 100%) !important;
    
    /* El texto se vuelve oscuro (o blanco puro) al hacer hover */
    color: {COLOR_FONDO_OSCURO} !important; 
    
    /* Brillo cian fuerte */
    box-shadow: 0 0 15px {COLOR_PRINCIPAL}; 
    
    /* Quitamos el opacity, la transición es el cambio de color */
    opacity: 1; 
    
    /* Pequeña elevación */
    transform: translateY(-1px);
}}

    /* Controles de Entrada (File Uploader, Selectbox, Date Input, Text Input) */
/* Aplicado a los contenedores y elementos de entrada reales */

/* Estilo Base de los Inputs */
.stFileUploader, 
.stSelectbox>div>div, 
.stDateInput>div>input, 
.stTextInput>div>div>input {{
    /* Fondo oscuro semi-transparente para profundidad */
    background: {COLOR_FONDO_CONTENEDOR} !important; 
    
    /* Texto interior del input en Cian Eléctrico */
    color: {COLOR_PRINCIPAL} !important; 
    
    border-radius: 4px; /* Un poco más sutil */
    
    /* Borde Cian suave (usando el color principal semitransparente) */
    border: 1px solid rgba(0, 255, 194, 0.4); 
    
    transition: all 0.2s ease-in-out; /* Transición suave para el hover/focus */
}}

/* Etiquetas de los Inputs */
.stFileUploader label, 
.stSelectbox label, 
.stDateInput label, 
.stTextInput label {{
    /* Etiquetas en color de fuente claro (casi blanco) */
    color: {COLOR_FUENTE} !important; 
    font-weight: 500;
}}

/* Efecto Focus (Cuando el usuario hace clic en el campo) */
.stFileUploader:focus-within, 
.stSelectbox>div>div:focus-within, 
.stDateInput>div>input:focus-within, 
.stTextInput>div>div>input:focus-within {{
    /* Borde sólido y brillante al enfocar */
    border-color: {COLOR_PRINCIPAL}; 
    
    /* El efecto clave: Brillo Cian (Holográfico) */
    box-shadow: 0 0 10px {COLOR_SOMBRA}; 
}}

    /* Alertas/Mensajes (Info/Success/Warning) */
    .stAlert {{
        background: rgba(0, 255, 153, 0.08) !important; 
        border-left: 4px solid {COLOR_PRINCIPAL} !important;
        border-radius: 6px;
    }}
    
    /* Contenedores Compactos de Carga y Parámetros */
    .compact-card {{
        background: rgba(30, 30, 50, 0.85); /* Un poco más claro para contraste */
        border-radius: 15px; 
        padding: 15px; 
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4); 
        border: 1px solid rgba(0, 255, 153, 0.3);
        min-width: 140px; 
        max-width: 250px;
    }}
    .compact-card span {{color: {COLOR_PRINCIPAL}; font-weight: 700; font-size: 0.9rem;}}
    .compact-card div[data-testid="stDateInput"], .compact-card div[data-testid="stTextInput"], .compact-card div[data-testid="stFileUploader"] {{ margin-bottom: 0.5rem; }}

    /* Sidebar Navigation */
    .css-1d391kg {{ /* Selector de Streamlit para el sidebar */
        background-color: rgba(10, 10, 20, 0.9) !important; /* Sidebar más oscuro */
        border-right: 2px solid {COLOR_PRINCIPAL};
    }}
    .css-1d391kg a {{color: {COLOR_FUENTE};}}
    .css-1d391kg strong {{color: {COLOR_PRINCIPAL};}}

    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================================================
# 💻 ESTRUCTURA HTML (con los nuevos estilos)
# ==================================================================================

# Título principal y logo grande
col1, col2 = st.columns([3,2])
with col1:
    st.markdown("""
    <h1 style='font-size:4.0rem; font-weight:700; margin-bottom:0.2rem; color:#FFFFFF;'>
        INDICADORES ALS 
    </h1>
    """, unsafe_allow_html=True)
with col2:
    # Aumentar un poco el tamaño del logo para un mejor impacto visual
    st.image('https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png', width=350) 

# =================== HEADER & FILE UPLOAD (Mantenemos la lógica de la sesión) ===================

if 'df_forma9_raw' not in st.session_state:
    st.session_state['df_forma9_raw'] = None
# ... (mantener el resto de la inicialización de session_state) ...

if 'df_forma9_raw' not in st.session_state:
    st.session_state['df_forma9_raw'] = None
if 'df_bd_raw' not in st.session_state:
    st.session_state['df_bd_raw'] = None
def new_func():
    st.session_state['df_forma9_calculated']

if 'df_forma9_calculated' not in st.session_state:
    st.session_state['df_forma9_calculated'] = None
if 'df_bd_calculated' not in st.session_state:
    st.session_state['df_bd_calculated'] = None
if 'reporte_runes' not in st.session_state:
    st.session_state['reporte_runes'] = None
if 'reporte_run_life' not in st.session_state:
    st.session_state['reporte_run_life'] = None
if 'reporte_fallas' not in st.session_state:
    st.session_state['reporte_fallas'] = None
if 'df_trabajo' not in st.session_state:
    st.session_state['df_trabajo'] = None
if 'verificaciones' not in st.session_state:
    st.session_state['verificaciones'] = None
if 'unique_pozos' not in st.session_state:
    st.session_state['unique_pozos'] = []
if 'unique_als' not in st.session_state:
    st.session_state['unique_als'] = []
if 'unique_activos' not in st.session_state:
    st.session_state['unique_activos'] = []


# ========== NUEVO LAYOUT DE CARGA Y FECHA ========== 
st.markdown("---")

# Obtener colores del tema actual para el menú
theme_now = get_theme(st.session_state.get('theme_mode', 'dark'))
accent = theme_now['COLOR_PRINCIPAL']
fg = theme_now['COLOR_FUENTE']

# Barra lateral con enlaces anclados a secciones internas (usa el menú lateral por defecto de Streamlit)
st.sidebar.markdown(f"""
<style>
    /* Estilo para el contenedor general del texto en la barra lateral */
    div[data-testid="stSidebarContent"] {{
        background-color: #0d1117;
    }}

    /* Estilo moderno para los enlaces de navegación */
    .sidebar-link {{
        color: {COLOR_FUENTE} !important;
        text-decoration: none !important;
        display: block;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        background: transparent;
        border-left: 3px solid transparent;
    }}

    /* Efecto hover moderno */
    .sidebar-link:hover {{
        background-color: rgba(255, 255, 255, 0.1);
        border-left: 3px solid {COLOR_PRINCIPAL};
        transform: translateX(5px);
    }}
        margin: 5px 0;
        border-radius: 4px; /* Bordes sutilmente redondeados */
    }}
    
    /* Efecto hover MEJORADO: el enlace brilla con el color principal */
    .sidebar-link:hover {{
        color: {COLOR_PRINCIPAL} !important;
        /* GLOW más notable y definido */
        text-shadow: 0 0 7px {COLOR_SOMBRA}, 0 0 10px {COLOR_PRINCIPAL}30;
        background-color: rgba(0, 255, 153, 0.05); /* Sombra muy sutil al pasar el mouse */
        font-weight: 600; /* Ligeramente más grueso */
        text-decoration: none; /* Asegura que no haya subrayado en hover */
    }}

    /* Estilo para los enlaces activos (opcional, si usas estados) */
    .sidebar-link.active {{
        color: {COLOR_PRINCIPAL} !important;
        text-shadow: 0 0 10px {COLOR_SOMBRA};
        font-weight: bold;
        text-decoration: none; /* Asegura que no haya subrayado en estado activo */
    }}
</style>

<div style='
    color:{COLOR_PRINCIPAL}; 
    font-size:1.3rem; /* Título un poco más grande */
    font-weight:900; 
    margin-bottom:20px; 
    padding-left: 5px; /* Alineación con los enlaces */
    letter-spacing: 2px; /* Más espaciado para look futurista */
    text-shadow: 0 0 10px {COLOR_SOMBRA}, 0 0 20px {COLOR_PRINCIPAL}50; /* Doble sombra de brillo */
'>
    NAVEGACIÓN DE SISTEMAS 🧭
</div>

<a href="#resultados-y-reportes" class='sidebar-link'>📊 Resultados y Reportes</a>
<a href="#reporte-de-runes" class='sidebar-link'>🏃‍♂️ Reporte de RUNES</a>
<a href="#historico-run-life-por-campo" class='sidebar-link'>📈 Run Life </a>
<a href="#fallas-mensuales" class='sidebar-link'>🛑 Fallas Mensuales</a>
<a href="#listado-de-pozos-fallados" class='sidebar-link'>🚨 Pozos Fallados</a>
<a href="#indices-de-falla" class='sidebar-link'>📉 Índices de Falla</a>
<a href="#mtbf" class='sidebar-link'>⏳ MTBF</a>
<a href="#data-frame-final-de-trabajo" class='sidebar-link'>💾 DataFrame </a>
<a href="#grafico-resumen" class='sidebar-link'>💹 Gráfico Resumen</a>

<hr style='border-top: 3px solid {COLOR_PRINCIPAL}; opacity: 0.5; margin: 10px 0;'>

<div style='font-size:0.85rem; color:{COLOR_PRINCIPAL}; opacity:0.6; padding-left: 5px;'>
    // Módulo v1.0 <br>
    // Desarrollado por AJM 🧑‍💻
</div>
""", unsafe_allow_html=True)


# Apartado compacto para carga de archivos y parámetros
col_f9, col_bd, col_params = st.columns([1, 1, 1])

# --- Tarjeta 1: Carga de FORMA 9 ---
with col_f9:
    st.markdown("""
    <div class='compact-card'>
        <span>Carga de FORMA 9 🗃️</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True): 
        forma9_file = st.file_uploader("FORMA 9 (.csv/.xlsx)", type=["csv", "xlsx"], key="forma9_file")
        url_forma9 = st.text_input("URL F9", key="url_forma9_excel", help="URL pública de FORMA 9 (OneDrive/SharePoint)")
        
        # Lógica de conexión
        forma9_online_file = None
        if url_forma9:
            try:
                # La importación de requests y tempfile se recomienda al inicio del script.
                r = requests.get(url_forma9)
                r.raise_for_status()
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
                tmp.write(r.content)
                tmp.flush()
                forma9_online_file = tmp.name
                st.success("F9 online OK.")
            except Exception as e:
                st.error(f"F9 online error: {e}")

# --- Tarjeta 2: Carga de BD Principal ---
with col_bd:
    st.markdown("""
    <div class='compact-card'>
        <span>Carga  Base de Datos 🗃️</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True): 
        bd_file = st.file_uploader("BD (.csv o .xlsx)", type=["csv", "xlsx"], key="bd_file")
        url_bd = st.text_input("URL BD", key="url_bd_excel", help="URL pública de BD (OneDrive/SharePoint)")
        
        # Lógica de conexión
        bd_online_file = None
        if url_bd:
            try:
                r = requests.get(url_bd)
                r.raise_for_status()
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
                tmp.write(r.content)
                tmp.flush()
                bd_online_file = tmp.name
                st.success("BD online OK.")
            except Exception as e:
                st.error(f"BD online error: {e}")

# --- Tarjeta 3: Parámetros de Evaluación ---
with col_params:
    st.markdown("""
    <div class='compact-card'>
        <span>Parámetros de Evaluación ⚙️</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True): 
        fecha_evaluacion = st.date_input("🗓️ Fecha de Evaluación", datetime.now().date(), key="fecha_eval")
        
        # Botón de Cálculo (con ícono)
        calcular_btn = st.button("🚀 Calcular Datos Iniciales", key="calcular_btn", use_container_width=True)

    # Determinar qué archivo usar para cada uno
    # Usar archivo local si existe, si no el online
    forma9_final = forma9_file if forma9_file is not None else forma9_online_file
    bd_final = bd_file if bd_file is not None else bd_online_file
    
    # =================== Lógica de Cálculo (Se mantiene intacta) ===================
    if forma9_final and bd_final:
        st.success("¡Ambos archivos cargados! Haz clic en el botón para calcular.")
        if calcular_btn:
            import os
            # Normalizar entradas: si son rutas (strings) convertir a BytesIO con .name
            def normalize_file(f):
                if f is None:
                    return None
                # Si es un path string (por ejemplo archivo descargado a tmp.name)
                if isinstance(f, str):
                    try:
                        with open(f, 'rb') as fh:
                            data = fh.read()
                        bio = io.BytesIO(data)
                        # asignar atributo name para compatibilidad con la lógica existente
                        bio.name = os.path.basename(f)
                        return bio
                    except Exception as e:
                        st.error(f"No se pudo leer el archivo local '{f}': {e}")
                        return None
                # Si es un UploadedFile o similar, devolver tal cual
                return f

            forma9_input = normalize_file(forma9_final)
            bd_input = normalize_file(bd_final)

            if forma9_input is None or bd_input is None:
                st.error("No se pudo procesar los archivos. Revisa las rutas o los archivos subidos.")
            else:
                try:
                    df_forma9_raw, df_bd_raw = cargar_y_limpiar_datos(forma9_input, bd_input)
                    if df_forma9_raw is None or df_bd_raw is None:
                        st.error("La lectura/limpieza de los archivos falló. Revisa los mensajes anteriores.")
                    else:
                        # Ejecutar cálculos iniciales y procesamientos
                        df_forma9_calc, df_bd_calc = perform_initial_calculations(df_forma9_raw, df_bd_raw, fecha_evaluacion)
                        df_trabajo, reporte_fallas = calcular_indicadores_finales(df_forma9_calc, df_bd_calc)
                        reporte_runes, reporte_run_life, verificaciones = generar_reporte_completo(df_bd_calc, df_forma9_calc, fecha_evaluacion)

                        # Guardar en session_state para uso posterior en la UI
                        st.session_state['df_forma9_raw'] = df_forma9_raw
                        st.session_state['df_bd_raw'] = df_bd_raw
                        st.session_state['df_forma9_calculated'] = df_forma9_calc
                        st.session_state['df_bd_calculated'] = df_bd_calc
                        st.session_state['reporte_runes'] = reporte_runes
                        st.session_state['reporte_run_life'] = reporte_run_life
                        st.session_state['reporte_fallas'] = reporte_fallas
                        st.session_state['df_trabajo'] = df_trabajo
                        st.session_state['verificaciones'] = verificaciones

                        # Listas únicas para filtros
                        st.session_state['unique_pozos'] = sorted(df_bd_calc['POZO'].dropna().unique().tolist()) if 'POZO' in df_bd_calc.columns else []
                        st.session_state['unique_als'] = sorted(df_bd_calc['ALS'].dropna().unique().tolist()) if 'ALS' in df_bd_calc.columns else []
                        st.session_state['unique_activos'] = sorted(df_bd_calc['ACTIVO'].dropna().unique().tolist()) if 'ACTIVO' in df_bd_calc.columns else []

                        st.success("Cálculos finalizados correctamente.")
                except Exception as e:
                    st.error(f"Error durante el procesamiento: {e}")


if st.session_state['reporte_runes'] is not None:
    st.markdown("---")
    st.markdown(f"""
    <h2 id="resultados-y-reportes" style='font-size:2rem; font-weight:700; margin-bottom:0.3em;'>
        <span style='color:{COLOR_PRINCIPAL};'>📈 Resultados y Reportes</span>
    </h2>
    """, unsafe_allow_html=True)


    # Filtros generales
    activo_options = ['TODOS'] + st.session_state.get('unique_activos', [])
    bloque_options = ['TODOS']
    campo_options = ['TODOS']
    als_options = ['TODOS']
    proveedor_options = ['TODOS']
    if 'BLOQUE' in st.session_state['df_bd_calculated'].columns:
        bloque_options += sorted([str(x) for x in st.session_state['df_bd_calculated']['BLOQUE'].dropna().unique()])
    if 'CAMPO' in st.session_state['df_bd_calculated'].columns:
        campo_options += sorted([str(x) for x in st.session_state['df_bd_calculated']['CAMPO'].dropna().unique()])
    if 'ALS' in st.session_state['df_bd_calculated'].columns:
        als_options += sorted([str(x) for x in st.session_state['df_bd_calculated']['ALS'].dropna().unique()])
    if 'PROVEEDOR' in st.session_state['df_bd_calculated'].columns:
        proveedor_options += sorted([str(x) for x in st.session_state['df_bd_calculated']['PROVEEDOR'].dropna().unique()])

    # --- Barra de filtros fijada en la sidebar (usa los mismos keys para no cambiar la funcionalidad) ---
    with st.sidebar:
        st.markdown(f"""
        <div style="position:sticky; top:0; z-index:9999; padding:10px 0 20px 0; background: transparent;">
            <h4 style='margin:0; color: {COLOR_PRINCIPAL};'>🔎 Filtros (fijados)</h4>
        </div>
        """, unsafe_allow_html=True)

        # Los widgets en la sidebar comparten las mismas claves (keys) que los del área principal,
        # por lo que cualquier cambio en la sidebar actualizará las variables usadas por el resto
        # del script y no se altera la funcionalidad existente.
        st.selectbox(
            "🌐 Filtrar por Activo:",
            options=activo_options,
            key='general_activo_filter',
            format_func=lambda x: x if x == 'TODOS' else f"{x} 🛢️"
        )
        st.selectbox(
            "🎲 Filtrar por Bloque:",
            options=bloque_options,
            key='general_bloque_filter',
            format_func=lambda x: x if x == 'TODOS' else f"{x} 🏢"
        )
        st.selectbox(
            "🎴 Filtrar por Campo:",
            options=campo_options,
            key='general_campo_filter',
            format_func=lambda x: x if x == 'TODOS' else f"{x} 🌱"
        )
        st.selectbox(
            "🔧 Filtrar por ALS:",
            options=als_options,
            key='general_als_filter',
            format_func=lambda x: x if x == 'TODOS' else f"{x} ⚙️"
        )
        st.selectbox(
            "🏭 Filtrar por Proveedor:",
            options=proveedor_options,
            key='general_proveedor_filter',
            format_func=lambda x: x if x == 'TODOS' else f"{x} 🏭"
        )

    col1, col2, col3, col4, col5 = st.columns(5)
    # Evitar duplicar widgets con la misma key: los selectboxes interactivos se muestran
    # en la sidebar (arriba, fijados). Aquí leemos los valores desde session_state para
    # conservar la funcionalidad existente y mostrar el valor seleccionado en la UI.
    selected_activo = st.session_state.get('general_activo_filter', 'TODOS')
    selected_bloque = st.session_state.get('general_bloque_filter', 'TODOS')
    selected_campo = st.session_state.get('general_campo_filter', 'TODOS')
    selected_als = st.session_state.get('general_als_filter', 'TODOS')
    selected_proveedor = st.session_state.get('general_proveedor_filter', 'TODOS')

    with col1:
        display_activo = selected_activo if selected_activo == 'TODOS' else f"{selected_activo} 🛢️"
        st.markdown(f"**🌐 Activo:** {display_activo}")
    with col2:
        display_bloque = selected_bloque if selected_bloque == 'TODOS' else f"{selected_bloque} �"
        st.markdown(f"**🎲 Bloque:** {display_bloque}")
    with col3:
        display_campo = selected_campo if selected_campo == 'TODOS' else f"{selected_campo} 🌱"
        st.markdown(f"**🎴 Campo:** {display_campo}")
    with col4:
        display_als = selected_als if selected_als == 'TODOS' else f"{selected_als} ⚙️"
        st.markdown(f"**🔧 ALS:** {display_als}")
    with col5:
        display_proveedor = selected_proveedor if selected_proveedor == 'TODOS' else f"{selected_proveedor} 🏭"
        st.markdown(f"**🏭 Proveedor:** {display_proveedor}")

    df_bd_filtered = st.session_state['df_bd_calculated'].copy()
    df_forma9_filtered = st.session_state['df_forma9_calculated'].copy()

    # Aplicar filtros
    if selected_activo != 'TODOS':
        df_bd_filtered = df_bd_filtered[df_bd_filtered['ACTIVO'] == selected_activo]
    if selected_bloque != 'TODOS' and 'BLOQUE' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['BLOQUE'] == selected_bloque]
    if selected_campo != 'TODOS' and 'CAMPO' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['CAMPO'] == selected_campo]
    if selected_als != 'TODOS' and 'ALS' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['ALS'] == selected_als]
    if selected_proveedor != 'TODOS' and 'PROVEEDOR' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['PROVEEDOR'] == selected_proveedor]
    pozos_in_filtered_bd = df_bd_filtered['POZO'].unique()
    df_forma9_filtered = df_forma9_filtered[df_forma9_filtered['POZO'].isin(pozos_in_filtered_bd)]

    # --- Sección de Reporte de RUNES ---
    st.markdown(f"""
    <h3 id="reporte-de-runes" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:'COLOR_PRINCIPAL';'>📊 Reporte de RUNES</span>
    </h3>
    """, unsafe_allow_html=True)

    reporte_runes_filtered, reporte_run_life_filtered, verificaciones_filtered = generar_reporte_completo(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)

    # Calcular índice de falla anual para el mapa conceptual
    indice_resumen_df, _ = calcular_indice_falla_anual(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)

    # Calcular MTBF global y por ALS para el mapa conceptual
    from mtbf import calcular_mtbf
    mtbf_global, _ = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
    mtbf_als = None
    if 'ALS' in df_bd_filtered.columns and st.session_state.get('kpis_als_filter', 'TODOS') != 'TODOS':
        als_val = st.session_state.get('kpis_als_filter', 'TODOS')
        df_bd_als = df_bd_filtered[df_bd_filtered['ALS'] == als_val]
        mtbf_als, _ = calcular_mtbf(df_bd_als, fecha_evaluacion)

    # Guardar KPIs principales en session_state para el chat IA
    st.session_state['mtbf_global'] = mtbf_global
    # Ejemplo para otros KPIs, debes agregar los cálculos correctos:
    st.session_state['indice_severidad_global'] = indice_resumen_df['Índice de Severidad'].mean() if 'Índice de Severidad' in indice_resumen_df else None
    st.session_state['pozos_problema'] = ', '.join([str(p) for p in pozos_problema['POZO'].tolist()]) if 'pozos_problema' in locals() and not pozos_problema.empty else None
    st.session_state['indice_falla_global'] = indice_resumen_df['Índice de Falla'].mean() if 'Índice de Falla' in indice_resumen_df else None
    st.session_state['run_life_promedio'] = df_bd_filtered['RUN LIFE @ FALLA'].mean() if 'RUN LIFE @ FALLA' in df_bd_filtered else None
    st.session_state['fallas_comunes'] = ', '.join(df_bd_filtered['FALLA'].value_counts().head(3).index.tolist()) if 'FALLA' in df_bd_filtered else None
    st.session_state['total_runs'] = df_bd_filtered.shape[0]
    st.session_state['pozos_on'] = df_bd_filtered[df_bd_filtered['ESTADO'] == 'ON']['POZO'].nunique() if 'ESTADO' in df_bd_filtered and 'POZO' in df_bd_filtered else None
    st.session_state['pozos_off'] = df_bd_filtered[df_bd_filtered['ESTADO'] == 'OFF']['POZO'].nunique() if 'ESTADO' in df_bd_filtered and 'POZO' in df_bd_filtered else None

    # Mostrar KPIs y mapa conceptual ANTES de dividir en columnas
    mostrar_kpis(
        df_bd_filtered,
        reporte_runes_filtered,
        reporte_run_life_filtered,
        indice_resumen_df,
        mtbf_global,
        mtbf_als,
        df_forma9_filtered,
        fecha_evaluacion
    )

    # Ahora sí, dividir en columnas para tablas y gráficas
    col_table, col_chart = st.columns([0.4, 0.6])

    with col_table:
        st.dataframe(reporte_runes_filtered, hide_index=True)
    with col_chart:
        color_sequence = get_color_sequence()
        fig = px.bar(
            reporte_runes_filtered,
            x='Categoría',
            y='Conteo',
            color='Categoría',
            title=styled_title(f'Conteo de RUNES por Categoría ({selected_activo})'),
            color_discrete_sequence=color_sequence
        )
        layout = get_plotly_layout()
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)
    # --- Nueva sección: BOPD vs Run Life por Bloque ---
    st.markdown("""
    <h4 style='margin-top:1em;'>📌 BOPD vs Run Life por Bloque (Buckets de años)</h4>
    """, unsafe_allow_html=True)

    # Determinar qué pozos y runs usar: tomar último RUN por pozo con FECHA_RUN <= fecha_evaluacion
    try:
        fecha_eval = pd.to_datetime(fecha_evaluacion)
        df_runs_validos = df_bd_filtered[df_bd_filtered['FECHA_RUN'] <= fecha_eval].copy()
        if df_runs_validos.empty:
            st.info('No hay RUNs previos a la fecha de evaluación para los pozos filtrados.')
        df_last_run = df_runs_validos.sort_values('FECHA_RUN').groupby('POZO', as_index=False).last()
        # Filtrar solo pozos operativos: sin FECHA_PULL ni FECHA_FALLA (o con esas fechas posteriores a la evaluación)
        try:
            # Asegurar tipo datetime
            if 'FECHA_PULL' in df_last_run.columns:
                df_last_run['FECHA_PULL'] = pd.to_datetime(df_last_run['FECHA_PULL'], errors='coerce')
            else:
                df_last_run['FECHA_PULL'] = pd.NaT
            if 'FECHA_FALLA' in df_last_run.columns:
                df_last_run['FECHA_FALLA'] = pd.to_datetime(df_last_run['FECHA_FALLA'], errors='coerce')
            else:
                df_last_run['FECHA_FALLA'] = pd.NaT
            df_last_run['FECHA_RUN'] = pd.to_datetime(df_last_run['FECHA_RUN'], errors='coerce')

            mask_operativos = (
                (df_last_run['FECHA_RUN'] <= fecha_eval) &
                ((df_last_run['FECHA_PULL'].isna()) | (df_last_run['FECHA_PULL'] > fecha_eval)) &
                ((df_last_run['FECHA_FALLA'].isna()) | (df_last_run['FECHA_FALLA'] > fecha_eval))
            )
            df_last_run = df_last_run[mask_operativos].copy()
        except Exception as e:
            st.warning(f"No se pudo aplicar el filtro de pozos operativos al conjunto de RUNs: {e}")
    except Exception:
        df_last_run = df_bd_filtered.copy()

    # Obtener BOPD desde FORMA9 filtrando por el MES de la fecha de evaluación
    df_f9 = df_forma9_filtered.copy()
    df_f9_sum = pd.DataFrame(columns=['POZO', 'BOPD'])
    try:
        if 'FECHA_FORMA9' in df_f9.columns:
            df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce')
            fecha_eval = pd.to_datetime(fecha_evaluacion)
            # Filtrar por mismo mes y año de la fecha de evaluación
            df_f9_month = df_f9[(df_f9['FECHA_FORMA9'].dt.year == fecha_eval.year) & (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)].copy()

            # Determinar columna de dias trabajados y BOPD (nombres normalizados en carga)
            dias_col = next((c for c in df_f9_month.columns if 'DIAS' in str(c).upper()), None)
            bopd_col = next((c for c in df_f9_month.columns if 'BOPD' in str(c).upper()), None)

            if dias_col is not None:
                df_f9_month[dias_col] = pd.to_numeric(df_f9_month[dias_col], errors='coerce').fillna(0)
                # Conservar solo filas con dias trabajados > 0 (pozos que produjeron en el mes)
                df_f9_month = df_f9_month[df_f9_month[dias_col] > 0].copy()

            if not df_f9_month.empty and bopd_col is not None:
                df_f9_month[bopd_col] = pd.to_numeric(df_f9_month[bopd_col], errors='coerce').fillna(0)
                # Sumar BOPD por pozo en el mes
                df_f9_sum = df_f9_month.groupby('POZO', as_index=False).agg({bopd_col: 'sum'})
                df_f9_sum.rename(columns={bopd_col: 'BOPD'}, inplace=True)
            else:
                df_f9_sum = pd.DataFrame(columns=['POZO', 'BOPD'])
        else:
            df_f9_sum = pd.DataFrame(columns=['POZO', 'BOPD'])
    except Exception as e:
        st.warning(f"Error al procesar FORMA9 para mes de evaluación: {e}")
        df_f9_sum = pd.DataFrame(columns=['POZO', 'BOPD'])

    # Correlacionar BOPD (suma en el mes y solo pozos con DIAS TRABAJADOS>0) con el RUN correspondiente en BD
    # Para mapear el RUN usamos la última fecha de FORMA9 dentro del mes por pozo
    if not df_f9_sum.empty:
        # Reconstruir df_f9_month raw para obtener la última fecha por pozo
        try:
            df_f9_month_raw = df_f9[(df_f9['FECHA_FORMA9'].dt.year == fecha_eval.year) & (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)].copy()
        except Exception:
            df_f9_month_raw = pd.DataFrame()

        if not df_f9_month_raw.empty:
            # última fecha de forma9 dentro del mes por pozo
            df_f9_lastdate = df_f9_month_raw.sort_values('FECHA_FORMA9').groupby('POZO', as_index=False).last()[['POZO', 'FECHA_FORMA9']]
            # asegurar que df_f9_sum tenga la columna POZO
            df_f9_sum = df_f9_sum.copy()
            # unir suma de BOPD con la última fecha para mapear
            df_f9_merge = pd.merge(df_f9_sum, df_f9_lastdate, on='POZO', how='left')
        else:
            df_f9_merge = df_f9_sum.copy()
            df_f9_merge['FECHA_FORMA9'] = pd.NaT

        # Preparar BD para matching: columnas importantes
        bd_match = df_bd_filtered.copy()
        for dtcol in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
            if dtcol in bd_match.columns:
                bd_match[dtcol] = pd.to_datetime(bd_match[dtcol], errors='coerce')
            else:
                bd_match[dtcol] = pd.NaT

        # Hacer merge por POZO y aplicar la lógica de inclusión por fecha
        if not df_f9_merge.empty:
            df_f9_merge['_idx'] = range(len(df_f9_merge))
            merged_df = pd.merge(df_f9_merge, bd_match[['POZO', 'RUN', 'FECHA_RUN', 'FECHA_PULL', 'RUN LIFE']], on='POZO', how='left')
            merged_df['FECHA_FORMA9'] = pd.to_datetime(merged_df['FECHA_FORMA9'], errors='coerce')
            # considerar fecha de corte: si FECHA_PULL es NaT usar fecha_evaluacion
            merged_df['FECHA_PULL_FILL'] = merged_df['FECHA_PULL'].fillna(fecha_eval)
            merged_df['is_match'] = (merged_df['FECHA_FORMA9'] >= merged_df['FECHA_RUN']) & (merged_df['FECHA_FORMA9'] < merged_df['FECHA_PULL_FILL'])
            # elegir el RUN con FECHA_RUN más reciente (max) por cada registro original
            # 1) Match directo: FECHA_FORMA9 en el rango [FECHA_RUN, FECHA_PULL)
            runlife_map = {}
            try:
                matched = merged_df[merged_df['is_match']].copy()
                if not matched.empty:
                    best_idx = matched.groupby('_idx')['FECHA_RUN'].idxmax()
                    best_matches = merged_df.loc[best_idx]
                    runlife_map = best_matches.set_index('_idx')['RUN LIFE'].to_dict()
            except Exception:
                runlife_map = {}

            # 2) Fallback: si algún pozo no tiene match directo, buscar el RUN con FECHA_RUN <= FECHA_FORMA9
            missing_idxs = [i for i in range(len(df_f9_merge)) if i not in runlife_map]
            if missing_idxs:
                for i in missing_idxs:
                    try:
                        candidate = merged_df[(merged_df['_idx'] == i) & (merged_df['FECHA_RUN'] <= merged_df.loc[merged_df['_idx'] == i, 'FECHA_FORMA9'].iloc[0])]
                        if not candidate.empty:
                            # tomar el RUN con FECHA_RUN más reciente
                            idx_choice = candidate['FECHA_RUN'].idxmax()
                            runlife_map[i] = merged_df.loc[idx_choice, 'RUN LIFE']
                    except Exception:
                        # dejar sin match si algo falla
                        continue

            df_f9_merge['RUN LIFE'] = df_f9_merge.index.map(lambda i: runlife_map.get(i, np.nan))

            # Mostrar resumen rápido de mapeo para ayudar a debugging y ver distribución
            try:
                total_pozos = len(df_f9_merge)
                mapeados = df_f9_merge['RUN LIFE'].notna().sum()
                no_mapeados = total_pozos - int(mapeados)
                st.markdown(f"**Pozos en FORMA9 (mes):** {total_pozos} — **Con RUN asociado:** {mapeados} — **Sin RUN:** {no_mapeados}")
            except Exception:
                pass
            merged = df_f9_merge[['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE']].copy()
        else:
            merged = pd.DataFrame(columns=['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE'])
    else:
        merged = pd.DataFrame(columns=['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE'])

    # Normalizar columnas
    merged['BOPD'] = pd.to_numeric(merged['BOPD'], errors='coerce').fillna(0)
    merged['RUN LIFE'] = pd.to_numeric(merged['RUN LIFE'], errors='coerce').fillna(0)

    # Bucketizar Run Life (días -> años)
    def bucket_runlife(days):
        years = days / 365.0
        if pd.isna(days):
            return 'Sin Datos'
        if years < 2:
            return '<2 años'
        if 2 <= years < 4:
            return '2-4 años'
        if 4 <= years < 6:
            return '4-6 años'
        return '>6 años'

    if not merged.empty:
        merged['RunLifeBucket'] = merged['RUN LIFE'].apply(bucket_runlife)

        # Agregados por bucket (suma de BOPD entre todos los bloques) y conteo de pozos únicos
        agg = merged.groupby(['RunLifeBucket']).agg(
            BOPD_sum=pd.NamedAgg(column='BOPD', aggfunc='sum'),
            Pozos=pd.NamedAgg(column='POZO', aggfunc=lambda x: x.nunique())
        ).reset_index()

        # Asegurar orden de buckets
        bucket_order = ['<2 años', '2-4 años', '4-6 años', '>6 años']
        agg = agg.set_index('RunLifeBucket').reindex(bucket_order).fillna({'BOPD_sum': 0, 'Pozos': 0}).reset_index()

        if agg.empty:
            st.info('No hay datos suficientes para generar la gráfica por buckets de Run Life.')
        else:
            # Mostrar tabla agregada (sujeta a filtros generales aplicados previamente)
            st.markdown('**Tabla agregada: BOPD (suma) y número de pozos por Bucket de Run Life**')
            st.dataframe(agg.rename(columns={'RunLifeBucket': 'Bucket Run Life', 'BOPD_sum': 'BOPD (suma)', 'Pozos': 'Número de Pozos'}), hide_index=True)

            # Gráfica: 4 columnas (x = buckets) con la suma total de BOPD (y). Añadir número de pozos en un cuadrito sobre cada columna.
            fig2 = px.bar(
                agg,
                x='RunLifeBucket',
                y='BOPD_sum',
                labels={'RunLifeBucket': 'Run Life (Buckets)', 'BOPD_sum': 'BOPD (suma)'},
                title=styled_title('BOPD total por Bucket de Run Life')
            )
            # Añadir anotaciones (cuadrito) con número de pozos
            max_y = agg['BOPD_sum'].max() if not agg['BOPD_sum'].empty else 0
            for i, row in agg.iterrows():
                y_val = float(row['BOPD_sum'])
                # posicionar el cuadrito dentro de la barra si es posible, sino encima
                if y_val > 0:
                    y_ann = y_val * 0.5
                else:
                    y_ann = max_y * 0.02
                fig2.add_annotation(
                    x=row['RunLifeBucket'],
                    y=y_ann,
                    text=f"{int(row['Pozos'])}",
                    showarrow=False,
                    font={'color': COLOR_FUENTE, 'size':12},
                    align='center',
                    bgcolor='rgba(0,0,0,0.6)',
                    bordercolor=COLOR_PRINCIPAL,
                    borderwidth=1,
                    opacity=0.9
                )

            layout = get_plotly_layout()
            fig2.update_layout(**layout)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info('No hay datos de RUN o de FORMA9 disponibles para el filtro actual.')

    with st.expander("Verificaciones de Consistencia", expanded=False):
        for relacion, es_valida in verificaciones_filtered.items():
            status = "✅ Válida" if es_valida else "❌ No válida"
            st.markdown(f"<span style='font-size:11px; color:{COLOR_FUENTE};'>{relacion}: {status}</span>", unsafe_allow_html=True)
    
    st.markdown("""
    <h3 id="historico-de-run-life-por-campo" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:'COLOR_PRINCIPAL';'>⏳ Histórico RUN LIFE por Campo</span>
    </h3>
    """, unsafe_allow_html=True)
    col_table_runlife, col_chart_runlife = st.columns([0.35, 0.65])
    # Selector de campo (ACTIVO)
    activo_runlife = selected_activo if 'selected_activo' in locals() or 'selected_activo' in globals() else 'TODOS'

    # Calcular Run Life total (fallados + pulling) para la fecha evaluada y filtro
    df_runlife_total = df_bd_filtered.copy()
    if activo_runlife != 'TODOS' and 'ACTIVO' in df_runlife_total.columns:
        df_runlife_total = df_runlife_total[df_runlife_total['ACTIVO'] == activo_runlife]
    # Considerar solo los que tienen FECHA_PULL o FECHA_FALLA en el año evaluado
    runlife_total = df_runlife_total[
        ((df_runlife_total['FECHA_PULL'].notna()) | (df_runlife_total['FECHA_FALLA'].notna())) &
        (df_runlife_total['FECHA_RUN'].dt.date <= fecha_evaluacion)
    ]['RUN LIFE'].mean()
    st.metric(label=f"Run Life Total ({'Todos' if activo_runlife == 'TODOS' else activo_runlife}) para la fecha evaluada", value=f"{runlife_total:.2f}" if not pd.isna(runlife_total) else "No disponible")

    # Generar histórico por campo

    # Usar siempre la función corregida para el histórico de run life promedio mensual
    historico_run_life = generar_historico_run_life(df_bd_filtered, fecha_evaluacion)

    with col_table_runlife:
        if historico_run_life is not None:
            st.dataframe(historico_run_life, hide_index=True)

    with col_chart_runlife:
        if historico_run_life is not None and 'ACTIVO' in historico_run_life.columns:
            # Definir paleta de colores personalizada para los campos (ACTIVO)
            # Usar la secuencia de colores proporcionada por el usuario
            color_sequence = get_color_sequence()
            fig = px.bar(
                historico_run_life,
                x='Mes',
                y='Run Life Promedio',
                color='ACTIVO',
                barmode='group',
                title=styled_title('⭕ Run Life Promedio Mensual por Activo'),
                labels={'Mes': 'Mes', 'Run Life Promedio': 'Run Life Promedio', 'ACTIVO': 'Campo'},
                color_discrete_sequence=color_sequence
            )
            layout = get_plotly_layout()
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
        elif historico_run_life is not None:
            fig = px.bar(
                historico_run_life,
                x='Mes',
                y='Run Life',
                title=styled_title('Run Life Promedio Mensual'),
                labels={'Mes': 'Mes', 'Run Life': 'Run Life Promedio'}
            )
            fig.update_layout(
                plot_bgcolor=COLOR_FONDO_OSCURO,
                paper_bgcolor=COLOR_FONDO_OSCURO,
                font_color=COLOR_FUENTE,
                title_font_color=COLOR_PRINCIPAL,
                xaxis=dict(color=COLOR_FUENTE),
                yaxis=dict(color=COLOR_PRINCIPAL)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <h3 id=\"fallas-mensuales\" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'>📉 Fallas Mensuales</span>
    </h3>
    """, unsafe_allow_html=True)
    if not st.session_state['reporte_fallas'].empty:
        min_date_falla = st.session_state['reporte_fallas']['MES'].min().date()
        max_date_falla = st.session_state['reporte_fallas']['MES'].max().date()
        start_date_falla, end_date_falla = st.date_input(
            "Filtra por rango de fecha para las fallas:",
            [min_date_falla, max_date_falla],
            key='date_filter_falla'
        )
        filtered_fallas = st.session_state['reporte_fallas'][
            (st.session_state['reporte_fallas']['MES'].dt.date >= start_date_falla) & 
            (st.session_state['reporte_fallas']['MES'].dt.date <= end_date_falla)
        ]

        # Enriquecer la tabla con run life a falla y razón de pull
        detalles_fallas = []
        for _, row in filtered_fallas.iterrows():
            mes = row['MES']
            mask = (df_bd_filtered['FECHA_FALLA'].dt.to_period('M') == mes.to_period('M'))
            runs_mes = df_bd_filtered[mask]
            for _, run in runs_mes.iterrows():
                razon = run.get('RAZON ESPECIFICA PULL', '')
                clasificacion = clasificar_razon_ia(razon) if razon else ''
                detalles_fallas.append({
                    'Mes': mes,
                    'Pozo': run.get('POZO', ''),
                    'Fecha Falla': run.get('FECHA_FALLA', ''),
                    'Run Life a Falla': run.get('RUN LIFE', ''),
                    'Razón de Pull': razon,
                    'Clasificación IA': clasificacion
                })
        df_detalles_fallas = pd.DataFrame(detalles_fallas)

        # --- Layout 2x2 simétrico ---
        col1, col2 = st.columns(2)
        with col1:
            if not df_detalles_fallas.empty:
                st.dataframe(df_detalles_fallas, use_container_width=True)
            else:
                st.dataframe(filtered_fallas, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Sumatoria Total de Fallas en el Rango")
            st.info(f"Fallas Totales: {len(df_detalles_fallas)}")

        with col2:
            if not df_detalles_fallas.empty:
                df_graf = df_detalles_fallas.copy()
                def clasificar_runlife(rl):
                    try:
                        rl = float(rl)
                    except:
                        return 'Sin Dato'
                    if rl <= 30:
                        return 'Infantil'
                    elif 30 < rl <= 60:
                        return 'Prematura'
                    elif rl <= 1100:
                        return 'En Garantía'
                    elif rl > 1100:
                        return 'Sin Garantía'
                    return 'Sin Dato'
                df_graf['Clasificación Run Life'] = df_graf['Run Life a Falla'].apply(clasificar_runlife)
                conteo = df_graf.groupby(['Clasificación Run Life', 'Clasificación IA']).size().reset_index(name='Cantidad')
                orden_runlife = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía']
                colores_runlife = {
                    'Infantil': '#00FF8C',
                    'Prematura': '#A66EFF',
                    'En Garantía': '#00BFFF',
                    'Sin Garantía': '#0b683a'
                }
                import plotly.graph_objects as go
                fig_runlife = go.Figure()
                for runlife in orden_runlife:
                    df_cat = conteo[conteo['Clasificación Run Life'] == runlife]
                    fig_runlife.add_trace(go.Bar(
                        x=df_cat['Clasificación IA'],
                        y=df_cat['Cantidad'],
                        name=runlife,
                        marker_color=colores_runlife.get(runlife, COLOR_PRINCIPAL)
                    ))
                layout = get_plotly_layout()
                fig_runlife.update_layout(barmode='group', title=styled_title('📉Distribución de Fallas por Run Life y Tipo de Falla IA'), xaxis_title='Tipo de Falla IA', yaxis_title='Cantidad de Fallas', legend_title='Clasificación Run Life')
                fig_runlife.update_layout(**layout)
                st.plotly_chart(fig_runlife, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            if not df_detalles_fallas.empty:
                df_graf = df_detalles_fallas.copy()
                tipo_falla_counts = df_graf['Clasificación IA'].value_counts().reset_index()
                tipo_falla_counts.columns = ['Tipo de Falla IA', 'Cantidad']
                import plotly.express as px

                fig_torta = px.pie(
                    tipo_falla_counts,
                    names='Tipo de Falla IA',
                    values='Cantidad',
                    # Título mejorado con COLOR_PRINCIPAL y efecto brillo
                    title=styled_title('📉 Distribución de Fallas por Tipo de falla')
                )

                # 1. Aplicar la paleta de colores y el efecto de separación
                fig_torta.update_traces(
                    textinfo='percent+label',
                    pull=[0.05] * len(tipo_falla_counts),
                    marker=dict(colors=get_color_sequence())
                )

                # 2. El layout aplica los colores de fondo y fuente oscuros/brillantes
                layout = get_plotly_layout()
                fig_torta.update_layout(**layout)

                st.plotly_chart(fig_torta, use_container_width=True)
            else:
                st.info("No hay datos de fallas para mostrar.")

        with col4:
            if 'ACTIVO' in df_bd_filtered.columns and 'FECHA_FALLA' in df_bd_filtered.columns:
                df_fallas_periodo = df_bd_filtered[(df_bd_filtered['FECHA_FALLA'].dt.date >= start_date_falla) & (df_bd_filtered['FECHA_FALLA'].dt.date <= end_date_falla)]
                
                if not df_fallas_periodo.empty:
                    fallas_campo = df_fallas_periodo.groupby([df_fallas_periodo['FECHA_FALLA'].dt.to_period('M'), 'ACTIVO']).size().reset_index(name='Fallas')
                    fallas_campo['MES'] = fallas_campo['FECHA_FALLA'].dt.to_timestamp()
                    # Título con estilo holográfico
                    title_html = styled_title('💢Fallas Mensuales por Activo')
                    
                    fig_campo = px.bar(
                        fallas_campo,
                        x='MES',
                        y='Fallas',
                        color='ACTIVO',
                        barmode='group',
                        title=title_html,
                        labels={'MES': 'Mes', 'Fallas': 'Cantidad de Fallas', 'ACTIVO': 'Activo'},
                        color_discrete_sequence=get_color_sequence() # APLICACIÓN DE LA NUEVA PALETA
                    )
                    
                    # --- APLICACIÓN DEL LAYOUT FUTURISTA/OSCURO ---
                    # Reemplazamos la actualización manual por la función ya existente para consistencia
                    layout = get_plotly_layout()
                    fig_campo.update_layout(**layout)
                    
                    # Ajustes específicos para el gráfico de barras (si son necesarios, se mantienen)
                    fig_campo.update_xaxes(showgrid=True, gridcolor='rgba(0, 255, 153, 0.2)')
                    fig_campo.update_yaxes(showgrid=True, gridcolor='rgba(0, 255, 153, 0.2)')
                    
                    st.plotly_chart(fig_campo, use_container_width=True)
            
    else:
        st.info("No hay datos de fallas para mostrar.")

    st.markdown("---")
    st.markdown(f"""
    <h3 id="listado-de-pozos-fallados" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'>📜 Listado de Pozos Fallados</span>
    </h3>
    """, unsafe_allow_html=True)

    pozos_fallados_df = df_bd_filtered[
        (df_bd_filtered['FECHA_FALLA'].dt.date >= fecha_evaluacion - timedelta(days=365)) &
        (df_bd_filtered['FECHA_FALLA'].dt.date <= fecha_evaluacion)
    ]

    if not pozos_fallados_df.empty:
        fallas_por_pozo = pozos_fallados_df.groupby('POZO')['RUN'].count().reset_index()
        fallas_por_pozo.rename(columns={'RUN': 'Cantidad de Fallas'}, inplace=True)
        fallas_por_pozo.sort_values(by='Cantidad de Fallas', ascending=False, inplace=True)
        
        col_listado, col_severidad = st.columns([0.5, 0.5])
        
        with col_listado:
            st.dataframe(
                fallas_por_pozo.style.apply(highlight_problema, axis=1),
                hide_index=True
            )
        
        with col_severidad:
            total_fallas_severidad = fallas_por_pozo['Cantidad de Fallas'].sum()
            num_pozos_fallados = fallas_por_pozo.shape[0]
            indice_severidad = (total_fallas_severidad / num_pozos_fallados) if num_pozos_fallados > 0 else 0;
            
            st.metric(label="Índice de Severidad", value=f"{indice_severidad:.2f}")

            # Sección de pozos problema
            st.markdown("---")
            st.markdown("<span style='font-size:1.1rem; color:{COLOR_PRINCIPAL}; font-weight:700;'>Pozos Problema</span>", unsafe_allow_html=True)
            pozos_problema = fallas_por_pozo[fallas_por_pozo['Cantidad de Fallas'] > 1]

            if not pozos_problema.empty:
                st.markdown("Los siguientes pozos tienen más de una falla en el último año:")
                # Traer razón específica de pull y clasificarla
                for index, row in pozos_problema.iterrows():
                    # Buscar razones en df_bd_filtered para ese pozo
                    # Filtrar solo razones del último año respecto a la fecha de evaluación
                    if 'RAZON ESPECIFICA PULL' in df_bd_filtered.columns and 'FECHA_FALLA' in df_bd_filtered.columns:
                        mask = (
                            (df_bd_filtered['POZO'] == row['POZO']) &
                            (df_bd_filtered['FECHA_FALLA'].dt.date >= fecha_evaluacion - timedelta(days=365)) &
                            (df_bd_filtered['FECHA_FALLA'].dt.date <= fecha_evaluacion)
                        )
                        razones = df_bd_filtered.loc[mask, 'RAZON ESPECIFICA PULL'].dropna().tolist()
                    else:
                        razones = []
                    with st.expander(f"{row['POZO']} ({row['Cantidad de Fallas']} fallas)", expanded=False):
                        if len(razones) == 0:
                            st.markdown("<span style='color: #FFFFFF;'>No hay razones disponibles</span>", unsafe_allow_html=True)
                        else:
                            for i, razon in enumerate(razones, 1):
                                clasificacion = clasificar_razon_ia(razon)
                                st.markdown(f"<span style='color: #FFFFFF;'>* Falla {i} Razón: {razon} | Clasificación IA: <b style='color:{COLOR_PRINCIPAL}'>{clasificacion}</b></span>", unsafe_allow_html=True)
            else:
                st.info("¡No hay pozos con más de una falla en el último año!")


    else:
        st.info(f"No hay pozos fallados en el último año para el activo '{selected_activo}' en la fecha de evaluación seleccionada.")


    st.markdown("---")
# Mostrar la sección de "Índices de Falla" sólo si ya se cargaron y calcularon los datos
if st.session_state.get('df_bd_calculated') is not None and st.session_state.get('df_forma9_calculated') is not None:
    # Recrear los dataframes filtrados a partir del cálculo almacenado en session_state
    df_bd_filtered = st.session_state['df_bd_calculated'].copy()
    df_forma9_filtered = st.session_state['df_forma9_calculated'].copy()

    # Aplicar los mismos filtros globales que usa la UI (si existen)
    try:
        selected_activo = st.session_state.get('general_activo_filter', 'TODOS')
        selected_bloque = st.session_state.get('general_bloque_filter', 'TODOS')
        selected_campo = st.session_state.get('general_campo_filter', 'TODOS')
        selected_als = st.session_state.get('general_als_filter', 'TODOS')
        selected_proveedor = st.session_state.get('general_proveedor_filter', 'TODOS')
    except Exception:
        # Si por alguna razón no existen las keys, mantener valores por defecto
        selected_activo = 'TODOS'
        selected_bloque = 'TODOS'
        selected_campo = 'TODOS'
        selected_als = 'TODOS'
        selected_proveedor = 'TODOS'

    if selected_activo != 'TODOS' and 'ACTIVO' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['ACTIVO'] == selected_activo]
    if selected_bloque != 'TODOS' and 'BLOQUE' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['BLOQUE'] == selected_bloque]
    if selected_campo != 'TODOS' and 'CAMPO' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['CAMPO'] == selected_campo]
    if selected_als != 'TODOS' and 'ALS' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['ALS'] == selected_als]
    if selected_proveedor != 'TODOS' and 'PROVEEDOR' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['PROVEEDOR'] == selected_proveedor]

    pozos_in_filtered_bd = df_bd_filtered['POZO'].unique() if 'POZO' in df_bd_filtered.columns else []
    if not df_forma9_filtered.empty and 'POZO' in df_forma9_filtered.columns:
        df_forma9_filtered = df_forma9_filtered[df_forma9_filtered['POZO'].isin(pozos_in_filtered_bd)]

    st.markdown(f"""
    <h3 id="indices-de-falla" style='font-size:2rem; font-weight:600; margin-bottom:0.5em;'>
        <span style='color:{COLOR_PRINCIPAL};'>📊 Índices de Falla</span>
    </h3>
    """, unsafe_allow_html=True)

    if not df_bd_filtered.empty and not df_forma9_filtered.empty:
        try:
            # Llamada a la función con el cálculo rolling
            indice_resumen_df, df_mensual_hist = calcular_indice_falla_anual(
                df_bd_filtered,
                df_forma9_filtered,
                fecha_evaluacion
            )

            # Tabla de resumen ocupa todo el ancho arriba
            st.markdown(f"<span style='font-size:1.2rem; color:{COLOR_PRINCIPAL}; font-weight:700;'>Resumen de Índices para {selected_activo} (Rolling 12 Meses)</span>", unsafe_allow_html=True)
            st.dataframe(indice_resumen_df, hide_index=True)

            # Preparar datos para ambas gráficas
            df_plot_indices = df_mensual_hist.copy()

            # --- CAMBIO CLAVE: Usar las columnas ROLLING ---
            df_plot_indices_melted = df_plot_indices.melt(
                id_vars=['Mes'],
                value_vars=['Indice_Falla_Rolling_ON', 'Indice_Falla_Rolling_ALS_ON'],
                var_name='Indicador',
                value_name='Índice'
            )

            # Debajo, dos columnas: izquierda (línea pequeña), derecha (barras mensual)
            col_hist_line, col_bar_mes = st.columns([0.4, 0.6])
            with col_hist_line:
                fig_line = px.line(
                    df_plot_indices_melted,
                    x='Mes',
                    y='Índice',
                    color='Indicador',
                    markers=True,
                    title=styled_title('Histórico Índice de Falla (Rolling 12M)'),
                    labels={'Mes': 'Mes', 'Índice': 'Valor del Índice'},
                    color_discrete_sequence=color_sequence
                )
                fig_line.update_layout(
                    xaxis={'categoryorder':'category ascending'},
                    height=220,
                    legend=dict(font=dict(size=10)),
                    margin=dict(l=10, r=10, t=40, b=10),
                    plot_bgcolor=COLOR_FONDO_OSCURO,
                    paper_bgcolor=COLOR_FONDO_OSCURO,
                    font_color=COLOR_FUENTE,
                    title_font_color=COLOR_PRINCIPAL
                )
                fig_line.update_yaxes(tickformat='.2%')
                st.plotly_chart(fig_line, use_container_width=True)

            with col_bar_mes:
                fig_bar = px.bar(
                    df_plot_indices_melted,
                    x='Mes',
                    y='Índice',
                    color='Indicador',
                    barmode='group',
                    title=styled_title('Índice de Falla Mensual (Rolling 12M)'),
                    labels={'Mes': 'Mes', 'Índice': 'Valor del Índice'},
                    color_discrete_sequence=color_sequence
                )
                fig_bar.update_layout(
                    xaxis={'categoryorder':'category ascending'},
                    height=220,
                    legend=dict(font=dict(size=10)),
                    margin=dict(l=10, r=10, t=40, b=10),
                    plot_bgcolor=COLOR_FONDO_OSCURO,
                    paper_bgcolor=COLOR_FONDO_OSCURO,
                    font_color=COLOR_FUENTE,
                    title_font_color=COLOR_PRINCIPAL
                )
                fig_bar.update_yaxes(tickformat='.2%')
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("---")
            st.markdown(f"<span style='font-size:1.1rem; color:{COLOR_PRINCIPAL}; font-weight:700;'>♻ Detalle Mensual para el Cálculo de los Índices Anuales</span>", unsafe_allow_html=True)

            col_table_operativos, col_chart_operativos = st.columns([0.5, 0.5])
            with col_table_operativos:
                df_display_mensual = df_mensual_hist.copy()
                df_display_mensual = df_display_mensual[['Mes', 'Fallas Totales', 'Fallas ALS', 'Pozos Operativos', 'Pozos ON']]
                st.dataframe(df_display_mensual)

            with col_chart_operativos:
                df_plot = df_mensual_hist.copy()
                df_plot_melted = df_plot.melt(
                    id_vars=['Mes'],
                    value_vars=['Pozos Operativos', 'Pozos ON'],
                    var_name='Indicador',
                    value_name='Conteo'
                )
                fig = px.line(
                    df_plot_melted,
                    x='Mes',
                    y='Conteo',
                    color='Indicador',
                    markers=True,
                    title=styled_title('Pozos Operativos vs. Pozos Encendidos (ON)'),
                    labels={'Mes': 'Mes', 'Conteo': 'Conteo de Pozos'},
                    color_discrete_sequence=color_sequence
                )
                fig.update_layout(xaxis={'categoryorder':'category ascending'})
                fig.update_layout(
                    plot_bgcolor=COLOR_FONDO_OSCURO,
                    paper_bgcolor=COLOR_FONDO_OSCURO,
                    font_color=COLOR_FUENTE,
                    title_font_color=COLOR_PRINCIPAL
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Ocurrió un error al calcular los índices de falla. Asegúrate de que los datos filtrados contengan la información necesaria: {e}")

    # Mostrar MTBF después del índice de falla
    st.markdown("""
    <h3 id="mtbf" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'>MTBF</span>
    </h3>
    """, unsafe_allow_html=True)
    try:
        mtbf_global, mtbf_por_pozo = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        mostrar_mtbf(mtbf_global, mtbf_por_pozo, df_bd=df_bd_filtered, fecha_evaluacion=fecha_evaluacion)
    except Exception as e:
        st.warning(f"No se pudo calcular el MTBF: {e}")

    st.markdown("""
    <h3 id="dataframe-final-de-trabajo" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'>📋 DataFrame Final de TRABAJO</span>
    </h3>
    """, unsafe_allow_html=True)
    st.dataframe(df_bd_filtered)


    # --- Exportar Excel con tablas y gráficas usando descargar.py ---
    from descargar import exportar_excel_con_graficas
    tablas = {
        'TRABAJO_FINAL': df_bd_filtered,
        'RUNES_RESUMEN': reporte_runes_filtered,
        'RUN_LIFE_HISTORICO': historico_run_life,
        'FALLAS_MENSUALES': st.session_state['reporte_fallas']
    }
    if 'indice_resumen_df' in locals():
        tablas['INDICE_FALLA_ANUAL'] = indice_resumen_df
    if 'df_mensual_hist' in locals():
        tablas['HISTORICO_INDICES'] = df_mensual_hist

    # Gráficas: ejemplo con plotly, convertir a matplotlib
    import matplotlib.pyplot as plt
    graficas = {}
    try:
        # Si tienes figuras plotly, conviértelas a matplotlib
        # Por ejemplo: fig_bar.write_image('temp.png') y luego plt.imread('temp.png')
        # Aquí solo ejemplo vacío:
        pass
    except Exception as e:
        st.warning(f"No se pudieron agregar gráficas: {e}")

    if st.button('📥 Descargar Reporte Completo (.xlsx)', use_container_width=True):
        excel_bytes = exportar_excel_con_graficas(tablas, graficas)
        st.download_button(
            label="Descargar Excel",
            data=excel_bytes,
            file_name="Reporte_Indicadores_ALS.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ----------------- Gráfico Resumen Anual (añadido por grafico.py) -----------------
    try:
        # Import local para no romper el flujo si el archivo no existe
        from grafico import generar_grafico_resumen

        # Asegúrate de que COLOR_PRINCIPAL esté importado de theme.py
        # from theme import COLOR_PRINCIPAL 

        fig_resumen, df_resumen = generar_grafico_resumen(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, titulo=f"Gráfico Resumen Anual - {selected_activo}")
        
        if fig_resumen is not None:
            # Título estilizado para el gráfico
            # (Usamos la f-string para inyectar COLOR_PRINCIPAL, que da el efecto ciberpunk)
            st.markdown(f"<h3 style='margin-top:1em; color:{COLOR_PRINCIPAL};'>📚 Gráfico Resumen</h3>", unsafe_allow_html=True)
            
            # Gráfico Dinámico: Plotly y ajuste de ancho asegurado
            st.plotly_chart(fig_resumen, use_container_width=True)
            
            # ELIMINADO: No se muestra la tabla (df_resumen) para que el gráfico sea el único foco
            # st.dataframe(df_resumen, hide_index=True) 

    except Exception as e:
        st.warning(f"No se pudo generar el gráfico resumen: {e}")




