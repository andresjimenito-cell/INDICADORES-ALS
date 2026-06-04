import pandas as pd

excel_path = "saved_uploads/bd_online.xlsx"
df = pd.read_excel(excel_path)

# Normalize column names for easy access
df.columns = [str(c).strip().upper() for c in df.columns]

# Print value counts of FECHA PULL for active wells (where OPERANDO ESTADO is X or x or not null)
active_mask = df['OPERANDO ESTADO'].notna() & df['OPERANDO ESTADO'].astype(str).str.strip().str.upper().isin(['X', 'SI'])
active_df = df[active_mask]
print("Active wells count:", len(active_df))
print("Active wells - unique FECHA PULL values:")
print(active_df['FECHA PULL'].value_counts(dropna=False).head(10))

print("\nActive wells - unique FECHA FALLA values:")
print(active_df['FECHA FALLA'].value_counts(dropna=False).head(10))

print("\nActive wells - unique RUN LIFE @ FALLA values:")
print(active_df['RUN LIFE @ FALLA'].value_counts(dropna=False).head(10))

# Let's inspect some rows of active wells
print("\nActive wells - first 5 rows of columns POZO, FECHA RUN, FECHA FALLA, FECHA PULL, RUN LIFE @ FALLA:")
print(active_df[['POZO', 'FECHA RUN', 'FECHA FALLA', 'FECHA PULL', 'RUN LIFE @ FALLA']].head(5))

# What is the maximum date in FECHA RUN/FALLA/PULL?
print("\nMax FECHA RUN:", pd.to_datetime(df['FECHA RUN'], errors='coerce').max())
print("Max FECHA FALLA:", pd.to_datetime(df['FECHA FALLA'], errors='coerce').max())
print("Max FECHA PULL:", pd.to_datetime(df['FECHA PULL'], errors='coerce').max())
