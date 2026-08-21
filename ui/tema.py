"""
Módulo de Tema Centralizado - Sistema de Colores Parex Resources
==================================================================
Centraliza los colores de la aplicación ajustados al tema corporativo de Parex.
Ahora usa el nuevo sistema semántico de theme.py como fuente de verdad.
"""

from theme import (
    get_colors,
    get_semantic_color,
    get_brand_color,
    get_surface_color,
    get_text_color,
)

_colors = get_colors()

# ============================================================================
# COLORES BASE Y TEMA PRINCIPAL PAREX RESOURCES (Brand colors)
# ============================================================================
COLOR_VERDE_PAREX      = get_brand_color("primary")      # #137659
COLOR_DORADO_PAREX     = get_brand_color("secondary")    # #c09c2e
COLOR_VERDE_OSCURO     = get_brand_color("accent")       # #095139
COLOR_FONDO_CLARO      = get_surface_color("background") # #f5f7f6
COLOR_TEXTO_OSCURO     = get_text_color("primary")       # #1f221e
COLOR_TEXTO_MUTED      = get_text_color("muted")         # #5b5c55

# Compatibilidad con los nombres anteriores de variables
COLOR_MAGENTA_NEON     = COLOR_VERDE_PAREX
COLOR_AZUL_CIBER       = COLOR_VERDE_OSCURO
COLOR_PURPURA_MEDIO    = COLOR_DORADO_PAREX
COLOR_FONDO_OSCURO     = COLOR_FONDO_CLARO
COLOR_FUENTE_NEON      = COLOR_TEXTO_OSCURO
COLOR_GLOW_SUAVE       = get_surface_color("glow")

COLOR_PRINCIPAL        = COLOR_VERDE_PAREX
COLOR_FUENTE           = COLOR_TEXTO_OSCURO
COLOR_FONDO_CONTENEDOR = get_surface_color("container_bg")
COLOR_SOMBRA           = 'rgba(0, 0, 0, 0.05)'
COLOR_GRID             = 'rgba(19, 118, 89, 0.08)'
COLOR_BORDE            = get_surface_color("border")

# ============================================================================
# COLORES SEMÁNTICOS (NUEVO - usar estos para estados/acciones)
# ============================================================================
COLOR_SUCCESS          = get_semantic_color("success")   # #137659 - Verde = bueno, meta cumplida
COLOR_WARNING          = get_semantic_color("warning")   # #c09c2e - Dorado = atención, near-meta
COLOR_DANGER           = get_semantic_color("danger")    # #c62828 - Rojo = falla, crítica
COLOR_INFO             = get_semantic_color("info")      # #0284c7 - Azul = información, ALS

# ============================================================================
# SIDEBAR
# ============================================================================
COLOR_SIDEBAR_BG_START = '#eaf4ef'
COLOR_SIDEBAR_BG_END   = '#ffffff'
COLOR_SIDEBAR_CARD_BG  = '#ffffff'
COLOR_TEXTO_DEFAULT    = COLOR_TEXTO_OSCURO
COLOR_GLOW_BLUE        = COLOR_DORADO_PAREX

# ============================================================================
# GRÁFICOS
# ============================================================================
SECUENCIA_COLORES_GRAFICOS = _colors["chart"]["series"]

# Clasificación de run life (legacy - mantener compatibilidad)
COLOR_RL_INFANTIL     = '#b29c3e'
COLOR_RL_PREMATURA    = COLOR_VERDE_OSCURO
COLOR_RL_EN_GARANTIA  = COLOR_VERDE_PAREX
COLOR_RL_SIN_GARANTIA = COLOR_TEXTO_MUTED

# ============================================================================
# INTERFAZ (DASHBOARD CSS)
# ============================================================================
COLOR_DASH_PRIMARY   = COLOR_VERDE_PAREX
COLOR_DASH_SECONDARY = COLOR_DORADO_PAREX
COLOR_DASH_PINK      = '#8b7411'
COLOR_DASH_ORANGE    = '#d97706'
COLOR_DASH_CYAN      = '#0f766e'
COLOR_DASH_GREEN     = '#15803d'
COLOR_DASH_YELLOW    = '#ca8a04'
COLOR_DASH_DARK      = COLOR_TEXTO_OSCURO
COLOR_DASH_LIGHT     = '#ffffff'

# ============================================================================
# COMPONENTES COMUNES
# ============================================================================
COLOR_EXITO_TEXTO       = COLOR_SUCCESS
COLOR_EXITO_FONDO_BOX   = '#eaf4ef'
COLOR_BLANCO            = '#ffffff'
COLOR_NEGRO             = '#000000'
COLOR_TRANSPARENTE      = 'rgba(0,0,0,0)'

COLOR_HEADER_BG         = COLOR_VERDE_PAREX
COLOR_HEADER_BORDER     = COLOR_DORADO_PAREX
COLOR_HEADER_TEXT       = '#ffffff'
COLOR_PURPLE_LIGHT      = '#eaf4ef'

COLOR_GRADIENTE_MAGENTA_1 = COLOR_VERDE_PAREX
COLOR_GRADIENTE_MAGENTA_2 = COLOR_VERDE_OSCURO
COLOR_GRADIENTE_AZUL_1    = COLOR_VERDE_PAREX
COLOR_GRADIENTE_AZUL_2    = COLOR_DORADO_PAREX

COLOR_BLANCO_TRANSP_11 = 'rgba(19, 118, 89, 0.08)'
COLOR_AZUL_TRANSP_11   = 'rgba(192, 156, 46, 0.08)'
COLOR_BLANCO_TRANSP_02 = 'rgba(0, 0, 0, 0.02)'
COLOR_BLANCO_TRANSP_06 = 'rgba(0, 0, 0, 0.05)'

COLOR_SOMBRA_AZUL_44   = 'rgba(19, 118, 89, 0.15)'
COLOR_SOMBRA_NEGRA_25  = 'rgba(0,0,0,0.05)'
COLOR_SOMBRA_NEGRA_60  = 'rgba(0,0,0,0.1)'

COLOR_GRID_NEON        = 'rgba(19, 118, 89, 0.15)'
COLOR_NEGRO_SUAVE      = COLOR_TEXTO_OSCURO

def get_color_sequence():
    return SECUENCIA_COLORES_GRAFICOS