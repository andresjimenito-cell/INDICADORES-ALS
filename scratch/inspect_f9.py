
import pandas as pd
import io

def inspect_excel(file_path):
    print(f"Inspecting {file_path}")
    try:
        df = pd.read_excel(file_path, nrows=10, header=None)
        for i, row in df.iterrows():
            cols = [str(c) for c in row.tolist()]
            print(f"Row {i}: {cols}")
    except Exception as e:
        print(f"Error: {e}")

inspect_excel('saved_uploads/forma9_online.xlsx')
