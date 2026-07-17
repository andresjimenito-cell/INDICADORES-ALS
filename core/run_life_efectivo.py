import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data(show_spinner=False)
def calcular_run_life_efectivo(df_bd, df_forma9, fecha_evaluacion=None):
    """
    Calcula el Run Life Efectivo (tiempo real trabajado acumulado) para cada corrida (RUN).
    Retorna el promedio global y el DataFrame df_bd actualizado con la columna 'RUN_LIFE_EFECTIVO'.
    """
    
    if df_bd is None or df_bd.empty or df_forma9 is None or df_forma9.empty:
        return 0.0, df_bd

    # Copias para no modificar originales fuera de la función inmediatamente
    df_runs = df_bd.copy()
    if 'RUN_LIFE_EFECTIVO' in df_runs.columns:
        df_runs.drop(columns=['RUN_LIFE_EFECTIVO'], inplace=True)
    df_f9 = df_forma9.copy()

    # Convertir fecha de evaluación si es necesario
    if fecha_evaluacion is None:
        fecha_evaluacion = pd.Timestamp.now()
    else:
        fecha_evaluacion = pd.to_datetime(fecha_evaluacion)

    # --- Preprocesamiento de Fechas y Columnas ---
    
    print(f"\n[DEBUG RLE] Iniciando cálculo...")
    print(f"[DEBUG RLE] Tamaño BD: {len(df_runs)}, Forma9: {len(df_f9)}")
    print(f"[DEBUG RLE] Fecha evaluación: {fecha_evaluacion}")
    
    # Verificar que existan columnas necesarias
    if 'POZO' not in df_runs.columns:
        print("[DEBUG RLE] ERROR: Columna POZO no existe en df_bd")
        return 0.0, df_runs
    if 'POZO' not in df_f9.columns:
        print("[DEBUG RLE] ERROR: Columna POZO no existe en df_forma9")
        return 0.0, df_runs
    if 'RUN' not in df_runs.columns:
        print("[DEBUG RLE] ERROR: Columna RUN no existe en df_bd")
        return 0.0, df_runs
        
    # Normalizar POZO para asegurar matches
    df_runs['POZO'] = df_runs['POZO'].astype(str).str.strip().str.upper()
    df_f9['POZO'] = df_f9['POZO'].astype(str).str.strip().str.upper()
    
    print(f"[DEBUG RLE] Pozos únicos BD: {df_runs['POZO'].nunique()}, Forma9: {df_f9['POZO'].nunique()}")
    
    # Asegurar tipos datetime en BD y normalizar
    for col in ['FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL']:
        if col in df_runs.columns:
            df_runs[col] = pd.to_datetime(df_runs[col], errors='coerce').dt.normalize()

    # Buscar columna de fecha en forma9
    fecha_col_f9 = None
    for posible_col in ['FECHA_FORMA9', 'FECHA', 'FECHA FORMA9', 'FECHA_FORMA_9']:
        if posible_col in df_f9.columns:
            fecha_col_f9 = posible_col
            break
    
    if fecha_col_f9 is None:
        print(f"[DEBUG RLE] ERROR: No se encontró columna de fecha en forma9. Cols: {df_f9.columns.tolist()}")
        return 0.0, df_runs
    
    # Renombrar a nombre estándar
    if fecha_col_f9 != 'FECHA_FORMA9':
        df_f9.rename(columns={fecha_col_f9: 'FECHA_FORMA9'}, inplace=True)
    
    df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
    
    # Buscar columna de días trabajados
    dias_col = None
    for posible_col in ['DIAS TRABAJADOS', 'DIAS_TRABAJADOS', 'DIAS TRAB', 'DIAS']:
        if posible_col in df_f9.columns:
            dias_col = posible_col
            break
    
    if dias_col is None:
        print(f"[DEBUG RLE] ERROR: No se encontró columna DIAS TRABAJADOS en forma9. Cols: {df_f9.columns.tolist()}")
        return 0.0, df_runs
    
    # Renombrar a nombre estándar
    if dias_col != 'DIAS TRABAJADOS':
        df_f9.rename(columns={dias_col: 'DIAS TRABAJADOS'}, inplace=True)
    
    df_f9['DIAS TRABAJADOS'] = pd.to_numeric(df_f9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
    
    print(f"[DEBUG RLE] Total dias trabajados en Forma9: {df_f9['DIAS TRABAJADOS'].sum():.2f}")
    
    # --- Calcular Fecha Fin de cada Run ---
    df_runs['FECHA_FIN_CALC'] = fecha_evaluacion.normalize()
    
    mask_pull = df_runs['FECHA_PULL'].notna()
    df_runs.loc[mask_pull, 'FECHA_FIN_CALC'] = df_runs.loc[mask_pull, 'FECHA_PULL']
    
    mask_falla = df_runs['FECHA_FALLA'].notna()
    df_runs.loc[mask_falla, 'FECHA_FIN_CALC'] = df_runs.loc[mask_falla, 'FECHA_FALLA']
    
    # --- Agregación - Método Vectorizado de Alto Rendimiento ---
    # Para evitar bucles Python, realizamos un merge_asof para asociar cada registro diario
    # de df_f9 a una corrida específica de df_runs (FECHA_RUN <= FECHA_FORMA9 <= FECHA_FIN_CALC).
    # Usamos index_bd para identificar las corridas de forma única y evitar colisiones si
    # hay corridas duplicadas o con la misma numeración para el mismo pozo.
    df_runs['index_bd'] = df_runs.index
    df_runs_sorted = df_runs[['index_bd', 'POZO', 'RUN', 'FECHA_RUN', 'FECHA_FIN_CALC']].sort_values('FECHA_RUN')
    
    df_f9_subset = df_f9[['POZO', 'FECHA_FORMA9', 'DIAS TRABAJADOS']].copy()
    df_f9_sorted = df_f9_subset.sort_values('FECHA_FORMA9')
    
    merged_rle = pd.merge_asof(
        df_f9_sorted,
        df_runs_sorted,
        left_on='FECHA_FORMA9',
        right_on='FECHA_RUN',
        by='POZO',
        direction='backward'
    )
    
    # Comprobar que la fecha del registro diario está dentro del rango de vigencia de la corrida
    is_rle_match = (
        merged_rle['FECHA_RUN'].notna() &
        (merged_rle['FECHA_FORMA9'] <= merged_rle['FECHA_FIN_CALC'])
    )
    
    # Agrupar y sumar los días trabajados por index_bd
    grouped_rle = merged_rle[is_rle_match].groupby('index_bd')['DIAS TRABAJADOS'].sum().reset_index()
    
    df_result = pd.merge(
        df_runs,
        grouped_rle,
        on='index_bd',
        how='left'
    )
    
    df_result['RUN_LIFE_EFECTIVO'] = df_result['DIAS TRABAJADOS'].fillna(0.0)
    df_result.drop(columns=['DIAS TRABAJADOS', 'index_bd', 'FECHA_FIN_CALC'], inplace=True, errors='ignore')
    
    # Mantener el mismo index original que df_bd
    df_result.index = df_runs.index
    
    promedio_global = df_result['RUN_LIFE_EFECTIVO'].mean()
    
    # --- Diagnósticos de RLE ---
    print(f"\n=== RESULTADO RUN LIFE EFECTIVO ===")
    print(f"Pozos únicos en BD: {df_runs['POZO'].nunique()}")
    print(f"Pozos únicos en Forma9: {df_f9['POZO'].nunique()}")
    pozos_comun = set(df_runs['POZO'].unique()) & set(df_f9['POZO'].unique())
    print(f"Pozos en común: {len(pozos_comun)}")
    print(f"Total días trabajados en Forma9: {df_f9['DIAS TRABAJADOS'].sum():.2f}")
    print(f"Runs totales: {len(df_result)}")
    print(f"Runs con RLE > 0: {(df_result['RUN_LIFE_EFECTIVO'] > 0).sum()}")
    print(f"RLE Promedio: {promedio_global:.2f} días")
    print(f"===================================\n")
    
    return promedio_global, df_result
