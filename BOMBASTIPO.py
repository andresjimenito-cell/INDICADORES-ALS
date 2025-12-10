"""
BOMBASTIPO.py
Script para extraer estadísticas de bombas y accesorios por CAMPO
Uso:
    python BOMBASTIPO.py --bd path/to/bd.xlsx --output resumen.csv

Salida: prints resumen y guarda CSVs con detalles en carpeta `bomp_out` (por defecto).

Requisitos: pandas, numpy, openpyxl, requests, streamlit (para la UI)
"""
import argparse
import os
import re
import tempfile
import json
import requests
import html
import sys # Necesario para la lógica de ejecución

from collections import Counter
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def show_streamlit_ui():
    # Intenta importar Streamlit solo cuando se llama a esta función
    try:
        import streamlit as st
    except ImportError:
        print('Streamlit no está instalado en este entorno.')
        return

    # Colocar la app en modo ancho
    st.set_page_config(page_title='BOMBASTIPO', layout='wide')
    st.title('BOMBASTIPO — Estadísticas de Bombas por Campo')
    st.markdown('Carga la BD (.csv/.xlsx) por archivo o pega la URL (OneDrive/SharePoint). Selecciona filtros y luego pulsa **Generar estadísticas**.')

    # Primera fila: uploader + URL + opciones
    top_cols = st.columns([1.5, 1.5, 1])
    uploaded = top_cols[0].file_uploader('Sube BD (.csv/.xlsx)', type=['csv', 'xlsx'])
    default_url = 'https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=MOmxMR'
    url = top_cols[1].text_input('O pega la URL pública de la BD (OneDrive)', value=default_url)
    auto_load = top_cols[2].checkbox('Cargar automáticamente desde URL', value=True)

    # Guardar JSON opción y nota de carpeta (no pedir ruta)
    meta_cols = st.columns([1, 1, 2])
    save_json_chk = meta_cols[0].checkbox('Guardar JSON (opcional)', value=False)
    st.write('Los CSV se guardan internamente (carpeta `bomp_out`) y también puedes descargar desde la UI.')

    # Mantener DataFrame en sesión para evitar que la interfaz vuelva al inicio
    if 'df' not in st.session_state:
        st.session_state['df'] = None
        st.session_state['bd_name'] = None

    # Cargar DataFrame cuando se sube archivo o cuando se usa URL con auto_load
    bd_loaded = False
    if uploaded is not None:
        tmpdir = tempfile.mkdtemp()
        fname = os.path.join(tmpdir, uploaded.name)
        with open(fname, 'wb') as fh:
            fh.write(uploaded.getvalue())
        try:
            st.session_state['df'] = read_bd(fname)
            st.session_state['bd_name'] = uploaded.name
            bd_loaded = True
            st.success(f'Archivo subido: {uploaded.name} — {st.session_state["df"].shape[0]} filas')
        except Exception as e:
            st.error(f'Error leyendo el archivo subido: {e}')
    elif url and auto_load and (st.session_state.get('df') is None):
        # intentar descargar
        tmpdir = os.path.join(os.getcwd(), 'saved_uploads')
        os.makedirs(tmpdir, exist_ok=True)
        fname = os.path.join(tmpdir, 'bd_online.xlsx')
        try:
            def _download_onedrive(url, dest_path):
                r = requests.get(url, timeout=30, allow_redirects=True)
                r.raise_for_status()
                content_type = r.headers.get('content-type','')
                content = r.content
                is_html = 'text/html' in content_type or (isinstance(content, (bytes,bytearray)) and b'<html' in content[:400].lower())
                if is_html:
                    txt = content.decode('utf-8', errors='ignore')
                    m = re.search(r'FileGetUrl"\s*:\s*\"([^\"]+?)\"', txt) or re.search(r'FileUrlNoAuth"\s*:\s*\"([^\"]+?)\"', txt)
                    if m:
                        download_url = m.group(1).replace('\\u0026', '&').replace('\\/', '/')
                        download_url = html.unescape(download_url)
                        r2 = requests.get(download_url, timeout=30, allow_redirects=True)
                        r2.raise_for_status()
                        with open(dest_path, 'wb') as fh:
                            fh.write(r2.content)
                        return True
                    else:
                        with open(dest_path, 'wb') as fh:
                            fh.write(content)
                        return True
                else:
                    with open(dest_path, 'wb') as fh:
                        fh.write(content)
                    return True

            ok = _download_onedrive(url, fname)
            if ok:
                st.session_state['df'] = read_bd(fname)
                st.session_state['bd_name'] = os.path.basename(fname)
                bd_loaded = True
                st.success(f'BD descargada: {st.session_state["bd_name"]} — {st.session_state["df"].shape[0]} filas')
            else:
                st.error('No se pudo descargar la BD desde la URL proporcionada.')
        except Exception as e:
            st.error(f'Error al descargar BD: {e}')

    if st.session_state.get('df') is not None:
        df = st.session_state['df']
        # Preparar opciones de filtros
        cols = list(df.columns)
        campo_col = find_column(cols, ['CAMPO']) or find_column(cols, ['ACTIVO']) or 'CAMPO_TEMP'
        if campo_col not in df.columns:
            df['CAMPO_TEMP'] = 'SIN CAMPO'
            campo_col = 'CAMPO_TEMP'

        # detectar columna activo de forma tolerante
        activo_col = get_column(df, ['ACTIVO', 'ASSET', 'ASSET ID', 'ACTIVO ID', 'WELL', 'POZO'])
        if not activo_col:
            for c in cols:
                cu = c.upper()
                if 'ACTIV' in cu or 'ASSET' in cu or 'POZO' in cu:
                    activo_col = c
                    break

        # aplicar filtro RUNNING por defecto para la lista previa
        pull_col = find_column(cols, ['FECHA DE PULL', 'PULL', 'FECHA PULL', 'PULL STATUS', 'STATUS PULL'])
        df_filtered = df
        if pull_col and pull_col in df.columns:
            try:
                mask = df[pull_col].astype(str).str.upper().str.contains(r'\bRUN\b|\bRUNNING\b')
                df_filtered = df[mask]
            except Exception:
                df_filtered = df

        # opciones
        campos = sorted(list(set(df_filtered[campo_col].dropna().astype(str).tolist())))
        activos = []
        if activo_col and activo_col in df_filtered.columns:
            activos = sorted(list(set(df_filtered[activo_col].dropna().astype(str).tolist())))

        # Mostrar filtros distribuidos horizontalmente
        fcols = st.columns([1.5, 1.5, 1])
        periodo = fcols[0].radio('Periodo', ['Todos', 'Último año', 'Últimos 2 años'], index=0)
        sel_campo = fcols[1].selectbox('Selecciona un Campo', ['--Todos--'] + campos, key='sel_campo')
        # activos filtrados en función del campo seleccionado
        if activo_col and activo_col in df_filtered.columns:
            if sel_campo != '--Todos--':
                activos_filtrados = sorted(list(set(df_filtered[df_filtered[campo_col].astype(str) == str(sel_campo)][activo_col].dropna().astype(str).tolist())))
            else:
                activos_filtrados = activos
        else:
            activos_filtrados = []
        sel_activo = fcols[2].selectbox('Selecciona un Activo', ['--Todos--'] + activos_filtrados, key='sel_activo') if activos_filtrados else '--Todos--'

        # Botón para generar resultados (NO se ejecuta por cambios en selectboxes)
        run_col = st.columns([1, 3])
        with run_col[0]:
            run = st.button('Generar estadísticas')

        # Si se pulsa, generar y mostrar resultados debajo
        if run:
            # mapear periodo a years
            years = None
            if periodo == 'Último año':
                years = 1
            elif periodo == 'Últimos 2 años':
                years = 2

            # aplicar filtros combinados sobre df_filtered
            df_selected = df_filtered
            if sel_campo != '--Todos--':
                df_selected = df_selected[df_selected[campo_col].astype(str) == str(sel_campo)]
            if sel_activo != '--Todos--' and activo_col and activo_col in df_selected.columns:
                df_selected = df_selected[df_selected[activo_col].astype(str) == str(sel_activo)]

            # generar resumen y guardar outputs
            try:
                # Si el usuario seleccionó un Activo, agrupar por activo; si no, por campo
                if sel_activo != '--Todos--' and activo_col and activo_col in df.columns:
                    resumen_sel = estadisticas_por_grupo(df_selected, activo_col, years=years)
                else:
                    resumen_sel = estadisticas_por_campo(df_selected, years=years)

                outdir = 'bomp_out'
                csv_paths = save_csvs(outdir, resumen_sel)
                # Si estamos en Streamlit y existe el Excel resumen, ofrecer descarga
                try:
                    if 'summary_excel' in csv_paths:
                        with open(csv_paths['summary_excel'], 'rb') as fh:
                            data = fh.read()
                        st.download_button('Descargar resumen (Excel)', data, file_name=os.path.basename(csv_paths['summary_excel']), mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    elif 'summary_csv' in csv_paths:
                        with open(csv_paths['summary_csv'], 'rb') as fh:
                            data = fh.read()
                        st.download_button('Descargar resumen (CSV)', data, file_name=os.path.basename(csv_paths['summary_csv']), mime='text/csv')
                except Exception:
                    pass
                if save_json_chk:
                    save_json(outdir, resumen_sel, 'bomp_resumen.json')
                st.success('Estadísticas generadas')
                # No mostrar botones de descarga (pedido del usuario)
                st.info(f"CSV generados en carpeta interna: {os.path.abspath(outdir)}")

                # Mostrar datos en 3 columnas: izquierda=tablas, medio=gráficas, derecha=recomendación
                for key, info in resumen_sel.items():
                    info = info or ({'pumps_top': {}, 'motor_types': {}, 'cable_awg': {}, 'ytool': {}, 'vsd_kva': {}})
                    st.markdown(f'## Resultados — {key}')
                    c_left, c_mid, c_right = st.columns([1.1, 1.4, 0.8])

                    # Preparar datos/tablas
                    pumps = info.get('pumps_top', {}) or {}
                    motors = info.get('motor_types', {}) or {}
                    awg = info.get('cable_awg', {}) or {}
                    ytool = info.get('ytool', {}) or {}
                    vsd = info.get('vsd_kva', {}) or {}

                    # LEFT: tablas (usar tablas por defecto de Streamlit — compactas y claras)
                    with c_left:
                        st.subheader('Tablas')
                        if pumps:
                            dfp = pd.DataFrame([{'modelo': k, 'count': v.get('count', v) if isinstance(v, dict) else v,
                                                 'min_bbl': v.get('min_bbl') if isinstance(v, dict) else None,
                                                 'max_bbl': v.get('max_bbl') if isinstance(v, dict) else None}
                                                for k, v in pumps.items()])
                            st.markdown('**Bombas (Top)**')
                            st.dataframe(dfp.sort_values('count', ascending=False), use_container_width=True)
                        else:
                            st.write('Bombas: No disponible')

                        if motors:
                            dfm = pd.DataFrame(list(motors.items()), columns=['motor', 'count']).sort_values('count', ascending=False)
                            st.markdown('**Motores**')
                            st.dataframe(dfm, use_container_width=True)
                        else:
                            st.write('Motores: No disponible')

                        if awg:
                            dfc = pd.DataFrame(list(awg.items()), columns=['awg', 'count']).sort_values('count', ascending=False)
                            st.markdown('**AWG**')
                            st.dataframe(dfc, use_container_width=True)
                        else:
                            st.write('AWG: No disponible')

                        if ytool:
                            dfy = pd.DataFrame(list(ytool.items()), columns=['valor', 'count'])
                            st.markdown('**Y-Tool**')
                            st.dataframe(dfy, use_container_width=True)
                        else:
                            st.write('Y-Tool: No disponible')

                        if vsd:
                            df_vs = pd.DataFrame([{'kva': k, 'count': int(v)} for k, v in vsd.items()]).sort_values('count', ascending=False)
                            st.markdown('**VSD KVA**')
                            st.dataframe(df_vs, use_container_width=True)
                        else:
                            st.write('VSD KVA: No disponible')

                    # MIDDLE: gráficas (compactas)
                    with c_mid:
                        st.subheader('Gráficas')
                        compact_height = 260
                        if pumps:
                            try:
                                fig = px.bar(dfp.sort_values('count', ascending=True), x='count', y='modelo', orientation='h',
                                             color='count', color_continuous_scale='Viridis', title='Frecuencia de modelos')
                                fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=6), height=compact_height)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                pass
                        if motors:
                            try:
                                fig = px.pie(dfm, names='motor', values='count', title='Distribución de tipos de motor')
                                fig.update_layout(margin=dict(t=20, b=6), height=compact_height)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                pass
                        if awg:
                            try:
                                fig = px.bar(dfc.sort_values('count', ascending=False), x='awg', y='count', title='AWG más comunes',
                                             color='count', color_continuous_scale='Blues')
                                fig.update_layout(margin=dict(t=20, b=6), height=compact_height)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                pass
                        if ytool:
                            try:
                                fig = px.pie(dfy, names='valor', values='count', title='Y-Tool (SI/NO)')
                                fig.update_layout(margin=dict(t=20, b=6), height=compact_height)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                pass
                        if vsd:
                            try:
                                fig = px.bar(df_vs.sort_values('count', ascending=False), x='kva', y='count', title='VSD KVA',
                                             color='count', color_continuous_scale='Reds')
                                fig.update_layout(margin=dict(t=20, b=6), height=compact_height)
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception:
                                pass

                    # RIGHT: Recomendación estructurada en tabla
                    with c_right:
                        rec_items = []
                        if pumps:
                            top_pump, top_pump_val = max(pumps.items(), key=lambda x: x[1]['count'] if isinstance(x[1], dict) else x[1])
                            rec_items.append(('Bomba', top_pump))
                            if isinstance(top_pump_val, dict):
                                mi = top_pump_val.get('min_bbl'); ma = top_pump_val.get('max_bbl')
                                if mi is not None or ma is not None:
                                    rec_items.append(('Rango caudal (bbl)', f"{mi if mi is not None else '?'} - {ma if ma is not None else '?'}"))
                        if motors:
                            top_motor = max(motors.items(), key=lambda x: x[1])[0]
                            rec_items.append(('Motor', top_motor))
                        if ytool:
                            top_y = max(ytool.items(), key=lambda x: x[1])[0]
                            rec_items.append(('Y-Tool', top_y))
                        if vsd:
                            top_v = max(vsd.items(), key=lambda x: x[1])[0]
                            rec_items.append(('VSD KVA', top_v))
                        if awg:
                            top_awg = max(awg.items(), key=lambda x: x[1])[0]
                            rec_items.append(('AWG', top_awg))

                            # Agregar longitud promedio de cable a recomendaciones si está disponible
                            cl = info.get('cable_length_mean')
                            if cl is not None:
                                try:
                                    cl_fmt = round(float(cl), 2)
                                except Exception:
                                    cl_fmt = cl
                                rec_items.append(('Longitud cable (promedio)', f"{cl_fmt}"))

                        if rec_items:
                            rec_df = pd.DataFrame(rec_items, columns=['Ítem', 'Recomendación'])
                            st.markdown(f"### ✅ Recomendación diseño para campo: **{key}**")
                            # Mostrar con st.table para apariencia compacta y ordenada
                            st.table(rec_df)
                            st.markdown('_Sugerencia rápida basada en los datos disponibles. Verificar en campo antes de aplicar._')
                        else:
                            st.write('Sin recomendaciones disponibles')
            except Exception as e:
                st.error(f'Error procesando BD: {e}')


# --- 2. Funciones de Procesamiento de Datos ---

def read_bd(path):
    """
    Lee un archivo .csv o .xlsx y normaliza nombres de columnas (uppercase, remove dots/#).
    """
    if path is None:
        raise ValueError("Se requiere la ruta del archivo BD")

    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    # Leer sin encabezado para detectar filas de encabezado reales
    try:
        if path.lower().endswith('.csv'):
            raw = pd.read_csv(path, header=None, encoding='latin1', low_memory=False, on_bad_lines='skip')
        else:
            raw = pd.read_excel(path, header=None)
    except Exception:
        # último recurso: lectura directa con pandas
        if path.lower().endswith('.csv'):
            return pd.read_csv(path, encoding='latin1', low_memory=False)
        else:
            return pd.read_excel(path)

    # Detectar fila de encabezado principal buscando palabras clave típicas
    keywords = ['RUN', 'FECHA', 'POZO', 'ID', 'WELL', 'POZO']
    header_row = None
    maxrows = min(50, raw.shape[0])
    for i in range(maxrows):
        row_vals = raw.iloc[i].astype(str).str.upper().tolist()
        # si la fila contiene varias de las keywords, la consideramos header
        hits = sum(1 for k in keywords if any(k in (c or '') for c in row_vals))
        if hits >= 2:
            header_row = i
            break

    if header_row is None:
        # fallback: primer fila no vacía
        for i in range(maxrows):
            if not raw.iloc[i].dropna().empty:
                header_row = i
                break

    if header_row is None:
        # No se detectó, leer con el primer renglón como encabezado
        if path.lower().endswith('.csv'):
            df = pd.read_csv(path, encoding='latin1', low_memory=False)
        else:
            df = pd.read_excel(path)
        df.columns = [str(c).upper().strip().replace('#', '').replace('.', '').strip() for c in df.columns]
        return df

    # Determinar si existe una fila de subtítulos justo debajo del header_row
    subtitle_row = header_row + 1 if header_row + 1 < raw.shape[0] else None
    use_multi = False
    if subtitle_row is not None:
        sub = raw.iloc[subtitle_row]
        # Contar celdas con texto no numérico en subtítulo
        text_like = 0
        non_null = 0
        for v in sub:
            if pd.isna(v):
                continue
            non_null += 1
            sval = str(v).strip()
            if sval == '':
                continue
            # si contiene letras o símbolos comunes de subtítulos (/, -), lo contamos
            if re.search(r'[A-Za-zÁÉÍÓÚÑáéíóúñ/]', sval):
                text_like += 1
        if non_null > 0 and (text_like / non_null) >= 0.3:
            use_multi = True

    # Leer el dataframe con el header detectado (simple o multirow)
    try:
        if path.lower().endswith('.csv'):
            if use_multi:
                df = pd.read_csv(path, header=[header_row, subtitle_row], encoding='latin1', low_memory=False, on_bad_lines='skip')
            else:
                df = pd.read_csv(path, header=header_row, encoding='latin1', low_memory=False, on_bad_lines='skip')
        else:
            if use_multi:
                df = pd.read_excel(path, header=[header_row, subtitle_row])
            else:
                df = pd.read_excel(path, header=header_row)
    except Exception:
        # Si falla la lectura con multi-header, intentar lectura simple
        if path.lower().endswith('.csv'):
            df = pd.read_csv(path, header=header_row, encoding='latin1', low_memory=False, on_bad_lines='skip')
        else:
            df = pd.read_excel(path, header=header_row)

    # Si tenemos MultiIndex en columnas, aplanar combinando categoria + subtitulo
    if isinstance(df.columns, pd.MultiIndex):
        new_cols = []
        for col in df.columns:
            parts = [str(p).strip() for p in col if str(p).strip().lower() not in ('nan', '')]
            if len(parts) == 0:
                new = ''
            else:
                new = ' '.join(parts)
            new_cols.append(new)
        df.columns = new_cols

    # Normalizar columnas: mayúsculas, eliminar símbolos problemáticos
    df.columns = [re.sub(r'[\#\.]', '', str(c)).upper().strip() for c in df.columns]

    return df


def find_column(cols, patterns):
    """Devuelve el nombre de columna que mejor coincida con alguna de las patterns (lista de substrings, mayúsculas)."""
    cols_up = [c.upper() for c in cols]
    # patterns may be list of candidate substrings (already upper/lower agnostic)
    for pat in patterns:
        pat_up = pat.upper()
        for c in cols:
            cu = c.upper()
            if pat_up in cu:
                return c

    # fallback: try each word in each pattern
    for pat in patterns:
        for word in pat.split():
            w = word.strip().upper()
            if not w:
                continue
            for c in cols:
                if w in c.upper():
                    return c
    return None


def get_column(df, candidates):
    """Retorna el nombre de columna del dataframe que coincida con cualquiera de los candidatos.
    candidates: lista de strings (substrings probables)."""
    cols = list(df.columns)
    for cand in candidates:
        col = find_column(cols, [cand])
        if col:
            return col
    return None


def parse_pump_model(model_str):
    """
    Intenta extraer rango (min,max) o valor "nominal" desde nombres de modelos.
    """
    if pd.isna(model_str):
        return (None, None)
    s = str(model_str).upper()
    m = re.search(r"(\d{2,5})\s*-\s*(\d{2,5})", s)
    if m:
        a = int(m.group(1))
        b = int(m.group(2))
        return (min(a, b), max(a, b))
    m2 = re.search(r"\((\d{2,5})\s*[-–]\s*(\d{2,5})\)", s)
    if m2:
        a = int(m2.group(1)); b = int(m2.group(2))
        return (min(a,b), max(a,b))
    nums = re.findall(r"\d{2,5}", s)
    if nums:
        vals = [int(x) for x in nums]
        if len(vals) >= 2:
            a = min(vals); b = max(vals)
            if a > 2000 and a % 10 == 0: a = a // 10
            if b > 2000 and b % 10 == 0: b = b // 10
            return (min(a,b), max(a,b))
        else:
            v = vals[0]
            if v > 2000 and v % 10 == 0:
                v = v // 10
            return (v, v)
    return (None, None)


def extract_awg(s):
    """Extrae valor AWG de una cadena (ej: 'AWG 10', '#10', '10 AWG', '10/0')"""
    if pd.isna(s):
        return None
    ss = str(s).upper()
    m = re.search(r"AWG\s*#?\s*(\d{1,3}(?:/\d)?)", ss)
    if m:
        return m.group(1)
    m2 = re.search(r"#\s*(\d{1,3}(?:/\d)?)\b", ss)
    if m2:
        return m2.group(1)
    m3 = re.search(r"(\d{1,3}(?:/\d)?)\s*AWG\b", ss)
    if m3:
         return m3.group(1)
    m4 = re.search(r"\b(\d{1,3}(?:/\d)?)\b", ss)
    if m4:
        return m4.group(1)
    return None


def parse_yes_no(val):
    if pd.isna(val):
        return None
    s = str(val).strip().upper()
    if s in ('YES', 'Y', 'SI', 'S', 'TRUE', '1'):
        return 'YES'
    if s in ('NO', 'N', 'FALSE', '0'):
        return 'NO'
    return s


def parse_kva(val):
    if pd.isna(val):
        return None
    s = str(val)
    m = re.search(r"(\d+[\.,]?\d*)", s)
    if m:
        v = m.group(1).replace(',', '.')
        try:
            return float(v)
        except Exception:
            return None
    return None


def estadisticas_por_campo(df, years=None):
    """
    Genera un diccionario con las estadísticas solicitadas por campo.
    """
    cols = list(df.columns)
    campo_col = find_column(cols, ['CAMPO']) or find_column(cols, ['ACTIVO']) or 'CAMPO_TEMP'

    # Filtrar filas por estado RUNNING en columna de Pull (ej: 'FECHA DE PULL' o 'PULL')
    pull_col = find_column(cols, ['FECHA DE PULL', 'PULL', 'FECHA PULL', 'PULL STATUS', 'STATUS PULL'])
    df_filtered = df
    if pull_col and pull_col in df.columns:
        try:
            mask = df[pull_col].astype(str).str.upper().str.contains(r'\bRUN\b|\bRUNNING\b')
            df_filtered = df[mask]
        except Exception:
            df_filtered = df
    else:
        # si no existe columna de pull, dejamos df sin filtrar
        df_filtered = df

    # Filtrar por periodo (años) si se solicita: buscar columna de fecha y filtrar rows recientes
    def _filter_by_years(df_in, years):
        if not years:
            return df_in
        date_col = find_column(list(df_in.columns), ['FECHA DE PULL', 'PULL DATE', 'FECHA', 'DATE', 'FECHA_PULL'])
        if not date_col or date_col not in df_in.columns:
            return df_in
        try:
            dates = pd.to_datetime(df_in[date_col], errors='coerce', dayfirst=True)
            cutoff = pd.Timestamp.now() - pd.DateOffset(years=years)
            return df_in[dates >= cutoff]
        except Exception:
            return df_in

    # Mejor detección de columnas usando candidatos explícitos
    pump_col = get_column(df, ['PUMP UPPER MODELO', 'PUMP UPPER MODEL', 'PUMP UPPER', 'PUMP MODEL', 'PUMP', 'BOMBA', 'MODELO', 'MODEL'])
    # Detección robusta para columna de motores: preferir 'TEC.MOTOR' o columnas que contengan TEC + MOTOR/MOTORES
    motor_col = None
    if 'TEC.MOTOR' in df.columns:
        motor_col = 'TEC.MOTOR'
    else:
        candidates = [c for c in df.columns if 'TEC' in c.upper() and ('MOTOR' in c.upper() or 'MOTORES' in c.upper())]
        # preferir candidate que incluya subtítulo AM/PMM
        preferred = None
        for c in candidates:
            cu = c.upper()
            if 'AM' in cu or 'PMM' in cu or 'AM/PMM' in cu or 'AM PMM' in cu:
                preferred = c
                break
        if preferred:
            motor_col = preferred
        elif candidates:
            motor_col = candidates[0]
        else:
            # fallback a la búsqueda por nombre más genérica
            motor_col = get_column(df, ['TEC.MOTOR', 'TEC MOTOR', 'MOTOR', 'MOTOR TIPO', 'TIPO MOTOR'])

    # Buscar columna de cable AWG (preferencia: contiene both 'CABLE' and 'AWG')
    cable_col = None
    for c in df.columns:
        cu = c.upper()
        if 'CABLE' in cu and 'AWG' in cu:
            cable_col = c
            break
    if cable_col is None:
        cable_col = get_column(df, ['CABLE (FONDO)', 'CABLE FONDO', 'CABLE', 'CABLE(FONDO)', 'AWG'])

    ytool_col = get_column(df, ['Y-TOOL', 'YTOOL', 'Y TOOL'])

    # Buscar VSD KVA (preferencia 'VSD' and 'KVA')
    vsd_col = None
    for c in df.columns:
        cu = c.upper()
        if 'VSD' in cu and 'KVA' in cu:
            vsd_col = c
            break
    if vsd_col is None:
        vsd_col = get_column(df, ['VSD KVA', 'VSD', 'KVA', 'VARIADOR', 'KVA VSD'])

    # Fallback por posición: cable = 5ta columna (index 4), vsd = 6ta columna (index 5)
    if cable_col is None:
        try:
            if df.shape[1] >= 5:
                cable_col = df.columns[4]
        except Exception:
            cable_col = None
    if vsd_col is None:
        try:
            if df.shape[1] >= 6:
                vsd_col = df.columns[5]
        except Exception:
            vsd_col = None

    # Detectar columna de longitud de cable para agrupamiento por grupo
    length_col = None
    for c in df.columns:
        cu = c.upper()
        if 'CABLE' in cu and 'LONGITUD' in cu:
            length_col = c
            break
    if length_col is None:
        for c in df.columns:
            cu = c.upper()
            if 'LONGITUD' in cu or 'LENGTH' in cu or 'LONG' in cu:
                length_col = c
                break
    if length_col is None:
        length_col = get_column(df, ['CABLE (FONDO) LONGITUD', 'LONGITUD', 'LENGTH'])

    # Detectar columna de longitud de cable (ej: "CABLE (FONDO) LONGITUD" o sólo "LONGITUD")
    length_col = None
    for c in df.columns:
        cu = c.upper()
        if 'CABLE' in cu and 'LONGITUD' in cu:
            length_col = c
            break
    if length_col is None:
        for c in df.columns:
            cu = c.upper()
            if 'LONGITUD' in cu or 'LENGTH' in cu or 'LONG' in cu:
                length_col = c
                break
    if length_col is None:
        length_col = get_column(df, ['CABLE (FONDO) LONGITUD', 'LONGITUD', 'LENGTH'])

    if campo_col not in df.columns:
        df['CAMPO_TEMP'] = 'SIN CAMPO'
        campo_col = 'CAMPO_TEMP'

    # Aplicar filtro de años si solicitado
    if years and isinstance(years, int) and years > 0:
        df_filtered = _filter_by_years(df_filtered, years)

    groupby = df_filtered.groupby(campo_col)
    resumen = {}

    for campo, g in groupby:
        row = {}
        if pump_col and pump_col in g.columns:
            modelos = g[pump_col].fillna('SIN MODELO').astype(str)
            top = modelos.value_counts().head(10).to_dict()
            parsed = {}
            for mod, cnt in top.items():
                mi, ma = parse_pump_model(mod)
                parsed[mod] = {'count': int(cnt), 'min_bbl': mi, 'max_bbl': ma}
            row['pumps_top'] = parsed
            row['pumps_most_used'] = modelos.value_counts().idxmax() if not modelos.empty else None
        else:
            row['pumps_top'] = {}
            row['pumps_most_used'] = None

        # Motores: extraer desde la columna detectada (preferente 'TEC.MOTOR' o 'TEC MOTORES' con subtítulo AM/PMM)
        if motor_col and motor_col in g.columns:
            motors_raw = g[motor_col].fillna('SIN_MOTOR').astype(str).str.upper().str.strip()
            # intentar extraer AM / PMM si aparecen en el texto
            extracted = motors_raw.str.extract(r'\b(AM|PMM)\b', expand=False)
            motors_final = extracted.fillna(motors_raw)
            row['motor_types'] = motors_final.value_counts().to_dict()
        else:
            row['motor_types'] = {}

        if cable_col and cable_col in g.columns:
            cables = g[cable_col].dropna().astype(str)
            awgs = [extract_awg(x) for x in cables]
            awg_cnt = Counter([a for a in awgs if a is not None])
            row['cable_awg'] = dict(awg_cnt)
        else:
            row['cable_awg'] = {}

        # Promedio de longitud de cable (por grupo)
        if length_col and length_col in g.columns:
            lens = g[length_col].dropna().astype(str).str.extract(r'(\d+[\.,]?\d*)', expand=False)
            lens = lens.str.replace(',', '.', regex=False)
            lens = pd.to_numeric(lens, errors='coerce')
            mean_len = float(lens.mean()) if not lens.empty and not lens.dropna().empty else None
            row['cable_length_mean'] = mean_len
        else:
            row['cable_length_mean'] = None

        # Promedio de longitud de cable (por campo)
        if length_col and length_col in g.columns:
            # Extraer primer número de cada celda y convertir a float (soporta ',' decimal)
            lens = g[length_col].dropna().astype(str).str.extract(r'(\d+[\.,]?\d*)', expand=False)
            lens = lens.str.replace(',', '.', regex=False)
            lens = pd.to_numeric(lens, errors='coerce')
            mean_len = float(lens.mean()) if not lens.empty and not lens.dropna().empty else None
            row['cable_length_mean'] = mean_len
        else:
            row['cable_length_mean'] = None

        if ytool_col and ytool_col in g.columns:
            yvals = g[ytool_col].apply(parse_yes_no)
            ycnt = yvals.value_counts(dropna=True).to_dict()
            row['ytool'] = {k: int(v) for k, v in ycnt.items()}
        else:
            row['ytool'] = {}

        if vsd_col and vsd_col in g.columns:
            # Obtener conteo por valor literal de la columna VSD (subtítulo KVA)
            vals = g[vsd_col].dropna().astype(str).str.strip()
            if not vals.empty:
                cnts = vals.value_counts().to_dict()
                row['vsd_kva'] = {k: int(v) for k, v in cnts.items()}
            else:
                row['vsd_kva'] = {}
        else:
            row['vsd_kva'] = {}

        resumen[campo] = row

    return resumen


def estadisticas_por_grupo(df, group_col, years=None):
    """
    Versión general que agrupa por la columna `group_col` (por ejemplo, activo) y
    devuelve el mismo formato de resumen que `estadisticas_por_campo`.
    """
    cols = list(df.columns)

    # Filtrar filas por estado RUNNING si existe columna de Pull
    pull_col = find_column(cols, ['FECHA DE PULL', 'PULL', 'FECHA PULL', 'PULL STATUS', 'STATUS PULL'])
    df_filtered = df
    if pull_col and pull_col in df.columns:
        try:
            mask = df[pull_col].astype(str).str.upper().str.contains(r'\bRUN\b|\bRUNNING\b')
            df_filtered = df[mask]
        except Exception:
            df_filtered = df

    # Filtrar por periodo si se solicita
    def _filter_by_years_local(df_in, years):
        if not years:
            return df_in
        date_col = find_column(list(df_in.columns), ['FECHA DE PULL', 'PULL DATE', 'FECHA', 'DATE', 'FECHA_PULL'])
        if not date_col or date_col not in df_in.columns:
            return df_in
        try:
            dates = pd.to_datetime(df_in[date_col], errors='coerce', dayfirst=True)
            cutoff = pd.Timestamp.now() - pd.DateOffset(years=years)
            return df_in[dates >= cutoff]
        except Exception:
            return df_in

    # Detección de columnas de interés (mismas heurísticas que en estadisticas_por_campo)
    pump_col = get_column(df, ['PUMP UPPER MODELO', 'PUMP UPPER MODEL', 'PUMP UPPER', 'PUMP MODEL', 'PUMP', 'BOMBA', 'MODELO', 'MODEL'])
    motor_col = None
    if 'TEC.MOTOR' in df.columns:
        motor_col = 'TEC.MOTOR'
    else:
        candidates = [c for c in df.columns if 'TEC' in c.upper() and ('MOTOR' in c.upper() or 'MOTORES' in c.upper())]
        preferred = None
        for c in candidates:
            cu = c.upper()
            if 'AM' in cu or 'PMM' in cu or 'AM/PMM' in cu or 'AM PMM' in cu:
                preferred = c
                break
        if preferred:
            motor_col = preferred
        elif candidates:
            motor_col = candidates[0]
        else:
            motor_col = get_column(df, ['TEC.MOTOR', 'TEC MOTOR', 'MOTOR', 'MOTOR TIPO', 'TIPO MOTOR'])

    cable_col = None
    for c in df.columns:
        cu = c.upper()
        if 'CABLE' in cu and 'AWG' in cu:
            cable_col = c
            break
    if cable_col is None:
        cable_col = get_column(df, ['CABLE (FONDO)', 'CABLE FONDO', 'CABLE', 'CABLE(FONDO)', 'AWG'])

    ytool_col = get_column(df, ['Y-TOOL', 'YTOOL', 'Y TOOL'])

    vsd_col = None
    for c in df.columns:
        cu = c.upper()
        if 'VSD' in cu and 'KVA' in cu:
            vsd_col = c
            break
    if vsd_col is None:
        vsd_col = get_column(df, ['VSD KVA', 'VSD', 'KVA', 'VARIADOR', 'KVA VSD'])

    # Fallback por posición
    if cable_col is None:
        try:
            if df.shape[1] >= 5:
                cable_col = df.columns[4]
        except Exception:
            cable_col = None
    if vsd_col is None:
        try:
            if df.shape[1] >= 6:
                vsd_col = df.columns[5]
        except Exception:
            vsd_col = None

    if years and isinstance(years, int) and years > 0:
        df_filtered = _filter_by_years_local(df_filtered, years)

    if group_col not in df_filtered.columns:
        return {}

    groupby = df_filtered.groupby(group_col)
    resumen = {}

    for key, g in groupby:
        row = {}
        if pump_col and pump_col in g.columns:
            modelos = g[pump_col].fillna('SIN MODELO').astype(str)
            top = modelos.value_counts().head(10).to_dict()
            parsed = {}
            for mod, cnt in top.items():
                mi, ma = parse_pump_model(mod)
                parsed[mod] = {'count': int(cnt), 'min_bbl': mi, 'max_bbl': ma}
            row['pumps_top'] = parsed
            row['pumps_most_used'] = modelos.value_counts().idxmax() if not modelos.empty else None
        else:
            row['pumps_top'] = {}
            row['pumps_most_used'] = None

        if motor_col and motor_col in g.columns:
            motors_raw = g[motor_col].fillna('SIN_MOTOR').astype(str).str.upper().str.strip()
            extracted = motors_raw.str.extract(r'\b(AM|PMM)\b', expand=False)
            motors_final = extracted.fillna(motors_raw)
            row['motor_types'] = motors_final.value_counts().to_dict()
        else:
            row['motor_types'] = {}

        if cable_col and cable_col in g.columns:
            cables = g[cable_col].dropna().astype(str)
            awgs = [extract_awg(x) for x in cables]
            awg_cnt = Counter([a for a in awgs if a is not None])
            row['cable_awg'] = dict(awg_cnt)
        else:
            row['cable_awg'] = {}

        if ytool_col and ytool_col in g.columns:
            yvals = g[ytool_col].apply(parse_yes_no)
            ycnt = yvals.value_counts(dropna=True).to_dict()
            row['ytool'] = {k: int(v) for k, v in ycnt.items()}
        else:
            row['ytool'] = {}

        if vsd_col and vsd_col in g.columns:
            vals = g[vsd_col].dropna().astype(str).str.strip()
            if not vals.empty:
                cnts = vals.value_counts().to_dict()
                row['vsd_kva'] = {k: int(v) for k, v in cnts.items()}
            else:
                row['vsd_kva'] = {}
        else:
            row['vsd_kva'] = {}

        resumen[key] = row

    return resumen


def save_csvs(outdir, resumen):
    """Genera CSVs por estadística a partir del resumen devuelto por `estadisticas_por_campo`.
    Devuelve dict con rutas guardadas."""
    os.makedirs(outdir, exist_ok=True)
    paths = {}

    # Pumps
    rows = []
    for campo, info in resumen.items():
        pumps = info.get('pumps_top', {}) or {}
        for modelo, d in pumps.items():
            rows.append({
                'CAMPO': campo,
                'modelo': modelo,
                'count': int(d.get('count', 0) if isinstance(d, dict) else d),
                'min_bbl': d.get('min_bbl') if isinstance(d, dict) else None,
                'max_bbl': d.get('max_bbl') if isinstance(d, dict) else None
            })
    if rows:
        df_pumps = pd.DataFrame(rows)
        ppath = os.path.join(outdir, 'pumps_by_campo.csv')
        df_pumps.to_csv(ppath, index=False, encoding='utf-8')
        paths['pumps'] = ppath

    # Motors
    rows = []
    for campo, info in resumen.items():
        motors = info.get('motor_types', {}) or {}
        for motor, cnt in motors.items():
            rows.append({'CAMPO': campo, 'motor': motor, 'count': int(cnt)})
    if rows:
        df_m = pd.DataFrame(rows)
        mpath = os.path.join(outdir, 'motors_by_campo.csv')
        df_m.to_csv(mpath, index=False, encoding='utf-8')
        paths['motors'] = mpath

    # Cable AWG
    rows = []
    for campo, info in resumen.items():
        awgs = info.get('cable_awg', {}) or {}
        for awg, cnt in awgs.items():
            rows.append({'CAMPO': campo, 'awg': awg, 'count': int(cnt)})
    if rows:
        df_c = pd.DataFrame(rows)
        cpath = os.path.join(outdir, 'cable_awg_by_campo.csv')
        df_c.to_csv(cpath, index=False, encoding='utf-8')
        paths['cable_awg'] = cpath

    # Cable length (promedio por campo)
    rows = []
    for campo, info in resumen.items():
        val = info.get('cable_length_mean')
        if val is not None:
            rows.append({'CAMPO': campo, 'cable_length_mean': float(val)})
    if rows:
        df_len = pd.DataFrame(rows)
        lpath = os.path.join(outdir, 'cable_length_by_campo.csv')
        df_len.to_csv(lpath, index=False, encoding='utf-8')
        paths['cable_length'] = lpath

    # Y-Tool
    rows = []
    for campo, info in resumen.items():
        y = info.get('ytool', {}) or {}
        for val, cnt in y.items():
            rows.append({'CAMPO': campo, 'ytool_value': val, 'count': int(cnt)})
    if rows:
        df_y = pd.DataFrame(rows)
        ypath = os.path.join(outdir, 'ytool_by_campo.csv')
        df_y.to_csv(ypath, index=False, encoding='utf-8')
        paths['ytool'] = ypath

    # VSD KVA: generar CSV con conteo por valor KVA por campo
    rows = []
    for campo, info in resumen.items():
        v = info.get('vsd_kva', {}) or {}
        for kva_val, cnt in v.items():
            rows.append({'CAMPO': campo, 'kva_value': kva_val, 'count': int(cnt)})
    if rows:
        df_v = pd.DataFrame(rows)
        vpath = os.path.join(outdir, 'vsd_kva_by_campo.csv')
        df_v.to_csv(vpath, index=False, encoding='utf-8')
        paths['vsd_kva'] = vpath

    # Generar resumen consolidado por campo para Excel
    summary_rows = []
    for campo, info in resumen.items():
        # VSD: elegir el valor más frecuente si existe
        vsd_val = None
        vsd = info.get('vsd_kva', {}) or {}
        if vsd:
            try:
                vsd_val = max(vsd.items(), key=lambda x: x[1])[0]
            except Exception:
                vsd_val = None

        # Rango de caudal: tomar el pump más usado y su min/max
        rango = None
        pumps = info.get('pumps_top', {}) or {}
        if pumps:
            try:
                top_pump = max(pumps.items(), key=lambda x: x[1]['count'] if isinstance(x[1], dict) else x[1])
                pname, pdata = top_pump[0], top_pump[1]
                if isinstance(pdata, dict):
                    mi = pdata.get('min_bbl'); ma = pdata.get('max_bbl')
                    if mi is not None and ma is not None:
                        rango = f"{mi} - {ma} bbl"
                    elif mi is not None:
                        rango = f"{mi} bbl"
                    else:
                        rango = pname
                else:
                    rango = pname
            except Exception:
                rango = None

        # AWG: top
        awg_val = None
        awg = info.get('cable_awg', {}) or {}
        if awg:
            try:
                awg_val = max(awg.items(), key=lambda x: x[1])[0]
            except Exception:
                awg_val = None

        # Motor: top
        motor_val = None
        motors = info.get('motor_types', {}) or {}
        if motors:
            try:
                motor_val = max(motors.items(), key=lambda x: x[1])[0]
            except Exception:
                motor_val = None

        # Y-Tool: top
        ytool_val = None
        ytool = info.get('ytool', {}) or {}
        if ytool:
            try:
                ytool_val = max(ytool.items(), key=lambda x: x[1])[0]
            except Exception:
                ytool_val = None

        summary_rows.append({
            'CAMPO': campo,
            'VSD_KVA': vsd_val,
            'RANGO_CAUDAL': rango,
            'CABLE_AWG': awg_val,
            'MOTOR': motor_val,
            'YTOOL': ytool_val
        })

    if summary_rows:
        df_sum = pd.DataFrame(summary_rows)
        # Guardar tanto XLSX como CSV para compatibilidad
        sum_xlsx = os.path.join(outdir, 'summary_by_campo.xlsx')
        try:
            df_sum.to_excel(sum_xlsx, index=False)
            paths['summary_excel'] = sum_xlsx
        except Exception:
            # fallback a CSV si no hay openpyxl
            sum_csv = os.path.join(outdir, 'summary_by_campo.csv')
            df_sum.to_csv(sum_csv, index=False, encoding='utf-8')
            paths['summary_csv'] = sum_csv

    return paths


def save_json(outdir, data, name='bombastipo_resumen.json'):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return path


# --- 3. Ejecución por Línea de Comandos (CLI) ---
def main():
    parser = argparse.ArgumentParser(description='Genera estadísticas de bombas por CAMPO desde la BD')
    parser.add_argument('--bd', required=True, help='Ruta al archivo BD (.csv/.xlsx)')
    parser.add_argument('--output', default='bomp_out', help='Directorio de salida')
    parser.add_argument('--top', type=int, default=5, help='Número de modelos top a mostrar por campo')
    parser.add_argument('--download', action='store_true', help='Permite descargar la BD si --bd es una URL (por defecto deshabilitado)')
    parser.add_argument('--save-json', action='store_true', help='Guardar también un JSON resumen (por defecto no)')
    parser.add_argument('--years', type=int, choices=[1,2], help='Filtrar registros por los últimos N años (1 o 2)')
    args = parser.parse_args()

    bd_arg = args.bd
    # Si bd es una URL, requerir flag --download para permitir la descarga (evita intentos automáticos)
    if isinstance(bd_arg, str) and bd_arg.strip().lower().startswith('http') and not args.download:
        print("La ruta proporcionada parece una URL. Por seguridad la descarga automática está deshabilitada.")
        print("Si deseas que el script intente descargar la URL, vuelve a ejecutar con el flag --download.")
        print("Alternativa: descarga el archivo manualmente y pasa la ruta local a --bd.")
        return

    if isinstance(bd_arg, str) and bd_arg.strip().lower().startswith('http') and args.download:
        upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        fname = os.path.join(upload_dir, 'bd_online.xlsx')
        try:
            def _download_onedrive(url, dest_path):
                # [Lógica de descarga de OneDrive/Sharepoint]
                r = requests.get(url, timeout=30, allow_redirects=True)
                r.raise_for_status()
                content_type = r.headers.get('content-type','')
                content = r.content
                is_html = 'text/html' in content_type or (isinstance(content, (bytes,bytearray)) and b'<html' in content[:400].lower())
                if is_html:
                    txt = content.decode('utf-8', errors='ignore')
                    m = re.search(r'FileGetUrl"\s*:\s*"([^\"]+?)"', txt) or re.search(r'FileUrlNoAuth"\s*:\s*"([^\"]+?)"', txt)
                    if m:
                        download_url = m.group(1).replace('\\u0026', '&').replace('\\/', '/')
                        download_url = html.unescape(download_url)
                        r2 = requests.get(download_url, timeout=30, allow_redirects=True)
                        r2.raise_for_status()
                        with open(dest_path, 'wb') as fh: fh.write(r2.content)
                        return True
                    else:
                        with open(dest_path, 'wb') as fh: fh.write(content)
                        return True
                else:
                    with open(dest_path, 'wb') as fh: fh.write(content)
                    return True

            ok = _download_onedrive(bd_arg, fname)
            if ok:
                bd_path = fname
                print(f"BD descargada en: {bd_path}")
            else:
                print("No se pudo descargar la BD desde la URL proporcionada.")
                return
        except Exception as e:
            print(f"Error al descargar BD desde URL: {e}")
            return
    else:
        bd_path = bd_arg

    df = read_bd(bd_path)
    resumen = estadisticas_por_campo(df, years=args.years)

    outdir = args.output
    csv_paths = save_csvs(outdir, resumen)
    saved = None
    if args.save_json:
        saved = save_json(outdir, resumen, 'bomp_resumen.json')

    # Imprimir resumen compacto por campo
    for campo, info in resumen.items():
        print(f"\n=== CAMPO: {campo} ===")
        pumps_top = info.get('pumps_top', {})
        if pumps_top:
            print("Bombas top:")
            sorted_pumps = sorted(pumps_top.items(), key=lambda x: -x[1]['count'] if isinstance(x[1], dict) and 'count' in x[1] else 0)
            
            for i, (m, d) in enumerate(sorted_pumps):
                if i >= args.top:
                    break
                mi = d.get('min_bbl'); ma = d.get('max_bbl')
                rng = f"({mi}-{ma} bbl)" if mi is not None and ma is not None else (f"({mi} bbl)" if mi is not None else '')
                print(f"  - {m}: {d.get('count')} veces {rng}")
        else:
            print("Bombas: No disponible")

        motors = info.get('motor_types', {})
        if motors:
            print("Motores:")
            for k, v in motors.items():
                print(f"  - {k}: {v}")
        else:
            print("Motores: No disponible")

        awg = info.get('cable_awg', {})
        if awg:
            print("AWG de cable más comunes:")
            for k, v in awg.items():
                print(f"  - AWG {k}: {v}")
        else:
            print("AWG: No disponible")

        cl = info.get('cable_length_mean')
        if cl is not None:
            print(f"Longitud cable promedio: {cl}")
        else:
            print("Longitud de cable: No disponible")

        ytool = info.get('ytool', {})
        if ytool:
            print("Y-Tool:")
            for k, v in ytool.items():
                print(f"  - {k}: {v}")
        else:
            print("Y-Tool: No disponible")

        vsd = info.get('vsd_kva', {})
        if vsd:
            print("VSD KVA:")
            for k, v in vsd.items():
                print(f"  - {k}: {v}")
        else:
            print("VSD KVA: No disponible")

    if saved:
        print(f"\nResumen JSON guardado en: {saved}")
    if csv_paths:
        print("CSV generados:")
        for k, p in csv_paths.items():
            print(f"  - {k}: {p}")


# --- 4. Lógica de Ejecución Corregida (¡La Solución!) ---

if __name__ == '__main__':
    # Esta es la lógica estándar y más robusta para scripts duales (CLI y Streamlit).
    #
    # 1. Si Streamlit está ejecutando el script (`'streamlit' in sys.modules` es TRUE), 
    #    o si se llama sin argumentos CLI, forzamos la UI.
    # 2. Si se llama con argumentos (ej: `python BOMBASTIPO.py --bd ...`), ejecutamos `main()`.

    if 'streamlit' in sys.modules or len(sys.argv) == 1:
        # Se ejecuta la interfaz Streamlit
        show_streamlit_ui()
    else:
        # Se asume modo CLI si hay argumentos (aparte del nombre del script)
        # y no estamos en un entorno Streamlit detectado.
        try:
             main()
        except SystemExit:
             # argparse puede lanzar SystemExit (ej. si faltan args o se usa --help).
             # Dejamos que el script termine con el error de la CLI.
             pass