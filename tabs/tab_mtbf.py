"""
tabs/tab_mtbf.py
================
Renderiza el contenido del Tab "🕒 TMEF (MTBF)":
 - Análisis MTBF Global y por Pozo (via mtbf.py)
 - Verificaciones de Consistencia
 - Histórico de Tiempo de Vida por Campo
 - Gráficos ECharts Histórico
"""

import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import COLOR_PRINCIPAL, get_color_sequence
from mtbf import calcular_mtbf, mostrar_mtbf
from calculations import calcular_run_life_efectivo, generar_historico_run_life
import tema

def render_tab_mtbf(
    df_bd_filtered,
    df_forma9_filtered,
    fecha_evaluacion,
    verificaciones_filtered,
    selected_activo,
):
    """Renderiza el contenido completo del Tab MTBF."""
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(19, 91, 236, 0.1), transparent); padding: 10px; border-left: 5px solid #135bec; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
        <h3 id="analisis-mtbf" style='font-size:1.6rem; font-weight:800; margin:0; color:#135bec; letter-spacing: -0.5px;'>
             ANÁLISIS DE TMEF (MTBF)
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # ── Análisis MTBF ─────────────────────────────────────────────────────
    try:
        mtbf_global, mtbf_por_pozo = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        
        mtbf_efectivo_global = None
        if 'RUN_LIFE_EFECTIVO' in df_bd_filtered.columns:
            try:
                mtbf_efectivo_global, _ = calcular_mtbf(df_bd_filtered, fecha_evaluacion, col_life='RUN_LIFE_EFECTIVO')
            except Exception:
                mtbf_efectivo_global = None
        
        mostrar_mtbf(
            mtbf_global, 
            mtbf_por_pozo, 
            mtbf_efectivo=mtbf_efectivo_global, 
            df_bd=df_bd_filtered, 
            fecha_evaluacion=fecha_evaluacion
        )
    except Exception as e:
        st.warning(f"No se pudo calcular el MTBF: {e}")

    # ── Verificaciones ───────────────────────────────────────────────────
    with st.expander("Verificaciones de Consistencia", expanded=False):
        for relacion, es_valida in verificaciones_filtered.items():
            status = "✅ Válida" if es_valida else "❌ No válida"
            st.markdown(f"<span style='font-size:11px;'>{relacion}: {status}</span>", unsafe_allow_html=True)
    
    # ── Histórico Run Life ──────────────────────────────────────────────
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(255, 222, 49, 0.1), transparent); padding: 10px; border-left: 5px solid #FFDE31; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
        <h3 id="historico-de-run-life-por-campo" style='font-size:1.3rem; font-weight:800; margin:0; color:#FFDE31; letter-spacing: -0.5px;'>
             HISTÓRICO TIEMPO DE VIDA POR CAMPO
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Calcular métricas rápidas
    df_runlife_total = df_bd_filtered.copy()
    if selected_activo != 'TODOS' and 'ACTIVO' in df_runlife_total.columns:
        df_runlife_total = df_runlife_total[df_runlife_total['ACTIVO'] == selected_activo]
    
    runlife_total = df_runlife_total[
        ((df_runlife_total['FECHA_PULL'].notna()) | (df_runlife_total['FECHA_FALLA'].notna())) &
        (df_runlife_total['FECHA_RUN'].dt.date <= fecha_evaluacion)
    ]['RUN LIFE'].mean()
    runlife_total_val = float(runlife_total) if not pd.isna(runlife_total) else 0.0
    
    try:
        run_life_efectivo_val, _ = calcular_run_life_efectivo(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
    except Exception:
        run_life_efectivo_val = 0.0

    st.markdown(f"""
    <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 20px;">
        <div style="flex: 1; padding: 20px; background: linear-gradient(135deg, {tema.COLOR_GRADIENTE_MAGENTA_1}, {tema.COLOR_GRADIENTE_MAGENTA_2}); border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); text-align: center; color: white;">
            <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">TIEMPO VIDA TOTAL ({selected_activo})</div>
            <div style="font-size: 36px; font-weight: 800; margin-top: 10px;">{runlife_total_val:.2f} <span style="font-size: 16px; font-weight: 400;">días</span></div>
        </div>
        <div style="flex: 1; padding: 20px; background: linear-gradient(135deg, {tema.COLOR_GRADIENTE_AZUL_1}, {tema.COLOR_GRADIENTE_AZUL_2}); border-radius: 15px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2); text-align: center; color: #E0E0E0;">
            <div style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">RUN LIFE EFECTIVO ({selected_activo})</div>
            <div style="font-size: 36px; font-weight: 800; margin-top: 10px;">{run_life_efectivo_val:.2f} <span style="font-size: 16px; font-weight: 400;">días</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    historico_run_life = generar_historico_run_life(df_bd_filtered, fecha_evaluacion)

    col_table_runlife, col_chart_runlife = st.columns([0.5, 0.5])
    
    with col_table_runlife:
        if historico_run_life is not None:
            st.dataframe(historico_run_life, hide_index=True, use_container_width=True)

    with col_chart_runlife:
        if historico_run_life is not None and not historico_run_life.empty:
            if 'ACTIVO' in historico_run_life.columns:
                historico_run_life['Mes_Str'] = pd.to_datetime(historico_run_life['Mes'], errors='coerce').dt.strftime('%Y-%m-%d')
                months = sorted(historico_run_life['Mes_Str'].unique().tolist())
                activos = sorted(historico_run_life['ACTIVO'].unique().tolist())
                color_seq = get_color_sequence()
                
                series = []
                for act in activos:
                    df_act = historico_run_life[historico_run_life['ACTIVO'] == act]
                    data_act = [float(df_act[df_act['Mes_Str'] == m]['Tiempo Op. Promedio'].values[0]) if len(df_act[df_act['Mes_Str'] == m]) > 0 else 0 for m in months]
                    series.append({
                        "name": act, "type": "bar", "data": data_act,
                        "itemStyle": {"borderRadius": [4, 4, 0, 0]}
                    })

                echarts_options = {
                    "backgroundColor": "transparent",
                    "title": {"text": "TIEMPO DE VIDA PROMEDIO MENSUAL POR ACTIVO", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 14, "fontWeight": "900"}},
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {"data": activos, "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 10}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
                    "xAxis": [{"type": "category", "data": months, "axisLabel": {"color": "#888", "fontSize": 10}}],
                    "yAxis": [{"type": "value", "name": "Días", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                    "color": color_seq,
                    "series": series
                }
            else:
                months = [str(m) for m in historico_run_life['Mes']]
                data = [float(x) for x in historico_run_life['Tiempo Op. Promedio'].tolist()]
                echarts_options = {
                    "backgroundColor": "transparent",
                    "title": {"text": "TIEMPO DE VIDA PROMEDIO MENSUAL", "left": "center", "textStyle": {"color": COLOR_PRINCIPAL, "fontSize": 14, "fontWeight": "900"}},
                    "tooltip": {"trigger": "axis"},
                    "xAxis": [{"type": "category", "data": months}],
                    "yAxis": [{"type": "value"}],
                    "series": [{"type": "bar", "data": data, "itemStyle": {"color": COLOR_PRINCIPAL, "borderRadius": [8, 8, 0, 0]}}]
                }
            
            html_chart = f"""
            <div id="echarts-mtbf-hist" style="width:100%; height:320px;"></div>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
            <script>
                (function() {{
                    var myChart = echarts.init(document.getElementById('echarts-mtbf-hist'), 'dark');
                    myChart.setOption({json.dumps(echarts_options)});
                    window.addEventListener('resize', function() {{ myChart.resize(); }});
                }})();
            </script>
            """
            components.html(html_chart, height=340)
