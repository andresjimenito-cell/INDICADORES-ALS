import pandas as pd
import openpyxl

excel_path = "saved_uploads/bd_online.xlsx"

# Read only first 10 rows to inspect the columns
df = pd.read_excel(excel_path, nrows=10)
print("Raw Columns:")
print(df.columns.tolist())

# Let's read the full file but only selected columns to see missing/populated values
df_full = pd.read_excel(excel_path, usecols=lambda col: any(k in str(col).upper() for k in ['RUN', 'FALLA', 'PULL', 'OPERANDO', 'MTBF']))

print("\nValue counts or non-null counts:")
print(df_full.info())

# Find the exact name of the RUN LIFE @ FALLA column in Excel
col_life = [c for c in df_full.columns if 'RUN LIFE' in str(c).upper() and 'FALLA' in str(c).upper()]
col_op = [c for c in df_full.columns if 'OPERANDO' in str(c).upper()]
col_mtbf = [c for c in df_full.columns if 'INDICADOR' in str(c).upper() or 'MTBF' in str(c).upper()]

print("\nMatching columns:")
print("col_life:", col_life)
print("col_op:", col_op)
print("col_mtbf:", col_mtbf)

if col_life:
    cl = col_life[0]
    # Check non-null count for rows where OPERANDO/active is different
    print(f"\nNon-null count of {cl}:", df_full[cl].notna().sum())
    # Print a few rows where they are populated
    print(df_full[[cl] + col_op + col_mtbf].dropna(subset=[cl]).head(10))
