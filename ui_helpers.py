import os
import base64


def get_base64_image(fname: str) -> str:
    """Buscar una imagen en rutas comunes y devolver su contenido en base64 (sin prefijo MIME).
    Rutas buscadas: directorio del script, working directory, carpeta 'saved_uploads' en CWD.
    Devuelve cadena vacía si no se encuentra o no puede leerse.
    """
    search_paths = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(script_dir, fname))
    except Exception:
        pass
    try:
        search_paths.append(os.path.join(os.getcwd(), fname))
    except Exception:
        pass
    try:
        search_paths.append(os.path.join(os.getcwd(), 'saved_uploads', fname))
    except Exception:
        pass

    for p in search_paths:
        if p and os.path.exists(p):
            try:
                with open(p, 'rb') as fh:
                    b = fh.read()
                return base64.b64encode(b).decode('utf-8')
            except Exception:
                continue
    return ''


def get_logo_img_tag(fname: str = 'logo_eiti.png', width: int = None, height: int = None, style: str = '') -> str:
    """Devuelve una etiqueta <img> con el logo en base64 si se encuentra; si no, devuelve
    una etiqueta con una URL pública de respaldo.
    """
    b64 = get_base64_image(fname)
    size_attrs = ''
    if width:
        size_attrs += f" width='{width}'"
    if height:
        size_attrs += f" height='{height}'"
    if b64:
        return f"<img src=\"data:image/png;base64,{b64}\"{size_attrs} style='{style}'/>"
    # Fallback: imagen remota conocida (Frontera) — se puede cambiar si se desea
    fallback = 'https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png'
    return f"<img src='{fallback}'{size_attrs} style='{style}'/>"
