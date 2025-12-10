import pandas as pd
import numpy as np
from theme import get_colors, get_plotly_layout

_colors = get_colors()
COLOR_PRINCIPAL = _colors.get('primary', '#00ff99')
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = _bg_raw or '#1a1a2e'
get_color_sequence = _colors.get('color_sequence', lambda mode=None: [COLOR_PRINCIPAL, '#00cfff', '#FFDE31', '#5AFFDA'])
get_plotly_layout = get_plotly_layout
from datetime import timedelta

def calcular_indice_falla_anual(df_bd, df_forma9, fecha_evaluacion):
    """
    Calcula los índices de falla para los últimos 3 años (36 meses),
    incluyendo el cálculo de 12 meses rodante (rolling) para la gráfica, 
    y el resumen final.
    """
    end_date = pd.to_datetime(fecha_evaluacion).date()
    start_date = end_date - timedelta(days=365 * 12)
    
    # Asegurar que las columnas de fecha son datetime
    df_bd['FECHA_RUN'] = pd.to_datetime(df_bd['FECHA_RUN'])
    df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd['FECHA_FALLA'])
    df_bd['FECHA_PULL'] = pd.to_datetime(df_bd['FECHA_PULL'])
    
    df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'])
    
    monthly_data = []
    current_month_date = start_date.replace(day=1)
    
    while current_month_date <= end_date:
        fecha_fin_mes = (pd.to_datetime(current_month_date) + pd.offsets.MonthEnd(0)).date()
        
        # Filtrar df_bd hasta el final del mes para calcular activos y fallas
        df_bd_mes = df_bd[
            (df_bd['FECHA_RUN'].dt.date <= fecha_fin_mes)
        ].copy()
        
        # Filtrar df_forma9 para el mes actual
        df_forma9_mes = df_forma9[
            (df_forma9['FECHA_FORMA9'].dt.date >= current_month_date) &
            (df_forma9['FECHA_FORMA9'].dt.date <= fecha_fin_mes)
        ].copy()
        
        pozos_operativos_mes = df_bd_mes[
            (df_bd_mes['FECHA_FALLA'].isna() | (df_bd_mes['FECHA_FALLA'].dt.date > fecha_fin_mes)) & 
            (df_bd_mes['FECHA_PULL'].isna() | (df_bd_mes['FECHA_PULL'].dt.date > fecha_fin_mes))
        ]['POZO'].nunique()

        pozos_on = df_forma9_mes[df_forma9_mes['DIAS TRABAJADOS'] > 0]['POZO'].nunique()

        fallas_totales_mes = df_bd_mes[
            (df_bd_mes['FECHA_FALLA'].dt.date >= current_month_date) & 
            (df_bd_mes['FECHA_FALLA'].dt.date <= fecha_fin_mes)
        ].shape[0]
        
        fallas_als_mes = df_bd_mes[
            (df_bd_mes['FECHA_FALLA'].dt.date >= current_month_date) & 
            (df_bd_mes['FECHA_FALLA'].dt.date <= fecha_fin_mes) &
            (df_bd_mes['INDICADOR_MTBF'] == 1)
        ].shape[0]
        
        monthly_data.append({
            'Mes': current_month_date.strftime('%Y-%m'),
            'Fallas Totales': fallas_totales_mes,
            'Fallas ALS': fallas_als_mes,
            'Pozos Operativos': pozos_operativos_mes,
            'Pozos ON': pozos_on
        })

        current_month_date = (pd.to_datetime(current_month_date) + pd.offsets.MonthBegin(1)).date()

    df_mensual = pd.DataFrame(monthly_data)
    df_mensual.sort_values(by='Mes', ascending=True, inplace=True)
    
    # 1. CÁLCULO DE ÍNDICES MENSUALES (Se mantiene para referencia, pero se IGNORARÁ en el gráfico)
    df_mensual['Indice de Falla ON'] = (df_mensual['Fallas Totales'] / df_mensual['Pozos ON']).replace([np.inf, -np.inf], np.nan).fillna(0)
    df_mensual['Indice de Falla ALS ON'] = (df_mensual['Fallas ALS'] / df_mensual['Pozos ON']).replace([np.inf, -np.inf], np.nan).fillna(0)
    
    
    # --- 2. CÁLCULO DE ÍNDICES ANUALES MÓVILES (ROLLING 12-MONTH) PARA LA GRÁFICA ---
    WINDOW_SIZE = 12
    
    # Suma de Fallas en los últimos 12 meses
    df_mensual['Fallas_Totales_Rolling'] = df_mensual['Fallas Totales'].rolling(window=WINDOW_SIZE, min_periods=WINDOW_SIZE).sum()
    df_mensual['Fallas_ALS_Rolling'] = df_mensual['Fallas ALS'].rolling(window=WINDOW_SIZE, min_periods=WINDOW_SIZE).sum()
    
    # Promedio de Pozos ON en los últimos 12 meses (la base)
    df_mensual['Pozos_ON_Rolling_Avg'] = df_mensual['Pozos ON'].rolling(window=WINDOW_SIZE, min_periods=WINDOW_SIZE).mean()
    df_mensual['Pozos_Operativos_Rolling_Avg'] = df_mensual['Pozos Operativos'].rolling(window=WINDOW_SIZE, min_periods=WINDOW_SIZE).mean()

    # Cálculo de los Índices Rolling (Estos deben usarse en la gráfica)
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
    
    # --- 3. CÁLCULO DE LA TABLA DE RESUMEN (FINAL) ---
    # Se usa la misma lógica que antes, usando tail(12) que es el último punto del rolling.
    df_last_12 = df_mensual.tail(12).copy()
    
    total_fallas = df_last_12['Fallas Totales'].sum()
    total_fallas_als = df_last_12['Fallas ALS'].sum()
    promedio_operativos = df_last_12['Pozos Operativos'].mean()
    promedio_on = df_last_12['Pozos ON'].mean()
    
    indice_falla_total = (total_fallas / promedio_operativos) if promedio_operativos > 0 else 0
    indice_falla_als = (total_fallas_als / promedio_operativos) if promedio_operativos > 0 else 0
    indice_falla_on = (total_fallas / promedio_on) if promedio_on > 0 else 0
    indice_falla_als_on = (total_fallas_als / promedio_on) if promedio_on > 0 else 0
    
    resumen_calculo = pd.DataFrame({
        'Indicador': [
            'Índice de Falla Total', 
            'Índice de Falla ALS', 
            'Índice de Falla ON', 
            'Índice de Falla ALS ON'
        ],
        'Valor': [
            f'{indice_falla_total:.2%}', 
            f'{indice_falla_als:.2%}', 
            f'{indice_falla_on:.2%}', 
            f'{indice_falla_als_on:.2%}'
        ],
        'Base': [
            int(promedio_operativos), 
            int(promedio_operativos), 
            int(promedio_on), 
            int(promedio_on)
        ],
        'Fallas': [
            total_fallas, 
            total_fallas_als, 
            total_fallas, 
            total_fallas_als
        ]
    })

    # Asegúrate de usar estas columnas en tu función de gráfico:
    # - Indice_Falla_Rolling_ON
    # - Indice_Falla_Rolling_ALS_ON
    return resumen_calculo, df_mensual