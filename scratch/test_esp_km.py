import pickle
import pandas as pd
import numpy as np

d = pickle.load(open('cache_data/last_run_data.pkl', 'rb'))
df_bd = d['df_bd']

grp = df_bd[df_bd['ALS'] == 'ESP'].copy()
grp = grp[grp['RUN LIFE'].notna() & (grp['RUN LIFE'] > 0)].copy()

times = pd.to_numeric(grp['RUN LIFE'], errors='coerce').values
events = grp['FECHA_FALLA'].notna().values

order = np.argsort(times)
t_sorted = times[order]
e_sorted = events[order]

print(f"Total ESP: {len(times)}, Fallas: {events.sum()}")
print("First 10 times:", t_sorted[:10])
print("First 10 events:", e_sorted[:10])

unique_t = np.unique(t_sorted)
surv = 1.0
n_at_risk = len(t_sorted)
x_vals, y_vals = [0.0], [100.0]

for ut in unique_t:
    mask_t = (t_sorted == ut)
    d_i = np.sum(e_sorted[mask_t])
    c_i = len(mask_t) - d_i
    if n_at_risk > 0:
        surv *= (1.0 - d_i / n_at_risk)
    x_vals.append(float(ut))
    y_vals.append(round(surv * 100.0, 2))
    n_at_risk -= len(mask_t)

print(f"Final surv ESP: {surv*100:.2f}%")
print("Sample y_vals:", y_vals[::100])
