# === IMPORTS ===
import streamlit as st
from datetime import datetime
import time
import subprocess
import sys
import os
import importlib.util

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="🚀 Sistema Frontera Energy",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === COLORES Y TEMA ===
# Definición de colores mejorada para un look más "cyberpunk" y hi-tech
COLOR_PRIMARIO = '#00FF99'     # Verde Neón
COLOR_ACENTO = '#00D9FF'       # Azul Ciber
COLOR_FONDO_OSCURO = '#0A0E27' # Azul Profundo
COLOR_SOMBRA = 'rgba(0, 255, 153, 0.7)' # Sombra de neón
COLOR_FUENTE = '#E8F5E9'       # Gris Casi Blanco

# === ESTILOS CSS - SIN ANIMACIONES MOLESTAS ===
st.markdown(f"""
<style>
    :root {{
        --color-primario: {COLOR_PRIMARIO};
        --color-acento: {COLOR_ACENTO};
        --color-fondo-oscuro: {COLOR_FONDO_OSCURO};
        --color-sombra: {COLOR_SOMBRA};
        --color-fuente: {COLOR_FUENTE};
    }}
    
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* FONDO ESTÁTICO */
    .stApp {{
        background: linear-gradient(135deg, var(--color-fondo-oscuro) 0%, #0d1117 50%, #0a0e27 100%);
        background-attachment: fixed;
    }}
    
    /* OCULTAR ELEMENTOS DE STREAMLIT (controlado por la UI — usar los botones de la barra lateral) */
    /* Nota: la visibilidad del menú ya no se oculta aquí de forma permanente. */
    
    /* LOGO */
    .logo-container {{
        text-align: center;
        margin-bottom: 3rem;
    }}
    
    .logo-text {{
        font-family: 'Orbitron', monospace;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--color-primario), var(--color-acento));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px var(--color-sombra);
        letter-spacing: 5px;
        margin-bottom: 0.5rem;
    }}
    
    .logo-subtitle {{
        font-family: 'Rajdhani', sans-serif;
        color: var(--color-acento);
        font-size: 1.1rem;
        letter-spacing: 3px;
        margin-top: 0.5rem;
        font-weight: 400;
    }}
    
    /* INPUTS DE LOGIN */
    .stTextInput > div > div > input {{
        background: rgba(10, 14, 39, 0.9) !important;
        border: 2px solid rgba(0, 255, 153, 0.3) !important;
        border-radius: 12px;
        color: var(--color-fuente) !important;
        padding: 1.2rem;
        font-size: 1.1rem;
        transition: all 0.3s;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--color-primario) !important;
        box-shadow: 0 0 25px var(--color-sombra) !important;
        outline: none;
    }}
    
    .stTextInput > label {{
        color: var(--color-acento) !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }}
    
    /* BOTONES */
    .stButton > button {{
        width: 100%;
        background: linear-gradient(135deg, var(--color-primario), var(--color-acento));
        color: var(--color-fondo-oscuro);
        border: none;
        border-radius: 12px;
        padding: 1.2rem;
        font-family: 'Orbitron', monospace;
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 3px;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 10px 30px rgba(0, 255, 153, 0.4);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-4px);
        box-shadow: 0 15px 45px rgba(0, 255, 153, 0.7);
    }}
    
    /* DASHBOARD HEADER */
    .dashboard-header {{
        background: rgba(0, 255, 153, 0.05); /* Ligeramente más transparente */
        border: 1px solid rgba(0, 255, 153, 0.3);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 50px rgba(0, 255, 153, 0.5);
    }}
    
    .dashboard-title {{
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--color-primario), var(--color-acento));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        letter-spacing: 5px;
        text-shadow: 0 0 10px rgba(0, 255, 153, 0.3);
    }}
    
    .dashboard-subtitle {{
        text-align: center;
        color: var(--color-fuente);
        font-size: 1.3rem;
        margin-top: 1rem;
        opacity: 0.9;
        font-family: 'Rajdhani', sans-serif;
    }}
    
    /* CARDS - Con efecto Frosted Glass */
    .module-card {{
        background: rgba(10, 14, 39, 0.7); /* Menos opaco para el efecto */
        border: 1px solid rgba(0, 255, 153, 0.5);
        border-radius: 25px;
        padding: 3rem;
        transition: all 0.4s ease;
        backdrop-filter: blur(8px); /* Efecto Frosted Glass */
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        position: relative;
        height: 100%;
        min-height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    
    .module-card:hover {{
        transform: scale(1.02); /* Escala sutil */
        border-color: var(--color-acento);
        box-shadow: 0 25px 60px rgba(0, 255, 153, 0.5);
    }}
    
    .module-icon {{
        font-size: 5.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(45deg, var(--color-primario), var(--color-acento));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px var(--color-sombra));
    }}
    
    .module-title {{
        font-family: 'Orbitron', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--color-primario);
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }}
    
    .module-description {{
        color: var(--color-fuente);
        text-align: center;
        font-size: 1rem;
        line-height: 1.7;
        opacity: 0.85;
        flex-grow: 1; /* Para que ocupe espacio y las tarjetas se vean uniformes */
    }}
    
    .module-badge {{
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: linear-gradient(90deg, #FF6B6B, #FF9966); /* Distinto color para el badge */
        color: var(--color-fondo-oscuro);
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 900;
        letter-spacing: 1px;
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.5);
    }}
    
    /* INFO CARDS (pequeñas estadísticas) */
    .info-card {{
        text-align: center; 
        padding: 1.8rem; 
        background: rgba(0, 255, 153, 0.05); 
        border-radius: 15px; 
        border: 1px solid rgba(0, 255, 153, 0.3);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s;
    }}
    
    .info-card:hover {{
        background: rgba(0, 255, 153, 0.1);
        box-shadow: 0 10px 30px var(--color-sombra);
    }}
    
    .info-icon {{
        font-size: 2.5rem; 
        margin-bottom: 0.5rem; 
        color: var(--color-acento);
        filter: drop-shadow(0 0 8px var(--color-acento));
    }}
    
    .info-value {{
        color: var(--color-primario); 
        font-weight: 900; 
        font-size: 2rem; 
        font-family: 'Orbitron', monospace;
    }}
    
    .info-label {{
        color: var(--color-fuente); 
        opacity: 0.8; 
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* EXPANDER (Estado de Módulos) */
    .stExpander {{
        border: 1px solid rgba(0, 255, 153, 0.3) !important;
        border-radius: 12px;
        background: rgba(10, 14, 39, 0.6) !important;
    }}

    .stExpander > div:first-child > div:first-child {{
        padding: 1rem 1.5rem !important;
        background: rgba(0, 255, 153, 0.1) !important;
        border-radius: 12px 12px 0 0;
        font-weight: 700;
        color: var(--color-primario);
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
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

# Control para mostrar/ocultar elementos nativos de Streamlit (menú, footer, header)
if 'show_streamlit_ui' not in st.session_state:
    st.session_state['show_streamlit_ui'] = False

def _apply_streamlit_ui_visibility():
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

# Añadir controles rápidos en la barra lateral para restaurar/ocultar el menú
with st.sidebar.expander('Ajustes de UI', expanded=False):
    if st.button('Restaurar menú Streamlit', key='restore_menu_btn'):
        st.session_state['show_streamlit_ui'] = True
        st.experimental_rerun()
    if st.button('Ocultar menú Streamlit', key='hide_menu_btn'):
        st.session_state['show_streamlit_ui'] = False
        st.experimental_rerun()

# Aplicar la visibilidad en cada carga
_apply_streamlit_ui_visibility()

# === LÓGICA DE EJECUCIÓN DEL MÓDULO (IN-PROCESS) ===
if 'launch_module_path' in st.session_state and st.session_state.get('launch_module_path'):
    launch_path = st.session_state.get('launch_module_path')
    launch_name = st.session_state.get('launch_module_name', os.path.splitext(os.path.basename(launch_path))[0])

    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<h2 style='color: var(--color-acento); margin:0; font-family: 'Orbitron', monospace;'>🚀 EJECUTANDO MÓDULO: {launch_name.upper()}</h2>"
                f"</div>", unsafe_allow_html=True)

    # Botón de retorno más estético
    if st.button("⬅️ VOLVER AL DASHBOARD", key="btn_return_dashboard"):
        # Limpieza de session state
        for key in ['launch_module_path', 'launch_module_name']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun() # <-- CORRECCIÓN A st.rerun()

    # Importar y ejecutar el módulo
    try:
        spec = importlib.util.spec_from_file_location("launched_module", launch_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        st.error(f"❌ Error al cargar el módulo {launch_path}: {e}")
        st.write("Si quieres volver al dashboard pulsa 'VOLVER AL DASHBOARD'.")
    
    st.stop() # Bloquear la ejecución del resto del script

# === FUNCIÓN DE AUTENTICACIÓN ===
def authenticate(username, password):
    """Autenticación simple"""
    users = {
        "lenin": "1",
        "practicante": "2",
        "invitado": "3",
        "jaime": "1",
    }
    return users.get(username) == password

# === FUNCIÓN PARA ABRIR MÓDULOS (LÓGICA INTACTA) ===
def open_module(module_name):
    """Marca la sesión para cargar un módulo en el mismo proceso y recarga la app."""
    try:
        # Resolver nombre de fichero de forma robusta (case-insensitive) y usar ruta absoluta
        cwd_files = os.listdir('.')
        target = None
        # Si se pasó con extensión exacta y existe, usarlo
        if module_name in cwd_files:
            target = module_name
        else:
            # Buscar coincidencia case-insensitive
            lower_target = module_name.lower()
            for f in cwd_files:
                if f.lower() == lower_target:
                    target = f
                    break
            # Si no se encontró, intentar añadir .py
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
        
        # Forzar recarga
        st.rerun() # <-- CORRECCIÓN A st.rerun()
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

# === PANTALLA DE LOGIN MEJORADA ===
def show_login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Contenedor centralizado para el login
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # Logo Centrado
        st.markdown("""
        <div class="logo-container">
            <div class="logo-text"> ACCESO SEGURO</div>
            <div class="logo-subtitle">SISTEMA FRONTERA ENERGY</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Imagen (Centrada)
        st.markdown(
            "<div style='text-align:center; margin-bottom: 2rem;'>"
            "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='280'/>"
            "</div>",
            unsafe_allow_html=True
        )
        
        # Formulario de login
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("👤 USUARIO", placeholder="Ingresa tu usuario")
            password = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña")
            submit = st.form_submit_button("🔑 INICIAR SESIÓN", use_container_width=True)
            
            if submit:
                if authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"✅ ¡Bienvenido, {username.upper()}!")
                    time.sleep(0.5)
                    st.rerun() # <-- CORRECCIÓN A st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas. Inténtalo de nuevo.")
        
        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 3rem; opacity: 0.6;'>
            <small>Sistema de Monitoreo & Control | © 2025 Frontera Energy</small>
        </div>
        """, unsafe_allow_html=True)

# === DASHBOARD PRINCIPAL MEJORADO ===
def show_dashboard():
    # Header del Dashboard
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">CENTRO DE CONTROL</h1>
        <p class="dashboard-subtitle">Bienvenido, **{st.session_state.username.upper()}**. Selecciona el módulo a iniciar.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid de Módulos
    col1, col2 = st.columns(2, gap="large")
    
    # --- MÓDULO 1: INDICADORES ALS ---
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
        
        # El botón debe estar fuera del markdown para ser interactivo
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("🚀 INICIAR INDICADORES", key="btn_indicadores", use_container_width=True):
            open_module("indicadores.py")
    
    # --- MÓDULO 2: EVALUACIÓN ESP ---
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
        
        # El botón debe estar fuera del markdown para ser interactivo
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        if st.button("🚀 INICIAR EVALUACIÓN", key="btn_evaluacion", use_container_width=True):
            open_module("evaluacion.py")
    
    # --- INFO ADICIONAL ---
    st.markdown("---")
    
    col_info1, col_info2, col_info3 = st.columns(3, gap="large")
    
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
    
    # Verificación de archivos (Mejorada con Expander)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📁 VERIFICACIÓN DE ARCHIVOS DEL SISTEMA"):
        col_check1, col_check2 = st.columns(2)
        
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
    
    # Botón de cerrar sesión
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_logout1, col_logout2, col_logout3 = st.columns([2, 2, 2])
    with col_logout2:
        if st.button("🚪 CERRAR SESIÓN", key="btn_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun() # <-- CORRECCIÓN A st.rerun()

# === LÓGICA PRINCIPAL ===
def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
