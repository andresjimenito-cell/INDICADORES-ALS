import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from theme import plotly_styled_title as theme_plotly_styled_title
from grafico import generar_resumen_mensual, inject_plotly_dynamic_styles

def plotly_styled_title(text: str) -> str:
    try:
        return theme_plotly_styled_title(text)
    except Exception:
        return f"<b>{text.upper()}</b>"

def generar_grafico_run_life(df_bd, df_forma9, fecha_evaluacion, titulo="Gráfico Run Life"):
    """
    Genera figura mensual enfocada SOLO en métricas de Run Life y TMEF.
    Incluye: RunLife_Promedio, RunLife_General, RunLife_Efectivo, RunLife_Efectivo_Fallados, TMEF_Promedio
    """
    df_monthly = generar_resumen_mensual(df_bd, df_forma9, fecha_evaluacion)
    if df_monthly.empty:
        return None, df_monthly

    # Inyectar estilos dinámicos de Plotly
    inject_plotly_dynamic_styles()
    
    # Colores HUD más vibrantes (consistentes con grafico.py)
    CYAN_NEON = '#00D9FF'
    GREEN_ELECTRIC = '#00ff9f'
    AMARILLO_NEON = '#FFAB40'
    GRID_COLOR = 'rgba(128,128,128,0.15)'
    FONT_TECH = 'Consolas, "Courier New", monospace'

    # Asignación de colores para Run Life
    COLOR_RUNLIFE = GREEN_ELECTRIC
    COLOR_RUNLIFE_GEN = '#a6ff00'
    COLOR_RLE = "#FFF700"
    COLOR_RLE_FALLA = '#00CCFF'
    COLOR_TMEF = '#E6E6E6'

    fig = go.Figure()

    # --- TRAZAS DE RUN LIFE ---
    
    # 1. Run Life Promedio
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['RunLife_Promedio'], 
        name='TIEMPO DE VIDA', 
        mode='lines+markers',
        marker=dict(symbol='circle', size=8, color=COLOR_RUNLIFE), 
        line=dict(width=3, color=COLOR_RUNLIFE),
        hovertemplate='<b>[TIEMPO DE VIDA]</b><br>DÍAS: %{y:.2f}<extra></extra>'
    ))

    # 2. Run Life General
    if 'RunLife_General' in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly['Mes'], 
            y=df_monthly['RunLife_General'], 
            name='TIEMPO DE VIDA TOTAL', 
            mode='lines+markers',
            marker=dict(symbol='circle-open', size=8, color=COLOR_RUNLIFE_GEN), 
            line=dict(width=3, color=COLOR_RUNLIFE_GEN),
            hovertemplate='<b>[TIEMPO DE VIDA TOTAL]</b><br>DÍAS: %{y:.2f}<extra></extra>'
        ))

    # 3. Run Life Efectivo Total
    if 'RunLife_Efectivo' in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly['Mes'], 
            y=df_monthly['RunLife_Efectivo'], 
            name='TIEMPO DE VIDA EFECTIVO TOTAL', 
            mode='lines+markers',
            marker=dict(symbol='circle', size=8, color=COLOR_RLE), 
            line=dict(width=3, dash='dot', color=COLOR_RLE),
            hovertemplate='<b>[TIEMPO DE VIDA EFECTIVO TOTAL]</b><br>DÍAS: %{y:.2f}<extra></extra>'
        ))

    # 4. Run Life Efectivo Fallados
    if 'RunLife_Efectivo_Fallados' in df_monthly.columns:
        fig.add_trace(go.Scatter(
            x=df_monthly['Mes'], 
            y=df_monthly['RunLife_Efectivo_Fallados'], 
            name='TIEMPO DE VIDA EFECTIVO', 
            mode='lines+markers',
            marker=dict(symbol='circle-open', size=8, color="#00549A"), 
            line=dict(width=3, dash='dot', color="#8FA73B"),
            hovertemplate='<b>[TIEMPO DE VIDA EFECTIVO]</b><br>DÍAS: %{y:.2f}<extra></extra>'
        ))

    # 5. TMEF
    fig.add_trace(go.Scatter(
        x=df_monthly['Mes'], 
        y=df_monthly['TMEF_Promedio'], 
        name='TMEF PROM', 
        mode='lines+markers',
        marker=dict(symbol='circle', size=7, color=COLOR_TMEF), 
        line=dict(width=2, dash='dot', color=COLOR_TMEF),
        visible='legendonly',
        hovertemplate='<b>[TMEF]</b><br>DÍAS: %{y:.2f}<extra></extra>'
    ))

    # --- LAYOUT ---
    if not df_monthly.empty:
        x_start = pd.to_datetime('2019-01-01')
        x_end = df_monthly['Mes'].max()
    else:
        x_start = pd.to_datetime('2019-01-01')
        x_end = pd.to_datetime(fecha_evaluacion)

    from theme import get_plotly_layout
    layout = get_plotly_layout()
    if titulo:
        layout['title'] = plotly_styled_title(titulo)
    else:
        layout['title'] = None
    layout.update(dict(
        showlegend=True,
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
            title=None,
            tickformat='%Y-%m',
            range=[x_start, x_end],
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec',
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=None,
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec',
            tickfont=dict(size=9)
        ),
        margin=dict(t=40, b=30, l=35, r=35),
        height=280
    ))

    fig.update_layout(**layout)
    # Decoración HUD
    fig.add_shape(type='line', x0=0, y0=1.02, x1=1, y1=1.02, xref='paper', yref='paper', line=dict(color='#00f2ff', width=2))

    return fig, df_monthly


def generar_grafico_pozos_indices(df_bd, df_forma9, fecha_evaluacion, titulo="Gráfico Pozos e Índices"):
    """
    Genera figura mensual enfocada en Pozos (ON/OFF) e Índices de Falla.
    Incluye: Pozos_ON, Pozos_OFF, Indice_Falla_ON, Indice_Falla_ON_ALS
    """
    df_monthly = generar_resumen_mensual(df_bd, df_forma9, fecha_evaluacion)
    if df_monthly.empty:
        return None, df_monthly

    # Normalizar índices defensivamente
    for col in ['Indice_Falla_ON', 'Indice_Falla_ON_ALS']:
        if col in df_monthly.columns:
            df_monthly[col] = pd.to_numeric(df_monthly[col], errors='coerce')
            max_val = df_monthly[col].max(skipna=True)
            if pd.notna(max_val) and (max_val > 1 and max_val <= 100):
                df_monthly[col] = df_monthly[col] / 100.0
            df_monthly[col] = df_monthly[col].clip(lower=0.0, upper=10.0)
            df_monthly[col].fillna(0, inplace=True)

    # Inyectar estilos dinámicos de Plotly
    inject_plotly_dynamic_styles()
    
    # Colores HUD más vibrantes
    CYAN_NEON = '#00D9FF'
    MAGENTA_ALERTA = '#ff0055'
    AMARILLO_NEON = '#FFAB40'
    GRID_COLOR = 'rgba(128,128,128,0.15)'
    FONT_TECH = 'Consolas, "Courier New", monospace'

    # Asignación de colores
    COLOR_POZOS_ON = CYAN_NEON
    COLOR_POZOS_OFF = '#141943'
    COLOR_IF_ON = MAGENTA_ALERTA
    COLOR_IF_ALS = AMARILLO_NEON

    fig = go.Figure()

    # --- TRAZAS ---

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
        hovertemplate='<b>[ESTADO: INACTIVOS]</b><br>CANTIDAD: %{y}<extra></extra>'
    ))

    # 2. Índices de Falla
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
    if titulo:
        layout['title'] = plotly_styled_title(titulo)
    else:
        layout['title'] = None
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
            title=None,
            tickformat='%Y-%m',
            range=[x_start, x_end],
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec',
            tickfont=dict(size=9)
        ),
        yaxis=dict(
            title=None,
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec',
            tickfont=dict(size=9)
        ),
        yaxis2=dict(
            title=None,
            overlaying='y',
            side='right',
            range=[0, upper_y2],
            tickformat='.0%',
            showgrid=False,
            linecolor='#00f2ff',
            tickfont=dict(size=9, color='#00f2ff')
        ),
        margin=dict(t=40, b=30, l=35, r=35),
        height=280
    ))

    fig.update_layout(**layout)
    # Decoración HUD
    fig.add_shape(type='line', x0=0, y0=1.02, x1=1, y1=1.02, xref='paper', yref='paper', line=dict(color='#00f2ff', width=2))

    return fig, df_monthly


def render_premium_echarts_run_life(df_monthly, titulo="TIEMPO DE VIDA DASHBOARD"):
    """
    Renderiza un gráfico premium de Tiempo de Vida utilizando ECharts (HTML/JS).
    """
    import json
    import streamlit.components.v1 as components
    from io import BytesIO

    if df_monthly is None or df_monthly.empty:
        return st.info("No hay datos mensuales para este filtro.")

    # Preparar datos para descarga en Excel
    df_export = df_monthly[['Mes', 'RunLife_Promedio']].copy()
    if 'RunLife_General' in df_monthly.columns:
        df_export['RunLife_General'] = df_monthly['RunLife_General']
    if 'TMEF_Promedio' in df_monthly.columns:
        df_export['TMEF_Promedio'] = df_monthly['TMEF_Promedio']
    if 'RunLife_Efectivo' in df_monthly.columns:
        df_export['RunLife_Efectivo'] = df_monthly['RunLife_Efectivo']
    if 'RunLife_Efectivo_Fallados' in df_monthly.columns:
        df_export['RunLife_Efectivo_Fallados'] = df_monthly['RunLife_Efectivo_Fallados']
    
    # Renombrar columnas para mejor legibilidad
    df_export.rename(columns={
        'Mes': 'Mes',
        'RunLife_Promedio': 'Tiempo de Vida Promedio (días)',
        'RunLife_General': 'Tiempo de Vida Total (días)',
        'TMEF_Promedio': 'TMEF Promedio (días)',
        'RunLife_Efectivo': 'Tiempo de Vida Efectivo Total (días)',
        'RunLife_Efectivo_Fallados': 'Tiempo de Vida Efectivo Fallados (días)'
    }, inplace=True)
    
    # El botón de exportación individual ha sido eliminado.
    # La exportación se realiza de forma global al final del reporte.

    # Asegurar conversión a string para JSON
    categories = [str(m) for m in df_monthly['Mes'].dt.strftime('%b %Y')]
    def _safe_list(series):
        return [round(float(x), 2) if pd.notna(x) else None for x in series.tolist()]

    rl_prom = _safe_list(df_monthly['RunLife_Promedio'])
    rl_gen = _safe_list(df_monthly.get('RunLife_General', pd.Series([0]*len(df_monthly))))
    tmef = _safe_list(df_monthly.get('TMEF_Promedio', pd.Series([0]*len(df_monthly))))
    rle = _safe_list(df_monthly.get('RunLife_Efectivo', pd.Series([0]*len(df_monthly))))
    rle_fallados = _safe_list(df_monthly.get('RunLife_Efectivo_Fallados', pd.Series([0]*len(df_monthly))))
    if_on_1500 = [round(float(x) * 100, 2) if pd.notna(x) else None for x in df_monthly.get('Indice_Falla_ON_1500', [])]
    if_als_1500 = [round(float(x) * 100, 2) if pd.notna(x) else None for x in df_monthly.get('Indice_Falla_ON_ALS_1500', [])]
    
    COLOR_SUCCESS = "#137659" 
    COLOR_TOTAL = "#095139"   
    COLOR_EFECTIVO = "#c09c2e" 
    COLOR_EFECTIVO_FALLADOS = "#a28834" 
    COLOR_TMEF = "#5b5c55"     
    COLOR_ACCENT = "#137659"

    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "show": bool(titulo), "text": titulo.upper(),
            "left": "center",
            "top": 10,
            "textStyle": {
                "color": "#137659",
                "fontSize": 14,
                "fontFamily": "Arial, sans-serif",
                "fontWeight": "bold"
            }
        },
        "textStyle": {"fontFamily": "Arial, sans-serif"},
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#137659",
            "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}
        },
        "legend": {
            "data": ["T. Vida Promed", "T. Vida Total", "T. Vida Efectivo", "T. V. Efec. Fallado", "TMEF", "Ind. Falla ON <1500", "Ind. Falla ALS <1500"],
            "bottom": 0,
            "textStyle": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "18%", "containLabel": True},
        "xAxis": [{"type": "category", "data": categories, "axisLabel": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}}],
        "yAxis": [
            {"type": "value", "name": "DÍAS", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}},
            {"type": "value", "name": "INDICE %", "position": "right", "axisLabel": {"color": "#475569", "formatter": "{value}%", "fontFamily": "Arial, sans-serif"}}
        ],
        "series": [
            {"name": "T. Vida Promed", "type": "line", "smooth": True, "lineStyle": {"width": 3, "color": COLOR_SUCCESS}, "itemStyle": {"color": COLOR_SUCCESS}, "data": rl_prom},
            {"name": "T. Vida Total", "type": "line", "smooth": True, "lineStyle": {"width": 2, "type": "dashed", "color": COLOR_TOTAL}, "itemStyle": {"color": COLOR_TOTAL}, "data": rl_gen},
            {"name": "T. Vida Efectivo", "type": "line", "smooth": True, "lineStyle": {"width": 2, "type": "dotted", "color": COLOR_EFECTIVO}, "itemStyle": {"color": COLOR_EFECTIVO}, "data": rle},
            {"name": "T. V. Efec. Fallado", "type": "line", "smooth": True, "lineStyle": {"width": 2, "type": "dotted", "color": COLOR_EFECTIVO_FALLADOS}, "itemStyle": {"color": COLOR_EFECTIVO_FALLADOS}, "data": rle_fallados},
            {"name": "TMEF", "type": "line", "smooth": True, "lineStyle": {"width": 1, "type": "dashed", "color": COLOR_TMEF}, "itemStyle": {"color": COLOR_TMEF}, "data": tmef},
            {"name": "Ind. Falla ON <1500", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 2, "type": "dashed", "color": "#c09c2e"}, "itemStyle": {"color": "#c09c2e"}, "data": if_on_1500},
            {"name": "Ind. Falla ALS <1500", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 2, "type": "dashed", "color": "#d32f2f"}, "itemStyle": {"color": "#d32f2f"}, "data": if_als_1500}
        ]
    }
    chart_height = 400
    container_height = chart_height + 20

    html_template = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        #chart-container-rl {{
            position: relative; 
            width:100%; 
            height:{chart_height}px; 
            background: #ffffff; 
            border: 1.5px solid rgba(19, 118, 89, 0.13); 
            border-radius: 16px; 
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(19, 118, 89, 0.04), 0 8px 32px rgba(19, 118, 89, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }}
        #chart-container-rl:hover {{
            transform: translateY(-2px);
            border-color: rgba(19, 118, 89, 0.25);
            box-shadow: 0 6px 20px rgba(19, 118, 89, 0.10), 0 12px 40px rgba(19, 118, 89, 0.12);
        }}
        #zoom-btn-rl {{
            position: absolute; 
            top: 10px; 
            right: 10px; 
            z-index: 1000; 
            background: rgba(255, 255, 255, 0.95); 
            border: 1px solid rgba(19, 118, 89, 0.25); 
            color: #137659; 
            padding: 4px 10px; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 8px; 
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            backdrop-filter: blur(4px);
            transition: all 0.25s ease;
            height: 22px;
            line-height: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            display: flex;
            align-items: center;
        }}
        #zoom-btn-rl:hover {{
            background: #137659;
            color: #ffffff;
            border-color: #137659;
            box-shadow: 0 4px 12px rgba(19, 118, 89, 0.2);
        }}
    </style>
    <div id="chart-container-rl">
        <div id="echarts-rl" style="width:100%; height:100%;"></div>
        <button id="zoom-btn-rl">⛶ FULL</button>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var container = document.getElementById('chart-container-rl');
            var chartDom = document.getElementById('echarts-rl');
            var zoomBtn = document.getElementById('zoom-btn-rl');
            var myChart = echarts.init(chartDom, null);
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
                    zoomBtn.innerHTML = '✕ CLOSE';
                }} else {{
                    document.exitFullscreen();
                    container.style.height = '{chart_height}px';
                    zoomBtn.innerHTML = '⛶ FULL';
                }}
            }});

            document.addEventListener('fullscreenchange', exitHandler);
            function exitHandler() {{
                if (!document.fullscreenElement) {{
                    container.style.height = '{chart_height}px';
                    zoomBtn.innerHTML = '⛶ FULL';
                    myChart.resize();
                }} else {{
                    myChart.resize();
                }}
            }}
        }})();
    </script>
    """
    components.html(html_template, height=container_height)
    st.markdown('</div>', unsafe_allow_html=True)
def render_premium_echarts_pozos(df_monthly, titulo="OPERATIVIDAD DASHBOARD"):
    """
    Renderiza un gráfico premium de Pozos e Índices utilizando ECharts (HTML/JS).
    """
    import json
    import streamlit.components.v1 as components
    from io import BytesIO

    if df_monthly is None or df_monthly.empty:
        return st.info("No hay datos mensuales para este filtro.")

    # Preparar datos para descarga en Excel
    df_export = df_monthly[['Mes', 'Pozos_ON', 'Pozos_OFF']].copy()
    if 'Indice_Falla_ON' in df_monthly.columns:
        df_export['Indice_Falla_ON'] = df_monthly['Indice_Falla_ON']
    if 'Indice_Falla_ON_ALS' in df_monthly.columns:
        df_export['Indice_Falla_ON_ALS'] = df_monthly['Indice_Falla_ON_ALS']
    
    # Renombrar columnas para mejor legibilidad
    df_export.rename(columns={
        'Mes': 'Mes',
        'Pozos_ON': 'Pozos Activos',
        'Pozos_OFF': 'Pozos Inactivos',
        'Indice_Falla_ON': 'Índice de Falla ON (%)',
        'Indice_Falla_ON_ALS': 'Índice de Falla ALS ON (%)'
    }, inplace=True)
    
    # Convertir índices a porcentaje para mejor legibilidad
    if 'Índice de Falla ON (%)' in df_export.columns:
        df_export['Índice de Falla ON (%)'] = df_export['Índice de Falla ON (%)'] * 100
    if 'Índice de Falla ALS ON (%)' in df_export.columns:
        df_export['Índice de Falla ALS ON (%)'] = df_export['Índice de Falla ALS ON (%)'] * 100
    
    # El botón de exportación individual ha sido eliminado.
    # La exportación se realiza de forma global al final del reporte.

    # Asegurar conversión a string para JSON
    categories = [str(m) for m in df_monthly['Mes'].dt.strftime('%b %Y')]
    pozos_on = [int(x) if pd.notna(x) else 0 for x in df_monthly['Pozos_ON'].tolist()]
    pozos_off = [int(x) if pd.notna(x) else 0 for x in df_monthly['Pozos_OFF'].tolist()]
    if_on = [round(float(x) * 100, 2) if pd.notna(x) else None for x in df_monthly.get('Indice_Falla_ON', [])]
    if_als = [round(float(x) * 100, 2) if pd.notna(x) else None for x in df_monthly.get('Indice_Falla_ON_ALS', [])]
    if_on_1500 = [round(float(x) * 100, 2) if pd.notna(x) else None for x in df_monthly.get('Indice_Falla_ON_1500', [])]
    if_als_1500 = [round(float(x) * 100, 2) if pd.notna(x) else None for x in df_monthly.get('Indice_Falla_ON_ALS_1500', [])]
    COLOR_ACCENT = "#137659"
    COLOR_DANGER = "#d32f2f"
    COLOR_WARNING = "#c09c2e"

    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "show": bool(titulo), "text": titulo.upper(),
            "left": "center",
            "top": 10,
            "textStyle": {
                "color": "#137659",
                "fontSize": 14,
                "fontFamily": "Arial, sans-serif",
                "fontWeight": "bold"
            }
        },
        "textStyle": {"fontFamily": "Arial, sans-serif"},
        "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255, 255, 255, 0.95)", "borderColor": COLOR_ACCENT, "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}},
        "legend": {"data": ["Pozos ON", "Pozos OFF", "Ind. Falla ON", "Ind. Falla ALS", "Ind. Falla ON <1500", "Ind. Falla ALS <1500"], "bottom": 0, "textStyle": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}},
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "18%", "containLabel": True},
        "xAxis": [{"type": "category", "data": categories, "axisLabel": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}}],
        "yAxis": [
            {"type": "value", "name": "POZOS", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}},
            {"type": "value", "name": "INDICE %", "position": "right", "axisLabel": {"color": "#475569", "formatter": "{value}%", "fontFamily": "Arial, sans-serif"}}
        ],
        "series": [
            {"name": "Pozos ON", "type": "bar", "stack": "total", "itemStyle": {"color": COLOR_ACCENT}, "data": pozos_on},
            {
                "name": "Pozos OFF", 
                "type": "bar", 
                "stack": "total", 
                "itemStyle": {
                    "color": "#5b5c55",
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
            {"name": "Ind. Falla ON", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 3, "color": COLOR_DANGER}, "itemStyle": {"color": COLOR_DANGER}, "data": if_on},
            {"name": "Ind. Falla ALS", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 2, "color": COLOR_WARNING}, "itemStyle": {"color": COLOR_WARNING}, "data": if_als},
            {"name": "Ind. Falla ON <1500", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 2, "type": "dashed", "color": "#c09c2e"}, "itemStyle": {"color": "#c09c2e"}, "data": if_on_1500},
            {"name": "Ind. Falla ALS <1500", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 2, "type": "dashed", "color": "#d32f2f"}, "itemStyle": {"color": "#d32f2f"}, "data": if_als_1500}
        ]
    }

    chart_height = 400
    container_height = chart_height + 20

    html_template = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        #chart-container-pozos {{
            position: relative; 
            width:100%; 
            height:{chart_height}px; 
            background: #ffffff; 
            border: 1.5px solid rgba(19, 118, 89, 0.13); 
            border-radius: 16px; 
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(19, 118, 89, 0.04), 0 8px 32px rgba(19, 118, 89, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }}
        #chart-container-pozos:hover {{
            transform: translateY(-2px);
            border-color: rgba(19, 118, 89, 0.25);
            box-shadow: 0 6px 20px rgba(19, 118, 89, 0.10), 0 12px 40px rgba(19, 118, 89, 0.12);
        }}
        #zoom-btn-pozos {{
            position: absolute; 
            top: 10px; 
            right: 10px; 
            z-index: 1000; 
            background: rgba(255, 255, 255, 0.95); 
            border: 1px solid rgba(19, 118, 89, 0.25); 
            color: #137659; 
            padding: 4px 10px; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 8px; 
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            backdrop-filter: blur(4px);
            transition: all 0.25s ease;
            height: 22px;
            line-height: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            display: flex;
            align-items: center;
        }}
        #zoom-btn-pozos:hover {{
            background: #137659;
            color: #ffffff;
            border-color: #137659;
            box-shadow: 0 4px 12px rgba(19, 118, 89, 0.2);
        }}
    </style>
    <div id="chart-container-pozos">
        <div id="echarts-pozos" style="width:100%; height:100%;"></div>
        <button id="zoom-btn-pozos">⛶ FULL</button>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var container = document.getElementById('chart-container-pozos');
            var chartDom = document.getElementById('echarts-pozos');
            var zoomBtn = document.getElementById('zoom-btn-pozos');
            var myChart = echarts.init(chartDom, null);
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
                    zoomBtn.innerHTML = '✕ CLOSE';
                }} else {{
                    document.exitFullscreen();
                    container.style.height = '{chart_height}px';
                    zoomBtn.innerHTML = '⛶ FULL';
                }}
            }});

            document.addEventListener('fullscreenchange', exitHandler);
            function exitHandler() {{
                if (!document.fullscreenElement) {{
                    container.style.height = '{chart_height}px';
                    zoomBtn.innerHTML = '⛶ FULL';
                    myChart.resize();
                }} else {{
                    myChart.resize();
                }}
            }}
        }})();
    </script>
    """
    components.html(html_template, height=container_height)
