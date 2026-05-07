"""
tabs/tab_resumen.py
===================
Renderiza el contenido del Tab "📊 RESUMEN":
 - Tabla + chart ECharts de RUNES por categoría
 - Sección Estado de la Campaña (Pozos Nuevos vs Intervenciones)
"""

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from config import COLOR_PRINCIPAL, get_color_sequence
from calculations import generar_reporte_completo


def _calcular_metricas_grupo(df_grupo, nombre_grupo, color_borde, fecha_eval_ts, df_forma9_filtered):
    """Genera el HTML de una tarjeta de métricas para un grupo de pozos."""
    if df_grupo.empty:
        return f"""<div style="flex:1;background:rgba(255,255,255,0.02);border:1px solid {color_borde}44;
border-radius:12px;padding:20px;text-align:center;opacity:0.6;">
<div style="color:{color_borde};font-weight:bold;letter-spacing:1px;">{nombre_grupo.upper()}</div>
<div style="font-size:0.8rem;margin-top:5px;color:#888;">SIN REGISTROS ACTIVOS</div>
</div>"""

    total_pozos = df_grupo['POZO'].nunique()
    fallados = df_grupo[
        df_grupo['FECHA_FALLA'].notna() & (df_grupo['FECHA_FALLA'] <= fecha_eval_ts)
    ]['POZO'].nunique()
    operativos = df_grupo[
        ((df_grupo['FECHA_PULL'].isna()) | (df_grupo['FECHA_PULL'] > fecha_eval_ts)) &
        ((df_grupo['FECHA_FALLA'].isna()) | (df_grupo['FECHA_FALLA'] > fecha_eval_ts))
    ]['POZO'].nunique()

    pozos_grupo  = df_grupo['POZO'].unique()
    df_f9_grupo  = df_forma9_filtered[df_forma9_filtered['POZO'].isin(pozos_grupo)].copy()
    produccion_total = 0.0
    if not df_f9_grupo.empty:
        df_last_prod = df_f9_grupo.sort_values('FECHA_FORMA9').groupby('POZO').last()
        col_bopd = next((c for c in df_last_prod.columns if 'BOPD' in str(c).upper()), None)
        if col_bopd:
            produccion_total = pd.to_numeric(df_last_prod[col_bopd], errors='coerce').sum()

    pct_op = (operativos / total_pozos * 100) if total_pozos > 0 else 0

    return f"""
<div style="flex:1;background:linear-gradient(145deg,rgba(15,23,42,0.9),rgba(2,6,23,1));
border:1px solid {color_borde}44;border-radius:20px;padding:22px;position:relative;
overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.5);min-width:300px;">
<div style="position:absolute;top:0;right:0;width:80px;height:80px;
background:radial-gradient(circle at 100% 0%,{color_borde}33,transparent 70%);"></div>
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:18px;">
<div>
<div style="color:{color_borde};font-weight:900;font-size:1.1rem;letter-spacing:1px;font-family:'Outfit';">{nombre_grupo.upper()}</div>
<div style="font-size:0.7rem;color:#64748b;font-weight:bold;margin-top:2px;">OPERACIÓN TÁCTICA</div>
</div>
<div style="text-align:right;">
<div style="font-size:1.6rem;font-weight:900;color:#fff;line-height:1;">{total_pozos}</div>
<div style="font-size:0.6rem;color:{color_borde};font-weight:bold;letter-spacing:1px;">CORRIDAS</div>
</div>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;background:rgba(255,255,255,0.03);
padding:15px;border-radius:15px;border:1px solid rgba(255,255,255,0.05);">
<div style="text-align:center;">
<div style="font-size:0.6rem;color:#94a3b8;margin-bottom:4px;font-weight:bold;">ACTIVOS</div>
<div style="font-size:1.3rem;font-weight:900;color:#00ff9d;">{operativos}</div>
</div>
<div style="text-align:center;border-left:1px solid rgba(255,255,255,0.1);border-right:1px solid rgba(255,255,255,0.1);">
<div style="font-size:0.6rem;color:#94a3b8;margin-bottom:4px;font-weight:bold;">FALLADOS</div>
<div style="font-size:1.3rem;font-weight:900;color:#ff3e3e;">{fallados}</div>
</div>
<div style="text-align:center;">
<div style="font-size:0.6rem;color:#94a3b8;margin-bottom:4px;font-weight:bold;">BOPD</div>
<div style="font-size:1.3rem;font-weight:900;color:#00f2ff;">{produccion_total:,.0f}</div>
</div>
</div>
<div style="margin-top:15px;height:4px;background:rgba(255,255,255,0.05);border-radius:2px;overflow:hidden;">
<div style="width:{pct_op}%;height:100%;background:linear-gradient(90deg,{color_borde},#fff);
box-shadow:0 0 10px {color_borde};"></div>
</div>
</div>
"""


def render_tab_resumen(
    df_bd_filtered: pd.DataFrame,
    df_forma9_filtered: pd.DataFrame,
    reporte_runes_filtered,
    fecha_evaluacion,
    selected_activo: str,
):
    """Renderiza el contenido completo del Tab RESUMEN."""

    # ── Tabla + Chart RUNES ───────────────────────────────────────────────
    col_table, col_chart = st.columns([0.4, 0.6])

    with col_table:
        st.markdown(f"""
<div style="background:linear-gradient(90deg,{COLOR_PRINCIPAL}11,transparent);padding:8px;
border-left:4px solid {COLOR_PRINCIPAL};border-radius:4px;margin-bottom:12px;">
<h5 style='margin:0;color:{COLOR_PRINCIPAL};font-weight:800;font-size:1.1rem;'>🔢 RESUMEN DE CORRIDAS</h5>
</div>
""", unsafe_allow_html=True)

        if reporte_runes_filtered is not None:
            for col_safe in ['CLUSTER', 'POZO', 'RUN', 'ALS', 'Categoría']:
                if col_safe in reporte_runes_filtered.columns:
                    reporte_runes_filtered[col_safe] = reporte_runes_filtered[col_safe].astype(str)
        st.dataframe(reporte_runes_filtered, hide_index=True, use_container_width=True, height=350)

    with col_chart:
        if reporte_runes_filtered is not None and not reporte_runes_filtered.empty:
            categories = reporte_runes_filtered['Categoría'].tolist()
            counts     = reporte_runes_filtered['Conteo'].tolist()

            echarts_options = {
                "backgroundColor": "transparent",
                "title": {
                    "text": f"RUNS POR CATEGORÍA ({selected_activo})",
                    "left": "center",
                    "textStyle": {"color": "#fff", "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"},
                },
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "grid": {"left": "3%", "right": "4%", "bottom": "3%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "value", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
                "yAxis": [{"type": "category", "data": categories, "axisLabel": {"color": "#fff", "fontSize": 11}}],
                "series": [{
                    "name": "Cantidad", "type": "bar", "data": counts,
                    "itemStyle": {
                        "color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
                                  "colorStops": [{"offset": 0, "color": COLOR_PRINCIPAL}, {"offset": 1, "color": "#00f2ff"}]},
                        "borderRadius": [0, 10, 10, 0],
                    },
                    "label": {"show": True, "position": "right", "color": "#fff", "fontWeight": "bold"},
                }],
            }
            html_content = f"""
<div id="echarts-runes" style="width:100%;height:320px;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
(function(){{
    var myChart=echarts.init(document.getElementById('echarts-runes'),'dark');
    myChart.setOption({json.dumps(echarts_options)});
    window.addEventListener('resize',function(){{myChart.resize();}});
}})();
</script>
"""
            components.html(html_content, height=340)
        else:
            st.info("No hay datos para mostrar en el conteo de RUNES.")

    # ── KPIs de Alto Nivel ──
    import kpis
    kpis.mostrar_kpis(
        df_bd_filtered, 
        reporte_runes=reporte_runes_filtered, 
        df_forma9=df_forma9_filtered, 
        fecha_evaluacion=fecha_evaluacion
    )
    
    st.markdown("---")
    
    # ── Estado de la Campaña ──────────────────────────────────────────────
    fecha_eval_ts  = pd.to_datetime(fecha_evaluacion)
    anio_campana   = fecha_eval_ts.year

    st.markdown(f"""
<div style="background:linear-gradient(90deg,rgba(0,242,255,0.1),transparent);padding:12px 20px;
border-left:5px solid #00f2ff;border-radius:8px;margin:1.5em 0;
box-shadow:-10px 0 20px rgba(0,242,255,0.1);display:flex;align-items:center;gap:15px;">
<div style="width:10px;height:10px;background:#00f2ff;border-radius:50%;
box-shadow:0 0 10px #00f2ff;animation:pulse 2s infinite;"></div>
<h4 style='font-size:1.2rem;font-weight:900;margin:0;color:#fff;letter-spacing:3px;
text-transform:uppercase;font-family:"Outfit",sans-serif;'>
ESTADO DE LA CAMPAÑA <span style="color:#00f2ff;">{anio_campana}</span>
</h4>
<style> @keyframes pulse {{0%{{opacity:0.4;}}50%{{opacity:1;}}100%{{opacity:0.4;}}}} </style>
</div>
""", unsafe_allow_html=True)

    df_campana = df_bd_filtered[df_bd_filtered['FECHA_RUN'].dt.year == anio_campana].copy()

    if df_campana.empty:
        st.info(f"No hay registros de Runs iniciados en el año {anio_campana}.")
        return

    df_campana['RUN'] = pd.to_numeric(df_campana['RUN'], errors='coerce').fillna(0)
    df_nuevos        = df_campana[df_campana['RUN'] == 1].copy()
    df_intervenciones = df_campana[df_campana['RUN'] > 1].copy()

    html_nuevos = _calcular_metricas_grupo(df_nuevos,        "Pozos Nuevos",        "#00cfff", fecha_eval_ts, df_forma9_filtered)
    html_interv = _calcular_metricas_grupo(df_intervenciones, "Workover / Servicios", "#ff00ff", fecha_eval_ts, df_forma9_filtered)

    st.markdown(f"""
<div style="display:flex;gap:15px;flex-wrap:wrap;margin-bottom:15px;">
{html_nuevos}
{html_interv}
</div>
""", unsafe_allow_html=True)

    with st.expander(f"📋 Ver detalle de Pozos Campaña {anio_campana}"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### Pozos Nuevos")
            if not df_nuevos.empty:
                st.dataframe(df_nuevos[['POZO', 'RUN', 'FECHA_RUN', 'FECHA_FALLA', 'ACTIVO']].reset_index(drop=True), use_container_width=True)
            else:
                st.info("Sin pozos nuevos.")
        with c2:
            st.markdown("##### Intervenciones")
            if not df_intervenciones.empty:
                st.dataframe(df_intervenciones[['POZO', 'RUN', 'FECHA_RUN', 'FECHA_FALLA', 'ACTIVO']].reset_index(drop=True), use_container_width=True)
            else:
                st.info("Sin intervenciones.")

    # ── Gráficos Avanzados (Integración de grafico.py y grafico_run_life.py) ──
    st.markdown("---")
    st.markdown(f"""
<div style="background:linear-gradient(90deg,{COLOR_PRINCIPAL}11,transparent);padding:8px;
border-left:4px solid {COLOR_PRINCIPAL};border-radius:4px;margin:1.5em 0;">
<h4 style='margin:0;color:{COLOR_PRINCIPAL};font-weight:800;font-size:1.2rem;letter-spacing:1px;'>📈 DASHBOARD DE PERFORMANCE ESTRATÉGICO</h4>
</div>
""", unsafe_allow_html=True)

    import grafico
    import grafico_run_life

    # Generar data mensual
    _, df_monthly = grafico.generar_grafico_resumen(
        df_bd_filtered, 
        df_forma9_filtered, 
        fecha_evaluacion,
        titulo="Performance Mensual"
    )

    if not df_monthly.empty:
        # Gráfico Principal
        grafico.render_premium_echarts(
            df_monthly, 
            titulo=f"VISUALIZACIÓN CRÍTICA - {selected_activo}"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficos Secundarios
        c1, c2 = st.columns(2)
        with c1:
            grafico_run_life.render_premium_echarts_run_life(df_monthly, titulo="TIEMPO DE VIDA")
        with c2:
            grafico_run_life.render_premium_echarts_pozos(df_monthly, titulo="OPERATIVIDAD")
    else:
        st.info("No hay datos mensuales suficientes para generar el Dashboard Estratégico.")
