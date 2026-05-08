"""
tabs/tab_mtbf.py
================
Visualización profesional de TMEF (MTBF).
Utiliza estética HUD y Zero Space Waste.
Typology aligned with 'Indices & Fallas' (Spectacular UI).
"""

import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
from mtbf import calcular_mtbf
from calculations import calcular_run_life_efectivo, generar_historico_run_life
from styles import render_hud_table

def render_tab_mtbf(
    df_bd_filtered,
    df_forma9_filtered,
    fecha_evaluacion,
    verificaciones_filtered,
    selected_activo,
):
    """Renderiza el contenido del Tab MTBF con estilo HUD Profesional."""
    
    # --- 1. PROCESAMIENTO ---
    try:
        mtbf_global, step_df = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        mtbf_efectivo_global = 0
        if not df_bd_filtered.empty:
            try:
                mtbf_efectivo_global, _ = calcular_mtbf(df_bd_filtered, fecha_evaluacion, col_life='RUN_LIFE_EFECTIVO')
            except: mtbf_efectivo_global = 0
        
        rl_total = df_bd_filtered['RUN LIFE'].mean() if not df_bd_filtered.empty else 0
        try:
            rl_efec, _ = calcular_run_life_efectivo(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
        except: rl_efec = 0

        # --- 2. KPI GRID SUPERIOR (4 COLUMNS) ---
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🕒</div><div class="kpi-label">TMEF GLOBAL</div><div class="kpi-value" style="color:#00f2ff;">{mtbf_global:.0f} d</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🛡️</div><div class="kpi-label">TMEF EFECTIVO</div><div class="kpi-value" style="color:#00ff9d;">{mtbf_efectivo_global:.0f} d</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">💎</div><div class="kpi-label">RL PROMEDIO</div><div class="kpi-value" style="color:#ffbd00;">{rl_total:.0f} d</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚡</div><div class="kpi-label">RL EFECTIVO</div><div class="kpi-value" style="color:#ff00ff;">{rl_efec:.0f} d</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"Error en análisis MTBF: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 3. GRÁFICOS DE TENDENCIA (SIDE BY SIDE) ---
    
    historico_run_life = generar_historico_run_life(df_bd_filtered, fecha_evaluacion)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        if historico_run_life is not None and not historico_run_life.empty:
            historico_run_life['Mes_Str'] = pd.to_datetime(historico_run_life['Mes'], errors='coerce').dt.strftime('%Y-%m')
            months = sorted(historico_run_life['Mes_Str'].unique().tolist())
            
            activos = sorted(df_bd_filtered['ACTIVO'].unique().tolist()) if 'ACTIVO' in df_bd_filtered.columns else ['GLOBAL']
            series = []
            colors = ['#00f2ff', '#ff00ff', '#00ff9d', '#ffbd00', '#7000ff']
            for i, act in enumerate(activos):
                df_act = historico_run_life[historico_run_life['ACTIVO'] == act] if 'ACTIVO' in historico_run_life.columns else historico_run_life
                data_act = [round(float(df_act[df_act['Mes_Str'] == m]['Tiempo Op. Promedio'].values[0]), 1) if len(df_act[df_act['Mes_Str'] == m]) > 0 else 0 for m in months]
                series.append({
                    "name": act, 
                    "type": "line", 
                    "smooth": True, 
                    "data": data_act, 
                    "itemStyle": {"color": colors[i % len(colors)]},
                    "lineStyle": {"width": 3},
                    "areaStyle": {"color": f"{colors[i % len(colors)]}1A"} 
                })

            echarts_rl = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "TENDENCIA DE LONGEVIDAD",
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
                    "textStyle": {"color": "#fff", "fontFamily": "Arial, sans-serif"}
                },
                "legend": {"bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 10, "fontFamily": "Arial, sans-serif"}, "icon": "circle"},
                "grid": {"left": "3%", "right": "4%", "bottom": "18%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months, "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [{"type": "value", "name": "Días", "axisLabel": {"color": "#888", "fontFamily": "Arial, sans-serif"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                "series": series
            }
            components.html(f'<div id="echarts-rl-trend" style="width:100%; height:380px; background:#060a1e; border-radius:15px; overflow:hidden; border:1px solid rgba(0,242,255,0.1);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-rl-trend"),"dark");myChart.setOption({json.dumps(echarts_rl)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    with col_right:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        if not df_bd_filtered.empty:
            df_pozo = df_bd_filtered.groupby('POZO')['RUN LIFE'].mean().reset_index()
            df_pozo.columns = ['POZO', 'VALOR']
            top_mtbf = df_pozo.sort_values('VALOR', ascending=False).head(10)
            
            echarts_bar = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "LONGEVIDAD POR POZO (TOP 10)",
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
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(6, 10, 30, 0.9)",
                    "borderColor": "#00f2ff",
                    "textStyle": {"color": "#fff", "fontFamily": "Arial, sans-serif"}
                },
                "grid": {"left": "3%", "right": "15%", "bottom": "10%", "top": "15%", "containLabel": True},
                "xAxis": {"type": "value", "splitLine": {"show": False}, "axisLabel": {"show": False}},
                "yAxis": {"type": "category", "data": top_mtbf['POZO'].tolist(), "axisLabel": {"color": "#fff", "fontSize": 10, "fontFamily": "Arial, sans-serif"}},
                "series": [{
                    "type": "bar",
                    "data": top_mtbf['VALOR'].tolist(),
                    "itemStyle": {
                        "color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0, "colorStops": [{"offset": 0, "color": "#ff00ff"}, {"offset": 1, "color": "rgba(255, 0, 255, 0.1)"}]},
                        "borderRadius": [0, 5, 5, 0]
                    },
                    "label": {"show": True, "position": "right", "color": "#ff00ff", "fontFamily": "Arial, sans-serif", "formatter": "{c} d"}
                }]
            }
            components.html(f'<div id="echarts-mtbf-bar" style="width:100%; height:380px; background:#060a1e; border-radius:15px; overflow:hidden; border:1px solid rgba(0,242,255,0.1);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-mtbf-bar"),"dark");myChart.setOption({json.dumps(echarts_bar)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 4. DETALLE DE CÁLCULO TMEF (Tabla) ---
    st.markdown("<h5 style='color:#00f2ff; font-family:Arial, sans-serif !important; margin-bottom:10px;'>ANÁLISIS DE EVENTOS & LONGEVIDAD</h5>", unsafe_allow_html=True)
    if step_df is not None:
        render_hud_table(step_df.head(50))
    else:
        st.info("No hay detalles de cálculo disponibles.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
