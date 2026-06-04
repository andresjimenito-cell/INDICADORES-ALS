import sys
import os
import pickle
sys.path.append(os.getcwd())

from config import CACHE_FILE
from mtbf import calcular_mtbf

if CACHE_FILE.exists():
    with open(CACHE_FILE, 'rb') as f:
        data = pickle.load(f)
    df_bd = data['df_bd']
    fecha_evaluacion = data['fecha_evaluacion']
    
    # Filter for ESP
    df_esp = df_bd[df_bd['ALS'].astype(str).str.strip() == 'ESP'].copy()
    
    mtbf, df_steps = calcular_mtbf(df_esp, fecha_evaluacion)
    
    print(f"Calculated MTBF: {mtbf}")
    print("\nColumns in df_esp:")
    print(df_esp.columns.tolist())
    
    print("\nINDICADOR_MTBF value counts:")
    print(df_esp['INDICADOR_MTBF'].value_counts(dropna=False))
    
    print("\nFirst 20 rows of calculation steps:")
    print(df_steps.head(20))
    
    print("\nLast 20 rows of calculation steps:")
    print(df_steps.tail(20))
else:
    print("Cache file does not exist")
