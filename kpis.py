import streamlit as st
import pandas as pd
from graphviz import Digraph
import datetime 
import pandas as pd 
from theme import get_colors
import mtbf as mtbf_mod

_colors = get_colors()
COLOR_PRINCIPAL = _colors.get('primary', '#00ff99')
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = _bg_raw or '#1a1a2e'
COLOR_FONDO_CONTENEDOR = _colors.get('container_bg', 'rgba(25, 25, 40, 0.7)')
COLOR_SOMBRA = 'transparent'

# Colores adicionales específicos locales (si se requieren tonos distintos se definen aquí)
# Text colors: prefer theme text if available, otherwise good defaults
COLOR_TEXTO_DATOS = _colors.get('muted', '#b3f0cc')
COLOR_TEXTO_PRINCIPAL = _colors.get('text_on_primary', _colors.get('text', '#ffffff'))

# Usaremos la implementación real de MTBF desde el módulo `mtbf.py` (importado como mtbf_mod)

def mostrar_kpis(df_bd, reporte_runes=None, reporte_run_life=None, indice_resumen_df=None, mtbf_global=None, mtbf_als=None, df_forma9=None, fecha_evaluacion=None):
    # Contenedor para el filtro y el título (código omitido por brevedad)
    with st.container():
        # Title and brief description using native Streamlit components so they adapt to theme
        st.header("KPIs")  
        als_options = ['ESP'] + sorted(df_bd['ALS'].dropna().unique().tolist()) if 'ALS' in df_bd.columns else ['TODOS']
        selected_als = st.selectbox(
            'Filtro por Sistema de Levantamiento (ALS):',
            als_options,
            key='kpis_als_filter_cyber',
            index=0,
            help='Selecciona un sistema ALS para refinar el análisis',
        )
        if selected_als != 'ESP':
            df_bd_als = df_bd[df_bd['ALS'] == selected_als]
        else:
            df_bd_als = df_bd.copy()

    # Configuración del mapa conceptual
    dot = Digraph(comment='Conceptual Map', format='png')
    # Solo establecer bgcolor si existe un color concreto, sino dejar por defecto
    dot_attr_kwargs = {'rankdir':'LR', 'splines':'polyline', 'ranksep':'0.5', 'nodesep':'0.5'}
    # Siempre establecer un bgcolor explícito: usar el color del tema si existe,
    # de lo contrario usar 'transparent' para que el contenedor de Streamlit
    # muestre su propio fondo.
    dot_attr_kwargs['bgcolor'] = COLOR_FONDO_OSCURO if COLOR_FONDO_OSCURO else 'transparent'
    dot.attr(**dot_attr_kwargs)

    # Paleta de Nodos
    kpi_node_colors = {
    'KPIs': COLOR_PRINCIPAL, # Mantiene el color principal del tema (asumo que es claro/cian)
    'RL': '#00F5FF',         # 1. Run Life - Verde Bosque Profundo
    'MTBF': '#A1039D',       # 2. MTBF - Púrpura Oscuro / Berenjena
    'IF': '#5EFF00',         # 3. Índice de Falla - Rojo Ladrillo / Óxido Oscuro (Alerta Sutil)
    'RUNs': '#0011D1',       # 4. Corridas - Azul Marino Sólido (Diferente a ON)
    'ON': '#0011D1',         # 5. Pozos ON - Dorado Opaco / Oliváceo
    'OFF': '#0011D1',        # 6. Pozos OFF - Gris Oscuro (Visible, no negro)
    }
    
    # Estilo de nodos de Concepto
    node_style_main = {
        'shape': 'box', 
        'style': 'filled,bold,rounded',
        'fontname': 'Courier-Bold', 
        'fontsize': '20',       
        'fontcolor': COLOR_TEXTO_PRINCIPAL, 
        'penwidth': '2',        
        'color': COLOR_PRINCIPAL,
    }

    # === SOLUCIÓN: Definición de estilo para el nodo ROOT ===
    root_style = node_style_main.copy()
    root_style['fillcolor'] = COLOR_PRINCIPAL
    root_style['fontcolor'] = COLOR_TEXTO_PRINCIPAL if COLOR_TEXTO_PRINCIPAL else "#000000"
    root_style['penwidth'] = '3'
    root_style['color'] = "#ffffff"

    
    # Estilo de nodos de Datos - Cyberpunk (más angosto)
    node_style_data = {
        'shape': 'box',
        'style': 'filled,rounded',
        'fontname': 'Courier',
        'fontsize': '18',  # Reducido para nodos más angostos
        'fontcolor': "#ffffff",
        'fillcolor': COLOR_FONDO_CONTENEDOR,
        'penwidth': '2',
        'color': COLOR_PRINCIPAL,
        'width': '1.2',   # Menor ancho
        'margin': '0.03,0.2', # Menor margen
    }
    
    # Nodos principales
    # LÍNEA CORREGIDA: Usando el diccionario de estilo 'root_style'
    dot.node('KPIs', label=' KPIS ', **root_style) 
    
    # Nodos de Nivel 1 (KPIs)
    node_style_lvl1 = node_style_main.copy()
    node_style_lvl1['shape'] = 'box'
    node_style_lvl1['fontsize'] = '20'
    node_style_lvl1['fontcolor'] = COLOR_TEXTO_PRINCIPAL
    
    dot.node('RUNs', label='RUNS', fillcolor=kpi_node_colors['RUNs'], **node_style_lvl1)
    dot.node('RL', label='RUN LIFE ', fillcolor=kpi_node_colors['RL'], **node_style_lvl1)
    dot.node('MTBF', label='MTBF ', fillcolor=kpi_node_colors['MTBF'], **node_style_lvl1)
    dot.node('IF', label='FAILURE INDEX', fillcolor=kpi_node_colors['IF'], **node_style_lvl1)
    
    # [ --- Lógica de Cálculo de Datos (Omitida por brevedad, pero debe estar aquí) --- ]
    # Se asume que las variables *_label están definidas.
    
    # (Resto de la lógica de cálculo y definición de labels...)
    # ----------------------------------------------------------------------------------
    if fecha_evaluacion is None:
        fecha_evaluacion = datetime.datetime.now()
    else:
        try:
            fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
        except Exception:
            fecha_evaluacion = datetime.datetime.now()
            
    # Usar la función real de cálculo de MTBF
    try:
        mtbf_als_val, _ = mtbf_mod.calcular_mtbf(df_bd_als, fecha_evaluacion)
    except Exception:
        mtbf_als_val = None
    try:
        mtbf_total_val, _ = mtbf_mod.calcular_mtbf(df_bd, fecha_evaluacion)
    except Exception:
        mtbf_total_val = None

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).date()
    df_bd['FECHA_RUN_DATE'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce').dt.date
    df_bd['FECHA_PULL_DATE'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce').dt.date
    df_bd['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce').dt.date

    def filtrar_als(df, als):
        if als and als != 'TODOS' and 'ALS' in df.columns:
            return df[df['ALS'] == als].copy()
        return df.copy()

    def calc_running(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_fallados(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].notna()) & (df['FECHA_FALLA_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_operativos(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].isna() | (df['FECHA_FALLA_DATE'] > fecha_eval)) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]

    df_bd_als_calc = filtrar_als(df_bd, selected_als)
    run_todos = calc_running(df_bd, fecha_eval_date)
    fallado_todos = calc_fallados(df_bd, fecha_eval_date)
    operativos_todos = calc_operativos(df_bd, fecha_eval_date)
    run_als = calc_running(df_bd_als_calc, fecha_eval_date)
    fallado_als = calc_fallados(df_bd_als_calc, fecha_eval_date)
    operativos_als = calc_operativos(df_bd_als_calc, fecha_eval_date)

    run_label = f"TOTAL: {run_todos}\n{selected_als}: {run_als}"
    fallado_label = f"TOTAL: {fallado_todos}\n{selected_als}: {fallado_als}"
    operativos_label = f"TOTAL: {operativos_todos}\n{selected_als}: {operativos_als}"

    if df_forma9 is not None:
        df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
        df_forma9['DIAS TRABAJADOS'] = pd.to_numeric(df_forma9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
        if 'SISTEMA ALS' in df_forma9.columns:
            df_forma9 = df_forma9.rename(columns={'SISTEMA ALS': 'ALS'})
        
        df_forma9_eval = df_forma9[
            (df_forma9['FECHA_FORMA9'].dt.date >= (fecha_eval_date - pd.Timedelta(days=30))) &
            (df_forma9['FECHA_FORMA9'].dt.date <= fecha_eval_date)
        ]
        
        if selected_als != 'TODOS' and 'ALS' in df_forma9_eval.columns:
            df_forma9_eval_als = df_forma9_eval[df_forma9_eval['ALS'] == selected_als]
            pozos_on_als = df_forma9_eval_als[df_forma9_eval_als['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
            pozos_on_todos = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
        else:
            pozos_on_todos = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
            pozos_on_als = pozos_on_todos
        
        pozos_off_todos = operativos_todos - pozos_on_todos if operativos_todos >= pozos_on_todos else 0
        pozos_off_als = operativos_als - pozos_on_als if operativos_als >= pozos_on_als else 0
        
        on_label = f"TOTAL: {pozos_on_todos}\n{selected_als}: {pozos_on_als}"
        off_label = f"TOTAL: {pozos_off_todos}\n{selected_als}: {pozos_off_als}"
        
        rl_todos = 0
        rl_als = 0
        if reporte_run_life is not None and not reporte_run_life.empty:
            val = reporte_run_life.loc[reporte_run_life['Categoría'] == 'Run Life Apagados + Fallados', 'Valor']
            if not val.empty:
                rl_todos = float(val.values[0])
        
        if selected_als != 'TODOS' and 'ALS' in df_bd.columns:
            fecha_eval = pd.to_datetime(fecha_evaluacion)
            df_bd_als_rl = df_bd[df_bd['ALS'] == selected_als].copy()
            df_bd_als_rl['FECHA_PULL_DATE'] = pd.to_datetime(df_bd_als_rl['FECHA_PULL'], errors='coerce')
            df_bd_als_rl['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd_als_rl['FECHA_FALLA'], errors='coerce')
            df_bd_als_rl['FECHA_RUN_DATE'] = pd.to_datetime(df_bd_als_rl['FECHA_RUN'], errors='coerce')
            df_bd_als_eval = df_bd_als_rl[df_bd_als_rl['FECHA_RUN_DATE'].dt.date <= fecha_eval.date()].copy()
            run_life_als = df_bd_als_eval[(df_bd_als_eval['FECHA_PULL_DATE'].notna()) | (df_bd_als_eval['FECHA_FALLA_DATE'].notna())]['RUN LIFE'].mean()
            if pd.notna(run_life_als):
                rl_als = float(run_life_als)
        rl_label = f"TOTAL: {rl_todos:.2f} Días\n{selected_als}: {rl_als:.2f} Días"
    else:
        on_label = "TOTAL: N/D\nALS: N/D"
        off_label = "TOTAL: N/D\nALS: N/D"
        rl_label = "TOTAL: N/D\nALS: N/D"

    mtbf_total_str = f"{mtbf_total_val:.2f}" if mtbf_total_val is not None else "N/D"
    mtbf_als_str = f"{mtbf_als_val:.2f}" if mtbf_als_val is not None else "N/D"
    mtbf_label = f"TOTAL: {mtbf_total_str} Días\n{selected_als}: {mtbf_als_str} Días"
    
    def get_if_val(df, indicador, als=None):
        if df is not None and 'Indicador' in df.columns and 'Valor' in df.columns:
            if als and als != 'TODOS' and 'ALS' in df.columns:
                row = df[(df['Indicador'] == indicador) & (df['ALS'] == als)]
            else:
                row = df[df['Indicador'] == indicador]
            if not row.empty:
                return str(row['Valor'].values[0])
        return "N/D"
        
    if_on = get_if_val(indice_resumen_df, 'Índice de Falla ON')
    if_als_on = get_if_val(indice_resumen_df, 'Índice de Falla ALS ON', selected_als)
    if_label = f"TOTAL ON: {if_on}\n{selected_als} ON: {if_als_on}"
    # ----------------------------------------------------------------------------------


    # === Construcción de Nodos y Conexiones (Mantenido) ===
    dot.node('run_data', run_label, **node_style_data)
    dot.node('rl_data', rl_label, **node_style_data)
    dot.node('mtbf_data', mtbf_label, **node_style_data)
    dot.node('if_data', if_label, **node_style_data)
    
    node_style_lvl2 = node_style_lvl1.copy()
    node_style_lvl2['shape'] = 'BOX'
    node_style_lvl2['fontsize'] = '20'
    
    dot.node('fallado_node', 'FAILED', fillcolor=kpi_node_colors['IF'], **node_style_lvl2) 
    dot.node('operativos_node', 'OPERATIONAL', fillcolor=kpi_node_colors['RUNs'], **node_style_lvl2)
    
    dot.edge('KPIs', 'RUNs', penwidth='3', color="#0011D1", arrowhead='none')
    dot.edge('KPIs', 'RL', penwidth='3', color='#00F5FF', arrowhead='none')
    dot.edge('KPIs', 'MTBF', penwidth='3', color='#A1039D', arrowhead='none')
    dot.edge('KPIs', 'IF', penwidth='3', color='#5EFF00', arrowhead='none')
    
    dot.edge('RUNs', 'run_data',penwidth='3', color="#0011D1", arrowhead='normal') 
    dot.edge('RL', 'rl_data',penwidth='3', color='#00F5FF', arrowhead='normal')
    dot.edge('MTBF', 'mtbf_data',penwidth='3', color='#A1039D', arrowhead='normal')
    dot.edge('IF', 'if_data', penwidth='3', color='#5EFF00', arrowhead='normal')

    dot.edge('run_data', 'fallado_node', penwidth='3', color=kpi_node_colors['IF'], arrowhead='normal')
    dot.edge('run_data', 'operativos_node', penwidth='3', color=kpi_node_colors['RUNs'], arrowhead='normal')

    node_style_data_sub = node_style_data.copy()
    # Evitar forzar negro absoluto; usar el color de contenedor del tema o transparencia
    node_style_data_sub['fillcolor'] = COLOR_FONDO_CONTENEDOR if COLOR_FONDO_CONTENEDOR else 'transparent'
    node_style_data_sub['width'] = '1.2'  # Menor ancho
    node_style_data_sub['fontsize'] = '14' # Más pequeño aún
    node_style_data_sub['margin'] = '0.05,0.2' # Menor margen
    
    dot.node('fallado_data', fallado_label, **node_style_data_sub)
    dot.node('operativos_data', operativos_label, **node_style_data_sub)
    
    dot.edge('fallado_node', 'fallado_data', penwidth='3', color=kpi_node_colors['IF'], arrowhead='vee')
    dot.edge('operativos_node', 'operativos_data', penwidth='3', color=kpi_node_colors['RUNs'], arrowhead='vee')

    node_style_lvl3 = node_style_lvl2.copy()
    node_style_lvl3['shape'] = 'ellipse'
    
    dot.node('on_node', 'ON', fillcolor=kpi_node_colors['ON'], **node_style_lvl3) 
    dot.node('off_node', 'OFF', fillcolor=kpi_node_colors['OFF'], **node_style_lvl3) 
    
    dot.edge('operativos_data', 'on_node', penwidth='3', color=kpi_node_colors['ON'], arrowhead='normal')
    dot.edge('operativos_data', 'off_node', penwidth='3', color=kpi_node_colors['OFF'], arrowhead='normal')

    dot.node('on_data', on_label, **node_style_data_sub)
    dot.node('off_data', off_label, **node_style_data_sub)
    
    dot.edge('on_node', 'on_data', penwidth='3', color=kpi_node_colors['ON'], arrowhead='vee')
    dot.edge('off_node', 'off_data', penwidth='3', color=kpi_node_colors['OFF'], arrowhead='vee')

    # Mostrar en Streamlit
    st.graphviz_chart(dot)


def build_kpis_graph(df_bd, df_forma9=None, reporte_run_life=None, indice_resumen_df=None, selected_als='TODOS', fecha_evaluacion=None):
    """Construye y devuelve un objeto graphviz.Digraph con los nodos y etiquetas de KPIs.
    Esta función no imprime en Streamlit; devuelve el `dot` para que el llamador lo muestre.
    """
    # Normalizar columnas
    df_bd = df_bd.copy()
    df_bd.columns = [str(c).upper().strip() for c in df_bd.columns]
    if df_forma9 is not None:
        df_forma9 = df_forma9.copy()
        df_forma9.columns = [str(c).upper().strip() for c in df_forma9.columns]
        if 'SISTEMA ALS' in df_forma9.columns and 'ALS' not in df_forma9.columns:
            df_forma9 = df_forma9.rename(columns={'SISTEMA ALS': 'ALS'})

    # Fecha evaluación
    if fecha_evaluacion is None:
        fecha_evaluacion = datetime.datetime.now()
    else:
        try:
            fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
        except Exception:
            fecha_evaluacion = datetime.datetime.now()

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).date()

    # Crear columnas fecha coerced
    for col in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
        if col in df_bd.columns:
            df_bd[col + '_DATE'] = pd.to_datetime(df_bd[col], errors='coerce').dt.date
        else:
            df_bd[col + '_DATE'] = pd.NaT

    def filtrar_als(df, als):
        if als and als != 'TODOS' and 'ALS' in df.columns:
            return df[df['ALS'] == als].copy()
        return df.copy()

    def calc_running(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_fallados(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].notna()) & (df['FECHA_FALLA_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_operativos(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].isna() | (df['FECHA_FALLA_DATE'] > fecha_eval)) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]

    df_bd_als = filtrar_als(df_bd, selected_als)
    run_todos = calc_running(df_bd, fecha_eval_date)
    fallado_todos = calc_fallados(df_bd, fecha_eval_date)
    operativos_todos = calc_operativos(df_bd, fecha_eval_date)

    # Pozos ON en forma9 (últimos 30 días)
    pozos_on_todos = 0
    if df_forma9 is not None and not df_forma9.empty:
        fecha_col = next((c for c in df_forma9.columns if 'FECHA' in c), None)
        dias_col = next((c for c in df_forma9.columns if 'DIAS' in c), None)
        pozo_col = next((c for c in df_forma9.columns if 'POZO' in c), None)
        if fecha_col and dias_col and pozo_col:
            df_forma9[fecha_col] = pd.to_datetime(df_forma9[fecha_col], errors='coerce')
            df_forma9_eval = df_forma9[(df_forma9[fecha_col].dt.date >= (fecha_eval_date - pd.Timedelta(days=30))) & (df_forma9[fecha_col].dt.date <= fecha_eval_date)]
            pozos_on_todos = int(df_forma9_eval[df_forma9_eval[dias_col] > 0][pozo_col].nunique())

    pozos_off_todos = max(0, operativos_todos - pozos_on_todos)

    # Run Life promedio
    rl_todos = None
    if reporte_run_life is not None and not reporte_run_life.empty:
        val = reporte_run_life.loc[reporte_run_life['Categoría'] == 'Run Life Apagados + Fallados', 'Valor']
        if not val.empty:
            try:
                rl_todos = float(val.values[0])
            except Exception:
                rl_todos = None

    # MTBF
    try:
        mtbf_total_val, _ = mtbf_mod.calcular_mtbf(df_bd, fecha_evaluacion)
    except Exception:
        mtbf_total_val = None

    # IF simple
    denom = max(1, run_todos + fallado_todos)
    try:
        if_pct = (fallado_todos / denom) * 100
    except Exception:
        if_pct = None

    # Construir etiquetas
    run_label = f"TOTAL: {run_todos}"
    fallado_label = f"TOTAL: {fallado_todos}"
    operativos_label = f"TOTAL: {operativos_todos}"
    on_label = f"ON: {pozos_on_todos}"
    off_label = f"OFF: {pozos_off_todos}"
    rl_label = f"{rl_todos:.2f} d" if rl_todos is not None else 'N/D'
    mtbf_label = f"{mtbf_total_val:.2f} d" if mtbf_total_val is not None else 'N/D'
    if_label = f"{if_pct:.1f}%" if if_pct is not None else 'N/D'

    # Construir Digraph
    dot = Digraph(comment='KPIs Mini Map', format='png')
    dot.attr(rankdir='LR', splines='polyline', bgcolor='transparent')
    node_attr = {
        'shape': 'box',
        'style': 'filled,rounded',
        'fontname': 'Arial',
        'fontsize': '10',
        'fontcolor': COLOR_TEXTO_DATOS,
        'fillcolor': COLOR_FONDO_CONTENEDOR,
        'color': COLOR_PRINCIPAL,
    }
    dot.attr('node', **node_attr)

    dot.node('KPIS', label='KPIs')
    dot.node('RUN', label=f"RUNs\n{run_label}")
    dot.node('RL', label=f"RunLife\n{rl_label}")
    dot.node('MTBF', label=f"MTBF\n{mtbf_label}")
    dot.node('IF', label=f"IF\n{if_label}")
    dot.node('ON', label=on_label)
    dot.node('OFF', label=off_label)

    dot.edge('KPIS', 'RUN', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('KPIS', 'RL', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('KPIS', 'MTBF', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('KPIS', 'IF', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('RUN', 'ON', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('RUN', 'OFF', penwidth='2', color=COLOR_PRINCIPAL)

    return dot
