import sys
import os
import pickle
import pandas as pd

sys.path.append(os.getcwd())
from config import CACHE_FILE
from mtbf import calcular_mtbf

if CACHE_FILE.exists():
    with open(CACHE_FILE, 'rb') as f:
        data = pickle.load(f)
    df_bd = data['df_bd']
    fecha_evaluacion = data['fecha_evaluacion']
    
    for als in df_bd['ALS'].dropna().unique():
        als_str = str(als).strip()
        df_als = df_bd[df_bd['ALS'].astype(str).str.strip() == als_str].copy()
        
        # Only ended runs: FECHA_FALLA is not null or FECHA_PULL is not null
        df_als['FECHA_FALLA_DT'] = pd.to_datetime(df_als['FECHA_FALLA'], errors='coerce')
        df_als['FECHA_PULL_DT'] = pd.to_datetime(df_als['FECHA_PULL'], errors='coerce')
        df_ended = df_als[df_als['FECHA_FALLA_DT'].notna() | df_als['FECHA_PULL_DT'].notna()].copy()
        
        mtbf_ended, _ = calcular_mtbf(df_ended, fecha_evaluacion)
        print(f"ALS: {als_str} | Ended Rows: {len(df_ended)} | Failures (INDICADOR_MTBF=1): {df_ended[df_ended['INDICADOR_MTBF']==1].shape[0]}")
        print(f"  MTBF (Ended only): {mtbf_ended:.2f}")
else:
    print("No cache")
