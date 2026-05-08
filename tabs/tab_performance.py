"""
tabs/tab_performance.py
=======================
Análisis de Performance BOPD vs Longevidad de Equipos.
Estética HUD con alta densidad de datos y gráficos ECharts Premium.
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
from styles import render_hud_table

def bucket_runlife(days):
    """Categoriza los días de Run Life en los rangos solicitados: <2, 2-4, 4-6, >6 años."""
    if pd.isna(days): return 'N/A'
    years = days / 365.25
    if years < 2: return '< 2 años'
    if years < 4: return '2 - 4 años'
    if years < 6: return '4 - 6 años'
    return '> 6 años'

def render_performance_echarts(df_range):
    """Renderiza el gráfico de correlación usando ECharts para estética IU profesional."""
    
    categories = df_range.index.tolist()
    pozos_data = df_range['POZO'].tolist()
    bopd_data = [round(x, 1) for x in df_range['BOPD'].tolist()]

    options = {
        "backgroundColor": "transparent",
        "title": {
            "text": "BOPD VS RUN LIFE (CATEGORÍA)",
            "left": "center",
            "top": 0,
            "textStyle": {
                "color": "#00f2ff",
                "fontSize": 13,
                "fontFamily": "Arial, sans-serif",
                "fontWeight": "bold"
            }
        },
        "textStyle": {"fontFamily": "Arial, sans-serif"},
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(6, 10, 30, 0.9)",
            "borderColor": "#00f2ff",
            "borderWidth": 1,
            "textStyle": {"color": "#fff", "fontFamily": "Arial, sans-serif"}
        },
        "legend": {
            "data": ["NÚMERO DE POZOS", "PROD. PROMEDIO (BOPD)"],
            "textStyle": {"color": "#ccc", "fontSize": 10, "fontFamily": "Arial, sans-serif"},
            "bottom": 0
        },
        "grid": {"top": "15%", "left": "5%", "right": "5%", "bottom": "15%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.1)"}},
            "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}
        },
        "yAxis": [
            {
                "type": "value",
                "name": "POZOS",
                "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}},
                "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}
            },
            {
                "type": "value",
                "name": "BOPD",
                "splitLine": {"show": False},
                "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}
            }
        ],
        "series": [
            {
                "name": "NÚMERO DE POZOS",
                "type": "bar",
                "barWidth": "40%",
                "itemStyle": {
                    "color": {
                        "type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [{"offset": 0, "color": "#00f2ff"}, {"offset": 1, "color": "rgba(0, 242, 255, 0.1)"}]
                    },
                    "borderRadius": [5, 5, 0, 0]
                },
                "data": pozos_data
            },
            {
                "name": "PROD. PROMEDIO (BOPD)",
                "type": "line",
                "yAxisIndex": 1,
                "smooth": True,
                "symbol": "diamond",
                "symbolSize": 12,
                "lineStyle": {"width": 4, "color": "#ff00ff", "shadowBlur": 10, "shadowColor": "#ff00ff"},
                "itemStyle": {"color": "#ff00ff"},
                "label": {"show": True, "position": "top", "color": "#fff", "fontSize": 10, "fontFamily": "Arial, sans-serif"},
                "data": bopd_data
            }
        ]
    }

    html = f"""
    <div id="perf-chart" style="width:100%; height:450px; background:#060a1e; border-radius:15px; overflow:hidden; border:1px solid rgba(0,242,255,0.1);"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        var chart = echarts.init(document.getElementById('perf-chart'), 'dark');
        chart.setOption({json.dumps(options)});
        window.onresize = function() {{ chart.resize(); }};
    </script>
    """
    components.html(html, height=460)

def render_tab_performance(df_bd_filtered, df_forma9_filtered, fecha_evaluacion):
    """Renderiza el contenido del Tab PERFORMANCE con estilo HUD."""
    
    fecha_eval = pd.to_datetime(fecha_evaluacion)
    
    # 1. PROCESAMIENTO DE CORRELACIÓN (Solo Pozos ON del Mes)
    try:
        df_f9 = df_forma9_filtered.copy()
        df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9.get('FECHA_FORMA9'), errors='coerce')
        
        df_month = df_f9[
            (df_f9['FECHA_FORMA9'].dt.year == fecha_eval.year) & 
            (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)
        ].copy()
        
        bopd_col = next((c for c in df_month.columns if 'BOPD' in str(c).upper()), None)
        if bopd_col:
            df_month[bopd_col] = pd.to_numeric(df_month[bopd_col], errors='coerce').fillna(0)
            df_on = df_month[df_month[bopd_col] > 0].copy()
            df_sum = df_on.groupby('POZO', as_index=False).agg({bopd_col: 'mean'}) 
            df_sum.rename(columns={bopd_col: 'BOPD'}, inplace=True)
        else:
            df_sum = pd.DataFrame(columns=['POZO', 'BOPD'])

        bd = df_bd_filtered.copy()
        bd['FECHA_RUN'] = pd.to_datetime(bd.get('FECHA_RUN'), errors='coerce')
        
        results = []
        for _, row in df_sum.iterrows():
            pozo = row['POZO']
            bopd = row['BOPD']
            pozo_data = bd[bd['POZO'] == pozo].sort_values('FECHA_RUN', ascending=False)
            if not pozo_data.empty:
                rl = pozo_data.iloc[0].get('RUN LIFE', 0)
                results.append({'POZO': pozo, 'BOPD': bopd, 'RUN_LIFE': rl, 'RANGO': bucket_runlife(rl)})

        df_perf = pd.DataFrame(results)

    except Exception as e:
        st.error(f"Error procesando performance: {e}")
        df_perf = pd.DataFrame()

    if df_perf.empty:
        st.warning("⚠️ No hay pozos ON detectados para el mes de evaluación seleccionado.")
        return

    # KPIs de la Vista (4 COLUMNS for symmetry with MTBF)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🎯</div><div class="kpi-label">POZOS ON (MES)</div><div class="kpi-value" style="color:#00f2ff;">{len(df_perf)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🛢️</div><div class="kpi-label">PROD. PROM. ON</div><div class="kpi-value" style="color:#00ff9d;">{df_perf["BOPD"].mean():.1f}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🔥</div><div class="kpi-label">TOTAL BOPD ON</div><div class="kpi-value" style="color:#ffbd00;">{df_perf["BOPD"].sum():.0f}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">💎</div><div class="kpi-label">MAX LONGEVIDAD</div><div class="kpi-value" style="color:#ff00ff;">{df_perf["RUN_LIFE"].max():.0f} d</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        df_range = df_perf.groupby('RANGO').agg({'POZO': 'count', 'BOPD': 'mean'}).reindex(['< 2 años', '2 - 4 años', '4 - 6 años', '> 6 años']).fillna(0)
        
        categories = df_range.index.tolist()
        pozos_data = df_range['POZO'].tolist()
        bopd_data = [round(x, 1) for x in df_range['BOPD'].tolist()]

        options = {
            "backgroundColor": "transparent",
            "title": {
                "text": "📈 CORRELACIÓN PROD. VS LONGEVIDAD",
                "left": "center",
                "top": 0,
                "textStyle": {"color": "#00f2ff", "fontSize": 13, "fontFamily": "Arial, sans-serif", "fontWeight": "bold", "textShadowBlur": 10, "textShadowColor": "rgba(0, 242, 255, 0.4)"}
            },
            "textStyle": {"fontFamily": "Arial, sans-serif"},
            "tooltip": {"trigger": "axis", "backgroundColor": "rgba(6, 10, 30, 0.9)", "borderColor": "#00f2ff", "borderWidth": 1, "textStyle": {"color": "#fff", "fontFamily": "Arial, sans-serif"}},
            "legend": {"data": ["POZOS", "BOPD"], "textStyle": {"color": "#ccc", "fontSize": 10, "fontFamily": "Arial, sans-serif"}, "bottom": 0, "icon": "circle"},
            "grid": {"top": "15%", "left": "5%", "right": "5%", "bottom": "18%", "containLabel": True},
            "xAxis": {"type": "category", "data": categories, "axisLabel": {"color": "#888", "fontSize": 10, "fontFamily": "Arial, sans-serif"}},
            "yAxis": [
                {"type": "value", "name": "POZOS", "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}, "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}}, 
                {"type": "value", "name": "BOPD", "splitLine": {"show": False}, "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}}
            ],
            "series": [
                {
                    "name": "POZOS", "type": "bar", "barWidth": "40%", 
                    "itemStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1, "colorStops": [{"offset": 0, "color": "#00f2ff"}, {"offset": 1, "color": "rgba(0, 242, 255, 0.1)"}]}, "borderRadius": [5, 5, 0, 0]}, 
                    "data": pozos_data
                },
                {
                    "name": "BOPD", "type": "line", "yAxisIndex": 1, "smooth": True, "symbol": "diamond", "symbolSize": 8, 
                    "lineStyle": {"width": 3, "color": "#ff00ff", "shadowBlur": 10, "shadowColor": "rgba(255, 0, 255, 0.5)"}, 
                    "itemStyle": {"color": "#ff00ff"}, "data": bopd_data
                }
            ]
        }
        components.html(f'<div id="perf-chart-main" style="width:100%; height:380px; background:#060a1e; border-radius:15px; overflow:hidden; border:1px solid rgba(0,242,255,0.1);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("perf-chart-main"),"dark");myChart.setOption({json.dumps(options)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    with col_right:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        top_bopd = df_perf.sort_values('BOPD', ascending=False).head(10)
        
        echarts_top_bopd = {
            "backgroundColor": "transparent",
            "title": {
                "text": "🏆 TOP 10 PRODUCCIÓN POR POZO",
                "left": "center",
                "top": 0,
                "textStyle": {"color": "#00f2ff", "fontSize": 13, "fontFamily": "Arial, sans-serif", "fontWeight": "bold", "textShadowBlur": 10, "textShadowColor": "rgba(0, 242, 255, 0.4)"}
            },
            "textStyle": {"fontFamily": "Arial, sans-serif"},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}, "backgroundColor": "rgba(6, 10, 30, 0.9)", "borderColor": "#00f2ff", "textStyle": {"color": "#fff", "fontFamily": "Arial, sans-serif"}},
            "grid": {"left": "3%", "right": "15%", "bottom": "10%", "top": "15%", "containLabel": True},
            "xAxis": {"type": "value", "splitLine": {"show": False}, "axisLabel": {"show": False}},
            "yAxis": {"type": "category", "data": top_bopd['POZO'].tolist(), "axisLabel": {"color": "#fff", "fontSize": 10, "fontFamily": "Arial, sans-serif"}},
            "series": [{
                "type": "bar",
                "data": top_bopd['BOPD'].tolist(),
                "itemStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0, "colorStops": [{"offset": 0, "color": "#00ff9d"}, {"offset": 1, "color": "rgba(0, 255, 157, 0.1)"}]}, "borderRadius": [0, 5, 5, 0], "shadowBlur": 10, "shadowColor": "rgba(0, 255, 157, 0.3)"},
                "label": {"show": True, "position": "right", "color": "#00ff9d", "fontFamily": "Arial, sans-serif", "formatter": "{c} b"}
            }]
        }
        components.html(f'<div id="perf-chart-top" style="width:100%; height:380px; background:#060a1e; border-radius:15px; overflow:hidden; border:1px solid rgba(0,242,255,0.1);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("perf-chart-top"),"dark");myChart.setOption({json.dumps(echarts_top_bopd)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- LA TABLITA (ESTILO HUD ESPECTACULAR) ---
    st.markdown("<h5 style='color:#00f2ff; font-family:Arial, sans-serif !important;'>📝 DETALLE DE PRODUCCIÓN POZOS ON</h5>", unsafe_allow_html=True)
    
    # Preparamos el DF para el renderizador HUD
    df_render = df_perf.sort_values('BOPD', ascending=False).rename(columns={
        'POZO': 'POZO',
        'BOPD': 'PROD. BOPD',
        'RUN_LIFE': 'DÍAS RUN LIFE',
        'RANGO': 'CATEGORÍA'
    })
    
    # Llamamos al nuevo renderizador espectacular
    render_hud_table(df_render)
