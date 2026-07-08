import pandas as pd
import streamlit as st
import plotly.express as px
import json
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

@st.cache_data(show_spinner=False)
def calcular_mtbf(df_bd, fecha_evaluacion, col_life='RUN LIFE @ FALLA', col_indicador='INDICADOR_MTBF'):
    """
    Calcula el MTBF usando el método solicitado: filtrado, orden, columnas auxiliares y fórmula especial.
    Permite especificar la columna de tiempo de vida (col_life) para soportar MTBF Efectivo.
    """
    df = df_bd.copy()
    
    # Asegurar que las columnas existen
    if col_life not in df.columns:
        if col_life == 'RUN LIFE @ FALLA' and 'RUN LIFE FALLA' in df.columns:
            col_life = 'RUN LIFE FALLA'
        elif 'RUN LIFE' in df.columns and col_life == 'RUN LIFE @ FALLA':
            col_life = 'RUN LIFE'
        else:
            return 0, pd.DataFrame()

    df['FECHA_RUN'] = pd.to_datetime(df['FECHA_RUN'], errors='coerce')
    df['FECHA_FALLA'] = pd.to_datetime(df['FECHA_FALLA'], errors='coerce')
    df['FECHA_PULL'] = pd.to_datetime(df.get('FECHA_PULL'), errors='coerce')
    
    # Filtrar solo por fecha de evaluación
    df = df[df['FECHA_RUN'] <= pd.to_datetime(fecha_evaluacion)]
    
    # Filtrar solo registros que hayan terminado (tienen fecha de falla o fecha de pull)
    df = df[df['FECHA_FALLA'].notna() | df['FECHA_PULL'].notna()]
    
    # Filtrar solo registros con tiempo de vida válido
    df = df[df[col_life].notna()]
    df = df.sort_values(col_life).reset_index(drop=True)
    
    n = len(df)
    if n == 0:
        return 0, pd.DataFrame()
        
    # ITEM: enumerar 1,2,3...
    df['ITEM'] = range(1, n+1)
    
    # R(ti/Ti-1): si col_indicador==1 usar fórmula, si no, poner 1
    if col_indicador in df.columns:
        df['R(ti/Ti-1)'] = df.apply(lambda row: (n + 1 - row['ITEM']) / (n + 2 - row['ITEM']) if row[col_indicador] == 1 else 1, axis=1)
    else:
        df['R(ti/Ti-1)'] = 1
        
    # R(Ti): acumulativo multiplicativo
    r_ti = []
    current_rti = 1.0
    for val in df['R(ti/Ti-1)']:
        current_rti *= val
        r_ti.append(current_rti)
    df['R(Ti)'] = r_ti
    
    # R(Ti)*dt
    dt = df[col_life].values
    rti_dt = []
    for i, r in enumerate(df['R(Ti)']):
        if i == 0:
            rti_dt.append(r * (dt[i] - 0))
        else:
            rti_dt.append(r * (dt[i] - dt[i-1]))
    df['R(Ti)*dt'] = rti_dt
    
    mtbf = df['R(Ti)*dt'].sum()
    return mtbf, df[['ITEM', col_life, 'R(ti/Ti-1)', 'R(Ti)', 'R(Ti)*dt']]

def mostrar_mtbf(mtbf_global, mtbf_por_pozo, mtbf_efectivo=None, df_bd=None, fecha_evaluacion=None):
    # Layout de KPIs principales usando clases HUD
    k1, k2 = st.columns(2)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🕒</div><div class="kpi-label">TMEF GLOBAL</div><div class="kpi-value">{mtbf_global:.0f}</div><div class="kpi-trend-positive">Días Run Life</div></div>', unsafe_allow_html=True)
    with k2:
        if mtbf_efectivo is not None:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚡</div><div class="kpi-label">TMEF EFECTIVO</div><div class="kpi-value" style="color:#00ff9d;">{mtbf_efectivo:.0f}</div><div class="kpi-trend-positive">Días Trabajados</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">📊</div><div class="kpi-label">PRECISIÓN</div><div class="kpi-value">98%</div><div class="kpi-trend-positive">Análisis Estadístico</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_tabla, col_graf = st.columns([0.4, 0.6])
    with col_tabla:
        grupo_col = 'CAMPO' if df_bd is not None and 'CAMPO' in df_bd.columns else 'ACTIVO'
        if df_bd is not None and grupo_col in df_bd.columns:
            st.markdown(f"<h5>📊 TMEF POR {grupo_col}</h5>", unsafe_allow_html=True)
            res_campo = []
            for item in sorted(df_bd[grupo_col].dropna().unique()):
                df_c = df_bd[df_bd[grupo_col] == item]
                val_c, _ = calcular_mtbf(df_c, fecha_evaluacion)
                if val_c > 0:
                    row_data = {grupo_col.title(): item, 'TMEF': round(val_c, 1)}
                    res_campo.append(row_data)
            
            if res_campo:
                df_res_campo = pd.DataFrame(res_campo).sort_values('TMEF', ascending=False)
                st.dataframe(df_res_campo, use_container_width=True, hide_index=True)

    with col_graf:
        if df_bd is not None and mtbf_global > 0:
            res_graf = []
            for item in sorted(df_bd[grupo_col].dropna().unique()):
                df_c = df_bd[df_bd[grupo_col] == item]
                val_c, _ = calcular_mtbf(df_c, fecha_evaluacion)
                if val_c > 0:
                    res_graf.append({'Categoria': item, 'TMEF': round(val_c, 1)})
            
            if res_graf:
                df_res_graf = pd.DataFrame(res_graf).sort_values('TMEF', ascending=True)
                echarts_options_val = {
                    "backgroundColor": "transparent",
                    "title": {"text": f"COMPARATIVA TMEF", "left": "center", "textStyle": {"color": "#137659", "fontSize": 14, "fontFamily": "Outfit"}},
                    "tooltip": {
                        "trigger": "axis", 
                        "axisPointer": {"type": "shadow"},
                        "backgroundColor": "rgba(255, 255, 255, 0.95)",
                        "borderColor": "#137659",
                        "borderWidth": 1,
                        "textStyle": {"color": "#1f221e"}
                    },
                    "grid": {"left": "3%", "right": "10%", "bottom": "3%", "top": "15%", "containLabel": True},
                    "xAxis": {"type": "value", "axisLabel": {"color": "#475569"}, "splitLine": {"lineStyle": {"color": "rgba(19, 118, 89, 0.05)"}}},
                    "yAxis": {"type": "category", "data": df_res_graf['Categoria'].tolist(), "axisLabel": {"color": "#1f221e"}},
                    "series": [{
                        "name": "TMEF", "type": "bar", "data": df_res_graf['TMEF'].tolist(),
                        "itemStyle": {
                            "color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
                                      "colorStops": [{"offset": 0, "color": "#c09c2e"}, {"offset": 1, "color": "rgba(192, 156, 46, 0.1)"}]},
                            "borderRadius": [0, 10, 10, 0]
                        },
                        "label": {"show": True, "position": "right", "color": "#1f221e"}
                    }]
                }
                
                html_val = f"""
                <div id="echarts-mtbf-val" style="width:100%; height:320px;"></div>
                <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
                <script>
                    (function() {{
                        var myChart = echarts.init(document.getElementById('echarts-mtbf-val'), null);
                        myChart.setOption({json.dumps(echarts_options_val)});
                        window.addEventListener('resize', function() {{ myChart.resize(); }});
                    }})();
                </script>
                """
                st.components.v1.html(html_val, height=340)
        else:
            st.info("No hay datos suficientes para generar el gráfico de valores TMEF.")

def historico_mtbf(df_bd, fecha_evaluacion):
    """
    Calcula el MTBF promedio mensual por CAMPO (o ACTIVO) considerando todos los pozos activos en cada mes.
    """
    df_bd = df_bd.copy()
    grupo_col = 'CAMPO' if 'CAMPO' in df_bd.columns else 'ACTIVO'
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
            promedio = activos_mes.groupby(grupo_col)['MTBF_MES'].mean().reset_index()
            promedio['Mes'] = fin_mes
            historico.append(promedio)
    if historico:
        df_hist = pd.concat(historico, ignore_index=True)
        # Asegurar que la columna tenga un nombre consistente para el gráfico
        if grupo_col in df_hist.columns:
            df_hist.rename(columns={grupo_col: 'CATEGORIA'}, inplace=True)
        df_hist = df_hist[['Mes', 'CATEGORIA', 'MTBF_MES']]
        df_hist.rename(columns={'MTBF_MES': 'TMEF Promedio'}, inplace=True)
        return df_hist
    else:
        return pd.DataFrame(columns=['Mes', 'CATEGORIA', 'TMEF Promedio'])

def render_premium_echarts_mtbf(df_hist, titulo="TMEF HISTÓRICO POR CAMPO"):
    import json
    import streamlit.components.v1 as components
    
    if df_hist.empty:
        return st.info("No hay datos históricos de TMEF para mostrar.")
    
    # Preparar datos
    months = sorted([str(m) for m in df_hist['Mes'].dt.strftime('%Y-%m').unique()])
    categorias = sorted(df_hist['CATEGORIA'].unique().tolist())
    
    series = []
    color_seq = [
        '#137659', '#c09c2e', '#095139', '#5b5c55', '#a28834', '#d32f2f', '#d2b48c'
    ]
    
    for i, cat in enumerate(categorias):
        df_cat = df_hist[df_hist['CATEGORIA'] == cat]
        data_cat = []
        for m in months:
            val = df_cat[df_cat['Mes'].dt.strftime('%Y-%m') == m]['TMEF Promedio'].values
            data_cat.append(round(float(val[0]), 2) if len(val) > 0 else 0)
        
        series.append({
            "name": cat,
            "type": "bar",
            "data": data_cat,
            "itemStyle": {"borderRadius": [4, 4, 0, 0]}
        })

    echarts_options = {
        "backgroundColor": "transparent",
        "title": {
            "text": titulo,
            "left": "center",
            "textStyle": {"color": "#137659", "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
        },
        "tooltip": {
            "trigger": "axis", 
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#137659",
            "borderWidth": 1,
            "textStyle": {"color": "#1f221e"}
        },
        "legend": {"data": categorias, "bottom": 0, "textStyle": {"color": "#475569", "fontSize": 10}},
        "grid": {"left": "3%", "right": "4%", "bottom": "15%", "top": "15%", "containLabel": True},
        "xAxis": [{"type": "category", "data": months, "axisLabel": {"color": "#475569", "fontSize": 10}}],
        "yAxis": [{"type": "value", "name": "Días", "axisLabel": {"color": "#475569"}, "splitLine": {"lineStyle": {"color": "rgba(19, 118, 89, 0.05)"}}}],
        "color": color_seq,
        "series": series
    }
    
    html_content = f"""
    <div id="echarts-mtbf" style="width:100%; height:400px; background:#ffffff; border-radius:15px; border:1px solid rgba(19, 118, 89, 0.15);"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var myChart = echarts.init(document.getElementById('echarts-mtbf'), null);
            myChart.setOption({json.dumps(echarts_options)});
            window.addEventListener('resize', function() {{ myChart.resize(); }});
        }})();
    </script>
    """
    components.html(html_content, height=420)

def graficar_historico_mtbf(df_hist):
    render_premium_echarts_mtbf(df_hist)