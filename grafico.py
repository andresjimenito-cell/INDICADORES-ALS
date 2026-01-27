import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import copy
from datetime import datetime
from theme import get_colors, get_plotly_layout, plotly_styled_title as theme_plotly_styled_title
import plotly.graph_objects as _go
import streamlit as st

def inject_plotly_dynamic_styles():
    """
    Inyecta estilos CSS dinámicos para que los gráficos de Plotly se adapten
    automáticamente al modo oscuro/claro de Streamlit.
    """
    st.markdown("""
    <style>
    /* ========================================
       ESTILOS DINÁMICOS PARA GRÁFICAS (Plotly)
       Ejes, Leyenda y Texto: Blanco en Dark / Negro en Light
    ======================================== */

    /* 1. CONFIGURACIÓN DE FONDOS */
    [data-testid="stPlotlyChart"], .plotly-graph-div, .js-plotly-plot {
        background-color: transparent !important;
    }

    /* 2. MODO OSCURO (DARK MODE) */
    /* Ejes, Leyenda, Títulos y Ticks en BLANCO */
    [data-theme="dark"] .plotly text,
    [data-theme="dark"] .plotly tspan,
    [data-theme="dark"] .plotly .xtick text,
    [data-theme="dark"] .plotly .ytick text,
    [data-theme="dark"] .plotly .xtitle,
    [data-theme="dark"] .plotly .ytitle,
    div[data-portal-id][data-theme="dark"] .plotly text,
    div[data-portal-id][data-theme="dark"] .plotly tspan,
    div[data-portal-id][data-theme="dark"] .plotly .xtick text,
    div[data-portal-id][data-theme="dark"] .plotly .ytick text {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    [data-theme="dark"] .plotly .bg, 
    [data-theme="dark"] .plotly .plotbg, 
    [data-theme="dark"] .plotly .bgrect {
        fill: #0A0E27 !important;
    }

    /* 3. MODO CLARO (LIGHT MODE) */
    /* Ejes, Leyenda, Títulos y Ticks en NEGRO */
    [data-theme="light"] .plotly text,
    [data-theme="light"] .plotly tspan,
    [data-theme="light"] .plotly .xtick text,
    [data-theme="light"] .plotly .ytick text,
    [data-theme="light"] .plotly .xtitle,
    [data-theme="light"] .plotly .ytitle,
    div[data-portal-id][data-theme="light"] .plotly text,
    div[data-portal-id][data-theme="light"] .plotly tspan,
    div[data-portal-id][data-theme="light"] .plotly .xtick text,
    div[data-portal-id][data-theme="light"] .plotly .ytick text {
        fill: #000000 !important;
        color: #000000 !important;
    }

    [data-theme="light"] .plotly .bg, 
    [data-theme="light"] .plotly .plotbg, 
    [data-theme="light"] .plotly .bgrect {
        fill: #ffffff !important;
    }

    /* 4. TEXTO DE LEYENDA CON ILUMINACIÓN BLANCA ULTRA-INTENSA */
    .plotly .legendtext {
        fill: #000000 !important;
        color: #000000 !important;
        /* Resplandor masivo acumulado para brillo extremo */
        filter: drop-shadow(0 0 2px #fff) 
                drop-shadow(0 0 3px #fff) 
                drop-shadow(0 0 5px #fff) 
    }

    /* 5. COLOR DE LAS LÍNEAS DE LOS EJES (OPCIONAL) */
    /* Para que las líneas de la cuadrícula no sean demasiado fuertes */
    [data-theme="dark"] .plotly .gridlayer path { stroke: rgba(255,255,255,0.4) !important; }
    [data-theme="light"] .plotly .gridlayer path { stroke: rgba(0,0,0,0.4) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Configuración de Tema (usar API del módulo theme) ---
_colors = get_colors()
get_color_sequence = _colors.get('color_sequence', lambda: ['#00ff99', '#00cfff', '#FFDE31', '#5AFFDA'])
get_plotly_layout = get_plotly_layout

def plotly_styled_title(text: str) -> str:
    try:
        return theme_plotly_styled_title(text)
    except Exception:
        return f"<b>{text.upper()}</b>"

from indice_falla import calcular_indice_falla_anual # Asegúrate de que esta función realmente existe y es necesaria

# --- Función Auxiliar (Eliminada, solo se usa la canónica de indice_falla.py) ---

# Dejamos esta función como estaba, sin la lógica de cálculo de índices internos
# para asegurar que la única fuente de índices sea la función calcular_indice_falla_anual ya corregida.

@st.cache_data(show_spinner="Generando resumen mensual...")
def generar_resumen_mensual(df_bd, df_forma9, fecha_evaluacion):
    """
    Genera un DataFrame mensual con métricas combinadas:
    - RunLife_Promedio (calculado en esta función)
    - Pozos_Operativos, Pozos_ON, Pozos_OFF, Índices de Falla Rolling (de indice_falla.py).
    """
    if df_bd is None or df_forma9 is None:
        return pd.DataFrame()

    # Preparación de datos y fechas
    df_bd = df_bd.copy()
    df_f9 = df_forma9.copy()
    
    # Normalización de fechas
    df_bd['FECHA_RUN'] = pd.to_datetime(df_bd.get('FECHA_RUN', pd.NaT), errors='coerce').dt.normalize()
    df_bd['FECHA_PULL'] = pd.to_datetime(df_bd.get('FECHA_PULL', pd.NaT), errors='coerce').dt.normalize()
    df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd.get('FECHA_FALLA', pd.NaT), errors='coerce').dt.normalize()
    
    df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9.get('FECHA_FORMA9', pd.NaT), errors='coerce').dt.normalize()
    df_f9['DIAS TRABAJADOS'] = pd.to_numeric(df_f9.get('DIAS TRABAJADOS', 0), errors='coerce').fillna(0)
    
    # 1. Generar NICK (Pozo-Run) en df_bd para identificar corridas
    if 'NICK' not in df_bd.columns and all(col in df_bd.columns for col in ['POZO', 'RUN']):
        df_bd['NICK'] = df_bd['POZO'].astype(str) + '-' + df_bd['RUN'].astype(str)
    
    # 2. Obtener el DataFrame mensual completo (incluyendo Pozos, Fallas e Índices Rolling)
    try:
        # Aquí obtenemos el DataFrame completo que ya calcula Pozos Operativos/ON
        # y los índices Rolling (Indice_Falla_Rolling_ON, etc.)
        resumen_tmp, df_mensual_full = calcular_indice_falla_anual(df_bd, df_f9, fecha_evaluacion)
    except Exception:
        # En caso de error, devolver un DF vacío
        return pd.DataFrame()

    if df_mensual_full.empty:
        return pd.DataFrame()

    # Crear Mes_dt para el merge
    df_mensual_full['Mes_dt'] = pd.to_datetime(df_mensual_full['Mes'].astype(str) + '-01', errors='coerce').dt.normalize()
    df_mensual_full.dropna(subset=['Mes_dt'], inplace=True)
    
    # --- PASO 3: Calcular RunLife_Promedio (Solo la métrica faltante) ---
    
    # Agrupar días trabajados por NICK (total acumulado hasta la fecha)
    if 'NICK' not in df_f9.columns and all(col in df_f9.columns for col in ['POZO', 'RUN']):
        df_f9['NICK'] = df_f9['POZO'].astype(str) + '-' + df_f9['RUN'].astype(str)
        
    cum_por_nick = df_f9.groupby('NICK', dropna=True)['DIAS TRABAJADOS'].sum() if 'NICK' in df_f9.columns and not df_f9.empty else pd.Series(dtype=float)

    runlife_rows = []
    
    # Importar la función oficial de cálculo de MTBF
    # Importar la función oficial de cálculo de MTBF y Run Life Efectivo
    # Asegurar que el path incluye el directorio actual para imports locales
    import sys
    import os
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())

    from mtbf import calcular_mtbf
    from run_life_efectivo import calcular_run_life_efectivo

    runlife_rows = []
    
    # Pre-calcular fechas para eficiencia
    if 'FECHA_RUN' in df_bd.columns:
        df_bd['FECHA_RUN_DT'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')
    if 'FECHA_PULL' in df_bd.columns:
        df_bd['FECHA_PULL_DT'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce')
    if 'FECHA_FALLA' in df_bd.columns:
        df_bd['FECHA_FALLA_DT'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')

    # Iterar sobre los meses que ya tienen los índices calculados
    for _, r in df_mensual_full.iterrows():
        mes_inicio = r['Mes_dt']
        mes_fin = (mes_inicio + pd.offsets.MonthEnd(0)).normalize()

        # --- CÁLCULO DE RUN LIFE PROMEDIO (Método ACUMULADO A FECHA CORTE) ---
        # Filtramos eventos FINALIZADOS (Fallas o Pulls) hasta el cierre del mes
        ended_runs = df_bd[
            (
                (df_bd['FECHA_FALLA_DT'].notna()) & (df_bd['FECHA_FALLA_DT'] <= mes_fin)
            ) | (
                (df_bd['FECHA_PULL_DT'].notna()) & (df_bd['FECHA_PULL_DT'] <= mes_fin)
            )
        ].copy()
        
        # Calcular Run Life si no está presente o asegurar consistencia
        # Run Life = Fecha Fin - Fecha Inicio
        ended_runs['Final_Date'] = np.where(
            ended_runs['FECHA_FALLA_DT'].notna(), 
            ended_runs['FECHA_FALLA_DT'], 
            ended_runs['FECHA_PULL_DT']
        )
        ended_runs['RL_Days'] = (ended_runs['Final_Date'] - ended_runs['FECHA_RUN_DT']).dt.days
        
        sum_rl = ended_runs['RL_Days'].sum()
        count_ended = len(ended_runs)
        
        runlife_promedio = (sum_rl / count_ended) if count_ended > 0 else 0.0

        # --- CÁLCULO DE RUN LIFE GENERAL (Activos + Fallados) ---
        all_started_runs = df_bd[df_bd['FECHA_RUN_DT'] <= mes_fin].copy()
        if not all_started_runs.empty:
            all_started_runs['End_Snapshot'] = mes_fin
            # Máscara de los que YA habían fallado o tenido pull a esta fecha de corte
            mask_ended_snap = (
                ((all_started_runs['FECHA_FALLA_DT'].notna()) & (all_started_runs['FECHA_FALLA_DT'] <= mes_fin)) |
                ((all_started_runs['FECHA_PULL_DT'].notna()) & (all_started_runs['FECHA_PULL_DT'] <= mes_fin))
            )
            # Para los terminados, usar su fecha real de fin
            all_started_runs.loc[mask_ended_snap, 'End_Snapshot'] = np.where(
                all_started_runs.loc[mask_ended_snap, 'FECHA_FALLA_DT'].notna(),
                all_started_runs.loc[mask_ended_snap, 'FECHA_FALLA_DT'],
                all_started_runs.loc[mask_ended_snap, 'FECHA_PULL_DT']
            )
            all_started_runs['RL_Gen_Days'] = (all_started_runs['End_Snapshot'] - all_started_runs['FECHA_RUN_DT']).dt.days
            runlife_general = all_started_runs['RL_Gen_Days'].mean()
        else:
            runlife_general = 0.0

        # --- CÁLCULO DE TMEF (Coherente con INDICADORES.py) ---
        try:
            tmef_calc, _ = calcular_mtbf(df_bd, mes_fin)
        except Exception:
            tmef_calc = 0.0
            
        # --- CÁLCULO DE RUN LIFE EFECTIVO (Histórico) ---
        rl_efectivo_fallados = 0.0
        try:
            # 1. Filtrar por fecha de inicio
            current_runs = df_bd[df_bd['FECHA_RUN_DT'] <= mes_fin].copy()
            
            if not current_runs.empty:
                # 2. Asegurar columnas limpias de fecha en el DF que pasamos
                current_runs['FECHA_RUN'] = current_runs['FECHA_RUN_DT']
                current_runs['FECHA_FALLA'] = current_runs['FECHA_FALLA_DT']
                current_runs['FECHA_PULL'] = current_runs['FECHA_PULL_DT']
                
                # 3. ENMASCARAR EVENTOS FUTUROS (Time Travel)
                current_runs.loc[current_runs['FECHA_FALLA'] > mes_fin, 'FECHA_FALLA'] = pd.NaT
                current_runs.loc[current_runs['FECHA_PULL'] > mes_fin, 'FECHA_PULL'] = pd.NaT
                
                # 4. Calcular usando la función oficial
                rl_efectivo_calc, df_rle_hist = calcular_run_life_efectivo(current_runs, df_f9, mes_fin)
                
                # 5. Filtrar solo extraídos/fallados para la métrica específica
                mask_ended_rle = (df_rle_hist['FECHA_FALLA'].notna()) | (df_rle_hist['FECHA_PULL'].notna())
                rl_efectivo_fallados = df_rle_hist[mask_ended_rle]['RUN_LIFE_EFECTIVO'].mean() if not df_rle_hist[mask_ended_rle].empty else 0.0
            else:
                rl_efectivo_calc = 0.0
        except Exception as e:
            rl_efectivo_calc = 0.0
            rl_efectivo_fallados = 0.0

        runlife_rows.append({
            'Mes_dt': mes_inicio,
            'RunLife_Promedio': runlife_promedio,
            'RunLife_General': runlife_general,
            'TMEF_Promedio': tmef_calc,
            'RunLife_Efectivo': rl_efectivo_calc,
            'RunLife_Efectivo_Fallados': rl_efectivo_fallados
        })

    df_runlife = pd.DataFrame(runlife_rows)
    
    # --- PASO 4: Combinar datos y renombrar columnas para el gráfico ---
    
    # Unir RunLife al DF principal de métricas
    df_monthly = pd.merge(df_mensual_full, df_runlife, on='Mes_dt', how='left')

    # Calcular Pozos OFF
    df_monthly['Pozos_OFF'] = df_monthly['Pozos Operativos'] - df_monthly['Pozos ON']
    df_monthly['Pozos_OFF'] = df_monthly['Pozos_OFF'].clip(lower=0)
    
    # 💥💥💥 CORRECCIÓN DE ERROR "Mes is not unique" 💥💥💥
    # Eliminar la columna 'Mes' string original antes de renombrar 'Mes_dt'
    if 'Mes' in df_monthly.columns:
        df_monthly.drop(columns=['Mes'], inplace=True)
        
    # CRÍTICO: Renombrar 'Mes_dt' a 'Mes' y los índices Rolling a los nombres que espera el gráfico
    df_final = df_monthly.rename(columns={
        'Mes_dt': 'Mes', # <-- Ahora sí se puede renombrar 'Mes_dt' a 'Mes' sin conflicto
        'Pozos Operativos': 'Pozos_Operativos',
        'Pozos ON': 'Pozos_ON',
        'Indice_Falla_Rolling_ON': 'Indice_Falla_ON', # <-- Se usa el Rolling para el gráfico
        'Indice_Falla_Rolling_ALS_ON': 'Indice_Falla_ON_ALS', # <-- Se usa el Rolling para el gráfico
    })
    
    # Filtrar solo donde tenemos datos de índices (donde la ventana rolling de 12 meses ya se ha llenado)
    df_final = df_final[df_final['Indice_Falla_ON'].notna()]
    
    # Seleccionar y ordenar las columnas finales
    final_cols = [
        'Mes', 'Pozos_Operativos', 'Pozos_ON', 'Pozos_OFF', 
        'RunLife_Promedio', 'RunLife_General', 'TMEF_Promedio', 
        'RunLife_Efectivo', 'RunLife_Efectivo_Fallados', 
        'Indice_Falla_ON', 'Indice_Falla_ON_ALS'
    ]
    return df_final[final_cols].sort_values('Mes').reset_index(drop=True)


def generar_grafico_resumen(df_bd, df_forma9, fecha_evaluacion, titulo="Gráfico Resumen"):
    """
    Genera figura mensual con estética Cyberpunk/HUD Futuro.
    Mantiene la lógica intacta, solo se modifica la visualización.
    """
    df_monthly = generar_resumen_mensual(df_bd, df_forma9, fecha_evaluacion)
    if df_monthly.empty:
        return None, df_monthly

    # Normalizar índices defensivamente (Lógica intacta)
    for col in ['Indice_Falla_ON', 'Indice_Falla_ON_ALS']:
        if col in df_monthly.columns:
            df_monthly[col] = pd.to_numeric(df_monthly[col], errors='coerce')
            max_val = df_monthly[col].max(skipna=True)
            if pd.notna(max_val) and (max_val > 1 and max_val <= 100):
                df_monthly[col] = df_monthly[col] / 100.0
            df_monthly[col] = df_monthly[col].clip(lower=0.0, upper=10.0)
            df_monthly[col].fillna(0, inplace=True)

    # --- PALETA CROMÁTICA ADAPTABLE ---
    # Inyectar estilos dinámicos de Plotly
    inject_plotly_dynamic_styles()
    
    # Colores HUD más vibrantes
    CYAN_NEON = '#00D9FF'      # Celeste vibrante
    GREEN_ELECTRIC = '#B200CC' # Verde neón
    MAGENTA_ALERTA = '#ff0055' # Magenta alerta
    AMARILLO_NEON = '#FFAB40' # Amarillo/Naranja neón
    GRID_COLOR = 'rgba(128,128,128,0.15)' # Gris sutil para ambos temas
    FONT_TECH = 'Consolas, "Courier New", monospace'

    # Asignación de colores
    COLOR_POZOS_ON = CYAN_NEON
    COLOR_POZOS_OFF = '#141943'
    COLOR_RUNLIFE = GREEN_ELECTRIC
    COLOR_RUNLIFE_GEN = '#a6ff00'
    COLOR_RLE = "#FFF700"
    COLOR_RLE_FALLA = '#00CCFF'
    COLOR_TMEF = '#E6E6E6'
    COLOR_IF_ON = MAGENTA_ALERTA
    COLOR_IF_ALS = AMARILLO_NEON

    fig = go.Figure()

    # --- TRAZAS (ESTILO HUD ESPAÑOL) ---

    # 1. Barras (Pozos ON/OFF)
    fig.add_trace(go.Bar(
        x=df_monthly['Mes'], 
        y=df_monthly['Pozos_ON'], 
        name='POZOS ACTIVOS', 
        marker=dict(color=COLOR_POZOS_ON, line=dict(color=COLOR_POZOS_ON, width=1), opacity=1),
        offsetgroup=0.5,
        hovertemplate='<b>[ESTADO: ACTIVOS]</b><br>CANTIDAD: %{y}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=df_monthly['Mes'], 
        y=df_monthly['Pozos_OFF'], 
        name='POZOS INACTIVOS', 
        marker=dict(color=COLOR_POZOS_OFF, line=dict(width=1), opacity=1),
        offsetgroup=0.5, 
        base=df_monthly['Pozos_ON'],
        hovertemplate='<b>[ESTADO: INACTIVOS]</b><br>CANTIDAD: %{y}<extra></extra>'
    )) 

    # 2. Líneas de Tiempo de Vida (RV)
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['RunLife_Promedio'], 
        name='TIEMPO DE VIDA', 
        mode='lines+markers',
        marker=dict(symbol='circle', size=8, color=COLOR_RUNLIFE), 
        line=dict(width=3, color=COLOR_RUNLIFE),
        yaxis='y1',
        hovertemplate='<b>[TIEMPO DE VIDA ]</b><br>DÍAS: %{y:.2f}<extra></extra>'
    ))

    if 'RunLife_General' in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly['Mes'], 
            y=df_monthly['RunLife_General'], 
            name='TIEMPO DE VIDA TOTAL', 
            mode='lines+markers',
            marker=dict(symbol='circle-open', size=8, color=COLOR_RUNLIFE_GEN), 
            line=dict(width=3, color=COLOR_RUNLIFE_GEN),
            yaxis='y1',
            hovertemplate='<b>[TIEMPO DE VIDA TOTAL]</b><br>DÍAS: %{y:.2f}<extra></extra>'
        ))

    if 'RunLife_Efectivo' in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly['Mes'], 
            y=df_monthly['RunLife_Efectivo'], 
            name='TIEMPO DE VIDA EFECTIVO TOTAL', 
            mode='lines+markers',
            marker=dict(symbol='circle', size=8, color=COLOR_RLE), 
            line=dict(width=3, dash='dot', color=COLOR_RLE),
            yaxis='y1',
            hovertemplate='<b>[TIEMPO DE VIDA EFECTIVO TOTAL]</b><br>DÍAS: %{y:.2f}<extra></extra>'
        ))

    if 'RunLife_Efectivo_Fallados' in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly['Mes'], 
            y=df_monthly['RunLife_Efectivo_Fallados'], 
            name='TIEMPO DE VIDA EFECTIVO', 
            mode='lines+markers',
            marker=dict(symbol='circle-open', size=8, color="#00549A"), 
            line=dict(width=3, dash='dot', color="#8FA73B"),
            yaxis='y1',
            hovertemplate='<b>[TIEMPO DE VIDA EFECTIVO]</b><br>DÍAS: %{y:.2f}<extra></extra>'
        ))

    # 3. TMEF
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['TMEF_Promedio'], 
        name='TMEF PROM', 
        mode='lines+markers',
        marker=dict(symbol='circle', size=7, color=COLOR_TMEF), 
        line=dict(width=2, dash='dot', color=COLOR_TMEF),
        yaxis='y1',
        visible='legendonly',
        hovertemplate='<b>[TMEF]</b><br>DÍAS: %{y:.2f}<extra></extra>'
    ))

    # 4. Índices de Falla
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['Indice_Falla_ON'], 
        name='ÍNDICE FALLA (ON)', 
        mode='lines+markers', 
        marker=dict(symbol='diamond', size=8, color=COLOR_IF_ON), 
        line=dict(width=4, color=COLOR_IF_ON),
        yaxis='y2',
        hovertemplate='<b>[IF_ON]</b><br>ÍNDICE: %{y:.2%}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['Indice_Falla_ON_ALS'], 
        name='ÍNDICE FALLA ALS (ON)', 
        mode='lines+markers', 
        marker=dict(symbol='diamond-open', size=8, color=COLOR_IF_ALS), 
        line=dict(width=4, color=COLOR_IF_ALS),
        yaxis='y2',
        hovertemplate='<b>[IF_ALS_ON]</b><br>ÍNDICE: %{y:.2%}<extra></extra>'
    ))

    # --- LAYOUT (HUD SIMÉTRICO) ---

    max_indice = max(
        float(np.nanmax(df_monthly['Indice_Falla_ON'].replace([np.inf, -np.inf], np.nan).fillna(0))) if 'Indice_Falla_ON' in df_monthly.columns else 0,
        float(np.nanmax(df_monthly['Indice_Falla_ON_ALS'].replace([np.inf, -np.inf], np.nan).fillna(0))) if 'Indice_Falla_ON_ALS' in df_monthly.columns else 0
    )
    upper_y2 = max(0.01, max_indice * 1.01)

    if not df_monthly.empty:
        x_start = pd.to_datetime('2019-01-01')
        x_end = df_monthly['Mes'].max()
    else:
        x_start = pd.to_datetime('2019-01-01')
        x_end = pd.to_datetime(fecha_evaluacion)

    from theme import get_plotly_layout
    layout = get_plotly_layout()
    layout['title'] = plotly_styled_title(titulo)
    layout.update(dict(
        showlegend=True,
        barmode='stack',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(10, 14, 39, 0.8)',
            bordercolor='#00f2ff',
            borderwidth=1
        ),
        xaxis=dict(
            title=dict(text='<b>TIEMPO</b>', font=dict(size=14, family='Outfit')),
            tickformat='%Y-%m',
            range=[x_start, x_end],
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec'
        ),
        yaxis=dict(
            title=dict(text='<b>POZOS / DÍAS VIDA / TMEF</b>', font=dict(size=14, family='Outfit')),
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec'
        ),
        yaxis2=dict(
            title=dict(text='<b>ÍNDICE DE FALLA</b>', font=dict(size=14, family='Outfit')),
            overlaying='y',
            side='right',
            range=[0, upper_y2],
            tickformat='.2%',
            showgrid=False,
            linecolor='#00f2ff'
        ),
        margin=dict(t=100, b=80, l=90, r=90)
    ))

    fig.update_layout(**layout)
    # Decoración HUD
    fig.add_shape(type='line', x0=0, y0=1.02, x1=1, y1=1.02, xref='paper', yref='paper', line=dict(color='#00f2ff', width=2))

    return fig, df_monthly


def render_premium_echarts(df_monthly, titulo="PERFORMANCE DASHBOARD"):
    """
    Renderiza un gráfico premium estilo HUD utilizando ECharts (HTML/JS).
    Proporciona una visualización mucho más fluida, moderna e interactiva que Plotly.
    """
    import json
    import streamlit.components.v1 as components

    if df_monthly is None or df_monthly.empty:
        return st.info("No hay datos mensuales para este filtro.")

    # Preparar datos para JSON
    # Convertir fechas a string para evitar errores de serialización Timestamp
    categories = [str(m) for m in df_monthly['Mes'].dt.strftime('%b %Y')]

    
    # Colores del tema
    COLOR_PRIMARY = "#135bec" # Azul
    COLOR_ACCENT = "#00f2ff"  # Cyan
    COLOR_SUCCESS = "#b200cc" # Violeta/Magenta (Tiempo Vida)
    COLOR_DANGER = "#ff0055"  # Rojo/Magenta (Indice Falla)
    COLOR_WARNING = "#ffab40" # Naranja (Indice Falla ALS)

    import pandas as pd
    pozos_on = df_monthly['Pozos_ON'].tolist()
    pozos_off = df_monthly['Pozos_OFF'].tolist()
    rl_prom = [round(float(x), 2) for x in df_monthly['RunLife_Promedio'].tolist()]
    rl_gen = [round(float(x), 2) for x in df_monthly['RunLife_General'].tolist()]
    tmef = [round(float(x), 2) for x in df_monthly['TMEF_Promedio'].tolist()]
    rle = [round(float(x), 2) for x in df_monthly['RunLife_Efectivo'].tolist()]
    rle_fallados = [round(float(x), 2) for x in df_monthly.get('RunLife_Efectivo_Fallados', [0]*len(df_monthly)).tolist()]
    # Asegurar que los índices existen antes de redondear
    if_on = [round(float(x) * 100, 2) if pd.notna(x) else 0 for x in df_monthly['Indice_Falla_ON'].tolist()] if 'Indice_Falla_ON' in df_monthly.columns else []
    if_als = [round(float(x) * 100, 2) if pd.notna(x) else 0 for x in df_monthly['Indice_Falla_ON_ALS'].tolist()] if 'Indice_Falla_ON_ALS' in df_monthly.columns else []


    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "text": titulo.upper(),
            "left": "center",
            "top": 0,
            "textStyle": {
                "color": "#fff",
                "fontSize": 18,
                "fontFamily": "Outfit, sans-serif",
                "fontWeight": "900",
                "letterSpacing": 1
            }
        },
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(6, 10, 30, 0.9)",
            "borderColor": COLOR_ACCENT,
            "borderWidth": 1,
            "textStyle": {"color": "#fff", "fontSize": 12},
            "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}}
        },
        "legend": {
            "data": ["Pozos ON", "Pozos OFF", "T. Vida Prom", "T. Vida Total", "T. Vida Efectivo", "T. V. Efec. Fallados", "TMEF", "Ind. Falla ON", "Ind. Falla ALS"],
            "bottom": 0,
            "textStyle": {"color": "#ccc", "fontSize": 10},
            "icon": "circle",
            "itemGap": 15
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "12%",
            "top": "18%",
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "boundaryGap": True,
                "data": categories,
                "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.1)"}},
                "axisLabel": {"color": "#888", "fontSize": 10}
            }
        ],
        "yAxis": [
            {
                "type": "value",
                "name": "POZOS / DÍAS",
                "position": "left",
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}},
                "axisLine": {"show": True, "lineStyle": {"color": COLOR_PRIMARY}},
                "axisLabel": {"color": "#888"}
            },
            {
                "type": "value",
                "name": "INDICE %",
                "position": "right",
                "splitLine": {"show": False},
                "axisLine": {"show": True, "lineStyle": {"color": COLOR_DANGER}},
                "axisLabel": {"color": "#888", "formatter": "{value} %"}
            }
        ],
        "series": [
            {
                "name": "Pozos ON",
                "type": "bar",
                "stack": "Total",
                "barWidth": "60%",
                "itemStyle": {
                    "color": {
                        "type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [{"offset": 0, "color": COLOR_ACCENT}, {"offset": 1, "color": "rgba(0, 242, 255, 0.1)"}]
                    },
                    "borderRadius": [4, 4, 0, 0]
                },
                "data": pozos_on
            },
            {
                "name": "Pozos OFF",
                "type": "bar",
                "stack": "Total",
                "itemStyle": {
                    "color": "#ff4d4d", 
                    "opacity": 0.4,
                    "decal": {
                        "symbol": "rect",
                        "size": 1,
                        "dashArrayX": [1, 0],
                        "dashArrayY": [2, 2],
                        "rotation": 0.785
                    }
                },
                "data": pozos_off
            },
            {
                "name": "T. Vida Prom",
                "type": "line",
                "smooth": True,
                "symbol": "circle",
                "symbolSize": 8,
                "lineStyle": {"width": 3, "color": COLOR_SUCCESS},
                "itemStyle": {"color": COLOR_SUCCESS},
                "data": rl_prom
            },
            {
                "name": "T. Vida Total",
                "type": "line",
                "smooth": True,
                "lineStyle": {"width": 2, "type": "dashed", "color": "#a6ff00"},
                "itemStyle": {"color": "#a6ff00"},
                "data": rl_gen
            },
            {
                "name": "T. Vida Efectivo",
                "type": "line",
                "smooth": True,
                "lineStyle": {"width": 2, "type": "dotted", "color": "#FFF700"},
                "itemStyle": {"color": "#FFF700"},
                "data": rle
            },
            {
                "name": "T. V. Efec. Fallados",
                "type": "line",
                "smooth": True,
                "lineStyle": {"width": 2, "type": "dotted", "color": "#00CCFF"},
                "itemStyle": {"color": "#00CCFF"},
                "data": rle_fallados
            },
            {
                "name": "TMEF",
                "type": "line",
                "smooth": True,
                "lineStyle": {"width": 1, "type": "dashed", "color": "#ccc"},
                "itemStyle": {"color": "#ccc"},
                "data": tmef
            },
            {
                "name": "Ind. Falla ON",
                "type": "line",
                "yAxisIndex": 1,
                "smooth": True,
                "symbol": "diamond",
                "symbolSize": 10,
                "lineStyle": {"width": 4, "color": COLOR_DANGER, "shadowBlur": 10, "shadowColor": COLOR_DANGER},
                "itemStyle": {"color": COLOR_DANGER},
                "areaStyle": {
                    "color": {
                        "type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [{"offset": 0, "color": "rgba(255, 0, 85, 0.2)"}, {"offset": 1, "color": "transparent"}]
                    }
                },
                "data": if_on
            },
            {
                "name": "Ind. Falla ALS",
                "type": "line",
                "yAxisIndex": 1,
                "smooth": True,
                "symbol": "diamond",
                "symbolSize": 8,
                "lineStyle": {"width": 3, "color": COLOR_WARNING},
                "itemStyle": {"color": COLOR_WARNING},
                "data": if_als
            }
        ]
    }

    chart_height = 500
    container_height = chart_height + 20

    html_template = f"""
    <div id="chart-container" style="position: relative; width:100%; height:{chart_height}px; background: #060a1e; border-radius: 15px; overflow: hidden;">
        <div id="echarts-main" style="width:100%; height:100%;"></div>
        <button id="zoom-btn" style="
            position: absolute; 
            top: 10px; 
            right: 10px; 
            z-index: 1000; 
            background: rgba(200, 43, 150, 0.2); 
            border: 1px solid rgba(200, 43, 150, 0.4); 
            color: #ff00ff; 
            padding: 4px 10px; 
            border-radius: 20px; 
            cursor: pointer; 
            font-size: 11px; 
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            text-transform: uppercase;
            backdrop-filter: blur(5px);
            transition: all 0.3s;
        ">⛶ Ampliar</button>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var container = document.getElementById('chart-container');
            var chartDom = document.getElementById('echarts-main');
            var zoomBtn = document.getElementById('zoom-btn');
            var myChart = echarts.init(chartDom, 'dark');
            var option = {json.dumps(echarts_options)};
            
            myChart.setOption(option);
            
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});

            zoomBtn.addEventListener('click', function() {{
                if (!document.fullscreenElement) {{
                    container.requestFullscreen().catch(err => {{
                        alert(`Error intentando activar pantalla completa: ${{err.message}}`);
                    }});
                    container.style.height = '100vh';
                    zoomBtn.innerHTML = '✕ Cerrar';
                }} else {{
                    document.exitFullscreen();
                    container.style.height = '{chart_height}px';
                    zoomBtn.innerHTML = '⛶ Ampliar';
                }}
            }});

            document.addEventListener('fullscreenchange', exitHandler);
            function exitHandler() {{
                if (!document.fullscreenElement) {{
                    container.style.height = '{chart_height}px';
                    zoomBtn.innerHTML = '⛶ Ampliar';
                    myChart.resize();
                }} else {{
                    myChart.resize();
                }}
            }}
        }})();
    </script>
    """
    
    components.html(html_template, height=container_height)
