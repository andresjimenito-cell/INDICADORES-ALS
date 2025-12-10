"""
Módulo de Tema Centralizado - Sistema de Colores INDICADORES ALS
==================================================================
Contiene todas las definiciones de colores y estilos utilizados en la aplicación.
Este módulo centraliza 91 constantes de color para mantener consistencia visual
y facilitar cambios de tema globales.

Convenciones:
- Todos los colores usan valores hexadecimales (#RRGGBB) o rgba()
- Los nombres describen función o apariencia
- Modificar valores aquí afecta toda la aplicación automáticamente
"""

# ============================================================================
# COLORES BASE Y TEMA PRINCIPAL
# ============================================================================

# Colores por defecto (fallback si no se usa tema cyberpunk)
COLOR_PRINCIPAL_DEFAULT = '#0a84ff'  # Azul estándar de iOS/Streamlit por defecto
COLOR_FUENTE_DEFAULT = '#0f1724'     # Gris oscuro para texto en temas claros

# ============================================================================
# TEMA NEÓN / CYBERPUNK (Activo por defecto)
# PALETA DE COLORES EITI COLOMBIA
# ============================================================================
COLOR_MAGENTA_NEON = '#C82B96'    # Magenta Vibrante (Acento Brillante del logo EITI)
                                  # Color principal de acentos, títulos y bordes
                                  # Usado en: títulos H1-H3, bordes de tarjetas, highlights
                                  
COLOR_AZUL_CIBER = '#292866'      # Púrpura Profundo / Índigo (Acento Oscuro del logo EITI)
                                  # Usado en: gradientes de fondo, botones hover, elementos oscuros
                                  
COLOR_PURPURA_MEDIO = '#570054'   # Púrpura Medio (Transición/Sombra del logo EITI)
                                  # Usado en: transiciones, sombras, elementos intermedios
                                  
COLOR_FONDO_OSCURO = '#0E1117'    # Fondo oscuro slate/negro (mismo tono que resumen_publico.py usa para elementos)
                                  # Color oscuro sólido para toda la aplicación
                                  
COLOR_FUENTE_NEON = '#E0FFFF'     # Texto claro con tono azulado para buena legibilidad
                                  # Usado en: párrafos, labels, texto general
                                  
COLOR_GLOW_SUAVE = 'rgba(168, 168, 255, 0.4)'  # Resplandor suave azul-violeta
                                                # Usado en: box-shadow, efectos de brillo

# ============================================================================
# ALIAS FUNCIONALES PRINCIPALES
# ============================================================================
COLOR_PRINCIPAL = COLOR_MAGENTA_NEON         # Alias: color de acento principal de la app
COLOR_FUENTE = COLOR_FUENTE_NEON            # Alias: color de texto por defecto
COLOR_FONDO_CONTENEDOR = 'transparent'      # Fondo de contenedores (transparente para glassmorphism)
COLOR_SOMBRA = 'transparent'                # Sombras deshabilitadas por defecto
COLOR_GRID = 'rgba(0,0,0,0)'                # Grid de gráficos (oculto)
COLOR_BORDE = 'rgba(0,0,0,0)'               # Bordes de elementos (oculto)

# ============================================================================
# SIDEBAR (Barra lateral de navegación y filtros)
# ============================================================================
COLOR_SIDEBAR_BG_START = '#090821'          # Inicio del gradiente vertical de fondo
COLOR_SIDEBAR_BG_END = '#000000'            # Final del gradiente vertical de fondo
COLOR_SIDEBAR_CARD_BG = 'rgba(10, 26, 47, 0.6)'  # Fondo semi-transparente de tarjetas
COLOR_TEXTO_DEFAULT = '#ffffff'             # Texto gris claro estándar
COLOR_GLOW_BLUE = '#ffffff'                 # Azul suave para resplandores y acentos

# ============================================================================
# PALETA DE COLORES PARA GRÁFICOS (Plotly/Charts)
# ============================================================================
# Secuencia de 7 colores ultra-saturados para series en gráficos de barras,
# líneas y pie charts. Se aplica automáticamente vía get_color_sequence()
SECUENCIA_COLORES_GRAFICOS = [
    '#00A2FF',  # 1. Azul Zafiro Eléctrico - Primera serie
    '#55228A',  # 2. Verde Lima Neón - Segunda serie
    '#0011D1',  # 3. Azul Cobalto Profundo - Tercera serie
    '#00F5FF',  # 4. Cyan/Verde Neón Puro - Cuarta serie
    '#4B0073',  # 5. Morado Índigo Profundo - Quinta serie
    '#000980',  # 6. Azul Ultra Oscuro Medianoche - Sexta serie
    "#A1039D"   # 7. Magenta Vibrante - Séptima serie
]

# ============================================================================
# CLASIFICACIÓN DE RUN LIFE (Fallas por tiempo de operación)
# ============================================================================
# Colores específicos para categorizar fallas según días de operación:
COLOR_RL_INFANTIL = '#0051FF'       # Azul intenso - Fallas en primeros 30 días
COLOR_RL_PREMATURA = '#5EFF00'      # Verde lima - Fallas entre 30-60 días
COLOR_RL_EN_GARANTIA = '#0011D1'    # Azul profundo - Fallas hasta 1100 días (bajo garantía)
COLOR_RL_SIN_GARANTIA = '#4B0073'   # Morado - Fallas después de 1100 días

# ============================================================================
# DASHBOARD CSS (Variables de diseño para headers y UI)
# ============================================================================
COLOR_DASH_PRIMARY = '#6366f1'      # Índigo - Color primario de header
COLOR_DASH_SECONDARY = '#8b5cf6'    # Violeta - Color secundario de header
COLOR_DASH_PINK = '#ec4899'         # Rosa vibrante - Acentos especiales
COLOR_DASH_ORANGE = '#f97316'       # Naranja - Alertas/warnings
COLOR_DASH_CYAN = '#06b6d4'         # Cyan - Info/tooltips
COLOR_DASH_GREEN = '#10b981'        # Verde - Success/confirmaciones
COLOR_DASH_YELLOW = '#fbbf24'       # Amarillo - Advertencias suaves
COLOR_DASH_DARK = '#0f172a'         # Azul muy oscuro - Fondos de contraste
COLOR_DASH_LIGHT = '#f8fafc'        # Blanco azulado - Textos en fondos oscuros

# ============================================================================
# UI GENERAL (Mensajes, cuadros de éxito, elementos básicos)
# ============================================================================
COLOR_EXITO_TEXTO = '#292866'           # Verde neón para mensajes de éxito
COLOR_EXITO_FONDO_BOX = '#0a0e27'       # Fondo oscuro para cajas de confirmación
COLOR_BLANCO = '#ffffff'                # Blanco puro para textos de alto contraste
COLOR_NEGRO = '#000000'                 # Negro puro (raramente usado)
COLOR_TRANSPARENTE = 'rgba(0,0,0,0)'   # Transparente completo

# ============================================================================
# HEADER DEL DASHBOARD (Barra superior principal)
# ============================================================================
COLOR_HEADER_BG = '#1e293b'         # Fondo gris-azul oscuro del header
COLOR_HEADER_BORDER = '#3b82f6'     # Borde azul brillante del header
COLOR_HEADER_TEXT = '#f8fafc'       # Texto blanco-azulado del header
COLOR_PURPLE_LIGHT = '#a78bfa'      # Lila claro para acentos en header

# ============================================================================
# GRADIENTES Y EFECTOS VISUALES
# ============================================================================
# Componentes para gradientes lineales en CSS (magenta/púrpura)
COLOR_GRADIENTE_MAGENTA_1 = '#A1039D'   # Inicio gradiente magenta (KPI boxes)
COLOR_GRADIENTE_MAGENTA_2 = '#6A00A1'   # Final gradiente magenta (más oscuro)

# Componentes para gradientes lineales en CSS (azul)
COLOR_GRADIENTE_AZUL_1 = '#8800FF'      # Inicio gradiente azul (KPI boxes)
COLOR_GRADIENTE_AZUL_2 = '#0041D1'      # Final gradiente azul (más profundo)

# Colores transparentes para superposiciones y efectos glassmorphism
COLOR_BLANCO_TRANSP_11 = '#ffffff11'         # Blanco 7% opacidad (hex)
COLOR_AZUL_TRANSP_11 = '#8800FF11'           # Azul 7% opacidad (hex)
COLOR_BLANCO_TRANSP_02 = 'rgba(255,255,255,0.02)'  # Blanco 2% opacidad (rgba)
COLOR_BLANCO_TRANSP_06 = 'rgba(255,255,255,0.06)'  # Blanco 6% opacidad (rgba)

# Sombras de caja (box-shadow)
COLOR_SOMBRA_AZUL_44 = '#8800FF44'          # Azul 27% opacidad para glow effects
COLOR_SOMBRA_NEGRA_25 = 'rgba(0,0,0,0.25)'  # Negro 25% para sombras profundas
COLOR_SOMBRA_NEGRA_60 = 'rgba(0,0,0,0.6)'   # Negro 60% para anotaciones en gráficos

# Grid de gráficos Plotly
COLOR_GRID_NEON = 'rgba(0, 255, 153, 0.2)'  # Verde neón semi-transparente para gridlines

# Colores de texto sobre fondos especiales
COLOR_NEGRO_SUAVE = '#000011'               # Casi negro con tinte azul (texto en gradientes claros)

# ============================================================================
# EFECTOS VISUALES ANIMADOS (Fondo con luces)
# ============================================================================
# Colores para efectos de luz radial/gradiente en el fondo animado
COLOR_LUZ_RADIAL_1 = 'rgba(99, 102, 241, 0.15)'     # Índigo suave - Primera luz
COLOR_LUZ_RADIAL_2 = 'rgba(139, 92, 246, 0.1)'      # Violeta tenue - Segunda luz
COLOR_LUZ_RADIAL_3 = 'rgba(236, 72, 153, 0.08)'     # Rosa tenue - Tercera luz

# Partículas de estrellas brillantes
COLOR_PARTICULA_BLANCA = 'white'                     # Partículas brillantes tipo estrellas
COLOR_PARTICULA_OPACIDAD = '0.3'                     # Opacidad de las partículas (30%)

# ============================================================================
# FUNCIONES UTILITARIAS
# ============================================================================
def get_color_sequence():
    """
    Retorna la secuencia de colores para gráficos.
    
    Returns:
        list: Lista de 7 colores hexadecimales para usar en Plotly charts
    
    Uso:
        fig = px.bar(..., color_discrete_sequence=get_color_sequence())
    """
    return SECUENCIA_COLORES_GRAFICOS
