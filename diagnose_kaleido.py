
import sys
import os

log_file = "kaleido_diagnosis.log"

def log(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# Clean log file
if os.path.exists(log_file):
    os.remove(log_file)

log(f"Python executable: {sys.executable}")
log(f"Python version: {sys.version}")

try:
    import plotly
    log(f"Plotly version: {plotly.__version__}")
except ImportError:
    log("Plotly not installed")

try:
    import kaleido
    log(f"Kaleido version: {kaleido.__version__}")
    log(f"Kaleido path: {os.path.dirname(kaleido.__file__)}")
except ImportError:
    log("Kaleido not installed")

try:
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Bar(y=[1, 3, 2]))
    log("Figure created. Attempting export...")
    img = fig.to_image(format="png", engine="kaleido")
    log(f"Export successful. Image size: {len(img)} bytes")
except Exception as e:
    log(f"Export FAILED. Error: {e}")
    import traceback
    log(traceback.format_exc())
