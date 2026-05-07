"""
styles.py
=========
Centraliza TODA la inyección de CSS de la aplicación.
Expone apply_all_styles() que debe llamarse UNA VEZ al inicio del script principal.
"""

import html as html_module
import streamlit as st
import tema
from config import (
    COLOR_PRINCIPAL, COLOR_FUENTE, COLOR_FONDO_OSCURO, COLOR_FONDO_CONTENEDOR,
    COLOR_MAGENTA_NEON, COLOR_AZUL_CIBER, COLOR_GLOW_SUAVE, COLOR_GRID,
)
from dashboard_css import get_dashboard_css


def inject_custom_css():
    """Inyecta CSS base del sidebar y layout sin modificar comportamiento por defecto."""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700;900&family=Inter:wght@300;400;600&display=swap');

        [data-testid="stAppViewContainer"] {{ padding: 0 !important; margin: 0 !important; }}
        [data-testid="stMainBlockContainer"] {{ padding: 1rem !important; box-sizing: border-box !important; }}
        [data-testid="stToolbar"] {{ display: block !important; visibility: visible !important; }}
        [data-testid="stHeader"] {{ display: block !important; visibility: visible !important; }}

        .stApp {{
            background-color: #0a0e27 !important;
            background-image: 
                linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%),
                radial-gradient(circle at 10% 20%, rgba(19,91,236,0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(0,242,255,0.05) 0%, transparent 40%) !important;
            background-size: 100% 4px, 100% 100%, 100% 100% !important;
            font-family: 'Inter', sans-serif !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: #060a1e !important;
            background-image: radial-gradient(circle at 0% 0%, rgba(0,242,255,0.08) 0%, transparent 50%),
                              linear-gradient(180deg, #060a1e 0%, #030612 100%) !important;
            border-right: 1px solid rgba(0,242,255,0.2) !important;
            box-shadow: 10px 0 30px rgba(0,0,0,0.5) !important;
        }}
        [data-testid="stSidebar"]::before {{
            content: " "; position: absolute; top:0; left:0; bottom:0; right:0;
            background: linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.1) 50%);
            z-index:100; background-size:100% 4px; pointer-events:none; opacity:0.2;
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap:1.2rem !important; padding:2rem 1rem !important; }}
        [data-testid="stSidebar"] .stMarkdown p {{ font-family:'Inter',sans-serif !important; color:#94a3b8 !important; font-size:0.9rem !important; }}
        [data-testid="stSidebar"] label {{
            font-family:'Outfit',sans-serif !important; color:#00f2ff !important; text-transform:uppercase !important;
            letter-spacing:0.15em !important; font-weight:700 !important; font-size:0.7rem !important;
            margin-bottom:0.5rem !important; text-shadow:0 0 5px rgba(0,242,255,0.2) !important;
        }}
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {{
            background-color:rgba(10,15,30,0.7) !important; border:1px solid rgba(0,242,255,0.2) !important;
            border-radius:12px !important; backdrop-filter:blur(10px) !important; transition:all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
        }}
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"]:hover {{
            border-color:#00f2ff !important; background-color:rgba(10,15,30,0.9) !important;
            box-shadow:0 0 20px rgba(0,242,255,0.15) !important; transform:translateY(-1px);
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
            font-family:'Outfit',sans-serif !important; color:#ff00ff !important; text-transform:uppercase !important;
            letter-spacing:0.2em !important; font-weight:900 !important; font-size:1.1rem !important;
            margin-top:1rem !important; margin-bottom:1.5rem !important;
            text-shadow:0 0 15px rgba(255,0,255,0.3) !important;
            border-bottom:1px solid rgba(255,0,255,0.2); padding-bottom:0.5rem;
        }}
        [data-testid="stSidebar"] ::-webkit-scrollbar {{ width:4px; }}
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{ background:rgba(0,242,255,0.2); border-radius:10px; }}

        .stPlotlyChart {{ background:transparent !important; border-radius:15px !important; box-shadow:0 10px 30px rgba(0,0,0,0.4) !important; }}
        footer {{ visibility:hidden !important; }}
    </style>
    """, unsafe_allow_html=True)


def _apply_base_css():
    """Aplica el bloque CSS de tarjetas, botones e inputs."""
    _container_bg = COLOR_FONDO_CONTENEDOR if COLOR_FONDO_CONTENEDOR else 'transparent'
    lines = ["<style>"]
    if COLOR_FONDO_OSCURO:
        lines.append(f".stApp {{ background-color: {COLOR_FONDO_OSCURO} !important; }}")
        if COLOR_FUENTE:
            lines.append(f".stApp, .stApp * {{ color: {COLOR_FUENTE} !important; }}")
    lines.append(f"h1, h2, h3 {{ color: {COLOR_PRINCIPAL} !important; text-shadow: 0 2px 10px {COLOR_PRINCIPAL}33; }}")
    lines.append(
        f"div[data-testid=\"stMetric\"] {{ background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)) !important; "
        f"backdrop-filter: blur(6px) saturate(120%); border-radius: 12px !important; padding: 12px !important; "
        f"margin-bottom: 12px !important; box-shadow: 0 10px 30px {COLOR_PRINCIPAL}33, 0 4px 8px rgba(0,0,0,0.25) !important; "
        f"border: 1px solid rgba(255,255,255,0.03) !important; }}"
    )
    lines.append(f".stDataFrame, .stTable {{ background: {_container_bg} !important; color: {COLOR_FUENTE} !important; border-radius: 10px !important; box-shadow: 0 8px 30px rgba(0,0,0,0.25) !important; }}")
    lines.append(
        f".stButton>button {{ background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important; "
        f"border: 1px solid {COLOR_PRINCIPAL} !important; color: {COLOR_PRINCIPAL} !important; border-radius: 10px !important; "
        f"padding: 10px 14px !important; box-shadow: 0 6px 18px rgba(0,0,0,0.35), 0 2px 6px rgba(0,0,0,0.2) inset !important; "
        f"transition: transform 180ms ease, box-shadow 180ms ease; }}"
    )
    lines.append(
        f".stButton>button:hover {{ transform: translateY(-3px) rotateX(1deg); "
        f"box-shadow: 0 18px 50px {COLOR_PRINCIPAL}33, 0 6px 20px rgba(0,0,0,0.45) !important; "
        f"color: {tema.COLOR_BLANCO} !important; background: linear-gradient(90deg, {COLOR_PRINCIPAL}, {tema.SECUENCIA_COLORES_GRAFICOS[6]}) !important; }}"
    )
    lines.append(".stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input, .stFileUploader { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.04) !important; border-radius: 8px !important; padding: 8px !important; box-shadow: inset 0 2px 6px rgba(0,0,0,0.2); }")
    lines.append(".plotly .bg, .plotly .plotbg, .plotly .bgrect, .plotly .cartesianlayer .bg { fill: rgba(0,0,0,0) !important; }")
    lines.append(".plotly svg { background: transparent !important; }")
    lines.append(".compact-card { background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); padding: 8px 12px; border-radius: 10px; display: inline-block; font-weight:700; color: inherit; box-shadow: 0 8px 20px rgba(0,0,0,0.25); margin-bottom:8px; }")
    lines.append(".compact-card, .upload-card { transition: all 0.3s ease; display: inline-block; padding: 18px 24px; border-radius: 16px; font-weight: 700; color: #ffffff; background-color: #0a0e27; border: 1px solid rgba(41,1,94,0.4); box-shadow: 0 0 3px rgba(41,1,94,0.5), inset 0 0 2px rgba(41,1,94,0.3); cursor: default; }")
    lines.append(".compact-card:hover, .upload-card:hover { box-shadow: 0 0 6px #C82B96, inset 0 0 3px rgba(217,0,206,0.5); transform: translateY(-1px); }")
    lines.append(".stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input, .stFileUploader { min-height:48px; padding:12px 14px !important; font-size:14px !important; border-radius:10px !important; }")
    lines.append(".upload-area { padding:10px; border-radius:10px; background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); border:1px dashed rgba(255,255,255,0.06); box-shadow: inset 0 4px 12px rgba(0,0,0,0.06); margin-top:8px; }")
    lines.append("[data-testid=\"stToolbar\"] { display: block !important; visibility: visible !important; }")
    lines.append("[data-testid=\"stHeader\"] { display: block !important; visibility: visible !important; }")
    lines.append("html, body { overflow-x: hidden !important; max-width: 100vw !important; }")
    lines.append("[data-testid=\"stAppViewContainer\"] { overflow-x: hidden !important; max-width: 100vw !important; }")
    lines.append("[data-testid=\"stMainBlockContainer\"] { overflow-x: hidden !important; max-width: 100% !important; box-sizing: border-box !important; }")
    lines.append("[data-testid=\"stVerticalBlock\"], [data-testid=\"stHorizontalBlock\"] { overflow-x: hidden !important; max-width: 100% !important; box-sizing: border-box !important; }")
    lines.append("[data-testid=\"column\"] { overflow-x: hidden !important; max-width: 100% !important; box-sizing: border-box !important; }")
    lines.append(".stDataFrame, .stTable { max-width: 100% !important; overflow-x: auto !important; box-sizing: border-box !important; }")
    lines.append("div.row-widget { overflow-x: hidden !important; max-width: 100% !important; }")
    lines.append("</style>")
    st.markdown('\n'.join(lines), unsafe_allow_html=True)


def _apply_page_css():
    """Aplica el bloque CSS de página: tipografía, métricas, tablas, inputs, gráficos."""
    page_css = ["<style>"]
    page_css.append(f"""
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    body, .stApp {{ background-color: {COLOR_FONDO_OSCURO} !important; font-family: 'Rajdhani', sans-serif; color: {COLOR_FUENTE}; }}
    .main .block-container {{ max-width: 2000px; padding-left: 1rem; padding-right: 2rem; margin-left: 0rem; margin-right: 2rem; }}
    """)
    page_css.append(f"""
    h1, h2, h3 {{
        font-family: 'Orbitron', monospace !important; font-weight: 700;
        background: linear-gradient(90deg, {COLOR_MAGENTA_NEON}, {COLOR_AZUL_CIBER});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: none; text-transform: uppercase; letter-spacing: 3px;
    }}
    """)
    page_css.append(f"""
    div[data-testid="stMetric"] {{
        background: rgba(12,20,50,0.7) !important; backdrop-filter: blur(8px);
        border-radius: 15px !important; padding: 20px !important; margin-bottom: 20px !important;
        border: 1px solid {COLOR_MAGENTA_NEON}33 !important; box-shadow: 0 0 25px {COLOR_GLOW_SUAVE} !important; transition: all 0.3s;
    }}
    div[data-testid="stMetric"]:hover {{ box-shadow: 0 0 35px {COLOR_MAGENTA_NEON}88 !important; transform: translateY(-3px); }}
    div[data-testid="stMetricValue"] {{ font-family:'Orbitron',monospace; color:{COLOR_AZUL_CIBER} !important; text-shadow:0 0 10px {COLOR_AZUL_CIBER}55; }}
    div[data-testid="stMetricLabel"] {{ color:{COLOR_FUENTE} !important; font-weight:600; text-transform:uppercase; letter-spacing:1px; }}
    """)
    page_css.append(f"""
    /* Estilo Premium para DataFrames y Tablas (UI Style) */
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataFrame, .stTable {{
        background: rgba(10, 14, 39, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(0, 242, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 242, 255, 0.05) !important;
        transition: all 0.3s ease;
    }}
    
    [data-testid="stDataFrame"]:hover, [data-testid="stTable"]:hover {{
        border-color: rgba(0, 242, 255, 0.4) !important;
        box-shadow: 0 15px 50px rgba(0, 242, 255, 0.1), inset 0 0 30px rgba(0, 242, 255, 0.08) !important;
    }}

    /* Estilizado de las cabeceras de tabla (ag-grid y estándar) */
    .stDataFrame th, .stTable th {{
        background: rgba(0, 242, 255, 0.05) !important;
        color: #00f2ff !important;
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.75rem !important;
        border-bottom: 2px solid rgba(0, 242, 255, 0.3) !important;
    }}

    .stDataFrame td, .stTable td {{
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-size: 0.85rem !important;
        color: rgba(255, 255, 255, 0.85) !important;
    }}

    /* Inputs estilo HUD */
    .stSelectbox>div>div, .stTextInput>div>div>input, .stDateInput>div>input,
    .stFileUploader, div[data-testid="stFileUploadDropzone"] {{
        background: rgba(15, 23, 42, 0.8) !important; 
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        color: #fff !important; 
        border-radius: 10px !important; 
        padding: 8px !important; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }}
    
    .stSelectbox>div>div:hover, .stTextInput>div>div>input:hover {{
        border-color: #00f2ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.2) !important;
    }}
    """)
    page_css.append("""
    .stPlotlyChart > div[role='figure'] { background: rgba(0,0,0,0) !important; border-radius: 10px; }
    .plotly .bg, .plotly .plotbg, .plotly .bgrect, .plotly .cartesianlayer .bg { fill: rgba(0,0,0,0) !important; }
    .plotly svg { background: transparent !important; }
    .plotly .legend rect { fill: rgba(0,0,0,0) !important; stroke: rgba(0,0,0,0) !important; }
    .plotly .legend text, .plotly .legendtitle { fill: currentColor !important; }
    /* Estilo Premium para TABS */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px !important;
        background-color: rgba(10, 14, 39, 0.5) !important;
        padding: 10px !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        color: rgba(255, 255, 255, 0.6) !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        border: 1px solid transparent !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        padding: 0 20px !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(0, 242, 255, 0.1), rgba(0, 242, 255, 0.05)) !important;
        color: #00f2ff !important;
        border: 1px solid rgba(0, 242, 255, 0.4) !important;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.15) !important;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: #fff !important;
        background-color: rgba(255, 255, 255, 0.08) !important;
    }}

    /* Contenedores de Gráficos */
    .stPlotlyChart, [data-testid="stGraphVis"] {{
        background: rgba(15, 23, 42, 0.3) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 10px !important;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4) !important;
    }}

    div[data-testid="stVerticalBlock"], div[data-testid="stHorizontalBlock"],
    div[data-testid="column"], section[data-testid="stSidebar"],
    .element-container, .stMarkdown, .stDataFrame {
        position: relative; z-index: 100 !important;
    }
    """)
    page_css.append("</style>")
    st.markdown('\n'.join(page_css), unsafe_allow_html=True)


def _apply_dashboard_css():
    """Inyecta el CSS del dashboard (header, animaciones, tarjetas)."""
    st.markdown(get_dashboard_css(), unsafe_allow_html=True)

    dashboard_css = f"""
<style>
:root {{
    --color-primary: {tema.COLOR_DASH_PRIMARY};
    --color-secondary: {tema.COLOR_DASH_SECONDARY};
    --color-accent-pink: {tema.COLOR_DASH_PINK};
    --color-accent-orange: {tema.COLOR_DASH_ORANGE};
    --color-accent-cyan: {tema.COLOR_DASH_CYAN};
    --color-accent-green: {tema.COLOR_DASH_GREEN};
    --color-accent-yellow: {tema.COLOR_DASH_YELLOW};
    --color-dark: {tema.COLOR_DASH_DARK};
    --color-light: {tema.COLOR_DASH_LIGHT};
    --gradient-fire: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 25%, #c44569 50%, #a73667 75%, #8b2760 100%);
    --gradient-ocean: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    --gradient-sunset: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    --gradient-aurora: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    --gradient-cosmic: linear-gradient(135deg, #5f2c82 0%, #49a09d 100%);
    --gradient-neon: linear-gradient(135deg, #00f260 0%, #0575e6 100%);
    --radius-xl: 24px; --radius-mega: 32px;
    --shadow-glow: 0 0 40px rgba(99,102,241,0.5);
    --shadow-intense: 0 20px 60px rgba(0,0,0,0.4);
    --transition-fast: 0.3s cubic-bezier(0.4,0,0.2,1);
    --transition-smooth: 0.6s cubic-bezier(0.34,1.56,0.64,1);
}}
@keyframes float {{ 0%,100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} }}
@keyframes pulse-glow {{
    0%,100% {{ box-shadow: 0 0 20px rgba(99,102,241,0.5),0 0 40px rgba(139,92,246,0.3); }}
    50% {{ box-shadow: 0 0 40px rgba(99,102,241,0.8),0 0 80px rgba(139,92,246,0.6); }}
}}
@keyframes gradient-shift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
@keyframes shimmer {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(100%); }} }}
@keyframes rotate-border {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
.stApp {{ background: transparent; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
.main .block-container {{ padding: 1.2rem 1.8rem; max-width: 100%; }}
.dashboard-header {{
    background: {tema.COLOR_HEADER_BG}; padding: 1.5rem 2rem; border-radius: 8px; margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); border-bottom: 4px solid {tema.COLOR_HEADER_BORDER};
    color: {tema.COLOR_HEADER_TEXT}; position: relative; overflow: hidden;
}}
.dashboard-header::before {{
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate-border 15s linear infinite;
}}
.dashboard-header:hover {{
    transform: translateY(-8px) scale(1.01);
    box-shadow: 0 0 100px rgba(236,0,212,0.8), 0 30px 100px rgba(0,0,0,0.6), inset 0 0 150px rgba(255,255,255,0.15);
}}
.header-title {{ font-size:3.5rem; font-weight:900; background:linear-gradient(135deg,{tema.COLOR_BLANCO} 0%,{tema.COLOR_PURPLE_LIGHT} 50%,{tema.COLOR_DASH_PINK} 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; text-shadow:0 5px 20px rgba(255,255,255,0.3); letter-spacing:-1px; position:relative; z-index:1; }}
.header-date {{ background:rgba(255,255,255,0.15); backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px); padding:1rem 2.5rem; border-radius:50px; font-weight:800; font-size:1.2rem; border:2px solid rgba(255,255,255,0.3); color:{tema.COLOR_BLANCO}; box-shadow:0 0 10px rgba(99,241,161,0.5),inset 0 0 20px rgba(255,255,255,0.1); position:relative; z-index:1; transition:all var(--transition-fast); }}
.header-date:hover {{ transform:scale(1.05); box-shadow:0 0 50px rgba(236,72,153,0.08); }}
</style>
"""
    st.markdown(dashboard_css, unsafe_allow_html=True)


def apply_all_styles():
    """
    Punto de entrada único: aplica TODOS los bloques CSS en el orden correcto.
    Llamar una sola vez al inicio del script principal.
    """
    _apply_base_css()
    _apply_page_css()
    _apply_dashboard_css()
    inject_custom_css()


def show_success_box(msg: str):
    """Muestra un mensaje de éxito con estilo Ciberpunk."""
    COLOR_OK    = tema.COLOR_EXITO_TEXTO
    COLOR_BG    = tema.COLOR_EXITO_FONDO_BOX
    safe_msg    = html_module.escape(str(msg))
    st.markdown(f"""
        <div class='success-box'>
            <div class='success-check'>☑</div>
            <div class='success-body'>
                <div class='success-title'>OPERACIÓN HECHA</div>
                <div class='success-message'>{safe_msg}</div>
            </div>
        </div>
        <style>
            .success-box {{ display:flex; align-items:center; gap:1rem; padding:1.2rem 1.5rem; border-radius:12px;
                background:{COLOR_BG}99; border:1px solid {COLOR_OK}aa;
                box-shadow:0 0 15px {COLOR_OK}55,inset 0 0 5px {COLOR_OK}22; margin-bottom:1rem; }}
            .success-check {{ font-size:2rem; line-height:1; }}
            .success-title {{ font-weight:700; color:{COLOR_OK}; font-size:1.15rem; text-transform:uppercase;
                letter-spacing:1.5px; text-shadow:0 0 5px {COLOR_OK}33; }}
            .success-message {{ color:"{tema.COLOR_BLANCO}"; opacity:0.9; font-size:0.95rem; margin-top:0.2rem; }}
        </style>
    """, unsafe_allow_html=True)
