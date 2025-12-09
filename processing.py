"""
Módulo de procesamiento compartido para las aplicaciones de indicadores.
Contiene funciones comunes para cálculos iniciales de datos.
"""

import pandas as pd
import numpy as np
from datetime import timedelta


def perform_initial_calculations(df_forma9, df_bd, fecha_evaluacion):
    """
    Realiza los cálculos iniciales en BD y luego en FORMA 9 de manera vectorizada y eficiente,
    basado en una fecha de evaluación.
    
    Args:
        df_forma9: DataFrame de FORMA9
        df_bd: DataFrame de BD
        fecha_evaluacion: Fecha de evaluación
        
    Returns:
        Tuple[DataFrame, DataFrame]: (df_forma9_processed, df_bd_processed)
    """
    # Si no se pasa fecha_evaluacion, preferir la máxima FECHA_FORMA9 disponible
    if fecha_evaluacion is None:
        try:
            if df_forma9 is not None and 'FECHA_FORMA9' in df_forma9.columns:
                tmp_dates = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
                if not tmp_dates.dropna().empty:
                    fecha_evaluacion = tmp_dates.max()
        except Exception:
            fecha_evaluacion = None

    fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
    
    # Calcular RUN LIFE
    df_bd['RUN LIFE'] = np.where(
        df_bd['FECHA_FALLA'].notna(),
        (df_bd['FECHA_FALLA'] - df_bd['FECHA_RUN']).dt.days,
        np.where(
            df_bd['FECHA_PULL'].notna(),
            (df_bd['FECHA_PULL'] - df_bd['FECHA_RUN']).dt.days,
            np.where(
                df_bd['FECHA_PULL'].isna(),
                (fecha_evaluacion - df_bd['FECHA_RUN']).dt.days,
                np.nan
            )
        )
    )

    df_bd['NICK'] = df_bd['POZO'].astype(str) + '-' + df_bd['RUN'].astype(str)
    
    df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'])
    
    df_forma9_copy = df_forma9.copy()
    
    df_bd_filtered = df_bd[df_bd['FECHA_RUN'] <= fecha_evaluacion].copy()

    merged_df = pd.merge(df_forma9_copy.reset_index(), df_bd_filtered[['POZO', 'RUN', 'PROVEEDOR', 'FECHA_RUN', 'FECHA_PULL']], on='POZO', how='left')
    
    merged_df['is_match'] = (merged_df['FECHA_FORMA9'] >= merged_df['FECHA_RUN']) & \
                             (merged_df['FECHA_FORMA9'] < merged_df['FECHA_PULL'].fillna(pd.to_datetime(fecha_evaluacion)))
    
    best_matches_idx = merged_df[merged_df['is_match']].groupby('index')['FECHA_RUN'].idxmax()
    
    best_matches_df = merged_df.loc[best_matches_idx]
    
    df_forma9_copy['RUN'] = best_matches_df.set_index('index')['RUN']
    df_forma9_copy['PROVEEDOR'] = best_matches_df.set_index('index')['PROVEEDOR']
    
    df_forma9_copy[['RUN', 'PROVEEDOR']] = df_forma9_copy[['RUN', 'PROVEEDOR']].fillna('NO DATA✍️')

    df_forma9_copy['NICK'] = df_forma9_copy['POZO'].astype(str) + '-' + df_forma9_copy['RUN'].astype(str)

    return df_forma9_copy, df_bd
