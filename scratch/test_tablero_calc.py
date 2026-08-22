import pickle
import pandas as pd
import numpy as np
import os, sys

sys.path.append(os.path.abspath('core'))
sys.path.append(os.path.abspath('data'))
sys.path.append(os.path.abspath('ui'))
sys.path.append(os.path.abspath('tabs'))

d = pickle.load(open('cache_data/last_run_data.pkl', 'rb'))
df_bd = d['df_bd']
df_forma9 = d['df_forma9']
fecha_eval = pd.to_datetime(d['fecha_evaluacion'])
fecha_eval_date = fecha_eval.normalize()
mes_eval = fecha_eval.month
anio_eval = fecha_eval.year

# 1. Tablero logic
df_resumen = df_bd.copy()
EXCLUIDOS = {
    'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
    'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
    'MAPACHE/PERICO', 'MAPACHE-PERICO',
    'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
    'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
    'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE'
}
for col_filter in ('ACTIVO', 'BLOQUE', 'CAMPO'):
    if col_filter in df_resumen.columns:
        df_resumen = df_resumen[~df_resumen[col_filter].astype(str).str.upper().str.strip().isin(EXCLUIDOS)]

df_resumen = df_resumen[df_resumen['FECHA_RUN'].dt.normalize() <= fecha_eval_date].copy()
df_resumen.loc[df_resumen['FECHA_FALLA'].dt.normalize() > fecha_eval_date, 'FECHA_FALLA'] = pd.NaT

df = df_resumen.copy()
df['_RUN']  = df['FECHA_RUN'].dt.normalize()
df['_FALL'] = df['FECHA_FALLA'].dt.normalize() if 'FECHA_FALLA' in df.columns else pd.Series(pd.NaT, index=df.index)
df['_PULL'] = df['FECHA_PULL'].dt.normalize()  if 'FECHA_PULL'  in df.columns else pd.Series(pd.NaT, index=df.index)

mask_fondo = (df['_RUN'] <= fecha_eval_date) & (df['_PULL'].isna() | (df['_PULL'] > fecha_eval_date))
df_fondo = df[mask_fondo]
als_fondo = df_fondo['POZO'].nunique() if 'POZO' in df_fondo.columns else 0
df_falla = df_fondo[df_fondo['_FALL'].notna() & (df_fondo['_FALL'] <= fecha_eval_date)]
als_fallados = df_falla['POZO'].nunique() if 'POZO' in df_falla.columns else 0
als_operativos = df_fondo[df_fondo['_FALL'].isna() | (df_fondo['_FALL'] > fecha_eval_date)]['POZO'].nunique() if 'POZO' in df_fondo.columns else 0

pozos_en_resumen = df_resumen['POZO'].unique()
df_forma9_untr = df_forma9[df_forma9['POZO'].isin(pozos_en_resumen)].copy()

df_f9 = df_forma9_untr.copy()
df_f9 = df_f9[(df_f9['FECHA_FORMA9'].dt.month == mes_eval) & (df_f9['FECHA_FORMA9'].dt.year == anio_eval)]

df_f9['_F9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
dias_col  = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9.columns else None
mask_on   = (df_f9['_F9'].dt.month == mes_eval) & (df_f9['_F9'].dt.year == anio_eval)
if dias_col:
    mask_on = mask_on & (pd.to_numeric(df_f9[dias_col], errors='coerce').fillna(0) > 0)

fluid_cols = [c for c in df_f9.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
if fluid_cols:
    mask_fluid = pd.Series(False, index=df_f9.index)
    for fc in fluid_cols:
        mask_fluid = mask_fluid | (pd.to_numeric(df_f9[fc], errors='coerce').fillna(0) > 0)
    mask_on = mask_on & mask_fluid

pozos_on  = set(df_f9[mask_on]['POZO'].astype(str).str.strip().unique())
activos   = len(pozos_on)
inactivos = max(0, als_operativos - activos)

print(f"als_fondo: {als_fondo}, als_operativos: {als_operativos}, activos: {activos}, inactivos: {inactivos}")

# 2. IF calculation
from indice_falla import calcular_indice_falla_anual
_, df_mensual_if = calcular_indice_falla_anual(df.copy(), df_forma9_untr.copy(), fecha_eval)
print("df_mensual_if tail(3):")
print(df_mensual_if[['Mes', 'Pozos ON', 'Fallas ALS', 'Indice de Falla ALS ON', 'Indice_Falla_Rolling_ALS_ON_1500']].tail(3))
