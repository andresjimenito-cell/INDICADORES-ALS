import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import copy
from datetime import datetime
from theme import get_colors, get_plotly_layout
import plotly.graph_objects as _go
import streamlit as st

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
    
    # Importar la función oficial de cálculo de MTBF
    from mtbf import calcular_mtbf

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

        # --- CÁLCULO DE TMEF (Coherente con INDICADORES.py) ---
        # Usamos la función oficial calcular_mtbf pasando el dataframe completo y la fecha de corte.
        # La función interno filtra por FECHA_RUN <= mes_fin y usa los valores estáticos de RUN LIFE / INDICADOR
        # tal como lo hace el indicador global.
        try:
            tmef_calc, _ = calcular_mtbf(df_bd, mes_fin)
        except Exception:
            tmef_calc = 0.0

        runlife_rows.append({
            'Mes_dt': mes_inicio,
            'RunLife_Promedio': runlife_promedio,
            'TMEF_Promedio': tmef_calc
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
        yaxis='y1',
        visible='legendonly'
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


def exportar_png_claro(fig, filename, width=1200, height=700, scale=2):
    """
    Exporta la figura Plotly a PNG con fondo claro y texto/leyenda oscuros.

    Parámetros:
    - fig: objeto Plotly (go.Figure)
    - filename: ruta de salida (incluye .png)
    - width, height: dimensiones en píxeles
    - scale: escala para resolución (dpi equivalente)
    Devuelve la ruta del archivo generado.
    """
    # Hacer una copia para no mutar la figura original usada en la UI
    fig_copy = copy.deepcopy(fig)

    # Forzar tema claro y texto oscuro
    fig_copy.update_layout(
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black'),
        legend=dict(font=dict(color='black'), bgcolor='rgba(255,255,255,0.9)', bordercolor='rgba(0,0,0,0.08)')
    )

    # Asegurar ejes, títulos y ticks en color oscuro
    fig_copy.update_xaxes(color='black', title_font=dict(color='black'), tickfont=dict(color='black'))
    fig_copy.update_yaxes(color='black', title_font=dict(color='black'), tickfont=dict(color='black'))
    try:
        if fig_copy.layout.yaxis2 is not None:
            fig_copy.layout.yaxis2.color = 'black'
    except Exception:
        pass

    # Forzar título principal y subtítulos en negro
    try:
        if fig_copy.layout.title is not None:
            fig_copy.layout.title.font = dict(color='black')
    except Exception:
        pass

    # Actualizar trazas para asegurar hoverlabels y textos en negro
    try:
        fig_copy.update_traces(hoverlabel=dict(font=dict(color='black'), bgcolor='white'))
    except Exception:
        pass

    for tr in fig_copy.data:
        try:
            # Forzar texto de serie/etiquetas dentro de la traza
            tr.update(textfont=dict(color='black'))
        except Exception:
            pass
        try:
            # Forzar hoverlabel por traza también
            tr.update(hoverlabel=dict(font=dict(color='black'), bgcolor='white'))
        except Exception:
            pass
        try:
            # Si la traza tiene marcador con borde, oscurecer el borde para contraste
            if hasattr(tr, 'marker') and tr.marker is not None and hasattr(tr.marker, 'line'):
                tr.marker.line.color = 'black'
        except Exception:
            pass

    # Forzar color en anotaciones, sliders, botones y colorbars si existen
    try:
        anns = list(fig_copy.layout.annotations) if hasattr(fig_copy.layout, 'annotations') and fig_copy.layout.annotations is not None else []
        for ann in anns:
            try:
                ann.font.color = 'black'
            except Exception:
                try:
                    ann['font'] = dict(color='black')
                except Exception:
                    pass
    except Exception:
        pass

    try:
        # Actualizar leyenda nuevamente por si el tema la sobreescribió
        fig_copy.update_layout(legend=dict(font=dict(color='black'), bgcolor='rgba(255,255,255,0.9)', bordercolor='rgba(0,0,0,0.08)'))
    except Exception:
        pass

    # Forzar cualquier color de texto remanente en el layout y ejes a negro (más agresivo)
    try:
        fig_json = fig_copy.to_plotly_json()
        layout = fig_json.get('layout', {})

        def _force_black_colors(obj):
            if isinstance(obj, dict):
                # If this dict describes a font, force its color
                if 'font' in obj and isinstance(obj['font'], dict):
                    obj['font']['color'] = 'black'
                # Common direct color keys
                for key in list(obj.keys()):
                    v = obj[key]
                    if key.lower().endswith('color') and isinstance(v, str):
                        obj[key] = 'black'
                    elif key in ('color',) and isinstance(v, str):
                        obj[key] = 'black'
                    elif isinstance(v, (dict, list)):
                        _force_black_colors(v)
            elif isinstance(obj, list):
                for item in obj:
                    _force_black_colors(item)

        _force_black_colors(layout)
        # Ensure background is white and no template overrides
        layout['paper_bgcolor'] = 'white'
        layout['plot_bgcolor'] = 'white'
        layout['template'] = None

        # Forzar explícitamente propiedades de leyenda (múltiples ubicaciones)
        if 'legend' not in layout or not isinstance(layout.get('legend'), dict):
            layout['legend'] = {}
        layout['legend']['font'] = {'color': 'black', 'family': layout.get('font', {}).get('family', None), 'size': layout.get('font', {}).get('size', None)}
        # título de leyenda si existe
        if 'title' in layout['legend'] and isinstance(layout['legend']['title'], dict):
            layout['legend']['title'].setdefault('font', {})
            layout['legend']['title']['font']['color'] = 'black'

        # También forzar en layout principal
        if 'font' not in layout:
            layout['font'] = {}
        layout['font']['color'] = 'black'

        fig_fixed = _go.Figure(fig_json)
        # Asegurar que el objeto final tiene legend.font.color en la API de Python
        try:
            fig_fixed.layout.legend.font.color = 'black'
            if hasattr(fig_fixed.layout.legend, 'title') and fig_fixed.layout.legend.title is not None:
                fig_fixed.layout.legend.title.font.color = 'black'
        except Exception:
            pass

        fig_copy = fig_fixed
    except Exception:
        pass

    # Escribir PNG usando kaleido (pio) si está disponible
    try:
        pio.write_image(fig_copy, filename, format='png', width=width, height=height, scale=scale)
    except Exception:
        # Fallback a método del propio objeto
        fig_copy.write_image(filename, width=width, height=height, scale=scale)

    return filename


def exportar_png_claro_bytes(fig, width=1200, height=700, scale=2):
    """
    Devuelve los bytes PNG de la figura con fondo claro y texto en negro.
    Útil para usar con Streamlit `st.download_button(data=..., file_name=..., mime='image/png')`.
    """
    fig_copy = copy.deepcopy(fig)

    # Aplicar los mismos ajustes que en exportar_png_claro
    fig_copy.update_layout(
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black'),
        legend=dict(font=dict(color='black'), bgcolor='rgba(255,255,255,0.9)', bordercolor='rgba(0,0,0,0.08)')
    )
    fig_copy.update_xaxes(color='black', title_font=dict(color='black'), tickfont=dict(color='black'))
    fig_copy.update_yaxes(color='black', title_font=dict(color='black'), tickfont=dict(color='black'))
    try:
        if fig_copy.layout.yaxis2 is not None:
            fig_copy.layout.yaxis2.color = 'black'
    except Exception:
        pass
    try:
        if fig_copy.layout.title is not None:
            fig_copy.layout.title.font = dict(color='black')
    except Exception:
        pass
    try:
        fig_copy.update_traces(hoverlabel=dict(font=dict(color='black'), bgcolor='white'))
    except Exception:
        pass

    for tr in fig_copy.data:
        try:
            tr.update(textfont=dict(color='black'))
        except Exception:
            pass
        try:
            tr.update(hoverlabel=dict(font=dict(color='black'), bgcolor='white'))
        except Exception:
            pass
        try:
            if hasattr(tr, 'marker') and tr.marker is not None and hasattr(tr.marker, 'line'):
                tr.marker.line.color = 'black'
        except Exception:
            pass

    try:
        anns = list(fig_copy.layout.annotations) if hasattr(fig_copy.layout, 'annotations') and fig_copy.layout.annotations is not None else []
        for ann in anns:
            try:
                ann.font.color = 'black'
            except Exception:
                try:
                    ann['font'] = dict(color='black')
                except Exception:
                    pass
    except Exception:
        pass

    # Forzar layout text negro agresivamente (recursively)
    try:
        fig_json = fig_copy.to_plotly_json()
        layout = fig_json.get('layout', {})

        def _force_black_colors(obj):
            if isinstance(obj, dict):
                if 'font' in obj and isinstance(obj['font'], dict):
                    obj['font']['color'] = 'black'
                for key in list(obj.keys()):
                    v = obj[key]
                    if key.lower().endswith('color') and isinstance(v, str):
                        obj[key] = 'black'
                    elif key in ('color',) and isinstance(v, str):
                        obj[key] = 'black'
                    elif isinstance(v, (dict, list)):
                        _force_black_colors(v)
            elif isinstance(obj, list):
                for item in obj:
                    _force_black_colors(item)

        _force_black_colors(layout)
        layout['paper_bgcolor'] = 'white'
        layout['plot_bgcolor'] = 'white'
        layout['template'] = None
        fig_fixed = _go.Figure(fig_json)
        fig_copy = fig_fixed
    except Exception:
        pass

    try:
        img_bytes = pio.to_image(fig_copy, format='png', width=width, height=height, scale=scale)
    except Exception:
        try:
            img_bytes = fig_copy.to_image(format='png', width=width, height=height, scale=scale)
        except Exception as e:
            raise


def aplicar_tema_claro(fig):
    """
    Aplica tema claro a una figura Plotly: fondo blanco, texto/leyenda/ejes negros.
    Devuelve una copia de la figura con los cambios aplicados.
    """
    fig_copy = copy.deepcopy(fig)
    
    # Fondo blanco
    fig_copy.update_layout(
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black')
    )
    
    # Leyenda oscura
    fig_copy.update_layout(
        legend=dict(
            font=dict(color='black'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.1)'
        )
    )
    
    # Ejes oscuros
    fig_copy.update_xaxes(color='black', title_font=dict(color='black'), tickfont=dict(color='black'))
    fig_copy.update_yaxes(color='black', title_font=dict(color='black'), tickfont=dict(color='black'))
    
    # Forzar todos los colores de texto a negro recursivamente
    try:
        fig_json = fig_copy.to_plotly_json()
        layout = fig_json.get('layout', {})
        
        def _force_black(obj):
            if isinstance(obj, dict):
                if 'font' in obj and isinstance(obj['font'], dict):
                    obj['font']['color'] = 'black'
                for key in list(obj.keys()):
                    v = obj[key]
                    if key.lower().endswith('color') and isinstance(v, str):
                        obj[key] = 'black'
                    elif isinstance(v, (dict, list)):
                        _force_black(v)
            elif isinstance(obj, list):
                for item in obj:
                    _force_black(item)
        
        _force_black(layout)
        layout['paper_bgcolor'] = 'white'
        layout['plot_bgcolor'] = 'white'
        
        fig_copy = _go.Figure(fig_json)
        try:
            fig_copy.layout.legend.font.color = 'black'
        except Exception:
            pass
    except Exception:
        pass
    
    return fig_copy


def mostrar_grafica_con_boton_tema(fig, titulo="Gráfico"):
    """
    Muestra una gráfica en Streamlit con un botón para cambiar entre tema oscuro y claro.
    """
    if 'tema_grafico' not in st.session_state:
        st.session_state['tema_grafico'] = 'oscuro'
    
    # Botones para cambiar tema
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        if st.button('🌗', help='Cambiar tema'):
            st.session_state['tema_grafico'] = 'claro' if st.session_state['tema_grafico'] == 'oscuro' else 'oscuro'
            st.rerun()
    
    with col2:
        st.write(f"Tema: {st.session_state['tema_grafico'].upper()}")
    
    # Aplicar tema según selección
    if st.session_state['tema_grafico'] == 'claro':
        fig_final = aplicar_tema_claro(fig)
    else:
        fig_final = fig
    
    st.plotly_chart(fig_final, use_container_width=True)

    return img_bytes
