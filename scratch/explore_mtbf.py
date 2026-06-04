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
    
    # Filter for ESP
    df_esp = df_bd[df_bd['ALS'].astype(str).str.strip() == 'ESP'].copy()
    
    df_esp['FECHA_RUN'] = pd.to_datetime(df_esp['FECHA_RUN'], errors='coerce')
    df_esp['FECHA_FALLA'] = pd.to_datetime(df_esp['FECHA_FALLA'], errors='coerce')
    df_esp = df_esp[df_esp['FECHA_RUN'] <= pd.to_datetime(fecha_evaluacion)]
    
    print("ESP STATS:")
    print(f"Total rows: {len(df_esp)}")
    print(f"INDICADOR_MTBF == 1: {len(df_esp[df_esp['INDICADOR_MTBF'] == 1])}")
    print(f"INDICADOR_MTBF == 0: {len(df_esp[df_esp['INDICADOR_MTBF'] == 0])}")
    
    print("\nMean of RUN LIFE:")
    print(df_esp.groupby('INDICADOR_MTBF')['RUN LIFE'].mean())
    print("\nMean of RUN LIFE FALLA:")
    print(df_esp.groupby('INDICADOR_MTBF')['RUN LIFE FALLA'].mean())
    print("\nMean of RUN_LIFE_EFECTIVO:")
    print(df_esp.groupby('INDICADOR_MTBF')['RUN_LIFE_EFECTIVO'].mean())
    
    print("\nSum of RUN LIFE:")
    print(df_esp.groupby('INDICADOR_MTBF')['RUN LIFE'].sum())
    
    print("\nSum of RUN_LIFE_EFECTIVO:")
    print(df_esp.groupby('INDICADOR_MTBF')['RUN_LIFE_EFECTIVO'].sum())
    
    # Let's test: Sum of RUN LIFE of failed wells / count of failures
    print("\nSum of RUN LIFE for failures / count of failures:")
    print(df_esp[df_esp['INDICADOR_MTBF'] == 1]['RUN LIFE'].sum() / len(df_esp[df_esp['INDICADOR_MTBF'] == 1]))
    
    # Let's test: Sum of RUN LIFE for all wells / count of failures
    print("\nSum of RUN LIFE for all ESP / count of failures:")
    print(df_esp['RUN LIFE'].sum() / len(df_esp[df_esp['INDICADOR_MTBF'] == 1]))
    
    # What if the denominator is NOT INDICADOR_MTBF == 1, but something else?
    # What if the user calculates MTBF by: sum(RUN LIFE) / sum(INDICADOR_MTBF)?
    # Wait, sum(RUN LIFE) of all wells / count of failures. But earlier we got 6355 days.
    # What if we only filter by: the wells that have actually failed (e.g. have FECHA_FALLA or FECHA_PULL or OPERANDO_ESTADO is not active)?
    print("\nValue counts of OPERANDO_ESTADO:")
    print(df_esp['OPERANDO_ESTADO'].value_counts(dropna=False))
    
    # What if we only sum run life of wells that are NOT active?
    df_not_active = df_esp[df_esp['OPERANDO_ESTADO'].astype(str).str.upper().str.strip() != 'SI']
    print(f"\nNon-active ESP wells count: {len(df_not_active)}")
    print(f"Sum of RUN LIFE for non-active: {df_not_active['RUN LIFE'].sum()}")
    print(f"MTBF (Sum of RUN LIFE of non-active / failures): {df_not_active['RUN LIFE'].sum() / len(df_esp[df_esp['INDICADOR_MTBF'] == 1])}")
    
    # What if we filter to only those where FECHA_FALLA is not null?
    df_failed = df_esp[df_esp['FECHA_FALLA'].notna()]
    print(f"\nFailed ESP wells (FECHA_FALLA not na) count: {len(df_failed)}")
    print(f"Sum of RUN LIFE of failed: {df_failed['RUN LIFE'].sum()}")
    print(f"MTBF (Sum of RUN LIFE of failed / failures): {df_failed['RUN LIFE'].sum() / len(df_esp[df_esp['INDICADOR_MTBF'] == 1])}")
    
    # Let's check: Average of RUN LIFE of failed wells
    print(f"Average RUN LIFE of failed wells: {df_failed['RUN LIFE'].mean()}")
    
    # Wait, what if we use: Sum of RUN_LIFE_EFECTIVO of failed wells?
    print(f"Average RUN_LIFE_EFECTIVO of failed wells: {df_failed['RUN_LIFE_EFECTIVO'].mean()}")
    
    # Wait! What if the Kaplan-Meier-like formula has a bug?
    # Let's check the formula again.
    # df['R(ti/Ti-1)'] = df.apply(lambda row: (n + 1 - row['ITEM']) / (n + 2 - row['ITEM']) if row[col_indicador] == 1 else 1, axis=1)
    # Wait! In Spanish: "EL CALULO SE HACE CON -INDICADOR MTBF = 1 OSEA QUE SIGNIFICA QUE FALLO POR ALS"
    # Wait! Is it possible that row[col_indicador] == 1 means it FAILED, so we use the fraction, BUT if it is 0 (censored), we use 1?
    # Yes, that's what the code does: `if row[col_indicador] == 1 else 1`.
    # Wait! If the user says:
    # "RECUERDA QUE EL CALULO SE HACE CON -INDICADOR MTBF = 1 OSEA QUE SIGNIFICA QUE FALLO POR ALS , ESQUE ESTA DANDO VALORES ADSURDOS DE 4000 Y ASI CUANDO REALMENTE ES DE 2100 Y POR EL ESTILO"
    # Wait, let's look at standard MTBF (Kaplan-Meier):
    # In standard Kaplan-Meier, the formula is:
    # MTBF = sum( R(t_i) * dt_i )
    # But wait, is there an alternative formula that does:
    # MTBF = Sum(RUN LIFE) / Sum(INDICADOR_MTBF == 1) ?
    # But for ESP, Sum(RUN LIFE) / Sum(INDICADOR_MTBF == 1) is 6357.29 days!
    # Wait, why is it 6357.29 days?
    # Because 2,265 rows have a lot of active runs with very long run lives.
    # What if the user calculates:
    # Sum(RUN LIFE @ FALLA) / Sum(INDICADOR_MTBF == 1)?
    # Wait, is the column "RUN LIFE FALLA" only populated when there is a failure?
    # Let's print the sum of "RUN LIFE FALLA" and see!
    print("\nSum of RUN LIFE FALLA for all ESP:")
    print(df_esp['RUN LIFE FALLA'].sum())
    print("Count of INDICADOR_MTBF == 1 in ESP:")
    print(df_esp[df_esp['INDICADOR_MTBF'] == 1].shape[0])
    print("MTBF = Sum(RUN LIFE FALLA) / Sum(INDICADOR_MTBF == 1):")
    print(df_esp['RUN LIFE FALLA'].sum() / df_esp[df_esp['INDICADOR_MTBF'] == 1].shape[0])
    
    print("\nMTBF = Sum(RUN LIFE FALLA for INDICADOR_MTBF == 1) / Count(INDICADOR_MTBF == 1):")
    print(df_esp[df_esp['INDICADOR_MTBF'] == 1]['RUN LIFE FALLA'].sum() / df_esp[df_esp['INDICADOR_MTBF'] == 1].shape[0])

else:
    print("No cache")
