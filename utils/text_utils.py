"""
utils/text_utils.py
Utilidades para manejo de texto, codificación y formatos consistentes.
Soluciona problemas de caracteres raros (Ã, Â·) y estandariza mensajes.
"""
import unicodedata

# Diccionario de reemplazo para caracteres problemáticos comunes
CHAR_FIXES = {
    'Ã': '',  # A menudo artefacto de decodificación UTF-8 mal interpretada
    'Â': '',  # Artefacto común antes de puntos medios o tildes
    '': '',  # Caracter de reemplazo
}

def clean_text(text: str) -> str:
    """
    Limpia texto de artefactos de codificación comunes y normaliza unicode.
    Útil para arreglar símbolos raros en títulos y tablas.
    """
    if not isinstance(text, str):
        return text
    
    # Normalizar unicode (NFKD separa acentos de letras base)
    text = unicodedata.normalize('NFKD', text)
    
    # Eliminar artefactos comunes
    for bad, good in CHAR_FIXES.items():
        text = text.replace(bad, good)
    
    # Limpiar espacios dobles resultantes
    text = " ".join(text.split())
    
    return text.strip()

def get_status_badge_text(count: int, label_singular: str, label_plural: str) -> str:
    """
    Genera texto consistente para contadores.
    Ej: "0 ALS", "1 Falla", "5 Fallas"
    """
    if count == 0:
        return f"0 {label_plural}"
    elif count == 1:
        return f"1 {label_singular}"
    else:
        return f"{count} {label_plural}"

def format_metric_value(value, decimals=0, suffix="", prefix=""):
    """
    Formatea valores numéricos para métricas de manera consistente.
    Maneja nulos y ceros elegantemente.
    """
    if value is None:
        return "N/A"
    
    try:
        import numpy as np
        if not np.isfinite(value):
            return "N/A"
    except (ImportError, TypeError, ValueError):
        pass
    
    if decimals == 0:
        formatted = f"{int(value):,}"
    else:
        formatted = f"{value:,.{decimals}f}"
    
    return f"{prefix}{formatted}{suffix}"

def safe_string_conversion(val):
    """
    Convierte cualquier valor a string de forma segura, evitando errores de encoding.
    """
    if val is None:
        return ""
    s = str(val)
    return clean_text(s)
