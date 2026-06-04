
import pandas as pd
import io

def inspect_excel(file_path):
    print(f"Inspecting {file_path}")
    try:
        df = pd.read_excel(file_path, nrows=10, header=None)
        for i, row in df.iterrows():
            normalized_cols = [
                str(c).upper().strip().replace('.', '').replace('#', '')
                for c in row.tolist() if pd.notna(c)
            ]
            print(f"Row {i}: {normalized_cols}")
    except Exception as e:
        print(f"Error: {e}")

inspect_excel('saved_uploads/forma9_online.xlsx')
inspect_excel('saved_uploads/bd_online.xlsx')
