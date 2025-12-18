import streamlit as st
import streamlit.components.v1 as components
import os
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import socket
import shutil
import requests
import re
import html

# Configuration - Updated Port
PORT = 8504
FOLDER_NAME = "esp-visualizer-pro (8)"
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), FOLDER_NAME, "dist")
SAVED_UPLOADS_DIR = os.path.join(os.getcwd(), 'saved_uploads')

# Data Sources
DATA_SOURCE_BD = os.path.join(SAVED_UPLOADS_DIR, 'bd_online.xlsx')
DATA_DEST_BD = os.path.join(DIST_DIR, 'bd.xlsx')

CURVE_URL = "https://1drv.ms/x/c/06cc4035ad46ff97/IQDfSMUid3XzSboJNZ0NPT1uATj27nVud0N2zQROHn2_yoo?e=MsySGY"
DATA_SOURCE_CURVES = os.path.join(SAVED_UPLOADS_DIR, 'curves.xlsx')
DATA_DEST_CURVES = os.path.join(DIST_DIR, 'curves.xlsx')

# Ensure directories
os.makedirs(SAVED_UPLOADS_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

def _download_onedrive(url, dest_path):
    try:
        r = requests.get(url, timeout=60, allow_redirects=True)
        r.raise_for_status()
        content = r.content
        
        # Check if it's the OneDrive wrapper page
        if b'<html' in content[:1000].lower() or b'<!doctype html>' in content[:1000].lower():
            txt = content.decode('utf-8', errors='ignore')
            # Regex to find direct download link
            m = re.search(r'FileGetUrl"\s*:\s*"([^"]+)"', txt) or re.search(r'FileUrlNoAuth"\s*:\s*"([^"]+)"', txt)
            if m:
                download_url = m.group(1).replace('\\u0026', '&').replace('\\/', '/')
                download_url = html.unescape(download_url)
                r2 = requests.get(download_url, timeout=60)
                r2.raise_for_status()
                with open(dest_path, 'wb') as f:
                    f.write(r2.content)
                return True
        
        # If not html or no regex match, assume content is the file
        with open(dest_path, 'wb') as f:
            f.write(content)
        return True
    except Exception as e:
        # print(f"Download Error: {e}")
        return False

def prepare_data_files():
    """Ensure both BD and Curves files are in the dist folder."""
    # 1. BD File
    if os.path.exists(DATA_SOURCE_BD):
        try:
            shutil.copy2(DATA_SOURCE_BD, DATA_DEST_BD)
        except: pass
        
    # 2. Curves File
    if not os.path.exists(DATA_SOURCE_CURVES):
       with st.spinner("Descargando base de datos de curvas (Primera vez)..."):
           success = _download_onedrive(CURVE_URL, DATA_SOURCE_CURVES)
           if not success:
               st.warning("No se pudo descargar el archivo de curvas. Verifique su conexión.")

    if os.path.exists(DATA_SOURCE_CURVES):
        try:
           shutil.copy2(DATA_SOURCE_CURVES, DATA_DEST_CURVES)
        except: pass

def serve_app():
    """Function to run the HTTP server in a separate thread"""
    try:
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIST_DIR, **kwargs)
            
            def end_headers(self):
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                super().end_headers()
        
        TCPServer.allow_reuse_address = True
        with TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except OSError:
        pass 

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_server_if_needed():
    if not is_port_in_use(PORT):
        thread = threading.Thread(target=serve_app, daemon=True)
        thread.start()

def main():
    prepare_data_files() 
    start_server_if_needed()
    
    st.markdown("""
        <style>
            .main .block-container {
                max-width: 98% !important;
                padding-top: 2rem !important;
                padding-right: 1rem !important;
                padding-left: 1rem !important;
                padding-bottom: 0rem !important;
            }
            iframe {
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
                background-color: #0E1117;
            }
        </style>
    """, unsafe_allow_html=True)
    
    components.iframe(f"http://localhost:{PORT}", height=1000, scrolling=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Error launching visualizer: {e}")
