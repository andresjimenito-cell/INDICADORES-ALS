import sys
import os
import pickle
import pandas as pd

sys.path.append(os.getcwd())
from config import CACHE_FILE

def calcular_mtbf_custom(df, col_life='RUN LIFE', col_indicador='INDICADOR_MTBF'):
    df = df[df[col_life].notna()].copy()
    df = df.sort_values(col_life).reset_index(drop=True)
    n = len(df)
    if n == 0:
        return 0
    df['ITEM'] = range(1, n+1)
    df['R(ti/Ti-1)'] = df.apply(lambda row: (n + 1 - row['ITEM']) / (n + 2 - row['ITEM']) if row[col_indicador] == 1 else 1, axis=1)
    r_ti = []
    current_rti = 1.0
    for val in df['R(ti/Ti-1)']:
        current_rti *= val
        r_ti.append(current_rti)
    df['R(Ti)'] = r_ti
    dt = df[col_life].values
    rti_dt = []
    for i, r in enumerate(df['R(Ti)']):
        if i == 0:
            rti_dt.append(r * (dt[i] - 0))
        else:
            rti_dt.append(r * (dt[i] - dt[i-1]))
    df['R(Ti)*dt'] = rti_dt
    return df['R(Ti)*dt'].sum()

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
    
    print("Total ESP:", len(df_esp))
    
    # Filter 1: Only rows where FECHA_FALLA is not null
    df_failed = df_esp[df_esp['FECHA_FALLA'].notna()]
    print("MTBF (only FECHA_FALLA not null):", calcular_mtbf_custom(df_failed))
    
    # Filter 2: Only rows where FECHA_PULL is not null
    df_pulled = df_esp[df_esp['FECHA_PULL'].notna()]
    print("MTBF (only FECHA_PULL not null):", calcular_mtbf_custom(df_pulled))
    
    # Filter 3: Only rows where FECHA_FALLA is not null OR FECHA_PULL is not null
    df_ended = df_esp[df_esp['FECHA_FALLA'].notna() | df_esp['FECHA_PULL'].notna()]
    print("MTBF (FECHA_FALLA or FECHA_PULL not null):", calcular_mtbf_custom(df_ended))
    
    # Filter 4: Let's check if INDICADOR_MTBF is 1
    # What if the user calculates: Sum(RUN LIFE) of all ESP / sum(INDICADOR_MTBF) but they filter out active wells?
    # Let's check:
    df_inactive = df_esp[df_esp['OPERANDO_ESTADO'].isna() | (df_esp['OPERANDO_ESTADO'] == '')]
    print("MTBF (Sum of RUN LIFE of inactive / count of failures):", df_inactive['RUN LIFE'].sum() / df_esp[df_esp['INDICADOR_MTBF']==1].shape[0])
    
    # Wait, what if the user's formula for MTBF is:
    # MTBF = Sum of RUN LIFE of all wells (active & failed) / count of failures? But that is 6355 days.
    # What if the user filters the rows to: only wells that have failed (FECHA_FALLA not null) and divides by number of ALS failures?
    # That is: Sum(RUN LIFE of df_failed) / count of failures (where INDICADOR_MTBF == 1)
    # df_failed has FECHA_FALLA not null.
    # Sum(RUN LIFE of df_failed) is 1,089,155.
    # failures (where INDICADOR_MTBF == 1) is 548.
    # 1,089,155 / 548 = 1987.5 days.
    # What if we define failures where FECHA_FALLA is not null and INDICADOR_MTBF == 1?
    df_failed_als = df_esp[df_esp['FECHA_FALLA'].notna() & (df_esp['INDICADOR_MTBF'] == 1)]
    print("Count of ESP wells with FECHA_FALLA not null and INDICADOR_MTBF == 1:", len(df_failed_als))
    print("MTBF (Sum of RUN LIFE of df_failed / count of df_failed_als):", df_failed['RUN LIFE'].sum() / len(df_failed_als))
    
    # What if we do: Sum of RUN LIFE of all ESP wells / count of df_failed_als?
    print("MTBF (Sum of RUN LIFE of all ESP / count of df_failed_als):", df_esp['RUN LIFE'].sum() / len(df_failed_als))
    
    # Let's check: what if the user's formula is actually:
    # MTBF = Sum of RUN LIFE of all wells where INDICADOR_MTBF == 1 / count of failures?
    # That is the mean of RUN LIFE of failed wells, which is 1095 days.
    
    # Wait! Let's check if the formula in the Excel sheet uses a simpler Kaplan-Meier?
    # Or is there any other file or sheet in the folder?
    # Let's look at the sheet itself!
    # Wait, where is the excel file saved?
    # Let's check saved_uploads.
else:
    print("No cache")
