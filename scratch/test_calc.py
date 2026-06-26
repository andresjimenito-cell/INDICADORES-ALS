import sys
import os
sys.path.append(os.getcwd())

import pickle
import pandas as pd
from indice_falla import calcular_indice_falla_anual

try:
    with open('cache_data/last_run_data.pkl', 'rb') as f:
        data = pickle.load(f)
    df_bd = data['df_bd']
    df_forma9 = data['df_forma9']
    fecha_eval = data['fecha_evaluacion']
    
    resumen, df_mensual = calcular_indice_falla_anual(df_bd, df_forma9, fecha_eval)
    print("RESUMEN:")
    print(resumen)
    
    print("\nÚltimos meses en df_mensual:")
    print(df_mensual[['Mes', 'Pozos ON', 'Pozos_ON_1500', 'Fallas Totales', 'Fallas_1500']].tail(5))
except Exception as e:
    print("Error:", e)
