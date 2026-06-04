import sys
import os
import pickle
import pandas as pd
import numpy as np

sys.path.append(os.getcwd())
from config import CACHE_FILE

if CACHE_FILE.exists():
    with open(CACHE_FILE, 'rb') as f:
        data = pickle.load(f)
    df_bd = data['df_bd']
    fecha_evaluacion = data['fecha_evaluacion']
    
    # Filter for ESP
    df_esp = df_bd[df_bd['ALS'].astype(str).str.strip() == 'ESP'].copy()
    
    # Clean/parse dates and filter as done in calcular_mtbf
    df_esp['FECHA_RUN'] = pd.to_datetime(df_esp['FECHA_RUN'], errors='coerce')
    df_esp['FECHA_FALLA'] = pd.to_datetime(df_esp['FECHA_FALLA'], errors='coerce')
    df_esp = df_esp[df_esp['FECHA_RUN'] <= pd.to_datetime(fecha_evaluacion)]
    
    print(f"Total rows for ESP: {len(df_esp)}")
    print(f"INDICADOR_MTBF value counts:")
    print(df_esp['INDICADOR_MTBF'].value_counts(dropna=False))
    
    for col_life in ['RUN LIFE', 'RUN LIFE FALLA']:
        if col_life not in df_esp.columns:
            print(f"\nColumn {col_life} not found.")
            continue
            
        print(f"\n--- Analizando con columna: {col_life} ---")
        df_c = df_esp[df_esp[col_life].notna()].copy()
        print(f"Rows with notna life: {len(df_c)}")
        
        # 1. Formula actual en mtbf.py
        df_c = df_c.sort_values(col_life).reset_index(drop=True)
        n = len(df_c)
        df_c['ITEM'] = range(1, n+1)
        df_c['R(ti/Ti-1)'] = df_c.apply(lambda row: (n + 1 - row['ITEM']) / (n + 2 - row['ITEM']) if row['INDICADOR_MTBF'] == 1 else 1, axis=1)
        r_ti = []
        current_rti = 1.0
        for val in df_c['R(ti/Ti-1)']:
            current_rti *= val
            r_ti.append(current_rti)
        df_c['R(Ti)'] = r_ti
        dt = df_c[col_life].values
        rti_dt = []
        for i, r in enumerate(df_c['R(Ti)']):
            if i == 0:
                rti_dt.append(r * (dt[i] - 0))
            else:
                rti_dt.append(r * (dt[i] - dt[i-1]))
        df_c['R(Ti)*dt'] = rti_dt
        mtbf_actual = df_c['R(Ti)*dt'].sum()
        print(f"MTBF (Formula Actual): {mtbf_actual:.2f}")
        
        # 2. ¿Qué pasa si filtramos a INDICADOR_MTBF == 1 y aplicamos la misma formula?
        df_f = df_esp[df_esp[col_life].notna() & (df_esp['INDICADOR_MTBF'] == 1)].copy()
        df_f = df_f.sort_values(col_life).reset_index(drop=True)
        n_f = len(df_f)
        df_f['ITEM'] = range(1, n_f+1)
        df_f['R(ti/Ti-1)'] = df_f.apply(lambda row: (n_f + 1 - row['ITEM']) / (n_f + 2 - row['ITEM']), axis=1)
        r_ti_f = []
        current_rti_f = 1.0
        for val in df_f['R(ti/Ti-1)']:
            current_rti_f *= val
            r_ti_f.append(current_rti_f)
        df_f['R(Ti)'] = r_ti_f
        dt_f = df_f[col_life].values
        rti_dt_f = []
        for i, r in enumerate(df_f['R(Ti)']):
            if i == 0:
                rti_dt_f.append(r * (dt_f[i] - 0))
            else:
                rti_dt_f.append(r * (dt_f[i] - dt_f[i-1]))
        df_f['R(Ti)*dt'] = rti_dt_f
        mtbf_f = df_f['R(Ti)*dt'].sum()
        print(f"MTBF (Filtrando INDICADOR_MTBF == 1 + formula): {mtbf_f:.2f}")
        
        # 3. Simple Promedio de RUN LIFE de fallas
        avg_life_f = df_esp[df_esp[col_life].notna() & (df_esp['INDICADOR_MTBF'] == 1)][col_life].mean()
        print(f"Promedio simple de RUN LIFE de fallas (INDICADOR_MTBF == 1): {avg_life_f:.2f}")
        
        # 4. Standard MTBF = Sum(RUN LIFE) / Count(Failures)
        sum_life = df_esp[df_esp[col_life].notna()][col_life].sum()
        count_failures = df_esp[df_esp['INDICADOR_MTBF'] == 1].shape[0]
        if count_failures > 0:
            std_mtbf = sum_life / count_failures
            print(f"MTBF Standard (Sum RUN LIFE / Count failures): {std_mtbf:.2f}")
        else:
            print("No failures")
            
        # 5. Formula de Kaplan Meier corregida (ej. n en lugar de n+1 / n+2)
        # R(ti/Ti-1) = (n - item) / (n - item + 1)
        df_km = df_esp[df_esp[col_life].notna()].copy()
        df_km = df_km.sort_values(col_life).reset_index(drop=True)
        n_km = len(df_km)
        df_km['ITEM'] = range(1, n_km+1)
        df_km['R(ti/Ti-1)'] = df_km.apply(lambda row: (n_km - row['ITEM']) / (n_km - row['ITEM'] + 1) if row['INDICADOR_MTBF'] == 1 else 1, axis=1)
        r_ti_km = []
        current_rti_km = 1.0
        for val in df_km['R(ti/Ti-1)']:
            current_rti_km *= val
            r_ti_km.append(current_rti_km)
        df_km['R(Ti)'] = r_ti_km
        dt_km = df_km[col_life].values
        rti_dt_km = []
        for i, r in enumerate(df_km['R(Ti)']):
            if i == 0:
                rti_dt_km.append(r * (dt_km[i] - 0))
            else:
                rti_dt_km.append(r * (dt_km[i] - dt_km[i-1]))
        df_km['R(Ti)*dt'] = rti_dt_km
        mtbf_km = df_km['R(Ti)*dt'].sum()
        print(f"MTBF (Formula KM estandar): {mtbf_km:.2f}")
        
else:
    print("Cache file does not exist")
