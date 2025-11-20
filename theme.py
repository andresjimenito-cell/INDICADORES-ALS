"""Tema compartido para la aplicación: Dark Cyberpunk (Cian Eléctrico sobre Azul Profundo).
Paleta mejorada para un contraste alto y un look de pantalla holográfica.
"""
# --- PALETA BASE ---
COLOR_PRINCIPAL = '#00FFC2'  # Cian Eléctrico / Esmeralda Brillante (Acento)
COLOR_FONDO_OSCURO = '#101820'  # Azul Medianoche Profundo (Fondo)
COLOR_FONDO_CONTENEDOR = 'rgba(10, 24, 32, 0.8)'  # Contenedor semi-transparente
COLOR_SOMBRA = 'rgba(0, 255, 194, 0.6)'  # Sombra para efecto "brillo ciber"
COLOR_FUENTE = '#ffffff'  # Color de fuente claro (casi blanco/cian)

# --- FUNCIONES AUXILIARES ---

def get_color_sequence():
    """Devuelve una secuencia de colores que armoniza con el tema oscuro/cian."""
    return [
       '#00FF8C',  # 1. Verde Esmeralda (Principal, menos brillante que el cian puro)
        '#A66EFF',  # 2. Violeta/Púrpura Eléctrico (Alto contraste, moderno)
        '#00BFFF',  # 3. Azul Cielo Profundo (Tono frío)
        '#0b683a',  # 4. Naranja Caliente (Para alertas o fallas, no tan agresivo como el rojo)
        '#007A0C',  # 5. Dorado Suave / Amarillo (Fácil de leer en el fondo)
        '#30DDD5',  # 6. Turquesa Medio (Tono acuático)
        '#5952c7',  # 7. Blanco puro (Como recurso de último contraste)
        '#6A0DAD',  # 8. Índigo Profundo (Para subtonos o categorías menos importantes)
    ]

# ESTA ES LA FUNCIÓN ACTUALIZADA CON EL BORDE
def get_plotly_layout(xaxis_color=None, yaxis_color=None):
    """Devuelve un dict con layout base para Plotly usando el tema oscuro futurista,
    incluyendo un borde exterior en COLOR_PRINCIPAL.
    """
    xa = xaxis_color or COLOR_PRINCIPAL
    ya = yaxis_color or COLOR_PRINCIPAL
    
    # Definición de la forma de borde (Rectángulo)
    borde_shape = {
        'type': 'rect',
        # Coordenadas que cubren toda la figura (sistema 'paper')
        'xref': 'paper',
        'yref': 'paper',
        'x0': 0,
        'y0': 0,
        'x1': 1,
        'y1': 1,
        # Estilo del borde
        'line': {
            'color': COLOR_PRINCIPAL,
            'width': 1,  # Grosor del borde
        },
        'layer': 'below', # Asegura que esté detrás de los ejes y datos
    }
    
    return {
        'plot_bgcolor': COLOR_FONDO_OSCURO,
        'paper_bgcolor': COLOR_FONDO_OSCURO,
        'font_color': COLOR_FUENTE,
        'title_font_color': COLOR_PRINCIPAL,
        # Grillas sutiles
        'xaxis': {'color': xa, 'gridcolor': 'rgba(0, 255, 194, 0.2)'},
        'yaxis': {'color': ya, 'gridcolor': 'rgba(0, 255, 194, 0.2)'},
        # Añade la forma del borde al layout
        'shapes': [borde_shape] 
    }


def styled_title(text: str) -> str:
    """Devuelve HTML con color y sombra de texto para usar como título en gráficas/markdown."""
    return f"<span style=\"color:{COLOR_PRINCIPAL}; text-shadow: 0 0 8px {COLOR_SOMBRA};\">{text}</span>"