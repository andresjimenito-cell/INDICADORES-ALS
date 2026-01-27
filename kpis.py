import streamlit as st
import pandas as pd
from graphviz import Digraph
import datetime 
import pandas as pd 
from theme import get_colors
import mtbf as mtbf_mod

import tema

_colors = get_colors()
# Usar Magenta Neon como color principal para KPIs
COLOR_PRINCIPAL = getattr(tema, 'COLOR_MAGENTA_NEON', '#C82B96')
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = _bg_raw or '#1a1a2e'
COLOR_FONDO_CONTENEDOR = _colors.get('container_bg', 'rgba(25, 25, 40, 0.7)')
COLOR_SOMBRA = 'transparent'

# Colores adicionales específicos locales (si se requieren tonos distintos se definen aquí)
# Text colors: prefer theme text if available, otherwise good defaults
COLOR_TEXTO_DATOS = _colors.get('muted', '#b3f0cc')
COLOR_TEXTO_PRINCIPAL = _colors.get('text_on_primary', _colors.get('text', '#ffffff'))

# Usaremos la implementación real de MTBF desde el módulo `mtbf.py` (importado como mtbf_mod)

def mostrar_kpis(df_bd, reporte_runes=None, reporte_run_life=None, indice_resumen_df=None, mtbf_global=None, mtbf_als=None, df_forma9=None, fecha_evaluacion=None):
    # Contenedor para el filtro y el título (código omitido por brevedad)
    with st.container():
        # Usar la misma clave que el resto de la app para mantener sincronía
        # Construir opciones seguras y estables
        if 'ALS' in df_bd.columns:
            als_opts = sorted([str(x).strip() for x in df_bd['ALS'].dropna().unique() if str(x).strip() != ''])
        else:
            als_opts = []

        als_options = ['ESP'] + als_opts

        # Mantener selección previa si existe
        cur = st.session_state.get('kpis_als_filter', 'ESP')
        try:
            idx = als_options.index(str(cur)) if str(cur) in als_options else 0
        except Exception:
            idx = 0

        is_in_dialog = st.session_state.get('kpi_in_dialog', False)
        # Usar key dinámica para evitar conflicto cuando se renderiza dentro del diálogo
        widget_key = 'kpis_als_filter_dialog' if is_in_dialog else 'kpis_als_filter'
        
        selected_als = st.selectbox(
            'Filtro por Sistema de Levantamiento (ALS):',
            als_options,
            key=widget_key,
            index=idx,
            help='Selecciona un sistema ALS para refinar el análisis',
        )

        # Filtrar df según la selección (TODOS = no filtrar)
        if selected_als and selected_als != 'TODOS':
            df_bd_als = df_bd[df_bd['ALS'].astype(str).str.strip() == str(selected_als).strip()].copy()
        else:
            df_bd_als = df_bd.copy()

    # === SOLUCIÓN: Premium KPI Hierarchy Map v5.0 (Vibrant & Interactive) ===
    from run_life_efectivo import calcular_run_life_efectivo
    import streamlit.components.v1 as components
    
    # ----------------------------------------------------------------------------------
    # Lógica de Cálculo de Datos (Mantenida y extendida)
    # ----------------------------------------------------------------------------------
    if fecha_evaluacion is None:
        fecha_evaluacion = datetime.datetime.now()
    else:
        try:
            fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
        except Exception:
            fecha_evaluacion = datetime.datetime.now()
            
    # MTBF
    try:
        mtbf_als_val, _ = mtbf_mod.calcular_mtbf(df_bd_als, fecha_evaluacion)
    except Exception:
        mtbf_als_val = None
    try:
        mtbf_total_val, _ = mtbf_mod.calcular_mtbf(df_bd, fecha_evaluacion)
    except Exception:
        mtbf_total_val = None

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).date()
    df_bd['FECHA_RUN_DATE'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce').dt.date
    df_bd['FECHA_PULL_DATE'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce').dt.date
    df_bd['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce').dt.date

    def filtrar_als(df, als):
        if als and als != 'TODOS' and 'ALS' in df.columns:
            return df[df['ALS'] == als].copy()
        return df.copy()

    def calc_running(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_fallados(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].notna()) & (df['FECHA_FALLA_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_operativos(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].isna() | (df['FECHA_FALLA_DATE'] > fecha_eval)) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]

    df_bd_als_calc = filtrar_als(df_bd, selected_als)
    run_todos = calc_running(df_bd, fecha_eval_date)
    fallado_todos = calc_fallados(df_bd, fecha_eval_date)
    operativos_todos = calc_operativos(df_bd, fecha_eval_date)
    run_als = calc_running(df_bd_als_calc, fecha_eval_date)
    fallado_als = calc_fallados(df_bd_als_calc, fecha_eval_date)
    operativos_als = calc_operativos(df_bd_als_calc, fecha_eval_date)

    run_label = f"TOTAL: {run_todos}\n{selected_als}: {run_als}"
    fallado_label = f"TOTAL: {fallado_todos}\n{selected_als}: {fallado_als}"
    operativos_label = f"TOTAL: {operativos_todos}\n{selected_als}: {operativos_als}"

    if df_forma9 is not None:
        df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
        df_forma9['DIAS TRABAJADOS'] = pd.to_numeric(df_forma9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
        if 'SISTEMA ALS' in df_forma9.columns:
            df_forma9 = df_forma9.rename(columns={'SISTEMA ALS': 'ALS'})
        
        df_forma9_eval = df_forma9[
            (df_forma9['FECHA_FORMA9'].dt.date >= (fecha_eval_date - pd.Timedelta(days=30))) &
            (df_forma9['FECHA_FORMA9'].dt.date <= fecha_eval_date)
        ]
        
        if selected_als != 'TODOS' and 'ALS' in df_forma9_eval.columns:
            df_forma9_eval_als = df_forma9_eval[df_forma9_eval['ALS'] == selected_als]
            pozos_on_als = df_forma9_eval_als[df_forma9_eval_als['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
            pozos_on_todos = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
        else:
            pozos_on_todos = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
            pozos_on_als = pozos_on_todos
        
        pozos_off_todos = operativos_todos - pozos_on_todos if operativos_todos >= pozos_on_todos else 0
        pozos_off_als = operativos_als - pozos_on_als if operativos_als >= pozos_on_als else 0
        
        on_label = f"TOTAL: {pozos_on_todos}\n{selected_als}: {pozos_on_als}"
        off_label = f"TOTAL: {pozos_off_todos}\n{selected_als}: {pozos_off_als}"
        
        rl_todos = 0
        rl_als = 0
        if reporte_run_life is not None and not reporte_run_life.empty:
            val = reporte_run_life.loc[reporte_run_life['Categoría'] == 'Tiempo de Vida Promedio (Fallados+Ext)', 'Valor']
            if not val.empty:
                rl_todos = float(val.values[0])
        
        if selected_als != 'TODOS' and 'ALS' in df_bd.columns:
            fecha_eval = pd.to_datetime(fecha_evaluacion)
            df_bd_als_rl = df_bd[df_bd['ALS'] == selected_als].copy()
            df_bd_als_rl['FECHA_PULL_DATE'] = pd.to_datetime(df_bd_als_rl['FECHA_PULL'], errors='coerce')
            df_bd_als_rl['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd_als_rl['FECHA_FALLA'], errors='coerce')
            df_bd_als_rl['FECHA_RUN_DATE'] = pd.to_datetime(df_bd_als_rl['FECHA_RUN'], errors='coerce')
            df_bd_als_eval = df_bd_als_rl[df_bd_als_rl['FECHA_RUN_DATE'].dt.date <= fecha_eval.date()].copy()
            run_life_als = df_bd_als_eval[(df_bd_als_eval['FECHA_PULL_DATE'].notna()) | (df_bd_als_eval['FECHA_FALLA_DATE'].notna())]['RUN LIFE'].mean()
            if pd.notna(run_life_als):
                rl_als = float(run_life_als)
        rl_label = f"TOTAL: {rl_todos:.2f} Días\n{selected_als}: {rl_als:.2f} Días"
    else:
        on_label = "TOTAL: N/D\nALS: N/D"
        off_label = "TOTAL: N/D\nALS: N/D"
        rl_label = "TOTAL: N/D\nALS: N/D"

    # Run Life Efectivo Calculation
    try:
        rle_total_val, _ = calcular_run_life_efectivo(df_bd, df_forma9, fecha_evaluacion)
        _, df_bd_als_rle = calcular_run_life_efectivo(df_bd_als_calc, df_forma9, fecha_evaluacion)
        # Recalcular RLE por ALS si no es TODOS
        rle_als_val = df_bd_als_rle['RUN_LIFE_EFECTIVO'].mean() if 'RUN_LIFE_EFECTIVO' in df_bd_als_rle.columns else 0
        rle_label = f"TOTAL: {rle_total_val:.2f} Días\n{selected_als}: {rle_als_val:.2f} Días"
    except Exception:
        rle_label = "TOTAL: N/D\nALS: N/D"

    mtbf_total_str = f"{mtbf_total_val:.2f}" if mtbf_total_val is not None else "N/D"
    mtbf_als_str = f"{mtbf_als_val:.2f}" if mtbf_als_val is not None else "N/D"
    mtbf_label = f"TOTAL: {mtbf_total_str} Días\n{selected_als}: {mtbf_als_str} Días"
    
    def get_if_val(df, indicador, als=None):
        if df is not None and 'Indicador' in df.columns and 'Valor' in df.columns:
            if als and als != 'TODOS' and 'ALS' in df.columns:
                row = df[(df['Indicador'] == indicador) & (df['ALS'] == als)]
            else:
                row = df[df['Indicador'] == indicador]
            if not row.empty:
                return str(row['Valor'].values[0])
        return "N/D"
        
    if_on = get_if_val(indice_resumen_df, 'Índice de Falla ON')
    if_als_on = get_if_val(indice_resumen_df, 'Índice de Falla ALS ON', selected_als)
    if_label = f"TOTAL ON: {if_on}\n{selected_als} ON: {if_als_on}"
    # ----------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------
    # Lógica de Botón Flotante para Fullscreen (Eliminado a petición del usuario)
    # ----------------------------------------------------------------------------------
    
    # Flag para saber si estamos dentro del diálogo (mantener para compatibilidad interna)
    is_in_dialog = st.session_state.get('kpi_in_dialog', False)

    # ----------------------------------------------------------------------------------
    # Ajustes de Escala para Modo Compacto (Ahora 100% Ancho)
    # ----------------------------------------------------------------------------------
    # Aumentar scale_factor ya que ahora los KPIs ocupan 100% del ancho
    scale_factor = 0.88 if not is_in_dialog else 1.0
    iframe_height = 580 if not is_in_dialog else 850
    
    transform_style = f"transform: scale({scale_factor}) translateX(-50%) translateY(40px); transform-origin: top left; width: {100/scale_factor}%; position: absolute; left: 50%; top: 10px;"
 
    # Preparar el HTML con los datos - Formato Stacked Premium
    def br_hud(text):
        parts = text.split("\n")
        if len(parts) > 1:
            # Color amarillo neón para la segunda línea (ALS) para que sea muy visible
            return f'<span class="text-white font-black text-sm tracking-tight">{parts[0]}</span><br><span class="text-[#FFDE31] text-[10px] font-bold tracking-[0.1em] uppercase drop-shadow-[0_0_5px_rgba(255,222,49,0.5)]">{parts[1]}</span>'
        return f'<span class="text-white font-black text-sm tracking-tight">{text}</span>'
 
    html_content = f"""
<!DOCTYPE html>
<html class="dark">
<head>
    <meta charset="utf-8"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&family=Inter:wght@400;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@300&display=swap" rel="stylesheet"/>
    <style>
        :root {{ 
            --neon: #00f2ff; 
            --magento: #bc13fe; 
            --emerald: #00ff9d; 
            --amber: #FFDE31;
            --bg-hud: #060a1e;
        }}
        body {{ 
            background: transparent; 
            font-family: 'Inter', sans-serif; 
            height: 100vh; 
            overflow: hidden; 
            margin: 0;
            user-select: none;
        }}
        
        /* --- TECH BACKGROUND EFFECTS --- */
        .grid-bg {{
            background-image: linear-gradient(rgba(0, 242, 255, 0.05) 1px, transparent 1px), 
                              linear-gradient(90deg, rgba(0, 242, 255, 0.05) 1px, transparent 1px);
            background-size: 40px 40px;
            mask-image: radial-gradient(circle at center, black, transparent 80%);
            animation: grid-move 20s infinite linear;
        }}
        @keyframes grid-move {{ 
            from {{ background-position: 0 0; }} 
            to {{ background-position: 40px 40px; }} 
        }}

        .scanlines {{
            position: fixed; inset: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%);
            background-size: 100% 4px;
            pointer-events: none; z-index: 100; opacity: 0.3;
        }}

        /* --- CARDS & INTERACTIVITY --- */
        .hud-card {{
            background: rgba(10, 15, 30, 0.7);
            backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 14px 20px;
            transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
            position: relative;
            box-shadow: 0 10px 40px rgba(0,0,0,0.4);
            display: flex; align-items: center; gap: 18px;
            overflow: hidden;
        }}
        .hud-card::after {{
            content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle at center, var(--neon), transparent 70%);
            opacity: 0; transition: opacity 0.5s; pointer-events: none; z-index: -1;
        }}
        .hud-card:hover {{
            transform: translateY(-8px) scale(1.05);
            border-color: var(--neon);
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.25);
            background: rgba(10, 15, 30, 0.9);
        }}
        .hud-card:hover::after {{ opacity: 0.05; }}
        
        .hud-card::before {{
            content: ''; position: absolute; left: 0; top: 20%; height: 60%; width: 3px;
            background: var(--neon); border-radius: 0 4px 4px 0;
            box-shadow: 0 0 10px var(--neon);
        }}
        
        /* --- DATA FLOW ANIMATIONS --- */
        .conn-path {{ 
            stroke-dasharray: 15, 15; 
            animation: flow 5s linear infinite; 
            stroke-width: 2;
            opacity: 0.3;
            filter: drop-shadow(0 0 5px currentColor);
        }}
        @keyframes flow {{ to {{ stroke-dashoffset: -60; }} }}

        .glow-icon {{ filter: drop-shadow(0 0 12px currentColor); }}
        
        /* --- FLOATING TECH ORBS --- */
        .orb {{
            position: absolute; width: 500px; height: 500px; border-radius: 50%;
            filter: blur(120px); opacity: 0.12; z-index: -2;
        }}
        .orb-pulse {{ animation: orbit-float 30s infinite ease-in-out; }}
        @keyframes orbit-float {{
            0%, 100% {{ transform: translate(0, 0) scale(1); opacity: 0.1; }}
            50% {{ transform: translate(100px, 50px) scale(1.2); opacity: 0.2; }}
        }}
    </style>
</head>
<body>
    <div class="scanlines"></div>
    <div class="grid-bg fixed inset-0"></div>
    <div class="orb orb-pulse bg-[#C82B96] -top-20 -left-20"></div>
    <div class="orb orb-pulse bg-[#00f2ff] -bottom-20 -right-20" style="animation-delay: -15s;"></div>

    <div class="flex items-center justify-center h-full relative z-10" style="{transform_style}">
        
        <!-- SVG Connections -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 1500 650">
            <g fill="none">
                <!-- Data Paths Left (Conectan a X=560 para alinear con left-[18%]) -->
                <path class="conn-path" d="M 750 325 C 650 325, 600 120, 560 120" stroke="#00f2ff"></path>
                <path class="conn-path" d="M 750 325 C 650 325, 600 220, 560 220" stroke="#00ff9d"></path>
                <path class="conn-path" d="M 750 325 C 650 325, 600 325, 560 325" stroke="#ff0055"></path>
                <path class="conn-path" d="M 750 325 C 650 325, 600 430, 560 430" stroke="#FFDE31"></path>
                <path class="conn-path" d="M 750 325 C 650 325, 600 530, 560 530" stroke="#94a3b8"></path>
                
                <!-- Data Paths Right (Conectan a X=940 para alinear con right-[18%]) -->
                <path class="conn-path" d="M 750 325 C 850 325, 900 150, 940 150" stroke="#bc13fe"></path>
                <path class="conn-path" d="M 750 325 C 850 325, 900 250, 940 250" stroke="#bc13fe"></path>
                <path class="conn-path" d="M 750 325 C 850 325, 900 350, 940 350" stroke="#00ff9d"></path>
                <path class="conn-path" d="M 750 325 C 850 325, 900 450, 940 450" stroke="#ff0055"></path>
            </g>
        </svg>

        <!-- Central Nerve System Unit -->
        <div class="relative group z-50">
            <div class="w-40 h-40 rounded-full bg-[#0a0f1e] border-2 border-[#00f2ff]/40 flex flex-col items-center justify-center shadow-[0_0_80px_rgba(0,242,255,0.3)] group-hover:scale-110 group-hover:border-[#00f2ff] transition-all duration-700 cursor-help">
                <div class="absolute inset-0 rounded-full bg-[radial-gradient(circle,#00f2ff20,transparent_70%)] animate-pulse"></div>
                <!-- Tech ring -->
                <div class="absolute inset-0 border-[1px] border-dashed border-[#00f2ff]/20 rounded-full animate-[spin_20s_linear_infinite]"></div>
                <span class="material-symbols-outlined text-[#00f2ff] text-6xl mb-1 glow-icon">dashboard_customize</span>
                <span class="text-[12px] font-black tracking-[5px] text-[#00f2ff] uppercase drop-shadow-[0_0_8px_#00f2ff]">KPIs</span>
            </div>
        </div>

        <!-- Left Column: Command Units (Ajustado a 18%) -->
        <div class="absolute left-[18%] flex flex-col gap-6 items-end">
            <div class="hud-card w-72 text-right" style="--neon: #00f2ff;">
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Corridas</div>
                    {br_hud(run_label)}
                </div>
                <div class="w-12 h-12 rounded-lg bg-[#00f2ff]/10 flex items-center justify-center border border-[#00f2ff]/30">
                    <span class="material-symbols-outlined text-[#00f2ff] text-3xl glow-icon">terminal</span>
                </div>
            </div>
            <div class="hud-card w-72 text-right" style="--neon: #00ff9d;">
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Operativos</div>
                    {br_hud(operativos_label)}
                </div>
                <div class="w-12 h-12 rounded-lg bg-[#00ff9d]/10 flex items-center justify-center border border-[#00ff9d]/30">
                    <span class="material-symbols-outlined text-[#00ff9d] text-3xl glow-icon">analytics</span>
                </div>
            </div>
            <div class="hud-card w-72 text-right" style="--neon: #ff0055;">
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Fallados</div>
                    {br_hud(fallado_label)}
                </div>
                <div class="w-12 h-12 rounded-lg bg-[#ff0055]/10 flex items-center justify-center border border-[#ff0055]/30">
                    <span class="material-symbols-outlined text-[#ff0055] text-3xl glow-icon">emergency_home</span>
                </div>
            </div>
            <div class="hud-card w-72 text-right" style="--neon: #FFDE31;">
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Activos</div>
                    {br_hud(on_label)}
                </div>
                <div class="w-12 h-12 rounded-lg bg-[#FFDE31]/10 flex items-center justify-center border border-[#FFDE31]/30">
                    <span class="material-symbols-outlined text-[#FFDE31] text-3xl glow-icon">energy_program_saving</span>
                </div>
            </div>
            <div class="hud-card w-72 text-right" style="--neon: #94a3b8;">
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Apagados</div>
                    {br_hud(off_label)}
                </div>
                <div class="w-12 h-12 rounded-lg bg-[#94a3b8]/10 flex items-center justify-center border border-[#94a3b8]/30">
                    <span class="material-symbols-outlined text-slate-400 text-3xl glow-icon">power_off</span>
                </div>
            </div>
        </div>

        <!-- Right Column: Performance Outbound (Ajustado a 18%) -->
        <div class="absolute right-[18%] flex flex-col gap-6 items-start">
            <div class="hud-card w-72" style="--neon: #bc13fe;">
                <div class="w-12 h-12 rounded-lg bg-[#bc13fe]/10 flex items-center justify-center border border-[#bc13fe]/30">
                    <span class="material-symbols-outlined text-[#bc13fe] text-3xl glow-icon">hourglass_top</span>
                </div>
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Run Life</div>
                    {br_hud(rl_label)}
                </div>
            </div>
            <div class="hud-card w-72" style="--neon: #bc13fe;">
                <div class="w-12 h-12 rounded-lg bg-[#bc13fe]/10 flex items-center justify-center border border-[#bc13fe]/30">
                    <span class="material-symbols-outlined text-[#bc13fe] text-3xl glow-icon">monitoring</span>
                </div>
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">TMEF / MTBF</div>
                    {br_hud(mtbf_label)}
                </div>
            </div>
            <div class="hud-card w-72" style="--neon: #00ff9d;">
                <div class="w-12 h-12 rounded-lg bg-[#00ff9d]/10 flex items-center justify-center border border-[#00ff9d]/30">
                    <span class="material-symbols-outlined text-[#00ff9d] text-3xl glow-icon">health_metrics</span>
                </div>
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Run Life Efectivo</div>
                    {br_hud(rle_label)}
                </div>
            </div>
            <div class="hud-card w-72" style="--neon: #ff0055;">
                <div class="w-12 h-12 rounded-lg bg-[#ff0055]/10 flex items-center justify-center border border-[#ff0055]/30">
                    <span class="material-symbols-outlined text-[#ff0055] text-3xl glow-icon">query_stats</span>
                </div>
                <div class="flex-1">
                    <div class="text-[10px] font-black text-[#94a3b8] tracking-[3px] uppercase mb-1">Indice de Falla</div>
                    {br_hud(if_label)}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    components.html(html_content, height=iframe_height, scrolling=False)


from graphviz import Digraph # Import Digraph

def build_kpis_graph(df_bd, df_forma9=None, reporte_run_life=None, indice_resumen_df=None, selected_als='TODOS', fecha_evaluacion=None):
    """Construye y devuelve un objeto graphviz.Digraph con los nodos y etiquetas de KPIs.
    Esta función no imprime en Streamlit; devuelve el `dot` para que el llamador lo muestre.
    """
    # Normalizar columnas
    df_bd = df_bd.copy()
    df_bd.columns = [str(c).upper().strip() for c in df_bd.columns]
    if df_forma9 is not None:
        df_forma9 = df_forma9.copy()
        df_forma9.columns = [str(c).upper().strip() for c in df_forma9.columns]
        if 'SISTEMA ALS' in df_forma9.columns and 'ALS' not in df_forma9.columns:
            df_forma9 = df_forma9.rename(columns={'SISTEMA ALS': 'ALS'})

    # Fecha evaluación
    if fecha_evaluacion is None:
        fecha_evaluacion = datetime.datetime.now()
    else:
        try:
            fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
        except Exception:
            fecha_evaluacion = datetime.datetime.now()

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).date()

    # Crear columnas fecha coerced
    for col in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
        if col in df_bd.columns:
            df_bd[col + '_DATE'] = pd.to_datetime(df_bd[col], errors='coerce').dt.date
        else:
            df_bd[col + '_DATE'] = pd.NaT

    def filtrar_als(df, als):
        if als and als != 'TODOS' and 'ALS' in df.columns:
            return df[df['ALS'] == als].copy()
        return df.copy()

    def calc_running(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_fallados(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].notna()) & (df['FECHA_FALLA_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]
    def calc_operativos(df, fecha_eval):
        return df[(df['FECHA_FALLA_DATE'].isna() | (df['FECHA_FALLA_DATE'] > fecha_eval)) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))].shape[0]

    df_bd_als = filtrar_als(df_bd, selected_als)
    run_todos = calc_running(df_bd, fecha_eval_date)
    fallado_todos = calc_fallados(df_bd, fecha_eval_date)
    operativos_todos = calc_operativos(df_bd, fecha_eval_date)

    # Pozos ON en forma9 (últimos 30 días)
    pozos_on_todos = 0
    if df_forma9 is not None and not df_forma9.empty:
        fecha_col = next((c for c in df_forma9.columns if 'FECHA' in c), None)
        dias_col = next((c for c in df_forma9.columns if 'DIAS' in c), None)
        pozo_col = next((c for c in df_forma9.columns if 'POZO' in c), None)
        if fecha_col and dias_col and pozo_col:
            df_forma9[fecha_col] = pd.to_datetime(df_forma9[fecha_col], errors='coerce')
            df_forma9_eval = df_forma9[(df_forma9[fecha_col].dt.date >= (fecha_eval_date - pd.Timedelta(days=30))) & (df_forma9[fecha_col].dt.date <= fecha_eval_date)]
            pozos_on_todos = int(df_forma9_eval[df_forma9_eval[dias_col] > 0][pozo_col].nunique())

    pozos_off_todos = max(0, operativos_todos - pozos_on_todos)

    # Run Life promedio
    rl_todos = None
    if reporte_run_life is not None and not reporte_run_life.empty:
        val = reporte_run_life.loc[reporte_run_life['Categoría'] == 'Tiempo de Vida Promedio (Fallados+Ext)', 'Valor']
        if not val.empty:
            try:
                rl_todos = float(val.values[0])
            except Exception:
                rl_todos = None

    # MTBF
    try:
        mtbf_total_val, _ = mtbf_mod.calcular_mtbf(df_bd, fecha_evaluacion)
    except Exception:
        mtbf_total_val = None

    # IF simple
    denom = max(1, run_todos + fallado_todos)
    try:
        if_pct = (fallado_todos / denom) * 100
    except Exception:
        if_pct = None

    # Construir etiquetas
    run_label = f"TOTAL: {run_todos}"
    fallado_label = f"TOTAL: {fallado_todos}"
    operativos_label = f"TOTAL: {operativos_todos}"
    on_label = f"ON: {pozos_on_todos}"
    off_label = f"OFF: {pozos_off_todos}"
    rl_label = f"{rl_todos:.2f} d" if rl_todos is not None else 'N/D'
    mtbf_label = f"{mtbf_total_val:.2f} d" if mtbf_total_val is not None else 'N/D'
    if_label = f"{if_pct:.1f}%" if if_pct is not None else 'N/D'

    # Construir Digraph
    dot = Digraph(comment='KPIs Mini Map', format='png')
    dot.attr(rankdir='LR', splines='polyline', bgcolor='transparent')
    node_attr = {
        'shape': 'box',
        'style': 'filled,rounded',
        'fontname': 'Arial',
        'fontsize': '10',
        'fontcolor': COLOR_TEXTO_DATOS,
        'fillcolor': COLOR_FONDO_CONTENEDOR,
        'color': COLOR_PRINCIPAL,
    }
    dot.attr('node', **node_attr)

    dot.node('KPIS', label='KPIs')
    dot.node('RUN', label=f"Corridas\n{run_label}")
    dot.node('RL', label=f"TiempoVida\n{rl_label}")
    dot.node('MTBF', label=f"TMEF\n{mtbf_label}")
    dot.node('IF', label=f"Ind.Falla\n{if_label}")
    dot.node('ON', label=on_label)
    dot.node('OFF', label=off_label)

    dot.edge('KPIS', 'RUN', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('KPIS', 'RL', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('KPIS', 'MTBF', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('KPIS', 'IF', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('RUN', 'ON', penwidth='2', color=COLOR_PRINCIPAL)
    dot.edge('RUN', 'OFF', penwidth='2', color=COLOR_PRINCIPAL)

    return dot