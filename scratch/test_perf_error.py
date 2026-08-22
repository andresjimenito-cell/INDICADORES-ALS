import pickle
import pandas as pd
import numpy as np
import os, sys
import traceback

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('core'))
sys.path.append(os.path.abspath('data'))
sys.path.append(os.path.abspath('ui'))
sys.path.append(os.path.abspath('tabs'))

d = pickle.load(open('cache_data/last_run_data.pkl', 'rb'))
df_bd = d['df_bd']
df_forma9 = d['df_forma9']
fecha_eval = pd.to_datetime(d['fecha_evaluacion'])

print("--- Testing tab_performance ---")
try:
    from tabs.tab_performance import render_tab_performance
    render_tab_performance(df_bd, df_forma9, fecha_eval)
    print("tab_performance OK")
except Exception as e:
    print("ERROR in tab_performance:")
    traceback.print_exc()

print("\n--- Testing tab_mtbf ---")
try:
    from tabs.tab_mtbf import render_tab_mtbf
    render_tab_mtbf(df_bd, df_forma9, fecha_eval)
    print("tab_mtbf OK")
except Exception as e:
    print("ERROR in tab_mtbf:")
    traceback.print_exc()
