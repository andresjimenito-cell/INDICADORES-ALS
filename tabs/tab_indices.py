"""
tabs/tab_indices.py
===================
Renderiza el contenido del Tab "📈 ÍNDICES & DATA":
 - Resumen de Índices de Falla (Rolling 12 Meses)
 - Gráficos Históricos (Línea y Barras)
 - Tabla de Operatividad vs Fallas
 - Gráfico ECharts de Operatividad
 - Dataframe final de trabajo
"""

import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import COLOR_PRINCIPAL
from indice_falla import calcular_indice_falla_anual

def render_tab_indices(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, selected_activo):
    """Renderiza el contenido completo del Tab INDICES & DATA."""
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(94, 255, 0, 0.1), transparent); padding: 10px; border-left: 5px solid #5EFF00; border-radius: 5px; margin-top: 2em; margin-bottom: 1em;">
        <h3 id="indices-de-falla" style='font-size:1.6rem; font-weight:800; margin:0; color:#5EFF00; letter-spacing: -0.5px;'>
             ÍNDICES DE FALLA
        </h3>
    </div>
    """, unsafe_allow_html=True)

    if not df_bd_filtered.empty and not df_forma9_filtered.empty:
        try:
            indice_resumen_df, df_mensual_hist = calcular_indice_falla_anual(
                df_bd_filtered,
                df_forma9_filtered,
                fecha_evaluacion
            )
            
            st.markdown(f"""
            <div class="fancy-subtitle">
                <span>📊 Resumen de Índices para {selected_activo} (Rolling 12 Meses)</span>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(indice_resumen_df, hide_index=True, use_container_width=True)

            df_plot_indices = df_mensual_hist.copy()
            months_idx = [str(m) for m in df_plot_indices['Mes']]
            val_if_on = [round(float(x)*100, 2) for x in df_plot_indices['Indice_Falla_Rolling_ON'].tolist()]
            val_if_als = [round(float(x)*100, 2) for x in df_plot_indices['Indice_Falla_Rolling_ALS_ON'].tolist()]
            
            col_hist_line, col_bar_mes = st.columns([0.5, 0.5])
            
            with col_hist_line:
                echarts_line = {
                    "backgroundColor": "transparent",
                    "title": {"text": "HISTÓRICO ÍNDICE DE FALLA (ROLLING 12M)", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 12}},
                    "tooltip": {"trigger": "axis", "formatter": "{b}<br/>{a0}: {c0}%<br/>{a1}: {c1}%"},
                    "legend": {"data": ["Ind. Falla ON", "Ind. Falla ALS ON"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 9}},
                    "xAxis": [{"type": "category", "data": months_idx}],
                    "yAxis": [{"type": "value", "axisLabel": {"formatter": "{value}%"}}],
                    "series": [
                        {"name": "Ind. Falla ON", "type": "line", "smooth": True, "data": val_if_on, "itemStyle": {"color": COLOR_PRINCIPAL}},
                        {"name": "Ind. Falla ALS ON", "type": "line", "smooth": True, "data": val_if_als, "itemStyle": {"color": "#00f2ff"}}
                    ]
                }
                components.html(f'<div id="echarts-if-line" style="width:100%; height:250px;"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-if-line"),"dark");myChart.setOption({json.dumps(echarts_line)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=270)

            with col_bar_mes:
                echarts_bar = {
                    "backgroundColor": "transparent",
                    "title": {"text": "ÍNDICE DE FALLA MENSUAL", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 12}},
                    "tooltip": {"trigger": "axis", "formatter": "{b}<br/>{a0}: {c0}%<br/>{a1}: {c1}%"},
                    "legend": {"data": ["Ind. Falla ON", "Ind. Falla ALS ON"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 9}},
                    "xAxis": [{"type": "category", "data": months_idx}],
                    "yAxis": [{"type": "value", "axisLabel": {"formatter": "{value}%"}}],
                    "series": [
                        {"name": "Ind. Falla ON", "type": "bar", "data": val_if_on, "itemStyle": {"color": COLOR_PRINCIPAL, "borderRadius": [4, 4, 0, 0]}},
                        {"name": "Ind. Falla ALS ON", "type": "bar", "data": val_if_als, "itemStyle": {"color": "#00f2ff", "borderRadius": [4, 4, 0, 0]}}
                    ]
                }
                components.html(f'<div id="echarts-if-bar" style="width:100%; height:250px;"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-if-bar"),"dark");myChart.setOption({json.dumps(echarts_bar)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=270)

            col_table_op, col_chart_op = st.columns([0.5, 0.5])
            with col_table_op:
                df_disp = df_mensual_hist[['Mes', 'Fallas Totales', 'Fallas ALS', 'Pozos Operativos', 'Pozos ON']].copy()
                st.dataframe(df_disp, use_container_width=True)

            with col_chart_op:
                months_op = [str(m) for m in df_mensual_hist['Mes']]
                p_ops = df_mensual_hist['Pozos Operativos'].tolist()
                p_on = df_mensual_hist['Pozos ON'].tolist()
                f_tots = df_mensual_hist['Fallas Totales'].tolist()
                f_als = df_mensual_hist['Fallas ALS'].tolist()

                echarts_op = {
                    "backgroundColor": "transparent",
                    "title": {"text": "OPERATIVIDAD VS FALLAS MENSUALES", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 14, "fontWeight": "900"}},
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": ["Pozos Operativos", "Pozos ON", "Fallas Totales", "Fallas ALS"], "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 9}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                    "xAxis": [{"type": "category", "data": months_op}],
                    "yAxis": [{"type": "value", "name": "POZOS"}, {"type": "value", "name": "FALLAS", "position": "right", "splitLine": {"show": False}}],
                    "series": [
                        {"name": "Pozos Operativos", "type": "line", "smooth": True, "data": p_ops, "itemStyle": {"color": "#135bec"}},
                        {"name": "Pozos ON", "type": "line", "smooth": True, "data": p_on, "itemStyle": {"color": "#00f2ff"}},
                        {"name": "Fallas Totales", "type": "bar", "yAxisIndex": 1, "data": f_tots, "itemStyle": {"color": "rgba(255, 140, 0, 0.4)"}},
                        {"name": "Fallas ALS", "type": "bar", "yAxisIndex": 1, "data": f_als, "itemStyle": {"color": "rgba(138, 43, 226, 0.6)"}}
                    ]
                }
                components.html(f'<div id="echarts-op-fallas" style="width:100%; height:350px;"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-op-fallas"),"dark");myChart.setOption({json.dumps(echarts_op)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=370)

        except Exception as e:
            st.error(f"Error en índices de falla: {e}")

    st.markdown("##### 📁 DATA FINAL DE TRABAJO")
    st.dataframe(df_bd_filtered, use_container_width=True)
