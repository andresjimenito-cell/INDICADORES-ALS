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
from theme import get_colors, get_plotly_layout as theme_get_plotly_layout, styled_title as theme_styled_title
import requests
import tempfile
import os
import re
import html
import importlib
import tema
import base64

# Obtener una paleta sencilla y no intrusiva desde `theme.py`.
# Usamos valores neutros para evitar efectos (sombras, bordes, grillas) que
# oculten controles o filtors en la UI.
_colors = get_colors()
COLOR_PRINCIPAL = tema.COLOR_PRINCIPAL
COLOR_FUENTE = tema.COLOR_FUENTE
# El background devuelto por theme puede ser None o un color concreto. Evitar
# forzar blanco por defecto: si el tema devuelve blanco explícito, tratamos
# eso como 'no forzar' para dejar que Streamlit controle el fondo.
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = tema.COLOR_FONDO_OSCURO

COLOR_FONDO_CONTENEDOR = tema.COLOR_FONDO_CONTENEDOR
COLOR_SOMBRA = tema.COLOR_SOMBRA

# Tonos de acento discretos
COLOR_ACENTO_1 = COLOR_PRINCIPAL
COLOR_ACENTO_2 = _colors.get('muted', '#888888')
COLOR_ACENTO_3 = COLOR_ACENTO_2
COLOR_GRID = tema.COLOR_GRID
COLOR_BORDE = tema.COLOR_BORDE

# Paleta de colores ULTRA-SATURADOS con nombres descriptivos
get_color_sequence = tema.get_color_sequence


def get_theme(mode: str = 'dark') -> dict:
    return {
        'COLOR_PRINCIPAL': COLOR_PRINCIPAL,
        'COLOR_FUENTE': COLOR_FUENTE,
        'COLOR_FONDO_OSCURO': COLOR_FONDO_OSCURO,
        'COLOR_FONDO_CONTENEDOR': COLOR_FONDO_CONTENEDOR,
        'COLOR_SOMBRA': COLOR_SOMBRA,
        'get_color_sequence': get_color_sequence,
    }


def get_plotly_layout(xaxis_color: str = None, yaxis_color: str = None) -> dict:
    """Delegar al layout de `theme.py` cuando sea posible; usar valores neutrales si falla."""
    try:
        return theme_get_plotly_layout(xaxis_color, yaxis_color)
    except Exception:
        xa = xaxis_color or COLOR_FUENTE
        ya = yaxis_color or COLOR_FUENTE
        # Forzar fondo completamente transparente para las gráficas (usuario lo solicitó)
        bg = tema.COLOR_TRANSPARENTE
        return {
            'plot_bgcolor': bg,
            'paper_bgcolor': bg,
            'font_color': COLOR_FUENTE,
            'title_font_color': COLOR_PRINCIPAL,
            'xaxis': {'color': xa, 'gridcolor': COLOR_GRID},
            'yaxis': {'color': ya, 'gridcolor': COLOR_GRID},
        }


def get_base64_image(fname: str) -> str:
    """Intentar leer una imagen local y devolver su contenido en base64 (sin prefijo MIME).
    Busca en el directorio del script, en el CWD y en `saved_uploads`.
    Si no se encuentra la imagen, devuelve cadena vacía (la etiqueta <img> quedará vacía).
    """
    search_paths = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, fname))
    except Exception:
        pass
    # cwd
    try:
        search_paths.append(os.path.join(os.getcwd(), fname))
    except Exception:
        pass
    # saved_uploads
    try:
        search_paths.append(os.path.join(os.getcwd(), 'saved_uploads', fname))
    except Exception:
        pass

    for p in search_paths:
        if p and os.path.exists(p):
            try:
                with open(p, 'rb') as fh:
                    b = fh.read()
                return base64.b64encode(b).decode('utf-8')
            except Exception:
                continue
    return ''

# =================== ESTILOS CSS MEJORADOS ===================
st.set_page_config(page_title="Indicadores ALS", layout="wide", initial_sidebar_state="auto")

# Bloque CSS inicial: tarjetas, botones y inputs con gradientes y efecto 3D sutil
_css_lines = []
_css_lines.append("<style>")
# Fondos y colores base según theme
if COLOR_FONDO_OSCURO:
    _css_lines.append(".stApp { background-color: %s !important; }" % COLOR_FONDO_OSCURO)
    if COLOR_FUENTE:
        _css_lines.append(".stApp, .stApp * { color: %s !important; }" % COLOR_FUENTE)

_css_lines.append("h1, h2, h3 { color: %s !important; text-shadow: 0 2px 10px %s33; }" % (COLOR_PRINCIPAL, COLOR_PRINCIPAL))

_container_bg = COLOR_FONDO_CONTENEDOR if COLOR_FONDO_CONTENEDOR else 'transparent'
# Tarjetas principales con efecto glass + 3D
_css_lines.append(
    "div[data-testid=\"stMetric\"] { background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)) !important; "
    "backdrop-filter: blur(6px) saturate(120%%); border-radius: 12px !important; padding: 12px !important; margin-bottom: 12px !important; "
    "box-shadow: 0 10px 30px %s33, 0 4px 8px rgba(0,0,0,0.25) !important; border: 1px solid rgba(255,255,255,0.03) !important; }" % COLOR_PRINCIPAL
)

_css_lines.append(".stDataFrame, .stTable { background: %s !important; color: %s !important; border-radius: 10px !important; box-shadow: 0 8px 30px rgba(0,0,0,0.25) !important; }" % (_container_bg, COLOR_FUENTE))

# Botones con gradiente, borde brillante y efecto 3D al pasar el puntero
_css_lines.append(
    ".stButton>button { background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important; "
    "border: 1px solid %s !important; color: %s !important; border-radius: 10px !important; padding: 10px 14px !important; "
    "box-shadow: 0 6px 18px rgba(0,0,0,0.35), 0 2px 6px rgba(0,0,0,0.2) inset !important; transition: transform 180ms ease, box-shadow 180ms ease; }" % (COLOR_PRINCIPAL, COLOR_PRINCIPAL)
)
_css_lines.append(
    ".stButton>button:hover { transform: translateY(-3px) rotateX(1deg); "
    "box-shadow: 0 18px 50px %s33, 0 6px 20px rgba(0,0,0,0.45) !important; color: %s !important; background: linear-gradient(90deg, %s, %s) !important; }" % (COLOR_PRINCIPAL, tema.COLOR_BLANCO, COLOR_PRINCIPAL, tema.SECUENCIA_COLORES_GRAFICOS[6])
)

# Inputs: suavizar bordes y sombra interior
_css_lines.append(".stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input, .stFileUploader { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.04) !important; border-radius: 8px !important; padding: 8px !important; box-shadow: inset 0 2px 6px rgba(0,0,0,0.2); }")

# Sidebar base transparente para poder customizar secciones
_css_lines.append("[data-testid=\"stSidebar\"] { background: transparent !important; border: none !important; padding: 10px 12px !important; }")

# Efecto sutil en gráficas Plotly
_css_lines.append(".stPlotlyChart > div[role='figure'], .plotly-graph-div { background: rgba(0,0,0,0) !important; border-radius: 10px !important; box-shadow: 0 12px 40px rgba(0,0,0,0.35) !important; }")

# Forzar transparencia dentro de los SVG de Plotly y rects de fondo
_css_lines.append(".plotly .bg, .plotly .plotbg, .plotly .bgrect, .plotly .cartesianlayer .bg { fill: rgba(0,0,0,0) !important; }")
_css_lines.append(".plotly svg { background: transparent !important; }")

# Compact card used in upload area
_css_lines.append(
    ".compact-card { background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); "
    "padding: 8px 12px; border-radius: 10px; display: inline-block; font-weight:700; color: inherit; box-shadow: 0 8px 20px rgba(0,0,0,0.25); margin-bottom:8px; }"
)

# Mejorar estilo de compact-card (tarjetas de carga) y uploader
_css_lines.append(
    # Estilo base de la tarjeta (Fondo oscuro, borde neón)
    ".compact-card, .upload-card { transition: all 0.3s ease; display: inline-block; padding: 18px 24px; border-radius: 16px; font-weight: 700; "
    
    # Color de Texto limpio (Sin text-shadow)
    "color: #ffffff; " +
    
    # Fondo de la tarjeta y Borde (Marco de neón - lo mantenemos para la estructura)
    "background-color: #0a0e27; " +
    "border: 1px solid rgba(41, 1, 94, 0.4); " + # Borde más sutil
    
    # Sombra: La tarjeta 'brilla' de forma muy sutil. Valores de blur bajos y opacidades bajas.
    # El brillo más intenso es el "inset" para que parezca que la luz está DENTRO de la tarjeta.
    "box-shadow: 0 0 3px rgba(41, 1, 94, 0.5), inset 0 0 2px rgba(41, 1, 94, 0.3); " +
    "cursor: default; }"
)

# Estilo al pasar el ratón (Hover): El brillo aumenta de forma apenas perceptible
_css_lines.append(
    ".compact-card:hover, .upload-card:hover { "
    # Aumentamos muy ligeramente el blur y la opacidad para el efecto hover
    "box-shadow: 0 0 6px #C82B96, inset 0 0 3px rgba(217, 0, 206, 0.5); " +
    "transform: translateY(-1px); }"
)

# Aumentar altura de selectboxes y estilo para facilitar lectura
_css_lines.append(
    ".stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input, .stFileUploader { min-height:48px; padding:12px 14px !important; font-size:14px !important; border-radius:10px !important; }"
)

# Específicos para sidebar selectboxes (más altos)
_css_lines.append(
    ".stSidebar .stSelectbox>div>div, .stSidebar .stSelectbox>div>div>div { min-height:48px; padding:12px 14px; font-size:14px; background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border-radius:10px; }"
)

# Estilo para el área de subida personalizada
_css_lines.append(
    ".upload-area { padding:10px; border-radius:10px; background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px dashed rgba(255,255,255,0.06); box-shadow: inset 0 4px 12px rgba(0,0,0,0.06); margin-top:8px; }"
)

_css_lines.append("</style>")
st.markdown('\n'.join(_css_lines), unsafe_allow_html=True)

# Asegúrate de importar la librería html si no lo has hecho:
import html 

# Asumiendo que esta variable está definida en el ámbito global o antes de usar la función:
# COLOR_PRIMARIO = '#00FF99'     # Tu Verde Neón Principal
# COLOR_FUENTE = '#E8F5E9'       # Tu Gris Casi Blanco

def show_success_box(msg: str):
    """
    Muestra un mensaje de éxito con estilo Ciberpunk simple,
    manteniendo la estructura original del código.
    """
    
    # Asignamos la variable para la inyección de CSS. 
    # Usaremos COLOR_PRIMARIO como nuestro COLOR_PRINCIPAL.
    COLOR_PRINCIPAL = tema.COLOR_EXITO_TEXTO
    COLOR_FONDO_OSCURO_BOX = tema.COLOR_EXITO_FONDO_BOX # Fondo oscuro para la caja
    
    # Escapar el mensaje
    safe_msg = html.escape(str(msg))
    
    # Renderizar el HTML y CSS
    st.markdown(f"""
        <div class='success-box'>
            <div class='success-check'>☑</div>
            <div class='success-body'>
                <div class='success-title'>OPERACIÓN HECHA</div>
                <div class='success-message'>{safe_msg}</div>
            </div>
        </div>
        <style>
            /* === ESTILOS CIBERPUNK INYECTADOS === */
            .success-box {{ 
                display:flex; 
                align-items:center; 
                gap: 1rem; /* Espaciado ajustado */
                padding: 1.2rem 1.5rem; 
                border-radius: 12px; 
                
                /* Fondo y Borde Neón */
                background: {COLOR_FONDO_OSCURO_BOX}99; /* Fondo muy oscuro, semi-transparente */
                border: 1px solid {COLOR_PRINCIPAL}aa; 
                
                /* Sombra para el efecto GLOW (reemplaza la caja 3D) */
                box-shadow: 0 0 15px {COLOR_PRINCIPAL}55, inset 0 0 5px {COLOR_PRINCIPAL}22; 
                margin-bottom: 1rem;
            }}
            
            .success-check {{ 
                font-size: 2rem; /* Ícono grande para impacto */
                line-height: 1;
                /* El icono ☑ ya brilla con el filtro de la caja, no requiere más estilos aquí */
            }}
            
            .success-title {{ 
                font-weight: 700; 
                color: {COLOR_PRINCIPAL}; /* Título verde neón */
                font-size: 1.15rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                /* Sombra de texto sutil */
                text-shadow: 0 0 5px {COLOR_PRINCIPAL}33; 
            }}
            
            .success-message {{ 
                color: "{tema.COLOR_BLANCO}"; /* Color del texto del mensaje */
                opacity: 0.9; 
                font-size: 0.95rem;
                margin-top: 0.2rem;
            }}
        </style>
    """, unsafe_allow_html=True)

# =================== FUNCIONES AUXILIARES (mantener igual) ===================
def styled_title(text: str) -> str:
    try:
        # preferir la función del módulo theme si está disponible
        return theme_styled_title(text)
    except Exception:
        return f"<span style=\"color:{COLOR_PRINCIPAL};\">{text}</span>"
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
    # Si no se pasa fecha_evaluacion, preferir la máxima FECHA_FORMA9 disponible
    if fecha_evaluacion is None:
        try:
            if df_forma9 is not None and 'FECHA_FORMA9' in df_forma9.columns:
                tmp_dates = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
                if not tmp_dates.dropna().empty:
                    fecha_evaluacion = tmp_dates.max()
        except Exception:
            fecha_evaluacion = None

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
    # Si no se pasa fecha_evaluacion, preferir la máxima FECHA_FORMA9 disponible
    if fecha_evaluacion is None:
        try:
            if df_forma9 is not None and 'FECHA_FORMA9' in df_forma9.columns:
                tmp_dates = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
                if not tmp_dates.dropna().empty:
                    fecha_evaluacion = tmp_dates.max()
        except Exception:
            fecha_evaluacion = None

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
        # Calcular contraste para asegurar legibilidad: elegir blanco o negro
        def _hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) if len(h) == 6 else (0, 0, 0)

        def _luminance(rgb):
            r, g, b = [c/255.0 for c in rgb]
            for i, v in enumerate((r, g, b)):
                if v <= 0.03928:
                    v = v/12.92
                else:
                    v = ((v+0.055)/1.055) ** 2.4
                if i == 0:
                    r = v
                elif i == 1:
                    g = v
                else:
                    b = v
            return 0.2126*r + 0.7152*g + 0.0722*b

        try:
            rgb = _hex_to_rgb(COLOR_PRINCIPAL)
            lum = _luminance(rgb)
            # Si luminancia alta -> texto oscuro, sino texto blanco
            text_color = tema.COLOR_NEGRO if lum > 0.5 else tema.COLOR_BLANCO
        except Exception:
            text_color = COLOR_FUENTE if COLOR_FUENTE else 'inherit'

        return [f'background-color: {COLOR_PRINCIPAL}; color: {text_color}; font-weight: bold;'] * len(s)
    else:
        return [''] * len(s)

# Título principal y logo grande (estilos específicos por secciones)
# === NUEVAS VARIABLES DE COLOR ===
COLOR_MAGENTA_NEON = tema.COLOR_MAGENTA_NEON   # celeste38C4FF
COLOR_AZUL_CIBER = tema.COLOR_AZUL_CIBER     # Azul Cielo Brillante
COLOR_FONDO_OSCURO = tema.COLOR_FONDO_OSCURO   # Azul Oscuro Profundo
COLOR_FUENTE = tema.COLOR_FUENTE         # Fuente clara con tono azulado
COLOR_GLOW_SUAVE = tema.COLOR_GLOW_SUAVE # Sombra de neón suave (Magenta)

# Usaremos COLOR_MAGENTA_NEON como nuestro COLOR_PRINCIPAL en el CSS
COLOR_PRINCIPAL = COLOR_MAGENTA_NEON
_page_css = ["<style>"]

# 1. ESTILO GLOBAL Y FONDO PROFUNDO
# Aplicamos el fondo y una fuente moderna (si no está Orbitron, usa sans-serif)
_page_css.append(f"""
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    body, .stApp {{ 
        background-color: {COLOR_FONDO_OSCURO} !important; 
        font-family: 'Rajdhani', sans-serif;
        color: {COLOR_FUENTE};
    }}
    
    /* === CORRECCIÓN: ANCHO AMPLIO Y CENTRADO === */
    .main .block-container {{
        max-width: 2000px; /* Ancho amplio (ajusta este valor si lo necesitas) */
        padding-left: 1rem;
        padding-right: 2rem;
        margin-left: 0rem;
        margin-right: 2rem;
    }}
""")

# 2. TITULARES (H1, H2, H3) - CORRECCIÓN PARA EMOJIS
_page_css.append(f"""
    h1, h2, h3 {{ 
        font-family: 'Orbitron', monospace !important;
        font-weight: 700;
        /* Degradado Magenta-Azul */
        background: linear-gradient(90deg, {COLOR_MAGENTA_NEON}, {COLOR_AZUL_CIBER});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none; /* <== CORRECCIÓN: QUITAR GLOW GLOBAL para que los emojis no brillen */
        text-transform: uppercase; 
        letter-spacing: 3px; 
    }}
""")

# 3. TARJETAS / MÉTRICAS (GLASSMORPHISM CON GLOW INTENSO)
# Esto aplica a div[data-testid="stMetric"] que suele ser donde van los números.
_page_css.append(f"""
    div[data-testid="stMetric"] {{ 
        /* Fondo Frosted Glass */
        background: rgba(12, 20, 50, 0.7) !important; 
        backdrop-filter: blur(8px);
        border-radius: 15px !important; 
        padding: 20px !important; 
        margin-bottom: 20px !important; 
        
        /* Borde y Sombra Neón */
        border: 1px solid {COLOR_MAGENTA_NEON}33 !important; 
        box-shadow: 0 0 25px {COLOR_GLOW_SUAVE} !important; 
        transition: all 0.3s;
    }}
    div[data-testid="stMetric"]:hover {{
        box-shadow: 0 0 35px {COLOR_MAGENTA_NEON}88 !important; 
        transform: translateY(-3px);
    }}
    /* Valor del métrico */
    div[data-testid="stMetricValue"] {{
        font-family: 'Orbitron', monospace;
        color: {COLOR_AZUL_CIBER} !important;
        text-shadow: 0 0 10px {COLOR_AZUL_CIBER}55;
    }}
    /* Etiqueta del métrico */
    div[data-testid="stMetricLabel"] {{
        color: {COLOR_FUENTE} !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
""")

# 4. TABLAS Y CONTENEDORES (Más oscuros y con borde neón)
_page_css.append(f"""
    .stDataFrame, .stTable, .stContainer, div[data-testid="stVerticalBlock"] {{ 
        background: {COLOR_FONDO_OSCURO}99 !important; /* Fondo más oscuro */
        border-radius: 5px !important; 
        border: 1px solid {COLOR_AZUL_CIBER}22; /* Borde sutil */
        box-shadow: 0 8px 30px rgba(0,0,0,0.4) !important; 
        padding: 10px;
    }}
""")

# 5. INPUTS Y SELECTBOXES (Fácil de ver)
_page_css.append(f"""
    .stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input, .stFileUploader, div[data-testid="stFileUploadDropzone"] {{ 
        background: {COLOR_FONDO_OSCURO} !important; 
        border: 1px solid {COLOR_MAGENTA_NEON}55 !important;
        color: {COLOR_FUENTE} !important;
        border-radius: 8px !important; 
        padding: 8px !important; 
        transition: all 0.2s;
    }}
    .stTextInput>div>div>input:focus {{
        border-color: {COLOR_AZUL_CIBER} !important;
        box-shadow: 0 0 15px {COLOR_AZUL_CIBER}44 !important;
    }}
""")

# 6. PLOTLY/GRÁFICOS (Fondo transparente)
_page_css.append("""
    .stPlotlyChart > div[role='figure'] { background: rgba(0,0,0,0) !important; border-radius: 10px; }
    .plotly .bg, .plotly .plotbg, .plotly .bgrect, .plotly .cartesianlayer .bg { fill: rgba(0,0,0,0) !important; }
    .plotly svg { background: transparent !important; }
    .plotly .legend rect { fill: rgba(0,0,0,0) !important; stroke: rgba(0,0,0,0) !important; }
    .plotly .legend text, .plotly .legendtitle { fill: currentColor !important; }
    
    /* Z-INDEX: Asegurar visibilidad sobre fondo animado */
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"],  
    div[data-testid="column"],
    section[data-testid="stSidebar"],
    .element-container,
    .stMarkdown,
    .stDataFrame {{
        position: relative;
        z-index: 100 !important;
    }}
""")

_page_css.append("</style>")
st.markdown('\n'.join(_page_css), unsafe_allow_html=True)

# ==================================================================================
# CSS COMPLETO DE RESUMEN_PUBLICO.PY
# ==================================================================================
from dashboard_css import get_dashboard_css
st.markdown(get_dashboard_css(), unsafe_allow_html=True)

# Copiar estilos de header desde `resumen_publico.py` para mantener consistencia visual
DASHBOARD_CSS = f"""
<style>
:root {{
    --color-primary: {tema.COLOR_DASH_PRIMARY};
    --color-secondary: {tema.COLOR_DASH_SECONDARY};
    --color-accent-pink: {tema.COLOR_DASH_PINK};
    --color-accent-orange: {tema.COLOR_DASH_ORANGE};
    --color-accent-cyan: {tema.COLOR_DASH_CYAN};
    --color-accent-green: {tema.COLOR_DASH_GREEN};
    --color-accent-yellow: {tema.COLOR_DASH_YELLOW};
    --color-dark: {tema.COLOR_DASH_DARK};
    --color-light: {tema.COLOR_DASH_LIGHT};
    --gradient-fire: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 25%, #c44569 50%, #a73667 75%, #8b2760 100%);
    --gradient-ocean: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    --gradient-sunset: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    --gradient-aurora: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    --gradient-cosmic: linear-gradient(135deg, #5f2c82 0%, #49a09d 100%);
    --gradient-neon: linear-gradient(135deg, #00f260 0%, #0575e6 100%);
    --radius-xl: 24px;
    --radius-mega: 32px;
    --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.5);
    --shadow-intense: 0 20px 60px rgba(0, 0, 0, 0.4);
    --transition-fast: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}}

@keyframes float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
}}

@keyframes pulse-glow {{
    0%, 100% {{ box-shadow: 0 0 20px rgba(99, 102, 241, 0.5), 0 0 40px rgba(139, 92, 246, 0.3); }}
    50% {{ box-shadow: 0 0 40px rgba(99, 102, 241, 0.8), 0 0 80px rgba(139, 92, 246, 0.6); }}
}}

@keyframes gradient-shift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes shimmer {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}

@keyframes rotate-border {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.stApp {{ background: transparent; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}

.main .block-container {{ padding: 1.2rem 1.8rem; max-width: 100%; }}

.dashboard-header {{
    background: {tema.COLOR_HEADER_BG}; 
    padding: 1.5rem 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    border-bottom: 4px solid {tema.COLOR_HEADER_BORDER}; 
    color: {tema.COLOR_HEADER_TEXT};
    position: relative;
    overflow: hidden;
}}

.dashboard-header::before {{
    content: ''; 
    position: absolute; 
    top: -50%; 
    left: -50%; 
    width: 200%; 
    height: 200%; 
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
    animation: rotate-border 15s linear infinite;
}}

.dashboard-header:hover {{ 
    transform: translateY(-8px) scale(1.01); 
    box-shadow: 
        0 0 100px rgba(236, 0, 212, 0.8),
        0 30px 100px rgba(0, 0, 0, 0.6),
        inset 0 0 150px rgba(255, 255, 255, 0.15);
}}

.header-title {{ font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, {tema.COLOR_BLANCO} 0%, {tema.COLOR_PURPLE_LIGHT} 50%, {tema.COLOR_DASH_PINK} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; text-shadow: 0 5px 20px rgba(255, 255, 255, 0.3); letter-spacing: -1px; position: relative; z-index: 1; }}

.header-date {{ background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 1rem 2.5rem; border-radius: 50px; font-weight: 800; font-size: 1.2rem; border: 2px solid rgba(255, 255, 255, 0.3); color: {tema.COLOR_BLANCO}; box-shadow: 0 0 10px rgba(99, 241, 161, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.1); position: relative; z-index: 1; transition: all var(--transition-fast); }}

.header-date:hover {{ transform: scale(1.05); box-shadow: 0 0 50px rgba(236, 72, 153, 0.08); }}

</style>
"""

st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

# ==================================================================================
# 💻 ESTRUCTURA HTML (con los nuevos estilos)
# ==================================================================================
col1, col2 = st.columns([4, 1])

with col1:
        # Render header consistente con `resumen_publico.py`
        try:
                fecha_display = st.session_state.get('fecha_eval', datetime.now().date())
                try:
                        fecha_str = pd.to_datetime(fecha_display).strftime('%d %b %Y')
                except Exception:
                        fecha_str = str(fecha_display)
        except Exception:
                fecha_str = ''

        try:
                from ui_helpers import get_logo_img_tag
                logo_html = get_logo_img_tag(width=100, style='height:80px; filter: drop-shadow(0 0 10px rgba(200, 43, 150, 0.5));')
        except Exception:
                logo_html = "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='100'/>"

        hero_html = f"""
        <div class='dashboard-header'>
            <div style='display:flex; align-items:center; justify-content:space-between;'>
                <div style='display:flex; align-items:center; gap: 1.5rem;'>
                    {logo_html}
                    <div class='header-title'>INDICADORES ALS</div>
                </div>
                <div class='header-date'>{fecha_str}</div>
            </div>
        </div>
        """
        st.markdown(hero_html, unsafe_allow_html=True)

with col2:
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    try:
        from ui_helpers import get_logo_img_tag
        logo_html_right = get_logo_img_tag(width=280, style='filter: drop-shadow(0 0 10px rgba(200, 43, 150, 0.5));')
    except Exception:
        logo_html_right = "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='280'/>"
    st.markdown(logo_html_right, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)



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

# Obtener colores del tema actual
theme_now = get_theme(st.session_state.get('theme_mode', 'dark'))
accent = theme_now['COLOR_PRINCIPAL']
fg = theme_now['COLOR_FUENTE']

# 🎨 ESTILO ULTRA NEÓN 2025 - SIDEBAR PREMIUM (Sin tocar lógica)
# ==================================================================================
NEON_PRIMARY   = tema.COLOR_AZUL_CIBER     # Cian neón puro (mejor que #66FCF1)
NEON_SECONDARY = tema.COLOR_MAGENTA_NEON     # Magenta para detalles (opcional)
GLOW_COLOR     = tema.COLOR_GLOW_BLUE
TEXT_DEFAULT   = tema.COLOR_TEXTO_DEFAULT
BG_DARK        = tema.COLOR_SIDEBAR_BG_START     # Azul muy oscuro para mayor contraste
BG_CARD        = tema.COLOR_SIDEBAR_CARD_BG

st.sidebar.markdown(f"""
<style>
    /* Fondo sutil de la sidebar para mayor profundidad */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, {BG_DARK} 0%, #0c1421 100%);
        backdrop-filter: blur(10px);
    }}

    /* Enlaces de navegación - Efecto cristal + glow brutal */
    .sidebar-anchor-link {{
        display: block;
        padding: 12px 16px;
        margin: 8px 12px;
        border-radius: 12px;
        text-decoration: none !important;
        color: {TEXT_DEFAULT} !important;
        font-size: 1rem;
        font-weight: 500;
        position: relative;
        overflow: hidden;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        background: {BG_CARD};
        backdrop-filter: blur(8px);
        
        /* Sombra interna suave */
        box-shadow: 
            inset 0 2px 8px rgba(0, 245, 255, 0.08),
            0 2px 10px rgba(0, 0, 0, 0.4);
    }}

    /* HOVER: EFECTO NEÓN EXPLOSIVO */
    .sidebar-anchor-link:hover {{
        color: #00FF99 !important;
        background: linear-gradient(135deg, rgba(0, 245, 255, 0.18), rgba(0, 245, 255, 0.05));
        border: 1px solid {GLOW_COLOR}40;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 
            0 0 20px {GLOW_COLOR}60,
            0 0 40px {GLOW_COLOR}30,
            inset 0 0 20px rgba(0, 245, 255, 0.15);
        
        /* Barra lateral iluminada + brillo de texto */
        text-shadow: 
            0 0 8px {GLOW_COLOR},
            0 0 16px {GLOW_COLOR}80;
    }}

    .sidebar-anchor-link::before {{
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.15), transparent);
        transition: left 0.7s;
    }}

    .sidebar-anchor-link:hover::before {{
        left: 100%;
    }}

    /* TÍTULO DE NAVEGACIÓN - MÁXIMO IMPACTO */
    .sidebar-nav-title {{
        color: {NEON_PRIMARY} !important;
        font-size: 1.65rem;
        font-weight: 900;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 20px 12px 30px 12px;
        padding: 12px 0;
        text-align: center;
        position: relative;
        background: linear-gradient(90deg, transparent, rgba(0, 245, 255, 0.15), transparent);
        border-radius: 12px;
        border: 1px solid {GLOW_COLOR}20;
        
        /* GLOW NUCLEAR */
        text-shadow: 
            0 0 10px {GLOW_COLOR},
            0 0 20px {GLOW_COLOR},
            0 0 40px {GLOW_COLOR},
            0 0 80px {GLOW_COLOR}60;
        
        animation: pulse-glow 4s infinite alternate;
    }}

    @keyframes pulse-glow {{
        0% {{ text-shadow: 0 0 10px {GLOW_COLOR}, 0 0 20px {GLOW_COLOR}, 0 0 40px {GLOW_COLOR}; }}
        100% {{ text-shadow: 0 0 15px {GLOW_COLOR}, 0 0 30px {GLOW_COLOR}, 0 0 60px {GLOW_COLOR}, 0 0 100px {GLOW_COLOR}80; }}
    }}

    /* Metadatos - más elegantes y sutiles */
    .sidebar-metadata {{
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        color: #ffffff;
        opacity: 0.9;
        margin: 20px 12px 10px;
        padding: 12px;
        background: rgba(10, 26, 47, 0.4);
        border-left: 3px solid {GLOW_COLOR}40;
        border-radius: 0 8px 8px 0;
    }}

    .sidebar-metadata p {{
        margin: 4px 0;
        line-height: 1.4;
    }}
</style>
""", unsafe_allow_html=True)

# ==================================================================================
# NAVEGACIÓN SIDEBAR - MISMA LÓGICA, AHORA VISUALMENTE BRUTAL
# ==================================================================================

st.sidebar.markdown(f"""
<div class='sidebar-nav-title'>
    M E N U
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<a href="#resultados-y-reportes" class='sidebar-anchor-link'>    \U0001F4CA Reportes</a>
<a href="#reporte-de-runes" class='sidebar-anchor-link'>         \U0001F3C3 Run Life </a>
<a href="#fallas-mensuales" class='sidebar-anchor-link'>        \U0001F6A8 Fallas </a>
<a href="#listado-de-pozos-fallados" class='sidebar-anchor-link'>\U0001F525 Pozos Fallados</a>
<a href="#indices-de-falla" class='sidebar-anchor-link'>        \U0001F4C9 Índices de Falla</a>
<a href="#mtbf" class='sidebar-anchor-link'>                    \U000023F3 MTBF / MTTR</a>
<a href="#data-frame-final-de-trabajo" class='sidebar-anchor-link'>\U0001F4BE Data Final </a>
<a href="#grafico-resumen" class='sidebar-anchor-link'>         \U0001F53C Gráfico  </a>
""", unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.markdown(f"""
<div class='sidebar-metadata'>
    <p>Módulo de Indicadores <strong>v1.1</strong></p>
    <p>Desarrollado por <strong>AJM</strong></p>
   
</div>
""", unsafe_allow_html=True)


# Resumen público deshabilitado: botón y ejecución remotos eliminados.
# Si necesita reactivar esta funcionalidad, vuelva a añadir un botón que establezca
# una flag en `st.session_state` y que el flujo de importación/ejecución invoque
# `resumen_publico.show_resumen()`.


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
        st.markdown("<div class='upload-area'>", unsafe_allow_html=True)
        forma9_file = st.file_uploader("FORMA 9 (.csv/.xlsx)", type=["csv", "xlsx"], key="forma9_file")
        st.markdown("</div>", unsafe_allow_html=True)
        url_forma9 = st.text_input(
            "URL F9",
            key="url_forma9_excel",
            value="https://1drv.ms/x/c/06cc4035ad46ff97/IQAlCua1BGOXRbcSzUY0OVyzAS8KOoDNxuvUqrsORhjMcKM?e=o8FZyJ",
            help="URL pública de FORMA 9 (OneDrive/SharePoint). Puedes subir un archivo local también."
        )
        
        # Lógica de conexión (descargar a carpeta persistente para evitar problemas en Windows)
        forma9_online_file = None
        if url_forma9:
            try:
                def _download_onedrive(url, dest_path):
                    # Intentar descargar la URL; si devuelve HTML (visor OneDrive), extraer la URL real
                    r = requests.get(url, timeout=30, allow_redirects=True)
                    r.raise_for_status()
                    content_type = r.headers.get('content-type','')
                    content = r.content
                    is_html = 'text/html' in content_type or (isinstance(content, (bytes,bytearray)) and b'<html' in content[:400].lower())
                    if is_html:
                        txt = content.decode('utf-8', errors='ignore')
                        # Buscar FileGetUrl o FileUrlNoAuth en el JSON embebido
                        m = re.search(r'FileGetUrl"\s*:\s*"([^"]+)"', txt) or re.search(r'FileUrlNoAuth"\s*:\s*"([^"]+)"', txt)
                        if m:
                            download_url = m.group(1)
                            # Unescape secuencias \u0026 y slashes
                            download_url = download_url.replace('\\u0026', '&').replace('\\/', '/')
                            download_url = html.unescape(download_url)
                            r2 = requests.get(download_url, timeout=30, allow_redirects=True)
                            r2.raise_for_status()
                            with open(dest_path, 'wb') as fh:
                                fh.write(r2.content)
                            return True
                        else:
                            # No encontramos URL de descarga en la página; guardar el HTML para inspección
                            with open(dest_path, 'wb') as fh:
                                fh.write(content)
                            return True
                    else:
                        with open(dest_path, 'wb') as fh:
                            fh.write(content)
                        return True

                upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
                os.makedirs(upload_dir, exist_ok=True)
                fname = os.path.join(upload_dir, 'forma9_online.xlsx')
                ok = _download_onedrive(url_forma9, fname)
                if ok:
                    forma9_online_file = fname
                    show_success_box("F9 online descargada OK.")
                else:
                    st.error("F9 online: no se pudo descargar el archivo real desde OneDrive.")
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
        st.markdown("<div class='upload-area'>", unsafe_allow_html=True)
        bd_file = st.file_uploader("BD (.csv o .xlsx)", type=["csv", "xlsx"], key="bd_file")
        st.markdown("</div>", unsafe_allow_html=True)
        url_bd = st.text_input(
            "URL BD",
            key="url_bd_excel",
            value="https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=P0xf75",
            help="URL pública de BD (OneDrive/SharePoint). Puedes subir un archivo local también."
        )
        
        # Lógica de conexión (descargar a carpeta persistente para evitar problemas en Windows)
        bd_online_file = None
        if url_bd:
            try:
                upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
                os.makedirs(upload_dir, exist_ok=True)
                fname = os.path.join(upload_dir, 'bd_online.xlsx')
                def _download_onedrive_local(url, dest_path):
                    # Reutilizar la misma lógica que para forma9
                    r = requests.get(url, timeout=30, allow_redirects=True)
                    r.raise_for_status()
                    content_type = r.headers.get('content-type','')
                    content = r.content
                    is_html = 'text/html' in content_type or (isinstance(content, (bytes,bytearray)) and b'<html' in content[:400].lower())
                    if is_html:
                        txt = content.decode('utf-8', errors='ignore')
                        m = re.search(r'FileGetUrl"\s*:\s*"([^"]+)"', txt) or re.search(r'FileUrlNoAuth"\s*:\s*"([^"]+)"', txt)
                        if m:
                            download_url = m.group(1)
                            download_url = download_url.replace('\\u0026', '&').replace('\\/', '/')
                            download_url = html.unescape(download_url)
                            r2 = requests.get(download_url, timeout=30, allow_redirects=True)
                            r2.raise_for_status()
                            with open(dest_path, 'wb') as fh:
                                fh.write(r2.content)
                            return True
                        else:
                            with open(dest_path, 'wb') as fh:
                                fh.write(content)
                            return True
                    else:
                        with open(dest_path, 'wb') as fh:
                            fh.write(content)
                        return True

                ok = _download_onedrive_local(url_bd, fname)
                if ok:
                    bd_online_file = fname
                    show_success_box("BD online descargada OK.")
                else:
                    st.error("BD online: no se pudo descargar el archivo real desde OneDrive.")
            except Exception as e:
                st.error(f"BD online error: {e}")

# --- Tarjeta 3: Parámetros de Evaluación ---
with col_params:
    st.markdown("""
    <div class='compact-card'>
        <span>Parámetros de Evaluación ⚙️</span>
    </div>
    """, unsafe_allow_html=True)
    
    # CSS específico para la alerta de fecha (tarjeta roja)
    st.markdown("""
    <style>
        /* Estilo para el contenedor de la tarjeta */
    .fecha-alerta {
        padding: 0.5rem 1rem;
        background-color: var(--secondary-background-color);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-weight: 700;
        color: var(--text-color);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    # Función auxiliar: último día del mes anterior
    def get_last_day_of_previous_month():
        today = datetime.now().date()
        first_day_of_current_month = today.replace(day=1)
        last_day_prev = first_day_of_current_month - timedelta(days=1)
        return last_day_prev

    with st.container(border=True): 
        # Fecha por defecto: último día del mes anterior
        default_date = get_last_day_of_previous_month()

        # Crear date_input con valor por defecto (editable) y tope en la fecha predeterminada
        fecha_evaluacion = st.date_input(
            "🗓️ Fecha de Evaluación",
            value=default_date,
            key="fecha_eval",
            disabled=False,
            max_value=default_date
        )

        # Mostrar alerta roja con la fecha en formato DD-MM-AAAA
        try:
            fecha_formateada_num = fecha_evaluacion.strftime("%d-%m-%Y")
        except Exception:
            fecha_formateada_num = str(fecha_evaluacion)

        st.markdown("---")
        # Mensaje de alerta que indica la fecha a evaluar y la regla
        st.markdown(f"""
        <div class="fecha-alerta">
            <div><span>FECHA EVALUAR:</span> <b>{fecha_formateada_num}</b></div>
            <div style="margin-top:0.25rem; font-size:0.95rem;">No superar esta fecha.</div>
        </div>
        """, unsafe_allow_html=True)

        # Botón de Cálculo (con ícono)
        calcular_btn = st.button("🚀 Calcular Datos Iniciales", key="calcular_btn", use_container_width=True)

    # Determinar qué archivo usar para cada uno
    # Usar archivo local si existe, si no el online
    forma9_final = forma9_file if forma9_file is not None else forma9_online_file
    bd_final = bd_file if bd_file is not None else bd_online_file
    
    # =================== Lógica de Cálculo (Se mantiene intacta) ===================
    if forma9_final and bd_final:
        show_success_box("¡Ambos archivos cargados! .")
        if calcular_btn:
            # Normalizar entradas: si son rutas (strings) convertir a BytesIO con .name
            def normalize_file(f):
                if f is None:
                    return None
                # Si es un path string (por ejemplo archivo descargado a tmp.name)
                if isinstance(f, str):
                    try:
                        # Intentar abrir la ruta tal cual
                        opened_path = None
                        try:
                            with open(f, 'rb') as fh:
                                data = fh.read()
                            opened_path = f
                        except FileNotFoundError:
                            # Probar rutas alternativas: cwd y saved_uploads
                            candidates = [
                                os.path.join(os.getcwd(), f),
                                os.path.join(os.getcwd(), 'saved_uploads', f)
                            ]
                            opened = False
                            for c in candidates:
                                if os.path.exists(c):
                                    with open(c, 'rb') as fh:
                                        data = fh.read()
                                    opened = True
                                    opened_path = c
                                    break
                            if not opened:
                                raise FileNotFoundError(f"Archivo no encontrado en rutas esperadas: {f}; intentadas: {candidates}")
                        bio = io.BytesIO(data)
                        # asignar atributo name a la ruta completa usada para evitar que pandas intente abrir
                        # un nombre relativo que no exista en Windows
                        bio.name = opened_path or f
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

                        show_success_box("Cálculos finalizados correctamente.")
                except Exception as e:
                    st.error(f"Error durante el procesamiento: {e}")



if st.session_state['reporte_runes'] is not None:
    st.markdown("---")
    st.markdown(f"""
    <h2 id="resultados-y-reportes" style='font-size:2rem; font-weight:700; margin-bottom:0.3em;'>
        <span style='color:{COLOR_PRINCIPAL};'>Resultados y Reportes</span>
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

    # CSS adicional para filtros visuales y sidebar mejor distribuido
        st.markdown(f"""
        <style>
            .filters-row {{ display:flex; gap:18px; align-items:stretch; margin: 8px 0 18px 0; }}
            .filter-card {{ flex:1; padding:14px; border-radius:14px; background: linear-gradient(135deg, {COLOR_PRINCIPAL}11, rgba(255,255,255,0.04)); box-shadow: 0 16px 40px {COLOR_PRINCIPAL}22, 0 6px 18px rgba(0,0,0,0.12); border:1px solid rgba(255,255,255,0.03); display:flex; flex-direction:column; justify-content:center; }}
            .filter-card .filter-value {{ color: {COLOR_PRINCIPAL}; }}
            .filter-card:hover {{ transform: translateY(-4px); transition: all 180ms ease; box-shadow: 0 22px 60px {COLOR_PRINCIPAL}33; }}
            .sidebar-section {{ padding:10px 8px; margin-bottom:12px; border-left:4px solid %s; border-radius:8px; background: linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.02)); }}
            .hero-title {{ padding: 16px 20px; border-radius:14px; background: linear-gradient(90deg, {COLOR_PRINCIPAL}, {tema.SECUENCIA_COLORES_GRAFICOS[6]}); color: #fff; box-shadow: 0 18px 50px {COLOR_PRINCIPAL}44; font-weight:900; letter-spacing:2px; transform: translateZ(0); }}
            .loading-layer {{ padding:12px; border-radius:10px; background: linear-gradient(90deg, rgba(255,255,255,0.03), {COLOR_PRINCIPAL}11); box-shadow: inset 0 -6px 20px rgba(0,0,0,0.12); }}
            /* Estilos mejorados para selectboxes en la sidebar */
            .stSidebar .stSelectbox>div>div, .stSidebar .stSelectbox>div>div>div {{ border-radius:8px; padding:8px 10px; box-shadow: 0 6px 18px rgba(0,0,0,0.15); background: linear-gradient(90deg, rgba(255,255,255,0.02), {COLOR_PRINCIPAL}07); border: 1px solid rgba(255,255,255,0.03); }}
            .stSidebar .stSelectbox>div>div:hover {{ box-shadow: 0 10px 30px {COLOR_PRINCIPAL}22; transform: translateY(-3px); }}
        </style>
        """ % COLOR_PRINCIPAL, unsafe_allow_html=True)

    # Se eliminaron las tarjetas visuales superiores para mostrar sólo los filtros en la sidebar.

    # --- Barra de filtros fijada en la sidebar (usa los mismos keys para no cambiar la funcionalidad) ---
    with st.sidebar:
        # Encabezado de filtros simple (no sticky, para evitar superposición con controles)
        st.subheader("🔎 Filtros")

        # Construir opciones de filtro de forma secuencial para que sean coherentes entre sí.
        df_calc = st.session_state.get('df_bd_calculated', pd.DataFrame())

        # Leer selecciones previas (si existen) para filtrar las opciones disponibles
        sel_activo = st.session_state.get('general_activo_filter', 'TODOS')
        sel_bloque = st.session_state.get('general_bloque_filter', 'TODOS')
        sel_campo = st.session_state.get('general_campo_filter', 'TODOS')
        sel_als = st.session_state.get('general_als_filter', 'TODOS')
        sel_proveedor = st.session_state.get('general_proveedor_filter', 'TODOS')

        # Construir opciones estables a partir del DataFrame base (no dependen de otros filtros)
        def _unique_options(col):
            if df_calc is None or df_calc.empty or col not in df_calc.columns:
                return ['TODOS']
            try:
                opts = sorted(df_calc[col].dropna().astype(str).unique().tolist())
                return ['TODOS'] + opts
            except Exception:
                return ['TODOS']

        activo_options = _unique_options('ACTIVO')
        bloque_options = _unique_options('BLOQUE')
        campo_options = _unique_options('CAMPO')
        als_options = _unique_options('ALS')
        proveedor_options = _unique_options('PROVEEDOR')

        # Asegurar que la selección actual permanezca en la lista de opciones
        def _ensure(options, key_name):
            cur = st.session_state.get(key_name, 'TODOS')
            if cur is None:
                cur = 'TODOS'
            cur = str(cur)
            if cur != 'TODOS' and cur not in options:
                options = options + [cur]
            return options

        activo_options = _ensure(activo_options, 'general_activo_filter')
        bloque_options = _ensure(bloque_options, 'general_bloque_filter')
        campo_options = _ensure(campo_options, 'general_campo_filter')
        als_options = _ensure(als_options, 'general_als_filter')
        proveedor_options = _ensure(proveedor_options, 'general_proveedor_filter')

        # Callback simple para marcar cambio (Streamlit rerun aplica los filtros inmediatamente)
        def _mark_change(key=None):
            st.session_state['filters_last_change'] = datetime.now().isoformat()

        # Mostrar selectboxes preservando el índice de la selección actual
        def _select_with_index(label, options, key):
            cur = st.session_state.get(key, 'TODOS')
            try:
                idx = options.index(str(cur)) if str(cur) in options else 0
            except Exception:
                idx = 0
            return st.selectbox(label, options=options, index=idx, key=key, on_change=_mark_change)

        _select_with_index("🌐 Filtrar por Activo:", activo_options, 'general_activo_filter')
        _select_with_index("🎲 Filtrar por Bloque:", bloque_options, 'general_bloque_filter')
        _select_with_index("🎴 Filtrar por Campo:", campo_options, 'general_campo_filter')
        _select_with_index("🔧 Filtrar por ALS:", als_options, 'general_als_filter')
        _select_with_index("🏭 Filtrar por Proveedor:", proveedor_options, 'general_proveedor_filter')

    # Los valores seleccionados en los filtros se leen desde session_state (sidebar) y
    # se usan directamente para aplicar los filtros más abajo. No se muestran tarjetas
    # ni controles redundantes en el tablero principal para mantener la UI limpia.
    selected_activo = st.session_state.get('general_activo_filter', 'TODOS')
    selected_bloque = st.session_state.get('general_bloque_filter', 'TODOS')
    selected_campo = st.session_state.get('general_campo_filter', 'TODOS')
    selected_als = st.session_state.get('general_als_filter', 'TODOS')
    selected_proveedor = st.session_state.get('general_proveedor_filter', 'TODOS')

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
        <span style='color:{COLOR_PRINCIPAL};'> Reporte de RUNES</span>
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

    # Bloque visual extra: KPIs magenta/azul y toolbar compacto
    st.markdown(f"""
    <style>
      .kpi-row {{ display:flex; gap:18px; margin-top:14px; }}
      .magenta-box {{ flex:1; padding:18px; border-radius:14px; background: linear-gradient(135deg,{tema.COLOR_GRADIENTE_MAGENTA_1},{tema.COLOR_GRADIENTE_MAGENTA_2}); color:{tema.COLOR_BLANCO}; box-shadow: 0 20px 60px {COLOR_PRINCIPAL}33, inset 0 -6px 20px {tema.COLOR_BLANCO_TRANSP_02}; }}
      .blue-box {{ flex:1; padding:18px; border-radius:14px; background: linear-gradient(135deg,{tema.COLOR_GRADIENTE_AZUL_1},{tema.COLOR_GRADIENTE_AZUL_2}); color:{tema.COLOR_NEGRO_SUAVE}; box-shadow: 0 20px 60px {tema.COLOR_SOMBRA_AZUL_44}, inset 0 -6px 20px {tema.COLOR_BLANCO_TRANSP_02}; }}
      .kpi-title {{ font-size:12px; opacity:0.9; }}
      .kpi-value {{ font-size:20px; font-weight:800; margin-top:8px; }}
      .toolbar {{ display:flex; gap:8px; align-items:center; margin-top:10px; }}
      .toolbar .btn {{ padding:8px 12px; border-radius:10px; background: linear-gradient(90deg,{tema.COLOR_BLANCO_TRANSP_11},{tema.COLOR_AZUL_TRANSP_11}); color: #fff; border:1px solid {tema.COLOR_BLANCO_TRANSP_06}; box-shadow: 0 8px 24px {tema.COLOR_SOMBRA_NEGRA_25}; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

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
    <h4 style='margin-top:1em;'>BOPD vs Run Life por Bloque en (años)</h4>
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
        if 4 <= years < 6:
            return '4-6 años'
        if years >= 6:
            return '>6 años'
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
            st.markdown('**Tabla agregada: BOPD (suma) y número de pozos  de Run Life**')
            st.dataframe(agg.rename(columns={'RunLifeBucket': 'Bucket Run Life', 'BOPD_sum': 'BOPD (suma)', 'Pozos': 'Número de Pozos'}), hide_index=True)

            # Gráfica: 4 columnas (x = buckets) con la suma total de BOPD (y). Añadir número de pozos en un cuadrito sobre cada columna.
            fig2 = px.bar(
                agg,
                x='RunLifeBucket',
                y='BOPD_sum',
                color='RunLifeBucket',
                color_discrete_sequence=get_color_sequence(),
                labels={'RunLifeBucket': 'Run Life (años)', 'BOPD_sum': 'BOPD (suma)'},
                title=styled_title('BOPD total por Run Life')
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
                font_dict = {'size': 12}
                if COLOR_FONDO_OSCURO:
                    font_dict['color'] = COLOR_FUENTE

                fig2.add_annotation(
                    x=row['RunLifeBucket'],
                    y=y_ann,
                    text=f"{int(row['Pozos'])}",
                    showarrow=False,
                    font=font_dict,
                    align='center',
                    bgcolor=tema.COLOR_SOMBRA_NEGRA_60,
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
            text_color = COLOR_FUENTE if COLOR_FONDO_OSCURO else 'inherit'
            st.markdown(f"<span style='font-size:11px; color:{text_color};'>{relacion}: {status}</span>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <h3 id="historico-de-run-life-por-campo" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'> Histórico RUN LIFE por Campo</span>
    </h3>
    """, unsafe_allow_html=True)
    # Ajuste de columnas a 50/50 para simetría
    col_table_runlife, col_chart_runlife = st.columns([0.5, 0.5])
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
                title=styled_title('Run Life Promedio Mensual por Activo'),
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
            # Usar layout del theme para respetar la detección de Streamlit
            layout = get_plotly_layout()
            # forzar color de título con acento
            layout.update({'title_font_color': COLOR_PRINCIPAL})
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""
    <h3 id="fallas-mensuales" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'> Fallas Mensuales</span>
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
                    'Infantil': tema.COLOR_RL_INFANTIL,
                    'Prematura': tema.COLOR_RL_PREMATURA,
                    'En Garantía': tema.COLOR_RL_EN_GARANTIA,
                    'Sin Garantía': tema.COLOR_RL_SIN_GARANTIA
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
                fig_runlife.update_layout(barmode='group', title=styled_title('Distribución de Fallas por Run Life y Tipo de Falla IA'), xaxis_title='Tipo de Falla IA', yaxis_title='Cantidad de Fallas', legend_title='Clasificación Run Life')
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
                    title=styled_title(' Distribución de Fallas por Tipo de falla')
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
                    title_html = styled_title('Fallas Mensuales por Activo')
                    
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
                    fig_campo.update_xaxes(showgrid=True, gridcolor=tema.COLOR_GRID_NEON)
                    fig_campo.update_yaxes(showgrid=True, gridcolor=tema.COLOR_GRID_NEON)
                    
                    st.plotly_chart(fig_campo, use_container_width=True)
    else:
        st.info("No hay datos de fallas para mostrar.")

    st.markdown("---")
    st.markdown(f"""
    <h3 id="listado-de-pozos-fallados" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
        <span style='color:{COLOR_PRINCIPAL};'> Listado de Pozos Fallados</span>
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
            st.markdown(f"<span style='font-size:1.1rem; color:{COLOR_PRINCIPAL}; font-weight:700;'>Pozos Problema</span>", unsafe_allow_html=True)
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
                        text_color = COLOR_FUENTE if COLOR_FONDO_OSCURO else 'inherit'
                        if len(razones) == 0:
                            st.markdown(f"<span style='color: {text_color};'>No hay razones disponibles</span>", unsafe_allow_html=True)
                        else:
                            for i, razon in enumerate(razones, 1):
                                clasificacion = clasificar_razon_ia(razon)
                                st.markdown(f"<span style='color: {text_color};'>* Falla {i} Razón: {razon} | Clasificación IA: <b style='color:{COLOR_PRINCIPAL}'>{clasificacion}</b></span>", unsafe_allow_html=True)
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
            <span style='color:{COLOR_PRINCIPAL};'> Índices de Falla</span>
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
                col_hist_line, col_bar_mes = st.columns([0.5, 0.5])
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
                    layout = get_plotly_layout()
                    # No sobrescribir 'legend' por completo (evita eliminar bgcolor transparente)
                    layout.update({'xaxis': {'categoryorder':'category ascending'}, 'height':220, 'margin':dict(l=10, r=10, t=40, b=10)})
                    # Ajustar el tamaño de fuente de la leyenda sin perder bgcolor/border
                    layout.setdefault('legend', {})
                    layout['legend'].setdefault('font', {})
                    layout['legend']['font']['size'] = 10
                    layout.update({'title_font_color': COLOR_PRINCIPAL})
                    fig_line.update_layout(**layout)
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
                    layout = get_plotly_layout()
                    layout.update({'xaxis': {'categoryorder':'category ascending'}, 'height':220, 'margin':dict(l=10, r=10, t=40, b=10)})
                    layout.setdefault('legend', {})
                    layout['legend'].setdefault('font', {})
                    layout['legend']['font']['size'] = 10
                    layout.update({'title_font_color': COLOR_PRINCIPAL})
                    fig_bar.update_layout(**layout)
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
                    layout = get_plotly_layout()
                    layout.update({'xaxis': {'categoryorder':'category ascending'}})
                    layout.update({'title_font_color': COLOR_PRINCIPAL})
                    fig.update_layout(**layout)
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Ocurrió un error al calcular los índices de falla. Asegúrate de que los datos filtrados contengan la información necesaria: {e}")
        # Mostrar MTBF después del índice de falla
        st.markdown(f"""
        <h3 id="mtbf" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
            <span style='color:{COLOR_PRINCIPAL};'>MTBF</span>
        </h3>
        """, unsafe_allow_html=True)
        try:
            mtbf_global, mtbf_por_pozo = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
            mostrar_mtbf(mtbf_global, mtbf_por_pozo, df_bd=df_bd_filtered, fecha_evaluacion=fecha_evaluacion)
        except Exception as e:
            st.warning(f"No se pudo calcular el MTBF: {e}")

        st.markdown(f"""
        <h3 id="dataframe-final-de-trabajo" style='font-size:1.4rem; font-weight:700; margin-top:1em;'>
            <span style='color:{COLOR_PRINCIPAL};'> DataFrame Final de TRABAJO</span>
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
            st.warning(f"No se pudieron agregar gráficas: {{e}}")

        if st.button(' Descargar Reporte Completo (.xlsx)', use_container_width=True):
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
                st.markdown(f"<h3 style='margin-top:1em; color:{{COLOR_PRINCIPAL}};'> Gráfico Resumen</h3>", unsafe_allow_html=True)
                
                # Gráfico Dinámico: Plotly y ajuste de ancho asegurado
                st.plotly_chart(fig_resumen, use_container_width=True)
                
                # ELIMINADO: No se muestra la tabla (df_resumen) para que el gráfico sea el único foco
                # st.dataframe(df_resumen, hide_index=True) 
        except Exception as e:
            st.warning(f"No se pudo generar el gráfico resumen: {{e}}")


