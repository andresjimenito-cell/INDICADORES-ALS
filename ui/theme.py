"""Tema de Parex Resources (Tema Claro, Verdes, Dorados y Blancos).
"""

import streamlit as st

def _detect_streamlit_base():
    return "light"


def get_colors(theme_base: str | None = None):
    """Devuelve el diccionario de colores corporativos de Parex Resources (Tema Claro) con tokens semánticos."""
    return {
        "brand": {
            "primary": "#2E7D46",       # Verde principal Parex
            "primary_dark": "#1F4620",  # Verde oscuro Parex
            "primary_light": "#EEF3EA", # Verde muy claro
            "secondary": "#C98A2C",     # Dorado principal Parex
            "secondary_light": "#FDF6E9",
            "accent": "#1F4620",        # Verde oscuro Parex
            "petrol": "#223A5E",        # Azul petróleo
        },
        "surface": {
            "background": "#F7F8F5",    # Fondo claro sutil
            "container_bg": "#ffffff",  # Tarjetas blancas
            "border": "#DCE2D8",
            "glow": "rgba(201, 138, 44, 0.2)",
        },
        "text": {
            "primary": "#262626",       # Texto principal oscuro
            "muted": "#707070",         # Texto secundario suave
            "on_brand": "#ffffff",      # Texto sobre brand colors
        },
        "semantic": {
            "success": "#2E7D46",       # Verde = bueno, operativo, meta cumplida
            "warning": "#C98A2C",       # Dorado = atención, degradado, near-meta
            "danger": "#C0392B",        # Rojo = falla, crítica, fuera de meta
            "info": "#223A5E",          # Azul petróleo = info
        },
        "chart": {
            "series": [
                "#2E7D46",  # Verde principal
                "#C98A2C",  # Dorado
                "#1F4620",  # Verde oscuro
                "#223A5E",  # Azul petróleo
                "#C0392B",  # Rojo falla
                "#5C6B73",  # Gris pizarra
                "#707070",  # Gris neutro
                "#4CA46A",  # Verde claro
            ]
        }
    }


def get_plotly_layout(xaxis_color: str | None = None, yaxis_color: str | None = None, theme_base: str | None = None):
    """Devuelve un layout claro de Plotly alineado con Parex Resources y tab_tablero."""
    colors = get_colors()
    brand = colors["brand"]
    text = colors["text"]
    xa = xaxis_color or text["primary"]
    ya = yaxis_color or text["primary"]

    layout = {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, 'Segoe UI', Arial, sans-serif", "color": text["primary"], "size": 11},
        "title": {
            "font": {"family": "'Source Serif 4', Georgia, serif", "size": 16, "color": brand["primary_dark"]},
            "pad": {"t": 15, "b": 15},
            "x": 0.02,
            "xanchor": "left"
        },
        "xaxis": {
            "color": xa,
            "gridcolor": "rgba(46, 125, 70, 0.07)",
            "linecolor": "rgba(46, 125, 70, 0.2)",
            "zeroline": False,
            "tickfont": {"size": 9, "family": "Inter, sans-serif"},
            "showgrid": True,
            "automargin": True
        },
        "yaxis": {
            "color": ya,
            "gridcolor": "rgba(46, 125, 70, 0.07)",
            "linecolor": "rgba(46, 125, 70, 0.2)",
            "zeroline": False,
            "tickfont": {"size": 9, "family": "Inter, sans-serif"},
            "showgrid": True,
            "automargin": True
        },
        "legend": {
            "bgcolor": "rgba(255, 255, 255, 0.95)",
            "bordercolor": "rgba(46, 125, 70, 0.2)",
            "borderwidth": 1,
            "font": {"size": 10, "color": text["primary"], "family": "Inter, sans-serif"},
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.25,
            "xanchor": "center",
            "x": 0.5
        },
        "margin": {"t": 40, "b": 60, "l": 45, "r": 25},
        "hovermode": "closest",
        "hoverlabel": {
            "bgcolor": "#ffffff",
            "font": {"family": "Inter, Arial, sans-serif", "size": 11, "color": "#262626"},
            "bordercolor": brand["primary"]
        },
        "colorway": chart["series"]
    }

    return layout


def styled_title(text: str, subtitle: str = None) -> str:
    """Genera un título con el estilo corporativo de Parex (Tema Claro) - sin gradientes."""
    colors = get_colors()
    brand = colors["brand"]
    sub_html = f'<div style="font-size: 10px; font-weight: 800; color: {brand["secondary"]}; text-transform: uppercase; letter-spacing: 0.4em; margin-bottom: 0.25rem; opacity: 0.9; display: flex; align-items: center; gap: 10px;">' \
               f'<span style="height: 1px; width: 25px; background: {brand["secondary"]};"></span>{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div style="margin: 2rem 0 1.5rem 0; position: relative; width: 100%;">
        {sub_html}
        <h2 style="font-family: 'Montserrat', sans-serif; font-size: 2.2rem; font-weight: 900; line-height: 1.1; margin: 0; color: {brand["primary"]}; letter-spacing: -0.02em; display: flex; align-items: baseline; gap: 0.5rem;">
            <span style="opacity: 0.95;">{text}</span>
            <span style="height: 4px; width: 4px; background: {brand["secondary"]}; border-radius: 50%;"></span>
        </h2>
        <div style="margin-top: 0.75rem; height: 2px; width: 100px; background: {brand["primary"]}; border-radius: 2px;"></div>
    </div>
    """


def plotly_styled_title(text: str) -> str:
    return f"<b>{text.upper()}</b>"


def get_semantic_color(role: str) -> str:
    """Obtiene un color semántico por rol: 'success', 'warning', 'danger', 'info'."""
    colors = get_colors()
    return colors["semantic"].get(role, colors["brand"]["primary"])


def get_brand_color(role: str) -> str:
    """Obtiene un color de marca por rol: 'primary', 'secondary', 'accent'."""
    colors = get_colors()
    return colors["brand"].get(role, colors["brand"]["primary"])


def get_surface_color(role: str) -> str:
    """Obtiene un color de superficie por rol: 'background', 'container_bg', 'border', 'glow'."""
    colors = get_colors()
    return colors["surface"].get(role, colors["surface"]["background"])


def get_text_color(role: str) -> str:
    """Obtiene un color de texto por rol: 'primary', 'muted', 'on_brand'."""
    colors = get_colors()
    return colors["text"].get(role, colors["text"]["primary"])
