"""
tabs/tab_performance.py
=======================
Renderiza el contenido del Tab "⚡ PERFORMANCE":
 - Correlación BOPD (FORMA9) vs Tiempo de Vida (BD)
 - Bucketización por antigüedad (años)
 - Gráficos ECharts de Producción por Antigüedad
 - Botón de descarga del dataset correlacionado
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL

def bucket_runlife(days):
    """Categoriza los días de Run Life en rangos de 2 años."""
    if pd.isna(days): return 'Sin Datos'
    years = days / 365.25
    if years < 2: return '< 2 años'
    if years < 4: return '2 - 4 años'
    if years < 6: return '4 - 6 años'
    return '> 6 años'

def render_tab_performance(df_bd_filtered, df_forma9_filtered, fecha_evaluacion):
    """Renderiza el contenido completo del Tab PERFORMANCE."""
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(0, 207, 255, 0.1), transparent); padding: 10px; border-left: 5px solid #00cfff; border-radius: 5px; margin-top: 1.5em; margin-bottom: 1em;">
        <h4 style='font-size:1.3rem; font-weight:800; margin:0; color:#00cfff;'>
            PRODUCCIÓN (BOPD) vs TIEMPO DE VIDA
        </h4>
    </div>
    """, unsafe_allow_html=True)

    try:
        fecha_eval = pd.to_datetime(fecha_evaluacion)
        df_runs_validos = df_bd_filtered[df_bd_filtered['FECHA_RUN'] <= fecha_eval].copy()
        
        if df_runs_validos.empty:
            st.info('No hay RUNs previos a la fecha de evaluación para los pozos filtrados.')
            return

        df_last_run = df_runs_validos.sort_values('FECHA_RUN').groupby('POZO', as_index=False).last()
        
        # Asegurar tipo datetime
        for dt_col in ['FECHA_PULL', 'FECHA_FALLA', 'FECHA_RUN']:
            if dt_col in df_last_run.columns:
                df_last_run[dt_col] = pd.to_datetime(df_last_run[dt_col], errors='coerce')
            else:
                df_last_run[dt_col] = pd.NaT

        mask_operativos = (
            (df_last_run['FECHA_RUN'] <= fecha_eval) &
            ((df_last_run['FECHA_PULL'].isna()) | (df_last_run['FECHA_PULL'] > fecha_eval)) &
            ((df_last_run['FECHA_FALLA'].isna()) | (df_last_run['FECHA_FALLA'] > fecha_eval))
        )
        df_last_run = df_last_run[mask_operativos].copy()
    except Exception as e:
        st.warning(f"No se pudo aplicar el filtro de pozos operativos: {e}")
        df_last_run = df_bd_filtered.copy()

    # Procesar FORMA9 para el mes de evaluación
    df_f9 = df_forma9_filtered.copy()
    df_f9_sum = pd.DataFrame(columns=['POZO', 'BOPD'])
    try:
        if 'FECHA_FORMA9' in df_f9.columns:
            df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce')
            df_f9_month = df_f9[(df_f9['FECHA_FORMA9'].dt.year == fecha_eval.year) & (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)].copy()

            dias_col = next((c for c in df_f9_month.columns if 'DIAS' in str(c).upper()), None)
            bopd_col = next((c for c in df_f9_month.columns if 'BOPD' in str(c).upper()), None)

            if dias_col:
                df_f9_month[dias_col] = pd.to_numeric(df_f9_month[dias_col], errors='coerce').fillna(0)
                df_f9_month = df_f9_month[df_f9_month[dias_col] > 0].copy()

            if not df_f9_month.empty and bopd_col:
                df_f9_month[bopd_col] = pd.to_numeric(df_f9_month[bopd_col], errors='coerce').fillna(0)
                df_f9_sum = df_f9_month.groupby('POZO', as_index=False).agg({bopd_col: 'sum'})
                df_f9_sum.rename(columns={bopd_col: 'BOPD'}, inplace=True)
    except Exception as e:
        st.warning(f"Error al procesar FORMA9: {e}")

    # Correlacionar BOPD con BD
    if not df_f9_sum.empty:
        try:
            # Data de soporte para el merge
            df_f9_month_raw = df_f9[(df_f9['FECHA_FORMA9'].dt.year == fecha_eval.year) & (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)].copy()
            df_f9_lastdate = df_f9_month_raw.sort_values('FECHA_FORMA9').groupby('POZO', as_index=False).last()[['POZO', 'FECHA_FORMA9']]
            df_f9_merge = pd.merge(df_f9_sum, df_f9_lastdate, on='POZO', how='left')
            
            # Usar la BD filtrada pero asegurar que tenemos las columnas necesarias
            bd_match = df_bd_filtered.copy()
            for col in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
                bd_match[col] = pd.to_datetime(bd_match.get(col), errors='coerce')

            # Para cada pozo en F9, buscar su Run activo en esa fecha
            # El Run activo es aquel donde FECHA_RUN <= FECHA_FORMA9 y (FECHA_PULL > FECHA_FORMA9 o es NaN)
            runlife_data = []
            for _, row_f9 in df_f9_merge.iterrows():
                pozo = row_f9['POZO']
                f9_date = row_f9['FECHA_FORMA9']
                
                # Buscar el run que estaba activo en la fecha de la Forma 9
                mask = (bd_match['POZO'] == pozo) & (bd_match['FECHA_RUN'] <= f9_date)
                runs_candidatos = bd_match[mask].copy()
                
                if not runs_candidatos.empty:
                    # Nos quedamos con el más reciente respecto a la fecha de F9
                    actual_run = runs_candidatos.sort_values('FECHA_RUN', ascending=False).iloc[0]
                    
                    # Calcular Run Life dinámico a la fecha de evaluación
                    # (Días transcurridos desde el inicio del run hasta la fecha de corte)
                    diff = (fecha_eval - actual_run['FECHA_RUN']).days
                    runlife_data.append(diff if diff >= 0 else 0)
                else:
                    runlife_data.append(np.nan)
            
            df_f9_merge['RUN LIFE'] = runlife_data
            
            total_pozos = len(df_f9_merge)
            mapeados = df_f9_merge['RUN LIFE'].notna().sum()
            st.markdown(f"**Pozos Operativos (ON en el mes):** {total_pozos} — **Con RUN asociado:** {mapeados}")
            
            merged = df_f9_merge[['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE']].copy()
        except Exception as e:
            st.warning(f"Error en correlación de performance: {e}")
            merged = pd.DataFrame(columns=['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE'])
    else:
        merged = pd.DataFrame(columns=['POZO', 'BOPD', 'FECHA_FORMA9', 'RUN LIFE'])

    merged['BOPD'] = pd.to_numeric(merged['BOPD'], errors='coerce').fillna(0)
    merged['RUN LIFE'] = pd.to_numeric(merged['RUN LIFE'], errors='coerce').fillna(0)
    merged['Rango'] = merged['RUN LIFE'].apply(bucket_runlife)

    # Gráfico y Tabla
    col_chart, col_data = st.columns([0.6, 0.4])
    
    with col_chart:
        resumen_bucket = merged.groupby('Rango').agg({'BOPD': 'sum', 'POZO': 'count'}).reset_index()
        orden_rangos = ['< 2 años', '2 - 4 años', '4 - 6 años', '> 6 años', 'Sin Datos']
        resumen_bucket['Rango'] = pd.Categorical(resumen_bucket['Rango'], categories=orden_rangos, ordered=True)
        resumen_bucket = resumen_bucket.sort_values('Rango')

        echarts_performance = {
            "backgroundColor": "transparent",
            "title": {"text": "PRODUCCIÓN POR ANTIGÜEDAD DE EQUIPO", "left": "center", "textStyle": {"color": "#fff", "fontSize": 14}},
            "tooltip": {"trigger": "axis", "formatter": "{b}<br/>BOPD: {c0}<br/>Pozos: {c1}"},
            "legend": {"data": ["BOPD", "Pozos"], "bottom": 0, "textStyle": {"color": "#ccc"}},
            "xAxis": {"type": "category", "data": resumen_bucket['Rango'].astype(str).tolist(), "axisLabel": {"color": "#888", "rotate": 30}},
            "yAxis": [{"type": "value", "name": "BOPD", "axisLabel": {"color": "#00f2ff"}}, {"type": "value", "name": "Pozos", "position": "right", "axisLabel": {"color": "#ff00ff"}}],
            "series": [
                {"name": "BOPD", "type": "bar", "data": resumen_bucket['BOPD'].tolist(), "itemStyle": {"color": "#00f2ff"}},
                {"name": "Pozos", "type": "line", "yAxisIndex": 1, "data": resumen_bucket['POZO'].tolist(), "itemStyle": {"color": "#ff00ff"}}
            ]
        }
        
        html_perf = f"""
        <div id="echarts-perf" style="width:100%; height:400px;"></div>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <script>
            (function() {{
                var myChart = echarts.init(document.getElementById('echarts-perf'), 'dark');
                myChart.setOption({json.dumps(echarts_performance)});
                window.addEventListener('resize', function() {{ myChart.resize(); }});
            }})();
        </script>
        """
        components.html(html_perf, height=420)

    with col_data:
        st.markdown("##### 📝 Detalle por Pozo")
        st.dataframe(merged[['POZO', 'BOPD', 'RUN LIFE', 'Rango']].sort_values('BOPD', ascending=False), hide_index=True, use_container_width=True)
        
        csv = merged.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Dataset Correlacionado", csv, "correlacion_bopd_runlife.csv", "text/csv", use_container_width=True)
