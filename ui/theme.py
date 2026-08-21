"""Tema de Parex Resources (Tema Claro, Verdes, Dorados y Blancos).
"""

import streamlit as st

def _detect_streamlit_base():
    return "light"


def get_colors(theme_base: str | None = None):
    """Devuelve el diccionario de colores corporativos de Parex Resources (Tema Claro) con tokens semánticos."""
    return {
        "brand": {
            "primary": "#137659",       # Verde principal Parex
            "secondary": "#c09c2e",     # Dorado principal Parex
            "accent": "#095139",        # Verde oscuro Parex
        },
        "surface": {
            "background": "#f5f7f6",    # Fondo claro
            "container_bg": "#ffffff",  # Tarjetas blancas
            "border": "rgba(19, 118, 89, 0.15)",
            "glow": "rgba(192, 156, 46, 0.2)",
        },
        "text": {
            "primary": "#1f221e",       # Texto principal
            "muted": "#5b5c55",         # Texto silenciado
            "on_brand": "#ffffff",      # Texto sobre brand colors
        },
        "semantic": {
            "success": "#137659",       # Verde = bueno, operativo, meta cumplida
            "warning": "#c09c2e",       # Dorado = atención, degradado, near-meta
            "danger": "#c62828",        # Rojo = falla, crítica, fuera de meta
            "info": "#0284c7",          # Azul = información, neutro, ALS
        },
        "chart": {
            "series": [
                "#137659",  # Verde principal
                "#c09c2e",  # Dorado
                "#095139",  # Verde oscuro
                "#8b7411",  # Dorado oscuro
                "#167658",  # Verde claro
                "#5b5c55",  # Gris oliva
                "#0284c7",  # Azul info
                "#c62828",  # Rojo danger
            ]
        }
    }


def get_plotly_layout(xaxis_color: str | None = None, yaxis_color: str | None = None, theme_base: str | None = None):
    """Devuelve un layout claro de Plotly alineado con Parex Resources."""
    colors = get_colors()
    brand = colors["brand"]
    text = colors["text"]
    chart = colors["chart"]
    xa = xaxis_color or text["primary"]
    ya = yaxis_color or text["primary"]

    layout = {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(234, 244, 239, 0.4)", # Fondo verde claro traslúcido
        "font": {"family": "Montserrat, Arial, sans-serif", "color": text["primary"], "size": 12},
        "title": {
            "font": {"family": "Montserrat, Arial, sans-serif", "size": 18, "color": brand["primary"]},
            "pad": {"t": 20, "b": 20},
            "x": 0.05,
            "xanchor": "left"
        },
        "xaxis": {
            "color": xa,
            "gridcolor": "rgba(19, 118, 89, 0.08)",
            "linecolor": "rgba(19, 118, 89, 0.2)",
            "zeroline": False,
            "tickfont": {"size": 10},
            "showgrid": True,
            "automargin": True
        },
        "yaxis": {
            "color": ya,
            "gridcolor": "rgba(19, 118, 89, 0.08)",
            "linecolor": "rgba(19, 118, 89, 0.2)",
            "zeroline": False,
            "tickfont": {"size": 10},
            "showgrid": True,
            "automargin": True
        },
        "legend": {
            "bgcolor": "rgba(255, 255, 255, 0.95)",
            "bordercolor": "rgba(19, 118, 89, 0.2)",
            "borderwidth": 1,
            "font": {"size": 11, "color": text["primary"]},
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.3,
            "xanchor": "center",
            "x": 0.5
        },
        "margin": {"t": 80, "b": 100, "l": 60, "r": 40},
        "hovermode": "closest",
        "hoverlabel": {
            "bgcolor": "#ffffff",
            "font": {"family": "Montserrat, Arial, sans-serif", "size": 13, "color": "#1f221e"},
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
