import pandas as pd
import numpy as np

# Load session state or mock test logic
print("Testing month math logic:")
fecha_eval = pd.to_datetime('2026-07-31')
first_month = (fecha_eval.replace(day=1) - pd.DateOffset(months=11)).normalize()
print(f"Evaluation date: {fecha_eval}")
print(f"12M Window start date: {first_month}")

months = []
for i in range(12):
    m_start = (first_month + pd.DateOffset(months=i)).replace(day=1).normalize()
    m_end = (m_start + pd.offsets.MonthEnd(0)).normalize()
    months.append((m_start, m_end))

print("Months calculated:")
for ms, me in months:
    print(f"  {ms.strftime('%Y-%m-%d')} to {me.strftime('%Y-%m-%d')}")
