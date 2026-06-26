"""
tabs/tab_fallas.py
==================
Análisis de Fallas con Estética HUD.
Visualización de severidad, distribución temporal y clasificación IA.
Typology aligned with 'Indices & Fallas' (Spectacular UI).
"""

import json
from datetime import timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
from calculations import clasificar_razon_ia, highlight_problema
from styles import render_hud_table

def clasificar_runlife(rl):
    """Categoriza el Run Life en etapas HUD."""
    try: rl = float(rl)
    except: return 'N/A'
    if rl <= 30: return 'Infantil'
    if rl <= 90: return 'Prematura'
    if rl <= 1100: return 'En Garantía'
    return 'Sin Garantía'

def render_tab_fallas(df_bd_filtered, fecha_evaluacion):
    """Renderiza el Tab FALLAS con alta densidad HUD Profesional."""
    
    if st.session_state.get('reporte_fallas') is None or st.session_state['reporte_fallas'].empty:
        st.info("Sin datos de fallas.")
        return

    reporte_fallas = st.session_state['reporte_fallas']
    fecha_eval = pd.to_datetime(fecha_evaluacion)
    
    # 1. KPI GRID SUPERIOR (4 COLUMNS)
    total_fallas_rango = len(reporte_fallas)
    fallas_als = df_bd_filtered[df_bd_filtered['INDICADOR_MTBF'] == 1].shape[0] if df_bd_filtered is not None else 0
    
    fecha_ini_str = st.session_state.get('fecha_inicio_state')
    if fecha_ini_str is not None:
        fecha_ini_dt = pd.to_datetime(fecha_ini_str).normalize()
    else:
        fecha_ini_dt = fecha_eval - pd.DateOffset(years=1)

    if df_bd_filtered is not None and not df_bd_filtered.empty:
        fallas_als_periodo = int(df_bd_filtered[
            (df_bd_filtered['FECHA_FALLA'].notna()) &
            (df_bd_filtered['FECHA_FALLA'] >= fecha_ini_dt) &
            (df_bd_filtered['FECHA_FALLA'] <= fecha_eval) &
            (df_bd_filtered['INDICADOR_MTBF'] == 1)
        ].shape[0])
    else:
        fallas_als_periodo = 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🚨</div><div class="kpi-label">TOTAL EVENTOS</div><div class="kpi-value" style="color:#137659;">{total_fallas_rango}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚙️</div><div class="kpi-label">FALLAS ALS</div><div class="kpi-value" style="color:#095139;">{fallas_als}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🔥</div><div class="kpi-label">FALLAS ALS PERI</div><div class="kpi-value" style="color:#c09c2e;">{fallas_als_periodo}</div></div>', unsafe_allow_html=True)
        
    if df_bd_filtered is not None and not df_bd_filtered.empty:
        fallas_periodo = int(df_bd_filtered[
            (df_bd_filtered['FECHA_FALLA'].notna()) &
            (df_bd_filtered['FECHA_FALLA'] >= fecha_ini_dt) &
            (df_bd_filtered['FECHA_FALLA'] <= fecha_eval)
        ].shape[0])
    else:
        fallas_periodo = 0

    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⏳</div><div class="kpi-label">FALLAS PERIODO</div><div class="kpi-value" style="color:#137659;">{fallas_periodo}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. ANÁLISIS DE DISTRIBUCIÓN (SIDE BY SIDE)
    col_left, col_right = st.columns(2)
    
    detalles = []
    if df_bd_filtered is not None:
        mask = (df_bd_filtered['FECHA_FALLA'] >= (fecha_eval - timedelta(days=365)))
        for _, run in df_bd_filtered[mask].iterrows():
            razon = run.get('RAZON ESPECIFICA PULL', '')
            clasif = clasificar_razon_ia(razon) if razon else 'Otros'
            if clasif == 'Desconocida':
                clasif = 'Otros'
            detalles.append({
                'Pozo': run['POZO'],
                'Vida': run['RUN LIFE'],
                'Clasif': clasif,
                'Etapa': clasificar_runlife(run['RUN LIFE'])
            })
    df_det = pd.DataFrame(detalles)

    with col_left:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        if not df_det.empty:
            conteo = df_det.groupby(['Etapa', 'Clasif']).size().reset_index(name='Cant')
            etapas = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía']
            tipos = sorted(df_det['Clasif'].unique().tolist())
            
            series = []
            colors = {'Infantil': '#d32f2f', 'Prematura': '#c09c2e', 'En Garantía': '#137659', 'Sin Garantía': '#5b5c55'}
            for et in etapas:
                data = [int(conteo[(conteo['Etapa'] == et) & (conteo['Clasif'] == t)]['Cant'].values[0]) if len(conteo[(conteo['Etapa'] == et) & (conteo['Clasif'] == t)]) > 0 else 0 for t in tipos]
                series.append({
                    "name": et, "type": "bar", "stack": "total", "data": data, 
                    "itemStyle": {"color": colors.get(et), "borderRadius": [2, 2, 0, 0]}
                })

            echarts_dist = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "DISTRIBUCIÓN POR ETAPA DE VIDA",
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
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(255, 255, 255, 0.95)",
                    "borderColor": "#137659",
                    "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}
                },
                "legend": {"bottom": 0, "textStyle": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}, "icon": "circle"},
                "grid": {"left": "3%", "right": "4%", "bottom": "20%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "category", "data": tipos, "axisLabel": {"color": "#475569", "rotate": 35, "fontSize": 9, "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [{"type": "value", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}, "splitLine": {"lineStyle": {"color": "rgba(19, 118, 89, 0.05)"}}}],
                "series": series
            }
            components.html(f'<div id="echarts-fallas-dist" style="width:100%; height:380px; background:#ffffff; border-radius:15px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-fallas-dist"),null);myChart.setOption({json.dumps(echarts_dist)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    with col_right:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        if not df_det.empty:
            pie_data = df_det['Clasif'].value_counts().reset_index()
            # Compatible columns resolution for different pandas versions
            col_name = 'count' if 'count' in pie_data.columns else (pie_data.columns[1] if len(pie_data.columns) > 1 else 'Clasif')
            col_label = 'Clasif' if 'Clasif' in pie_data.columns else pie_data.columns[0]
            pie_list = [{"name": str(r[col_label]), "value": int(r[col_name])} for _, r in pie_data.iterrows()]
            
            echarts_pie = {
                "backgroundColor": "transparent",
                "color": ["#137659", "#c09c2e", "#095139", "#5b5c55", "#a28834", "#d32f2f", "#d2b48c"],
                "title": {
                    "text": "CAUSA RAÍZ (ANÁLISIS IA)",
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
                    "trigger": "item",
                    "backgroundColor": "rgba(255, 255, 255, 0.95)",
                    "borderColor": "#137659",
                    "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}
                },
                "legend": {"orient": "vertical", "right": 10, "top": "center", "textStyle": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}},
                "series": [{
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["40%", "50%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {"borderRadius": 10, "borderColor": "#ffffff", "borderWidth": 2},
                    "label": {"show": False},
                    "emphasis": {"label": {"show": True, "fontSize": 14, "fontWeight": "bold", "color": "#1f221e", "fontFamily": "Arial, sans-serif"}},
                    "data": pie_list
                }]
            }
            components.html(f'<div id="echarts-fallas-pie" style="width:100%; height:380px; background:#ffffff; border-radius:15px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-fallas-pie"),null);myChart.setOption({json.dumps(echarts_pie)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3. DETALLE DE EVENTOS (Expander con HUD Table)
    with st.expander("📝 REGISTRO DETALLADO DE FALLAS & ANÁLISIS", expanded=False):
        if not reporte_fallas.empty:
            # Aquí no aplicamos el highlight_problema (Pandas Style) porque render_hud_table usa HTML puro.
            # Pero podemos pasar un DF ya formateado.
            render_hud_table(reporte_fallas.head(100))
        else:
            st.info("No hay detalles adicionales.")
