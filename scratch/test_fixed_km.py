import pickle
import pandas as pd
import numpy as np

d = pickle.load(open('cache_data/last_run_data.pkl', 'rb'))
df_bd = d['df_bd']

def test_fixed_kaplan_meier(df_bd):
    curves = {}
    for als, grp in df_bd.groupby('ALS'):
        grp = grp[grp['RUN LIFE'].notna() & (grp['RUN LIFE'] > 0)].copy()
        if len(grp) < 5:
            continue
        
        times = pd.to_numeric(grp['RUN LIFE'], errors='coerce').values
        events = grp['FECHA_FALLA'].notna().values
        
        order = np.argsort(times)
        t_sorted = times[order]
        e_sorted = events[order]
        
        unique_t, counts = np.unique(t_sorted, return_counts=True)
        surv = 1.0
        n_at_risk = len(t_sorted)
        x_vals, y_vals = [0.0], [100.0]
        
        for ut, count in zip(unique_t, counts):
            mask_t = (t_sorted == ut)
            d_i = np.sum(e_sorted[mask_t]) # number of failures at time ut
            if n_at_risk > 0:
                surv *= (1.0 - (d_i / n_at_risk))
            x_vals.append(float(ut))
            y_vals.append(round(surv * 100.0, 1))
            n_at_risk -= count # subtract only the items at risk at this time!
            
        curves[str(als)] = {'x': x_vals, 'y': y_vals, 'min_y': min(y_vals), 'max_x': max(x_vals)}

    return curves

res = test_fixed_kaplan_meier(df_bd)
for k, v in res.items():
    print(f"ALS: {k} -> points: {len(v['x'])}, max_x: {v['max_x']} days, min_surv: {v['min_y']}%, 50% surv at: ~{[x for x, y in zip(v['x'], v['y']) if y <= 50.0][:1]}")
