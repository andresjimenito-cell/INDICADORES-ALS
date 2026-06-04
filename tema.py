"""
Módulo de Tema Centralizado - Sistema de Colores Parex Resources
==================================================================
Centraliza los colores de la aplicación ajustados al tema corporativo de Parex.
"""

# ============================================================================
# COLORES BASE Y TEMA PRINCIPAL PAREX RESOURCES
# ============================================================================
COLOR_VERDE_PAREX = '#137659'      # Verde corporativo principal
COLOR_DORADO_PAREX = '#c09c2e'     # Dorado corporativo principal
COLOR_VERDE_OSCURO = '#095139'     # Verde oscuro para botones y estados activos
COLOR_FONDO_CLARO = '#f5f7f6'      # Fondo claro general
COLOR_TEXTO_OSCURO = '#1f221e'     # Texto principal oscuro
COLOR_TEXTO_MUTED = '#5b5c55'      # Texto silenciado gris oliva

# Compatibilidad con los nombres anteriores de variables
COLOR_MAGENTA_NEON = COLOR_VERDE_PAREX
COLOR_AZUL_CIBER = COLOR_VERDE_OSCURO
COLOR_PURPURA_MEDIO = COLOR_DORADO_PAREX
COLOR_FONDO_OSCURO = COLOR_FONDO_CLARO
COLOR_FUENTE_NEON = COLOR_TEXTO_OSCURO
COLOR_GLOW_SUAVE = 'rgba(192, 156, 46, 0.2)'

COLOR_PRINCIPAL = COLOR_VERDE_PAREX
COLOR_FUENTE = COLOR_TEXTO_OSCURO
COLOR_FONDO_CONTENEDOR = '#ffffff'
COLOR_SOMBRA = 'rgba(0, 0, 0, 0.05)'
COLOR_GRID = 'rgba(19, 118, 89, 0.08)'
COLOR_BORDE = 'rgba(19, 118, 89, 0.15)'

# ============================================================================
# SIDEBAR
# ============================================================================
COLOR_SIDEBAR_BG_START = '#eaf4ef'          # Fondo claro del sidebar
COLOR_SIDEBAR_BG_END = '#ffffff'            # Fin del gradiente claro
COLOR_SIDEBAR_CARD_BG = '#ffffff'           # Tarjetas blancas en el sidebar
COLOR_TEXTO_DEFAULT = COLOR_TEXTO_OSCURO
COLOR_GLOW_BLUE = COLOR_DORADO_PAREX

# ============================================================================
# GRÁFICOS
# ============================================================================
SECUENCIA_COLORES_GRAFICOS = [
    '#137659',  # 1. Verde Parex
    '#c09c2e',  # 2. Dorado Parex
    '#095139',  # 3. Verde oscuro
    '#8b7411',  # 4. Dorado oscuro
    '#167658',  # 5. Verde oliva
    '#5b5c55',  # 6. Gris oliva
    '#7c8072'   # 7. Verde grisáceo
]

# Clasificación de run life
COLOR_RL_INFANTIL = '#b29c3e'
COLOR_RL_PREMATURA = '#095139'
COLOR_RL_EN_GARANTIA = '#137659'
COLOR_RL_SIN_GARANTIA = '#5b5c55'

# ============================================================================
# INTERFAZ (DASHBOARD CSS)
# ============================================================================
COLOR_DASH_PRIMARY = COLOR_VERDE_PAREX
COLOR_DASH_SECONDARY = COLOR_DORADO_PAREX
COLOR_DASH_PINK = '#8b7411'
COLOR_DASH_ORANGE = '#d97706'
COLOR_DASH_CYAN = '#0f766e'
COLOR_DASH_GREEN = '#15803d'
COLOR_DASH_YELLOW = '#ca8a04'
COLOR_DASH_DARK = '#1f221e'
COLOR_DASH_LIGHT = '#ffffff'

# ============================================================================
# COMPONENTES COMUNES
# ============================================================================
COLOR_EXITO_TEXTO = '#15803d'
COLOR_EXITO_FONDO_BOX = '#eaf4ef'
COLOR_BLANCO = '#ffffff'
COLOR_NEGRO = '#000000'
COLOR_TRANSPARENTE = 'rgba(0,0,0,0)'

COLOR_HEADER_BG = '#137659'         # Fondo verde del header
COLOR_HEADER_BORDER = '#c09c2e'     # Borde dorado del header
COLOR_HEADER_TEXT = '#ffffff'       # Texto blanco en el header
COLOR_PURPLE_LIGHT = '#eaf4ef'

COLOR_GRADIENTE_MAGENTA_1 = COLOR_VERDE_PAREX
COLOR_GRADIENTE_MAGENTA_2 = COLOR_VERDE_OSCURO
COLOR_GRADIENTE_AZUL_1 = COLOR_VERDE_PAREX
COLOR_GRADIENTE_AZUL_2 = COLOR_DORADO_PAREX

COLOR_BLANCO_TRANSP_11 = 'rgba(19, 118, 89, 0.08)'
COLOR_AZUL_TRANSP_11 = 'rgba(192, 156, 46, 0.08)'
COLOR_BLANCO_TRANSP_02 = 'rgba(0, 0, 0, 0.02)'
COLOR_BLANCO_TRANSP_06 = 'rgba(0, 0, 0, 0.05)'

COLOR_SOMBRA_AZUL_44 = 'rgba(19, 118, 89, 0.15)'
COLOR_SOMBRA_NEGRA_25 = 'rgba(0,0,0,0.05)'
COLOR_SOMBRA_NEGRA_60 = 'rgba(0,0,0,0.1)'

COLOR_GRID_NEON = 'rgba(19, 118, 89, 0.15)'
COLOR_NEGRO_SUAVE = '#1f221e'

def get_color_sequence():
    return SECUENCIA_COLORES_GRAFICOS
