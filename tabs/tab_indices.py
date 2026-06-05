"""
tabs/tab_indices.py
===================
Visualización profesional de Índices de Falla y Operatividad.
Utiliza estética HUD y Zero Space Waste.
"""

import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
from indice_falla import calcular_indice_falla_anual
from styles import render_hud_table

def render_tab_indices(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, selected_activo):
    """Renderiza el contenido completo del Tab INDICES & DATA con estilo HUD."""
    
    if df_bd_filtered.empty or df_forma9_filtered.empty:
        st.warning("Datos insuficientes para calcular índices.")
        return

    try:
        indice_resumen_df, df_mensual_hist = calcular_indice_falla_anual(
            df_bd_filtered,
            df_forma9_filtered,
            fecha_evaluacion
        )
        
        # --- 1. KPI GRID (Resumen de Índices) ---
        
        # Extraer valores para las tarjetas
        def get_val(ind_name):
            try: return indice_resumen_df[indice_resumen_df['Indicador'] == ind_name]['Valor'].values[0]
            except: return "0%"

        # --- 1. KPI GRID (Resumen de Índices en fila única) ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">📊</div><div class="kpi-label">I.F. TOTAL</div><div class="kpi-value" style="color:#137659;">{get_val("Índice de Falla Total")}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚙️</div><div class="kpi-label">I.F. ALS</div><div class="kpi-value" style="color:#c09c2e;">{get_val("Índice de Falla ALS")}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🔋</div><div class="kpi-label">I.F. ON</div><div class="kpi-value" style="color:#095139;">{get_val("Índice de Falla ON")}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚡</div><div class="kpi-label">I.F. ALS ON</div><div class="kpi-value" style="color:#137659;">{get_val("Índice de Falla ALS ON")}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


        # --- 2. GRÁFICOS DE TENDENCIA ---
        months_idx = [str(m) for m in df_mensual_hist['Mes']]
        val_if_on = [round(float(x)*100, 2) for x in df_mensual_hist['Indice_Falla_Rolling_ON'].tolist()]
        val_if_als = [round(float(x)*100, 2) for x in df_mensual_hist['Indice_Falla_Rolling_ALS_ON'].tolist()]
        
        # Nuevas métricas RLE < 1500
        val_if_on_1500 = [round(float(x)*100, 2) for x in df_mensual_hist.get('Indice_Falla_Rolling_ON_1500', pd.Series([0]*len(df_mensual_hist))).tolist()]
        val_if_als_1500 = [round(float(x)*100, 2) for x in df_mensual_hist.get('Indice_Falla_Rolling_ALS_ON_1500', pd.Series([0]*len(df_mensual_hist))).tolist()]
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
            echarts_line = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "EVOLUCIÓN DE ÍNDICES",
                    "left": "center",
                    "top": 0,
                    "textStyle": {
                        "color": "#137659",
                        "fontSize": 13,
                        "fontFamily": "Arial, sans-serif",
                        "fontWeight": "bold"
                    }
                },
                "textStyle": {"fontFamily": "Arial, sans-serif"},
                "tooltip": {
                    "trigger": "axis", 
                    "backgroundColor": "rgba(255, 255, 255, 0.95)",
                    "borderColor": "#137659",
                    "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"},
                    "axisPointer": {"type": "cross"}
                },
                "legend": {"data": ["Ind. Falla ON", "Ind. Falla ALS ON", "Ind. Falla < 1500", "Ind. Falla ALS < 1500"], "bottom": 0, "textStyle": {"color": "#475569", "fontSize": 9, "fontFamily": "Arial, sans-serif"}},
                "grid": {"left": "3%", "right": "4%", "bottom": "18%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [{"type": "value", "axisLabel": {"formatter": "{value}%", "color": "#475569", "fontFamily": "Arial, sans-serif"}, "splitLine": {"lineStyle": {"color": "rgba(19, 118, 89, 0.05)"}}}],
                "series": [
                    {"name": "Ind. Falla ON", "type": "line", "smooth": True, "data": val_if_on, "itemStyle": {"color": "#137659"}, "lineStyle": {"width": 3}, "areaStyle": {"color": "rgba(19,118,89,0.05)"}},
                    {"name": "Ind. Falla ALS ON", "type": "line", "smooth": True, "data": val_if_als, "itemStyle": {"color": "#c09c2e"}, "lineStyle": {"width": 3}},
                    {"name": "Ind. Falla < 1500", "type": "line", "smooth": True, "data": val_if_on_1500, "itemStyle": {"color": "#5b5c55"}, "lineStyle": {"width": 2, "type": "dashed"}},
                    {"name": "Ind. Falla ALS < 1500", "type": "line", "smooth": True, "data": val_if_als_1500, "itemStyle": {"color": "#095139"}, "lineStyle": {"width": 2, "type": "dashed"}}
                ]
            }
            components.html(f'<div id="echarts-if-line" style="width:100%; height:380px; background:#ffffff; border-radius:15px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-if-line"),null);myChart.setOption({json.dumps(echarts_line)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

        with col_right:
            st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
            p_ops = df_mensual_hist['Pozos Operativos'].tolist()
            f_tots = df_mensual_hist['Fallas Totales'].tolist()
            echarts_op = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "📊 TENDENCIA DE OPERATIVIDAD VS EVENTOS",
                    "left": "center",
                    "top": 0,
                    "textStyle": {
                        "color": "#137659",
                        "fontSize": 13,
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
                "legend": {"data": ["Pozos Operativos", "Eventos Totales"], "bottom": 0, "textStyle": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}, "icon": "circle"},
                "grid": {"left": "3%", "right": "8%", "bottom": "18%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [
                    {"type": "value", "name": "POZOS", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}, "splitLine": {"lineStyle": {"color": "rgba(19, 118, 89, 0.05)"}}},
                    {"type": "value", "name": "EVENTOS", "position": "right", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}, "splitLine": {"show": False}}
                ],
                "series": [
                    {
                        "name": "Pozos Operativos", 
                        "type": "line", 
                        "smooth": True, 
                        "data": p_ops, 
                        "itemStyle": {"color": "#137659"}, 
                        "lineStyle": {"width": 3},
                        "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1, "colorStops": [{"offset": 0, "color": "rgba(19, 118, 89, 0.15)"}, {"offset": 1, "color": "transparent"}]}}
                    },
                    {
                        "name": "Eventos Totales", 
                        "type": "bar", 
                        "yAxisIndex": 1, 
                        "data": f_tots, 
                        "itemStyle": {"color": "rgba(192, 156, 46, 0.8)", "borderRadius": [4, 4, 0, 0]}
                    }
                ]
            }
            components.html(f'<div id="echarts-op-fallas" style="width:100%; height:380px; background:#ffffff; border-radius:15px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-op-fallas"),null);myChart.setOption({json.dumps(echarts_op)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 3. DETALLE DE DATA (Expander con HUD Table Interactivas) ---
        with st.expander("📄 VER TABLA DE DATOS HISTÓRICOS Y RESUMEN", expanded=False):
            st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>RESUMEN DE ÍNDICES</div>", unsafe_allow_html=True)
            render_hud_table(indice_resumen_df, table_id="resumen_indices")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>DETALLE MENSUAL</div>", unsafe_allow_html=True)
            
            # Construir la tabla con las columnas y orden exactos solicitados
            df_detalle = pd.DataFrame()
            df_detalle['Mes'] = df_mensual_hist['Mes']
            df_detalle['IF Total'] = df_mensual_hist['Indice_Falla_Rolling_ON'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS'] = df_mensual_hist['Indice_Falla_Rolling_ALS_ON'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF < 1500'] = df_mensual_hist.get('Indice_Falla_Rolling_ON_1500', pd.Series([0]*len(df_mensual_hist))).apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS < 1500'] = df_mensual_hist.get('Indice_Falla_Rolling_ALS_ON_1500', pd.Series([0]*len(df_mensual_hist))).apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['Pozos On'] = df_mensual_hist['Pozos ON'].fillna(0).astype(int)
            df_detalle['Pozos Fallados'] = df_mensual_hist['Fallas Totales'].fillna(0).astype(int)
            df_detalle['Fallas < 1500'] = df_mensual_hist.get('Fallas_1500', pd.Series([0]*len(df_mensual_hist))).fillna(0).astype(int)
            df_detalle['Fallas ALS < 1500'] = df_mensual_hist.get('Fallas_ALS_1500', pd.Series([0]*len(df_mensual_hist))).fillna(0).astype(int)
            df_detalle['Fallas ALS'] = df_mensual_hist['Fallas ALS'].fillna(0).astype(int)
            df_detalle['Pozos Off'] = (df_mensual_hist['Pozos Operativos'] - df_mensual_hist['Pozos ON']).clip(lower=0).fillna(0).astype(int)
            
            # Ordenar por Mes descendente para ver lo más reciente al inicio
            df_detalle = df_detalle.sort_values(by='Mes', ascending=False).reset_index(drop=True)
            
            render_hud_table(df_detalle, table_id="detalle_mensual")
            
    except Exception as e:
        st.error(f"Error en Tab Índices: {e}")
