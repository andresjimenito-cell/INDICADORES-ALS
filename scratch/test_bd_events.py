import pickle
import pandas as pd
import numpy as np

d = pickle.load(open('cache_data/last_run_data.pkl', 'rb'))
df_bd = d['df_bd']

print("Total rows:", len(df_bd))
print("FECHA_FALLA notna:", df_bd['FECHA_FALLA'].notna().sum())
print("FECHA_PULL notna:", df_bd['FECHA_PULL'].notna().sum())
print("OPERANDO_ESTADO value_counts:\n", df_bd['OPERANDO_ESTADO'].value_counts(dropna=False))
if 'SUB TIPO DE FALLA' in df_bd.columns:
    print("SUB TIPO DE FALLA value_counts:\n", df_bd['SUB TIPO DE FALLA'].value_counts(dropna=False).head(10))

# Let's inspect rows
print(df_bd[['POZO', 'RUN', 'ALS', 'FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL', 'RUN LIFE']].head(20))
