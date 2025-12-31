# Este archivo contiene el CSS completo de resumen_publico.py
# Para usar en indicadores.py

def get_dashboard_css():
    """Retorna el CSS completo del dashboard (basado en resumen_publico.py)"""
    return """
<style>
:root {
    /* 🎨 PALETA DE COLORES EITI COLOMBIA */
    --color-primary: #C82B96;        /* Magenta Vibrante EITI */
    --color-secondary: #8B2F89;      /* Púrpura Medio EITI */
    --color-accent-pink: #C82B96;    /* Magenta Vibrante EITI */
    --color-accent-purple: #4E2A68;  /* Púrpura Profundo EITI */
    --color-accent-orange: #f97316;
    --color-accent-cyan: #06b6d4;
    --color-accent-green: #10b981;
    --color-accent-yellow: #fbbf24;
    --color-dark: #0f172a;
    --color-light: #f8fafc;
    
    /* 🌈 GRADIENTES ÉPICOS - EITI COLOMBIA */
    --gradient-fire: linear-gradient(135deg, #C82B96 0%, #8B2F89 50%, #4E2A68 100%);      /* Gradiente principal EITI */
    --gradient-ocean: linear-gradient(135deg, #4E2A68 0%, #8B2F89 50%, #C82B96 100%);     /* Gradiente invertido EITI */
    --gradient-sunset: linear-gradient(135deg, #C82B96 0%, #fee140 100%);
    --gradient-aurora: linear-gradient(135deg, #8B2F89 0%, #fed6e3 100%);
    --gradient-cosmic: linear-gradient(135deg, #4E2A68 0%, #C82B96 100%);
    --gradient-neon: linear-gradient(135deg, #C82B96 0%, #4E2A68 100%);
    
    /* 📐 ESPACIADO Y FORMAS */
    --radius-xl: 24px;
    --radius-mega: 32px;
    --shadow-glow: 0 0 40px rgba(200, 43, 150, 0.5);    /* Magenta Vibrante EITI */
    --shadow-intense: 0 20px 60px rgba(0, 0, 0, 0.4);
    
    /* ⚡ ANIMACIONES */
    --transition-fast: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 🌟 ANIMACIONES KEYFRAMES */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.5), 0 0 40px rgba(139, 92, 246, 0.3); }
    50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.8), 0 0 80px rgba(139, 92, 246, 0.6); }
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

@keyframes rotate-border {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 🎯 ESTILOS GLOBALES */
.stApp {
    background: transparent;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main .block-container {
    padding: 1.2rem 1.8rem;
    max-width: 100%;
}

/* 🏭 HEADER INDUSTRIAL MODERNO */
.dashboard-header {
    background: #1e293b; 
    padding: 1.5rem 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    border-bottom: 4px solid #3b82f6; 
    color: #f8fafc;
    position: relative;
    overflow: hidden;
}

.dashboard-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: rotate-border 15s linear infinite;
}

.dashboard-header:hover {
    transform: translateY(-8px) scale(1.01);
    box-shadow: 
        0 0 100px rgba(236, 0, 212, 0.8),
        0 30px 100px rgba(0, 0, 0, 0.6),
        inset 0 0 150px rgba(255, 255, 255, 0.15);
}

.header-title {
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #C82B96 0%, #8B2F89 50%, #4E2A68 100%);  /* Gradiente EITI */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 5px 20px rgba(200, 43, 150, 0.3);  /* Sombra magenta */
    letter-spacing: -1px;
    position: relative;
    z-index: 1;
}

.header-date {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 1rem 2.5rem;
    border-radius: 50px;
    font-weight: 800;
    font-size: 1.2rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    box-shadow: 
        0 0 10px rgba(99, 241, 161, 0.5),
        inset 0 0 20px rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 1;
    transition: all var(--transition-fast);
}

.header-date:hover {
    transform: scale(1.05);
    box-shadow: 0 0 50px rgba(236, 72, 153, 0.8);
}

/* 💎 KPI CARDS */
.kpi-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(5px);
    border: 1.5px solid rgba(200, 43, 150, 0.3);   /* Magenta EITI */
    border-radius: var(--radius-xl);
    padding: 0.6rem 0.7rem;
    position: relative;
    overflow: hidden;
    box-shadow: 
        0 0 8px rgba(200, 43, 150, 0.2),           /* Glow magenta EITI */
        0 2px 10px rgba(0, 0, 0, 0.05);
    transition: all var(--transition-smooth);
    min-height: 90px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 153, 0.1), transparent);
    transition: left 0.5s;
}

.kpi-card:hover::before {
    left: 100%;
}

.kpi-card:hover {
    transform: translateY(-5px) scale(1.02);
    border-color: rgba(0, 255, 153, 0.4);
    box-shadow: 
        0 0 15px rgba(0, 255, 153, 0.2),
        0 5px 15px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
    font-size: 2rem;
    line-height: 1;
    margin-bottom: 0.6rem;
    transition: all var(--transition-smooth);
    display: inline-block;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.kpi-card:hover .kpi-icon {
    transform: scale(1.15) rotate(-5deg);
    filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.3));
}

.kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    background: linear-gradient(135deg, #C82B96, #8B2F89);  /* Gradiente EITI */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    opacity: 0.8;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 900;
    background: linear-gradient(135deg, #C82B96, #4E2A68);  /* Gradiente EITI */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}

/* ⚡ BOTONES LATERALES NEÓN */
.neon-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border-radius: var(--radius-xl);
    padding: 1.2rem 1rem;
    margin-bottom: 0.6rem;
    position: relative;
    border: 2px solid;
    transition: all var(--transition-smooth);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 120px;
}

.neon-card::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
    opacity: 0.3;
}

.neon-card:hover::after {
    width: 300px;
    height: 300px;
}

.neon-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 8px;
    height: 100%;
    transition: all var(--transition-fast);
}

.neon-card:hover {
    transform: translateX(12px) scale(1.04);
}

/* 🌈 VARIANTES DE COLOR */
.neon-success {
    border-color: rgba(16, 185, 129, 0.4);
}
.neon-success::before {
    background: var(--gradient-neon);
}
.neon-success::after {
    background: radial-gradient(circle, #10b981, transparent);
}
.neon-success:hover {
    box-shadow: 
        0 0 50px rgba(16, 185, 129, 1),
        inset 0 0 30px rgba(16, 185, 129, 0.3);
    border-color: #10b981;
}

.neon-danger {
    border-color: rgba(239, 68, 68, 0.4);
}
.neon-danger::before {
    background: var(--gradient-fire);
}
.neon-danger::after {
    background: radial-gradient(circle, #ef4444, transparent);
}
.neon-danger:hover {
    box-shadow: 
        0 0 50px rgba(239, 68, 68, 1),
        inset 0 0 30px rgba(239, 68, 68, 0.3);
    border-color: #ef4444;
}

.neon-info {
    border-color: rgba(6, 182, 212, 0.4);
}
.neon-info::before {
    background: var(--gradient-ocean);
}
.neon-info::after {
    background: radial-gradient(circle, #06b6d4, transparent);
}
.neon-info:hover {
    box-shadow: 
        0 0 50px rgba(6, 182, 212, 1),
        inset 0 0 30px rgba(6, 182, 212, 0.3);
    border-color: #06b6d4;
}

.neon-neutral {
    border-color: rgba(139, 92, 246, 0.4);
}
.neon-neutral::before {
    background: var(--gradient-aurora);
}
.neon-neutral::after {
    background: radial-gradient(circle, #8b5cf6, transparent);
}
.neon-neutral:hover {
    box-shadow: 
        0 0 50px rgba(139, 92, 246, 1),
        inset 0 0 30px rgba(139, 92, 246, 0.3);
    border-color: #8b5cf6;
}

.neon-label {
    font-weight: 800;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.4rem;
}

.neon-label .emoji-icon {
    font-size: 1.5rem;
    line-height: 1;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.neon-value {
    font-weight: 900;
    font-size: 1.8rem;
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 1px;
    text-align: center;
    margin-top: 0.2rem;
    padding: 0;
}

/* 📊 CONTENEDORES DE GRÁFICOS */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: var(--radius-mega);
    padding: 1.5rem 1.3rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
    box-shadow: 
        0 0 10px rgba(99, 102, 241, 0.2),
        0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all var(--transition-smooth);
}

div[data-testid="stVerticalBlockBorderWrapper"]::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--radius-mega);
    padding: 2px;
    background: linear-gradient(135deg, #6366f1, #ec4899, #f97316, #06b6d4);
    background-size: 300% 300%;
    animation: gradient-shift 6s ease infinite;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity var(--transition-fast);
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover::before {
    opacity: 1;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px);
    box-shadow: 
        0 0 80px rgba(236, 72, 153, 0.6),
        0 20px 70px rgba(0, 0, 0, 0.4);
}

h5 {
    font-size: 1.2rem !important;
    font-weight: 900;
    margin-bottom: 0.8rem !important;
    padding-bottom: 0.5rem;
    position: relative;
    background: linear-gradient(135deg, #fff, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h5::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #ec4899, #f97316);
    border-radius: 4px;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.8);
}

/* 🎯 EMOJIS */
.emoji, [role="img"], .emoji-icon {
    font-family: 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif !important;
    font-style: normal !important;
    font-weight: normal !important;
    line-height: 1 !important;
    vertical-align: middle;
    display: inline-block;
}

* {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.kpi-icon, .neon-label {
    -webkit-text-fill-color: initial !important;
    background-clip: border-box !important;
    -webkit-background-clip: border-box !important;
}

/* ========================================================================
   🎨 SIDEBAR COMPLETO - REDISEÑO PROFESIONAL Y COHESIVO
   ======================================================================== */

/* Contenedor principal del sidebar - MÁS ANCHO */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A0E27 0%, #0f1535 50%, #0A0E27 100%);
    border-right: 2px solid rgba(255, 0, 255, 0.15);
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
    min-width: 280px !important;
    max-width: 320px !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

section[data-testid="stSidebar"] > div > div {
    background: transparent;
    padding: 1.2rem 1rem !important;
}

/* ===== BOTONES DEL SIDEBAR ===== */
section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, rgba(255, 0, 255, 0.08), rgba(0, 217, 255, 0.08));
    border: 1.5px solid rgba(255, 0, 255, 0.25);
    border-radius: 10px;
    color: #E0FFFF;
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-align: left;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(135deg, rgba(255, 0, 255, 0.15), rgba(0, 217, 255, 0.15));
    border-color: rgba(255, 0, 255, 0.5);
    transform: translateX(4px);
    box-shadow: 0 4px 16px rgba(255, 0, 255, 0.3);
}

section[data-testid="stSidebar"] .stButton > button:active {
    transform: translateX(2px);
}

/* Botón de Dashboard (destacado) */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(255, 0, 255, 0.2), rgba(0, 217, 255, 0.2));
    border-color: rgba(255, 0, 255, 0.4);
    font-weight: 700;
}

/* ===== DIVISORES ===== */
section[data-testid="stSidebar"] hr {
    margin: 1.2rem 0;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 0, 255, 0.3), transparent);
}

/* ===== TEXTO Y MARKDOWN ===== */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div {
    color: #CBD5E1;
    font-family: 'Rajdhani', 'Segoe UI', sans-serif;
}

/* Títulos pequeños (etiquetas de sección) */
section[data-testid="stSidebar"] div[style*="font-size:0.8rem"] {
    color: #94A3B8 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 700;
    margin-bottom: 0.8rem;
    padding-left: 0.5rem;
    border-left: 3px solid rgba(0, 217, 255, 0.5);
}

/* ===== SELECTBOX Y WIDGETS ===== */
section[data-testid="stSidebar"] .stSelectbox label {
    font-size: 0.85rem;
    color: #94A3B8 !important;
    font-weight: 600;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
    background: rgba(15, 21, 53, 0.6);
    border: 1.5px solid rgba(255, 0, 255, 0.2);
    border-radius: 8px;
    color: #E0FFFF;
    font-size: 0.9rem;
    transition: all 0.3s ease;
}

section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:hover {
    border-color: rgba(255, 0, 255, 0.4);
    background: rgba(15, 21, 53, 0.9);
    box-shadow: 0 0 12px rgba(255, 0, 255, 0.2);
}

/* ===== NAVEGACIÓN INTERNA (LINKS) ===== */
.sidebar-anchor-link {
    display: block;
    padding: 0.65rem 1rem;
    margin-bottom: 0.4rem;
    color: #CBD5E1 !important;
    text-decoration: none !important;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: 8px;
    border-left: 3px solid transparent;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.02);
}

.sidebar-anchor-link:hover {
    background: rgba(255, 0, 255, 0.1);
    border-left-color: #FF00FF;
    color: #E0FFFF !important;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(255, 0, 255, 0.2);
}

/* ===== TÍTULO DE NAVEGACIÓN ===== */
.sidebar-nav-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #00D9FF;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 0.8rem 0;
    margin: 1rem 0 0.8rem 0;
    background: linear-gradient(135deg, rgba(255, 0, 255, 0.1), rgba(0, 217, 255, 0.1));
    border-radius: 8px;
    border: 1px solid rgba(0, 217, 255, 0.3);
}

/* ===== METADATA DEL SIDEBAR ===== */
.sidebar-metadata {
    margin-top: 2rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    text-align: center;
}

.sidebar-metadata p {
    margin: 0.3rem 0;
    font-size: 0.8rem;
    color: #94A3B8;
    line-height: 1.4;
}

.sidebar-metadata strong {
    color: #00D9FF;
    font-weight: 700;
}

/* ===== SCROLLBAR DEL SIDEBAR ===== */
section[data-testid="stSidebar"] ::-webkit-scrollbar {
    width: 8px;
}

section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}

section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #FF00FF, #00D9FF);
    border-radius: 4px;
}

section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #FF33FF, #33E5FF);
}

/* ===== ANIMACIONES ===== */
@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] .stSelectbox {
    animation: slideInLeft 0.4s ease-out;
}

/* Títulos de sección internos */
section[data-testid="stSidebar"] h3 {
    font-size: 0.9rem !important;
    color: #CBD5E1 !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.5rem !important;
    padding-left: 0.5rem;
    border-left: 2px solid var(--color-secondary);
}

/* 💠 CAJAS DE DETALLE (FINE COQUETRY) */
.detail-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    border-left: 3px solid transparent;
}

.detail-card:hover {
    transform: translateX(5px);
    background: rgba(255, 255, 255, 0.06);
    border-left: 3px solid var(--color-primary);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.detail-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.detail-content {
    font-size: 0.85rem;
    color: rgba(255, 255, 255, 0.6);
}

.highlight-pill {
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-accent-green);
}

/* 🏷️ SUBTÍTULOS ELEGANTES */
.fancy-subtitle {
    font-size: 1.1rem;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    gap: 8px;
}

</style>
"""
