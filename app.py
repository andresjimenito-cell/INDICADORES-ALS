# === IMPORTS ===
import sys
import os

# Ajustar sys.path para soportar las subcarpetas del proyecto
base_dir = os.path.dirname(__file__)
for subfolder in ['core', 'data', 'ui', 'tabs']:
    path_dir = os.path.abspath(os.path.join(base_dir, subfolder))
    if path_dir not in sys.path:
        sys.path.append(path_dir)

import streamlit as st
import time
import subprocess
import importlib.util
import tema

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="🚀 Sistema Parex Resources (Frontera)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === COLORES Y TEMA (Usando `tema.py`) ===
COLOR_PRIMARIO = getattr(tema, 'COLOR_PRINCIPAL', '#137659')
COLOR_ACENTO = getattr(tema, 'COLOR_DASH_GOLD', '#c09c2e')
COLOR_FONDO_OSCURO = '#f5f7f6'
COLOR_SOMBRA = 'rgba(19, 118, 89, 0.1)'
COLOR_FUENTE = '#1f221e'

# === ESTILOS CSS - DISEÑO IMPACTANTE Y COMPACTO ===
st.markdown(f"""
<style>

 
 /* ANIMACIONES */
 @keyframes gradientShift {{
  0% {{ background-position: 0% 50%; }}
  50% {{ background-position: 100% 50%; }}
  100% {{ background-position: 0% 50%; }}
 }}
 
 @keyframes pulse {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.7; }}
 }}
 
 @keyframes slideIn {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
 }}
 
 @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 10px rgba(19, 118, 89, 0.08); }}
        50% {{ box-shadow: 0 0 14px rgba(19, 118, 89, 0.12); }}
 }}
 
 /* FONDO */
 .stApp {{
    background: linear-gradient(135deg, #f5f7f6 0%, #eaf4ef 40%, #ffffff 100%);
    background-size: 150% 150%;
    animation: gradientShift 45s ease infinite;
    color: #1f221e !important;
 }}
 
 /* COMPACTACIÓN */
 .main .block-container {{
  padding: 1.5rem 2rem;
  max-width: 95%;
 }}
 
 div[data-testid="stVerticalBlock"] {{ gap: 0.5rem; }}
 div[data-testid="column"] {{ padding: 0 0.5rem !important; }}
 #MainMenu, footer {{ visibility: hidden !important; }}
 
 /* LOGO */
 .logo-container {{
  text-align: center;
  margin-bottom: 2rem;
  animation: slideIn 0.8s ease-out;
 }}
 
 .logo-text {{
  font-family: 'Arial', sans-serif;
  font-size: 2.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, {COLOR_PRIMARIO}, {COLOR_ACENTO});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
    text-shadow: 0 0 6px {COLOR_SOMBRA};
 }}
 
 .logo-subtitle {{
  font-family: 'Arial', sans-serif;
  font-size: 1.1rem;
  color: {COLOR_PRIMARIO};
  letter-spacing: 3px;
  margin-top: 0.5rem;
 }}
 
 /* INPUTS */
 .stTextInput > div > div > input {{
  background: #ffffff !important;
    border: 2px solid rgba(19, 118, 89, 0.2) !important;
  border-radius: 12px;
  padding: 1rem;
  color: #1f221e !important;
  transition: all 0.3s ease;
 }}
 
 .stTextInput > div > div > input:focus {{
  border-color: {COLOR_PRIMARIO} !important;
    box-shadow: 0 0 8px rgba(19, 118, 89, 0.15);
 }}
 
 /* FORM CONTENEDOR LOGIN */
 div[data-testid="stForm"] {{
    background-color: #ffffff !important;
    border: 1px solid rgba(19, 118, 89, 0.15) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
 }}
 
  /* BOTONES */
  .stButton > button, .stFormSubmitButton > button, button[data-testid="stFormSubmitButton"] {{
   padding: 1rem;
   font-family: 'Arial', sans-serif;
   font-weight: 700;
   letter-spacing: 2px;
   border-radius: 12px;
    background: linear-gradient(135deg, #137659, #095139) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 3px 8px rgba(19, 118, 89, 0.2) !important;
   transition: all 0.3s ease;
  }}
  
  .stButton > button:hover, .stFormSubmitButton > button:hover, button[data-testid="stFormSubmitButton"]:hover {{
   transform: translateY(-3px) !important;
     box-shadow: 0 6px 18px rgba(19, 118, 89, 0.3) !important;
   background: linear-gradient(135deg, #095139, #137659) !important;
  }}
 
    /* DASHBOARD HEADER */
 .dashboard-header {{
    background: linear-gradient(135deg, rgba(19, 118, 89, 0.02), rgba(192, 156, 46, 0.08));
        border: 2px solid rgba(19, 118, 89, 0.16);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
        animation: glow 10s ease-in-out infinite;
 }}
 
 .dashboard-title {{
  font-family: 'Arial', sans-serif;
  font-size: 2rem;
  font-weight: 900;
  background: linear-gradient(120deg, {COLOR_PRIMARIO}, {COLOR_ACENTO});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
  margin: 0;
 }}
 
 .dashboard-subtitle {{
  font-family: 'Arial', sans-serif;
  font-size: 1rem;
  margin-top: 0.5rem;
  color: {COLOR_PRIMARIO};
  letter-spacing: 2px;
 }}
 
 /* EXPANDER */
 .stExpander {{
    border: 2px solid rgba(19, 118, 89, 0.18);
  border-radius: 12px;
  background: #ffffff;
 }}
 
 /* SEPARADORES */
 hr {{
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, {COLOR_PRIMARIO}, transparent);
  margin: 1.5rem 0;
 }}
 
</style>
""", unsafe_allow_html=True)

# === INICIALIZACIÓN DE SESSION STATE ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'login_attempt' not in st.session_state:
    st.session_state.login_attempt = 0
if 'hide_main_menu_only' not in st.session_state:
    st.session_state['hide_main_menu_only'] = False
if 'show_streamlit_ui' not in st.session_state:
    st.session_state['show_streamlit_ui'] = True

# --- FUNCIONES DE VISIBILIDAD ---

def _apply_streamlit_ui_visibility():
    if st.session_state.get('hide_main_menu_only'):
        st.markdown(
            """
            <style>
            #MainMenu{visibility:hidden !important; height:0px !important; display:none !important;}
            </style>
            """,
            unsafe_allow_html=True,
        )
        return

    if st.session_state.get('show_streamlit_ui'):
        st.markdown(
            """
            <style>
            #MainMenu, footer, header, .stDeployButton, div[data-testid='stToolbar']{
                visibility: visible !important;
                height: auto !important;
                display: block !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            #MainMenu, footer, header, .stDeployButton, div[data-testid='stToolbar']{
                visibility: hidden !important;
                height: 0px !important;
                display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

_apply_streamlit_ui_visibility()

# === LÓGICA DE EJECUCIÓN DEL MÓDULO ===
if st.session_state.get('authenticated') and 'launch_module_path' in st.session_state and st.session_state.get('launch_module_path'):
    launch_path = st.session_state.get('launch_module_path')
    launch_name = st.session_state.get('launch_module_name', os.path.splitext(os.path.basename(launch_path))[0])

    try:
        spec = importlib.util.spec_from_file_location("launched_module", launch_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        # Si el módulo tiene una función main o show_resumen, la llamamos
        if hasattr(mod, 'show_resumen'):
            mod.show_resumen()
        elif hasattr(mod, 'main'):
            mod.main()
            
    except Exception as e:
        st.error(f"❌ Error al cargar el módulo {launch_path}: {e}")
        if st.button("VOLVER AL LOGIN"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.stop()

# === FUNCIÓN DE AUTENTICACIÓN ===
def authenticate(username, password):
    users = {
        "lenin": "1",
        "pt": "2",
        "jaime": "1",
        "ajm": "1",
        "nelson": "1",
    }
    return users.get(username) == password

# === FUNCIÓN PARA ABRIR MÓDULOS ===
def open_module(module_name):
    try:
        cwd_files = os.listdir('.')
        target = None
        if module_name in cwd_files:
            target = module_name
        else:
            lower_target = module_name.lower()
            for f in cwd_files:
                if f.lower() == lower_target:
                    target = f
                    break
            if target is None and not module_name.lower().endswith('.py'):
                for f in cwd_files:
                    if f.lower() == (module_name + '.py').lower():
                        target = f
                        break

        if target is None:
            st.error(f"❌ No se encontró el archivo: {module_name}")
            return False

        full_path = os.path.abspath(target)
        st.session_state['launch_module_path'] = full_path
        st.session_state['launch_module_name'] = os.path.splitext(os.path.basename(full_path))[0]
        st.rerun()
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

# === PANTALLA DE LOGIN ===
def show_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    
    with col2:
        st.markdown("""
        <div class="logo-container">
             <div class="logo-text">ACCESO SEGURO</div>
             <div class="logo-subtitle">SISTEMA PAREX RESOURCES (FRONTERA)</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            from ui_helpers import get_logo_img_tag
            logo_html = get_logo_img_tag(width=200, style='filter: drop-shadow(0 0 10px rgba(19,118,89,0.3));')
            st.markdown(f"<div style='text-align:center; margin-bottom: 1.5rem;'>{logo_html}</div>", unsafe_allow_html=True)
        except Exception:
            st.markdown(
                "<div style='text-align:center; margin-bottom: 1.5rem;'>"
                "<img src='https://images.teamtailor-cdn.com/images/s3/teamtailor-production/logotype-v3/image_uploads/ec3d9ca8-2f80-424a-89a1-bf6345ecb37f/original.png' width='200'/>"
                "</div>",
                unsafe_allow_html=True
            )
        
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("👤 USUARIO", placeholder="Ingresa tu usuario", label_visibility="collapsed")
            password = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed")
            submit = st.form_submit_button("🔑 INICIAR SESIÓN", use_container_width=True)
            
            if submit:
                if authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    try:
                        st.session_state['hide_main_menu_only'] = True if str(username).strip().lower() == 'invitado' else False
                    except Exception:
                        st.session_state['hide_main_menu_only'] = False
                    st.success(f"✅ ¡Bienvenido, {username.upper()}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Inténtalo de nuevo.")

        
        st.markdown("""
        <div style='text-align: center; margin-top: 1.5rem; opacity: 0.7; color: #475569;'>
            <small>Sistema de Monitoreo & Control AJM | © Parex Resources (Frontera)</small>
        </div>
        """, unsafe_allow_html=True)

# === LÓGICA PRINCIPAL ===
def main():
    if not st.session_state.get('authenticated', False):
        show_login()
    else:
        # Si ya estamos autenticados pero no hemos lanzado el módulo, lo lanzamos automáticamente
        if 'launch_module_path' not in st.session_state:
            username = (st.session_state.get('username') or '').strip().lower()
            if username == 'invitado':
                open_module('resumen_publico.py')
            else:
                # Se lanza INDICADORES.py por defecto
                open_module('INDICADORES.py')

if __name__ == "__main__":
    main()