# === IMPORTS ===
import streamlit as st
from datetime import datetime
import time
import subprocess
import sys
import os
import importlib.util
import tema

# ====================================================================
# 🚀 1. FORZAR MODO DARK DE STREAMLIT (REQUIERE AJUSTAR EL ARCHIVO .streamlit/config.toml)
# Streamlit prioriza el archivo de configuración. Para garantizar el tema oscuro,
# se asume que existe un archivo .streamlit/config.toml con las siguientes líneas:
# [theme]
# base = "dark"
# ====================================================================

# Si no puedes modificar config.toml, puedes intentar usar st.markdown para sobrescribir
# los colores globales de Streamlit, pero es menos robusto:
# st.set_page_config(..., theme={"base": "dark"})  # Esta opción no está disponible directamente en st.set_page_config

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="🚀 Sistema Frontera Energy",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === COLORES Y TEMA (Usando `tema.py`) ===
# Usar las constantes centralizadas del módulo `tema` para mantener consistencia
COLOR_PRIMARIO = getattr(tema, 'COLOR_PRINCIPAL', '#00FF99')
# Elegimos un color de acento derivado del tema; usar COLOR_DASH_CYAN si existe
COLOR_ACENTO = getattr(tema, 'COLOR_DASH_CYAN', getattr(tema, 'COLOR_AZUL_CIBER', '#00D9FF'))
COLOR_FONDO_OSCURO = getattr(tema, 'COLOR_FONDO_OSCURO', '#0A0E27')
COLOR_SOMBRA = getattr(tema, 'COLOR_GLOW_SUAVE', 'rgba(0, 255, 153, 0.5)')
COLOR_FUENTE = getattr(tema, 'COLOR_FUENTE', '#E8F5E9')

# === ESTILOS CSS - COMPACTACIÓN Y CIBER PUNK MINIMALISTA ===
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
    
    /* 1. COMPACTACIÓN GLOBAL y MODO DARK */
    .stApp {{
        background: linear-gradient(135deg, var(--color-fondo-oscuro) 0%, #0d1117 50%, #0a0e27 100%);
        background-attachment: fixed;
    }}
    
    /* Reducir el padding general del contenedor principal (MÁS COMPACTO) */
    .main .block-container {{
        padding-top: 1.5rem; 
        padding-bottom: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 95%; /* Usar casi todo el ancho */
    }}
    
    /* Reducir el margen de los contenedores internos (MENOS ESPACIO ENTRE ELEMENTOS) */
    div[data-testid="stVerticalBlock"] {{
        gap: 0.5rem; 
    }}
    
    /* Reducir el espacio entre columnas */
    div[data-testid="column"] {{
        padding: 0 0.5rem !important; 
    }}
    
    /* Ocultar elementos nativos de Streamlit (se mantiene el control con session_state) */
    #MainMenu, footer {{
        visibility: hidden !important; 
    }}
    
    /* 2. LOGO */
    .logo-container {{
        text-align: center;
        margin-bottom: 2rem; /* Compactado */
    }}
    
    .logo-text {{
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem; /* Compactado */
        font-weight: 900;
        background: linear-gradient(135deg, var(--color-primario), var(--color-acento));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px var(--color-sombra); /* Sombra reducida (menos ruido) */
        letter-spacing: 3px;
    }}
    
    /* 3. INPUTS Y BOTONES (más limpios) */
    .stTextInput > div > div > input {{
        background: rgba(10, 14, 39, 0.9) !important;
        border: 1px solid rgba(0, 255, 153, 0.3) !important; /* Borde más fino */
        border-radius: 8px; /* Borde menos redondo */
        padding: 1rem; /* Compactado */
        font-size: 1rem;
    }}
    
    .stTextInput > label {{
        margin-bottom: 0.3rem; /* Compactado */
    }}
    
    .stButton > button {{
        padding: 1rem; /* Compactado */
        font-size: 1rem;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0, 255, 153, 0.3); /* Sombra reducida */
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px); /* Menos movimiento */
        box-shadow: 0 8px 25px rgba(0, 255, 153, 0.5); 
    }}
    
    /* 4. DASHBOARD HEADER (Más compacto y sutil) */
    .dashboard-header {{
        background: rgba(0, 255, 153, 0.05); 
        border: 1px solid rgba(0, 255, 153, 0.2);
        border-radius: 15px; /* Menos redondo */
        padding: 1.5rem 2rem; /* Compactado */
        margin-bottom: 1.5rem; /* Compactado */
        backdrop-filter: blur(5px); /* Blur más sutil */
        box-shadow: 0 0 30px rgba(0, 255, 153, 0.2); /* Sombra más sutil */
    }}
    
    .dashboard-title {{
        font-size: 2rem; /* Compactado */
        letter-spacing: 3px;
        text-shadow: none; /* Eliminar sombra de texto (menos ruido) */
    }}
    
    .dashboard-subtitle {{
        font-size: 1rem; /* Compactado */
        margin-top: 0.5rem;
    }}
    
    /* 5. CARDS (Módulos - Más compactos y nítidos) */
    .module-card {{
        background: rgba(10, 14, 39, 0.8);
        border: 1px solid rgba(0, 255, 153, 0.4);
        border-radius: 15px;
        padding: 1.5rem; /* Compactado */
        backdrop-filter: blur(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
        min-height: 280px; /* Altura mínima reducida */
    }}
    
    .module-card:hover {{
        transform: scale(1.01); /* Movimiento muy sutil */
        box-shadow: 0 10px 30px rgba(0, 255, 153, 0.4);
    }}
    
    .module-icon {{
        font-size: 3.5rem; /* Compactado */
        margin-bottom: 0.8rem;
        filter: drop-shadow(0 0 8px var(--color-sombra)); /* Sombra reducida */
    }}
    
    .module-title {{
        font-size: 1.5rem; /* Compactado */
        margin-bottom: 0.8rem;
    }}
    
    .module-description {{
        font-size: 0.9rem; /* Compactado */
        line-height: 1.5;
    }}
    
    .module-badge {{
        padding: 0.4rem 0.8rem; /* Compactado */
        font-size: 0.7rem;
        top: 1rem; /* Compactado */
        right: 1rem; /* Compactado */
    }}
    
    /* 6. INFO CARDS (pequeñas estadísticas - Más compactas) */
    .info-card {{
        padding: 1rem; /* Compactado */
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }}
    
    .info-icon {{
        font-size: 2rem; /* Compactado */
    }}
    
    .info-value {{
        font-size: 1.5rem; /* Compactado */
    }}
    
    .info-label {{
        font-size: 0.8rem; /* Compactado */
    }}

    /* 7. EXPANDER (Compacto y más limpio) */
    .stExpander {{
        border-radius: 8px; /* Menos redondo */
    }}

    .stExpander > div:first-child > div:first-child {{
        padding: 0.8rem 1rem !important; /* Compactado */
        border-radius: 8px;
    }}
    
</style>
""", unsafe_allow_html=True)

# === INICIALIZACIÓN DE SESSION STATE (SIN CAMBIOS) ===
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

# --- FUNCIONES DE VISIBILIDAD, AUTENTICACIÓN Y APERTURA (SIN CAMBIOS ESTRUCTURALES) ---

def _apply_streamlit_ui_visibility():
    # If we only want to hide the main menu (e.g., for guest users), apply minimal CSS
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

    # Otherwise fall back to the full UI visibility toggle
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

# === LÓGICA DE EJECUCIÓN DEL MÓDULO (IN-PROCESS) ===
if 'launch_module_path' in st.session_state and st.session_state.get('launch_module_path'):
    launch_path = st.session_state.get('launch_module_path')
    launch_name = st.session_state.get('launch_module_name', os.path.splitext(os.path.basename(launch_path))[0])

    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
                f"<h2 style='color: var(--color-acento); margin:0; font-family: 'Orbitron', monospace;'>EJECUTANDO MÓDULO: {launch_name.upper()}</h2>"
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
        # Limpiar flags que podrían forzar la recarga de otras páginas (evitar bucles)
        for _k in ['show_resumen_publico', 'go_to_indicadores']:
            if _k in st.session_state:
                try:
                    del st.session_state[_k]
                except Exception:
                    pass

        # Mostrar info de depuración/resuelto (si existe)
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

        # Si el módulo define una función de entrada, llamarla explícitamente.
        # Esto cubre módulos como `resumen_publico.py` que llaman a `show_resumen()`
        # sólo cuando se ejecutan como script. Al importar por ruta, __name__ != '__main__',
        # por eso llamamos a la función si existe.
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
    
    st.stop() # Bloquear la ejecución del resto del script

# === FUNCIÓN DE AUTENTICACIÓN ===
def authenticate(username, password):
    """Autenticación simple"""
    users = {
        "lenin": "1",
        "practicante": "2",
        "invitado": "",
        "jaime": "1",
        "ajm": "1",
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
        # Guardar la ruta y el nombre resuelto para depuración
        st.session_state['launch_module_path'] = full_path
        st.session_state['launch_module_name'] = os.path.splitext(os.path.basename(full_path))[0]
        st.session_state['launch_module_resolved_filename'] = os.path.basename(target)

        # Guardar debug info para inspección tras rerun
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

        # Forzar recarga
        st.rerun() # <-- CORRECCIÓN A st.rerun()
        return True
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return False

# === PANTALLA DE LOGIN MEJORADA Y COMPACTADA ===
def show_login():
    st.markdown("<br><br>", unsafe_allow_html=True) # Menos espacio
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5]) # Columna central más ancha
    
    with col2:
        # Logo Centrado
        st.markdown("""
        <div class="logo-container">
            <div class="logo-text"> ACCESO SEGURO</div>
            <div class="logo-subtitle">SISTEMA FRONTERA ENERGY</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Imagen (Centrada) - Logo (local o fallback remoto)
        try:
            from ui_helpers import get_logo_img_tag
            logo_html = get_logo_img_tag(width=200, style='filter: drop-shadow(0 0 8px rgba(0,0,0,0.6));')
            st.markdown(f"<div style='text-align:center; margin-bottom: 1.5rem;'>{logo_html}</div>", unsafe_allow_html=True)
        except Exception:
            st.markdown(
                "<div style='text-align:center; margin-bottom: 1.5rem;'>"
                "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='200'/>"
                "</div>",
                unsafe_allow_html=True
            )
        
        # Formulario de login
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("👤 USUARIO", placeholder="Ingresa tu usuario", label_visibility="collapsed") # Ocultar label nativo
            password = st.text_input("🔒 CONTRASEÑA", type="password", placeholder="Ingresa tu contraseña", label_visibility="collapsed") # Ocultar label nativo
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
        
        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 1.5rem; opacity: 0.5;'>
            <small>Sistema de Monitoreo & Control AJM | ©  Frontera Energy</small>
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
    
    # Grid de Módulos (usando un grid de 2 columnas)
    col1, col2 = st.columns(2, gap="medium") # Espacio reducido
    
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
        
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True) # Compactado
        # Dos botones: uno para abrir el módulo Indicadores y otro para ir al Resumen Público
        col_btn1, col_btn2 = st.columns([1, 1], gap='small')
        with col_btn1:
            if st.button("🚀 INICIAR INDICADORES", key="btn_indicadores_dashboard", use_container_width=True):
                open_module("indicadores.py")
        with col_btn2:
            if st.button("📊 VER RESUMEN PÚBLICO", key="btn_resumen_publico", use_container_width=True):
                open_module("resumen_publico.py")
    
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
        
        st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True) # Compactado
        if st.button("🚀 INICIAR EVALUACIÓN", key="btn_evaluacion", use_container_width=True):
            open_module("evaluacion.py")
    
    # --- INFO ADICIONAL ---
    st.markdown("---") # Separador
    
    col_info1, col_info2, col_info3 = st.columns(3, gap="small") # Espacio reducido
    
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
    st.markdown("<br>", unsafe_allow_html=True) # Espacio reducido
    col_logout1, col_logout2, col_logout3 = st.columns([1, 2, 1])
    with col_logout2:
        if st.button("🚪 CERRAR SESIÓN", key="btn_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state['hide_main_menu_only'] = False
            st.rerun()

# === LÓGICA PRINCIPAL (SIN CAMBIOS) ===
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