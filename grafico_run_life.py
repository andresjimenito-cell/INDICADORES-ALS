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
    layout['title'] = plotly_styled_title(titulo)
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
            title=dict(text='<b>TIEMPO</b>', font=dict(size=14, family='Outfit')),
            tickformat='%Y-%m',
            range=[x_start, x_end],
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec'
        ),
        yaxis=dict(
            title=dict(text='<b>DÍAS DE VIDA</b>', font=dict(size=14, family='Outfit')),
            gridcolor='rgba(255,255,255,0.05)',
            linecolor='#135bec'
        ),
        margin=dict(t=100, b=80, l=90, r=90)
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
        base=df_monthly['Pozos_ON'],
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
            title=dict(text='<b>CANTIDAD POZOS</b>', font=dict(size=14, family='Outfit')),
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
    
    # Crear botón de descarga
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Tiempo de Vida y TEMF')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Descargar datos en Excel",
        data=excel_data,
        file_name="tiempo_vida_temf.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_run_life_excel"
    )

    # Asegurar conversión a string para JSON
    categories = [str(m) for m in df_monthly['Mes'].dt.strftime('%b %Y')]
    rl_prom = [round(float(x), 2) for x in df_monthly['RunLife_Promedio'].tolist()]
    rl_gen = [round(float(x), 2) for x in df_monthly.get('RunLife_General', [0]*len(df_monthly)).tolist()]
    tmef = [round(float(x), 2) for x in df_monthly.get('TMEF_Promedio', [0]*len(df_monthly)).tolist()]
    rle = [round(float(x), 2) for x in df_monthly.get('RunLife_Efectivo', [0]*len(df_monthly)).tolist()]
    rle_fallados = [round(float(x), 2) for x in df_monthly.get('RunLife_Efectivo_Fallados', [0]*len(df_monthly)).tolist()]
    
    COLOR_SUCCESS = "#00ff9f" # Verde Eléctrico
    COLOR_TOTAL = "#a6ff00"   # Verde Lima
    COLOR_EFECTIVO = "#FFF700" # Amarillo
    COLOR_EFECTIVO_FALLADOS = "#00CCFF" # Cyan
    COLOR_TMEF = "#E6E6E6"     # Gris/Blanco
    COLOR_ACCENT = "#00f2ff"

    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "text": titulo.upper(),
            "left": "center",
            "top": 0,
            "textStyle": {"color": "#fff", "fontSize": 16, "fontFamily": "Outfit", "fontWeight": "900"}
        },
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(6, 10, 30, 0.9)",
            "borderColor": COLOR_ACCENT,
            "textStyle": {"color": "#fff"}
        },
        "legend": {
            "data": ["T. Vida Promed", "T. Vida Total", "T. Vida Efectivo", "T. V. Efec. Fallado", "TMEF"],
            "bottom": 0,
            "textStyle": {"color": "#ccc", "fontSize": 10}
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
        "xAxis": [{"type": "category", "data": categories, "axisLabel": {"color": "#888", "fontSize": 10}}],
        "yAxis": [{"type": "value", "name": "DÍAS", "axisLabel": {"color": "#888"}}],
        "series": [
            {"name": "T. Vida Promed", "type": "line", "smooth": True, "lineStyle": {"width": 3, "color": COLOR_SUCCESS}, "itemStyle": {"color": COLOR_SUCCESS}, "data": rl_prom},
            {"name": "T. Vida Total", "type": "line", "smooth": True, "lineStyle": {"width": 2, "type": "dashed", "color": COLOR_TOTAL}, "itemStyle": {"color": COLOR_TOTAL}, "data": rl_gen},
            {"name": "T. Vida Efectivo", "type": "line", "smooth": True, "lineStyle": {"width": 2, "type": "dotted", "color": COLOR_EFECTIVO}, "itemStyle": {"color": COLOR_EFECTIVO}, "data": rle},
            {"name": "T. V. Efec. Fallado", "type": "line", "smooth": True, "lineStyle": {"width": 2, "type": "dotted", "color": COLOR_EFECTIVO_FALLADOS}, "itemStyle": {"color": COLOR_EFECTIVO_FALLADOS}, "data": rle_fallados},
            {"name": "TMEF", "type": "line", "smooth": True, "lineStyle": {"width": 1, "type": "dashed", "color": COLOR_TMEF}, "itemStyle": {"color": COLOR_TMEF}, "data": tmef}
        ]
    }
    chart_height = 400
    container_height = chart_height + 20

    html_template = f"""
    <div id="chart-container-rl" style="position: relative; width:100%; height:{chart_height}px; background: #060a1e; border-radius: 15px; overflow: hidden;">
        <div id="echarts-rl" style="width:100%; height:100%;"></div>
        <button id="zoom-btn-rl" style="
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
            var container = document.getElementById('chart-container-rl');
            var chartDom = document.getElementById('echarts-rl');
            var zoomBtn = document.getElementById('zoom-btn-rl');
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
    
    # Crear botón de descarga
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Pozos e Índices')
    excel_data = output.getvalue()
    
    st.download_button(
        label="📥 Descargar datos en Excel",
        data=excel_data,
        file_name="pozos_indices.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_pozos_indices_excel"
    )

    # Asegurar conversión a string para JSON
    categories = [str(m) for m in df_monthly['Mes'].dt.strftime('%b %Y')]
    pozos_on = df_monthly['Pozos_ON'].tolist()
    pozos_off = df_monthly['Pozos_OFF'].tolist()
    if_on = [round(float(x) * 100, 2) if pd.notna(x) else 0 for x in df_monthly.get('Indice_Falla_ON', [])]
    if_als = [round(float(x) * 100, 2) if pd.notna(x) else 0 for x in df_monthly.get('Indice_Falla_ON_ALS', [])]
    COLOR_ACCENT = "#00f2ff"
    COLOR_DANGER = "#ff0055"
    COLOR_WARNING = "#ffab40"

    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "text": titulo.upper(),
            "left": "center",
            "top": 0,
            "textStyle": {"color": "#fff", "fontSize": 16, "fontFamily": "Outfit", "fontWeight": "900"}
        },
        "tooltip": {"trigger": "axis", "backgroundColor": "rgba(6, 10, 30, 0.9)", "borderColor": COLOR_ACCENT, "textStyle": {"color": "#fff"}},
        "legend": {"data": ["Pozos ON", "Pozos OFF", "Ind. Falla ON", "Ind. Falla ALS"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 10}},
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
        "xAxis": [{"type": "category", "data": categories, "axisLabel": {"color": "#888", "fontSize": 10}}],
        "yAxis": [
            {"type": "value", "name": "POZOS", "axisLabel": {"color": "#888"}},
            {"type": "value", "name": "INDICE %", "position": "right", "axisLabel": {"color": "#888", "formatter": "{value}%"}}
        ],
        "series": [
            {"name": "Pozos ON", "type": "bar", "stack": "total", "itemStyle": {"color": COLOR_ACCENT}, "data": pozos_on},
            {
                "name": "Pozos OFF", 
                "type": "bar", 
                "stack": "total", 
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
            {"name": "Ind. Falla ON", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 3, "color": COLOR_DANGER}, "itemStyle": {"color": COLOR_DANGER}, "data": if_on},
            {"name": "Ind. Falla ALS", "type": "line", "yAxisIndex": 1, "smooth": True, "lineStyle": {"width": 2, "color": COLOR_WARNING}, "itemStyle": {"color": COLOR_WARNING}, "data": if_als}
        ]
    }

    chart_height = 400
    container_height = chart_height + 20

    html_template = f"""
    <div id="chart-container-pozos" style="position: relative; width:100%; height:{chart_height}px; background: #060a1e; border-radius: 15px; overflow: hidden;">
        <div id="echarts-pozos" style="width:100%; height:100%;"></div>
        <button id="zoom-btn-pozos" style="
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
            var container = document.getElementById('chart-container-pozos');
            var chartDom = document.getElementById('echarts-pozos');
            var zoomBtn = document.getElementById('zoom-btn-pozos');
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
