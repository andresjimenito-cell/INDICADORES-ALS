
import sys
import os
print(f"Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print("Path:")
for p in sys.path:
    print(f"  {p}")
