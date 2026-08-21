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
    get_semantic_color,
    get_brand_color,
    get_surface_color,
    get_text_color,
)

# ---------------------------------------------------------------------------
# 1. COLORES PRINCIPALES (desde theme.py - nuevo sistema semántico)
# ---------------------------------------------------------------------------
_colors = get_colors()
COLOR_PRINCIPAL    = get_brand_color("primary")      # #137659 - Brand primary (semantic: success)
COLOR_SECUNDARIO   = get_brand_color("secondary")    # #c09c2e - Brand secondary (semantic: warning)
COLOR_ACENTO       = get_brand_color("accent")       # #095139 - Brand accent
COLOR_FUENTE       = get_text_color("primary")       # #1f221e - Texto principal

# Semantic colors
COLOR_SUCCESS      = get_semantic_color("success")   # #137659 - Verde = bueno, meta cumplida
COLOR_WARNING      = get_semantic_color("warning")   # #c09c2e - Dorado = atención, near-meta
COLOR_DANGER       = get_semantic_color("danger")    # #c62828 - Rojo = falla, crítica
COLOR_INFO         = get_semantic_color("info")      # #0284c7 - Azul = información, ALS

# ---------------------------------------------------------------------------
# 2. COLORES DE FONDO (desde theme.py)
# ---------------------------------------------------------------------------
COLOR_FONDO_OSCURO     = get_surface_color("background")    # #f5f7f6
COLOR_FONDO_CONTENEDOR = get_surface_color("container_bg")  # #ffffff
COLOR_BORDE            = get_surface_color("border")        # rgba(19, 118, 89, 0.15)
COLOR_GLOW             = get_surface_color("glow")          # rgba(192, 156, 46, 0.2)

# ---------------------------------------------------------------------------
# 3. COLORES DE ACENTO Y GRILLA
# ---------------------------------------------------------------------------
COLOR_ACENTO_1 = COLOR_PRINCIPAL
COLOR_ACENTO_2 = get_text_color("muted")    # #5b5c55
COLOR_ACENTO_3 = COLOR_ACENTO_2
COLOR_GRID     = "rgba(19, 118, 89, 0.08)"

# ---------------------------------------------------------------------------
# 4. PALETA / SECUENCIA DE COLORES PARA GRÁFICOS
# ---------------------------------------------------------------------------
get_color_sequence = tema.get_color_sequence

# ---------------------------------------------------------------------------
# 5. COLORES DEL SIDEBAR / NEON (legacy - mantener compatibilidad)
# ---------------------------------------------------------------------------
NEON_PRIMARY   = COLOR_INFO
NEON_SECONDARY = COLOR_PRINCIPAL
GLOW_COLOR     = COLOR_GLOW
TEXT_DEFAULT   = COLOR_FUENTE
BG_DARK        = COLOR_FONDO_OSCURO
BG_CARD        = COLOR_FONDO_CONTENEDOR

# ---------------------------------------------------------------------------
# 6. RUTAS DE CACHÉ LOCAL
# ---------------------------------------------------------------------------
CACHE_DIR  = Path("cache_data")
CACHE_FILE = CACHE_DIR / "last_run_data.pkl"

# ---------------------------------------------------------------------------
# 7. FUNCIONES DE TEMA
# ---------------------------------------------------------------------------

BLOQUES_Y_CAMPOS_EXCLUIDOS = {
    'CANAGUARO',
    'ENTRERIOS',
    'ENTRE RIOS',
    'ENTRE RÍOS',
    'ENTRE_RIOS',
    'MAPACHE',
    'PERICO',
    'PERICO (88)',
    'MAPACHE PERICO',
    'MAPACHE - PERICO',
    'MAPACHE/PERICO',
    'MAPACHE-PERICO',
    'CORCEL NE',
    'CORCEL_NE',
    'CORCEL-NE',
    'CORCEL N3',
    'CORCEL_N3',
    'CORCEL-N3',
    'RIO META',
    'RIO_META',
    'RÍO META',
    'RÍO_META',
    'EL DIFICIL',
    'EL DIFICIL NE',
    'DIFICIL',
    'EL DIFÍCIL',
    'EL DIFÍCIL NE'
}

def get_theme(mode: str = 'light') -> dict:
    """Devuelve un dict con los colores principales del tema activo."""
    return {
        'COLOR_PRINCIPAL':         COLOR_PRINCIPAL,
        'COLOR_SECUNDARIO':        COLOR_SECUNDARIO,
        'COLOR_ACENTO':            COLOR_ACENTO,
        'COLOR_FUENTE':            COLOR_FUENTE,
        'COLOR_SUCCESS':           COLOR_SUCCESS,
        'COLOR_WARNING':           COLOR_WARNING,
        'COLOR_DANGER':            COLOR_DANGER,
        'COLOR_INFO':              COLOR_INFO,
        'COLOR_FONDO_OSCURO':      COLOR_FONDO_OSCURO,
        'COLOR_FONDO_CONTENEDOR':  COLOR_FONDO_CONTENEDOR,
        'COLOR_BORDE':             COLOR_BORDE,
        'COLOR_GLOW':              COLOR_GLOW,
        'get_color_sequence':      get_color_sequence,
    }


def get_plotly_layout(xaxis_color: str | None = None, yaxis_color: str | None = None) -> dict:
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


def styled_title(text: str, subtitle: str | None = None) -> str:
    """Genera un título HTML estilizado con el color principal del tema."""
    try:
        if subtitle is not None:
            return theme_styled_title(text, subtitle)
        return theme_styled_title(text)
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
