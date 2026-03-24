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

def calcular_mtbf(df_bd, fecha_evaluacion, col_life='RUN LIFE @ FALLA', col_indicador='INDICADOR_MTBF'):
    """
    Calcula el MTBF usando el método solicitado: filtrado, orden, columnas auxiliares y fórmula especial.
    Permite especificar la columna de tiempo de vida (col_life) para soportar MTBF Efectivo.
    """
    df = df_bd.copy()
    
    # Asegurar que las columnas existen
    if col_life not in df.columns:
        # Fallback a RUN LIFE si no existe (probablemente en df_bd_filtered inicial)
        if 'RUN LIFE' in df.columns and col_life == 'RUN LIFE @ FALLA':
            col_life = 'RUN LIFE'
        else:
            return 0, pd.DataFrame()

    df['FECHA_RUN'] = pd.to_datetime(df['FECHA_RUN'], errors='coerce')
    df['FECHA_FALLA'] = pd.to_datetime(df['FECHA_FALLA'], errors='coerce')
    
    # Filtrar solo por fecha de evaluación
    df = df[df['FECHA_RUN'] <= pd.to_datetime(fecha_evaluacion)]
    
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
    # Layout de KPIs principales
    if mtbf_efectivo is not None:
        st.markdown(f"""
        <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 2rem;">
            <div style="flex: 1; padding: 1.5rem; background: linear-gradient(135deg, rgba(19, 91, 236, 0.2), rgba(10, 14, 39, 0.7)); border: 1px solid rgba(19, 91, 236, 0.4); border-radius: 1.5rem; backdrop-filter: blur(20px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3); text-align: center; color: white; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(to right, #135bec, #00f2ff, #135bec);"></div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 800; color: #00f2ff; margin-bottom: 0.5rem; opacity: 0.8;">TMEF GLOBAL (RUN LIFE)</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 900; margin-top: 5px; text-shadow: 0 0 15px rgba(19, 91, 236, 0.4);">{mtbf_global:.2f} <span style="font-size: 1rem; font-weight: 500; color: #94a3b8;">días</span></div>
            </div>
            <div style="flex: 1; padding: 1.5rem; background: linear-gradient(135deg, rgba(0, 255, 157, 0.15), rgba(10, 39, 25, 0.7)); border: 1px solid rgba(0, 255, 157, 0.4); border-radius: 1.5rem; backdrop-filter: blur(20px); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3); text-align: center; color: white; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(to right, #00ff9d, #00f2ff, #00ff9d);"></div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 800; color: #00ff9d; margin-bottom: 0.5rem; opacity: 0.8;">TMEF EFECTIVO (DÍAS TRAB.)</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 900; margin-top: 5px; text-shadow: 0 0 15px rgba(0, 255, 157, 0.4);">{mtbf_efectivo:.2f} <span style="font-size: 1rem; font-weight: 500; color: #94a3b8;">días</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
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
        # Generar tablita de TMEF por Campo
        grupo_col = 'CAMPO' if df_bd is not None and 'CAMPO' in df_bd.columns else 'ACTIVO'
        if df_bd is not None and grupo_col in df_bd.columns:
            st.markdown(styled_title("TMEF por Campo", f"Resumen por {grupo_col.title()}"), unsafe_allow_html=True)
            res_campo = []
            for item in sorted(df_bd[grupo_col].dropna().unique()):
                df_c = df_bd[df_bd[grupo_col] == item]
                val_c, _ = calcular_mtbf(df_c, fecha_evaluacion)
                if val_c > 0:
                    row_data = {grupo_col.title(): item, 'TMEF (días)': round(val_c, 2)}
                    if mtbf_efectivo is not None and 'RUN_LIFE_EFECTIVO' in df_bd.columns:
                        val_efec, _ = calcular_mtbf(df_c, fecha_evaluacion, col_life='RUN_LIFE_EFECTIVO')
                        row_data['TMEF Efec.'] = round(val_efec, 2)
                    res_campo.append(row_data)
            
            if res_campo:
                df_res_campo = pd.DataFrame(res_campo).sort_values('TMEF (días)', ascending=False)
                st.dataframe(df_res_campo, use_container_width=True, hide_index=True)
            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(styled_title("Detalle de Análisis", "Cálculo de TMEF"), unsafe_allow_html=True)
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
        '#00f2ff', '#135bec', '#b200cc', '#00ff99', '#ffde31', '#ff4b4b', '#ffab40'
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
            "textStyle": {"color": "#fff", "fontSize": 14, "fontFamily": "Outfit", "fontWeight": "900"}
        },
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"data": categorias, "bottom": 0, "textStyle": {"color": "#ccc", "fontSize": 10}},
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