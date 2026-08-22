import pickle
import pandas as pd
import numpy as np

import sys, os
sys.path.append(os.path.abspath('.'))
d = pickle.load(open('cache_data/last_run_data.pkl', 'rb'))
df_bd = d['df_bd']

from tabs.tab_mtbf import _kaplan_meier

print("BD columns:", df_bd.columns)
print("BD shape:", df_bd.shape)

curves = _kaplan_meier(df_bd)
print("Curves keys:", list(curves.keys()))
for k, v in curves.items():
    print(f"Key {k}: x len={len(v['x'])}, y len={len(v['y'])}, max_x={max(v['x'])}, min_y={min(v['y'])}")

# Check echarts config
km_series = []
max_x = 100.0
for als, curve in curves.items():
    if curve.get('x'):
        max_x = max(max_x, max(curve['x']))
    km_series.append({
        "name": als, "type": "line", "smooth": False,
        "step": "end",
        "data": [[x, y] for x, y in zip(curve['x'], curve['y'])],
        "itemStyle": {"color": curve['color']},
        "lineStyle": {"width": 2.5, "color": curve['color']},
        "symbol": "none",
        "areaStyle": {"color": f"{curve['color']}0F"}
    })

print("max_x:", max_x)
print("Series count:", len(km_series))
