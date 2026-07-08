"""
data_loader.py
==============
Responsable de toda la entrada/salida de datos:
- Descarga desde OneDrive/SharePoint
- Caché local con pickle
- Carga y limpieza de archivos FORMA 9 y BD
- Normalización de archivos para pandas
"""

import io
import os
import re
import html as html_module
import pickle
import hashlib

import requests
import numpy as np
import pandas as pd
import streamlit as st

from data.config import CACHE_DIR, CACHE_FILE


# ===========================================================================
# 1. DESCARGA DESDE ONEDRIVE
# ===========================================================================

@st.cache_data(show_spinner="Descargando archivo desde la nube...", ttl=600)
def cached_onedrive_download(url: str, dest_filename: str):
    """
    Descarga un archivo desde OneDrive/SharePoint y lo guarda localmente.
    Usa caché para evitar descargas repetidas en cada rerun de Streamlit.
    Retorna la ruta local del archivo, o None si falla.
    """
    upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    dest_path = os.path.join(upload_dir, dest_filename)

    try:
        r = requests.get(url, timeout=30, allow_redirects=True)
        r.raise_for_status()
        content_type = r.headers.get('content-type', '')
        content = r.content
        is_html = 'text/html' in content_type or (
            isinstance(content, (bytes, bytearray)) and b'<html' in content[:400].lower()
        )

        if is_html:
            txt = content.decode('utf-8', errors='ignore')
            m = (
                re.search(r'FileGetUrl"\s*:\s*"([^"]+)"', txt)
                or re.search(r'FileUrlNoAuth"\s*:\s*"([^"]+)"', txt)
            )
            if m:
                download_url = m.group(1)
                download_url = download_url.replace('\\u0026', '&').replace('\\/', '/')
                download_url = html_module.unescape(download_url)
                r2 = requests.get(download_url, timeout=30, allow_redirects=True)
                r2.raise_for_status()
                with open(dest_path, 'wb') as fh:
                    fh.write(r2.content)
                return dest_path
            else:
                with open(dest_path, 'wb') as fh:
                    fh.write(content)
                return dest_path
        else:
            with open(dest_path, 'wb') as fh:
                fh.write(content)
            return dest_path
    except Exception:
        return None


# ===========================================================================
# 2. CACHÉ LOCAL (PICKLE)
# ===========================================================================

def save_cached_data(df_bd, df_forma9, fecha_eval, reporte_runes, historico, reporte_fallas, fecha_ini=None) -> bool:
    """Guarda los DataFrames y variables clave en un archivo pickle."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            'df_bd': df_bd,
            'df_forma9': df_forma9,
            'fecha_evaluacion': fecha_eval,
            'fecha_inicio': fecha_ini,
            'reporte_runes': reporte_runes,
            'historico_run_life': historico,
            'reporte_fallas': reporte_fallas,
        }
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        print(f"Error guardando caché: {e}")
        return False


def load_cached_data():
    """Carga los datos desde el archivo pickle si existe. Retorna None si no hay caché."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
        if 'fecha_inicio' not in data and 'fecha_evaluacion' in data:
            import pandas as pd
            try:
                data['fecha_inicio'] = (pd.to_datetime(data['fecha_evaluacion']) - pd.DateOffset(years=1)).date()
            except Exception:
                data['fecha_inicio'] = None
        return data
    except Exception as e:
        print(f"Error cargando caché: {e}")
        return None


# ===========================================================================
# 3. LECTURA Y LIMPIEZA DE ARCHIVOS
# ===========================================================================

@st.cache_data
def find_header(file_obj, keywords, max_rows: int = 50):
    """
    Busca la fila del encabezado que contiene todas las palabras clave dadas.
    Retorna el índice de la fila (int) o None si no se encontró.
    """
    file_obj.seek(0)
    name = getattr(file_obj, 'name', '')
    ext = name.split('.')[-1].lower() if '.' in name else ''
    
    try:
        if ext in ['xlsx', 'xlsm', 'xlsb', 'xls']:
            df_chunk = pd.read_excel(file_obj, header=None, nrows=max_rows)
        else:
            file_obj.seek(0)
            df_chunk = pd.read_csv(
                file_obj, header=None, nrows=max_rows, 
                encoding='latin1', on_bad_lines='skip',
                sep=None, engine='python'
            )
    except Exception as e:
        print(f"Error en find_header (lectura): {e}")
        file_obj.seek(0)
        return None

    def _norm(s):
        if not isinstance(s, str): s = str(s)
        return " ".join(re.sub(r'[^A-Z0-9]', ' ', s.upper()).split())

    norm_keywords = [_norm(k) for k in keywords]

    for i, row in df_chunk.iterrows():
        row_cols = [_norm(c) for c in row.tolist() if pd.notna(c)]
        if all(any(nk in col for col in row_cols) for nk in norm_keywords):
            file_obj.seek(0)
            return i

    file_obj.seek(0)
    return None



@st.cache_data
def cargar_y_limpiar_datos(forma9_file, bd_file):
    """
    Carga y limpia los DataFrames de FORMA 9 y BD.
    Estandariza nombres de columnas y tipos de datos.
    Retorna (df_forma9, df_bd) o (None, None) si hay error.
    """
    if forma9_file is None or bd_file is None:
        return None, None

    # --- Persistent JSON Cache check ---
    f9_hash, bd_hash = "", ""
    cache_f9, cache_bd = None, None
    try:
        forma9_file.seek(0)
        forma9_bytes = forma9_file.read()
        f9_hash = hashlib.sha256(forma9_bytes).hexdigest()
        forma9_file.seek(0)

        bd_file.seek(0)
        bd_bytes = bd_file.read()
        bd_hash = hashlib.sha256(bd_bytes).hexdigest()
        bd_file.seek(0)

        CACHE_DIR.mkdir(exist_ok=True)
        cache_f9 = CACHE_DIR / f"clean_f9_{f9_hash}.json"
        cache_bd = CACHE_DIR / f"clean_bd_{bd_hash}.json"

        if cache_f9.exists() and cache_bd.exists():
            df_forma9 = pd.read_json(cache_f9)
            df_bd = pd.read_json(cache_bd)

            # Convert date columns back to datetime
            df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
            df_bd['FECHA_RUN'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')
            df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
            df_bd['FECHA_PULL'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce')

            return df_forma9, df_bd
    except Exception:
        pass

    try:
        forma9_header_row = find_header(forma9_file, ['FECHA', 'DIAS', 'POZO'])
        if forma9_header_row is None:
            st.error("No se pudo encontrar el encabezado en FORMA 9. Revisa las columnas 'FECHA', 'DIAS' y 'POZO'.")
            return None, None

        bd_header_row = find_header(bd_file, ['RUN', 'FECHA RUN', 'POZO'])
        if bd_header_row is None:
            st.error("No se pudo encontrar el encabezado en BD. Revisa las columnas '# RUN', 'FECHA RUN' y 'POZO'.")
            return None, None

        if forma9_file.name.endswith('.csv'):
            df_forma9 = pd.read_csv(forma9_file, header=forma9_header_row, encoding='latin1', low_memory=False)
        else:
            df_forma9 = pd.read_excel(forma9_file, header=forma9_header_row)

        if bd_file.name.endswith('.csv'):
            df_bd = pd.read_csv(bd_file, header=bd_header_row, encoding='latin1', low_memory=False)
        else:
            df_bd = pd.read_excel(bd_file, header=bd_header_row)

    except Exception as e:
        st.error(f"Error al leer los archivos: {e}")
        return None, None

    # --- Limpieza FORMA 9 ---
    df_forma9.columns = [
        " ".join(re.sub(r'[^A-Z0-9]', ' ', str(col).upper()).split()).replace('POZO NO', 'POZO')
        for col in df_forma9.columns
    ]
    fecha_col_forma9 = next((col for col in df_forma9.columns if 'FECHA' in col), None)
    dias_col         = next((col for col in df_forma9.columns if 'DIAS'  in col), None)
    pozo_col_forma9  = next((col for col in df_forma9.columns if 'POZO'  in col), None)

    df_forma9.rename(columns={
        fecha_col_forma9: 'FECHA_FORMA9',
        dias_col:         'DIAS TRABAJADOS',
        pozo_col_forma9:  'POZO',
    }, inplace=True)
    df_forma9['FECHA_FORMA9']    = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
    df_forma9['DIAS TRABAJADOS'] = pd.to_numeric(df_forma9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
    df_forma9.dropna(subset=['FECHA_FORMA9', 'POZO'], inplace=True)

    # --- Limpieza BD ---
    df_bd.columns = [
        " ".join(re.sub(r'[^A-Z0-9]', ' ', str(col).upper()).split())
        for col in df_bd.columns
    ]
    run_col_bd       = next((col for col in df_bd.columns if 'RUN'             in col), None)
    fecha_run_col    = next((col for col in df_bd.columns if 'FECHA RUN'       in col), None)
    pozo_col_bd      = next((col for col in df_bd.columns if 'POZO'            in col), None)
    fecha_falla_col  = next((col for col in df_bd.columns if 'FECHA FALLA'     in col), None)
    fecha_pull_col   = next((col for col in df_bd.columns if 'FECHA PULL'      in col), None)
    operando_col     = next((col for col in df_bd.columns if 'OPERANDO'        in col), None)
    indicador_col    = next((col for col in df_bd.columns if 'INDICADOR MTBF'  in col), None)
    proveedor_col    = next((col for col in df_bd.columns if 'PROVEEDOR'       in col), None)
    als_col          = next((col for col in df_bd.columns if 'ALS'             in col), None)
    activo_col       = next((col for col in df_bd.columns if 'ACTIVO'          in col), None)
    severidad_col    = next((col for col in df_bd.columns if 'SEVERIDAD'       in col.upper()), None)

    df_bd.rename(columns={
        run_col_bd:      'RUN',
        fecha_run_col:   'FECHA_RUN',
        fecha_falla_col: 'FECHA_FALLA',
        fecha_pull_col:  'FECHA_PULL',
        operando_col:    'OPERANDO_ESTADO',
        indicador_col:   'INDICADOR_MTBF',
        pozo_col_bd:     'POZO',
        proveedor_col:   'PROVEEDOR',
        als_col:         'ALS',
        activo_col:      'ACTIVO',
        severidad_col:   'SEVERIDAD',
    }, inplace=True)

    df_bd['FECHA_RUN']       = pd.to_datetime(df_bd['FECHA_RUN'],   errors='coerce')
    df_bd['FECHA_FALLA']     = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    df_bd['FECHA_PULL']      = pd.to_datetime(df_bd['FECHA_PULL'],  errors='coerce')
    df_bd['INDICADOR_MTBF']  = pd.to_numeric(df_bd['INDICADOR_MTBF'], errors='coerce').fillna(0)

    # Considerar 'ALS fondo' en la columna 'RAZON PULL NUEVA CATEGORIZACION' como falla atribuida a ALS (INDICADOR_MTBF = 1)
    razon_col = 'RAZON PULL NUEVA CATEGORIZACION'
    if razon_col in df_bd.columns:
        cond_als_fondo = df_bd[razon_col].astype(str).str.strip().str.upper() == 'ALS FONDO'
        df_bd.loc[cond_als_fondo, 'INDICADOR_MTBF'] = 1

    if 'SEVERIDAD' in df_bd.columns:
        df_bd['SEVERIDAD'] = pd.to_numeric(df_bd['SEVERIDAD'], errors='coerce').fillna(0)
    else:
        st.warning("Columna 'SEVERIDAD' no encontrada en el archivo BD.")
        df_bd['SEVERIDAD'] = np.nan

    df_bd.dropna(subset=['FECHA_RUN', 'POZO'], inplace=True)

    # Filtrar 'ECUADOR' ya que el usuario indica que ya no existe
    if 'ACTIVO' in df_bd.columns:
        df_bd = df_bd[df_bd['ACTIVO'].astype(str).str.upper().str.strip() != 'ECUADOR'].copy()

    # Save to JSON cache
    if cache_f9 and cache_bd:
        try:
            df_forma9.to_json(cache_f9, date_format='iso', orient='records')
            df_bd.to_json(cache_bd, date_format='iso', orient='records')
        except Exception:
            pass

    return df_forma9, df_bd


# ===========================================================================
# 4. NORMALIZACIÓN DE ARCHIVOS (string path → BytesIO)
# ===========================================================================

def normalize_file(f):
    """
    Convierte una ruta (str) a BytesIO con atributo .name.
    Si ya es un UploadedFile o similar, lo retorna tal cual.
    Retorna None si no se pudo procesar.
    """
    if f is None:
        return None
    if isinstance(f, str):
        try:
            opened_path = None
            try:
                with open(f, 'rb') as fh:
                    data = fh.read()
                opened_path = f
            except FileNotFoundError:
                candidates = [
                    os.path.join(os.getcwd(), f),
                    os.path.join(os.getcwd(), 'saved_uploads', f),
                ]
                for c in candidates:
                    if os.path.exists(c):
                        with open(c, 'rb') as fh:
                            data = fh.read()
                        opened_path = c
                        break
                else:
                    raise FileNotFoundError(f"Archivo no encontrado en rutas esperadas: {f}")
            bio = io.BytesIO(data)
            bio.name = opened_path or f
            return bio
        except Exception as e:
            st.error(f"No se pudo leer el archivo local '{f}': {e}")
            return None
    return f
