"""
config.py
=========
Configuración global del proyecto: variables de color, constantes de caché,
funciones auxiliares de tema y layout de Plotly.

No contiene lógica de UI ni de cálculo. Solo constantes y getters.
"""

import os
import base64
from pathlib import Path

import tema
from theme import (
    get_colors,
    get_plotly_layout as theme_get_plotly_layout,
    styled_title as theme_styled_title,
    plotly_styled_title as theme_plotly_styled_title,
)

# ---------------------------------------------------------------------------
# 1. COLORES PRINCIPALES (desde tema.py)
# ---------------------------------------------------------------------------
COLOR_MAGENTA_NEON = tema.COLOR_MAGENTA_NEON
COLOR_AZUL_CIBER   = tema.COLOR_AZUL_CIBER
COLOR_GLOW_SUAVE   = tema.COLOR_GLOW_SUAVE
COLOR_FUENTE       = tema.COLOR_FUENTE
COLOR_PRINCIPAL    = COLOR_MAGENTA_NEON   # alias semántico

# ---------------------------------------------------------------------------
# 2. COLORES DE FONDO (desde theme y tema)
# ---------------------------------------------------------------------------
_colors = get_colors()
_bg_raw = _colors.get('background', None)

if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = tema.COLOR_FONDO_OSCURO

COLOR_FONDO_CONTENEDOR = tema.COLOR_FONDO_CONTENEDOR
COLOR_SOMBRA           = tema.COLOR_SOMBRA

# ---------------------------------------------------------------------------
# 3. COLORES DE ACENTO Y GRILLA
# ---------------------------------------------------------------------------
COLOR_ACENTO_1 = COLOR_PRINCIPAL
COLOR_ACENTO_2 = _colors.get('muted', '#888888')
COLOR_ACENTO_3 = COLOR_ACENTO_2
COLOR_GRID     = tema.COLOR_GRID
COLOR_BORDE    = tema.COLOR_BORDE

# ---------------------------------------------------------------------------
# 4. PALETA / SECUENCIA DE COLORES PARA GRÁFICOS
# ---------------------------------------------------------------------------
get_color_sequence = tema.get_color_sequence

# ---------------------------------------------------------------------------
# 5. COLORES DEL SIDEBAR / NEON
# ---------------------------------------------------------------------------
NEON_PRIMARY   = tema.COLOR_AZUL_CIBER
NEON_SECONDARY = tema.COLOR_MAGENTA_NEON
GLOW_COLOR     = tema.COLOR_GLOW_BLUE
TEXT_DEFAULT   = tema.COLOR_TEXTO_DEFAULT
BG_DARK        = tema.COLOR_SIDEBAR_BG_START
BG_CARD        = tema.COLOR_SIDEBAR_CARD_BG

# ---------------------------------------------------------------------------
# 6. RUTAS DE CACHÉ LOCAL
# ---------------------------------------------------------------------------
CACHE_DIR  = Path("cache_data")
CACHE_FILE = CACHE_DIR / "last_run_data.pkl"

# ---------------------------------------------------------------------------
# 7. FUNCIONES DE TEMA
# ---------------------------------------------------------------------------

def get_theme(mode: str = 'dark') -> dict:
    """Devuelve un dict con los colores principales del tema activo."""
    return {
        'COLOR_PRINCIPAL':        COLOR_PRINCIPAL,
        'COLOR_FUENTE':           COLOR_FUENTE,
        'COLOR_FONDO_OSCURO':     COLOR_FONDO_OSCURO,
        'COLOR_FONDO_CONTENEDOR': COLOR_FONDO_CONTENEDOR,
        'COLOR_SOMBRA':           COLOR_SOMBRA,
        'get_color_sequence':     get_color_sequence,
    }


def get_plotly_layout(xaxis_color: str = None, yaxis_color: str = None) -> dict:
    """
    Delega al layout de `theme.py` y usa valores seguros como fallback.
    """
    try:
        return theme_get_plotly_layout(xaxis_color, yaxis_color)
    except Exception:
        xa = xaxis_color or COLOR_FUENTE
        ya = yaxis_color or COLOR_FUENTE
        bg = tema.COLOR_TRANSPARENTE
        return {
            'plot_bgcolor':      bg,
            'paper_bgcolor':     bg,
            'font_color':        COLOR_FUENTE,
            'title_font_color':  COLOR_PRINCIPAL,
            'xaxis': {'color': xa, 'gridcolor': COLOR_GRID},
            'yaxis': {'color': ya, 'gridcolor': COLOR_GRID},
        }


def styled_title(text: str, subtitle: str = None) -> str:
    """Genera un título HTML estilizado con el color principal del tema."""
    try:
        return theme_styled_title(text, subtitle)
    except Exception:
        if subtitle:
            return (
                f"<div style='color:{COLOR_PRINCIPAL}; font-size: 0.8em;'>{subtitle}</div>"
                f"<span style=\"color:{COLOR_PRINCIPAL}; font-size: 1.5em; font-weight: bold;\">{text}</span>"
            )
        return f"<span style=\"color:{COLOR_PRINCIPAL};\">{text}</span>"


def plotly_styled_title(text: str) -> str:
    """Genera un título para gráficos Plotly en mayúsculas y negrita."""
    try:
        return theme_plotly_styled_title(text)
    except Exception:
        return f"<b>{text.upper()}</b>"


def get_base64_image(fname: str) -> str:
    """
    Lee una imagen local y devuelve su contenido en base64 (sin prefijo MIME).
    Busca en: directorio del script → CWD → saved_uploads.
    Devuelve cadena vacía si no se encuentra.
    """
    search_paths = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, fname))
    except Exception:
        pass
    try:
        search_paths.append(os.path.join(os.getcwd(), fname))
    except Exception:
        pass
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
