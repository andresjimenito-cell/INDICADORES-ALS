import streamlit as st
import pandas as pd
from graphviz import Digraph
import datetime 
import pandas as pd 
import theme as _theme_mod
import mtbf as mtbf_mod

COLOR_PRINCIPAL = getattr(_theme_mod, 'COLOR_PRINCIPAL', '#00ff99')
COLOR_FONDO_OSCURO = getattr(_theme_mod, 'COLOR_FONDO_OSCURO', '#1a1a2e')
COLOR_FONDO_CONTENEDOR = getattr(_theme_mod, 'COLOR_FONDO_CONTENEDOR', 'rgba(25, 25, 40, 0.7)')
COLOR_SOMBRA = getattr(_theme_mod, 'COLOR_SOMBRA', 'rgba(0, 255, 153, 0.5)')

# Colores adicionales específicos locales (si se requieren tonos distintos se definen aquí)
COLOR_TEXTO_DATOS = '#b3f0cc' # Verde claro para legibilidad
COLOR_TEXTO_PRINCIPAL = '#ffffff' # Blanco puro para los títulos principales

# Usaremos la implementación real de MTBF desde el módulo `mtbf.py` (importado como mtbf_mod)

def mostrar_kpis(df_bd, reporte_runes=None, reporte_run_life=None, indice_resumen_df=None, mtbf_global=None, mtbf_als=None, df_forma9=None, fecha_evaluacion=None):
    # Contenedor para el filtro y el título (código omitido por brevedad)
    with st.container():
        st.markdown(f"""
        <style>
            .stSelectbox label, .stMarkdown h3, .stMarkdown p {{ color: {COLOR_PRINCIPAL}; }}
            .stSelectbox div[data-baseweb="select"] {{ border-color: {COLOR_PRINCIPAL}; }}
        </style>
        <h3 style='font-size:1.9rem; font-weight:600; margin-bottom:0.7rem; letter-spacing: 2px; color: {COLOR_PRINCIPAL}; text-shadow: 0 0 10px {COLOR_PRINCIPAL};'>
             KPIs 
        </h3>
        <p style='color:#FFFFFF; font-size:1rem; font-family: monospace;'>
            Visualizando la performance operativa del sistema.
        </p>
        """, unsafe_allow_html=True)
        
        als_options = ['TODOS'] + sorted(df_bd['ALS'].dropna().unique().tolist()) if 'ALS' in df_bd.columns else ['TODOS']
        selected_als = st.selectbox(
            'Filtro por Sistema de Levantamiento (ALS):',
            als_options,
            key='kpis_als_filter_cyber',
            index=0,
            help='Selecciona un sistema ALS para refinar el análisis',
        )
        if selected_als != 'TODOS':
            df_bd_als = df_bd[df_bd['ALS'] == selected_als]
        else:
            df_bd_als = df_bd.copy()

    # Configuración del mapa conceptual
    dot = Digraph(comment='Conceptual Map', format='png')
    dot.attr(bgcolor=COLOR_FONDO_OSCURO, rankdir='LR', splines='polyline', ranksep='0.5', nodesep='0.5') 

    # Paleta de Nodos
    kpi_node_colors = {
    'KPIs': COLOR_PRINCIPAL, # Mantiene el color principal del tema (asumo que es claro/cian)
    'RL': '#008040',         # 1. Run Life - Verde Bosque Profundo
    'MTBF': '#5E3E7A',       # 2. MTBF - Púrpura Oscuro / Berenjena
    'IF': '#007A0C',         # 3. Índice de Falla - Rojo Ladrillo / Óxido Oscuro (Alerta Sutil)
    'RUNs': '#006699',       # 4. Corridas - Azul Marino Sólido (Diferente a ON)
    'ON': '#006699',         # 5. Pozos ON - Dorado Opaco / Oliváceo
    'OFF': '#006699',        # 6. Pozos OFF - Gris Oscuro (Visible, no negro)
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
    root_style['fontcolor'] = "000000"
    root_style['penwidth'] = '3'
    root_style['color'] = "#ffffff"

    
    # Estilo de nodos de Datos - Cyberpunk (más angosto)
    node_style_data = {
        'shape': 'box',
        'style': 'filled,rounded',
        'fontname': 'Courier',
        'fontsize': '18',  # Reducido para nodos más angostos
        'fontcolor': COLOR_TEXTO_DATOS,
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
    
    dot.edge('KPIs', 'RUNs', penwidth='3', color="#006699", arrowhead='none')
    dot.edge('KPIs', 'RL', penwidth='3', color='#008040', arrowhead='none')
    dot.edge('KPIs', 'MTBF', penwidth='3', color='#5E3E7A', arrowhead='none')
    dot.edge('KPIs', 'IF', penwidth='3', color='#007A0C', arrowhead='none')
    
    dot.edge('RUNs', 'run_data',penwidth='3', color="#006699", arrowhead='normal') 
    dot.edge('RL', 'rl_data',penwidth='3', color='#008040', arrowhead='normal')
    dot.edge('MTBF', 'mtbf_data',penwidth='3', color='#5E3E7A', arrowhead='normal')
    dot.edge('IF', 'if_data', penwidth='3', color='#007A0C', arrowhead='normal')

    dot.edge('run_data', 'fallado_node', penwidth='3', color=kpi_node_colors['IF'], arrowhead='normal')
    dot.edge('run_data', 'operativos_node', penwidth='3', color=kpi_node_colors['RUNs'], arrowhead='normal')

    node_style_data_sub = node_style_data.copy()
    node_style_data_sub['fillcolor'] = '#000000'
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
