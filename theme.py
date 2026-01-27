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
    """Devuelve un diccionario de colores según el tema base con estética premium."""
    detected = _detect_streamlit_base()
    if theme_base is None:
        theme_base = detected or "dark"

    if theme_base == "dark":
        return {
            "primary": "#135bec",
            "secondary": "#00f2ff",
            "accent": "#ff0080",
            "background": "#0a0e27",
            "container_bg": "rgba(10, 14, 39, 0.7)",
            "text": "#FFFFFF",
            "muted": "#94a3b8",
            "border": "rgba(255, 255, 255, 0.1)",
            "glow": "rgba(19, 91, 236, 0.4)",
        }

    # light (mantiene consistencia pero más brillante)
    return {
        "primary": "#135bec",
        "secondary": "#00d9ff",
        "accent": "#ff0080",
        "background": "#f8fafc",
        "container_bg": "rgba(255, 255, 255, 0.8)",
        "text": "#0f172a",
        "muted": "#64748b",
        "border": "rgba(15, 23, 42, 0.1)",
        "glow": "rgba(19, 91, 236, 0.2)",
    }


def get_plotly_layout(xaxis_color: str | None = None, yaxis_color: str | None = None, theme_base: str | None = None):
    """Devuelve un layout HUD premium para Plotly."""
    colors = get_colors(theme_base)
    xa = xaxis_color or colors.get("muted")
    ya = yaxis_color or colors.get("muted")

    layout = {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, sans-serif", "color": colors.get("text"), "size": 12},
        "title": {"font": {"family": "Outfit, sans-serif", "size": 24, "color": colors.get("text")}},
        "xaxis": {
            "color": xa,
            "gridcolor": "rgba(255, 255, 255, 0.05)",
            "linecolor": colors.get("primary"),
            "zeroline": False,
            "tickfont": {"size": 10}
        },
        "yaxis": {
            "color": ya,
            "gridcolor": "rgba(255, 255, 255, 0.05)",
            "linecolor": colors.get("primary"),
            "zeroline": False,
            "tickfont": {"size": 10}
        },
        "legend": {
            "bgcolor": "rgba(10, 14, 39, 0.8)",
            "bordercolor": colors.get("border"),
            "borderwidth": 1,
            "font": {"size": 11, "color": colors.get("text")}
        },
        "margin": {"t": 80, "b": 60, "l": 60, "r": 40},
        "hoverlabel": {
            "bgcolor": colors.get("background"),
            "font": {"family": "Inter, sans-serif", "size": 13},
            "bordercolor": colors.get("secondary")
        }
    }

    return layout


def styled_title(text: str, subtitle: str = None) -> str:
    """Genera un título premium estilo HUD para st.markdown."""
    sub_html = f'<div style="font-size: 10px; font-weight: 800; color: #00f2ff; text-transform: uppercase; letter-spacing: 0.4em; margin-bottom: 0.25rem; opacity: 0.8; display: flex; align-items: center; gap: 10px;">' \
               f'<span style="height: 1px; width: 25px; background: linear-gradient(to right, #00f2ff, transparent);"></span>{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div style="margin: 2rem 0 1.5rem 0; position: relative; width: 100%;">
        {sub_html}
        <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 900; line-height: 1.1; margin: 0; color: white; letter-spacing: -0.02em; display: flex; align-items: baseline; gap: 0.5rem;">
            <span style="opacity: 0.95;">{text}</span>
            <span style="height: 4px; width: 4px; background: #00f2ff; border-radius: 50%; box-shadow: 0 0 10px #00f2ff;"></span>
        </h2>
        <div style="margin-top: 0.75rem; height: 2px; width: 100px; background: linear-gradient(to right, #135bec, transparent); border-radius: 2px;"></div>
    </div>
    """


def plotly_styled_title(text: str) -> str:
    """Genera un título compatible con Plotly (HTML limitado)."""
    return f"<b>{text.upper()}</b>"
