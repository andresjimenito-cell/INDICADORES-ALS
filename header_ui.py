"""
header_ui.py
============
Renderiza el header principal de la aplicación (hero, logo, fecha).
Inicializa las claves de session_state necesarias.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

import tema
from config import COLOR_PRINCIPAL


def _init_session_state():
    """Inicializa las claves de session_state necesarias para la app."""
    defaults = {
        'df_forma9_raw':          None,
        'df_bd_raw':              None,
        'df_forma9_calculated':   None,
        'df_bd_calculated':       None,
        'reporte_runes':          None,
        'reporte_run_life':       None,
        'reporte_fallas':         None,
        'df_trabajo':             None,
        'verificaciones':         None,
        'unique_pozos':           [],
        'unique_als':             [],
        'unique_activos':         [],
        'fecha_evaluacion_state': datetime.now().date(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_header():
    """
    Renderiza el bloque de cabecera premium (col1: hero, col2: logo grande).
    También inicializa el session_state y aplica estilos del sidebar.
    """
    _init_session_state()

    col1, col2 = st.columns([4, 1])

    with col1:
        # Fecha de evaluación
        try:
            fecha_display = st.session_state.get('fecha_eval', datetime.now().date())
            fecha_str = pd.to_datetime(fecha_display).strftime('%d %b %Y')
        except Exception:
            fecha_str = ''

        # Logo
        try:
            from ui_helpers import get_logo_img_tag
            logo_html = get_logo_img_tag(width=100, style='height:80px; filter: drop-shadow(0 0 10px rgba(200,43,150,0.5));')
        except Exception:
            logo_html = "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='100'/>"

        header_style = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;800&family=Inter:wght@200;300;400;500;600;700&display=swap');
.hero-container-base {
    position:relative; width:100%; margin:1rem 0 2.5rem 0; overflow:hidden;
    border-radius:1.5rem; background:rgba(10,14,39,0.7); padding:2.5rem;
    border:1px solid rgba(255,255,255,0.1); backdrop-filter:blur(25px);
    box-shadow:0 25px 50px -12px rgba(0,0,0,0.5); color:white !important; font-family:'Inter',sans-serif;
}
.hero-bg-glow {
    position:absolute; inset:0;
    background:radial-gradient(circle at 20% 30%,rgba(19,91,236,0.15),transparent 50%),
               radial-gradient(circle at 80% 70%,rgba(0,242,255,0.1),transparent 50%);
    pointer-events:none;
}
.hero-flex-layout { position:relative; display:flex; align-items:center; justify-content:space-between; gap:2rem; z-index:10; }
.hero-left-side { display:flex; align-items:center; gap:2rem; }
.logo-aura-effect { position:relative; display:flex; align-items:center; justify-content:center; }
.logo-aura-effect::before {
    content:''; position:absolute; width:120%; height:120%;
    background:radial-gradient(circle,rgba(19,91,236,0.4) 0%,transparent 70%);
    filter:blur(15px); z-index:0;
}
.header-text-main { display:flex; flex-direction:column; }
.header-upper-tag {
    font-size:10px; font-weight:800; color:#00f2ff; text-transform:uppercase;
    letter-spacing:0.4em; margin-bottom:0.5rem; opacity:0.8;
    display:flex; align-items:center; gap:10px;
}
.header-upper-tag::before { content:''; height:1px; width:30px; background:linear-gradient(to right,#00f2ff,transparent); }
.main-title-text { font-family:'Outfit',sans-serif; font-size:3.5rem; font-weight:900; line-height:1; margin:0; letter-spacing:-0.02em; }
.title-gradient-als {
    background:linear-gradient(-45deg,#135bec,#00f2ff,#135bec,#00f2ff);
    background-size:300% 300%; -webkit-background-clip:text; background-clip:text;
    -webkit-text-fill-color:transparent; animation:flowGradient 5s ease infinite;
}
@keyframes flowGradient { 0%{background-position:0% 50%;} 50%{background-position:100% 50%;} 100%{background-position:0% 50%;} }
.meta-info-row { display:flex; align-items:center; gap:1.5rem; margin-top:1.25rem; }
.active-status-tag {
    display:flex; align-items:center; gap:0.5rem;
    background:rgba(0,242,255,0.1); border:1px solid rgba(0,242,255,0.3);
    padding:4px 12px; border-radius:20px;
}
.pulse-dot { width:6px; height:6px; background:#00f2ff; border-radius:50%; box-shadow:0 0 10px #00f2ff; animation:pulse 2s infinite; }
@keyframes pulse { 0%{opacity:1;transform:scale(1);} 50%{opacity:0.4;transform:scale(1.2);} 100%{opacity:1;transform:scale(1);} }
.status-txt { font-size:9px; font-weight:900; color:#00f2ff; text-transform:uppercase; letter-spacing:0.1em; }
.version-txt { font-size:10px; color:rgba(255,255,255,0.4); letter-spacing:0.2em; text-transform:uppercase; font-style:italic; }
.date-display-box {
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1);
    padding:1.25rem 2rem; border-radius:1.25rem; text-align:right; min-width:220px;
}
.date-lbl { font-size:10px; font-weight:700; color:rgba(255,255,255,0.5); text-transform:uppercase; letter-spacing:0.2em; display:block; margin-bottom:0.5rem; }
.date-val { font-family:'Outfit',sans-serif; font-size:2rem; font-weight:800; color:white; letter-spacing:0.05em; }
@media (max-width:1024px) {
    .hero-flex-layout { flex-direction:column; text-align:center; }
    .hero-left-side { flex-direction:column; }
    .header-upper-tag { justify-content:center; }
    .meta-info-row { justify-content:center; }
    .date-display-box { text-align:center; }
}
</style>
"""
        hero_html = f"""
<div class="hero-container-base">
    <div class="hero-bg-glow"></div>
    <div class="hero-flex-layout">
        <div class="hero-left-side">
            <div class="logo-aura-effect">
                <div style="position:relative;z-index:2;">{logo_html}</div>
            </div>
            <div class="header-text-main">
                <div class="header-upper-tag">Advanced Analytics System</div>
                <h1 class="main-title-text">
                    <span>INDICADORES</span>
                    <span class="title-gradient-als">ALS</span>
                </h1>
                <div class="meta-info-row">
                    <div class="active-status-tag">
                        <span class="pulse-dot"></span>
                        <span class="status-txt">Node Active</span>
                    </div>
                    <span class="version-txt">Matrix v5.2.4</span>
                </div>
            </div>
        </div>
        <div class="date-display-box">
            <span class="date-lbl">Fecha de Evaluación</span>
            <div class="date-val">{fecha_str.upper()}</div>
        </div>
    </div>
</div>
"""
        st.markdown(header_style, unsafe_allow_html=True)
        st.markdown(hero_html,    unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        try:
            from ui_helpers import get_logo_img_tag
            logo_html_right = get_logo_img_tag(width=280, style='filter:drop-shadow(0 0 10px rgba(200,43,150,0.5));')
        except Exception:
            logo_html_right = "<img src='https://www.fronteraenergy.ca/wp-content/uploads/2023/05/logo-frontera-white.png' width='280'/>"
        st.markdown(logo_html_right, unsafe_allow_html=True)
        st.markdown("</div>",        unsafe_allow_html=True)
