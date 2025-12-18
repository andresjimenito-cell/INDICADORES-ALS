# === IMPORTS ===
import streamlit as st
from datetime import datetime
import time
import subprocess
import sys
import os
import importlib.util
import tema

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="🚀 Sistema Frontera Energy",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === COLORES Y TEMA (Usando `tema.py`) ===
COLOR_PRIMARIO = getattr(tema, 'COLOR_PRINCIPAL', '#FF00FF')
COLOR_ACENTO = getattr(tema, 'COLOR_DASH_CYAN', getattr(tema, 'COLOR_AZUL_CIBER', '#00D9FF'))
COLOR_FONDO_OSCURO = getattr(tema, 'COLOR_FONDO_OSCURO', '#0A0E27')
COLOR_SOMBRA = getattr(tema, 'COLOR_GLOW_SUAVE', 'rgba(0, 255, 153, 0.12)')
COLOR_FUENTE = getattr(tema, 'COLOR_FUENTE', '#E8F5E9')

# === ESTILOS CSS - DISEÑO IMPACTANTE Y COMPACTO ===
st.markdown(f"""
<style>
 @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
 
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
    /* GLOW: tono fucsia atenuado (más oscuro y menos intenso) */
        0%, 100% {{ box-shadow: 0 0 10px rgba(120, 0, 80, 0.12); }}
        50% {{ box-shadow: 0 0 14px rgba(120, 0, 80, 0.16); }}
 }}
 
 /* FONDO */
 .stApp {{
    background: linear-gradient(135deg, #0E1117 0%, #131723 40%, #0d1117 50%);
    background-size: 150% 150%;
    animation: gradientShift 45s ease infinite;
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
  font-family: 'Orbitron', monospace;
  font-size: 2.5rem;
  font-weight: 900;
  background: linear-gradient(135deg, {COLOR_PRIMARIO}, {COLOR_ACENTO});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
    text-shadow: 0 0 6px {COLOR_SOMBRA};
 }}
 
 .logo-subtitle {{
  font-family: 'Rajdhani', sans-serif;
  font-size: 1.1rem;
  color: {COLOR_ACENTO};
  letter-spacing: 3px;
  margin-top: 0.5rem;
 }}
 
 /* INPUTS */
 .stTextInput > div > div > input {{
  background: rgba(10, 14, 39, 0.9) !important;
  /* CAMBIADO: De verde (0, 255, 153) a fucsia/morado (170, 0, 255) */
    border: 2px solid rgba(170, 0, 255, 0.26) !important;
  border-radius: 12px;
  padding: 1rem;
  color: {COLOR_FUENTE} !important;
  transition: all 0.3s ease;
 }}
 
 .stTextInput > div > div > input:focus {{
  border-color: {COLOR_ACENTO} !important;
  /* CAMBIADO: De verde (0, 255, 153) a fucsia/morado (170, 0, 255) */
    box-shadow: 0 0 8px rgba(170, 0, 255, 0.16);
 }}
 
 /* BOTONES */
 .stButton > button {{
  padding: 1rem;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 700;
  letter-spacing: 2px;
  border-radius: 12px;
  /* CAMBIADO: De verde/cian (0, 255, 153) y (0, 217, 255) a fucsia/morado (255, 0, 153) y (170, 0, 255) */
    background: linear-gradient(135deg, rgba(120, 0, 80, 0.16), rgba(90, 0, 170, 0.14));
    /* TONO FUSCIA OSCURECIDO */
        border: 2px solid rgba(120, 0, 80, 0.18);
        box-shadow: 0 3px 8px rgba(120, 0, 80, 0.12);
  transition: all 0.3s ease;
 }}
 
 .stButton > button:hover {{
  transform: translateY(-3px);
  /* CAMBIADO: De verde (0, 255, 153) a fucsia/morado (255, 0, 153) */
    box-shadow: 0 6px 18px rgba(120, 0, 80, 0.12);
  border-color: {COLOR_ACENTO};
 }}
 
    /* DASHBOARD HEADER */
 .dashboard-header {{
    /* FONDO DEL HEADER: fucsia atenuado */
    background: linear-gradient(135deg, rgba(120, 0, 80, 0.02), rgba(90, 0, 170, 0.08));
        border: 2px solid rgba(120, 0, 80, 0.16);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
        animation: glow 10s ease-in-out infinite;
 }}
 
 .dashboard-title {{
  font-family: 'Orbitron', monospace;
  font-size: 2rem;
  font-weight: 900;
  background: linear-gradient(120deg, {COLOR_PRIMARIO}, {COLOR_ACENTO});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
  margin: 0;
 }}
 
 .dashboard-subtitle {{
  font-family: 'Rajdhani', sans-serif;
  font-size: 1rem;
  margin-top: 0.5rem;
  color: {COLOR_ACENTO};
  letter-spacing: 2px;
 }}
 
 /* CARDS DE MÓDULOS */
 .module-card {{
    background: linear-gradient(135deg, rgba(10, 14, 39, 0.9), rgba(26, 31, 58, 0.8));
    /* Fucsia más oscuro y menos saturado para bordes */
    border: 2px solid rgba(120, 0, 80, 0.22);
  border-radius: 20px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.45);
  min-height: 280px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
 }}
 
 .module-card:hover {{
    transform: translateY(-8px);
        box-shadow: 0 10px 28px rgba(120, 0, 80, 0.12);
    border-color: {COLOR_ACENTO};
 }}
 
    .module-icon {{
    font-size: 3.5rem;
    margin-bottom: 0.8rem;
        filter: drop-shadow(0 0 8px {COLOR_SOMBRA});
 }}
 
 .module-title {{
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  font-weight: 700;
  color: {COLOR_ACENTO};
  margin-bottom: 0.8rem;
  letter-spacing: 2px;
 }}
 
 .module-description {{
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.9rem;
  line-height: 1.6;
  color: rgba(232, 245, 233, 0.9);
 }}
 
 .module-badge {{
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.4rem 0.8rem;
  font-size: 0.7rem;
  font-family: 'Rajdhani', sans-serif;
  font-weight: 700;
  letter-spacing: 1px;
  background: linear-gradient(135deg, {COLOR_PRIMARIO}, {COLOR_ACENTO});
  border-radius: 20px;
  /* CAMBIADO: De verde (0, 255, 153) a fucsia/morado (255, 0, 153) */
        box-shadow: 0 0 8px rgba(120, 0, 80, 0.12);
  animation: pulse 2s ease-in-out infinite;
 }}
 
 /* INFO CARDS */
 .info-card {{
  /* CAMBIADO: De verde/cian (0, 255, 153) y (0, 217, 255) a fucsia/morado (255, 0, 153) y (170, 0, 255) */
    background: linear-gradient(135deg, rgba(120, 0, 80, 0.16), rgba(90, 0, 170, 0.14));
    /* TONOS FUSCIA OSCURECIDOS */
        border: 2px solid rgba(120, 0, 80, 0.18);
        box-shadow: 0 3px 8px rgba(120, 0, 80, 0.12);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
 }}
 
 .info-card:hover {{
    transform: translateY(-5px);
        box-shadow: 0 6px 18px rgba(120, 0, 80, 0.12);
 }}
 
 .info-icon {{ font-size: 2rem; }}
 
 .info-value {{
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  font-weight: 700;
  color: {COLOR_ACENTO};
  margin: 0.5rem 0;
 }}
 
 .info-label {{
  font-family: 'Rajdhani', sans-serif;
  font-size: 0.8rem;
  letter-spacing: 1px;
  opacity: 0.8;
 }}

 /* EXPANDER */
 .stExpander {{
    /* EXPANDER: borde fucsia atenuado */
    border: 2px solid rgba(120, 0, 80, 0.18);
  border-radius: 12px;
  background: rgba(10, 14, 39, 0.6);
 }}
 
 /* SEPARADORES */
 hr {{
  border: none;
  height: 2px;
  background: linear-gradient(90deg, transparent, {COLOR_ACENTO}, transparent);
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
if 'launch_module_path' in st.session_state and st.session_state.get('launch_module_path'):
    launch_path = st.session_state.get('launch_module_path')
    launch_name = st.session_state.get('launch_module_name', os.path.splitext(os.path.basename(launch_path))[0])

    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<h2 style='color: {COLOR_ACENTO}; margin:0; font-family: \"Orbitron\", monospace;'>EJECUTANDO MÓDULO: {launch_name.upper()}</h2>"
                f"</div>", unsafe_allow_html=True)

    if st.button("⬅️ VOLVER AL DASHBOARD", key="btn_return_dashboard"):
        for key in ['launch_module_path', 'launch_module_name']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    try:
        for _k in ['show_resumen_publico', 'go_to_indicadores']:
            if _k in st.session_state:
                try:
                    del st.session_state[_k]
                except Exception:
                    pass

        debug_info = st.session_state.get('launch_module_debug')
        resolved_fname = st.session_state.get('launch_module_resolved_filename')
        if resolved_fname or debug_info:
            try:
                st.markdown(
                    f"<div style='margin-bottom:6px; font-size:12px; opacity:0.85;'>Archivo resuelto: <b>{resolved_fname}</b> — Ruta: <code>{launch_path}</code></div>",
                    unsafe_allow_html=True
                )
            except Exception:
                pass

        spec = importlib.util.spec_from_file_location("launched_module", launch_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        try:
            if hasattr(mod, 'show_resumen'):
                try:
                    mod.show_resumen()
                    st.stop()
                except Exception as e:
                    st.error(f"Error ejecutando show_resumen() del módulo {launch_path}: {e}")
            elif hasattr(mod, 'main'):
                try:
                    mod.main()
                    st.stop()
                except Exception as e:
                    st.error(f"Error ejecutando main() del módulo {launch_path}: {e}")
        except Exception:
            pass
    except Exception as e:
        st.error(f"❌ Error al cargar el módulo {launch_path}: {e}")
        st.write("Si quieres volver al dashboard pulsa 'VOLVER AL DASHBOARD'.")
    
    st.stop()

# === FUNCIÓN DE AUTENTICACIÓN ===
def authenticate(username, password):
    users = {
        "lenin": "1",
        "pt": "2",
        "jaime": "1",
        "ajm": "1",
    }
    return users.get(username) == password

# === FUNCIÓN PARA ABRIR MÓDULOS ===
def open_module(module_name):
    current_user = (st.session_state.get('username') or '').strip().lower()
    try:
        requested_basename = os.path.basename(module_name).lower()
    except Exception:
        requested_basename = str(module_name).lower()
    if current_user == 'invitado':
        if not (requested_basename == 'resumen_publico.py' or requested_basename == 'resumen_publico'):
            st.error("Acceso denegado: el usuario 'invitado' solo puede ver el Resumen Público.")
            return False
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
            st.info(f"💡 Asegúrate de que {module_name} esté en el mismo directorio que app.py")
            return False

        full_path = os.path.abspath(target)
        st.session_state['launch_module_path'] = full_path
        st.session_state['launch_module_name'] = os.path.splitext(os.path.basename(full_path))[0]
        st.session_state['launch_module_resolved_filename'] = os.path.basename(target)

        try:
            st.session_state['launch_module_debug'] = {
                'requested': module_name,
                'resolved_target': target,
                'full_path': full_path,
                'cwd': os.getcwd(),
                'cwd_files_count': len(os.listdir('.'))
            }
        except Exception:
            st.session_state['launch_module_debug'] = None

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
            <div class="logo-subtitle">SISTEMA FRONTERA ENERGY</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            from ui_helpers import get_logo_img_tag
            logo_html = get_logo_img_tag(width=200, style='filter: drop-shadow(0 0 15px rgba(0,141,255,0.9));')
            st.markdown(f"<div style='text-align:center; margin-bottom: 1.5rem;'>{logo_html}</div>", unsafe_allow_html=True)
        except Exception:
            st.markdown(
                "<div style='text-align:center; margin-bottom: 1.5rem;'>"
                "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='200'/>"
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

        if st.button("🔓 INGRESAR COMO INVITADO", key="btn_ingresar_invitado", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.username = 'invitado'
            st.session_state['hide_main_menu_only'] = True
            st.success("✅ Accedido como invitado")
            time.sleep(0.3)
            st.rerun()
        
        st.markdown("""
        <div style='text-align: center; margin-top: 1.5rem; opacity: 0.5;'>
            <small>Sistema de Monitoreo & Control AJM | © Frontera Energy</small>
        </div>
        """, unsafe_allow_html=True)

# === DASHBOARD PRINCIPAL ===
def show_dashboard():
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">CENTRO DE CONTROL</h1>
        <p class="dashboard-subtitle">Bienvenido, <strong>{st.session_state.username.upper()}</strong>. Selecciona el módulo a iniciar.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="module-card">
            <div class="module-badge">OPERACIONAL</div>
            <div class="module-icon">📊</div>
            <div class="module-title">INDICADORES ALS</div>
            <div class="module-description">
                Plataforma integral de análisis y monitoreo de indicadores de Sistemas Artificiales
                de Levantamiento (ALS). Incluye métricas clave como MTBF, Run Life, índices de falla y 
                reportes de performance de equipos.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns([1, 1], gap='small')
        with col_btn1:
            if st.button("🚀 INICIAR INDICADORES", key="btn_indicadores_dashboard", use_container_width=True):
                open_module("indicadores.py")
        with col_btn2:
            if st.button("📊 VER RESUMEN PÚBLICO", key="btn_resumen_publico", use_container_width=True):
                open_module("resumen_publico.py")
    
    with col2:
        st.markdown("""
        <div class="module-card">
            <div class="module-badge">INGENIERÍA</div>
            <div class="module-icon">⚙️</div>
            <div class="module-title">EVALUACIÓN ESP</div>
            <div class="module-description">
                Herramienta avanzada para la evaluación técnica, económica y energética 
                de diseños de Bombas Sumergibles Eléctricas (ESP). Permite la comparación 
                detallada de proveedores y análisis del Costo Total del Ciclo de Vida (TLCC).
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
        if st.button("🚀 INICIAR EVALUACIÓN", key="btn_evaluacion", use_container_width=True):
            open_module("evaluacion.py")

    with col3:
        st.markdown("""
        <div class="module-card">
            <div class="module-badge">INNOVACIÓN</div>
            <div class="module-icon">🖥️</div>
            <div class="module-title">ESP VISUALIZER</div>
            <div class="module-description">
                Visualización gráfica avanzada e interactiva para sistemas ESP. 
                Entorno visual moderno implementado con tecnología web de última generación.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
        if st.button("🚀 INICIAR VISUALIZADOR", key="btn_visualizador", use_container_width=True):
            open_module("esp_visualizer.py")
    
    st.markdown("---")
    
    col_info1, col_info2, col_info3 = st.columns(3, gap="small")
    
    with col_info1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-icon">💡</div>
            <div class="info-value">2</div>
            <div class="info-label">Módulos Activos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-icon">⏰</div>
            <div class="info-value">{datetime.now().strftime("%H:%M")}</div>
            <div class="info-label">Hora del Sistema</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-icon">👤</div>
            <div class="info-value">{st.session_state.username.upper()}</div>
            <div class="info-label">Usuario Activo</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📁 VERIFICACIÓN DE ARCHIVOS DEL SISTEMA"):
        col_check1, col_check2, col_check3 = st.columns(3)
        
        with col_check1:
            if os.path.exists("indicadores.py"):
                st.success("✅ **indicadores.py** encontrado y listo.")
            else:
                st.error("❌ **indicadores.py** no encontrado. Módulo Inactivo.")
        
        with col_check2:
            if os.path.exists("evaluacion.py"):
                st.success("✅ **evaluacion.py** encontrado y listo.")
            else:
                st.error("❌ **evaluacion.py** no encontrado. Módulo Inactivo.")
        
        with col_check3:
            if os.path.exists("esp_visualizer.py"):
                st.success("✅ **esp_visualizer.py** encontrado y listo.")
            else:
                st.error("❌ **esp_visualizer.py** no encontrado. Módulo Inactivo.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_logout1, col_logout2, col_logout3 = st.columns([1, 2, 1])
    with col_logout2:
        if st.button("🚪 CERRAR SESIÓN", key="btn_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state['hide_main_menu_only'] = False
            st.rerun()

# === LÓGICA PRINCIPAL ===
def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        username = (st.session_state.get('username') or '').strip().lower()

        if username == 'invitado':
            try:
                import importlib
                rp = importlib.import_module('resumen_publico')
                if hasattr(rp, 'show_resumen'):
                    rp.show_resumen()
                    return
            except Exception:
                try:
                    open_module('resumen_publico.py')
                    return
                except Exception:
                    st.error('No se pudo cargar el resumen público para el usuario invitado.')
                    return

        show_dashboard()

if __name__ == "__main__":
    main()
