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
        
        # Calculate with RUN LIFE (default)
        mtbf_val, _ = calcular_mtbf(df_als, fecha_evaluacion)
        # Calculate with RUN LIFE FALLA
        mtbf_falla, _ = calcular_mtbf(df_als, fecha_evaluacion, col_life='RUN LIFE FALLA')
        
        print(f"ALS: {als_str} | Rows: {len(df_als)} | Failures (INDICADOR_MTBF=1): {df_als[df_als['INDICADOR_MTBF']==1].shape[0]}")
        print(f"  MTBF (col_life=default): {mtbf_val:.2f}")
        print(f"  MTBF (col_life=RUN LIFE FALLA): {mtbf_falla:.2f}")
else:
    print("No cache")
