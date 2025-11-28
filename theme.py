"""Tema simple y adaptable para la aplicación.

Este módulo ofrece una paleta mínima que se adapta al tema de Streamlit
(si está disponible). Evita estilos pesados (sombras, bordes) para no
ocultar filtros u otros controles.
"""

def _detect_streamlit_base():
    """Intenta detectar la base del tema de Streamlit ('dark' o 'light').
    Devuelve 'dark'|'light' o None si no se puede detectar.
    """
    try:
        import streamlit as st
        # clave de configuración para el tema base
        # Preferimos la opción explícita 'theme.base'
        base = st.get_option("theme.base")
        if base in ("dark", "light"):
            return base
        # Algunas versiones/configuraciones exponen un dict en 'theme'
        theme_conf = st.get_option("theme")
        if isinstance(theme_conf, dict) and "base" in theme_conf and theme_conf["base"] in ("dark", "light"):
            return theme_conf["base"]
    except Exception:
        return None

    return None


def get_colors(theme_base: str | None = None):
    """Devuelve un diccionario simple de colores según el tema base.

    - Si `theme_base` es None, intenta detectar Streamlit; por defecto usa 'light'.
    - Los colores son mínimos: `primary`, `background`, `container_bg`, `text`, `muted`.
    """
    # Si no se pasa theme_base, intentamos detectar Streamlit. Si Streamlit está
    # configurado, devolvemos colores que respeten el tema y preferimos no forzar
    # un fondo (devuelve None en 'background') para que Streamlit lo maneje.
    detected = _detect_streamlit_base()
    if theme_base is None:
        theme_base = detected or "light"

    if theme_base == "dark":
        # Si Streamlit está activado y detección fue exitosa, no forzamos
        # un background para permitir que Streamlit pinte su fondo.
        return {
            "primary": "#0a84ff",
            "background": None if detected else "#0b1220",
            "container_bg": "rgba(255,255,255,0.03)",
            "text": "#E6EEF6",
            "muted": "#94a3b8",
        }

    # light (por defecto)
    return {
        "primary": "#0a84ff",
        "background": None if detected else "#ffffff",
        "container_bg": "rgba(0,0,0,0.03)",
        "text": "#0f1724",
        "muted": "#475569",
    }


def get_plotly_layout(xaxis_color: str | None = None, yaxis_color: str | None = None, theme_base: str | None = None):
    """Devuelve un layout mínimo para Plotly que se adapta al tema.

    - No dibuja sombras ni bordes extra.
    - Usa colores de texto para ejes y `primary` para títulos.
    """
    colors = get_colors(theme_base)
    xa = xaxis_color or colors.get("text")
    ya = yaxis_color or colors.get("text")

    layout = {
        "font_color": colors.get("text"),
        "title_font_color": colors.get("primary"),
        "xaxis": {"color": xa, "gridcolor": "rgba(0,0,0,0)"},
        "yaxis": {"color": ya, "gridcolor": "rgba(0,0,0,0)"},
    }

    # Si colors['background'] es None, eso indica que queremos que Streamlit
    # use su propio fondo; no forzamos plot_bgcolor/paper_bgcolor en ese caso.
    # Si colors['background'] es None, eso indica que queremos que Streamlit
    # use su propio fondo; en ese caso devolveremos explícitamente un fondo
    # transparente para Plotly para que el DOM deje ver el fondo que Streamlit
    # aplica. Si colors['background'] tiene un valor concreto, lo usamos.
    if colors.get("background") is not None:
        layout["plot_bgcolor"] = colors.get("background")
        layout["paper_bgcolor"] = colors.get("background")
    else:
        # Forzar transparencia explícita para que el canvas de Plotly no pinte
        # un fondo blanco por defecto y deje ver el fondo manejado por Streamlit.
        layout["plot_bgcolor"] = "rgba(0,0,0,0)"
        layout["paper_bgcolor"] = "rgba(0,0,0,0)"

    # Leyenda transparente por defecto para evitar cuadros blancos detrás
    # de la leyenda en temas donde Plotly pondría un fondo sólido.
    legend_font_color = colors.get("text") or "#000000"
    layout["legend"] = {
        "bgcolor": "rgba(0,0,0,0)",
        "bordercolor": "rgba(0,0,0,0)",
        # Plotly exige un color válido; usar el color de texto del tema.
        "font": {"color": legend_font_color}
    }

    return layout


def styled_title(text: str, theme_base: str | None = None) -> str:
    """Devuelve HTML simple para títulos, usando el color `primary` del tema.

    Evita sombras y estilos que puedan interferir con filtros o legibilidad.
    """
    colors = get_colors(theme_base)
    return f"<span style=\"color:{colors['primary']}; font-weight:600;\">{text}</span>"
