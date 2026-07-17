import pandas as pd
import numpy as np
import streamlit as st
from ui.theme import get_colors, get_plotly_layout
from datetime import timedelta

_colors = get_colors()
COLOR_PRINCIPAL = _colors.get('primary', '#00ff99')
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = _bg_raw or '#1a1a2e'
get_color_sequence = _colors.get('color_sequence', lambda mode=None: [COLOR_PRINCIPAL, '#00cfff', '#FFDE31', '#5AFFDA'])
get_plotly_layout = get_plotly_layout

@st.cache_data(show_spinner=False)
def calcular_indice_falla_anual(df_bd, df_forma9, fecha_evaluacion, fecha_inicio=None):
    """
    Calcula los índices de falla para el rango especificado o los últimos 12 años por defecto,
    incluyendo el cálculo de 12 meses rodante (rolling) para la gráfica, 
    y el resumen final.
    También calcula el índice adicional para pozos/runs con RUN_LIFE_EFECTIVO < 1500 días.
    """
    end_date = pd.to_datetime(fecha_evaluacion).normalize()
    if fecha_inicio is not None:
        start_date = pd.to_datetime(fecha_inicio).normalize()
    else:
        start_date = end_date - timedelta(days=365 * 12)
    
    # Start 12 months earlier to have history for rolling averages
    calc_start_date = start_date - pd.DateOffset(months=12)
    
    # Asegurar que las columnas de fecha son datetime
    df_bd = df_bd.copy()
    df_bd['FECHA_RUN'] = pd.to_datetime(df_bd['FECHA_RUN'])
    df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd['FECHA_FALLA'])
    df_bd['FECHA_PULL'] = pd.to_datetime(df_bd['FECHA_PULL'])
    
    df_forma9 = df_forma9.copy()
    df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'])
    
    # Pre-normalizar fechas fuera del bucle para evitar llamadas repetidas a .dt.normalize()
    df_bd['FECHA_RUN_NORM'] = df_bd['FECHA_RUN'].dt.normalize()
    df_bd['FECHA_FALLA_NORM'] = df_bd['FECHA_FALLA'].dt.normalize()
    df_bd['FECHA_PULL_NORM'] = df_bd['FECHA_PULL'].dt.normalize()
    
    df_forma9['FECHA_FORMA9_NORM'] = df_forma9['FECHA_FORMA9'].dt.normalize()
    
    # Asegurar que existe RUN_LIFE_EFECTIVO
    if 'RUN_LIFE_EFECTIVO' not in df_bd.columns:
        df_bd['RUN_LIFE_EFECTIVO'] = df_bd['RUN LIFE'] if 'RUN LIFE' in df_bd.columns else 0
    df_bd['RUN_LIFE_EFECTIVO'] = pd.to_numeric(df_bd['RUN_LIFE_EFECTIVO'], errors='coerce').fillna(0)
    
    monthly_data = []
    current_month_date = calc_start_date.replace(day=1)
    
    while current_month_date <= end_date:
        fecha_fin_mes = (pd.to_datetime(current_month_date) + pd.offsets.MonthEnd(0)).normalize()
        current_month_ts = pd.to_datetime(current_month_date).normalize()
        
        # Filtrar df_bd hasta el final del mes para calcular activos y fallas (sin copiar)
        df_bd_mes = df_bd[df_bd['FECHA_RUN_NORM'] <= fecha_fin_mes]
        
        # Filtrar df_forma9 para el mes actual (sin copiar)
        df_forma9_mes = df_forma9[
            (df_forma9['FECHA_FORMA9_NORM'] >= current_month_ts) &
            (df_forma9['FECHA_FORMA9_NORM'] <= fecha_fin_mes)
        ]
        
        # 1. Cálculos estándar
        pozos_operativos_mes = df_bd_mes[
            (df_bd_mes['FECHA_FALLA_NORM'].isna() | (df_bd_mes['FECHA_FALLA_NORM'] > fecha_fin_mes)) & 
            (df_bd_mes['FECHA_PULL_NORM'].isna() | (df_bd_mes['FECHA_PULL_NORM'] > fecha_fin_mes))
        ]['POZO'].nunique()

        pozos_on = df_forma9_mes[df_forma9_mes['DIAS TRABAJADOS'] > 0]['POZO'].nunique()

        fallas_totales_mes = df_bd_mes[
            (df_bd_mes['FECHA_FALLA_NORM'] >= current_month_ts) & 
            (df_bd_mes['FECHA_FALLA_NORM'] <= fecha_fin_mes)
        ].shape[0]
        
        fallas_als_mes = df_bd_mes[
            (df_bd_mes['FECHA_FALLA_NORM'] >= current_month_ts) & 
            (df_bd_mes['FECHA_FALLA_NORM'] <= fecha_fin_mes) &
            (df_bd_mes['INDICADOR_MTBF'] == 1)
        ].shape[0]
        
        # 2. Cálculos para RLE < 1500
        pozos_on_names = df_forma9_mes[df_forma9_mes['DIAS TRABAJADOS'] > 0]['POZO'].unique()
        
        # Obtener las corridas de pozos que estuvieron activos en algún momento de este mes
        df_bd_mes_activos = df_bd_mes[
            (df_bd_mes['FECHA_FALLA_NORM'].isna() | (df_bd_mes['FECHA_FALLA_NORM'] >= current_month_ts)) & 
            (df_bd_mes['FECHA_PULL_NORM'].isna() | (df_bd_mes['FECHA_PULL_NORM'] >= current_month_ts))
        ]
        
        # Filtrar pozos activos que tengan RLE < 1500
        pozos_activos_1500 = df_bd_mes_activos[df_bd_mes_activos['RUN_LIFE_EFECTIVO'] < 1500]['POZO'].unique()
        
        # La base es la intersección de pozos ON y pozos con RLE < 1500
        pozos_on_1500 = len(set(pozos_on_names) & set(pozos_activos_1500))
        
        df_bd_mes_1500 = df_bd_mes[df_bd_mes['RUN_LIFE_EFECTIVO'] < 1500]
        
        fallas_totales_1500 = df_bd_mes_1500[
            (df_bd_mes_1500['FECHA_FALLA_NORM'] >= current_month_ts) & 
            (df_bd_mes_1500['FECHA_FALLA_NORM'] <= fecha_fin_mes)
        ].shape[0]
        
        fallas_als_1500 = df_bd_mes_1500[
            (df_bd_mes_1500['FECHA_FALLA_NORM'] >= current_month_ts) & 
            (df_bd_mes_1500['FECHA_FALLA_NORM'] <= fecha_fin_mes) &
            (df_bd_mes_1500['INDICADOR_MTBF'] == 1)
        ].shape[0]
        
        monthly_data.append({
            'Mes': current_month_date.strftime('%Y-%m'),
            'Fallas Totales': fallas_totales_mes,
            'Fallas ALS': fallas_als_mes,
            'Pozos Operativos': pozos_operativos_mes,
            'Pozos ON': pozos_on,
            'Fallas_1500': fallas_totales_1500,
            'Fallas_ALS_1500': fallas_als_1500,
            'Pozos_ON_1500': pozos_on_1500
        })

        current_month_date = (pd.to_datetime(current_month_date) + pd.offsets.MonthBegin(1)).normalize()

    df_mensual = pd.DataFrame(monthly_data)
    df_mensual.sort_values(by='Mes', ascending=True, inplace=True)
    
    # 1. CÁLCULO DE ÍNDICES MENSUALES
    df_mensual['Indice de Falla ON'] = (df_mensual['Fallas Totales'] / df_mensual['Pozos ON']).replace([np.inf, -np.inf], np.nan).fillna(0)
    df_mensual['Indice de Falla ALS ON'] = (df_mensual['Fallas ALS'] / df_mensual['Pozos ON']).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # --- 2. CÁLCULO DE ÍNDICES ANUALES MÓVILES (ROLLING) PARA LA GRÁFICA ---
    # Si el rango seleccionado tiene menos de 12 meses, ajustamos WINDOW_SIZE a los meses disponibles
    num_meses_rango = len(df_mensual)
    WINDOW_SIZE = min(12, max(1, num_meses_rango))
    
    # Sumas de Fallas
    df_mensual['Fallas_Totales_Rolling'] = df_mensual['Fallas Totales'].rolling(window=WINDOW_SIZE, min_periods=1).sum()
    df_mensual['Fallas_ALS_Rolling'] = df_mensual['Fallas ALS'].rolling(window=WINDOW_SIZE, min_periods=1).sum()
    
    df_mensual['Fallas_1500_Rolling'] = df_mensual['Fallas_1500'].rolling(window=WINDOW_SIZE, min_periods=1).sum()
    df_mensual['Fallas_ALS_1500_Rolling'] = df_mensual['Fallas_ALS_1500'].rolling(window=WINDOW_SIZE, min_periods=1).sum()
    
    # Promedios de Pozos
    df_mensual['Pozos_ON_Rolling_Avg'] = df_mensual['Pozos ON'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    df_mensual['Pozos_Operativos_Rolling_Avg'] = df_mensual['Pozos Operativos'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    df_mensual['Pozos_ON_1500_Rolling_Avg'] = df_mensual['Pozos_ON_1500'].rolling(window=WINDOW_SIZE, min_periods=1).mean()

    # Cálculo de los Índices Rolling
    df_mensual['Indice_Falla_Rolling_ON'] = (
        df_mensual['Fallas_Totales_Rolling'] / df_mensual['Pozos_ON_Rolling_Avg']
    ).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    df_mensual['Indice_Falla_Rolling_ALS_ON'] = (
        df_mensual['Fallas_ALS_Rolling'] / df_mensual['Pozos_ON_Rolling_Avg']
    ).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    df_mensual['Indice_Falla_Rolling_Total'] = (
        df_mensual['Fallas_Totales_Rolling'] / df_mensual['Pozos_Operativos_Rolling_Avg']
    ).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    df_mensual['Indice_Falla_Rolling_ALS_Total'] = (
        df_mensual['Fallas_ALS_Rolling'] / df_mensual['Pozos_Operativos_Rolling_Avg']
    ).replace([np.inf, -np.inf], np.nan).fillna(0)

    df_mensual['Indice_Falla_Rolling_ON_1500'] = (
        df_mensual['Fallas_1500_Rolling'] / df_mensual['Pozos_ON_1500_Rolling_Avg']
    ).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    df_mensual['Indice_Falla_Rolling_ALS_ON_1500'] = (
        df_mensual['Fallas_ALS_1500_Rolling'] / df_mensual['Pozos_ON_1500_Rolling_Avg']
    ).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Filter the final monthly dataframe to only contain the requested date range for the chart/output
    df_mensual = df_mensual[df_mensual['Mes'] >= start_date.strftime('%Y-%m')].copy()
    
    # --- 3. CÁLCULO DE LA TABLA DE RESUMEN (FINAL) ---
    df_last_12 = df_mensual.tail(12).copy()
    
    total_fallas = df_last_12['Fallas Totales'].sum()
    total_fallas_als = df_last_12['Fallas ALS'].sum()
    promedio_operativos = df_last_12['Pozos Operativos'].mean()
    promedio_on = df_last_12['Pozos ON'].mean()
    
    total_fallas_1500 = df_last_12['Fallas_1500'].sum()
    total_fallas_als_1500 = df_last_12['Fallas_ALS_1500'].sum()
    promedio_on_1500 = df_last_12['Pozos_ON_1500'].mean()
    
    indice_falla_total = (total_fallas / promedio_operativos) if promedio_operativos > 0 else 0
    indice_falla_als = (total_fallas_als / promedio_operativos) if promedio_operativos > 0 else 0
    indice_falla_on = (total_fallas / promedio_on) if promedio_on > 0 else 0
    indice_falla_als_on = (total_fallas_als / promedio_on) if promedio_on > 0 else 0
    
    indice_falla_on_1500 = (total_fallas_1500 / promedio_on_1500) if promedio_on_1500 > 0 else 0
    indice_falla_als_on_1500 = (total_fallas_als_1500 / promedio_on_1500) if promedio_on_1500 > 0 else 0
    
    resumen_calculo = pd.DataFrame({
        'Indicador': [
            'Índice de Falla Total', 
            'Índice de Falla ALS', 
            'Índice de Falla ON', 
            'Índice de Falla ALS ON',
            'Índice de Falla ON RLE < 1500',
            'Índice de Falla ALS ON RLE < 1500'
        ],
        'Valor': [
            f'{indice_falla_total:.2%}', 
            f'{indice_falla_als:.2%}', 
            f'{indice_falla_on:.2%}', 
            f'{indice_falla_als_on:.2%}',
            f'{indice_falla_on_1500:.2%}',
            f'{indice_falla_als_on_1500:.2%}'
        ],
        'Base': [
            int(promedio_operativos), 
            int(promedio_operativos), 
            int(promedio_on), 
            int(promedio_on),
            int(promedio_on_1500) if pd.notna(promedio_on_1500) else 0,
            int(promedio_on_1500) if pd.notna(promedio_on_1500) else 0
        ],
        'Fallas': [
            total_fallas, 
            total_fallas_als, 
            total_fallas, 
            total_fallas_als,
            total_fallas_1500,
            total_fallas_als_1500
        ]
    })

    return resumen_calculo, df_mensual