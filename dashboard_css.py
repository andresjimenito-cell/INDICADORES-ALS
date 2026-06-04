# Este archivo contiene el CSS completo de resumen_publico.py
# Para usar en indicadores.py (Tema Claro Parex Resources)

def get_dashboard_css():
    """Retorna el CSS completo del dashboard en Tema Claro de Parex Resources"""
    return """
<style>
:root {
    /* 🎨 PALETA DE COLORES PAREX RESOURCES */
    --color-primary: #137659;        /* Verde Corporativo Parex */
    --color-secondary: #c09c2e;      /* Dorado Corporativo Parex */
    --color-accent-pink: #095139;    /* Verde Oscuro Parex */
    --color-accent-purple: #8b7411;  /* Dorado Oscuro */
    --color-accent-orange: #d97706;
    --color-accent-cyan: #0f766e;
    --color-accent-green: #15803d;
    --color-accent-yellow: #ca8a04;
    --color-dark: #1f221e;
    --color-light: #ffffff;
    
    /* 🌈 GRADIENTES CORPORATIVOS */
    --gradient-fire: linear-gradient(135deg, #137659 0%, #095139 100%);
    --gradient-ocean: linear-gradient(135deg, #c09c2e 0%, #8b7411 100%);
    --gradient-sunset: linear-gradient(135deg, #137659 0%, #eaf4ef 100%);
    --gradient-aurora: linear-gradient(135deg, #c09c2e 0%, #f5f7f6 100%);
    --gradient-cosmic: linear-gradient(135deg, #095139 0%, #137659 100%);
    --gradient-neon: linear-gradient(135deg, #137659 0%, #c09c2e 100%);
    
    /* 📐 ESPACIADO Y FORMAS */
    --radius-xl: 24px;
    --radius-mega: 32px;
    --shadow-glow: 0 4px 15px rgba(19, 118, 89, 0.15);
    --shadow-intense: 0 10px 30px rgba(0, 0, 0, 0.05);
    
    /* ⚡ ANIMACIONES */
    --transition-fast: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 🌟 ANIMACIONES KEYFRAMES */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 4px 15px rgba(19, 118, 89, 0.15); }
    50% { box-shadow: 0 8px 25px rgba(19, 118, 89, 0.25); }
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 🎯 ESTILOS GLOBALES */
.stApp {
    background: #f5f7f6 !important;
    font-family: 'Montserrat', 'Arial', sans-serif !important;
    color: #1f221e !important;
}

.main .block-container {
    padding: 0.5rem 1rem;
    max-width: 100%;
}

/* 🏭 HEADER MODERNO PAREX */
.dashboard-header {
    background: #137659; 
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 6px 15px rgba(19, 118, 89, 0.15);
    border-bottom: 4px solid #c09c2e; 
    color: #ffffff;
    position: relative;
    overflow: hidden;
    transition: all var(--transition-smooth);
}

.dashboard-header:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 8px 25px rgba(19, 118, 89, 0.25),
        inset 0 0 100px rgba(255, 255, 255, 0.05);
}

.header-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    position: relative;
    z-index: 1;
}

.header-date {
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: 0.5rem 1.3rem;
    border-radius: 50px;
    font-weight: 700;
    font-size: 0.95rem;
    border: 1px solid rgba(255, 255, 255, 0.4);
    color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    position: relative;
    z-index: 1;
    transition: all var(--transition-fast);
}

.header-date:hover {
    transform: scale(1.03);
    background: rgba(255, 255, 255, 0.25);
}

/* 💎 KPI CARDS */
.kpi-card {
    background: #ffffff;
    border: 1px solid rgba(19, 118, 89, 0.15);
    border-radius: 12px;
    padding: 1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
    transition: all var(--transition-smooth);
    min-height: 85px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.kpi-card:hover {
    transform: translateY(-3px);
    border-color: #137659;
    box-shadow: 0 6px 15px rgba(19, 118, 89, 0.1);
}

.kpi-icon {
    font-size: 1.4rem;
    line-height: 1;
    margin-bottom: 0.3rem;
    transition: all var(--transition-smooth);
    display: inline-block;
}

.kpi-card:hover .kpi-icon {
    transform: scale(1.08);
}

.kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #5b5c55;
}

.kpi-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: #1f221e;
    line-height: 1.2;
    margin-top: 2px;
}

/* ⚡ BOTONES LATERALES PAREX (TEMA CLARO) */
.neon-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.2rem 1rem;
    margin-bottom: 0.6rem;
    position: relative;
    border: 1.5px solid rgba(19, 118, 89, 0.15);
    transition: all var(--transition-smooth);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 110px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.03);
}

.neon-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    transition: all var(--transition-fast);
}

.neon-card:hover {
    transform: translateX(6px);
    border-color: #137659;
    box-shadow: 0 6px 20px rgba(19, 118, 89, 0.1);
}

/* 🌈 VARIANTES DE COLOR */
.neon-success {
    border-color: rgba(21, 128, 61, 0.2);
}
.neon-success::before {
    background: #137659;
}
.neon-success:hover {
    box-shadow: 0 4px 15px rgba(19, 118, 89, 0.12);
    border-color: #137659;
}

.neon-danger {
    border-color: rgba(217, 119, 6, 0.2);
}
.neon-danger::before {
    background: #c09c2e;
}
.neon-danger:hover {
    box-shadow: 0 4px 15px rgba(192, 156, 70, 0.12);
    border-color: #c09c2e;
}

.neon-info {
    border-color: rgba(15, 118, 110, 0.2);
}
.neon-info::before {
    background: #095139;
}
.neon-info:hover {
    box-shadow: 0 4px 15px rgba(9, 81, 57, 0.12);
    border-color: #095139;
}

.neon-neutral {
    border-color: rgba(91, 92, 85, 0.2);
}
.neon-neutral::before {
    background: #5b5c55;
}
.neon-neutral:hover {
    box-shadow: 0 4px 15px rgba(91, 92, 85, 0.12);
    border-color: #5b5c55;
}

.neon-label {
    font-weight: 700;
    font-size: 0.85rem;
    color: #1f221e;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.3rem;
}

.neon-label .emoji-icon {
    font-size: 1.3rem;
    line-height: 1;
}

.neon-value {
    font-weight: 800;
    font-size: 1.6rem;
    color: #137659;
    text-align: center;
    margin-top: 0.2rem;
    padding: 0;
}

/* 📊 CONTENEDORES DE GRÁFICOS (WHITE BOARDS) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border: 1px solid rgba(19, 118, 89, 0.15) !important;
    border-radius: 16px !important;
    padding: 1.5rem 1.3rem !important;
    margin-bottom: 0.8rem !important;
    position: relative;
    overflow: hidden !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    transition: all var(--transition-smooth) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(19, 118, 89, 0.08) !important;
    border-color: rgba(19, 118, 89, 0.3) !important;
}

h5 {
    font-size: 1.15rem !important;
    font-weight: 800;
    margin-bottom: 0.7rem !important;
    padding-bottom: 0.4rem;
    position: relative;
    color: #137659 !important;
}

h5::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 80px;
    height: 3px;
    background: #c09c2e;
    border-radius: 4px;
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

/* 💠 CAJAS DE DETALLE */
.detail-card {
    background: #ffffff;
    border: 1px solid rgba(19, 118, 89, 0.12);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
    transition: all 0.3s ease;
    border-left: 3px solid transparent;
}

.detail-card:hover {
    transform: translateX(4px);
    background: #f8faf9;
    border-left: 3px solid #137659;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.detail-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1f221e;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.detail-content {
    font-size: 0.85rem;
    color: #5b5c55;
}

.highlight-pill {
    background: rgba(19, 118, 89, 0.1);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #137659;
}

/* 🏷️ SUBTÍTULOS ELEGANTES */
.fancy-subtitle {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1f221e;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px dashed rgba(19, 118, 89, 0.25);
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
"""
