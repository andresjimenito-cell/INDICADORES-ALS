import sys
import os
import pickle
import pandas as pd

sys.path.append(os.getcwd())
from config import CACHE_FILE

if CACHE_FILE.exists():
    with open(CACHE_FILE, 'rb') as f:
        data = pickle.load(f)
    df_bd = data['df_bd']
    fecha_evaluacion = data['fecha_evaluacion']
    
    df_esp = df_bd[df_bd['ALS'].astype(str).str.strip() == 'ESP'].copy()
    df_esp['FECHA_RUN'] = pd.to_datetime(df_esp['FECHA_RUN'], errors='coerce')
    df_esp['FECHA_FALLA'] = pd.to_datetime(df_esp['FECHA_FALLA'], errors='coerce')
    df_esp['FECHA_PULL'] = pd.to_datetime(df_esp['FECHA_PULL'], errors='coerce')
    df_esp = df_esp[df_esp['FECHA_RUN'] <= pd.to_datetime(fecha_evaluacion)]
    
    # 1. Count failures by ALS:
    n_failures_als = df_esp[df_esp['INDICADOR_MTBF'] == 1].shape[0]
    print(f"Failures ALS (INDICADOR_MTBF == 1): {n_failures_als}")
    
    # 2. Filter ended runs
    df_ended = df_esp[df_esp['FECHA_FALLA'].notna() | df_esp['FECHA_PULL'].notna()]
    sum_life_ended = df_ended['RUN LIFE'].sum()
    print(f"Sum RUN LIFE (ended): {sum_life_ended}")
    print(f"Sum / Failures: {sum_life_ended / n_failures_als:.2f}")
    
    # 3. Filter ended runs where FECHA_FALLA is not null
    df_failed = df_esp[df_esp['FECHA_FALLA'].notna()]
    sum_life_failed = df_failed['RUN LIFE'].sum()
    print(f"Sum RUN LIFE (failed): {sum_life_failed}")
    print(f"Sum / Failures: {sum_life_failed / n_failures_als:.2f}")
    
    # 4. What about using RUN LIFE FALLA?
    sum_life_falla_failed = df_failed['RUN LIFE FALLA'].sum()
    print(f"Sum RUN LIFE FALLA (failed): {sum_life_falla_failed}")
    print(f"Sum / Failures: {sum_life_falla_failed / n_failures_als:.2f}")
    
    # 5. Let's look at the actual values of MTBF computed by Kaplan-Meier for ended runs
    # with col_life = 'RUN LIFE'
    from mtbf import calcular_mtbf
    val_mtbf_ended, _ = calcular_mtbf(df_ended, fecha_evaluacion)
    print(f"KM MTBF of ended runs (col_life=default): {val_mtbf_ended:.2f}")
    
    val_mtbf_ended_falla, _ = calcular_mtbf(df_ended, fecha_evaluacion, col_life='RUN LIFE FALLA')
    print(f"KM MTBF of ended runs (col_life=RUN LIFE FALLA): {val_mtbf_ended_falla:.2f}")
    
    # What about KM MTBF of failed-only runs?
    val_mtbf_failed, _ = calcular_mtbf(df_failed, fecha_evaluacion)
    print(f"KM MTBF of failed-only runs (col_life=default): {val_mtbf_failed:.2f}")
    
    # What if the user wants MTBF to be computed using the KM formula but censoring is based on whether it failed by ALS?
    # Wait, in the KM formula:
    # "R(ti/Ti-1): si INDICADOR_MTBF==1 usar fórmula, si no, poner 1"
    # This means INDICADOR_MTBF==1 is the EVENT (failure).
    # If a well is active or failed for other reasons, it is censored (R(ti/Ti-1) = 1).
    # Wait! If we do NOT include active wells in the KM calculation, i.e., we only use df_ended (completed runs),
    # then the MTBF is 2316 days.
    # If we only use df_failed (failed runs, either by ALS or other reasons), then the MTBF is 1761 days.
