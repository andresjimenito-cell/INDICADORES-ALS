import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import requests
import re
import html
import plotly.graph_objects as go
import plotly.express as px
import pickle
from pathlib import Path

CACHE_DIR = Path("cache_data")
CACHE_FILE = CACHE_DIR / "last_run_data.pkl"

def load_cached_data():
    """Carga los datos desde el archivo pickle si existe (compartido con INDICADORES.py)."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
        return data
    except Exception as e:
        print(f"Error cargando caché en resumen: {e}")
        return None

# Intentar usar el módulo de procesamiento compartido si existe
try:
    from processing import perform_initial_calculations as shared_perform_initial_calculations
except Exception:
    shared_perform_initial_calculations = None

# --- IMPORTACIONES RESTAURADAS ---
try:
    from theme import get_colors
    from grafico import generar_grafico_resumen, render_premium_echarts, generar_resumen_mensual
    from grafico_run_life import render_premium_echarts_run_life, render_premium_echarts_pozos
    import mtbf as mtbf_mod
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}.")
    def get_colors(): return {'primary': '#2563eb', 'secondary': '#64748b', 'text': '#0f172a', 'text_faded': '#64748b', 'container_bg': '#ffffff'}
    def generar_grafico_resumen(df_bd, df_f9, fecha): return None, None
    def render_premium_echarts(df, t=""): pass
    def render_premium_echarts_run_life(df, t=""): pass
    def render_premium_echarts_pozos(df, t=""): pass
    def generar_resumen_mensual(df1, df2, f): return pd.DataFrame()
    class mtbf_mod:
        @staticmethod
        def calcular_mtbf(df, f): return 0, None

# --- CONFIGURACIÓN DE PÁGINA ---
try:
    st.set_page_config(
       
        initial_sidebar_state='collapsed',
        page_icon="📊"
    )
except Exception:
    pass

# --- COLORES ---
# Usamos colores base, pero el CSS se encargará de la adaptación al tema
colors = get_colors()
PRIMARY = colors.get('primary', '#3b82f6')

# --- CSS DINÁMICO Y COMPACTO ---
DASHBOARD_CSS = f"""
<style>
:root {{
    /* 🎨 PALETA DE COLORES VIBRANTE */
    --color-primary: #6366f1;
    --color-secondary: #8b5cf6;
    --color-accent-pink: #ec4899;
    --color-accent-orange: #f97316;
    --color-accent-cyan: #06b6d4;
    --color-accent-green: #10b981;
    --color-accent-yellow: #fbbf24;
    --color-dark: #0f172a;
    --color-light: #f8fafc;
    
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=Inter:wght@300;400;600&family=Rajdhani:wght@500;700&display=swap');

    :root {{
        --neon-cyan: #00f2ff;
        --neon-magenta: #ff00ff;
        --neon-green: #00ff9d;
        --bg-deep: #060a1e;
        --glass: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.1);
        --transition-hud: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .stApp {{
        background-color: var(--bg-deep) !important;
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(0, 242, 255, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(255, 0, 255, 0.05) 0%, transparent 40%) !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* --- HUD SCANLINES --- */
    .stApp::before {{
        content: " ";
        position: fixed;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%);
        z-index: 9999;
        background-size: 100% 4px;
        pointer-events: none;
        opacity: 0.15;
    }}

    /* --- PREMIUM HEADER --- */
    .dashboard-header {{
        background: linear-gradient(135deg, rgba(6, 10, 30, 0.8), rgba(6, 10, 30, 0.4));
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 1.5rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4), inset 0 0 20px rgba(0, 242, 255, 0.05);
        position: relative;
        overflow: hidden;
    }}

    .dashboard-header::after {{
        content: '';
        position: absolute;
        bottom: 0; left: 0; width: 100%; height: 2px;
        background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-magenta), transparent);
    }}

    .header-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        color: #fff;
        letter-spacing: -1px;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
    }}

    .header-date {{
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--neon-cyan);
        text-transform: uppercase;
        letter-spacing: 4px;
        background: rgba(0, 242, 255, 0.1);
        padding: 5px 15px;
        border-radius: 8px;
        border: 1px solid rgba(0, 242, 255, 0.2);
    }}

    /* --- KPI CARDS HUD --- */
    .kpi-card {{
        background: rgba(10, 15, 30, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 18px;
        padding: 1.2rem;
        transition: var(--transition-hud);
        position: relative;
        overflow: hidden;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}

    .kpi-card:hover {{
        transform: translateY(-5px);
        border-color: var(--neon-cyan);
        box-shadow: 0 10px 30px rgba(0, 242, 255, 0.15);
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: var(--neon-cyan);
        opacity: 0.5;
    }}

    .kpi-icon {{
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 10px var(--neon-cyan));
    }}

    .kpi-label {{
        font-family: 'Outfit', sans-serif;
        font-size: 0.65rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }}

    .kpi-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        color: #fff;
        margin-top: 0.2rem;
    }}

    /* --- NEON BUTTONS / STATUS CARDS --- */
    .neon-card {{
        background: rgba(10, 15, 30, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: var(--transition-hud);
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }}

    .neon-card:hover {{
        background: rgba(10, 15, 30, 0.7);
        transform: scale(1.02);
    }}

    .neon-success {{ border-left: 4px solid var(--neon-green); box-shadow: inset 5px 0 15px rgba(0, 255, 157, 0.05); }}
    .neon-danger {{ border-left: 4px solid #ff4b4b; box-shadow: inset 5px 0 15px rgba(255, 75, 75, 0.05); }}
    .neon-info {{ border-left: 4px solid var(--neon-cyan); box-shadow: inset 5px 0 15px rgba(0, 242, 255, 0.05); }}
    .neon-neutral {{ border-left: 4px solid #94a3b8; box-shadow: inset 5px 0 15px rgba(148, 163, 184, 0.05); }}

    .neon-label {{
        font-family: 'Outfit', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}

    .neon-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 900;
        color: #fff;
    }}

    /* Tablas y Containers */
    .stContainer {{
        background: rgba(10, 15, 30, 0.3) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }}

    h5 {{
        font-family: 'Outfit', sans-serif !important;
        color: var(--neon-cyan) !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-weight: 800 !important;
        border-bottom: 1px solid rgba(0, 242, 255, 0.1);
        padding-bottom: 0.5rem;
    }}

</style>
"""

def _read_simple(f):
    if f is None: return None
    try:
        if f.name.lower().endswith('.csv'):
            return pd.read_csv(f, encoding='latin1', low_memory=False)
        else:
            return pd.read_excel(f)
    except:
        f.seek(0)
        return pd.read_csv(f, encoding='latin1', low_memory=False, on_bad_lines='skip')


def get_last_day_of_previous_month():
    today = datetime.now().date()
    first_day_of_current_month = today.replace(day=1)
    last_day_prev = first_day_of_current_month - timedelta(days=1)
    return last_day_prev


def _download_onedrive(url, dest_path):
    """Descarga una URL de OneDrive/SharePoint; si devuelve HTML intenta extraer la URL real."""
    try:
        r = requests.get(url, timeout=30, allow_redirects=True)
        r.raise_for_status()
        content = r.content
        content_type = r.headers.get('content-type','')
        is_html = 'text/html' in content_type or (isinstance(content, (bytes,bytearray)) and b'<html' in content[:400].lower())
        if is_html:
            txt = content.decode('utf-8', errors='ignore')
            m = re.search(r'FileGetUrl"\s*:\s*"([^"]+)"', txt) or re.search(r'FileUrlNoAuth"\s*:\s*"([^"]+)"', txt)
            if m:
                download_url = m.group(1).replace('\\u0026', '&').replace('\\/', '/')
                download_url = html.unescape(download_url)
                r2 = requests.get(download_url, timeout=30, allow_redirects=True)
                r2.raise_for_status()
                with open(dest_path, 'wb') as fh:
                    fh.write(r2.content)
                return True
            else:
                # guardar HTML para diagnóstico
                with open(dest_path, 'wb') as fh:
                    fh.write(content)
                return True
        else:
            with open(dest_path, 'wb') as fh:
                fh.write(content)
            return True
    except Exception:
        return False

def _calc_basic_kpis(df_bd, df_f9, fecha_eval):
    # (Lógica original de cálculo KPI)
    fecha_eval = pd.to_datetime(fecha_eval)
    df = df_bd.copy()
    for c in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
        if c in df.columns: df[c] = pd.to_datetime(df[c], errors='coerce')

    extraidos = 0
    running = 0
    fallados = 0
    pozos_on = 0
    
    if 'FECHA_RUN' in df.columns:
        cond = (df['FECHA_RUN'] <= fecha_eval)
        if 'FECHA_PULL' in df.columns: cond &= (df['FECHA_PULL'].isna() | (df['FECHA_PULL'] > fecha_eval))
        running = int(cond.sum())

    if 'FECHA_FALLA' in df.columns:
        cond = (df['FECHA_FALLA'].notna()) & (df['FECHA_FALLA'] <= fecha_eval)
        if 'FECHA_PULL' in df.columns: cond &= (df['FECHA_PULL'].isna() | (df['FECHA_PULL'] > fecha_eval))
        fallados = int(cond.sum())

    if 'FECHA_PULL' in df.columns:
        extraidos = int((df['FECHA_PULL'].notna() & (df['FECHA_PULL'] <= fecha_eval)).sum())

    if df_f9 is not None and not df_f9.empty:
        df_f9 = df_f9.copy()
        fecha_col = next((c for c in df_f9.columns if 'FECHA' in c), None)
        dias_col = next((c for c in df_f9.columns if 'DIAS' in c), None)
        pozo_col = next((c for c in df_f9.columns if 'POZO' in c), None)
        if fecha_col and dias_col and pozo_col:
            df_f9[fecha_col] = pd.to_datetime(df_f9[fecha_col], errors='coerce')
            mask = (df_f9[fecha_col].dt.year == fecha_eval.year) & (df_f9[fecha_col].dt.month == fecha_eval.month)
            pozos_on = int(df_f9[mask][df_f9[mask][dias_col] > 0][pozo_col].nunique())

    pozos_operativos = max(0, running - fallados)
    pozos_off = max(0, pozos_operativos - pozos_on)
    try:
        mtbf_val, _ = mtbf_mod.calcular_mtbf(df, fecha_eval)
        mtbf_str = f"{mtbf_val:.1f}" if mtbf_val else "N/D"
    except:
        mtbf_str = "N/D"
        mtbf_val = None

    return {
        'extraidos': extraidos, 'running': running, 'fallados': fallados,
        'pozos_on': pozos_on, 'pozos_off': pozos_off, 'mtbf': mtbf_str,"operativos": pozos_operativos
    }

def _render_top_kpi(icon, label, value, unit=""):
    """Tarjeta superior Premium HUD."""
    return f"""
    <div class='kpi-card'>
        <div class='kpi-icon'>{icon}</div>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}<span style='font-size:0.7rem; color:var(--neon-cyan); margin-left:4px; opacity:0.8; font-weight:400;'>{unit}</span></div>
    </div>
    """

def _render_neon_button(icon, label, value, style_class="neon-neutral"):
    """Botón lateral estilo Consola de Comando."""
    return f"""
    <div class='neon-card {style_class}'>
        <div style='display: flex; align-items: center; justify-content: space-between;'>
            <div style='display: flex; align-items: center; gap: 0.8rem;'>
                <span style='font-size: 1.2rem; filter: drop-shadow(0 0 5px currentColor);'>{icon}</span>
                <span class='neon-label'>{label}</span>
            </div>
            <div class='neon-value'>{value}</div>
        </div>
        <div style="height:2px; background: rgba(255,255,255,0.03); width:100%; margin-top:5px;"></div>
    </div>
    """

def generar_grafico_radar(kpis):
    """
    Genera un gráfico tipo 'radar' mejorado para mostrar la distribución de estado.
    Estilizado para un dashboard oscuro.
    """
    # Definición de datos
    vals = [kpis.get('running', 0), kpis.get('pozos_on', 0), kpis.get('pozos_off', 0), kpis.get('fallados', 0), kpis.get('operativos', 0)]
    cats = ['En Fondo', 'Pozos ON', 'Pozos OFF', 'Fallados', 'Operativos']
    
    # 1. Determinar el valor máximo para la escala (Mejora de visibilidad)
    # Se añade un buffer de 10% para que el polígono no toque el borde
    max_val = max(vals) * 1.15 if max(vals) > 0 else 100
    
    # Definición de constantes de estilo para consistencia
    COLOR_LINEA = '#10B981'  # Ejemplo de PRIMARY (Verde/Éxito)
    COLOR_RELLENO = 'rgba(16, 185, 129, 0.4)' # Verde con 40% de transparencia
    COLOR_GRID = 'rgba(255, 255, 255, 0.3)' # Líneas de cuadrícula blancas y sutiles
    COLOR_TICK_LABELS = 'white'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=vals, 
        theta=cats, 
        fill='toself',
        name='Distribución', # Se añade un nombre para la leyenda (aunque esté oculta)
        
        # Estilo de la línea del polígono
        line=dict(
            color=COLOR_LINEA,
            width=3 # Línea más gruesa para destacar
        ),
        
        # Estilo del relleno del polígono
        fillcolor=COLOR_RELLENO,
        
        # Marcadores para los puntos de datos
        marker=dict(
            size=6,
            color='#37FF00',
            symbol='circle'
        )
    ))
    
    fig.update_layout(
        title={
            'text': 'Distribución de Estado Operacional', 
            'y': 0.99, 
            'x': 0.5, 
            'xanchor': 'center', 
            'yanchor': 'top',
            'font': {'color': 'white', 'size': 16}
        },
        polar=dict(
            # Configuración del eje radial (valores)
            radialaxis=dict(
                visible=True, 
                range=[0, max_val], # Rango dinámico y con buffer
                showticklabels=False, # Ocultar los números en el eje para limpiar el gráfico
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                linewidth=1
            ),
            # Configuración del eje angular (categorías)
            angularaxis=dict(
                gridcolor=COLOR_GRID, 
                linecolor=COLOR_GRID,
                tickfont=dict(color=COLOR_TICK_LABELS, size=11), # Etiquetas blancas
                direction='clockwise' # Para un aspecto más formal de "reloj" o "telaraña"
            ),
            bgcolor='rgba(0,0,0,0)' # Fondo del polar transparente
        ),
        # Ajustes generales del layout
        margin=dict(l=20, r=20, t=40, b=20),
        height=340, 
        paper_bgcolor='rgba(0,0,0,0)', # Fondo de la figura transparente
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        showlegend=False
    )
    
    return fig


def generar_grafico_severidad_acelerador(indice_severidad):
    """
    Genera un gráfico tipo 'velocímetro/gauge' para mostrar el índice de severidad.
    """
    # Normalizar el índice de severidad para el rango 0-3
    max_valor = 3.0
    valor_actual = min(max(indice_severidad, 0), max_valor)
    
    # Determinar color basado en el valor
    if valor_actual > 1.5:
        color_aguja = '#FF0000'  # Rojo para alto
        label_estado = 'ALTO'
    elif valor_actual > 1.0:
        color_aguja = '#FF9000'  # Naranja para medio-alto
        label_estado = 'MEDIO-ALTO'
    else:
        color_aguja = '#37FF00'  # Verde para bajo
        label_estado = 'BAJO'
    
    fig = go.Figure()
    
    # Crear el velocímetro con go.Indicator
    fig.add_trace(go.Indicator(
        mode='gauge+number',
        value=valor_actual,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Severidad >1.05 Alerta '},
        number={'suffix': '', 'valueformat': '.2f'},
        gauge=go.indicator.Gauge(
            axis=dict(range=[0, max_valor], tickwidth=2, tickcolor='white'),
            bar=dict(color=color_aguja, thickness=0.2),
            bgcolor='rgba(100, 100, 100, 0.2)',
            borderwidth=2,
            bordercolor='white',
            steps=[
                dict(range=[0, 1], color='rgba(55, 255, 0, 0.3)'),        # Verde
                dict(range=[1, 1.05], color='rgba(255, 144, 0, 0.3)'),      # Naranja
                dict(range=[1.05, max_valor], color='rgba(255, 0, 0, 0.3)') # Rojo
            ],
            threshold=dict(
                line=dict(color='red', width=3),
                thickness=1,
                value=1.0
            )
        )
    ))
    
    fig.update_layout(
        height=320,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        showlegend=False
    )
    
    return fig

def get_color_sequence(mode=None):
    return [
        '#00A2FF',
        '#5EFF00',
        '#0011D1',
        '#00F5FF',
        '#4B0073',
        '#000980',
        '#A1039D'
    ]


def _normalize_cols_upper(df):
    if df is None: return None
    df = df.copy()
    df.columns = [str(c).upper().strip() for c in df.columns]
    # Normalizaciones ocasionales
    if 'SISTEMA ALS' in df.columns and 'ALS' not in df.columns:
        df = df.rename(columns={'SISTEMA ALS': 'ALS'})
    return df


def _prepare_and_run(df_forma9_raw, df_bd_raw, fecha_evaluacion):
    """
    Limpia y normaliza los DataFrames (similar a `cargar_y_limpiar_datos` de INDICADORES)
    y luego aplica la lógica de `perform_initial_calculations` para devolver
    (df_forma9_proc, df_bd_proc).
    """
    if df_forma9_raw is None or df_bd_raw is None:
        return None, None

    df_forma9 = df_forma9_raw.copy()
    df_bd = df_bd_raw.copy()

    try:
        # Normalizar nombres
        df_forma9.columns = [str(col).upper().strip().replace('#', '').replace('.', '').replace('POZO NO', 'POZO') for col in df_forma9.columns]
        fecha_col_forma9 = next((col for col in df_forma9.columns if 'FECHA' in col), None)
        dias_col = next((col for col in df_forma9.columns if 'DIAS' in col), None)
        pozo_col_forma9 = next((col for col in df_forma9.columns if 'POZO' in col), None)
        rename_map = {}
        if fecha_col_forma9: rename_map[fecha_col_forma9] = 'FECHA_FORMA9'
        if dias_col: rename_map[dias_col] = 'DIAS TRABAJADOS'
        if pozo_col_forma9: rename_map[pozo_col_forma9] = 'POZO'
        if rename_map:
            df_forma9 = df_forma9.rename(columns=rename_map)

        # Coerciones
        if 'FECHA_FORMA9' in df_forma9.columns:
            df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
        if 'DIAS TRABAJADOS' in df_forma9.columns:
            df_forma9['DIAS TRABAJADOS'] = pd.to_numeric(df_forma9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
        if 'POZO' in df_forma9.columns:
            df_forma9 = df_forma9.dropna(subset=['FECHA_FORMA9', 'POZO']) if 'FECHA_FORMA9' in df_forma9.columns else df_forma9.dropna(subset=['POZO'])
    except Exception:
        pass

    try:
        # BD cleaning
        df_bd.columns = [str(col).upper().strip().replace('#', '').replace('.', '') for col in df_bd.columns]
        run_col_bd = next((col for col in df_bd.columns if 'RUN' in col), None)
        fecha_run_col = next((col for col in df_bd.columns if 'FECHA RUN' in col), None)
        pozo_col_bd = next((col for col in df_bd.columns if 'POZO' in col), None)
        fecha_falla_col = next((col for col in df_bd.columns if 'FECHA FALLA' in col), None)
        fecha_pull_col = next((col for col in df_bd.columns if 'FECHA PULL' in col), None)
        operando_col = next((col for col in df_bd.columns if 'OPERANDO' in col), None)
        indicador_col = next((col for col in df_bd.columns if 'INDICADOR MTBF' in col), None)
        proveedor_col = next((col for col in df_bd.columns if 'PROVEEDOR' in col), None)
        als_col = next((col for col in df_bd.columns if 'ALS' in col), None)
        activo_col = next((col for col in df_bd.columns if 'ACTIVO' in col), None)
        severidad_col = next((col for col in df_bd.columns if 'SEVERIDAD' in col.upper() or 'SEVERIDAD' in col.upper()), None)

        rename_map_bd = {}
        if run_col_bd: rename_map_bd[run_col_bd] = 'RUN'
        if fecha_run_col: rename_map_bd[fecha_run_col] = 'FECHA_RUN'
        if fecha_falla_col: rename_map_bd[fecha_falla_col] = 'FECHA_FALLA'
        if fecha_pull_col: rename_map_bd[fecha_pull_col] = 'FECHA_PULL'
        if operando_col: rename_map_bd[operando_col] = 'OPERANDO_ESTADO'
        if indicador_col: rename_map_bd[indicador_col] = 'INDICADOR_MTBF'
        if pozo_col_bd: rename_map_bd[pozo_col_bd] = 'POZO'
        if proveedor_col: rename_map_bd[proveedor_col] = 'PROVEEDOR'
        if als_col: rename_map_bd[als_col] = 'ALS'
        if activo_col: rename_map_bd[activo_col] = 'ACTIVO'
        if severidad_col: rename_map_bd[severidad_col] = 'SEVERIDAD'
        if rename_map_bd:
            df_bd = df_bd.rename(columns=rename_map_bd)

        df_bd['FECHA_RUN'] = pd.to_datetime(df_bd.get('FECHA_RUN'), errors='coerce')
        df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd.get('FECHA_FALLA'), errors='coerce')
        df_bd['FECHA_PULL'] = pd.to_datetime(df_bd.get('FECHA_PULL'), errors='coerce')
        if 'INDICADOR_MTBF' in df_bd.columns:
            df_bd['INDICADOR_MTBF'] = pd.to_numeric(df_bd['INDICADOR_MTBF'], errors='coerce').fillna(0)
        if 'SEVERIDAD' in df_bd.columns:
            df_bd['SEVERIDAD'] = pd.to_numeric(df_bd['SEVERIDAD'], errors='coerce').fillna(0)
        else:
            df_bd['SEVERIDAD'] = np.nan

        df_bd = df_bd.dropna(subset=['FECHA_RUN', 'POZO']) if 'FECHA_RUN' in df_bd.columns and 'POZO' in df_bd.columns else df_bd
    except Exception:
        pass

    # Aplicar lógica de perform_initial_calculations (simplificada y adaptada)
    try:
        fecha_eval_ts = pd.to_datetime(fecha_evaluacion)
    except Exception:
        fecha_eval_ts = pd.to_datetime(df_forma9['FECHA_FORMA9'].max()) if ('FECHA_FORMA9' in df_forma9.columns and not df_forma9['FECHA_FORMA9'].isna().all()) else pd.to_datetime('today')

    try:
        # RUN LIFE
        df_bd['RUN LIFE'] = np.where(
            df_bd['FECHA_FALLA'].notna(),
            (df_bd['FECHA_FALLA'] - df_bd['FECHA_RUN']).dt.days,
            np.where(
                df_bd['FECHA_PULL'].notna(),
                (df_bd['FECHA_PULL'] - df_bd['FECHA_RUN']).dt.days,
                np.where(
                    df_bd['FECHA_PULL'].isna(),
                    (fecha_eval_ts - df_bd['FECHA_RUN']).dt.days,
                    np.nan
                )
            )
        )

        df_bd['NICK'] = df_bd['POZO'].astype(str) + '-' + df_bd['RUN'].astype(str)

        df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
        df_forma9_copy = df_forma9.copy()

        df_bd_filtered = df_bd[df_bd['FECHA_RUN'] <= fecha_eval_ts].copy()

        merged_df = pd.merge(df_forma9_copy.reset_index(), df_bd_filtered[['POZO', 'RUN', 'PROVEEDOR', 'FECHA_RUN', 'FECHA_PULL']], on='POZO', how='left')

        merged_df['is_match'] = (merged_df['FECHA_FORMA9'] >= merged_df['FECHA_RUN']) & \
                                 (merged_df['FECHA_FORMA9'] < merged_df['FECHA_PULL'].fillna(pd.to_datetime(fecha_evaluacion)))

        best_matches_idx = merged_df[merged_df['is_match']].groupby('index')['FECHA_RUN'].idxmax()
        best_matches_df = merged_df.loc[best_matches_idx]

        df_forma9_copy['RUN'] = best_matches_df.set_index('index')['RUN']
        df_forma9_copy['PROVEEDOR'] = best_matches_df.set_index('index')['PROVEEDOR']

        df_forma9_copy[['RUN', 'PROVEEDOR']] = df_forma9_copy[['RUN', 'PROVEEDOR']].fillna('NO DATA✍️')
        df_forma9_copy['NICK'] = df_forma9_copy['POZO'].astype(str) + '-' + df_forma9_copy['RUN'].astype(str)
    except Exception:
        pass

    return df_forma9_copy, df_bd





def render_bopd_vs_runlife(df_bd, df_f9, fecha_eval):
    """Renderiza la sección 'BOPD vs Run Life'. Se ajusta la altura del gráfico de barras.
    """
    import pandas as _pd
    import numpy as _np
    try:
        from theme import styled_title as _styled_title, get_plotly_layout as _get_plotly_layout, get_colors as _get_colors
    except Exception:
        def _styled_title(t):
            return t
        def _get_plotly_layout():
            return {}
        def _get_colors():
            return {'primary': '#0a84ff', 'text': '#0f1724', 'background': None}

    colors_local = _get_colors()
    COLOR_PRINCIPAL = colors_local.get('primary', '#0a84ff')
    COLOR_FUENTE = colors_local.get('text', '#0f1724')
    _bg_raw = colors_local.get('background', None)
    if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
        COLOR_FONDO_OSCURO = None
    else:
        COLOR_FONDO_OSCURO = _bg_raw

    # ... (Se mantiene la lógica de cálculo de datos del gráfico de barras - BOPD vs Run Life)
    try:
        fecha_eval = _pd.to_datetime(fecha_eval)
        df_runs_validos = df_bd[df_bd['FECHA_RUN'] <= fecha_eval].copy() if 'FECHA_RUN' in df_bd.columns else df_bd.copy()
        if df_runs_validos.empty:
            st.info('No hay RUNs previos a la fecha de evaluación para los pozos filtrados.')
        df_last_run = df_runs_validos.sort_values('FECHA_RUN').groupby('POZO', as_index=False).last() if 'FECHA_RUN' in df_runs_validos.columns else df_runs_validos.copy()
        try:
            if 'FECHA_PULL' in df_last_run.columns:
                df_last_run['FECHA_PULL'] = _pd.to_datetime(df_last_run['FECHA_PULL'], errors='coerce')
            else:
                df_last_run['FECHA_PULL'] = _pd.NaT
            if 'FECHA_FALLA' in df_last_run.columns:
                df_last_run['FECHA_FALLA'] = _pd.to_datetime(df_last_run['FECHA_FALLA'], errors='coerce')
            else:
                df_last_run['FECHA_FALLA'] = _pd.NaT
            df_last_run['FECHA_RUN'] = _pd.to_datetime(df_last_run['FECHA_RUN'], errors='coerce')

            mask_operativos = (
                (df_last_run['FECHA_RUN'] <= fecha_eval) &
                ((df_last_run['FECHA_PULL'].isna()) | (df_last_run['FECHA_PULL'] > fecha_eval)) &
                ((df_last_run['FECHA_FALLA'].isna()) | (df_last_run['FECHA_FALLA'] > fecha_eval))
            )
            df_last_run = df_last_run[mask_operativos].copy()
        except Exception as e:
            st.warning(f"No se pudo aplicar el filtro de pozos operativos al conjunto de RUNs: {e}")
    except Exception:
        df_last_run = df_bd.copy()

    # Procesar FORMA9 por mes de evaluación
    df_f9_local = df_f9.copy() if df_f9 is not None else _pd.DataFrame()
    df_f9_sum = _pd.DataFrame(columns=['POZO', 'BOPD'])
    try:
        if 'FECHA_FORMA9' in df_f9_local.columns:
            df_f9_local['FECHA_FORMA9'] = _pd.to_datetime(df_f9_local['FECHA_FORMA9'], errors='coerce')
            fecha_eval = _pd.to_datetime(fecha_eval)
            df_f9_month = df_f9_local[(df_f9_local['FECHA_FORMA9'].dt.year == fecha_eval.year) & (df_f9_local['FECHA_FORMA9'].dt.month == fecha_eval.month)].copy()

            dias_col = next((c for c in df_f9_month.columns if 'DIAS' in str(c).upper()), None)
            bopd_col = next((c for c in df_f9_month.columns if 'BOPD' in str(c).upper()), None)

            if dias_col is not None:
                df_f9_month[dias_col] = _pd.to_numeric(df_f9_month[dias_col], errors='coerce').fillna(0)
                df_f9_month = df_f9_month[df_f9_month[dias_col] > 0].copy()

            if not df_f9_month.empty and bopd_col is not None:
                df_f9_month[bopd_col] = _pd.to_numeric(df_f9_month[bopd_col], errors='coerce').fillna(0)
                df_f9_sum = df_f9_month.groupby('POZO', as_index=False).agg({bopd_col: 'sum'})
                df_f9_sum.rename(columns={bopd_col: 'BOPD'}, inplace=True)
            else:
                df_f9_sum = _pd.DataFrame(columns=['POZO', 'BOPD'])
        else:
            df_f9_sum = _pd.DataFrame(columns=['POZO', 'BOPD'])
    except Exception as e:
        st.warning(f"Error al procesar FORMA9 para mes de evaluación: {e}")
        df_f9_sum = _pd.DataFrame(columns=['POZO', 'BOPD'])

    # Mapear BOPD al RUN correspondiente
    if not df_f9_sum.empty:
        try:
            df_f9_month_raw = df_f9_local[(df_f9_local['FECHA_FORMA9'].dt.year == fecha_eval.year) & (df_f9_local['FECHA_FORMA9'].dt.month == fecha_eval.month)].copy()
        except Exception:
            df_f9_month_raw = _pd.DataFrame()

        if not df_f9_month_raw.empty:
            df_f9_lastdate = df_f9_month_raw.sort_values('FECHA_FORMA9').groupby('POZO', as_index=False).last()[['POZO', 'FECHA_FORMA9']]
            df_f9_sum = df_f9_sum.copy()
            df_f9_merge = _pd.merge(df_f9_sum, df_f9_lastdate, on='POZO', how='left')
        else:
            df_f9_merge = df_f9_sum.copy()
            df_f9_merge['FECHA_FORMA9'] = _pd.NaT

        bd_match = df_bd.copy()
        for dtcol in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
            if dtcol in bd_match.columns:
                bd_match[dtcol] = _pd.to_datetime(bd_match[dtcol], errors='coerce')
            else:
                bd_match[dtcol] = _pd.NaT

        if not df_f9_merge.empty:
            df_f9_merge['_idx'] = range(len(df_f9_merge))
            merged_df = _pd.merge(df_f9_merge, bd_match[['POZO', 'RUN', 'FECHA_RUN', 'FECHA_PULL', 'RUN LIFE']], on='POZO', how='left')
            merged_df['FECHA_FORMA9'] = _pd.to_datetime(merged_df['FECHA_FORMA9'], errors='coerce')
            merged_df['FECHA_PULL_FILL'] = merged_df['FECHA_PULL'].fillna(fecha_eval)
            merged_df['is_match'] = (merged_df['FECHA_FORMA9'] >= merged_df['FECHA_RUN']) & (merged_df['FECHA_FORMA9'] < merged_df['FECHA_PULL_FILL'])

            runlife_map = {}
            try:
                matched = merged_df[merged_df['is_match']].copy()
                if not matched.empty:
                    best_idx = matched.groupby('_idx')['FECHA_RUN'].idxmax()
                    best_matches = merged_df.loc[best_idx]
                    runlife_map = best_matches.set_index('_idx')['RUN LIFE'].to_dict()
            except Exception:
                runlife_map = {}

            missing_idxs = [i for i in range(len(df_f9_merge)) if i not in runlife_map]
            if missing_idxs:
                for i in missing_idxs:
                    try:
                        candidate = merged_df[(merged_df['_idx'] == i) & (merged_df['FECHA_RUN'] <= merged_df.loc[merged_df['_idx'] == i, 'FECHA_FORMA9'].iloc[0])]
                        if not candidate.empty:
                            idx_choice = candidate['FECHA_RUN'].idxmax()
                            runlife_map[i] = merged_df.loc[idx_choice, 'RUN LIFE']
                    except Exception:
                        continue

            df_f9_merge['RUN LIFE'] = df_f9_merge.index.map(lambda i: runlife_map.get(i, _np.nan))

            try:
                total_pozos = len(df_f9_merge)
                mapeados = df_f9_merge['RUN LIFE'].notna().sum()
                no_mapeados = total_pozos - int(mapeados)
                st.markdown(f"**Pozos en FORMA9 (mes):** {total_pozos} — **Con RUN asociado:** {mapeados} — **Sin RUN:** {no_mapeados}")
            except Exception:
                pass
            merged = df_f9_merge[['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE']].copy()
        else:
            merged = _pd.DataFrame(columns=['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE'])
    else:
        merged = _pd.DataFrame(columns=['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE'])

    merged['BOPD'] = _pd.to_numeric(merged['BOPD'], errors='coerce').fillna(0)
    merged['RUN LIFE'] = _pd.to_numeric(merged['RUN LIFE'], errors='coerce').fillna(0)

    def bucket_runlife(days):
        years = days / 365.0
        if _pd.isna(days):
            return 'Sin Datos'
        if years < 2:
            return '<2 años'
        if 2 <= years < 4:
            return '2-4 años'
        if 4 <= years < 6:
            return '4-6 años'
        return '>6 años'

    if not merged.empty:
        merged['RunLifeBucket'] = merged['RUN LIFE'].apply(bucket_runlife)

        agg = merged.groupby(['RunLifeBucket']).agg(
            BOPD_sum=_pd.NamedAgg(column='BOPD', aggfunc='sum'),
            Pozos=_pd.NamedAgg(column='POZO', aggfunc=lambda x: x.nunique())
        ).reset_index()

        bucket_order = ['<2 años', '2-4 años', '4-6 años', '>6 años']
        agg = agg.set_index('RunLifeBucket').reindex(bucket_order).fillna({'BOPD_sum': 0, 'Pozos': 0}).reset_index()

        if agg.empty:
            st.info('No hay datos suficientes para generar la gráfica por buckets de Run Life.')
        else:
            # Gráfico de barras
            fig2 = px.bar(
                agg,
                x='RunLifeBucket',
                y='BOPD_sum',
                color='RunLifeBucket',
                color_discrete_sequence=get_color_sequence(),
                labels={'RunLifeBucket': 'Run Life (años)', 'BOPD_sum': 'BOPD (suma)'},
                title=_styled_title('BOPD total por Run Life')
            )
            
            # --- AJUSTES CLAVE PARA LA SIMETRÍA Y LIMPIEZA ---
            max_y = agg['BOPD_sum'].max() if not agg['BOPD_sum'].empty else 0
            
            # 1. Aplicar la misma altura que el gráfico de radar (280px)
            # 2. Reducir los márgenes para maximizar el área de trazado
            layout = _get_plotly_layout()
            layout.update(
                height=280, # Altura fija de 280px para simetría
                margin=dict(l=30, r=30, t=30, b=10), # Margen ajustado
                showlegend=False # Se remueve la leyenda para ahorrar espacio
            )
            fig2.update_layout(**layout)
            # Forzar fondo transparente para evitar que Plotly o el layout lo pongan en blanco
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')


            for i, row in agg.iterrows():
                y_val = float(row['BOPD_sum'])
                
                # Modificación: Anotación justo encima de la barra
                y_ann = y_val + (max_y * 0.05) if max_y > 0 else 1 # 5% sobre el valor o un valor mínimo
                
                font_dict = {'size': 12, 'color': 'black'} # Color de fuente por defecto
                if COLOR_FONDO_OSCURO:
                    font_dict['color'] = COLOR_FUENTE

                fig2.add_annotation(
                    x=row['RunLifeBucket'],
                    y=y_ann, # Posición ajustada
                    text=f"{int(row['Pozos'])}",
                    showarrow=False,
                    font=font_dict,
                    align='center',
                    # Removidos el bgcolor/bordercolor para que sea un texto flotante y limpio.
                    bgcolor='rgba(0,0,0,0)', 
                    bordercolor='rgba(0,0,0,0)', 
                    opacity=1,
                    valign='bottom'
                )

            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info('No hay datos de RUN o de FORMA9 disponibles para el filtro actual.')

def show_resumen():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

    # Hero title similar to INDICADORES.py
    try:
        fecha_display = st.session_state.get('fecha_eval_resumen', get_last_day_of_previous_month())
        try:
            fecha_str = pd.to_datetime(fecha_display).strftime('%d %b %Y')
        except Exception:
            fecha_str = str(fecha_display)
    except Exception:
        fecha_str = ''

    # Cargar logo via helper (fallback a imagen remota)
    try:
        from ui_helpers import get_logo_img_tag
        logo_html = get_logo_img_tag(width=100, style='height:80px; filter: drop-shadow(0 0 10px rgba(200, 43, 150, 0.5));')
    except Exception:
        logo_html = "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='100'/>"

    hero_html = f"""
    <div class='dashboard-header'>
        <div style='display:flex; align-items:center; justify-content:space-between; position:relative; z-index:10;'>
            <div style='display:flex; align-items:center; gap: 2rem;'>
                <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 0 30px rgba(0, 242, 255, 0.1);">
                    {logo_html}
                </div>
                <div>
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.7rem; color: var(--neon-cyan); letter-spacing: 3px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; opacity: 0.8;">
                        Public Analytics Node
                    </div>
                    <div class='header-title'>INDICADORES <span style="color: var(--neon-cyan);">ALS</span></div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-family: 'Inter', sans-serif; font-size: 0.6rem; color: #94a3b8; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">
                    Fecha de Evaluación
                </div>
                <div class='header-date'>{fecha_str}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    if 'df_bd_calculated' not in st.session_state: st.session_state['df_bd_calculated'] = None
    if 'df_forma9_calculated' not in st.session_state: st.session_state['df_forma9_calculated'] = None
    if 'resumen_publico_calculated' not in st.session_state: st.session_state['resumen_publico_calculated'] = False
    if 'fecha_eval_resumen' not in st.session_state: st.session_state['fecha_eval_resumen'] = get_last_day_of_previous_month()
    
    # --- CONTROL DE ESTADO DE FILTROS ---
    if 'filters_expanded' not in st.session_state: st.session_state['filters_expanded'] = True

    def _collapse_filters():
        st.session_state['filters_expanded'] = False

    # Intentar cargar datos desde saved_uploads o descargar desde enlaces por defecto
    upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    f9_path = os.path.join(upload_dir, 'forma9_online.xlsx')
    bd_path = os.path.join(upload_dir, 'bd_online.xlsx')

    # Si no hay datos en session_state, intentar leer desde CACHÉ PRIMERO
    if st.session_state.get('df_forma9_calculated') is None or st.session_state.get('df_bd_calculated') is None:
        cached_data = load_cached_data()
        loaded = False
        
        if cached_data:
            try:
                st.session_state['df_bd_calculated'] = cached_data['df_bd']
                st.session_state['df_forma9_calculated'] = cached_data['df_forma9']
                # Sincronizar fecha si está disponible
                if 'fecha_evaluacion' in cached_data:
                    st.session_state['fecha_eval_resumen'] = cached_data['fecha_evaluacion']
                loaded = True
                st.toast(f"⚡ Datos cargados desde memoria caché ({cached_data.get('fecha_evaluacion', 'Fecha desc.')})")
            except Exception as e:
                st.warning(f"Error al aplicar datos de caché: {e}")
                loaded = False
        
        # Si no funcionó la caché, intentar leer desde disco (saved_uploads)
        if not loaded:
            try:
                if os.path.exists(f9_path) and os.path.exists(bd_path):
                    try:
                        with open(f9_path, 'rb') as f:
                            st.session_state['df_forma9_calculated'] = _read_simple(f)
                        with open(bd_path, 'rb') as f:
                            st.session_state['df_bd_calculated'] = _read_simple(f)
                        loaded = True
                    except Exception:
                        loaded = False
            except Exception:
                loaded = False

        # Si no se pudieron leer, intentar descargar desde los enlaces por defecto
        if not loaded:
            default_f9 = "https://1drv.ms/x/c/06cc4035ad46ff97/IQAlCua1BGOXRbcSzUY0OVyzAS8KOoDNxuvUqrsORhjMcKM?e=o8FZyJ"
            default_bd = "https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=P0xf75"
            try:
                ok1 = _download_onedrive(default_f9, f9_path)
                ok2 = _download_onedrive(default_bd, bd_path)
                if ok1 and ok2:
                    try:
                        with open(f9_path, 'rb') as f:
                            st.session_state['df_forma9_calculated'] = _read_simple(f)
                        with open(bd_path, 'rb') as f:
                            st.session_state['df_bd_calculated'] = _read_simple(f)
                        loaded = True
                    except Exception as e:
                        st.warning(f"No se pudieron leer los archivos descargados: {e}")
                else:
                    st.warning('No se pudieron descargar los archivos por defecto; revisa conectividad o enlaces.')
            except Exception as e:
                st.warning(f"Error al descargar archivos por defecto: {e}")

    df_bd = st.session_state.get('df_bd_calculated')
    df_f9 = st.session_state.get('df_forma9_calculated')

    # Normalizar silenciosamente columnas 'FECHA' (sin mostrar diagnóstico)
    try:
        def _silent_fix_fecha(df):
            if df is None:
                return df
            try:
                cols = [c for c in df.columns if 'FECHA' in str(c).upper()]
                if not cols:
                    return df
                col = cols[0]
                import pandas as _pd
                if not _pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = _pd.to_datetime(df[col], dayfirst=True, errors='coerce', infer_datetime_format=True)
            except Exception:
                pass
            return df

        df_bd = _silent_fix_fecha(df_bd)
        df_f9 = _silent_fix_fecha(df_f9)
    except Exception:
        pass

    # Validar que los DataFrames contengan columnas mínimas esperadas
    def _has_required_cols_df_forma9(df):
        if df is None: return False
        cols = [str(c).upper() for c in df.columns]
        return any('FECHA' in c for c in cols) and any('POZO' in c for c in cols)

    def _has_required_cols_df_bd(df):
        if df is None: return False
        cols = [str(c).upper() for c in df.columns]
        return any('FECHA' in c for c in cols) and any('POZO' in c for c in cols)

    data_ok = True
    if not _has_required_cols_df_forma9(df_f9) or not _has_required_cols_df_bd(df_bd):
        data_ok = False
        st.error('Los archivos cargados parecen no contener las columnas mínimas esperadas (FECHA, POZO).')
        try:
            # Mostrar información de archivos en saved_uploads para diagnóstico
            upload_dir = os.path.join(os.getcwd(), 'saved_uploads')
            f9_path = os.path.join(upload_dir, 'forma9_online.xlsx')
            bd_path = os.path.join(upload_dir, 'bd_online.xlsx')
            info_lines = []
            if os.path.exists(f9_path):
                info_lines.append(f"FORMA9: {f9_path} — {os.path.getsize(f9_path)} bytes")
            else:
                info_lines.append("FORMA9: no existe en saved_uploads")
            if os.path.exists(bd_path):
                info_lines.append(f"BD: {bd_path} — {os.path.getsize(bd_path)} bytes")
            else:
                info_lines.append("BD: no existe en saved_uploads")
            st.info('\n'.join(info_lines))
        except Exception:
            pass

        # Botón para forzar re-descarga desde los enlaces por defecto
        if st.button('🔁 Forzar redescarga desde OneDrive (sobrescribir)', key='force_redownload'):
            default_f9 = "https://1drv.ms/x/c/06cc4035ad46ff97/IQAlCua1BGOXRbcSzUY0OVyzAS8KOoDNxuvUqrsORhjMcKM?e=o8FZyJ"
            default_bd = "https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=P0xf75"
            try:
                _download_onedrive(default_f9, f9_path)
                _download_onedrive(default_bd, bd_path)
                st.success('Intentada redescarga. Pulsa nuevamente "Calcular Datos Iniciales".')
                st.experimental_rerun()
            except Exception as e:
                st.error(f'Error al intentar redescargar: {e}')


    # Fecha por defecto: último día del mes anterior (AHORA EDITABLE)
    default_date = get_last_day_of_previous_month()
    
    # Usar la fecha del session_state si existe, sino usar la fecha por defecto
    if st.session_state.get('fecha_eval_resumen') is None:
        st.session_state['fecha_eval_resumen'] = default_date
    
    fecha_eval = st.session_state.get('fecha_eval_resumen', default_date)
    fecha_fmt = pd.to_datetime(fecha_eval).strftime('%d %b %Y')

    # --- SECCIÓN DE FILTROS Y FECHA EDITABLE (MINIMIZABLE) ---
    # --- SECCIÓN DE FILTROS Y FECHA EDITABLE (MINIMIZABLE) ---
    with st.expander("🔍 Filtros y Parámetros", expanded=st.session_state['filters_expanded']):
        # Inicializar filtros únicos
        if 'unique_bloques_resumen' not in st.session_state:
            st.session_state['unique_bloques_resumen'] = ['TODOS']
        if 'unique_campos_resumen' not in st.session_state:
            st.session_state['unique_campos_resumen'] = ['TODOS']
        if 'unique_proveedores_resumen' not in st.session_state:
            st.session_state['unique_proveedores_resumen'] = ['TODOS']
        
        # Crear columnas para los filtros (2 filas)
        col_fecha, col_activo, col_als, col_bloque = st.columns(4)
        col_campo, col_proveedor, _, _ = st.columns(4)
        
        with col_fecha:
            # Fecha editable
            new_fecha = st.date_input(
                "📅 Fecha de Evaluación",
                value=fecha_eval,
                key="fecha_eval_input"
            )
            st.session_state['fecha_eval_resumen'] = new_fecha
            fecha_eval = new_fecha
            fecha_fmt = pd.to_datetime(fecha_eval).strftime('%d %b %Y')
        
        # ===== FILTROS PROGRESIVOS =====
        # Inicializar valores de filtros si no existen
        if 'resumen_activo_filter' not in st.session_state:
            st.session_state['resumen_activo_filter'] = 'TODOS'
        if 'resumen_als_filter' not in st.session_state:
            st.session_state['resumen_als_filter'] = 'TODOS'
        if 'resumen_bloque_filter' not in st.session_state:
            st.session_state['resumen_bloque_filter'] = 'TODOS'
        if 'resumen_campo_filter' not in st.session_state:
            st.session_state['resumen_campo_filter'] = 'TODOS'
        if 'resumen_proveedor_filter' not in st.session_state:
            st.session_state['resumen_proveedor_filter'] = 'TODOS'
        
        # Crear dataframe temporal para filtros progresivos
        df_filter_temp = df_bd.copy()
        
        # 1. FILTRO DE ACTIVO
        with col_activo:
            unique_activos = sorted(df_filter_temp['ACTIVO'].dropna().unique().tolist()) if 'ACTIVO' in df_filter_temp.columns else []
            activo_options = ['TODOS'] + unique_activos
            
            st.session_state['resumen_activo_filter'] = st.selectbox(
                "🏭 Activo",
                options=activo_options,
                index=activo_options.index(st.session_state['resumen_activo_filter']) if st.session_state['resumen_activo_filter'] in activo_options else 0,
                key='activo_resumen_select'
            )
        
        # Aplicar filtro de Activo
        if st.session_state['resumen_activo_filter'] != 'TODOS' and 'ACTIVO' in df_filter_temp.columns:
            df_filter_temp = df_filter_temp[df_filter_temp['ACTIVO'] == st.session_state['resumen_activo_filter']]
        
        # 2. FILTRO DE ALS
        with col_als:
            unique_als = sorted(df_filter_temp['ALS'].dropna().unique().tolist()) if 'ALS' in df_filter_temp.columns else []
            als_options = ['TODOS'] + unique_als
            
            # Si el valor actual no está en las opciones, resetear a TODOS
            if st.session_state['resumen_als_filter'] not in als_options:
                st.session_state['resumen_als_filter'] = 'TODOS'
            
            st.session_state['resumen_als_filter'] = st.selectbox(
                "⚙️ ALS",
                options=als_options,
                index=als_options.index(st.session_state['resumen_als_filter']) if st.session_state['resumen_als_filter'] in als_options else 0,
                key='als_resumen_select'
            )
        
        # Aplicar filtro de ALS
        if st.session_state['resumen_als_filter'] != 'TODOS' and 'ALS' in df_filter_temp.columns:
            df_filter_temp = df_filter_temp[df_filter_temp['ALS'] == st.session_state['resumen_als_filter']]
        
        # 3. FILTRO DE BLOQUE
        with col_bloque:
            unique_bloques = sorted(df_filter_temp['BLOQUE'].dropna().unique().tolist()) if 'BLOQUE' in df_filter_temp.columns else []
            bloque_options = ['TODOS'] + unique_bloques
            
            if st.session_state['resumen_bloque_filter'] not in bloque_options:
                st.session_state['resumen_bloque_filter'] = 'TODOS'
            
            st.session_state['resumen_bloque_filter'] = st.selectbox(
                "🎲 Bloque",
                options=bloque_options,
                index=bloque_options.index(st.session_state['resumen_bloque_filter']) if st.session_state['resumen_bloque_filter'] in bloque_options else 0,
                key='bloque_resumen_select'
            )
        
        # Aplicar filtro de Bloque
        if st.session_state['resumen_bloque_filter'] != 'TODOS' and 'BLOQUE' in df_filter_temp.columns:
            df_filter_temp = df_filter_temp[df_filter_temp['BLOQUE'] == st.session_state['resumen_bloque_filter']]
        
        # 4. FILTRO DE CAMPO
        with col_campo:
            unique_campos = sorted(df_filter_temp['CAMPO'].dropna().unique().tolist()) if 'CAMPO' in df_filter_temp.columns else []
            campo_options = ['TODOS'] + unique_campos
            
            if st.session_state['resumen_campo_filter'] not in campo_options:
                st.session_state['resumen_campo_filter'] = 'TODOS'
            
            st.session_state['resumen_campo_filter'] = st.selectbox(
                "🎴 Campo",
                options=campo_options,
                index=campo_options.index(st.session_state['resumen_campo_filter']) if st.session_state['resumen_campo_filter'] in campo_options else 0,
                key='campo_resumen_select'
            )
        
        # Aplicar filtro de Campo
        if st.session_state['resumen_campo_filter'] != 'TODOS' and 'CAMPO' in df_filter_temp.columns:
            df_filter_temp = df_filter_temp[df_filter_temp['CAMPO'] == st.session_state['resumen_campo_filter']]
        
        # 5. FILTRO DE PROVEEDOR
        with col_proveedor:
            unique_proveedores = sorted(df_filter_temp['PROVEEDOR'].dropna().unique().tolist()) if 'PROVEEDOR' in df_filter_temp.columns else []
            proveedor_options = ['TODOS'] + unique_proveedores
            
            if st.session_state['resumen_proveedor_filter'] not in proveedor_options:
                st.session_state['resumen_proveedor_filter'] = 'TODOS'
            
            st.session_state['resumen_proveedor_filter'] = st.selectbox(
                "🏢 Proveedor",
                options=proveedor_options,
                index=proveedor_options.index(st.session_state['resumen_proveedor_filter']) if st.session_state['resumen_proveedor_filter'] in proveedor_options else 0,
                key='proveedor_resumen_select'
            )

        # CÁLCULO manual mediante botón (igual que INDICADORES.py)
        col_calc = st.columns([1])[0]
        with col_calc:
            calcular_btn = st.button("🔄 DOBLE CLIP PARA MOSTRAR DATOS", key="calcular_btn_resumen", use_container_width=True, help="Procesar datos y mostrar KPIs", on_click=_collapse_filters)

        # Botón para ver análisis detallado (usar launch_module_path para navegación estable)
        col_analisis = st.columns([1])[0]
        with col_analisis:
            if st.button("📊 Ver Análisis Detallado", key="btn_indicadores_resumen", use_container_width=False):
                try:
                    cwd_files = os.listdir('.')
                    target = None
                    if 'indicadores.py' in cwd_files:
                        target = os.path.abspath('indicadores.py')
                    else:
                        for f in cwd_files:
                            if f.lower() == 'indicadores.py':
                                target = os.path.abspath(f)
                                break
                    if target is None:
                        st.error('No se encontró indicadores.py en el directorio. No se puede abrir el análisis detallado.')
                    else:
                        # Evitar que indicadores.py vuelva a redirigir al resumen
                        try:
                            if 'show_resumen_publico' in st.session_state:
                                st.session_state['show_resumen_publico'] = False
                        except Exception:
                            pass
                        st.session_state['launch_module_path'] = target
                        st.session_state['launch_module_name'] = os.path.splitext(os.path.basename(target))[0]
                        st.rerun()
                except Exception as e:
                    st.error(f'Error al intentar abrir indicadores.py: {e}')

        # Si el botón fue presionado y tenemos los DataFrames, normalizar columnas y marcar calculado
        if calcular_btn:
            if df_bd is None or df_f9 is None:
                st.error('No hay datos disponibles para calcular. Revisa saved_uploads o la conectividad.')
            else:
                try:
                    # Primero limpiar/normalizar con la rutina local
                    processed_f9, processed_bd = _prepare_and_run(df_f9, df_bd, fecha_eval)
                    # Si existe la implementación compartida más fiel (desde INDICADORES), usarla
                    if shared_perform_initial_calculations is not None and processed_f9 is not None and processed_bd is not None:
                        try:
                            proc_f9_2, proc_bd_2 = shared_perform_initial_calculations(processed_f9.copy(), processed_bd.copy(), fecha_eval)
                            # Si la llamada no devolvió None, preferir ese resultado (más cercano a INDICADORES.py)
                            if proc_f9_2 is not None and proc_bd_2 is not None:
                                processed_f9, processed_bd = proc_f9_2, proc_bd_2
                        except Exception:
                            # Si falla, quedarnos con la versión local
                            pass
                    if processed_f9 is None or processed_bd is None:
                        st.error('No se pudieron procesar los datos. Revisa los archivos en saved_uploads.')
                    else:
                        st.session_state['df_bd_calculated'] = processed_bd
                        st.session_state['df_forma9_calculated'] = processed_f9
                        st.session_state['resumen_publico_calculated'] = True
                        st.success('Cálculos iniciales procesados y guardados; ahora se muestran los KPIs.')
                except Exception as e:
                    st.error(f'Error al preparar los datos para cálculo: {e}')

    # Si aún no se ha calculado, detener para evitar mostrar KPIs vacíos
    if not st.session_state.get('resumen_publico_calculated'):
        st.info('Pulsa "Calcular Datos Iniciales" para generar el resumen con los enlaces por defecto.')
        st.stop()

    # Actualizar listas de filtros únicas para usar en los selectboxes
    if 'ACTIVO' in df_bd.columns:
        st.session_state['unique_activos_resumen'] = sorted(df_bd['ACTIVO'].dropna().unique().tolist())
    if 'ALS' in df_bd.columns:
        st.session_state['unique_als_resumen'] = sorted(df_bd['ALS'].dropna().unique().tolist())
    if 'BLOQUE' in df_bd.columns:
        st.session_state['unique_bloques_resumen'] = sorted(df_bd['BLOQUE'].dropna().unique().tolist())
    if 'CAMPO' in df_bd.columns:
        st.session_state['unique_campos_resumen'] = sorted(df_bd['CAMPO'].dropna().unique().tolist())
    if 'PROVEEDOR' in df_bd.columns:
        st.session_state['unique_proveedores_resumen'] = sorted(df_bd['PROVEEDOR'].dropna().unique().tolist())

    # CÁLCULOS
    kpis = _calc_basic_kpis(df_bd, df_f9, fecha_eval)
    
    rl_avg = 0.0
    if 'RUN LIFE' in df_bd.columns:
        v = pd.to_numeric(df_bd['RUN LIFE'], errors='coerce').dropna()
        if not v.empty: rl_avg = float(v.mean())
    
    # --- APLICAR FILTROS (si existen) ---
    df_bd_filtered = df_bd.copy()
    df_f9_filtered = df_f9.copy()
    
    selected_activo = st.session_state.get('resumen_activo_filter', 'TODOS')
    selected_als = st.session_state.get('resumen_als_filter', 'TODOS')
    selected_bloque = st.session_state.get('resumen_bloque_filter', 'TODOS')
    selected_campo = st.session_state.get('resumen_campo_filter', 'TODOS')
    selected_proveedor = st.session_state.get('resumen_proveedor_filter', 'TODOS')
    
    if selected_activo != 'TODOS' and 'ACTIVO' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['ACTIVO'] == selected_activo]
    
    if selected_als != 'TODOS' and 'ALS' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['ALS'] == selected_als]
    
    if selected_bloque != 'TODOS' and 'BLOQUE' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['BLOQUE'] == selected_bloque]
    
    if selected_campo != 'TODOS' and 'CAMPO' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['CAMPO'] == selected_campo]
    
    if selected_proveedor != 'TODOS' and 'PROVEEDOR' in df_bd_filtered.columns:
        df_bd_filtered = df_bd_filtered[df_bd_filtered['PROVEEDOR'] == selected_proveedor]
    
    # Filtrar forma9 por los pozos en bd_filtered
    if not df_bd_filtered.empty and 'POZO' in df_bd_filtered.columns:
        pozos_in_filtered = df_bd_filtered['POZO'].unique()
        df_f9_filtered = df_f9_filtered[df_f9_filtered['POZO'].isin(pozos_in_filtered)]
    
    # Recalcular KPIs con filtros aplicados
    kpis = _calc_basic_kpis(df_bd_filtered, df_f9_filtered, fecha_eval)
    
    rl_avg = 0.0
    if 'RUN LIFE' in df_bd_filtered.columns:
        v = pd.to_numeric(df_bd_filtered['RUN LIFE'], errors='coerce').dropna()
        if not v.empty: rl_avg = float(v.mean())

    rl_eff_avg = 0.0
    if 'RUN_LIFE_EFECTIVO' in df_bd_filtered.columns:
        v_eff = pd.to_numeric(df_bd_filtered['RUN_LIFE_EFECTIVO'], errors='coerce').dropna()
        if not v_eff.empty: rl_eff_avg = float(v_eff.mean())
    
    # Recalcular severidad con filtros (Total de fallas / Pozos con fallas) - Últimos 365 días
    indice_severidad = 0.0
    try:
        if 'POZO' in df_bd_filtered.columns and 'RUN' in df_bd_filtered.columns and 'FECHA_FALLA' in df_bd_filtered.columns:
            # Convertir fecha_eval a date si no lo es ya
            fecha_eval_date = fecha_eval if isinstance(fecha_eval, pd.Timestamp) or hasattr(fecha_eval, 'date') is False else pd.to_datetime(fecha_eval).date()
            if hasattr(fecha_eval, 'date'):
                fecha_eval_date = fecha_eval if hasattr(fecha_eval, 'year') and hasattr(fecha_eval, 'month') and hasattr(fecha_eval, 'day') else pd.to_datetime(fecha_eval).date()
            else:
                fecha_eval_date = pd.to_datetime(fecha_eval).date()
            
            # Filtrar solo las fallas de los últimos 365 días (como en INDICADORES.py)
            # Asegurar que FECHA_FALLA sea datetime
            df_bd_filtered['FECHA_FALLA'] = pd.to_datetime(df_bd_filtered['FECHA_FALLA'], errors='coerce')
            
            pozos_fallados_df = df_bd_filtered[
                (df_bd_filtered['FECHA_FALLA'].dt.date >= fecha_eval_date - timedelta(days=365)) &
                (df_bd_filtered['FECHA_FALLA'].dt.date <= fecha_eval_date)
            ]
            
            if not pozos_fallados_df.empty:
                # Contar fallas por pozo
                fallas_por_pozo = pozos_fallados_df.groupby('POZO')['RUN'].count().reset_index()
                fallas_por_pozo.rename(columns={'RUN': 'Cantidad de Fallas'}, inplace=True)
                
                total_fallas_severidad = fallas_por_pozo['Cantidad de Fallas'].sum()
                num_pozos_fallados = fallas_por_pozo.shape[0]
                indice_severidad = (total_fallas_severidad / num_pozos_fallados) if num_pozos_fallados > 0 else 0.0
    except Exception as e:
        indice_severidad = 0.0
        
    # --- CÁLCULOS DE ÍNDICE DE FALLA ---
    try:
        from indice_falla import calcular_indice_falla_anual
        indice_resumen_df, df_mensual_if = calcular_indice_falla_anual(df_bd_filtered, df_f9_filtered, fecha_eval)
        if_on_raw = None
        if_als_on_raw = None
        try:
            if 'Valor' in indice_resumen_df.columns and 'Indicador' in indice_resumen_df.columns:
                row = indice_resumen_df[indice_resumen_df['Indicador'] == 'Índice de Falla ON']
                if not row.empty:
                    if_on_raw = row['Valor'].values[0]
                
                row_als = indice_resumen_df[indice_resumen_df['Indicador'] == 'Índice de Falla ALS ON']
                if not row_als.empty:
                    if_als_on_raw = row_als['Valor'].values[0]
        except:
            if_on_raw = None
            if_als_on_raw = None
    except Exception as e:
        indice_resumen_df = None
        df_mensual_if = None
        if_on_raw = None
        if_als_on_raw = None
    
    # Convertir porcentaje a número
    def _pctstr_to_float(s):
        try:
            if s is None: return None
            s2 = str(s).strip()
            if s2.endswith('%'):
                s2 = s2.replace('%', '')
            return float(s2.replace(',', '.'))
        except:
            return None
    
    parsed_if_on = _pctstr_to_float(if_on_raw)
    fail_idx = parsed_if_on if parsed_if_on is not None else 0.0
    if_on_str = if_on_raw if if_on_raw is not None else 'N/D'
    if_als_on_str = if_als_on_raw if if_als_on_raw is not None else 'N/D'

    # --- TABLERO DASHBOARD: Fila 1 con 6 KPIs principales (incluyendo severidad) ---
    try:
        selected_als_display = st.session_state.get('resumen_als_filter', 'TODOS')
    except Exception:
        selected_als_display = 'TOTAL'
    
    # Calcular porcentaje de extracción
    total_corridas = kpis['extraidos'] + kpis['running']
    pct_extraccion = (kpis['extraidos'] / total_corridas * 100) if total_corridas > 0 else 0
    
    # Fila 1: 6 KPIs principales (MTBF, Run Life, Índice Falla ON, Índice Falla ALS, Extracción, Pozos ON)
    # Fila 1: 7 KPIs principales (MTBF, Run Life, Run Life Efec, Índice Falla ON, Índice Falla ALS, Extracción, Pozos ON)
    kpi1, kpi2, kpi_new, kpi3, kpi4, kpi5, kpi6 = st.columns([1, 1, 1, 1, 1, 1, 1])
    
    with kpi1: st.markdown(_render_top_kpi("⏱️", "MTBF Estimado", kpis['mtbf'], "días"), unsafe_allow_html=True)
    with kpi2: st.markdown(_render_top_kpi("📈", "Run Life Prom.", f"{rl_avg:.1f}", "días"), unsafe_allow_html=True)
    with kpi_new: st.markdown(_render_top_kpi("✅", "Run Life Efec.", f"{rl_eff_avg:.1f}", "días"), unsafe_allow_html=True)
    with kpi3: st.markdown(_render_top_kpi("📉", "Índice Falla ON", if_on_str, ""), unsafe_allow_html=True)
    with kpi4: st.markdown(_render_top_kpi("🎯", "Índice Falla ALS", if_als_on_str, ""), unsafe_allow_html=True)
    with kpi5: st.markdown(_render_top_kpi("🔄", "Extracción %", f"{pct_extraccion:.1f}", "%"), unsafe_allow_html=True)
    with kpi6: st.markdown(_render_top_kpi("📊", "Equipos ON", kpis['pozos_on'], "Rns"), unsafe_allow_html=True)

    # --- NUEVA SECCIÓN: ESTADO DE LA CAMPAÑA (RESUMEN) ---
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Asegurar fecha timestamp
    try:
        fecha_eval_ts = pd.to_datetime(fecha_eval)
        anio_campana = fecha_eval_ts.year
    except:
        anio_campana = datetime.now().year
        fecha_eval_ts = pd.Timestamp(datetime.now())

    # Contenedor visual Cabecera Premium
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, rgba(0, 242, 255, 0.1), transparent); 
        padding: 12px 20px; 
        border-left: 5px solid #00f2ff; 
        border-radius: 8px; 
        margin: 1.5em 0;
        box-shadow: -10px 0 20px rgba(0, 242, 255, 0.1);
        display: flex;
        align-items: center;
        gap: 15px;
    ">
        <div style="
            width: 10px; height: 10px; background: #00f2ff; border-radius: 50%;
            box-shadow: 0 0 10px #00f2ff; animation: pulse 2s infinite;
        "></div>
        <h4 style='
            font-size:1.2rem; font-weight:900; margin:0; 
            color:#fff; letter-spacing: 3px; text-transform: uppercase;
            font-family: "Outfit", sans-serif;
        '>
             Módulo de Campaña <span style="color:#00f2ff;">{anio_campana}</span>
        </h4>
        <style> @keyframes pulse {{ 0% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.4; }} }} </style>
    </div>
    """, unsafe_allow_html=True)

    # Lógica de cálculo (Copia adaptada de INDICADORES.py)
    df_campana = df_bd_filtered[pd.to_datetime(df_bd_filtered['FECHA_RUN'], errors='coerce').dt.year == anio_campana].copy()
    
    col_camp_1, col_camp_2 = st.columns(2)
    
    if df_campana.empty:
        st.info(f"No hay registros de campaña para {anio_campana}.")
    else:
        df_campana['RUN'] = pd.to_numeric(df_campana['RUN'], errors='coerce').fillna(0)
        df_nuevos = df_campana[df_campana['RUN'] == 1].copy()
        df_interv = df_campana[df_campana['RUN'] > 1].copy()

        def _render_campaign_card(df_g, title, color_hex):
            if df_g.empty:
                return f"""<div style="background:rgba(255,255,255,0.02); border:1px solid {color_hex}44; border-radius:12px; padding:20px; text-align:center; opacity:0.6;">
                    <div style="color:{color_hex}; font-weight:bold; letter-spacing:1px;">{title.upper()}</div>
                    <div style="font-size:0.8rem; margin-top:5px; color:#888;">SIN REGISTROS ACTIVOS</div>
                </div>"""
            
            total = df_g['POZO'].nunique()
            df_g['FECHA_FALLA_DT'] = pd.to_datetime(df_g['FECHA_FALLA'], errors='coerce')
            df_g['FECHA_PULL_DT'] = pd.to_datetime(df_g['FECHA_PULL'], errors='coerce')
            
            fallados = df_g[(df_g['FECHA_FALLA_DT'].notna()) & (df_g['FECHA_FALLA_DT'] <= fecha_eval_ts)]['POZO'].nunique()
            operativos = df_g[
                ((df_g['FECHA_PULL_DT'].isna()) | (df_g['FECHA_PULL_DT'] > fecha_eval_ts)) &
                ((df_g['FECHA_FALLA_DT'].isna()) | (df_g['FECHA_FALLA_DT'] > fecha_eval_ts))
            ]['POZO'].nunique()
            
            pozos_ids = df_g['POZO'].unique()
            df_f9_sub = df_f9_filtered[df_f9_filtered['POZO'].isin(pozos_ids)].copy()
            prod_val = 0.0
            if not df_f9_sub.empty:
                df_f9_sub['FECHA_FORMA9'] = pd.to_datetime(df_f9_sub['FECHA_FORMA9'], errors='coerce')
                df_last = df_f9_sub.sort_values('FECHA_FORMA9').groupby('POZO').last()
                c_bopd = next((c for c in df_last.columns if 'BOPD' in str(c).upper()), None)
                if c_bopd:
                    prod_val = pd.to_numeric(df_last[c_bopd], errors='coerce').sum()
            
            return f"""
            <div style="
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(2, 6, 23, 1));
                border: 1px solid {color_hex}44;
                border-radius: 20px;
                padding: 22px;
                position: relative;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                transition: transform 0.3s;
            ">
                <div style="position:absolute; top:0; right:0; width:80px; height:80px; background:radial-gradient(circle at 100% 0%, {color_hex}33, transparent 70%);"></div>
                
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px;">
                    <div>
                        <div style="color:{color_hex}; font-weight:900; font-size:1.1rem; letter-spacing:1px; font-family:'Outfit';">{title.upper()}</div>
                        <div style="font-size:0.7rem; color:#64748b; font-weight:bold; margin-top:2px;">OPERACIÓN TÁCTICA</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.6rem; font-weight:900; color:#fff; line-height:1;">{total}</div>
                        <div style="font-size:0.6rem; color:{color_hex}; font-weight:bold; letter-spacing:1px;">CORRIDAS</div>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; background:rgba(255,255,255,0.03); padding:15px; border-radius:15px; border:1px solid rgba(255,255,255,0.05);">
                    <div style="text-align:center;">
                        <div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px; font-weight:bold;">ACTIVOS</div>
                        <div style="font-size:1.3rem; font-weight:900; color:#00ff9d;">{operativos}</div>
                    </div>
                    <div style="text-align:center; border-left:1px solid rgba(255,255,255,0.1); border-right:1px solid rgba(255,255,255,0.1);">
                        <div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px; font-weight:bold;">FALLADOS</div>
                        <div style="font-size:1.3rem; font-weight:900; color:#ff3e3e;">{fallados}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:0.6rem; color:#94a3b8; margin-bottom:4px; font-weight:bold;">BOPD</div>
                        <div style="font-size:1.3rem; font-weight:900; color:#00f2ff;">{prod_val:,.0f}</div>
                    </div>
                </div>
                
                <div style="margin-top:15px; height:4px; background:rgba(255,255,255,0.05); border-radius:2px; overflow:hidden;">
                    <div style="width:{(operativos/total*100) if total>0 else 0}%; height:100%; background:linear-gradient(90deg, {color_hex}, #fff); box-shadow:0 0 10px {color_hex};"></div>
                </div>
            </div>
            """

        with col_camp_1:
            st.markdown(_render_campaign_card(df_nuevos, "Pozos Nuevos", "#00cfff"), unsafe_allow_html=True)
        with col_camp_2:
            st.markdown(_render_campaign_card(df_interv, "Intervenciones", "#ff00ff"), unsafe_allow_html=True)

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # --- LAYOUT PRINCIPAL (0.8 - 0.2) ---
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    col_main_content, col_estado_main = st.columns([0.8, 0.2])

    with col_main_content:
        # Fila 1: ECharts Dashboard (Top)
        try:
            df_monthly = generar_resumen_mensual(df_bd_filtered, df_f9_filtered, fecha_eval)
            if not df_monthly.empty:
                col_perf, col_rl_pz = st.columns([0.5, 0.5])
                with col_perf:
                    with st.container(border=True): render_premium_echarts(df_monthly, "Análisis de Performance")
                with col_rl_pz:
                    with st.container(border=True):
                        sub1, sub2 = st.columns(2)
                        with sub1: render_premium_echarts_run_life(df_monthly, "Tiempo de Vida")
                        with sub2: render_premium_echarts_pozos(df_monthly, "Operatividad")
        except: pass

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        # Fila 2: Mapa y KPIs Secundarios
        col_m, col_rest = st.columns([0.6, 0.4])
        with col_m:
            with st.container(border=True):
                st.markdown("##### 🗺️ Mapa Táctico")
                try:
                    from kpis import mostrar_kpis
                    reporte_run_life = pd.DataFrame({'Categoría': ['Tiempo de Vida Promedio (Fallados+Ext)'], 'Valor': [rl_avg]})
                    mostrar_kpis(df_bd=df_bd_filtered, reporte_run_life=reporte_run_life, indice_resumen_df=indice_resumen_df if 'indice_resumen_df' in dir() else None, mtbf_global=kpis['mtbf'], df_forma9=df_f9_filtered, fecha_evaluacion=fecha_eval)
                except: st.info("Mapa no disponible")
        
        with col_rest:
            # Severidad
            with st.container(border=True):
                st.markdown("##### ⚡ Severidad")
                try:
                    fig_sev = generar_grafico_severidad_acelerador(indice_severidad)
                    st.plotly_chart(fig_sev, use_container_width=True)
                except: pass
            # Radar
            with st.container(border=True):
                st.markdown("##### 🕸️ Estado")
                try:
                    fig2 = generar_grafico_radar(kpis)
                    st.plotly_chart(fig2, use_container_width=True)
                except: pass
            # BOPD vs Run Life
            with st.container(border=True):
                st.markdown("##### 📌 BOPD vs Run Life")
                try: render_bopd_vs_runlife(df_bd_filtered, df_f9_filtered, fecha_eval)
                except: pass

    with col_estado_main:
        # --- ESTADO OPERACIONAL EN COLUMNA VERTICAL (Derecha 0.2) ---
        st.markdown("#### 📊 Estado Operacional")
        
        # Botones apilados verticalmente
        st.markdown(_render_neon_button("🟢", "Running", kpis['running'], "neon-success"), unsafe_allow_html=True)
        st.markdown(_render_neon_button("🔴", "Fallados", kpis['fallados'], "neon-danger"), unsafe_allow_html=True)
        st.markdown(_render_neon_button("💡", "Pozos ON", kpis['pozos_on'], "neon-info"), unsafe_allow_html=True)
        st.markdown(_render_neon_button("⚫", "Pozos OFF", kpis['pozos_off'], "neon-neutral"), unsafe_allow_html=True)
        st.markdown(_render_neon_button("🔧", "Extraídos", kpis['extraidos'], "neon-danger"), unsafe_allow_html=True)
        st.markdown(_render_neon_button("📊", "Total Corridas", str(kpis['extraidos']+kpis['running']), "neon-info"), unsafe_allow_html=True)


if __name__ == '__main__':
    show_resumen()