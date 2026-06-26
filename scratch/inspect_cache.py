import pickle
import pandas as pd

try:
    with open('cache_data/last_run_data.pkl', 'rb') as f:
        data = pickle.load(f)
    df_bd = data['df_bd']
    print("Total rows in df_bd:", len(df_bd))
    print("Non-null FECHA_FALLA:", df_bd['FECHA_FALLA'].notna().sum())
    print("Sample FECHA_FALLA:", df_bd['FECHA_FALLA'].dropna().head(10).tolist())
    print("Unique POZO with non-null FECHA_FALLA:", df_bd[df_bd['FECHA_FALLA'].notna()]['POZO'].nunique())
    print("Types of FECHA_FALLA:", df_bd['FECHA_FALLA'].apply(type).value_counts())
except Exception as e:
    print("Error:", e)
