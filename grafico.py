import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from theme import get_colors, get_plotly_layout

# --- Configuración de Tema (usar API del módulo theme) ---
_colors = get_colors()
get_color_sequence = _colors.get('color_sequence', lambda: ['#00ff99', '#00cfff', '#FFDE31', '#5AFFDA'])
get_plotly_layout = get_plotly_layout

from indice_falla import calcular_indice_falla_anual # Asegúrate de que esta función realmente existe y es necesaria

# --- Función Auxiliar (Eliminada, solo se usa la canónica de indice_falla.py) ---

# Dejamos esta función como estaba, sin la lógica de cálculo de índices internos
# para asegurar que la única fuente de índices sea la función calcular_indice_falla_anual ya corregida.

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
    
    # Iterar sobre los meses que ya tienen los índices calculados
    for _, r in df_mensual_full.iterrows():
        mes_inicio = r['Mes_dt']
        mes_fin = (mes_inicio + pd.offsets.MonthEnd(0)).normalize()

        # Corridas (NICK) activas a fin de mes
        active_bd = df_bd[
            (df_bd['FECHA_RUN'].notna()) &
            (df_bd['FECHA_RUN'] <= mes_fin) &
            ((df_bd['FECHA_PULL'].isna()) | (df_bd['FECHA_PULL'] > mes_fin)) &
            ((df_bd['FECHA_FALLA'].isna()) | (df_bd['FECHA_FALLA'] > mes_fin))
        ].copy()
        
        # Asegurar NICK en active_bd
        if 'NICK' not in active_bd.columns:
            if all(col in active_bd.columns for col in ['POZO', 'RUN']):
                 active_bd['NICK'] = active_bd['POZO'].astype(str) + '-' + active_bd['RUN'].astype(str)
            else:
                 active_bd['NICK'] = 'No_NICK'
        
        active_nicks = active_bd['NICK'].dropna().unique()
        n_corridas = len(active_nicks)
        
        # RunLife_Promedio: Sumar los días acumulados solo para los NICK activos
        suma_acumulados = cum_por_nick.loc[cum_por_nick.index.intersection(active_nicks)].sum()
        runlife_promedio = (suma_acumulados / n_corridas) if n_corridas > 0 else 0.0

        runlife_rows.append({
            'Mes_dt': mes_inicio,
            'RunLife_Promedio': runlife_promedio,
            'TMEF_Promedio': (active_bd['FECHA_RUN'].apply(lambda d: (mes_fin - d).days).mean()) if not active_bd.empty else 0.0
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
    final_cols = ['Mes', 'Pozos_Operativos', 'Pozos_ON', 'Pozos_OFF', 'RunLife_Promedio', 'TMEF_Promedio', 'Indice_Falla_ON', 'Indice_Falla_ON_ALS']
    return df_final[final_cols].sort_values('Mes').reset_index(drop=True)


def generar_grafico_resumen(df_bd, df_forma9, fecha_evaluacion, titulo="Gráfico Resumen"):
    """
    Genera figura mensual con efecto neón/brillo en las LÍNEAS.
    """
    df_monthly = generar_resumen_mensual(df_bd, df_forma9, fecha_evaluacion)
    if df_monthly.empty:
        return None, df_monthly

    # Normalizar índices defensivamente: asegurar que las columnas de índice estén en ratio 0..1
    for col in ['Indice_Falla_ON', 'Indice_Falla_ON_ALS']:
        if col in df_monthly.columns:
            # Convertir a numérico de forma segura
            df_monthly[col] = pd.to_numeric(df_monthly[col], errors='coerce')
            # Si el valor máximo sigue siendo alto (> 1), es un porcentaje no dividido, lo dividimos.
            max_val = df_monthly[col].max(skipna=True)
            if pd.notna(max_val) and (max_val > 1 and max_val <= 100):
                df_monthly[col] = df_monthly[col] / 100.0
            
            # Clip por seguridad (mantenemos el rango amplio del original por si hay outliers)
            df_monthly[col] = df_monthly[col].clip(lower=0.0, upper=10.0)
            df_monthly[col].fillna(0, inplace=True)


    # Colores base para las líneas
    COLOR_RUNLIFE = '#0A4D57'
    COLOR_TMEF = '#A1039D'
    COLOR_IF_ON = '#F52738' 
    COLOR_IF_ALS = '#360A57' 

    fig = go.Figure()

    # --- Trazas ---

    # 1. Barras (Pozos ON/OFF) - Eje Y1
    fig.add_trace(go.Bar(x=df_monthly['Mes'], y=df_monthly['Pozos_ON'], name='Pozos ON', marker_color='#27E0F5', offsetgroup=1))
    fig.add_trace(go.Bar(x=df_monthly['Mes'], y=df_monthly['Pozos_OFF'], name='Pozos OFF', marker_color='#2757F5', offsetgroup=1, base=df_monthly['Pozos_ON'])) # STACKED BAR (OFF sobre ON)

    # 2. Línea (Run Life Promedio) - Eje Y1 
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['RunLife_Promedio'], 
        name='Tiempo Vida Promedio (días/pozo)', 
        mode='lines+markers',
        marker_symbol='diamond', 
        marker_color=COLOR_RUNLIFE, 
        line=dict(width=4, dash='solid', color=COLOR_RUNLIFE),
        marker=dict(size=4), 
        yaxis='y1'
    ))

    # 3. Línea (TMEF Promedio) - Eje Y1
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['TMEF_Promedio'], 
        name='TMEF Promedio (días)', 
        mode='lines+markers',
        marker_symbol='circle', 
        marker_color=COLOR_TMEF, 
        line=dict(width=4, dash='dot', color=COLOR_TMEF),
        marker=dict(size=4), 
        yaxis='y1'
    ))

    # 4. Índices de Falla (Rolling) - Eje Y2 
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['Indice_Falla_ON'], 
        name='Índice de Falla ON (Rolling 12M)', # Título para reflejar el rolling
        mode='lines+markers', 
        marker_symbol='diamond', 
        marker_color=COLOR_IF_ON, 
        line=dict(width=4, dash='solid', color=COLOR_IF_ON),
        marker=dict(size=4),
        yaxis='y2',
        hovertemplate='%{x}<br>Índice ON: %{y:.2%}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['Indice_Falla_ON_ALS'], 
        name='Índice de Falla ON ALS (Rolling 12M)', # Título para reflejar el rolling
        mode='lines+markers', 
        marker_symbol='diamond', 
        marker_color=COLOR_IF_ALS, 
        line=dict(width=4, dash='solid', color=COLOR_IF_ALS),
        marker=dict(size=4),
        yaxis='y2',
        hovertemplate='%{x}<br>Índice ON ALS: %{y:.2%}<extra></extra>'
    ))

    # --- Layout ---

    # Calcular rango superior para eje derecho (Y2)
    max_indice = max(
        float(np.nanmax(df_monthly['Indice_Falla_ON'].replace([np.inf, -np.inf], np.nan).fillna(0))) if 'Indice_Falla_ON' in df_monthly.columns else 0,
        float(np.nanmax(df_monthly['Indice_Falla_ON_ALS'].replace([np.inf, -np.inf], np.nan).fillna(0))) if 'Indice_Falla_ON_ALS' in df_monthly.columns else 0
    )
    # Rango de Y2: usar un margen alrededor del máximo
    upper_y2 = max(0.01, max_indice * 1.2)

    # Rango del eje X (forzar inicio en 2019)
    # Iniciar siempre desde 2019-01-01; terminar en el último mes con datos
    if not df_monthly.empty:
        x_start = pd.to_datetime('2019-01-01')
        x_end = df_monthly['Mes'].max()
    else:
        x_start = pd.to_datetime('2019-01-01')
        x_end = pd.to_datetime(fecha_evaluacion)
    x_range = [x_start, x_end]

    # Aplicar el layout base del tema
    layout_base = get_plotly_layout()
    
    # Configuración de ejes específicos
    yaxis1_config = dict(
        title='# Pozos / Tiempo Vida / TMEF (días)', 
        side='left', 
        color=layout_base['yaxis']['color']
    )
    yaxis2_config = dict(
        title='Índices de Falla (Ratio Rolling 12M)', # Título ajustado
        overlaying='y', 
        side='right', 
        showgrid=False, 
        rangemode='tozero', 
        range=[0, upper_y2],
        color='#A6FF00', 
        tickformat='.2%' 
    )
    xaxis_config = dict(
        title='Mes', 
        tickformat='%Y-%m',
        range=x_range,
        type='date', 
        color=layout_base['xaxis']['color']
    )
    
    # Combinar y actualizar el layout
    fig.update_layout(
        title=titulo,
        barmode='stack',
        xaxis=xaxis_config,
        yaxis=yaxis1_config,
        yaxis2=yaxis2_config,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='white')),
        margin=dict(t=100, b=50, l=50, r=50)
    )
    
    # Aplicar el resto del tema (colores de fondo, fuente, etc.)
    # Solo pasar las claves presentes y no-None para respetar cuando
    # `theme.get_plotly_layout()` deja el fondo a Streamlit (background=None).
    layout_updates = {k: v for k, v in layout_base.items() if v is not None}
    fig.update_layout(**layout_updates)

    # Asegurar que la leyenda tenga texto blanco (reaplicar por si el tema la sobreescribe)
    fig.update_layout(legend=dict(font=dict(color='white')))
    
    return fig, df_monthly
