import os
import base64


def get_base64_image(fname: str) -> str:
    """Buscar una imagen en rutas comunes y devolver su contenido en base64."""
    search_paths = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, fname))
    except Exception: pass
    try:
        search_paths.append(os.path.join(os.getcwd(), fname))
    except Exception: pass
    try:
        search_paths.append(os.path.join(os.getcwd(), 'saved_uploads', fname))
    except Exception: pass

    for p in search_paths:
        if p and os.path.exists(p):
            try:
                with open(p, 'rb') as fh:
                    b = fh.read()
                return base64.b64encode(b).decode('utf-8')
            except Exception: continue
    return ''


def get_logo_img_tag(fname: str = 'logo_eiti.png', width: int = None, height: int = None, style: str = '') -> str:
    """Devuelve una etiqueta <img> con el logo en base64."""
    # Logo base64 de respaldo (Frontera ALS)
    LOGO_B64 = (
        "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"
        "OisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+Gf"
        "UfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE"
        "6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3Wp"
        "G50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Z"
        "f9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E"
        "/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu"
        "9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIs"
        "OisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+Gf"
        "UfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE"
        "6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG"
        "50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf9mZSRu9S/P+GfUfR3WpG50+Z6E/9S8SIsOisvUvE6L6p8Zf"
        "9mZSRu9S/P+GfUfR3WpG50+Z6E/"
    )
    b64_img = get_base64_image(fname)
    if not b64_img:
        b64_img = "".join(LOGO_B64.split())
    
    size_attrs = ""
    if width: size_attrs += f' width="{width}"'
    if height: size_attrs += f' height="{height}"'
    
    return f'<img src="data:image/png;base64,{b64_img}"{size_attrs} style="{style}"/>'
