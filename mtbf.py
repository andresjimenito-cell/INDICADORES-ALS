import pandas as pd
import streamlit as st
import plotly.express as px
import theme as _theme_mod

COLOR_PRINCIPAL = getattr(_theme_mod, 'COLOR_PRINCIPAL', '#00ff99')
COLOR_FONDO_OSCURO = getattr(_theme_mod, 'COLOR_FONDO_OSCURO', '#1a1a2e')
get_color_sequence = getattr(_theme_mod, 'get_color_sequence', lambda mode=None: [COLOR_PRINCIPAL, '#00cfff', '#FFDE31', '#5AFFDA'])
get_plotly_layout = getattr(_theme_mod, 'get_plotly_layout', lambda xa=None, ya=None, mode=None: {
    'plot_bgcolor': COLOR_FONDO_OSCURO,
    'paper_bgcolor': COLOR_FONDO_OSCURO,
    'font_color': getattr(_theme_mod, 'COLOR_FUENTE', '#FFFFFF')
})
styled_title = getattr(_theme_mod, 'styled_title', lambda text, mode=None: f"<span style=\"color:{COLOR_PRINCIPAL}; text-shadow: 0 0 5px {COLOR_PRINCIPAL};\">{text}</span>")

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
    st.subheader('MTBF (Mean Time Between Failures)')
    st.metric(label='MTBF Global (días)', value=f"{mtbf_global:.2f}")
    col_tabla, col_graf = st.columns([0.4, 0.6])
    with col_tabla:
        # Si es la tabla auxiliar, mostrar index desde 1
        if isinstance(mtbf_por_pozo, pd.DataFrame) and 'ITEM' in mtbf_por_pozo.columns:
            st.dataframe(mtbf_por_pozo.set_index('ITEM'), use_container_width=True)
        else:
            st.dataframe(mtbf_por_pozo.reset_index().rename(columns={0: 'MTBF (días)'}), use_container_width=True, hide_index=True)
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
        df_hist.rename(columns={'MTBF_MES': 'MTBF Promedio'}, inplace=True)
        return df_hist
    else:
        return pd.DataFrame(columns=['Mes', 'ACTIVO', 'MTBF Promedio'])

def graficar_historico_mtbf(df_hist):
    if not df_hist.empty and 'ACTIVO' in df_hist.columns:
        color_sequence = get_color_sequence()
        fig = px.bar(
            df_hist,
            x='Mes',
            y='MTBF Promedio',
            color='ACTIVO',
            barmode='group',
        title=styled_title('MTBF promedio mensual por campo  (últimos 3 años)'),
            labels={'Mes': 'Mes', 'MTBF Promedio': 'MTBF Promedio (días)', 'ACTIVO': 'ACTIVO'},
            color_discrete_sequence=color_sequence
        )
        layout = get_plotly_layout()
        # asegurar orden de categorias y colores de ejes
        layout.update({'xaxis': {'categoryorder': 'category ascending', 'color': COLOR_PRINCIPAL}, 'yaxis': {'color': COLOR_PRINCIPAL}})
        fig.update_layout(**layout)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('No hay datos suficientes para mostrar el histórico de MTBF.')
