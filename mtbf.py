import pandas as pd
import streamlit as st
import plotly.express as px
from theme import get_colors, get_plotly_layout, styled_title, plotly_styled_title

_colors = get_colors()
COLOR_PRINCIPAL = _colors.get('primary', '#00ff99')
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = _bg_raw or '#1a1a2e'
get_color_sequence = _colors.get('color_sequence', lambda mode=None: [
    '#00A2FF',  # 1. Azul Zafiro Eléctrico
    '#55228A',  # 2. Verde Lima Neón
    '#0011D1',  # 3. Azul Cobalto Profundo
    '#00FF0D',  # 4. Verde Neón Puro
    '#4B0073',  # 5. Morado Índigo Profundo
    '#000980'   # 6. Azul Ultra Oscuro Medianoche
])
get_plotly_layout = get_plotly_layout
styled_title = styled_title

def calcular_mtbf(df_bd, fecha_evaluacion):
    """
    Calcula el MTBF usando el método solicitado: filtrado, orden, columnas auxiliares y fórmula especial.
    """
    df = df_bd.copy()
    df['FECHA_RUN'] = pd.to_datetime(df['FECHA_RUN'], errors='coerce')
    df['FECHA_FALLA'] = pd.to_datetime(df['FECHA_FALLA'], errors='coerce')
    # Filtrar solo por fecha de evaluación
    df = df[df['FECHA_RUN'] <= pd.to_datetime(fecha_evaluacion)]
    total_registros = len(df)
    total_mtbf_1 = (df['INDICADOR_MTBF'] == 1).sum() if 'INDICADOR_MTBF' in df.columns else 0
    total_runlife = df['RUN LIFE @ FALLA'].notna().sum() if 'RUN LIFE @ FALLA' in df.columns else 0
    # Mostrar resumen en consola/Streamlit
    # Usar todos los registros con RUN LIFE @ FALLA válido
    df = df[df['RUN LIFE @ FALLA'].notna()]
    df = df.sort_values('RUN LIFE @ FALLA').reset_index(drop=True)
    n = len(df)
    if n == 0:
        return 0, pd.DataFrame()
    # ITEM: enumerar 1,2,3...
    df['ITEM'] = range(1, n+1)
    # R(ti/Ti-1): si INDICADOR_MTBF==1 usar fórmula, si no, poner 1
    if 'INDICADOR_MTBF' in df.columns:
        df['R(ti/Ti-1)'] = df.apply(lambda row: (n + 1 - row['ITEM']) / (n + 2 - row['ITEM']) if row['INDICADOR_MTBF'] == 1 else 1, axis=1)
    else:
        df['R(ti/Ti-1)'] = 1
    # R(Ti): acumulativo multiplicativo
    r_ti = []
    for i, val in enumerate(df['R(ti/Ti-1)']):
        if i == 0:
            r_ti.append(val)
        else:
            r_ti.append(val * r_ti[i-1])
    df['R(Ti)'] = r_ti
    # R(Ti)*dt
    dt = df['RUN LIFE @ FALLA'].values
    rti_dt = []
    for i, r in enumerate(df['R(Ti)']):
        if i == 0:
            rti_dt.append(r * (dt[i] - 0))
        else:
            rti_dt.append(r * (dt[i] - dt[i-1]))
    df['R(Ti)*dt'] = rti_dt
    mtbf = df['R(Ti)*dt'].sum()
    return mtbf, df[['ITEM', 'RUN LIFE @ FALLA', 'R(ti/Ti-1)', 'R(Ti)', 'R(Ti)*dt']]

def mostrar_mtbf(mtbf_global, mtbf_por_pozo, df_bd=None, fecha_evaluacion=None):
    # Título removido por solicitud de usuario
    st.markdown(f"""
    <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 2rem;">
        <div style="flex: 1; padding: 2rem; background: linear-gradient(135deg, rgba(19, 91, 236, 0.2), rgba(10, 14, 39, 0.7)); border: 1px solid rgba(19, 91, 236, 0.4); border-radius: 1.5rem; backdrop-filter: blur(20px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3); text-align: center; color: white; position: relative; overflow: hidden;">
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(to right, #135bec, #00f2ff, #135bec);"></div>
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.3em; font-weight: 800; color: #00f2ff; margin-bottom: 0.5rem; opacity: 0.8;">TMEF GLOBAL ESTIMADO</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 4rem; font-weight: 900; margin-top: 5px; text-shadow: 0 0 20px rgba(19, 91, 236, 0.5);">{mtbf_global:.2f} <span style="font-size: 1.25rem; font-weight: 500; color: #94a3b8;">días</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_tabla, col_graf = st.columns([0.4, 0.6])
    with col_tabla:
        # Si es la tabla auxiliar, mostrar index desde 1
        if isinstance(mtbf_por_pozo, pd.DataFrame) and 'ITEM' in mtbf_por_pozo.columns:
            st.dataframe(mtbf_por_pozo.set_index('ITEM'), use_container_width=True)
        else:
            st.dataframe(mtbf_por_pozo.reset_index().rename(columns={0: 'TMEF (días)'}), use_container_width=True, hide_index=True)
    with col_graf:
        if df_bd is not None and fecha_evaluacion is not None:
            df_hist = historico_mtbf(df_bd, fecha_evaluacion)
            graficar_historico_mtbf(df_hist)
        else:
            pass  # Eliminado mensaje informativo para limpiar la UI

def historico_mtbf(df_bd, fecha_evaluacion):
    """
    Calcula el MTBF promedio mensual por ACTIVO considerando todos los pozos activos en cada mes.
    """
    df_bd = df_bd.copy()
    df_bd['FECHA_RUN'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')
    df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
    start_date = fecha_evaluacion - pd.DateOffset(years=3)
    meses = pd.date_range(start=start_date, end=fecha_evaluacion, freq='MS')
    historico = []
    for mes in meses:
        fin_mes = mes + pd.offsets.MonthEnd(0)
        activos_mes = df_bd[
            (df_bd['FECHA_RUN'] <= fin_mes) &
            (
                (df_bd['FECHA_PULL'].isna() | (df_bd['FECHA_PULL'] > fin_mes)) &
                (df_bd['FECHA_FALLA'].isna() | (df_bd['FECHA_FALLA'] > fin_mes))
            )
        ].copy()
        if not activos_mes.empty:
            activos_mes['MTBF_MES'] = (fin_mes - activos_mes['FECHA_RUN']).dt.days
            promedio = activos_mes.groupby('ACTIVO')['MTBF_MES'].mean().reset_index()
            promedio['Mes'] = fin_mes
            historico.append(promedio)
    if historico:
        df_hist = pd.concat(historico, ignore_index=True)
        df_hist = df_hist[['Mes', 'ACTIVO', 'MTBF_MES']]
        df_hist.rename(columns={'MTBF_MES': 'TMEF Promedio'}, inplace=True)
        return df_hist
    else:
        return pd.DataFrame(columns=['Mes', 'ACTIVO', 'TMEF Promedio'])

def render_premium_echarts_mtbf(df_hist, titulo="TMEF HISTÓRICO POR CAMPO"):
    import json
    import streamlit.components.v1 as components
    
    if df_hist.empty:
        return st.info("No hay datos históricos de TMEF para mostrar.")
    
    # Preparar datos
    months = sorted([str(m) for m in df_hist['Mes'].dt.strftime('%Y-%m').unique()])
    activos = sorted(df_hist['ACTIVO'].unique().tolist())
    
    series = []
    color_seq = [
        '#00f2ff', '#135bec', '#b200cc', '#00ff99', '#ffde31', '#ff4b4b', '#ffab40'
    ]
    
    for i, act in enumerate(activos):
        df_act = df_hist[df_hist['ACTIVO'] == act]
        data_act = []
        for m in months:
            val = df_act[df_act['Mes'].dt.strftime('%Y-%m') == m]['TMEF Promedio'].values
            data_act.append(round(float(val[0]), 2) if len(val) > 0 else 0)
        
        series.append({
            "name": act,
            "type": "bar",
            "data": data_act,
            "itemStyle": {"borderRadius": [4, 4, 0, 0]}
        })

    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "text": titulo,
            "left": "center",
            "textStyle": {"color": "#fff", "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
        },
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"data": activos, "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 10}},
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
        "xAxis": [{"type": "category", "data": months, "axisLabel": {"color": "#888", "fontSize": 10}}],
        "yAxis": [{"type": "value", "name": "Días", "axisLabel": {"color": "#888"}, "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.05)"}}}],
        "color": color_seq,
        "series": series
    }
    
    html_content = f"""
    <div id="echarts-mtbf" style="width:100%; height:400px;"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var myChart = echarts.init(document.getElementById('echarts-mtbf'), 'dark');
            myChart.setOption({json.dumps(echarts_options)});
            window.addEventListener('resize', function() {{ myChart.resize(); }});
        }})();
    </script>
    """
    components.html(html_content, height=420)

def graficar_historico_mtbf(df_hist):
    render_premium_echarts_mtbf(df_hist)