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
    """Devuelve una etiqueta <img> con el logo."""
    url = "https://companieslogo.com/img/orig/PXT.TO_BIG.D-d6c3b981.png?t=1720244493"
    size_attrs = ""
    if width: size_attrs += f' width="{width}"'
    if height: size_attrs += f' height="{height}"'
    
    return f'<img src="{url}"{size_attrs} style="{style}"/>'
