"""
tabs/tab_fallas.py
==================
Renderiza el contenido del Tab "🚨 FALLAS":
 - Filtro de rango de fechas para fallas
 - Distribución de fallas por tiempo y tipo (ECharts)
 - Pie chart de tipos de falla IA
 - Top pozos con más fallas
 - Listado detallado de pozos fallados
 - Sección de Pozos Problema (Multi-Fallas)
"""

import json
from datetime import timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import COLOR_PRINCIPAL
from calculations import clasificar_razon_ia, highlight_problema
import tema

def clasificar_runlife(rl):
    """Categoriza el Run Life en etapas: Infantil, Prematura, En Garantía, Sin Garantía."""
    try:
        rl = float(rl)
    except (ValueError, TypeError):
        return 'Sin Dato'
    if rl <= 30:
        return 'Infantil'
    elif 30 < rl <= 60:
        return 'Prematura'
    elif rl <= 1100:
        return 'En Garantía'
    elif rl > 1100:
        return 'Sin Garantía'
    return 'Sin Dato'

def render_tab_fallas(df_bd_filtered, fecha_evaluacion):
    """Renderiza el contenido completo del Tab FALLAS."""
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(245, 39, 56, 0.1), transparent); padding: 10px; border-left: 5px solid #F52738; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
        <h3 id="fallas-mensuales" style='font-size:1.3rem; font-weight:800; margin:0; color:#F52738; letter-spacing: -0.5px;'>
             ANÁLISIS DE FALLAS MENSUALES
        </h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get('reporte_fallas') is None or st.session_state['reporte_fallas'].empty:
        st.info("No hay datos de fallas disponibles.")
        return

    reporte_fallas = st.session_state['reporte_fallas']
    min_date_falla_data = reporte_fallas['MES'].min().date()
    max_date_falla = reporte_fallas['MES'].max().date()
    
    try:
        default_start = max_date_falla.replace(year=max_date_falla.year - 1)
    except ValueError:
        default_start = max_date_falla - timedelta(days=365)
        
    res_date = st.date_input(
        "Filtra por rango de fecha para las fallas:",
        [max(min_date_falla_data, default_start), max_date_falla],
        key='date_filter_falla'
    )
    
    if isinstance(res_date, list) and len(res_date) == 2:
        start_date_falla, end_date_falla = res_date
    else:
        start_date_falla, end_date_falla = min_date_falla_data, max_date_falla

    filtered_fallas = reporte_fallas[
        (reporte_fallas['MES'].dt.date >= start_date_falla) & 
        (reporte_fallas['MES'].dt.date <= end_date_falla)
    ]

    detalles_fallas = []
    if df_bd_filtered is not None:
        for _, row in filtered_fallas.iterrows():
            mes = row['MES']
            mask = (df_bd_filtered['FECHA_FALLA'].dt.to_period('M') == mes.to_period('M'))
            runs_mes = df_bd_filtered[mask]
            for _, run in runs_mes.iterrows():
                razon = run.get('RAZON ESPECIFICA PULL', '')
                clasificacion = clasificar_razon_ia(razon) if razon else 'Desconocida'
                detalles_fallas.append({
                    'Mes': mes,
                    'Pozo': run.get('POZO', ''),
                    'Fecha Falla': run.get('FECHA_FALLA', ''),
                    'Tiempo Vida a Falla': run.get('RUN LIFE', ''),
                    'Razón de Pull': razon,
                    'Clasificación IA': clasificacion
                })
    
    df_detalles_fallas = pd.DataFrame(detalles_fallas)

    col1, col2 = st.columns(2)
    with col1:
        if not df_detalles_fallas.empty:
            st.dataframe(df_detalles_fallas, use_container_width=True)
            st.info(f"Fallas Totales en Rango: {len(df_detalles_fallas)}")
        else:
            st.info("Sin detalles de fallas para el rango seleccionado.")

    with col2:
        if not df_detalles_fallas.empty:
            df_graf = df_detalles_fallas.copy()
            df_graf['Clasif. Tiempo Vida'] = df_graf['Tiempo Vida a Falla'].apply(clasificar_runlife)
            conteo = df_graf.groupby(['Clasif. Tiempo Vida', 'Clasificación IA']).size().reset_index(name='Cantidad')
            
            tipos_ia = sorted(conteo['Clasificación IA'].unique().tolist())
            orden_runlife = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía']
            colores_runlife = {
                'Infantil': tema.COLOR_RL_INFANTIL,
                'Prematura': tema.COLOR_RL_PREMATURA,
                'En Garantía': tema.COLOR_RL_EN_GARANTIA,
                'Sin Garantía': tema.COLOR_RL_SIN_GARANTIA
            }
            
            series_fallas = []
            for rl in orden_runlife:
                data_rl = [int(conteo[(conteo['Clasif. Tiempo Vida'] == rl) & (conteo['Clasificación IA'] == t)]['Cantidad'].values[0]) if len(conteo[(conteo['Clasif. Tiempo Vida'] == rl) & (conteo['Clasificación IA'] == t)]) > 0 else 0 for t in tipos_ia]
                series_fallas.append({"name": rl, "type": "bar", "stack": "Total", "data": data_rl, "itemStyle": {"color": colores_runlife.get(rl)}})

            echarts_dist = {
                "backgroundColor": "transparent",
                "title": {"text": "DISTRIBUCIÓN DE FALLAS POR TIEMPO Y TIPO", "left": "center", "textStyle": {"color": "#fff", "fontSize": 14, "fontWeight": "900"}},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {"data": orden_runlife, "bottom": 0, "textStyle": {"color": "#ccc"}},
                "xAxis": [{"type": "category", "data": tipos_ia, "axisLabel": {"color": "#888", "rotate": 30}}],
                "yAxis": [{"type": "value"}],
                "series": series_fallas
            }
            components.html(f'<div id="echarts-fallas-dist" style="width:100%; height:400px;"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-fallas-dist"),"dark");myChart.setOption({json.dumps(echarts_dist)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=420)

    col3, col4 = st.columns(2)
    with col3:
        if not df_detalles_fallas.empty:
            tipo_falla_counts = df_detalles_fallas['Clasificación IA'].value_counts().reset_index()
            tipo_falla_counts.columns = ['Tipo de Falla IA', 'Cantidad']
            pie_data = [{"name": r['Tipo de Falla IA'], "value": int(r['Cantidad'])} for _, r in tipo_falla_counts.iterrows()]
            
            FALLA_COLORS = ['#ff0055', '#00f2ff', '#00ff9d', '#ffbd00', '#C82B96', '#8b5cf6', '#0066ff', '#33ffcc']
            echarts_pie = {
                "backgroundColor": "transparent",
                "title": {"text": "DISTRIBUCIÓN POR TIPO DE FALLA (IA)", "left": "center", "top": 10, "textStyle": {"color": "#fff", "fontSize": 16, "fontWeight": "900"}},
                "color": FALLA_COLORS,
                "tooltip": {"trigger": "item", "formatter": "{b}<br/><b>{c} Eventos</b> ({d}%)"},
                "series": [{"type": "pie", "radius": ["20%", "75%"], "roseType": "radius", "data": pie_data}]
            }
            components.html(f'<div id="echarts-fallas-pie" style="width:100%; height:420px;"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-fallas-pie"),"dark");myChart.setOption({json.dumps(echarts_pie)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=440)

    with col4:
        if not df_detalles_fallas.empty:
            st.markdown("##### 🔥 Top Pozos con Más Fallas")
            top_pozos = df_detalles_fallas['Pozo'].value_counts().reset_index()
            top_pozos.columns = ['Pozo', 'N° Fallas']
            st.dataframe(top_pozos.head(10), hide_index=True, use_container_width=True)

    # ── Listado detallado y Pozos Problema ───────────────────────────────
    st.markdown("---")
    st.markdown("""<div style="background: linear-gradient(90deg, rgba(161, 3, 157, 0.1), transparent); padding: 10px; border-left: 5px solid #A1039D; border-radius: 5px; margin-top: 2em; margin-bottom: 1em;"><h3 style='font-size:1.3rem; font-weight:800; margin:0; color:#A1039D;'>LISTADO DETALLADO DE POZOS FALLADOS</h3></div>""", unsafe_allow_html=True)

    pozos_fallados_df = pd.DataFrame()
    if df_bd_filtered is not None and not df_bd_filtered.empty:
        limit_date = pd.to_datetime(fecha_evaluacion) - timedelta(days=365)
        pozos_fallados_df = df_bd_filtered[(df_bd_filtered['FECHA_FALLA'].dt.date >= limit_date.date()) & (df_bd_filtered['FECHA_FALLA'].dt.date <= pd.to_datetime(fecha_evaluacion).date())]

    if not pozos_fallados_df.empty:
        fallas_por_pozo = pozos_fallados_df.groupby('POZO')['RUN'].count().reset_index().rename(columns={'RUN': 'Cantidad de Fallas'}).sort_values(by='Cantidad de Fallas', ascending=False)
        col_listado, col_severidad = st.columns([0.5, 0.5])
        with col_listado:
            st.dataframe(fallas_por_pozo.style.apply(highlight_problema, axis=1), hide_index=True, use_container_width=True)
        with col_severidad:
            idx_sev = (fallas_por_pozo['Cantidad de Fallas'].sum() / fallas_por_pozo.shape[0]) if fallas_por_pozo.shape[0] > 0 else 0
            st.markdown(f'<div style="padding:20px; background:linear-gradient(135deg,#FF4B2B,#FF416C); border-radius:15px; text-align:center; color:white;"><div style="font-size:14px; opacity:0.9;">ÍNDICE DE SEVERIDAD</div><div style="font-size:32px; font-weight:800; margin-top:5px;">{idx_sev:.2f}</div></div>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown('<div class="fancy-subtitle"><span>⚠️ Pozos Problema (Multi-Fallas)</span></div>', unsafe_allow_html=True)
            pozos_prob = fallas_por_pozo[fallas_por_pozo['Cantidad de Fallas'] > 1]
            if not pozos_prob.empty:
                for _, row in pozos_prob.iterrows():
                    with st.expander(f"⚠️ {row['POZO']} ({row['Cantidad de Fallas']} fallas)"):
                        mask = (df_bd_filtered['POZO'] == row['POZO']) & (df_bd_filtered['FECHA_FALLA'] >= limit_date) & (df_bd_filtered['FECHA_FALLA'] <= pd.to_datetime(fecha_evaluacion))
                        razones = df_bd_filtered[mask]['RAZON ESPECIFICA PULL'].dropna().tolist()
                        for i, r in enumerate(razones, 1):
                            st.markdown(f"**Falla {i}:** {r}<br><span style='font-size:0.75em; opacity:0.6;'>Clasificación:</span> {clasificar_razon_ia(r)}", unsafe_allow_html=True)
            else:
                st.info("No hay pozos con más de una falla en el último año.")
    else:
        st.info("No hay pozos fallados en el último año.")
