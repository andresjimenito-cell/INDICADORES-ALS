import streamlit as st
import pandas as pd
try:
    from graphviz import Digraph
    HAS_GRAPHVIZ = True
except ImportError:
    HAS_GRAPHVIZ = False

import datetime 
import pandas as pd 
from ui.theme import get_colors
import core.mtbf as mtbf_mod

import ui.tema as tema

_colors = get_colors()
# Usar Magenta Neon como color principal para KPIs
COLOR_PRINCIPAL = getattr(tema, 'COLOR_PRINCIPAL', '#137659')
_bg_raw = _colors.get('background', None)
if isinstance(_bg_raw, str) and _bg_raw.strip().lower() in ('#ffffff', 'white'):
    COLOR_FONDO_OSCURO = None
else:
    COLOR_FONDO_OSCURO = '#f5f7f6'
COLOR_FONDO_CONTENEDOR = '#ffffff'
COLOR_SOMBRA = 'transparent'

# Colores adicionales específicos locales
COLOR_TEXTO_DATOS = '#475569'
COLOR_TEXTO_PRINCIPAL = '#1f221e'

def mostrar_kpis(df_bd, reporte_runes=None, reporte_run_life=None, indice_resumen_df=None, mtbf_global=None, mtbf_als=None, df_forma9=None, fecha_evaluacion=None):
    # Cargar bases de datos crudas sin el filtro de fecha de inicio para los KPIs superiores
    df_bd_raw = st.session_state.get('df_bd_calculated')
    df_forma9_raw = st.session_state.get('df_forma9_calculated')
    
    if fecha_evaluacion is None:
        try:
            state_val = st.session_state.get('fecha_evaluacion_state')
            if state_val is not None:
                fecha_evaluacion = pd.to_datetime(state_val)
            else:
                fecha_evaluacion = datetime.datetime.now()
        except Exception:
            fecha_evaluacion = datetime.datetime.now()
    else:
        try:
            fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
        except Exception:
            fecha_evaluacion = datetime.datetime.now()

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).normalize()

    if df_bd_raw is not None:
        df_bd = df_bd_raw.copy()
        if 'ACTIVO' in df_bd.columns:
            df_bd = df_bd[df_bd['ACTIVO'].astype(str).str.upper().str.strip() != 'ECUADOR']
        # Aplicar filtros del sidebar
        _filtros = {
            'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
            'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
            'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
            'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
            'PROVEEDOR': st.session_state.get('general_proveedor_filter', 'TODOS'),
            'NICK':      st.session_state.get('general_nick_filter',      'TODOS'),
        }
        for col, val in _filtros.items():
            if val != 'TODOS' and col in df_bd.columns:
                df_bd = df_bd[df_bd[col] == val]
        
        # Filtrar hasta fecha_evaluacion
        df_bd['FECHA_RUN_TEMP'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')
        df_bd = df_bd[df_bd['FECHA_RUN_TEMP'].dt.normalize() <= fecha_eval_date].copy()
        df_bd['FECHA_FALLA'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
        df_bd.loc[df_bd['FECHA_FALLA'].dt.normalize() > fecha_eval_date, 'FECHA_FALLA'] = pd.NaT

    if df_forma9_raw is not None:
        df_forma9 = df_forma9_raw.copy()
        # Filtrar forma 9 por pozos en df_bd
        pozos_en_bd = df_bd['POZO'].unique() if 'POZO' in df_bd.columns else []
        df_forma9 = df_forma9[df_forma9['POZO'].isin(pozos_en_bd)].copy()

    # El filtro de comparativa ahora se gestiona desde el header global.
    selected_als = st.session_state.get('kpis_als_filter', 'ESP')

    if selected_als and selected_als != 'TODOS':
        df_bd_als = df_bd[df_bd['ALS'].astype(str).str.strip() == str(selected_als).strip()].copy()
    else:
        df_bd_als = df_bd.copy()

    # === SOLUCIÓN: Premium KPI Hierarchy Map v5.0 (Vibrant & Interactive) ===
    from core.run_life_efectivo import calcular_run_life_efectivo
    import streamlit.components.v1 as components
    
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

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).normalize()
    fecha_ini_date = st.session_state.get('fecha_inicio_state')
    if fecha_ini_date is not None:
        fecha_ini_date = pd.to_datetime(fecha_ini_date).normalize()
    else:
        fecha_ini_date = fecha_eval_date - pd.Timedelta(days=30)

    df_bd['FECHA_RUN_DATE'] = pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce').dt.normalize()
    df_bd['FECHA_PULL_DATE'] = pd.to_datetime(df_bd['FECHA_PULL'], errors='coerce').dt.normalize()
    df_bd['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce').dt.normalize()

    def filtrar_als(df, als):
        if als and als != 'TODOS' and 'ALS' in df.columns:
            return df[df['ALS'] == als].copy()
        return df.copy()

    def calc_running(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))]['POZO'].nunique() if 'POZO' in df.columns else 0
    def calc_fallados(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_FALLA_DATE'].notna()) & (df['FECHA_FALLA_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))]['POZO'].nunique() if 'POZO' in df.columns else 0
    def calc_operativos(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_FALLA_DATE'].isna() | (df['FECHA_FALLA_DATE'] > fecha_eval)) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))]['POZO'].nunique() if 'POZO' in df.columns else 0

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

    on_label = f"TOTAL: 0\n{selected_als}: 0"
    off_label = f"TOTAL: 0\n{selected_als}: 0"

    if df_forma9 is not None:
        df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
        df_forma9['DIAS TRABAJADOS'] = pd.to_numeric(df_forma9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
        if 'SISTEMA ALS' in df_forma9.columns:
            df_forma9 = df_forma9.rename(columns={'SISTEMA ALS': 'ALS'})
        
        mes_eval = fecha_eval_date.month
        anio_eval = fecha_eval_date.year
        df_forma9_eval = df_forma9[
            (df_forma9['FECHA_FORMA9'].dt.month == mes_eval) &
            (df_forma9['FECHA_FORMA9'].dt.year == anio_eval)
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
        
    rl_todos = df_bd['RUN LIFE'].mean() if not df_bd.empty and 'RUN LIFE' in df_bd.columns else 0
    rl_als = df_bd_als_calc['RUN LIFE'].mean() if not df_bd_als_calc.empty and 'RUN LIFE' in df_bd_als_calc.columns else 0
    rl_label = f"TOTAL: {rl_todos:.2f} Días\n{selected_als}: {rl_als:.2f} Días"

    try:
        from core.run_life_efectivo import calcular_run_life_efectivo
        rle_total_val, _ = calcular_run_life_efectivo(df_bd, df_forma9, fecha_evaluacion)
        _, df_bd_als_rle = calcular_run_life_efectivo(df_bd_als_calc, df_forma9, fecha_evaluacion)
        rle_als_val = 0
        if df_bd_als_rle is not None and 'RUN_LIFE_EFECTIVO' in df_bd_als_rle.columns:
            rle_als_val = df_bd_als_rle['RUN_LIFE_EFECTIVO'].mean()
        rle_label = f"TOTAL: {rle_total_val:.2f} Días\n{selected_als}: {rle_als_val:.2f} Días"
    except Exception:
        rle_label = f"TOTAL: {rl_todos:.1f} D\n{selected_als}: {rl_als:.1f} D"

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
        
    from core.indice_falla import calcular_indice_falla_anual
    if_on = get_if_val(indice_resumen_df, 'Índice de Falla ON')
    
    try:
        if selected_als and selected_als != 'TODOS':
            if df_forma9 is not None:
                df_forma9_copy = df_forma9.copy()
                if 'SISTEMA ALS' in df_forma9_copy.columns:
                    df_forma9_copy = df_forma9_copy.rename(columns={'SISTEMA ALS': 'ALS'})
                if 'ALS' in df_forma9_copy.columns:
                    df_forma9_als = df_forma9_copy[df_forma9_copy['ALS'] == selected_als].copy()
                else:
                    df_forma9_als = df_forma9_copy
            else:
                df_forma9_als = None
                
            indice_resumen_df_als, _ = calcular_indice_falla_anual(df_bd_als, df_forma9_als, fecha_evaluacion)
            if_als_on = get_if_val(indice_resumen_df_als, 'Índice de Falla ALS ON')
        else:
            if_als_on = get_if_val(indice_resumen_df, 'Índice de Falla ALS ON')
    except Exception:
        if_als_on = "N/D"
        
    if_label = f"TOTAL ON: {if_on}\n{selected_als} ON: {if_als_on}"

    def format_card_val(text, als_color="#137659"):
        parts = text.split("\n")
        total_val = parts[0].replace("TOTAL: ", "").replace("TOTAL ON: ", "")
        als_label = parts[1].split(":")[0] if len(parts) > 1 else ""
        als_val = parts[1].split(":")[1].strip() if len(parts) > 1 else ""
        
        return f"""
            <div style="margin-top: 2px; text-align: center;">
                <div style="font-size: 0.55rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Global</div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #1f221e; line-height: 1;">{total_val}</div>
                <div style="margin-top: 4px;"></div>
                <div style="font-size: 0.55rem; color: #475569; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">{als_label}</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: {als_color}; line-height: 1;">{als_val}</div>
            </div>
        """

    cards_data = [
        {"title": "Corridas", "icon": "↻", "val": run_label, "color": "#137659"},
        {"title": "Operativos", "icon": "◈", "val": operativos_label, "color": "#095139"},
        {"title": "Activos ON", "icon": "⚡", "val": on_label, "color": "#c09c2e"},
        {"title": "Apagados OFF", "icon": "🔌", "val": off_label, "color": "#5b5c55"},
        {"title": "Fallados", "icon": "◉", "val": fallado_label, "color": "#d32f2f"},
        {"title": "Índice Falla", "icon": "⚠️", "val": if_label, "color": "#d32f2f"},
        {"title": "MTBF", "icon": "⏱️", "val": mtbf_label, "color": "#137659"},
        {"title": "Run Life", "icon": "⏳", "val": rl_label, "color": "#c09c2e"},
        {"title": "RL Efectivo", "icon": "✅", "val": rle_label, "color": "#095139"},
    ]

    cards_html = ""
    for c in cards_data:
        cards_html += f"""
        <div class="kpi-card-premium" style="border-top: 3px solid {c['color']}; align-items: center; text-align: center;">
            <div class="kpi-icon-container" style="background: {c['color']}15; color: {c['color']}; margin: 0 auto 10px auto;">
                {c['icon']}
            </div>
            <div class="kpi-content" style="align-items: center; text-align: center;">
                <div class="kpi-title" style="text-align: center; width: 100%;">{c['title']}</div>
                {format_card_val(c['val'], c['color'])}
            </div>
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html class="light">
<head>
    <meta charset="utf-8"/>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        
        body {{ 
            background-color: #f5f7f6 !important; 
            background: #f5f7f6 !important; 
            font-family: 'Inter', sans-serif !important; 
            margin: 0; 
            padding: 4px; 
            overflow: hidden; 
        }}
        
        @keyframes countUp {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .hud-grid {{
            display: grid;
            grid-template-columns: repeat(9, 1fr);
            gap: 10px;
            width: 100%;
        }}

        .kpi-card-premium {{
            background: linear-gradient(135deg, #f8fdfb 0%, #ffffff 100%);
            border: 1.5px solid rgba(19, 118, 89, 0.13);
            border-radius: 16px;
            padding: 10px 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 4px;
            min-width: 0;
            height: 155px;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
            box-shadow: 0 2px 8px rgba(19, 118, 89, 0.04), 0 8px 32px rgba(19, 118, 89, 0.06);
            position: relative;
            overflow: hidden;
            animation: countUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both;
        }}

        .kpi-card-premium:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(19, 118, 89, 0.10), 0 12px 40px rgba(19, 118, 89, 0.12);
            border-color: rgba(19, 118, 89, 0.25);
        }}

        .kpi-icon-container {{
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }}

        .kpi-content {{
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .kpi-title {{
            font-family: 'Inter', sans-serif !important;
            font-size: 0.62rem;
            font-weight: 800;
            color: #455a72;
            text-transform: uppercase;
            letter-spacing: 1px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
        }}

    </style>
</head>
<body>
    <div class="hud-grid">
        {cards_html}
    </div>
</body>
</html>
"""
    components.html(html_content, height=180, scrolling=False)


def build_kpis_graph(df_bd, df_forma9=None, reporte_run_life=None, indice_resumen_df=None, selected_als='TODOS', fecha_evaluacion=None):
    if not HAS_GRAPHVIZ:
        return None
    df_bd = df_bd.copy()
    df_bd.columns = [str(c).upper().strip() for c in df_bd.columns]
    if df_forma9 is not None:
        df_forma9 = df_forma9.copy()
        df_forma9.columns = [str(c).upper().strip() for c in df_forma9.columns]
        if 'SISTEMA ALS' in df_forma9.columns and 'ALS' not in df_forma9.columns:
            df_forma9 = df_forma9.rename(columns={'SISTEMA ALS': 'ALS'})

    if fecha_evaluacion is None:
        fecha_evaluacion = datetime.datetime.now()
    else:
        try:
            fecha_evaluacion = pd.to_datetime(fecha_evaluacion)
        except Exception:
            fecha_evaluacion = datetime.datetime.now()

    fecha_eval_date = pd.to_datetime(fecha_evaluacion).normalize()

    for col in ['FECHA_RUN', 'FECHA_PULL', 'FECHA_FALLA']:
        if col in df_bd.columns:
            df_bd[col + '_DATE'] = pd.to_datetime(df_bd[col], errors='coerce').dt.normalize()
        else:
            df_bd[col + '_DATE'] = pd.NaT

    def filtrar_als(df, als):
        if als and als != 'TODOS' and 'ALS' in df.columns:
            return df[df['ALS'] == als].copy()
        return df.copy()

    def calc_running(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))]['POZO'].nunique() if 'POZO' in df.columns else 0
    def calc_fallados(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_FALLA_DATE'].notna()) & (df['FECHA_FALLA_DATE'] <= fecha_eval) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))]['POZO'].nunique() if 'POZO' in df.columns else 0
    def calc_operativos(df, fecha_eval):
        return df[(df['FECHA_RUN_DATE'] <= fecha_eval) & (df['FECHA_FALLA_DATE'].isna() | (df['FECHA_FALLA_DATE'] > fecha_eval)) & (df['FECHA_PULL_DATE'].isna() | (df['FECHA_PULL_DATE'] > fecha_eval))]['POZO'].nunique() if 'POZO' in df.columns else 0

    df_bd_als = filtrar_als(df_bd, selected_als)
    run_todos = calc_running(df_bd, fecha_eval_date)
    fallado_todos = calc_fallados(df_bd, fecha_eval_date)
    operativos_todos = calc_operativos(df_bd, fecha_eval_date)

    pozos_on_todos = 0
    if df_forma9 is not None and not df_forma9.empty:
        fecha_col = next((c for c in df_forma9.columns if 'FECHA' in c), None)
        dias_col = next((c for c in df_forma9.columns if 'DIAS' in c), None)
        pozo_col = next((c for c in df_forma9.columns if 'POZO' in c), None)
        if fecha_col and dias_col and pozo_col:
            df_forma9[fecha_col] = pd.to_datetime(df_forma9[fecha_col], errors='coerce')
            fecha_ini_date = st.session_state.get('fecha_inicio_state')
            if fecha_ini_date is not None:
                fecha_ini_date = pd.to_datetime(fecha_ini_date).normalize()
            else:
                fecha_ini_date = fecha_eval_date - pd.Timedelta(days=30)
            df_forma9_eval = df_forma9[(df_forma9[fecha_col].dt.normalize() >= fecha_ini_date) & (df_forma9[fecha_col].dt.normalize() <= fecha_eval_date)]
            pozos_on_todos = int(df_forma9_eval[df_forma9_eval[dias_col] > 0][pozo_col].nunique())

    pozos_off_todos = max(0, operativos_todos - pozos_on_todos)

    rl_todos = None
    if reporte_run_life is not None and not reporte_run_life.empty:
        val = reporte_run_life.loc[reporte_run_life['Categoría'] == 'Tiempo de Vida Promedio (Fallados+Ext)', 'Valor']
        if not val.empty:
            try:
                rl_todos = float(val.values[0])
            except Exception:
                rl_todos = None

    try:
        mtbf_total_val, _ = mtbf_mod.calcular_mtbf(df_bd, fecha_evaluacion)
    except Exception:
        mtbf_total_val = None

    denom = max(1, run_todos + fallado_todos)
    try:
        if_pct = (fallado_todos / denom) * 100
    except Exception:
        if_pct = None

    run_label = f"TOTAL: {run_todos}"
    fallado_label = f"TOTAL: {fallado_todos}"
    operativos_label = f"TOTAL: {operativos_todos}"
    on_label = f"ON: {pozos_on_todos}"
    off_label = f"OFF: {pozos_off_todos}"
    rl_label = f"{rl_todos:.2f} d" if rl_todos is not None else 'N/D'
    mtbf_label = f"{mtbf_total_val:.2f} d" if mtbf_total_val is not None else 'N/D'
    if_label = f"{if_pct:.1f}%" if if_pct is not None else 'N/D'

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
