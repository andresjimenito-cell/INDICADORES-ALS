"""Tema de Parex Resources (Tema Claro, Verdes, Dorados y Blancos).
"""

import streamlit as st

def _detect_streamlit_base():
    return "light"


def get_colors(theme_base: str | None = None):
    """Devuelve el diccionario de colores corporativos de Parex Resources (Tema Claro)."""
    return {
        "primary": "#137659",       # Verde principal Parex
        "secondary": "#c09c2e",     # Dorado principal Parex
        "accent": "#095139",        # Verde oscuro Parex
        "background": "#f5f7f6",    # Fondo claro
        "container_bg": "#ffffff",  # Tarjetas blancas
        "text": "#1f221e",          # Texto oscuro para alta legibilidad
        "muted": "#5b5c55",         # Gris oliva/silenciado
        "border": "rgba(19, 118, 89, 0.15)",
        "glow": "rgba(192, 156, 46, 0.2)",
        "color_sequence": lambda mode=None: [
            "#137659",  # Verde principal
            "#c09c2e",  # Dorado
            "#095139",  # Verde oscuro
            "#8b7411",  # Dorado oscuro
            "#167658",  # Verde claro
            "#5b5c55"   # Gris oliva
        ]
    }


def get_plotly_layout(xaxis_color: str | None = None, yaxis_color: str | None = None, theme_base: str | None = None):
    """Devuelve un layout claro de Plotly alineado con Parex Resources."""
    colors = get_colors()
    xa = xaxis_color or colors.get("text")
    ya = yaxis_color or colors.get("text")

    layout = {
        "template": "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(234, 244, 239, 0.4)", # Fondo verde claro traslúcido
        "font": {"family": "Montserrat, Arial, sans-serif", "color": colors.get("text"), "size": 12},
        "title": {
            "font": {"family": "Montserrat, Arial, sans-serif", "size": 18, "color": colors.get("primary")},
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
            "font": {"size": 11, "color": colors.get("text")},
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
            "bordercolor": "#137659"
        },
        "colorway": colors["color_sequence"]()
    }

    return layout


def styled_title(text: str, subtitle: str = None) -> str:
    """Genera un título con el estilo corporativo de Parex (Tema Claro)."""
    colors = get_colors()
    sub_html = f'<div style="font-size: 10px; font-weight: 800; color: {colors["secondary"]}; text-transform: uppercase; letter-spacing: 0.4em; margin-bottom: 0.25rem; opacity: 0.9; display: flex; align-items: center; gap: 10px;">' \
               f'<span style="height: 1px; width: 25px; background: linear-gradient(to right, {colors["secondary"]}, transparent);"></span>{subtitle}</div>' if subtitle else ''
    
    return f"""
    <div style="margin: 2rem 0 1.5rem 0; position: relative; width: 100%;">
        {sub_html}
        <h2 style="font-family: 'Montserrat', sans-serif; font-size: 2.2rem; font-weight: 900; line-height: 1.1; margin: 0; color: {colors["primary"]}; letter-spacing: -0.02em; display: flex; align-items: baseline; gap: 0.5rem;">
            <span style="opacity: 0.95;">{text}</span>
            <span style="height: 4px; width: 4px; background: {colors["secondary"]}; border-radius: 50%; box-shadow: 0 0 10px {colors["secondary"]};"></span>
        </h2>
        <div style="margin-top: 0.75rem; height: 2px; width: 100px; background: linear-gradient(to right, {colors["primary"]}, transparent); border-radius: 2px;"></div>
    </div>
    """


def plotly_styled_title(text: str) -> str:
    return f"<b>{text.upper()}</b>"
