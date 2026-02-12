# --- ESTILO PARA TABLAS ---
import streamlit as st
import pandas as pd
import numpy as np

# CONFIGURACIÓN DE PÁGINA ANCHO TOTAL (WIDE MODE)
st.set_page_config(
    page_title="Indicadores ALS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para importar estilos desde dashboard_css.py Y agregar estilos de tablas
def inject_custom_css():
    """Inyecta CSS básico sin modificar el sidebar por defecto de Streamlit."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=Inter:wght@300;400;600&display=swap');

        /* --- CONFIGURACIÓN BÁSICA SIN MODIFICAR SIDEBAR --- */
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Contenedor principal - sin márgenes especiales */
        [data-testid="stMainBlockContainer"] {
            padding: 1rem !important;
            box-sizing: border-box !important;
        }

        /* MOSTRAR todos los elementos de Streamlit */
        [data-testid="stToolbar"] {
            display: block !important;
            visibility: visible !important;
        }

        [data-testid="stHeader"] {
            display: block !important;
            visibility: visible !important;
        }

        /* --- Global & Background --- */
        .stApp {
            background-color: #0a0e27 !important;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(19, 91, 236, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0, 242, 255, 0.05) 0%, transparent 40%) !important;
            font-family: 'Inter', sans-serif !important;
        }

    /* --- Sidebar Premium HUD Design --- */
        [data-testid="stSidebar"] {
            background-color: #060a1e !important;
            background-image: 
                radial-gradient(circle at 0% 0%, rgba(0, 242, 255, 0.08) 0%, transparent 50%),
                linear-gradient(180deg, #060a1e 0%, #030612 100%) !important;
            border-right: 1px solid rgba(0, 242, 255, 0.2) !important;
            box-shadow: 10px 0 30px rgba(0,0,0,0.5) !important;
        }

        /* HUD Scanline Effect - Sutil */
        [data-testid="stSidebar"]::before {
            content: " ";
            position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%);
            z-index: 100;
            background-size: 100% 4px;
            pointer-events: none;
            opacity: 0.2;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            gap: 1.2rem !important;
            padding: 2rem 1rem !important;
        }

        /* Sidebar Text & Labels */
        [data-testid="stSidebar"] .stMarkdown p {
            font-family: 'Inter', sans-serif !important;
            color: #94a3b8 !important;
            font-size: 0.9rem !important;
        }

        [data-testid="stSidebar"] label {
            font-family: 'Outfit', sans-serif !important;
            color: #00f2ff !important;
            text-transform: uppercase !important;
            letter-spacing: 0.15em !important;
            font-weight: 700 !important;
            font-size: 0.7rem !important;
            margin-bottom: 0.5rem !important;
            text-shadow: 0 0 5px rgba(0, 242, 255, 0.2) !important;
        }

        /* --- Custom Inputs Styling (HUD Style) --- */
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
            background-color: rgba(10, 15, 30, 0.7) !important;
            border: 1px solid rgba(0, 242, 255, 0.2) !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {
            border-color: #00f2ff !important;
            background-color: rgba(10, 15, 30, 0.9) !important;
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.15) !important;
            transform: translateY(-1px);
        }

        [data-testid="stSidebar"] .stSelectbox div[aria-selected="true"] {
            color: #fff !important;
            font-weight: 600 !important;
        }

        /* Títulos en Sidebar */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            font-family: 'Outfit', sans-serif !important;
            color: #ff00ff !important;
            text-transform: uppercase !important;
            letter-spacing: 0.2em !important;
            font-weight: 900 !important;
            font-size: 1.1rem !important;
            margin-top: 1rem !important;
            margin-bottom: 1.5rem !important;
            text-shadow: 0 0 15px rgba(255, 0, 255, 0.3) !important;
            border-bottom: 1px solid rgba(255, 0, 255, 0.2);
            padding-bottom: 0.5rem;
        }

        /* Sidebar Scrollbar */
        [data-testid="stSidebar"] ::-webkit-scrollbar {
            width: 4px;
        }
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
            background: rgba(0, 242, 255, 0.2);
            border-radius: 10px;
        }
 
        /* --- Estilo para Botones de Zoom (Más elegantes y pequeños) --- */
        button[kind="secondary"].st-emotion-cache-19rxjzo, 
        button[key*="btn_zoom"] {
            height: 28px !important;
            min-height: 28px !important;
            padding: 0 12px !important;
            font-size: 11px !important;
            background: rgba(200, 43, 150, 0.1) !important;
            border: 1px solid rgba(200, 43, 150, 0.3) !important;
            color: #ff00ff !important;
            border-radius: 20px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            transition: all 0.3s ease !important;
            width: auto !important;
            margin: 0 auto !important;
            display: block !important;
        }

        button[key*="btn_zoom"]:hover {
            background: rgba(200, 43, 150, 0.3) !important;
            border-color: #ff00ff !important;
            box-shadow: 0 0 15px rgba(200, 43, 150, 0.4) !important;
            transform: translateY(-1px);
        }
 
        /* --- Global Enhancements --- */
        .stPlotlyChart {
            background: transparent !important;
            border-radius: 15px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
        }
        
        /* Mantener footer oculto pero mostrar menú principal */
        footer {visibility: hidden !important;}
        
    </style>
    """, unsafe_allow_html=True)



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
from theme import get_colors, get_plotly_layout as theme_get_plotly_layout, styled_title as theme_styled_title, plotly_styled_title as theme_plotly_styled_title
import requests
import json
import streamlit.components.v1 as components
import tempfile
import os
import re
import html
import importlib
import tema
import base64
import pickle
from pathlib import Path
from run_life_efectivo import calcular_run_life_efectivo

@st.cache_data(show_spinner="Descargando archivo desde la nube...", ttl=600)
def cached_onedrive_download(url, dest_filename):
    """
    Descarga un archivo desde OneDrive/SharePoint y lo guarda localmente.
    Usa cache para evitar descargas repetidas en cada rerun de Streamlit.
    """
    import requests
    import re
    import html
    import os
    
    upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    dest_path = os.path.join(upload_dir, dest_filename)
    
    try:
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
                return dest_path
            else:
                # No encontramos URL de descarga en la página; guardar el HTML para inspección
                with open(dest_path, 'wb') as fh:
                    fh.write(content)
                return dest_path
        else:
            with open(dest_path, 'wb') as fh:
                fh.write(content)
            return dest_path
    except Exception as e:
        # Si falla la descarga, devolvemos None para que el flujo principal lo maneje
        return None

CACHE_DIR = Path("cache_data")
CACHE_FILE = CACHE_DIR / "last_run_data.pkl"

def save_cached_data(df_bd, df_forma9, fecha_eval, reporte_runes, historico, reporte_fallas):
    """Guarda los dataframes y variables clave en un archivo pickle."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            'df_bd': df_bd,
            'df_forma9': df_forma9,
            'fecha_evaluacion': fecha_eval,
            'reporte_runes': reporte_runes,
            'historico_run_life': historico,
            'reporte_fallas': reporte_fallas
        }
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        print(f"Error guardando caché: {e}")
        return False

def load_cached_data():
    """Carga los datos desde el archivo pickle si existe."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(f"Error cargando caché: {e}")
        return None
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
# st.set_page_config eliminada de aquí por ser redundante y causar conflictos

# --- INTENTO DE CARGA AUTOMÁTICA DE CACHÉ AL INICIO ---
if 'data_loaded_from_cache' not in st.session_state:
    cached_data = load_cached_data()
    if cached_data:
        st.session_state['df_bd_calculated'] = cached_data['df_bd']
        st.session_state['df_forma9_calculated'] = cached_data['df_forma9']
        st.session_state['fecha_evaluacion_state'] = cached_data['fecha_evaluacion'] # Guardar fecha para usarla
        st.session_state['reporte_runes'] = cached_data['reporte_runes']
        st.session_state['historico_run_life'] = cached_data['historico_run_life']
        st.session_state['reporte_fallas'] = cached_data['reporte_fallas']
        st.session_state['data_loaded_from_cache'] = True
        # Mensaje discreto de éxito
        st.toast(f"✅ Datos precargados del {cached_data['fecha_evaluacion'].strftime('%d-%m-%Y')}", icon="💾")
    else:
        st.session_state['data_loaded_from_cache'] = False

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
    ".compact-card, .upload-card { transition: all 0.3s ease; display: inline-block; padding: 18px 24px; border-radius: 16px; font-weight: 700; "
    "color: #ffffff; background-color: #0a0e27; border: 1px solid rgba(41, 1, 94, 0.4); "
    "box-shadow: 0 0 3px rgba(41, 1, 94, 0.5), inset 0 0 2px rgba(41, 1, 94, 0.3); cursor: default; }"
)

_css_lines.append(
    ".compact-card:hover, .upload-card:hover { "
    "box-shadow: 0 0 6px #C82B96, inset 0 0 3px rgba(217, 0, 206, 0.5); transform: translateY(-1px); }"
)

# Aumentar altura de selectboxes y estilo para facilitar lectura
_css_lines.append(
    ".stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input, .stFileUploader { min-height:48px; padding:12px 14px !important; font-size:14px !important; border-radius:10px !important; }"
)

# Estilo para el área de subida personalizada
_css_lines.append(
    ".upload-area { padding:10px; border-radius:10px; background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px dashed rgba(255,255,255,0.06); box-shadow: inset 0 4px 12px rgba(0,0,0,0.06); margin-top:8px; }"
)

# === RESTAURAR SIDEBAR POR DEFECTO - SIN MODIFICACIONES DE LAYOUT ===
# Solo aplicar estilos visuales básicos sin afectar posicionamiento

_css_lines.append(
    "[data-testid=\"stToolbar\"] { "
    "display: block !important; "
    "visibility: visible !important; "
    "}"
)

_css_lines.append(
    "[data-testid=\"stHeader\"] { "
    "display: block !important; "
    "visibility: visible !important; "
    "}"
)

# === ELIMINAR SCROLL HORIZONTAL ===
# Aplicar overflow-x: hidden en todos los niveles

_css_lines.append(
    "html, body { "
    "overflow-x: hidden !important; "
    "max-width: 100vw !important; "
    "}"
)

_css_lines.append(
    "[data-testid=\"stAppViewContainer\"] { "
    "overflow-x: hidden !important; "
    "max-width: 100vw !important; "
    "}"
)

_css_lines.append(
    "[data-testid=\"stMainBlockContainer\"] { "
    "overflow-x: hidden !important; "
    "max-width: 100% !important; "
    "box-sizing: border-box !important; "
    "}"
)

_css_lines.append(
    "[data-testid=\"stVerticalBlock\"], [data-testid=\"stHorizontalBlock\"] { "
    "overflow-x: hidden !important; "
    "max-width: 100% !important; "
    "box-sizing: border-box !important; "
    "}"
)

_css_lines.append(
    "[data-testid=\"column\"] { "
    "overflow-x: hidden !important; "
    "max-width: 100% !important; "
    "box-sizing: border-box !important; "
    "}"
)

_css_lines.append(
    ".stDataFrame, .stTable { "
    "max-width: 100% !important; "
    "overflow-x: auto !important; "
    "box-sizing: border-box !important; "
    "}"
)

_css_lines.append(
    "div.row-widget { "
    "overflow-x: hidden !important; "
    "max-width: 100% !important; "
    "}"
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
def styled_title(text: str, subtitle: str = None) -> str:
    try:
        # preferir la función del módulo theme si está disponible
        return theme_styled_title(text, subtitle)
    except Exception:
        if subtitle:
            return f"<div style='color:{COLOR_PRINCIPAL}; font-size: 0.8em;'>{subtitle}</div><span style=\"color:{COLOR_PRINCIPAL}; font-size: 1.5em; font-weight: bold;\">{text}</span>"
        return f"<span style=\"color:{COLOR_PRINCIPAL};\">{text}</span>"

def plotly_styled_title(text: str) -> str:
    try:
        return theme_plotly_styled_title(text)
    except Exception:
        return f"<b>{text.upper()}</b>"
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

@st.cache_data(show_spinner="Procesando cálculos iniciales...")
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

    # --- Integración Run Life Efectivo ---
    run_life_efectivo_promedio = 0.0
    try:
        # Calculamos y actualizamos df_bd con la nueva columna RUN_LIFE_EFECTIVO
        run_life_efectivo_promedio, df_bd = calcular_run_life_efectivo(df_bd, df_forma9, fecha_evaluacion)
        print(f"\n[OK] Run Life Efectivo calculado exitosamente: {run_life_efectivo_promedio:.2f} dias")
    except Exception as e:
        print(f"[ERROR] Error calculando Run Life Efectivo: {e}")
        import traceback
        traceback.print_exc()

    # Guardar en DataFrame para que esté disponible después
    df_bd.attrs['run_life_efectivo_promedio'] = run_life_efectivo_promedio
    
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

@st.cache_data(show_spinner="Generando reporte detallado...")
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

    fecha_evaluacion = pd.to_datetime(fecha_evaluacion).normalize()
    
    df_bd['FECHA_PULL_DATE'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce')
    df_bd['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    df_bd['FECHA_RUN_DATE'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')

    df_bd_eval = df_bd[df_bd['FECHA_RUN_DATE'].dt.normalize() <= fecha_evaluacion].copy()
    
    extraidos_count = df_bd_eval[df_bd_eval['FECHA_PULL_DATE'].dt.normalize() <= fecha_evaluacion].shape[0]

    running_count = df_bd_eval[
        (df_bd_eval['FECHA_RUN_DATE'].dt.normalize() <= fecha_evaluacion) &
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.normalize() > fecha_evaluacion))
    ].shape[0]

    fallados_count = df_bd_eval[
        (df_bd_eval['FECHA_FALLA_DATE'].dt.normalize() <= fecha_evaluacion) &
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.normalize() > fecha_evaluacion))
    ].shape[0]

    pozos_operativos = df_bd_eval[
        (df_bd_eval['FECHA_FALLA_DATE'].isna() | (df_bd_eval['FECHA_FALLA_DATE'].dt.normalize() > fecha_evaluacion)) & 
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.normalize() > fecha_evaluacion))
    ].shape[0]

    df_forma9_eval = df_forma9[
        (df_forma9['FECHA_FORMA9'].dt.normalize() >= (fecha_evaluacion - pd.Timedelta(days=30))) &
        (df_forma9['FECHA_FORMA9'].dt.normalize() <= fecha_evaluacion)
    ]
    pozos_on = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()

    pozos_off = abs(pozos_operativos - pozos_on)

    totales_count = extraidos_count + running_count

    reporte_runes = pd.DataFrame({
        'Categoría': ['Extraídos', 'En Fondo', 'Fallados', 'Pozos ON', 'Pozos OFF', 'Pozos Operativos', 'Totales'],
        'Conteo': [extraidos_count, running_count, fallados_count, pozos_on, pozos_off, pozos_operativos, totales_count]
    })
    
    verificaciones = {
        'On + Off = Operativos': pozos_on + pozos_off == pozos_operativos,
        'Fallados + Operativos = En Fondo': fallados_count + pozos_operativos == running_count,
        'En Fondo + Extraídos = Totales': running_count + extraidos_count == totales_count
    }

    # Calculo Correcto de Run Life Promedio (Solo eventos YA ocurridos a la fecha de corte)
    mask_ended_eval = (
        ((df_bd_eval['FECHA_PULL_DATE'].notna()) & (df_bd_eval['FECHA_PULL_DATE'].dt.normalize() <= fecha_evaluacion)) |
        ((df_bd_eval['FECHA_FALLA_DATE'].notna()) & (df_bd_eval['FECHA_FALLA_DATE'].dt.normalize() <= fecha_evaluacion))
    )
    run_life_apagados_fallados = df_bd_eval[mask_ended_eval]['RUN LIFE'].mean()
    run_life_general = df_bd_eval['RUN LIFE'].mean()
    
    reporte_run_life = pd.DataFrame({
        'Categoría': ['Tiempo de Vida Promedio (Fallados+Ext)', 'Tiempo de vida General'],
        'Valor': [run_life_apagados_fallados, run_life_general]
    })
    
    # Calcular Run Life Efectivo y agregarlo al reporte
    try:
        run_life_efectivo_val, df_rle_result = calcular_run_life_efectivo(df_bd_eval, df_forma9, fecha_evaluacion)
        
        # Calcular RLE solo para fallados/extraídos
        # Necesitamos que df_rle_result mantenga el índice o podamos filtrar por la misma máscara
        # mask_ended_eval aplica a df_bd_eval, que es la entrada de calcular_run_life_efectivo
        rle_fallados_val = df_rle_result[mask_ended_eval]['RUN_LIFE_EFECTIVO'].mean() if not df_rle_result[mask_ended_eval].empty else 0.0

        # Agregar al reporte
        reporte_run_life = pd.concat([
            reporte_run_life,
            pd.DataFrame({
                'Categoría': ['Tiempo de vida Efectivo (TODOS)', 'Tiempo de vida efectivo de equipos fallados'],
                'Valor': [run_life_efectivo_val, rle_fallados_val]
            })
        ], ignore_index=True)
    except Exception as e:
        print(f"[WARNING] No se pudo agregar Run Life Efectivo al reporte: {e}")
    
    return reporte_runes, reporte_run_life, verificaciones

@st.cache_data(show_spinner="Calculando histórico de Run Life...")
def generar_historico_run_life(df_bd_calculated, fecha_evaluacion):
    """
    Calcula el run life promedio mensual acumulado por ACTIVO considerando todos los RUNs
    FALLADOS o FINALIZADOS (Pull) hasta el cierre de cada mes.
    Lógica: Para cada mes, filtrar runs con Fecha Fin <= Fin Mes. Calcular promedio acumulado.
    """
    end_date = pd.to_datetime(fecha_evaluacion)
    start_date = end_date - timedelta(days=365 * 3)
    meses = pd.date_range(start=start_date, end=end_date, freq='MS')
    historico = []

    # Asegurar columnas de fecha temporales para filtrado
    df_bd = df_bd_calculated.copy()
    if 'FECHA_PULL' in df_bd.columns:
        df_bd['FECHA_PULL_DT'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce')
    else:
        df_bd['FECHA_PULL_DT'] = pd.NaT
        
    if 'FECHA_FALLA' in df_bd.columns:
        df_bd['FECHA_FALLA_DT'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    else:
        df_bd['FECHA_FALLA_DT'] = pd.NaT

    # Asegurar que RUN LIFE exista o recalcularlo para consistencia
    if 'RUN LIFE' not in df_bd.columns:
         df_bd['RUN LIFE'] = np.where(
            df_bd['FECHA_FALLA_DT'].notna(),
            (df_bd['FECHA_FALLA_DT'] - pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')).dt.days,
            np.where(
                df_bd['FECHA_PULL_DT'].notna(),
                (df_bd['FECHA_PULL_DT'] - pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')).dt.days,
                np.nan
            )
        )

    for mes in meses:
        fin_mes = mes + pd.offsets.MonthEnd(0)
        
        # Filtro: Runs que terminaron (Falla o Pull) en o antes de fin_mes
        mask_ended = (
            ((df_bd['FECHA_FALLA_DT'].notna()) & (df_bd['FECHA_FALLA_DT'] <= fin_mes)) |
            ((df_bd['FECHA_PULL_DT'].notna()) & (df_bd['FECHA_PULL_DT'] <= fin_mes))
        )
        ended_runs = df_bd[mask_ended].copy()

        if not ended_runs.empty:
            if 'ACTIVO' in ended_runs.columns:
                # Agrupar por activo
                promedio = ended_runs.groupby('ACTIVO')['RUN LIFE'].mean().reset_index()
                promedio['Mes'] = fin_mes
                promedio.rename(columns={'RUN LIFE': 'Tiempo Op. Promedio'}, inplace=True)
                historico.append(promedio)
            else:
                # Sin activo, global (aunque la función espera por activo, defensive)
                val = ended_runs['RUN LIFE'].mean()
                historico.append(pd.DataFrame({'Mes': [fin_mes], 'ACTIVO': ['Global'], 'Tiempo Op. Promedio': [val]}))

    if historico:
        df_historico = pd.concat(historico, ignore_index=True)
        return df_historico[['Mes', 'ACTIVO', 'Tiempo Op. Promedio']]
    else:
        return pd.DataFrame(columns=['Mes', 'ACTIVO', 'Tiempo Op. Promedio'])


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

        # Injection of Premium Header
        header_style = f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;800&family=Inter:wght@200;300;400;500;600;700&display=swap');
            
            .hero-container-base {{
                position: relative;
                width: 100%;
                margin: 1rem 0 2.5rem 0;
                overflow: hidden;
                border-radius: 1.5rem;
                background: rgba(10, 14, 39, 0.7);
                padding: 2.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(25px);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                color: white !important;
                font-family: 'Inter', sans-serif;
            }}
            
            .hero-bg-glow {{
                position: absolute;
                inset: 0;
                background: radial-gradient(circle at 20% 30%, rgba(19, 91, 236, 0.15), transparent 50%),
                            radial-gradient(circle at 80% 70%, rgba(0, 242, 255, 0.1), transparent 50%);
                pointer-events: none;
            }}
            
            .hero-flex-layout {{
                position: relative;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 2rem;
                z-index: 10;
            }}
            
            .hero-left-side {{
                display: flex;
                align-items: center;
                gap: 2rem;
            }}
            
            .logo-aura-effect {{
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .logo-aura-effect::before {{
                content: '';
                position: absolute;
                width: 120%;
                height: 120%;
                background: radial-gradient(circle, rgba(19, 91, 236, 0.4) 0%, transparent 70%);
                filter: blur(15px);
                z-index: 0;
            }}
            
            .header-text-main {{
                display: flex;
                flex-direction: column;
            }}
            
            .header-upper-tag {{
                font-size: 10px;
                font-weight: 800;
                color: #00f2ff;
                text-transform: uppercase;
                letter-spacing: 0.4em;
                margin-bottom: 0.5rem;
                opacity: 0.8;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .header-upper-tag::before {{
                content: '';
                height: 1px;
                width: 30px;
                background: linear-gradient(to right, #00f2ff, transparent);
            }}
            
            .main-title-text {{
                font-family: 'Outfit', sans-serif;
                font-size: 3.5rem;
                font-weight: 900;
                line-height: 1;
                margin: 0;
                letter-spacing: -0.02em;
            }}
            
            .title-gradient-als {{
                background: linear-gradient(-45deg, #135bec, #00f2ff, #135bec, #00f2ff);
                background-size: 300% 300%;
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: flowGradient 5s ease infinite;
            }}
            
            @keyframes flowGradient {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .meta-info-row {{
                display: flex;
                align-items: center;
                gap: 1.5rem;
                margin-top: 1.25rem;
            }}
            
            .active-status-tag {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(0, 242, 255, 0.1);
                border: 1px solid rgba(0, 242, 255, 0.3);
                padding: 4px 12px;
                border-radius: 20px;
            }}
            
            .pulse-dot {{
                width: 6px;
                height: 6px;
                background: #00f2ff;
                border-radius: 50%;
                box-shadow: 0 0 10px #00f2ff;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.4; transform: scale(1.2); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            
            .status-txt {{
                font-size: 9px;
                font-weight: 900;
                color: #00f2ff;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            }}
            
            .version-txt {{
                font-size: 10px;
                color: rgba(255,255,255,0.4);
                letter-spacing: 0.2em;
                text-transform: uppercase;
                font-style: italic;
            }}
            
            .date-display-box {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 1.25rem 2rem;
                border-radius: 1.25rem;
                text-align: right;
                min-width: 220px;
            }}
            
            .date-lbl {{
                font-size: 10px;
                font-weight: 700;
                color: rgba(255,255,255,0.5);
                text-transform: uppercase;
                letter-spacing: 0.2em;
                display: block;
                margin-bottom: 0.5rem;
            }}
            
            .date-val {{
                font-family: 'Outfit', sans-serif;
                font-size: 2rem;
                font-weight: 800;
                color: white;
                letter-spacing: 0.05em;
            }}
            
            @media (max-width: 1024px) {{
                .hero-flex-layout {{
                    flex-direction: column;
                    text-align: center;
                }}
                .hero-left-side {{
                    flex-direction: column;
                }}
                .header-upper-tag {{
                    justify-content: center;
                }}
                .meta-info-row {{
                    justify-content: center;
                }}
                .date-display-box {{
                    text-align: center;
                }}
            }}
        </style>
        """
        
        hero_html = f"""
        <div class="hero-container-base">
            <div class="hero-bg-glow"></div>
            <div class="hero-flex-layout">
                <div class="hero-left-side">
                    <div class="logo-aura-effect">
                        <div style="position: relative; z-index: 2;">{logo_html}</div>
                    </div>
                    <div class="header-text-main">
                        <div class="header-upper-tag">Advanced Analytics System</div>
                        <h1 class="main-title-text">
                            <span>INDICADORES</span>
                            <span class="title-gradient-als">ALS</span>
                        </h1>
                        <div class="meta-info-row">
                            <div class="active-status-tag">
                                <span class="pulse-dot"></span>
                                <span class="status-txt">Node Active</span>
                            </div>
                            <span class="version-txt">Matrix v5.2.4</span>
                        </div>
                    </div>
                </div>
                <div class="date-display-box">
                    <span class="date-lbl">Fecha de Evaluación</span>
                    <div class="date-val">{fecha_str.upper()}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(header_style, unsafe_allow_html=True)
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
    /* Fondo transparente para el contenido interno ya que el contenedor padre es la tarjeta flotante */
    section[data-testid="stSidebar"] > div {{
        background: transparent !important;
        padding-top: 2rem !important;
    }}

    /* --- SIDEBAR UNIFIED STYLES --- */
    .sidebar-header-unified {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.05);
    }}
    .sidebar-header-unified .icon {{
        font-size: 1.1rem;
        line-height: 1;
    }}
    .sidebar-header-unified .title {{
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 0.9rem;
        background: linear-gradient(90deg, #C82B96, #00D9FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    /* Links unificados */
    .sidebar-link {{
        display: block;
        padding: 10px 16px;
        margin: 6px 0;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.02), transparent);
        border-left: 3px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8 !important;
        text-decoration: none !important;
        font-size: 0.9rem;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }}
    .sidebar-link:hover {{
        background: linear-gradient(90deg, rgba(200, 43, 150, 0.15), transparent);
        border-left-color: #C82B96;
        color: #fff !important;
        padding-left: 20px;
        text-shadow: 0 0 10px rgba(200, 43, 150, 0.5);
    }}
</style>
""", unsafe_allow_html=True)

# ==================================================================================
# NAVEGACIÓN SIDEBAR - MISMA LÓGICA, AHORA VISUALMENTE BRUTAL
# ==================================================================================

# Inyectar estilos CSS personalizados (incluyendo estilos de tablas)
inject_custom_css()

# Función para cambiar de modulo desde este archivo
def open_module_from_indicadores(module_name):
    full_path = os.path.abspath(module_name)
    st.session_state['launch_module_path'] = full_path
    st.session_state['launch_module_name'] = os.path.splitext(os.path.basename(full_path))[0]
    st.session_state['launch_module_resolved_filename'] = os.path.basename(module_name)
    st.rerun()

# ===== HEADER DEL SIDEBAR - UNIFICADO =====
st.sidebar.markdown(f"""
<div style="text-align:center; padding:2rem 0 1rem 0;">
    <div style="font-family:'Orbitron', monospace; font-weight:900; font-size:1.6rem; 
                background: linear-gradient(135deg, #FF00FF 0%, #00D9FF 100%); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent;
                letter-spacing:3px; margin-bottom:5px;
                filter: drop-shadow(0 0 15px rgba(200, 43, 150, 0.4));">
        FRONTERA
    </div>
    <div style="font-family:'Rajdhani', sans-serif; font-size:0.8rem; 
                color:#94A3B8; letter-spacing:4px; font-weight:600; text-transform:uppercase; opacity:0.8;">
        ALS SYSTEM v1.3
    </div>
</div>
""", unsafe_allow_html=True)


# ===== NAVEGACIÓN PRINCIPAL =====
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

# ===== BOTÓN DE CERRAR SESIÓN =====
if st.sidebar.button("🚪 CERRAR SESIÓN", key="ind_btn_logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state['hide_main_menu_only'] = False
    st.rerun()



st.sidebar.divider()

# ===== METADATA =====
st.sidebar.markdown("""
<div class='sidebar-metadata'>
    <p>Módulo de Indicadores <strong>v1.2</strong></p>
    <p>Desarrollado por <strong>AJM</strong></p>
    <p style='font-size:0.7rem; opacity:0.6; margin-top:0.5rem;'>Frontera Energy © 2026</p>
</div>
""", unsafe_allow_html=True)


# Resumen público deshabilitado: botón y ejecución remotos eliminados.
# Si necesita reactivar esta funcionalidad, vuelva a añadir un botón que establezca
# una flag en `st.session_state` y que el flujo de importación/ejecución invoque
# `resumen_publico.show_resumen()`.


# Apartado compacto para carga de archivos y parámetros
# Expander principal para la sección de carga
# Se expande si NO hay datos calculados, se contrae si YA los hay.
expander_state = not st.session_state.get('df_bd_calculated') is not None
with st.expander("📂 Carga de Archivos y Parámetros", expanded=expander_state):
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
            fname = cached_onedrive_download(url_forma9, 'forma9_online.xlsx')
            if fname:
                forma9_online_file = fname
                show_success_box("F9 online descargada OK (Caché).")
            else:
                st.error("F9 online error: No se pudo descargar el archivo desde OneDrive.")

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
            fname = cached_onedrive_download(url_bd, 'bd_online.xlsx')
            if fname:
                bd_online_file = fname
                show_success_box("BD online descargada OK (Caché).")
            else:
                st.error("BD online error: No se pudo descargar el archivo desde OneDrive.")

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
                        df_forma9_calculated, df_bd_calculated = perform_initial_calculations(df_forma9_raw, df_bd_raw, fecha_evaluacion)
                        df_trabajo, reporte_fallas = calcular_indicadores_finales(df_forma9_calculated, df_bd_calculated)
                        reporte_runes_final, historico_run_life, verificaciones = generar_reporte_completo(df_bd_calculated, df_forma9_calculated, fecha_evaluacion)

                        # Guardar en session_state para uso posterior en la UI
                        st.session_state['df_forma9_raw'] = df_forma9_raw
                        st.session_state['df_bd_raw'] = df_bd_raw
                        # --- GUARDAR EN CACHÉ PARA PRÓXIMAS SESIONES ---
                        save_cached_data(
                            df_bd_calculated, 
                            df_forma9_calculated, 
                            fecha_evaluacion,
                            reporte_runes_final,
                            historico_run_life,
                            reporte_fallas
                        )
                        st.toast("Datos guardados en caché para carga rápida", icon="💾")
                        
                        st.session_state['df_bd_calculated'] = df_bd_calculated
                        st.session_state['df_forma9_calculated'] = df_forma9_calculated
                        st.session_state['fecha_evaluacion_state'] = fecha_evaluacion # Actualizar session state
                        st.session_state['reporte_runes'] = reporte_runes_final
                        st.session_state['historico_run_life'] = historico_run_life
                        st.session_state['reporte_fallas'] = reporte_fallas
                        st.session_state['df_trabajo'] = df_trabajo
                        st.session_state['verificaciones'] = verificaciones

                        # Listas únicas para filtros
                        st.session_state['unique_als'] = sorted(df_bd_calculated['ALS'].dropna().unique().tolist()) if 'ALS' in df_bd_calculated.columns else []
                        st.session_state['unique_activos'] = sorted(df_bd_calculated['ACTIVO'].dropna().unique().tolist()) if 'ACTIVO' in df_bd_calculated.columns else []

                        show_success_box("Cálculos finalizados correctamente.")
                except Exception as e:
                    st.error(f"Error durante el procesamiento: {e}")



if st.session_state['reporte_runes'] is not None:
    st.markdown("---")
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

    # Los filtros se renderizan con el estilo HUD inyectado globalmente

    # Se eliminaron las tarjetas visuales superiores para mostrar sólo los filtros en la sidebar.

    # --- Barra de filtros fijada en la sidebar (usa los mismos keys    # --- FILTROS GLOBALES EN SIDEBAR ---
    with st.sidebar:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(0, 242, 255, 0.1), rgba(255, 0, 255, 0.05));
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(0, 242, 255, 0.2);
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        ">
            <div style="font-size: 2rem; margin-bottom: 10px;">🛡️</div>
            <div style="font-family: 'Outfit', sans-serif; font-weight: 900; color: #fff; letter-spacing: 2px; font-size: 0.9rem;">
                CONTROL DE COMANDO
            </div>
            <div style="font-family: 'Inter', sans-serif; font-size: 0.6rem; color: #00f2ff; opacity: 0.8; margin-top: 5px; text-transform: uppercase;">
                System Ready • Filter Mode Active
            </div>
        </div>
        <div style="height: 1px; background: linear-gradient(90deg, transparent, rgba(0,242,255,0.3), transparent); margin-bottom: 20px;"></div>
        """, unsafe_allow_html=True)

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

        nick_options = _unique_options('NICK')
        nick_options = _ensure(nick_options, 'general_nick_filter')

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

        _select_with_index("🌐 Filtrar por Activo", activo_options, 'general_activo_filter')
        st.markdown('<div style="margin-top:-15px; margin-bottom:10px; height:1px; background:rgba(0,242,255,0.05);"></div>', unsafe_allow_html=True)
        
        _select_with_index("🎲 Filtrar por Bloque", bloque_options, 'general_bloque_filter')
        st.markdown('<div style="margin-top:-15px; margin-bottom:10px; height:1px; background:rgba(0,242,255,0.05);"></div>', unsafe_allow_html=True)
        
        _select_with_index("🎴 Filtrar por Campo", campo_options, 'general_campo_filter')
        st.markdown('<div style="margin-top:-15px; margin-bottom:10px; height:1px; background:rgba(0,242,255,0.05);"></div>', unsafe_allow_html=True)
        
        _select_with_index("🔧 Filtrar por ALS", als_options, 'general_als_filter')
        st.markdown('<div style="margin-top:-15px; margin-bottom:10px; height:1px; background:rgba(0,242,255,0.05);"></div>', unsafe_allow_html=True)
        
        _select_with_index("🏭 Filtrar por Proveedor", proveedor_options, 'general_proveedor_filter')

        st.markdown('<div style="margin-top:-15px; margin-bottom:10px; height:1px; background:rgba(0,242,255,0.05);"></div>', unsafe_allow_html=True)

        _select_with_index("🆔 Filtrar por Nick", nick_options, 'general_nick_filter')
        st.write("") # Espacio final

    # Los valores seleccionados en los filtros se leen desde session_state (sidebar) y
    # se usan directamente para aplicar los filtros más abajo. No se muestran tarjetas
    # ni controles redundantes en el tablero principal para mantener la UI limpia.
    selected_activo = st.session_state.get('general_activo_filter', 'TODOS')
    selected_bloque = st.session_state.get('general_bloque_filter', 'TODOS')
    selected_campo = st.session_state.get('general_campo_filter', 'TODOS')
    selected_als = st.session_state.get('general_als_filter', 'TODOS')
    selected_proveedor = st.session_state.get('general_proveedor_filter', 'TODOS')

    selected_nick = st.session_state.get('general_nick_filter', 'TODOS')

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

    if selected_nick != 'TODOS' and 'NICK' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['NICK'] == selected_nick]
    pozos_in_filtered_bd = df_bd_filtered['POZO'].unique()
    df_forma9_filtered = df_forma9_filtered[df_forma9_filtered['POZO'].isin(pozos_in_filtered_bd)]

    # --- Sección de Reporte de RUNES ---
    # --- Sección de Reporte de RUNES ---
    inject_custom_css()
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(200, 43, 150, 0.1), transparent); padding: 10px; border-left: 5px solid {COLOR_PRINCIPAL}; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
        <h3 id="reporte-de-runes" style='font-size:1.6rem; font-weight:800; margin:0; color:{COLOR_PRINCIPAL}; letter-spacing: -0.5px;'>
             REPORTE DE CORRIDAS (RUNES)
        </h3>
    </div>
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

    # === NUEVO LAYOUT REORGANIZADO ===
    # Fila 1: KPIs al 100% del ancho (centrado)
    # Crear un contenedor centrado para los KPIs
    kpi_container = st.container()
    with kpi_container:
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

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Fila 2: Gráficos lado a lado (50% grafico.py | 50% grafico_run_life.py)
    col_grafico, col_run_life = st.columns(2)

    # Columna izquierda (50%): grafico.py con sus 2 subgráficos
    with col_grafico:
        try:
            from grafico import generar_grafico_resumen, render_premium_echarts
            
            # Gráfico principal de grafico.py
            fig_final, df_monthly = generar_grafico_resumen(
                df_bd_filtered, df_forma9_filtered, fecha_evaluacion, 
                titulo=f"Gráfico Resumen Anual - {selected_activo}"
            )
            if df_monthly is not None and not df_monthly.empty:
                render_premium_echarts(df_monthly, titulo=f"Resumen Performance: {selected_activo}")
            elif fig_final is not None:
                st.plotly_chart(fig_final, use_container_width=True)
        except Exception as e:
            st.warning(f"No se pudo generar el gráfico resumen premium: {e}")

    # Columna derecha (50%): grafico_run_life.py con sus 2 subgráficos HORIZONTALES
    with col_run_life:
        try:
            from grafico_run_life import generar_grafico_run_life, generar_grafico_pozos_indices, render_premium_echarts_run_life, render_premium_echarts_pozos
            
            # Crear sub-columnas horizontales (25% cada una del total)
            sub_col1, sub_col2 = st.columns(2)
            
            with sub_col1:
                # Subgráfico 1 de run_life (25% del total)
                fig_rl, df_rl = generar_grafico_run_life(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
                if df_rl is not None and not df_rl.empty:
                    render_premium_echarts_run_life(df_rl, titulo="T. VIDA & TMEF")
                elif fig_rl:
                    st.plotly_chart(fig_rl, use_container_width=True)

            with sub_col2:
                # Subgráfico 2 de run_life (25% del total)
                fig_pi, df_pi = generar_grafico_pozos_indices(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
                if df_pi is not None and not df_pi.empty:
                    render_premium_echarts_pozos(df_pi, titulo="POZOS & ÍNDICES")
                elif fig_pi:
                    st.plotly_chart(fig_pi, use_container_width=True)
                    
        except Exception as e:
            st.warning(f"Error en gráficos especializados premium: {e}")


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

    # Los KPIs magenta/azul se omitieron o se movieron a mostrar_kpis()
    # No es necesario cerrar este div si no se abrió.

    
    # --- LAYOUT COMPACTO CON TABS ---
    st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] { gap: 4px; }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            background-color: rgba(255,255,255,0.03);
            border-radius: 5px 5px 0 0;
            padding: 0 16px;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 600;
            font-size: 14px;
            border: 1px solid rgba(255,255,255,0.05);
            border-bottom: none;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(180deg, rgba(200, 43, 150, 0.1), rgba(200, 43, 150, 0.02));
            border-top: 2px solid #C82B96;
            color: #fff !important;
        }
        .compact-header { 
            font-size: 1.1rem !important; 
            margin-bottom: 10px !important; 
            padding: 8px 12px !important;
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
            border-left: 3px solid #C82B96;
        }
    </style>
    """, unsafe_allow_html=True)

    tab_resumen, tab_performance, tab_fallas, tab_indices = st.tabs(["📊 RESUMEN", "⚡ PERFORMANCE", "🚨 FALLAS", "📈 ÍNDICES & DATA"])

    with tab_resumen:
        
        # Ahora sí, dividir en columnas para tablas y gráficas
        col_table, col_chart = st.columns([0.4, 0.6])
    
        with col_table:
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {COLOR_PRINCIPAL}11, transparent); padding: 8px; border-left: 4px solid {COLOR_PRINCIPAL}; border-radius: 4px; margin-bottom: 12px;">
                <h5 style='margin:0; color:{COLOR_PRINCIPAL}; font-weight:800; font-size:1.1rem;'>
                     🔢 RESUMEN DE CORRIDAS
                </h5>
            </div>
            """, unsafe_allow_html=True)
            
            # Sanitizar DataFrame para evitar errores de PyArrow (tipos mixtos)
            if reporte_runes_filtered is not None:
                for col_safe in ['CLUSTER', 'POZO', 'RUN', 'ALS', 'Categoría']:
                    if col_safe in reporte_runes_filtered.columns:
                        reporte_runes_filtered[col_safe] = reporte_runes_filtered[col_safe].astype(str)
            
            st.dataframe(reporte_runes_filtered, hide_index=True, use_container_width=True, height=350)
            
          
    
            
        with col_chart:
            # Gráfico ECharts Premium: Conteo de RUNES
            if reporte_runes_filtered is not None and not reporte_runes_filtered.empty:
                categories = reporte_runes_filtered['Categoría'].tolist()
                counts = reporte_runes_filtered['Conteo'].tolist()
                color_seq = get_color_sequence()
                
                echarts_options = {
                    "backgroundColor": "transparent",
                    "title": {
                        "text": f"RUNS POR CATEGORÍA ({selected_activo})",
                        "left": "center",
                        "textStyle": {"color": "#fff", "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
                    },
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "top": "15%", "containLabel": True},
                    "xAxis": [{"type": "value", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                    "yAxis": [{"type": "category", "data": categories, "axisLabel": {"color": "#fff", "fontSize": 11}}],
                    "series": [{
                        "name": "Cantidad",
                        "type": "bar",
                        "data": counts,
                        "itemStyle": {
                            "color": {
                                "type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
                                "colorStops": [{"offset": 0, "color": COLOR_PRINCIPAL}, {"offset": 1, "color": "#00f2ff"}]
                            },
                            "borderRadius": [0, 10, 10, 0]
                        },
                        "label": {"show": True, "position": "right", "color": "#fff", "fontWeight": "bold"}
                    }]
                }
                
                html_content = f"""
                <div id="echarts-runes" style="width:100%; height:320px;"></div>
                <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                <script>
                    (function() {{
                        var myChart = echarts.init(document.getElementById('echarts-runes'), 'dark');
                        myChart.setOption({json.dumps(echarts_options)});
                        window.addEventListener('resize', function() {{ myChart.resize(); }});
                    }})();
                </script>
                """
                components.html(html_content, height=340)
            else:
                st.info("No hay datos para mostrar en el conteo de RUNES.")
    
        # --- NUEVA SECCIÓN: ESTADO DE LA CAMPAÑA ---
        # Asegurar que fecha_evaluacion sea Timestamp para comparar con columnas datetime64
        fecha_eval_ts = pd.to_datetime(fecha_evaluacion)
        anio_campana = fecha_eval_ts.year
    
        # Contenedor visual Cabecera Premium
        st.markdown(f"""
<div style="background: linear-gradient(90deg, rgba(0, 242, 255, 0.1), transparent); padding: 12px 20px; border-left: 5px solid #00f2ff; border-radius: 8px; margin: 1.5em 0; box-shadow: -10px 0 20px rgba(0, 242, 255, 0.1); display: flex; align-items: center; gap: 15px;">
<div style="width: 10px; height: 10px; background: #00f2ff; border-radius: 50%; box-shadow: 0 0 10px #00f2ff; animation: pulse 2s infinite;"></div>
<h4 style='font-size:1.2rem; font-weight:900; margin:0; color:#fff; letter-spacing: 3px; text-transform: uppercase; font-family: "Outfit", sans-serif;'>ESTADO DE LA CAMPAÑA <span style="color:#00f2ff;">{anio_campana}</span></h4>
<style> @keyframes pulse {{ 0% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.4; }} }} </style>
</div>
""", unsafe_allow_html=True)
        
        # 1. Filtrar BD para el año de campaña (FECHA_RUN en el año evaluado)
        df_campana = df_bd_filtered[df_bd_filtered['FECHA_RUN'].dt.year == anio_campana].copy()
        
        if df_campana.empty:
            st.info(f"No hay registros de Runs iniciados en el año {anio_campana}.")
        else:
            # 2. Dividir en Pozos Nuevos (RUN=1) e Intervenciones/Trabajos (RUN>1)
            # Asegurar que RUN sea numérico
            df_campana['RUN'] = pd.to_numeric(df_campana['RUN'], errors='coerce').fillna(0)
            
            df_nuevos = df_campana[df_campana['RUN'] == 1].copy()
            df_intervenciones = df_campana[df_campana['RUN'] > 1].copy()
            
            def calcular_metricas_grupo(df_grupo, nombre_grupo, color_borde):
                if df_grupo.empty:
                    return f"""<div style="flex:1; background:rgba(255,255,255,0.02); border:1px solid {color_borde}44; border-radius:12px; padding:20px; text-align:center; opacity:0.6;">
<div style="color:{color_borde}; font-weight:bold; letter-spacing:1px;">{nombre_grupo.upper()}</div>
<div style="font-size:0.8rem; margin-top:5px; color:#888;">SIN REGISTROS ACTIVOS</div>
</div>"""
                
                # Métricas
                total_pozos = df_grupo['POZO'].nunique()
                fallados = df_grupo[df_grupo['FECHA_FALLA'].notna() & (df_grupo['FECHA_FALLA'] <= fecha_eval_ts)]['POZO'].nunique()
                operativos = df_grupo[
                    ((df_grupo['FECHA_PULL'].isna()) | (df_grupo['FECHA_PULL'] > fecha_eval_ts)) &
                    ((df_grupo['FECHA_FALLA'].isna()) | (df_grupo['FECHA_FALLA'] > fecha_eval_ts))
                ]['POZO'].nunique()
                
                pozos_grupo = df_grupo['POZO'].unique()
                df_f9_grupo = df_forma9_filtered[df_forma9_filtered['POZO'].isin(pozos_grupo)].copy()
                
                produccion_total = 0.0
                if not df_f9_grupo.empty:
                    df_last_prod = df_f9_grupo.sort_values('FECHA_FORMA9').groupby('POZO').last()
                    col_bopd = next((c for c in df_last_prod.columns if 'BOPD' in str(c).upper()), None)
                    if col_bopd:
                        produccion_total = pd.to_numeric(df_last_prod[col_bopd], errors='coerce').sum()
                    
                return f"""
<div style="flex:1; background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(2, 6, 23, 1)); border: 1px solid {color_borde}44; border-radius: 20px; padding: 22px; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); min-width: 300px;">
<div style="position:absolute; top:0; right:0; width:80px; height:80px; background:radial-gradient(circle at 100% 0%, {color_borde}33, transparent 70%);"></div>
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px;">
<div>
<div style="color:{color_borde}; font-weight:900; font-size:1.1rem; letter-spacing:1px; font-family:'Outfit';">{nombre_grupo.upper()}</div>
<div style="font-size:0.7rem; color:#64748b; font-weight:bold; margin-top:2px;">OPERACIÓN TÁCTICA</div>
</div>
<div style="text-align:right;">
<div style="font-size:1.6rem; font-weight:900; color:#fff; line-height:1;">{total_pozos}</div>
<div style="font-size:0.6rem; color:{color_borde}; font-weight:bold; letter-spacing:1px;">CORRIDAS</div>
</div>
</div>
<div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.05);">
<div style="text-align:center;">
<div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px; font-weight:bold;">ACTIVOS</div>
<div style="font-size:1.3rem; font-weight:900; color:#00ff9d;">{operativos}</div>
</div>
<div style="text-align:center; border-left:1px solid rgba(255,255,255,0.1); border-right:1px solid rgba(255,255,255,0.1);">
<div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px; font-weight:bold;">FALLADOS</div>
<div style="font-size:1.3rem; font-weight:900; color:#ff3e3e;">{fallados}</div>
</div>
<div style="text-align:center;">
<div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px; font-weight:bold;">BOPD</div>
<div style="font-size:1.3rem; font-weight:900; color:#00f2ff;">{produccion_total:,.0f}</div>
</div>
</div>
<div style="margin-top:15px; height:4px; background:rgba(255,255,255,0.05); border-radius:2px; overflow:hidden;">
<div style="width:{(operativos/total_pozos*100) if total_pozos>0 else 0}%; height:100%; background:linear-gradient(90deg, {color_borde}, #fff); box-shadow:0 0 10px {color_borde};"></div>
</div>
</div>
"""
    
            html_nuevos = calcular_metricas_grupo(df_nuevos, "Pozos Nuevos", "#00cfff") # Cian
            html_interv = calcular_metricas_grupo(df_intervenciones, "Workover / Servicios", "#ff00ff") # Magenta
            
            st.markdown(f"""<div style="display:flex; gap:15px; flex-wrap:wrap; margin-bottom:15px;">
    {html_nuevos}
    {html_interv}
    </div>""", unsafe_allow_html=True)
            
            # Opcional: Tabla detalle colapsable
            with st.expander(f"📋 Ver detalle de Pozos Campaña {anio_campana}"):
                 c1, c2 = st.columns(2)
                 with c1:
                     st.markdown("##### Pozos Nuevos")
                     if not df_nuevos.empty:
                         st.dataframe(df_nuevos[['POZO', 'RUN', 'FECHA_RUN', 'FECHA_FALLA', 'ACTIVO']].reset_index(drop=True), use_container_width=True)
                     else:
                         st.info("Sin pozos nuevos.")
                 with c2: 
                     st.markdown("##### Intervenciones")
                     if not df_intervenciones.empty:
                         st.dataframe(df_intervenciones[['POZO', 'RUN', 'FECHA_RUN', 'FECHA_FALLA', 'ACTIVO']].reset_index(drop=True), use_container_width=True)
                     else:
                         st.info("Sin intervenciones.")
    with tab_performance:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(0, 207, 255, 0.1), transparent); padding: 10px; border-left: 5px solid #00cfff; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
            <h4 style='font-size:1.3rem; font-weight:800; margin:0; color:#00cfff;'>
                PRODUCCIÓN (BOPD) vs TIEMPO DE VIDA
            </h4>
        </div>
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
                # Mostrar en columnas: Tabla pequeña a la izquierda, Gráfico a la derecha
                col_bopd_table, col_bopd_chart = st.columns([0.50, 0.50])

                with col_bopd_table:
                    st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
                    st.markdown('##### 📋 Detalle por Rango')
                    
                    # Preparar datos para descarga en Excel
                    df_export_bopd = agg.copy()
                    df_export_bopd.rename(columns={
                        'RunLifeBucket': 'Rango de Tiempo de Vida',
                        'BOPD_sum': 'Producción Total (BOPD)',
                        'Pozos': 'Cantidad de Pozos'
                    }, inplace=True)
                    
                    # Crear botón de descarga
                    from io import BytesIO
                    output_bopd = BytesIO()
                    with pd.ExcelWriter(output_bopd, engine='openpyxl') as writer:
                        df_export_bopd.to_excel(writer, index=False, sheet_name='BOPD vs Tiempo de Vida')
                        # Agregar también los datos detallados por pozo
                        if not merged.empty:
                            merged_export = merged[['POZO', 'BOPD', 'RUN LIFE', 'RunLifeBucket']].copy()
                            merged_export.rename(columns={
                                'POZO': 'Pozo',
                                'BOPD': 'Producción (BOPD)',
                                'RUN LIFE': 'Tiempo de Vida (días)',
                                'RunLifeBucket': 'Rango de Tiempo de Vida'
                            }, inplace=True)
                            merged_export.to_excel(writer, index=False, sheet_name='Detalle por Pozo')
                    excel_data_bopd = output_bopd.getvalue()
                    
                    st.download_button(
                        label="📥 Descargar datos en Excel",
                        data=excel_data_bopd,
                        file_name="produccion_bopd_vs_tiempo_vida.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_bopd_excel"
                    )
                    
                    st.dataframe(
                        agg.rename(columns={'RunLifeBucket': 'Rango', 'BOPD_sum': 'BOPD', 'Pozos': '# Pozos'}), 
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "BOPD": st.column_config.NumberColumn(format="%.1f"),
                        }
                    )

                with col_bopd_chart:
                    # Definir mapa de colores coherente (Gradiente Azul-Cian)
                    # <2y (Nuevo/Cyan), 2-4y (Azul Medio), 4-6y (Azul Oscuro), >6y (Magenta/Acento para destacar longevidad)
                    color_map = {
                        '<2 años': '#00efff',   # Cyan brillante
                        '2-4 años': '#00a3ff',  # Azul claro
                        '4-6 años': '#0055ff',  # Azul medio
                        '>6 años': '#ff00ff'    # Magenta (destacar lo 'raro' y bueno)
                    }
                    
                    # Gráfico ECharts Premium: BOPD vs Tiempo de Vida
                    buckets = agg['RunLifeBucket'].tolist()
                    bopd_values = agg['BOPD_sum'].tolist()
                    pozos_values = agg['Pozos'].tolist()

                    # Definir colors_list basado en el color_map
                    colors_list = [color_map.get(b, '#cccccc') for b in buckets]
                    
                    # Crear datos estructurados con colores individuales y gradientes
                    echarts_data = []
                    for i, val in enumerate(bopd_values):
                        base_color = colors_list[i]
                        echarts_data.append({
                            "value": val,
                            "itemStyle": {
                                "color": {
                                    "type": "linear",
                                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                                    "colorStops": [
                                        {"offset": 0, "color": base_color},
                                        {"offset": 1, "color": f"{base_color}66"}  # Transparencia al final
                                    ]
                                },
                                "borderRadius": [10, 10, 0, 0],
                                "shadowBlur": 10,
                                "shadowColor": f"{base_color}88"
                            }
                        })

                    echarts_options_bopd = {
                        "backgroundColor": "transparent",
                        "title": {
                            "text": "PRODUCCIÓN vs TIEMPO DE VIDA",
                            "left": "center",
                            "top": 5,
                            "textStyle": {
                                "color": "#00cfff",
                                "fontSize": 14,
                                "fontFamily": "Outfit, sans-serif",
                                "fontWeight": "900"
                            }
                        },
                        "tooltip": {
                            "trigger": "axis",
                            "axisPointer": {"type": "shadow"},
                            "backgroundColor": "rgba(6, 10, 30, 0.95)",
                            "borderColor": "#00cfff",
                            "borderWidth": 2,
                            "textStyle": {"color": "#fff", "fontSize": 12},
                            "formatter": "function(params) { var pozos = " + json.dumps(pozos_values) + "; return '<b style=\"color:#00cfff\">Rango:</b> ' + params[0].name + '<br/><b style=\"color:#00ff9f\">BOPD:</b> ' + params[0].value.toFixed(1) + '<br/><b style=\"color:#ffab40\">Pozos:</b> ' + pozos[params[0].dataIndex] + ' Pzs'; }"
                        },
                        "grid": {"left": "15", "right": "15", "bottom": "15", "top": "50", "containLabel": True},
                        "xAxis": {
                            "type": "category",
                            "data": buckets,
                            "axisLabel": {
                                "color": "#fff", 
                                "fontSize": 11,
                                "fontWeight": "bold"
                            },
                            "axisLine": {"lineStyle": {"color": "rgba(0, 207, 255, 0.3)", "width": 2}},
                            "axisTick": {"show": False}
                        },
                        "yAxis": {
                            "type": "value",
                            "name": "BOPD",
                            "nameTextStyle": {
                                "color": "#00cfff",
                                "fontSize": 12,
                                "fontWeight": "bold"
                            },
                            "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}},
                            "axisLabel": {"color": "#888", "fontSize": 10},
                            "axisLine": {"lineStyle": {"color": "rgba(0, 207, 255, 0.3)", "width": 2}}
                        },
                        "series": [
                            {
                                "data": echarts_data,
                                "type": "bar",
                                "barWidth": "60%",
                                "label": {
                                    "show": True,
                                    "position": "top",
                                    "color": "#fff",
                                    "fontSize": 11,
                                    "fontWeight": "bold",
                                    "formatter": "function(params) { var pozos = " + json.dumps(pozos_values) + "; var bopd = " + json.dumps(bopd_values) + "; return bopd[params.dataIndex].toFixed(0) + ' BOPD\\n' + pozos[params.dataIndex] + ' Pzs'; }"
                                }
                            }
                        ]
                    }
                    
                    # Reemplazar placeholders de funciones
                    js_options = json.dumps(echarts_options_bopd)
                    # Formatter del label
                    js_options = js_options.replace(
                        '"function(params) { var pozos = ' + json.dumps(pozos_values) + '; var bopd = ' + json.dumps(bopd_values) + '; return bopd[params.dataIndex].toFixed(0) + \' BOPD\\\\n\' + pozos[params.dataIndex] + \' Pzs\'; }"',
                        f"function(params) {{ var pozos = {json.dumps(pozos_values)}; var bopd = {json.dumps(bopd_values)}; return bopd[params.dataIndex].toFixed(0) + ' BOPD\\n' + pozos[params.dataIndex] + ' Pzs'; }}"
                    )
                    # Formatter del tooltip
                    js_options = js_options.replace(
                        '"function(params) { var pozos = ' + json.dumps(pozos_values) + '; return \'<b style=\\\"color:#00cfff\\\">Rango:</b> \' + params[0].name + \'<br/><b style=\\\"color:#00ff9f\\\">BOPD:</b> \' + params[0].value.toFixed(1) + \'<br/><b style=\\\"color:#ffab40\\\">Pozos:</b> \' + pozos[params[0].dataIndex] + \' Pzs\'; }"',
                        f"function(params) {{ var pozos = {json.dumps(pozos_values)}; return '<b style=\"color:#00cfff\">Rango:</b> ' + params[0].name + '<br/><b style=\"color:#00ff9f\">BOPD:</b> ' + params[0].value.toFixed(1) + '<br/><b style=\"color:#ffab40\">Pozos:</b> ' + pozos[params[0].dataIndex] + ' Pzs'; }}"
                    )

                    html_bopd = f"""
                    <div id="echarts-bopd" style="width:100%; height:360px; background: linear-gradient(135deg, rgba(0, 207, 255, 0.05), rgba(0, 15, 30, 0.1)); border-radius: 15px; padding: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);"></div>
                    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                    <script>
                        (function() {{
                            var myChart = echarts.init(document.getElementById('echarts-bopd'), 'dark');
                            myChart.setOption({js_options});
                            window.addEventListener('resize', function() {{ myChart.resize(); }});
                        }})();
                    </script>
                    """
                    components.html(html_bopd, height=380)
        else:
            st.info('No hay datos de RUN o de FORMA9 disponibles para el filtro actual.')

        with st.expander("Verificaciones de Consistencia", expanded=False):
            for relacion, es_valida in verificaciones_filtered.items():
                status = "✅ Válida" if es_valida else "❌ No válida"
                text_color = COLOR_FUENTE if COLOR_FONDO_OSCURO else 'inherit'
                st.markdown(f"<span style='font-size:11px; color:{text_color};'>{relacion}: {status}</span>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(255, 222, 49, 0.1), transparent); padding: 10px; border-left: 5px solid #FFDE31; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
            <h3 id="historico-de-run-life-por-campo" style='font-size:1.3rem; font-weight:800; margin:0; color:#FFDE31; letter-spacing: -0.5px;'>
                 HISTÓRICO TIEMPO DE VIDA POR CAMPO
            </h3>
        </div>
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
        runlife_total_val = float(runlife_total) if not pd.isna(runlife_total) else 0.0
        
        # Calcular Run Life Efectivo (usando función importada)
        try:
            run_life_efectivo_val, _ = calcular_run_life_efectivo(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
        except Exception:
            run_life_efectivo_val = 0.0

        st.markdown(f"""
        <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 20px;">
            <div style="flex: 1; padding: 20px; background: linear-gradient(135deg, {tema.COLOR_GRADIENTE_MAGENTA_1}, {tema.COLOR_GRADIENTE_MAGENTA_2}); border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; color: white;">
                <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">TIEMPO VIDA TOTAL ({'TODOS' if activo_runlife == 'TODOS' else activo_runlife})</div>
                <div style="font-size: 36px; font-weight: 800; margin-top: 10px;">{runlife_total_val:.2f} <span style="font-size: 16px; font-weight: 400;">días</span></div>
            </div>
            <div style="flex: 1; padding: 20px; background: linear-gradient(135deg, {tema.COLOR_GRADIENTE_AZUL_1}, {tema.COLOR_GRADIENTE_AZUL_2}); border-radius: 15px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); text-align: center; color: #E0E0E0;">
                <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">RUN LIFE EFECTIVO ({'TODOS' if activo_runlife == 'TODOS' else activo_runlife})</div>
                <div style="font-size: 36px; font-weight: 800; margin-top: 10px;">{run_life_efectivo_val:.2f} <span style="font-size: 16px; font-weight: 400;">días</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Generar histórico por campo

        # Usar siempre la función corregida para el histórico de run life promedio mensual
        historico_run_life = generar_historico_run_life(df_bd_filtered, fecha_evaluacion)

        with col_table_runlife:
            if historico_run_life is not None:
                st.dataframe(historico_run_life, hide_index=True)

        with col_chart_runlife:
            if historico_run_life is not None and 'ACTIVO' in historico_run_life.columns:
                # Gráfico ECharts Premium: Histórico Tiempo de Vida
                # Convertir meses a string corto YYYY-MM-DD para consistencia
                historico_run_life['Mes_Str'] = pd.to_datetime(historico_run_life['Mes'], errors='coerce').dt.strftime('%Y-%m-%d')
                months = sorted(historico_run_life['Mes_Str'].unique().tolist())
                activos = sorted(historico_run_life['ACTIVO'].unique().tolist())
                color_seq = get_color_sequence()
                
                series = []
                for i, act in enumerate(activos):
                    df_act = historico_run_life[historico_run_life['ACTIVO'] == act]
                    # Mapear valores a los meses correspondientes (llenar con 0 si falta)
                    data_act = []
                    # Asegurar orden cronológico de meses
                    for m in months:
                        val = df_act[df_act['Mes_Str'] == m]['Tiempo Op. Promedio'].values
                        data_act.append(float(val[0]) if len(val) > 0 else 0)
                    
                    series.append({
                        "name": act,
                        "type": "bar",
                        "data": data_act,
                        "itemStyle": {"borderRadius": [4, 4, 0, 0]}
                    })

                echarts_options_hist = {
                    "backgroundColor": "transparent",
                    "title": {
                        "text": "TIEMPO DE VIDA PROMEDIO MENSUAL POR ACTIVO",
                        "left": "center",
                        "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
                    },
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {"data": activos, "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 10}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                    "xAxis": [{"type": "category", "data": months, "axisLabel": {"color": "#888", "fontSize": 10}}],
                    "yAxis": [{"type": "value", "name": "Días", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                    "color": color_seq,
                    "series": series
                }
                
                html_hist = f"""
                <div id="echarts-hist" style="width:100%; height:320px;"></div>
                <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                <script>
                    (function() {{
                        var myChart = echarts.init(document.getElementById('echarts-hist'), 'dark');
                        myChart.setOption({json.dumps(echarts_options_hist)});
                        window.addEventListener('resize', function() {{ myChart.resize(); }});
                    }})();
                </script>
                """
                components.html(html_hist, height=340)
            elif historico_run_life is not None:
                # Caso sin ACTIVO (general)
                # Convertir meses a string para JSON
                months = [str(m) for m in historico_run_life['Mes']]
                data = [float(x) for x in historico_run_life['Tiempo Op. Promedio'].tolist()]
                
                echarts_options_gen = {
                    "backgroundColor": "transparent",
                    "title": {
                        "text": "TIEMPO DE VIDA PROMEDIO MENSUAL",
                        "left": "center",
                        "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
                    },
                    "tooltip": {"trigger": "axis"},
                    "grid": {"left": "3%", "right": "4%", "bottom": "10%", "top": "15%", "containLabel": True},
                    "xAxis": [{"type": "category", "data": months, "axisLabel": {"color": "#888"}}],
                    "yAxis": [{"type": "value", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                    "series": [{
                        "type": "bar",
                        "data": data,
                        "itemStyle": {"color": COLOR_PRINCIPAL, "borderRadius": [8, 8, 0, 0]}
                    }]
                }
                html_gen = f"""
                <div id="echarts-gen" style="width:100%; height:320px;"></div>
                <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                <script>
                    (function() {{
                        var myChart = echarts.init(document.getElementById('echarts-gen'), 'dark');
                        myChart.setOption({json.dumps(echarts_options_gen)});
                        window.addEventListener('resize', function() {{ myChart.resize(); }});
                    }})();
                </script>
                """
                components.html(html_gen, height=340)

    with tab_fallas:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(245, 39, 56, 0.1), transparent); padding: 10px; border-left: 5px solid #F52738; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
            <h3 id="fallas-mensuales" style='font-size:1.3rem; font-weight:800; margin:0; color:#F52738; letter-spacing: -0.5px;'>
                 ANÁLISIS DE FALLAS MENSUALES
            </h3>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state['reporte_fallas'].empty:
            # Definir rango por defecto: Último año desde la fecha máxima de falla
            # Si el rango es menor a un año, se muestra completo.
            # Esto evita que se muestre todo el histórico por defecto.
            min_date_falla_data = st.session_state['reporte_fallas']['MES'].min().date()
            max_date_falla = st.session_state['reporte_fallas']['MES'].max().date()
            
            # Calcular fecha inicio por defecto (1 año atrás)
            try:
                default_start = max_date_falla.replace(year=max_date_falla.year - 1)
            except ValueError: # Caso año bisiesto si cae en 29 feb
                default_start = max_date_falla - timedelta(days=365)
                
            start_date_falla, end_date_falla = st.date_input(
                "Filtra por rango de fecha para las fallas:",
                [max(min_date_falla_data, default_start), max_date_falla],
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
                        'Tiempo Vida a Falla': run.get('RUN LIFE', ''),
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

                    df_graf['Clasif. Tiempo Vida'] = df_graf['Tiempo Vida a Falla'].apply(clasificar_runlife)
                    conteo = df_graf.groupby(['Clasif. Tiempo Vida', 'Clasificación IA']).size().reset_index(name='Cantidad')
                    
                    # Gráfico ECharts Premium: Distribución de Fallas
                    try:
                        tipos_ia = sorted(conteo['Clasificación IA'].unique().tolist())
                    except Exception:
                        tipos_ia = []
                        
                    orden_runlife = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía']
                    colores_runlife = {
                        'Infantil': tema.COLOR_RL_INFANTIL,
                        'Prematura': tema.COLOR_RL_PREMATURA,
                        'En Garantía': tema.COLOR_RL_EN_GARANTIA,
                        'Sin Garantía': tema.COLOR_RL_SIN_GARANTIA
                    }
                    
                    series_fallas = []
                    for rl in orden_runlife:
                        data_rl = []
                        for t in tipos_ia:
                            val = conteo[(conteo['Clasif. Tiempo Vida'] == rl) & (conteo['Clasificación IA'] == t)]['Cantidad'].values
                            data_rl.append(int(val[0]) if len(val) > 0 else 0)
                        
                        series_fallas.append({
                            "name": rl,
                            "type": "bar",
                            "stack": "Total",
                            "data": data_rl,
                            "itemStyle": {"color": colores_runlife.get(rl)}
                        })

                    echarts_options_fallas = {
                        "backgroundColor": "transparent",
                        "title": {
                            "text": "DISTRIBUCIÓN DE FALLAS POR TIEMPO Y TIPO",
                            "left": "center",
                            "textStyle": {"color": "#fff", "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
                        },
                        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                        "legend": {"data": orden_runlife, "bottom": 0, "textStyle": {"color": "#ccc"}},
                        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                        "xAxis": [{"type": "category", "data": tipos_ia, "axisLabel": {"color": "#888", "fontSize": 10, "rotate": 30}}],
                        "yAxis": [{"type": "value", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                        "series": series_fallas
                    }
                    
                    html_fallas = f"""
                    <div id="echarts-fallas-dist" style="width:100%; height:400px;"></div>
                    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                    <script>
                        (function() {{
                            var myChart = echarts.init(document.getElementById('echarts-fallas-dist'), 'dark');
                            myChart.setOption({json.dumps(echarts_options_fallas)});
                            window.addEventListener('resize', function() {{ myChart.resize(); }});
                        }})();
                    </script>
                    """
                    components.html(html_fallas, height=420)
                else:
                    st.info("Sin datos para graficar distribución.")

            col3, col4 = st.columns(2)
            with col3:
                if not df_detalles_fallas.empty:
                    df_graf = df_detalles_fallas.copy()
                    # Verifica que exista la columna antes de agrupar
                    if 'Clasificación IA' in df_graf.columns:
                        tipo_falla_counts = df_graf['Clasificación IA'].value_counts().reset_index()
                        tipo_falla_counts.columns = ['Tipo de Falla IA', 'Cantidad']
                        
                        pie_data = []
                        for _, row in tipo_falla_counts.iterrows():
                            pie_data.append({"name": row['Tipo de Falla IA'], "value": int(row['Cantidad'])})
                        
                        # Colores Premium para Fallas
                        FALLA_COLORS = ['#ff0055', '#00f2ff', '#00ff9d', '#ffbd00', '#C82B96', '#8b5cf6', '#0066ff', '#33ffcc']
                        
                        echarts_options_pie = {
                            "backgroundColor": "transparent",
                            "title": {
                                "text": "DISTRIBUCIÓN POR TIPO DE FALLA (IA)",
                                "left": "center",
                                "top": 10,
                                "textStyle": {
                                    "color": "#fff", 
                                    "fontSize": 16, 
                                    "fontFamily": "Outfit", 
                                    "fontWeight": "900",
                                    "letterSpacing": 1
                                }
                            },
                            "color": FALLA_COLORS,
                            "tooltip": {
                                "trigger": "item", 
                                "formatter": "{b}<br/><b>{c} Eventos</b> ({d}%)",
                                "backgroundColor": "rgba(6, 10, 30, 0.9)",
                                "borderColor": "#00f2ff",
                                "textStyle": {"color": "#fff"}
                            },
                            "legend": {
                                "orient": "horizontal",
                                "bottom": 0,
                                "textStyle": {"color": "#ccc", "fontSize": 10},
                                "itemGap": 10
                            },
                            "series": [
                                {
                                    "name": "Tipo de Falla",
                                    "type": "pie",
                                    "radius": ["20%", "75%"],
                                    "center": ["50%", "50%"],
                                    "roseType": "radius",
                                    "itemStyle": {
                                        "borderRadius": 8,
                                        "borderColor": "rgba(255,255,255,0.1)",
                                        "borderWidth": 2,
                                        "shadowBlur": 20,
                                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                                    },
                                    "label": {
                                        "show": True,
                                        "position": "outside",
                                        "color": "#fff",
                                        "fontSize": 10,
                                        "fontFamily": "Outfit",
                                        "formatter": "{b}\n{d}%"
                                    },
                                    "emphasis": {
                                        "itemStyle": {
                                            "shadowBlur": 30,
                                            "shadowOffsetX": 0,
                                            "shadowColor": "rgba(0, 242, 255, 0.5)"
                                        },
                                        "label": {
                                            "show": True,
                                            "fontSize": 12,
                                            "fontWeight": "bold"
                                        }
                                    },
                                    "data": pie_data
                                }
                            ]
                        }
                        
                        html_pie = f"""
                        <div id="chart-container-falla" style="position: relative; width:100%; height:420px; background: rgba(10, 15, 30, 0.4); border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05);">
                            <div id="echarts-fallas-pie" style="width:100%; height:100%;"></div>
                            <button id="zoom-btn-falla" style="
                                position: absolute; top: 10px; right: 10px; z-index: 1000; 
                                background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.3); 
                                color: #00f2ff; padding: 4px 10px; border-radius: 20px; 
                                cursor: pointer; font-size: 10px; font-family: 'Outfit', sans-serif;
                                font-weight: 700; text-transform: uppercase; backdrop-filter: blur(5px);
                                transition: all 0.3s;
                            ">⛶ Ver Más</button>
                        </div>
                        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                        <script>
                            (function() {{
                                var container = document.getElementById('chart-container-falla');
                                var chartDom = document.getElementById('echarts-fallas-pie');
                                var zoomBtn = document.getElementById('zoom-btn-falla');
                                var myChart = echarts.init(chartDom, 'dark');
                                
                                myChart.setOption({json.dumps(echarts_options_pie)});
                                
                                window.addEventListener('resize', function() {{ myChart.resize(); }});

                                zoomBtn.addEventListener('click', function() {{
                                    if (!document.fullscreenElement) {{
                                        container.requestFullscreen();
                                        container.style.height = '100vh';
                                        zoomBtn.innerHTML = '✕ Cerrar';
                                    }} else {{
                                        document.exitFullscreen();
                                        container.style.height = '420px';
                                        zoomBtn.innerHTML = '⛶ Ver Más';
                                    }}
                                }});
                                
                                document.addEventListener('fullscreenchange', function() {{
                                    if (!document.fullscreenElement) {{
                                        container.style.height = '420px';
                                        zoomBtn.innerHTML = '⛶ Ver Más';
                                    }}
                                    myChart.resize();
                                }});
                            }})();
                        </script>
                        """
                        components.html(html_pie, height=440)
                    else:
                        st.info("Sin clasificación IA disponible.")
            
            with col4:
                if not df_detalles_fallas.empty:
                    st.markdown("##### 🔥 Top Pozos con Más Fallas")
                    top_pozos = df_detalles_fallas['Pozo'].value_counts().reset_index()
                    top_pozos.columns = ['Pozo', 'N° Fallas']
                    st.dataframe(top_pozos.head(10), hide_index=True, use_container_width=True)
                else:
                    st.info("Sin datos para top pozos.")

        st.markdown("---")
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, rgba(161, 3, 157, 0.1), transparent); padding: 10px; border-left: 5px solid #A1039D; border-radius: 5px; margin-top: 2em; margin-bottom: 1em;">
            <h3 id="listado-de-pozos-fallados" style='font-size:1.3rem; font-weight:800; margin:0; color:#A1039D; letter-spacing: -0.5px;'>
                 LISTADO DETALLADO DE POZOS FALLADOS
            </h3>
        </div>
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
                    hide_index=True,
                    use_container_width=True
                )
            
            with col_severidad:
                total_fallas_severidad = fallas_por_pozo['Cantidad de Fallas'].sum()
                num_pozos_fallados = fallas_por_pozo.shape[0]
                indice_severidad = (total_fallas_severidad / num_pozos_fallados) if num_pozos_fallados > 0 else 0;
                
                st.markdown(f"""
                <div style="padding: 20px; background: linear-gradient(135deg, #FF4B2B, #FF416C); border-radius: 15px; box-shadow: 0 10px 20px rgba(255, 65, 108, 0.3); text-align: center; color: white; margin-bottom: 20px;">
                    <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">ÍNDICE DE SEVERIDAD</div>
                    <div style="font-size: 32px; font-weight: 800; margin-top: 5px;">{indice_severidad:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                # Sección de pozos problema
                st.markdown("---")
                st.markdown(f"""
                <div class="fancy-subtitle">
                    <span>⚠️ Pozos Problema (Multi-Fallas)</span>
                </div>
                """, unsafe_allow_html=True)
                pozos_problema = fallas_por_pozo[fallas_por_pozo['Cantidad de Fallas'] > 1]

                if not pozos_problema.empty:
                    st.markdown("Los siguientes pozos tienen más de una falla en el último año:")
                    # Traer razón específica de pull y clasificarla
                    for index, row in pozos_problema.iterrows():
                        # Buscar razones en df_bd_filtered para ese pozo
                        if 'RAZON ESPECIFICA PULL' in df_bd_filtered.columns and 'FECHA_FALLA' in df_bd_filtered.columns:
                            mask = (
                                (df_bd_filtered['POZO'] == row['POZO']) &
                                (df_bd_filtered['FECHA_FALLA'].dt.date >= fecha_evaluacion - timedelta(days=365)) &
                                (df_bd_filtered['FECHA_FALLA'].dt.date <= fecha_evaluacion)
                            )
                            razones = df_bd_filtered.loc[mask, 'RAZON ESPECIFICA PULL'].dropna().tolist()
                        else:
                            razones = []
                        
                        # Usar st.expander para mantenerlo minimizado por defecto
                        with st.expander(f"⚠️ {row['POZO']} ({row['Cantidad de Fallas']} fallas)", expanded=False):
                            # Generar HTML estilizado para el contenido interno
                            razones_html = ""
                            if len(razones) == 0:
                                 razones_html = "<div style='opacity:0.6; font-style:italic; padding: 10px;'>No hay razones disponibles</div>"
                            else:
                                 for i, razon in enumerate(razones, 1):
                                     clasificacion = clasificar_razon_ia(razon)
                                     razon_clean = razon[:150] + "..." if len(razon) > 150 else razon
                                     # Estilo limpio para cada ítem dentro del expander
                                     razones_html += (
                                         f"<div style='margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;'>"
                                         f"<strong style='color: {COLOR_PRINCIPAL}; font-size: 0.95em;'>Falla {i}:</strong> <span style='opacity:0.9;'>{razon_clean}</span>"
                                         f"<br><div style='margin-top:4px;'><span style='font-size: 0.75em; opacity: 0.6;'>Clasificación sugerida: </span><span class='highlight-pill'>{clasificacion}</span></div>"
                                         f"</div>"
                                     )
                            
                            st.markdown(f"<div>{razones_html}</div>", unsafe_allow_html=True)

                else:
                    st.info("¡No hay pozos con más de una falla en el último año!")

        else:
            st.info(f"No hay pozos fallados en el último año para el activo '{selected_activo}' en la fecha de evaluación seleccionada.")

    with tab_indices:
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
            <div style="background: linear-gradient(90deg, rgba(94, 255, 0, 0.1), transparent); padding: 10px; border-left: 5px solid #5EFF00; border-radius: 5px; margin-top: 2em; margin-bottom: 1em;">
                <h3 id="indices-de-falla" style='font-size:1.6rem; font-weight:800; margin:0; color:#5EFF00; letter-spacing: -0.5px;'>
                     ÍNDICES DE FALLA
                </h3>
            </div>
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
                    # Tabla de resumen ocupa todo el ancho arriba
                    st.markdown(f"""
                    <div class="fancy-subtitle">
                        <span>📊 Resumen de Índices para {selected_activo} (Rolling 12 Meses)</span>
                    </div>
                    """, unsafe_allow_html=True)
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
                        # Gráfico ECharts Premium: Histórico Líneas
                        # Convertir meses a string para JSON
                        months_idx = [str(m) for m in df_plot_indices['Mes']]
                        val_if_on = [round(float(x)*100, 2) for x in df_plot_indices['Indice_Falla_Rolling_ON'].tolist()]
                        val_if_als = [round(float(x)*100, 2) for x in df_plot_indices['Indice_Falla_Rolling_ALS_ON'].tolist()]
                        
                        echarts_options_line = {
                            "backgroundColor": "transparent",
                            "title": {"text": "HISTÓRICO ÍNDICE DE FALLA (ROLLING 12M)", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 12, "fontWeight": "bold"}},
                            "tooltip": {"trigger": "axis", "formatter": "{b}<br/>{a0}: {c0}%<br/>{a1}: {c1}%"},
                            "legend": {"data": ["Ind. Falla ON", "Ind. Falla ALS ON"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 9}},
                            "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                            "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": "#888", "fontSize": 9}}],
                            "yAxis": [{"type": "value", "axisLabel": {"color": "#888", "fontSize": 9, "formatter": "{value}%"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                            "series": [
                                {"name": "Ind. Falla ON", "type": "line", "smooth": True, "data": val_if_on, "itemStyle": {"color": COLOR_PRINCIPAL}},
                                {"name": "Ind. Falla ALS ON", "type": "line", "smooth": True, "data": val_if_als, "itemStyle": {"color": "#00f2ff"}}
                            ]
                        }
                        
                        html_line = f"""
                        <div id="echarts-if-line" style="width:100%; height:250px;"></div>
                        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                        <script>
                            (function() {{
                                var myChart = echarts.init(document.getElementById('echarts-if-line'), 'dark');
                                myChart.setOption({json.dumps(echarts_options_line)});
                                window.addEventListener('resize', function() {{ myChart.resize(); }});
                            }})();
                        </script>
                        """
                        components.html(html_line, height=270)

                    with col_bar_mes:
                        # Gráfico ECharts Premium: Histórico Barras
                        echarts_options_bar_if = {
                            "backgroundColor": "transparent",
                            "title": {"text": "ÍNDICE DE FALLA MENSUAL", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 12, "fontWeight": "bold"}},
                            "tooltip": {"trigger": "axis", "formatter": "{b}<br/>{a0}: {c0}%<br/>{a1}: {c1}%"},
                            "legend": {"data": ["Ind. Falla ON", "Ind. Falla ALS ON"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 9}},
                            "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                            "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": "#888", "fontSize": 9}}],
                            "yAxis": [{"type": "value", "axisLabel": {"color": "#888", "fontSize": 9, "formatter": "{value}%"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                            "series": [
                                {"name": "Ind. Falla ON", "type": "bar", "data": val_if_on, "itemStyle": {"color": COLOR_PRINCIPAL, "borderRadius": [4, 4, 0, 0]}},
                                {"name": "Ind. Falla ALS ON", "type": "bar", "data": val_if_als, "itemStyle": {"color": "#00f2ff", "borderRadius": [4, 4, 0, 0]}}
                            ]
                        }
                        
                        html_bar_if = f"""
                        <div id="echarts-if-bar" style="width:100%; height:250px;"></div>
                        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                        <script>
                            (function() {{
                                var myChart = echarts.init(document.getElementById('echarts-if-bar'), 'dark');
                                myChart.setOption({json.dumps(echarts_options_bar_if)});
                                window.addEventListener('resize', function() {{ myChart.resize(); }});
                            }})();
                        </script>
                        """
                        components.html(html_bar_if, height=270)

                    # Detalle de Cálculos - Título removido por solicitud de usuario

                    col_table_operativos, col_chart_operativos = st.columns([0.5, 0.5])
                    with col_table_operativos:
                        df_display_mensual = df_mensual_hist.copy()
                        df_display_mensual = df_display_mensual[['Mes', 'Fallas Totales', 'Fallas ALS', 'Pozos Operativos', 'Pozos ON']]
                        st.dataframe(df_display_mensual)

                    with col_chart_operativos:
                        # Gráfico ECharts Premium: Operatividad vs Fallas (Doble Eje)
                        # Convertir meses a string para JSON
                        months_op = [str(m) for m in df_mensual_hist['Mes']]
                        p_operativos = df_mensual_hist['Pozos Operativos'].tolist()
                        p_on = df_mensual_hist['Pozos ON'].tolist()
                        f_totales = df_mensual_hist['Fallas Totales'].tolist()
                        f_als = df_mensual_hist['Fallas ALS'].tolist()

                        echarts_options_op = {
                            "backgroundColor": "transparent",
                            "title": {"text": "OPERATIVIDAD VS FALLAS MENSUALES", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 14, "fontWeight": "900"}},
                            "tooltip": {"trigger": "axis"},
                            "legend": {"data": ["Pozos Operativos", "Pozos ON", "Fallas Totales", "Fallas ALS"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 9}},
                            "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                            "xAxis": [{"type": "category", "data": months_op, "axisLabel": {"color": "#888", "fontSize": 10}}],
                            "yAxis": [
                                {"type": "value", "name": "POZOS", "axisLabel": {"color": "#0a84ff"}},
                                {"type": "value", "name": "FALLAS", "position": "right", "axisLabel": {"color": "#FF8C00"}, "splitLine": {"show": False}}
                            ],
                            "series": [
                                {"name": "Pozos Operativos", "type": "line", "smooth": True, "data": p_operativos, "itemStyle": {"color": "#135bec"}, "lineStyle": {"width": 3}},
                                {"name": "Pozos ON", "type": "line", "smooth": True, "data": p_on, "itemStyle": {"color": "#00f2ff"}, "lineStyle": {"width": 3}},
                                {"name": "Fallas Totales", "type": "bar", "yAxisIndex": 1, "data": f_totales, "itemStyle": {"color": "rgba(255, 140, 0, 0.4)"}},
                                {"name": "Fallas ALS", "type": "bar", "yAxisIndex": 1, "data": f_als, "itemStyle": {"color": "rgba(138, 43, 226, 0.6)"}}
                            ]
                        }
                        
                        html_op = f"""
                        <div id="echarts-op-fallas" style="width:100%; height:350px;"></div>
                        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                        <script>
                            (function() {{
                                var myChart = echarts.init(document.getElementById('echarts-op-fallas'), 'dark');
                                myChart.setOption({json.dumps(echarts_options_op)});
                                window.addEventListener('resize', function() {{ myChart.resize(); }});
                            }})();
                        </script>
                        """
                        components.html(html_op, height=370)

                except Exception as e:
                    st.error(f"Ocurrió un error al calcular los índices de falla. Asegúrate de que los datos filtrados contengan la información necesaria: {e}")
    # Sección MTBF: Mover a tab_performance
    with tab_performance:
        st.markdown("<br>", unsafe_allow_html=True)
        # Análisis MTBF
        try:
            mtbf_global, mtbf_por_pozo = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
            mostrar_mtbf(mtbf_global, mtbf_por_pozo, df_bd=df_bd_filtered, fecha_evaluacion=fecha_evaluacion)
        except Exception as e:
            st.warning(f"No se pudo calcular el MTBF: {e}")

    # Dataset y Gráficos Resumen: Mover a tab_indices
    with tab_indices:
        st.markdown("##### 📁 DATA FINAL DE TRABAJO")
        st.dataframe(df_bd_filtered, use_container_width=True)
        
        st.markdown("---")
        # Charts removed from here - moved to top layout as requested






