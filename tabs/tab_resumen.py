"""
tabs/tab_resumen.py
===================
Dashboard General — Layout v3  (Estética refinada)

Estructura:
  1. KPIs HUD Técnicos (No Scroll)
  2. Performance | Vida Útil | Operatividad (Triple Columna 1:1:1)
  3. Campaña Anual (100%)
  4. Treemap (100%)
  5. Detalle Campaña (tabla expandible)
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px

from config import COLOR_PRINCIPAL
import kpis
from grafico import generar_grafico_resumen, render_premium_echarts
from grafico_run_life import render_premium_echarts_run_life, render_premium_echarts_pozos
from styles import render_hud_table
from indice_falla import calcular_indice_falla_anual


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE DISEÑO
# ─────────────────────────────────────────────────────────────────────────────

_SURFACE  = "rgba(8, 12, 28, 0.75)"
_BORDER   = "rgba(255,255,255,0.06)"
_RADIUS   = "8px"

# Paleta de acento por KPI
_CYAN    = "#00e5ff"
_GREEN   = "#00e676"
_RED     = "#ff1744"
_MAGENTA = "#e040fb"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE UI
# ─────────────────────────────────────────────────────────────────────────────

def _inject_global_css() -> None:
    """Inyecta CSS global una sola vez: scrollbar, expander, métricas."""
    st.markdown("""
<style>
/* ── Scrollbar fina ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e2d4a; border-radius: 4px; }

/* ── Expander sin bordes gruesos ── */
.streamlit-expanderHeader {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    color: #00e5ff !important;
    letter-spacing: 1.5px;
    background: rgba(0,229,255,0.04) !important;
    border: 1px solid rgba(0,229,255,0.12) !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(0,229,255,0.08) !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    background: rgba(8,12,28,0.6) !important;
    padding: 8px !important;
}

/* ── Elimina padding excesivo de columnas ── */
[data-testid="column"] > div { padding: 0 4px !important; }

/* ── Ajuste de espacio superior (Zero Waste) ── */
div[data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0px !important;
}

/* Reducir padding interno de los tabs de Streamlit */
div[data-testid="stTab"] {
    padding-top: 0rem !important;
}

.kpi-hierarchy-container {
    margin-top: -10px !important;
}
</style>
""", unsafe_allow_html=True)


def _kpi_card(icon: str, label: str, value: str, color: str, sublabel: str = "") -> str:
    """Card KPI compacta (Legacy)."""
    glow = f"{color}22"
    return f"""
<div style="background:{_SURFACE}; border:1px solid {_BORDER}; border-left:2px solid {color}; border-radius:{_RADIUS}; padding:8px 12px; display:flex; align-items:center; gap:10px; box-shadow:inset 0 0 24px {glow}; min-height:54px;">
    <div style="width:32px; height:32px; background:{glow}; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:1rem;">{icon}</div>
    <div style="min-width:0;">
        <div style="font-size:0.5rem; font-weight:700; color:#455a72; letter-spacing:1.8px; text-transform:uppercase; font-family:'Arial', sans-serif !important;">{label}</div>
        <div style="font-size:1.25rem; font-weight:800; color:{color}; line-height:1.15;">{value}</div>
    </div>
</div>"""


def _section_title(text: str, color: str = _CYAN) -> None:
    """Título de sección: línea izquierda + texto en monospace."""
    st.markdown(
        f"""<div style="
            font-family: 'Arial', sans-serif !important;
            font-size: 0.58rem;
            font-weight: 700;
            color: {color};
            letter-spacing: 2.5px;
            text-transform: uppercase;
            border-left: 2px solid {color};
            padding: 2px 0 2px 8px;
            margin: 15px 0 10px 0;
            opacity: 0.9;
        ">{text}</div>""",
        unsafe_allow_html=True,
    )


def _mini_metric(label: str, value: str, color: str) -> str:
    """Micro-tarjeta para conteos dentro de la campaña anual."""
    return f"""
<div style="background:{color}0d; border:1px solid {color}25; border-radius:6px; padding:5px 10px; margin-bottom:4px;">
    <div style="color:{color}; font-size:0.48rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; font-family:'Arial', sans-serif !important;">{label}</div>
    <div style="font-size:1.3rem; font-weight:900; color:#ecf0f1; line-height:1.1;">{value}</div>
</div>"""


def _echarts_html(options: dict, height: int, chart_id: str) -> str:
    """Wrapper mínimo para ECharts con tema oscuro y contenedor premium."""
    return f"""
<div id="{chart_id}" style="width:100%;height:{height}px;background:#060a1e;border-radius:12px;border:1px solid rgba(0,242,255,0.15);overflow:hidden;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
(function(){{
    var el = document.getElementById('{chart_id}');
    var chart = echarts.init(el, 'dark', {{renderer:'canvas'}});
    chart.setOption({json.dumps(options)});
    new ResizeObserver(function(){{ chart.resize(); }}).observe(el);
}})();
</script>"""


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def render_tab_resumen(
    df_bd_filtered,
    df_forma9_filtered,
    reporte_runes_filtered,
    fecha_evaluacion,
    selected_activo,
):
    """Dashboard General v3 — Layout Optimizado Sin Scroll."""

    _inject_global_css()
    
    # Importar funciones de gráficos al inicio para evitar UnboundLocalError
    from grafico import generar_grafico_resumen
    from grafico_run_life import generar_grafico_run_life, generar_grafico_pozos_indices

    # ── Pre-procesamiento ────────────────────────────────────────────────────
    for col in ('FECHA_PULL', 'FECHA_FALLA', 'FECHA_RUN'):
        if col in df_bd_filtered.columns:
            df_bd_filtered[col] = pd.to_datetime(df_bd_filtered[col], errors='coerce')

    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    anio_campana  = fecha_eval_dt.year

    # Índice de falla
    try:
        indice_resumen_df, _ = calcular_indice_falla_anual(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
    except Exception:
        indice_resumen_df = None

    # Monthly summary
    fig_perf, df_monthly_summary = generar_grafico_resumen(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, titulo="")
    st.session_state['df_monthly_summary'] = df_monthly_summary

    # =========================================================================
    # FILA 1 — KPIs HUD TÉCNICOS (Ancho Completo, No Scroll)
    # =========================================================================
    kpis.mostrar_kpis(
        df_bd=df_bd_filtered,
        reporte_runes=reporte_runes_filtered,
        indice_resumen_df=indice_resumen_df,
        df_forma9=df_forma9_filtered,
        fecha_evaluacion=fecha_evaluacion,
    )
    
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # FILA 2 — PERFORMANCE | VIDA ÚTIL | OPERATIVIDAD (Triple Columna 1:1:1)
    # =========================================================================
    c1, c2, c3 = st.columns(3)

    with c1:
        _section_title("▸ Performance Histórico", _CYAN)
        if not df_monthly_summary.empty:
            render_premium_echarts(df_monthly_summary, titulo="")
        else:
            st.info("Sin datos de performance.")

    with c2:
        _section_title("▸ Tiempo de Vida", "#a855f7")
        if not df_monthly_summary.empty:
            render_premium_echarts_run_life(df_monthly_summary, titulo="")
        else:
            st.info("Sin datos.")

    with c3:
        _section_title("▸ Operatividad", _CYAN)
        if not df_monthly_summary.empty:
            render_premium_echarts_pozos(df_monthly_summary, titulo="")
        else:
            st.info("Sin datos.")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # =========================================================================
    # FILA 3 — CAMPAÑA ANUAL (100%)
    # =========================================================================
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    with st.container():
        _section_title(f"▸ Campaña {anio_campana}", "#ffbd00")
        st.write("") # Fuerza un salto de línea limpio en Streamlit

    if 'FECHA_RUN' not in df_bd_filtered.columns:
        st.info("Sin datos de campaña.")
    else:
        df_camp = df_bd_filtered[df_bd_filtered['FECHA_RUN'].dt.year == anio_campana].copy()

        if df_camp.empty:
            st.info(f"Sin corridas en {anio_campana}.")
        else:
            # Mini-métricas compactas en línea
            df_nv = df_camp[df_camp['RUN'] == 1] if 'RUN' in df_camp.columns else pd.DataFrame()
            df_ws = df_camp[df_camp['RUN'] >  1] if 'RUN' in df_camp.columns else df_camp
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(_mini_metric("Pozos nuevos", str(len(df_nv)), _CYAN),   unsafe_allow_html=True)
            with m2:
                st.markdown(_mini_metric("Well Service", str(len(df_ws)), _MAGENTA), unsafe_allow_html=True)

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

            # Datos para el gráfico
            df_camp['Mes']   = df_camp['FECHA_RUN'].dt.month
            df_camp['Tipo']  = (df_camp['RUN'].apply(lambda x: 'Nuevo' if x == 1 else 'WS')
                                if 'RUN' in df_camp.columns else 'Otro')
            df_camp['Falla'] = (
                df_camp['FECHA_FALLA'].notna() &
                (df_camp['FECHA_FALLA'] <= fecha_eval_dt)
            ).astype(int)

            mes_max   = fecha_eval_dt.month
            idx_meses = range(1, mes_max + 1)
            df_res    = (df_camp.groupby(['Mes', 'Tipo'])
                                .size()
                                .unstack(fill_value=0)
                                .reindex(idx_meses, fill_value=0))
            df_fall   = (df_camp[df_camp['Falla'] == 1]
                                .groupby('Mes').size()
                                .reindex(idx_meses, fill_value=0))

            _MES = ['Ene','Feb','Mar','Abr','May','Jun',
                    'Jul','Ago','Sep','Oct','Nov','Dic']
            cats = [_MES[i - 1] for i in df_res.index]
            d_nv = df_res['Nuevo'].tolist() if 'Nuevo' in df_res.columns else [0]*len(cats)
            d_ws = df_res['WS'].tolist()    if 'WS'    in df_res.columns else [0]*len(cats)
            d_fl = df_fall.tolist()

            # --- CÁLCULO DE MÉTRICAS ADICIONALES PARA CHART LATERAL ---
            val_total_corr = len(df_camp)
            val_nuevos     = len(df_nv)
            val_ws         = len(df_ws)
            val_fallas     = df_camp[df_camp['Falla'] == 1].shape[0]
            val_extraidos  = df_camp[df_camp['FECHA_PULL'].notna()].shape[0]
            val_activos    = val_total_corr - val_extraidos

            opts_camp = {
                "backgroundColor": "transparent",
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(8,14,32,0.92)",
                    "borderColor": "rgba(255,255,255,0.08)",
                    "textStyle": {"color": "#cfd8dc", "fontSize": 11},
                },
                "legend": {
                    "data": ["Nuevos", "Well Service", "Fallas"],
                    "textStyle": {"color": "#546e7a", "fontSize": 9},
                    "bottom": 0,
                    "itemHeight": 6,
                    "itemGap": 14,
                },
                "grid": {
                    "top": "15%", "left": "2%", "right": "2%",
                    "bottom": "16%", "containLabel": True,
                },
                "xAxis": {
                    "type": "category",
                    "data": cats,
                    "axisLabel": {"color": "#546e7a", "fontSize": 9},
                    "axisLine": {"lineStyle": {"color": "rgba(255,255,255,0.06)"}},
                    "axisTick": {"show": False},
                },
                "yAxis": {
                    "type": "value",
                    "axisLabel": {"color": "#546e7a", "fontSize": 9},
                    "splitLine": {"lineStyle": {"color": "rgba(255,255,255,0.04)", "type": "dashed"}},
                },
                "series": [
                    {
                        "name": "Nuevos", "type": "bar", "stack": "total",
                        "data": d_nv,
                        "barMaxWidth": 28,
                        "itemStyle": {
                            "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                      "colorStops": [
                                          {"offset": 0, "color": "#00e5ff"},
                                          {"offset": 1, "color": "#0077b6"},
                                      ]}
                        }
                    },
                    {
                        "name": "Well Service", "type": "bar", "stack": "total",
                        "data": d_ws,
                        "barMaxWidth": 28,
                        "itemStyle": {
                            "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                      "colorStops": [
                                          {"offset": 0, "color": "#e040fb"},
                                          {"offset": 1, "color": "#7b1fa2"},
                                      ]}
                        }
                    },
                    {
                        "name": "Fallas", "type": "line",
                        "data": d_fl,
                        "smooth": True,
                        "symbol": "circle",
                        "symbolSize": 6,
                        "lineStyle": {"width": 3, "color": "#ff1744"},
                        "itemStyle": {"color": "#ff1744", "borderWidth": 2, "borderColor": "#fff"}
                    }
                ]
            }

            opts_run_stats = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "📊 MÉTRICAS DE EJECUCIÓN",
                    "left": "center",
                    "top": 0,
                    "textStyle": {"color": "#00f2ff", "fontSize": 12, "fontFamily": "Arial, sans-serif", "fontWeight": "bold"}
                },
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "grid": {"top": "15%", "left": "5%", "right": "15%", "bottom": "10%", "containLabel": True},
                "xAxis": {"type": "value", "splitLine": {"show": False}, "axisLabel": {"show": False}},
                "yAxis": {
                    "type": "category",
                    "data": ["EXTRAÍDOS", "ACTIVOS", "FALLAS", "WELL SERVICE", "NUEVOS", "CORRIDAS"],
                    "axisLabel": {"color": "#fff", "fontSize": 9, "fontFamily": "Arial, sans-serif"}
                },
                "series": [{
                    "type": "bar",
                    "data": [
                        {"value": val_extraidos, "itemStyle": {"color": "#94a3b8"}},
                        {"value": val_activos,   "itemStyle": {"color": "#00ff9d"}},
                        {"value": val_fallas,    "itemStyle": {"color": "#ff1744"}},
                        {"value": val_ws,        "itemStyle": {"color": "#e040fb"}},
                        {"value": val_nuevos,    "itemStyle": {"color": "#00e5ff"}},
                        {"value": val_total_corr,"itemStyle": {"color": "#00ffa3"}}
                    ],
                    "label": {"show": True, "position": "right", "color": "#fff", "fontSize": 10, "fontFamily": "Arial, sans-serif"},
                    "barMaxWidth": 18,
                    "itemStyle": {"borderRadius": [0, 4, 4, 0]}
                }]
            }

            c_left, c_right = st.columns(2)
            with c_left:
                components.html(_echarts_html(opts_camp, 250, "chart_campana"), height=270)
            with c_right:
                components.html(_echarts_html(opts_run_stats, 250, "chart_run_stats"), height=270)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # =========================================================================
    # FILA 4 — MAPA DE ACTIVOS (Multi-Estado por Pozo)
    # =========================================================================
    _section_title("▸ Mapa de Activos — Estado Operacional", _CYAN)

    # Paleta de estados — solo ON/OFF
    _COLOR_ON   = "#2e7d32"   # Verde oscuro — Encendidos
    _COLOR_OFF  = "#c62828"   # Rojo oscuro  — Apagados

    if df_bd_filtered.empty:
        st.info("Sin datos para el mapa de activos.")
    else:
        hier_cols = [c for c in ('ACTIVO', 'BLOQUE', 'CAMPO', 'POZO') if c in df_bd_filtered.columns]

        if len(hier_cols) < 2:
            st.info("Se necesitan al menos 2 columnas jerárquicas (ACTIVO, BLOQUE, CAMPO, POZO).")
        else:
            try:
                df_tree = df_bd_filtered.copy()

                # ── 1. Limpiar NaN en columnas jerárquicas ─────────────────
                for col in hier_cols:
                    df_tree[col] = df_tree[col].fillna("DESCONOCIDO").astype(str).str.strip()

                # ── Normalizar fechas ───────────────────────────────────────
                fecha_eval_dt = pd.to_datetime(fecha_evaluacion).normalize()
                df_tree['_RUN_D']  = pd.to_datetime(df_tree['FECHA_RUN'],  errors='coerce').dt.normalize() if 'FECHA_RUN'  in df_tree.columns else pd.NaT
                df_tree['_PULL_D'] = pd.to_datetime(df_tree['FECHA_PULL'], errors='coerce').dt.normalize() if 'FECHA_PULL' in df_tree.columns else pd.NaT
                df_tree['_FALL_D'] = pd.to_datetime(df_tree['FECHA_FALLA'],errors='coerce').dt.normalize() if 'FECHA_FALLA' in df_tree.columns else pd.NaT

                run_life_col = 'RUN LIFE' if 'RUN LIFE' in df_tree.columns else None

                # ── Filtrar solo RUNs válidos a fecha de evaluación ────────
                df_eval = df_tree[df_tree['_RUN_D'].notna() & (df_tree['_RUN_D'] <= fecha_eval_dt)].copy()

                # ── Último RUN por POZO (= estado actual del pozo) ─────────
                if 'POZO' in df_eval.columns:
                    df_last = df_eval.sort_values('_RUN_D').groupby('POZO', as_index=False).last()
                else:
                    df_last = df_eval.copy()

                # ── Clasificar igual que kpis.py ───────────────────────────
                # calc_running:    RUN <= fecha_eval AND (no pull OR pull > fecha_eval)
                # calc_fallados:   RUN <= fecha_eval AND falla <= fecha_eval AND (no pull OR pull > fecha_eval)
                # calc_operativos: RUN <= fecha_eval AND (no falla OR falla > fecha_eval) AND (no pull OR pull > fecha_eval)
                m_pull   = df_last['_PULL_D'].notna() & (df_last['_PULL_D'] <= fecha_eval_dt)
                m_fall   = df_last['_FALL_D'].notna() & (df_last['_FALL_D'] <= fecha_eval_dt) & ~m_pull
                m_oper   = (df_last['_FALL_D'].isna() | (df_last['_FALL_D'] > fecha_eval_dt)) & \
                           (df_last['_PULL_D'].isna() | (df_last['_PULL_D'] > fecha_eval_dt))

                # ── ON/OFF: ventana 30 días exactos — IGUAL que kpis.py ────
                pozos_on_set = set()
                if df_forma9_filtered is not None and not df_forma9_filtered.empty:
                    _f9 = df_forma9_filtered.copy()
                    if 'FECHA_FORMA9' in _f9.columns and 'DIAS TRABAJADOS' in _f9.columns and 'POZO' in _f9.columns:
                        _f9['FECHA_FORMA9']    = pd.to_datetime(_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
                        _f9['DIAS TRABAJADOS'] = pd.to_numeric(_f9['DIAS TRABAJADOS'], errors='coerce').fillna(0)
                        _f9_eval = _f9[
                            (_f9['FECHA_FORMA9'] >= (fecha_eval_dt - pd.Timedelta(days=30))) &
                            (_f9['FECHA_FORMA9'] <= fecha_eval_dt)
                        ]
                        pozos_on_set = set(
                            _f9_eval[_f9_eval['DIAS TRABAJADOS'] > 0]['POZO'].astype(str).str.strip().tolist()
                        )

                # Asignar estado — solo ON/OFF para pozos operativos en df_bd
                def _asignar_estado(row):
                    pozo = str(row.get('POZO', '')).strip() if 'POZO' in row.index else ''
                    if m_pull.loc[row.name]: return None   # Extraído → excluir del mapa
                    if m_fall.loc[row.name]: return None   # Fallado → excluir del mapa
                    if m_oper.loc[row.name]:
                        return "ON" if pozo in pozos_on_set else "OFF"
                    return None

                df_last['ESTADO'] = df_last.apply(_asignar_estado, axis=1)

                # Solo pozos operativos (ON o OFF) para el mapa visual
                df_last_oper = df_last[df_last['ESTADO'].notna()].copy()

                # Propagar estado de vuelta a df_tree (para el treemap con jerarquía)
                if 'POZO' in df_tree.columns:
                    pozo_estado = df_last_oper.set_index('POZO')['ESTADO'].to_dict()
                    df_tree['ESTADO'] = df_tree['POZO'].map(pozo_estado)   # NaN = no operativo
                else:
                    df_tree['ESTADO'] = None

                # df_pozo: solo pozos ON/OFF, un registro por celda jerárquica
                agg_dict = {'ESTADO': ('ESTADO', 'last'), 'N_RUNS': ('ESTADO', 'count')}
                if run_life_col:
                    agg_dict['RUN_LIFE'] = (run_life_col, 'mean')
                df_pozo = (
                    df_eval.assign(ESTADO=df_eval['POZO'].map(pozo_estado) if 'POZO' in df_eval.columns else None)
                    .dropna(subset=['ESTADO'])
                    .sort_values('_RUN_D')
                    .groupby(hier_cols, as_index=False)
                    .agg(**agg_dict)
                )
                if 'RUN_LIFE' not in df_pozo.columns:
                    df_pozo['RUN_LIFE'] = 0

                # ── Conteos HUD — MISMA FÓRMULA EXACTA que kpis.py ────────
                # n_on:  unique POZOs en Forma9 (30 días) con DIAS TRABAJADOS > 0
                # n_oper: calc_operativos(df_bd) = filas con RUN<=eval, sin falla, sin pull
                # n_off:  max(0, n_oper - n_on)
                n_on  = int(len(pozos_on_set))
                n_oper = int((
                    (df_tree['_RUN_D'].notna() & (df_tree['_RUN_D'] <= fecha_eval_dt)) &
                    (df_tree['_FALL_D'].isna()  | (df_tree['_FALL_D'] > fecha_eval_dt)) &
                    (df_tree['_PULL_D'].isna()  | (df_tree['_PULL_D'] > fecha_eval_dt))
                ).sum())
                n_off = max(0, n_oper - n_on)
                n_tot = n_on + n_off

                # ── HUD: solo 3 tarjetas compactas ───────────────────────────
                st.markdown(f"""
                <div style="display:flex; gap:12px; flex-wrap:wrap; margin:10px 0 14px 0;">
                    <div style="flex:1; min-width:130px; background:rgba(46,125,50,0.12); border:1px solid {_COLOR_ON}88;
                        border-radius:10px; padding:12px 16px; text-align:center;">
                        <div style="color:{_COLOR_ON}; font-size:2rem; font-weight:900; font-family:Arial;">{n_on}</div>
                        <div style="color:#a5d6a7; font-size:0.65rem; letter-spacing:2px; font-family:Arial; margin-top:4px;">🟢 ENCENDIDOS</div>
                    </div>
                    <div style="flex:1; min-width:130px; background:rgba(198,40,40,0.12); border:1px solid {_COLOR_OFF}88;
                        border-radius:10px; padding:12px 16px; text-align:center;">
                        <div style="color:{_COLOR_OFF}; font-size:2rem; font-weight:900; font-family:Arial;">{n_off}</div>
                        <div style="color:#ef9a9a; font-size:0.65rem; letter-spacing:2px; font-family:Arial; margin-top:4px;">🔴 APAGADOS</div>
                    </div>
                    <div style="flex:1; min-width:130px; background:rgba(0,229,255,0.05); border:1px solid rgba(0,229,255,0.2);
                        border-radius:10px; padding:12px 16px; text-align:center;">
                        <div style="color:#00e5ff; font-size:2rem; font-weight:900; font-family:Arial;">{n_tot}</div>
                        <div style="color:#80deea; font-size:0.65rem; letter-spacing:2px; font-family:Arial; margin-top:4px;">◈ OPERATIVOS</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── 6. Construir go.Treemap — un pase robusto ─────────────
                import plotly.graph_objects as go

                # Paleta 15 tonos oscuros distinguibles para BLOQUEs
                _BP = [
                    "#0a1628","#1a0828","#091a09","#281408","#082820",
                    "#280818","#182808","#280d0d","#08083a","#18082a",
                    "#082818","#202808","#140828","#280a14","#081409",
                ]
                _b_uniq = sorted(df_pozo['BLOQUE'].unique()) if 'BLOQUE' in df_pozo.columns else []
                _b_clr  = {b: _BP[i % len(_BP)] for i, b in enumerate(_b_uniq)}

                S = "|||"   # separador legible para IDs
                _added = set()
                _ids, _lbl, _par, _val, _clr, _cdat = [], [], [], [], [], []

                def _add(node_id, label, parent, value, color, cdat):
                    if node_id not in _added:
                        _ids.append(node_id); _lbl.append(label)
                        _par.append(parent);   _val.append(value)
                        _clr.append(color);    _cdat.append(cdat)
                        _added.add(node_id)

                for _, row in df_pozo.iterrows():
                    a = str(row['ACTIVO']) if 'ACTIVO' in df_pozo.columns else ""
                    b = str(row['BLOQUE']) if 'BLOQUE' in df_pozo.columns else ""
                    c = str(row['CAMPO'])  if 'CAMPO'  in df_pozo.columns else ""
                    p = str(row['POZO'])   if 'POZO'   in df_pozo.columns else str(row.name)
                    estado = str(row.get('ESTADO', ''))
                    rl = float(row.get('RUN_LIFE', 1) or 1)
                    nr = int(row.get('N_RUNS', 0) or 0)

                    # — nodo ACTIVO —
                    if 'ACTIVO' in hier_cols:
                        _add(f"A{S}{a}", a, "", 0, "#060c16", ["", 0, 0])

                    # — nodo BLOQUE —
                    if 'BLOQUE' in hier_cols:
                        par_b = f"A{S}{a}" if 'ACTIVO' in hier_cols else ""
                        _add(f"B{S}{a}{S}{b}", b, par_b, 0, _b_clr.get(b,"#111827"), ["", 0, 0])

                    # — nodo CAMPO —
                    if 'CAMPO' in hier_cols:
                        if   'BLOQUE' in hier_cols: par_c = f"B{S}{a}{S}{b}"
                        elif 'ACTIVO' in hier_cols: par_c = f"A{S}{a}"
                        else:                        par_c = ""
                        _add(f"C{S}{a}{S}{b}{S}{c}", c, par_c, 0, _b_clr.get(b,"#111827"), ["", 0, 0])

                    # — hoja POZO —
                    if   'CAMPO'  in hier_cols: par_p = f"C{S}{a}{S}{b}{S}{c}"
                    elif 'BLOQUE' in hier_cols: par_p = f"B{S}{a}{S}{b}"
                    elif 'ACTIVO' in hier_cols: par_p = f"A{S}{a}"
                    else:                        par_p = ""
                    leaf_clr = _COLOR_ON if estado == 'ON' else _COLOR_OFF
                    _add(f"P{S}{a}{S}{b}{S}{c}{S}{p}", p, par_p,
                         max(1.0, rl), leaf_clr, [estado, rl, nr])

                fig_tree = go.Figure(go.Treemap(
                    ids=_ids, labels=_lbl, parents=_par, values=_val,
                    marker=dict(
                        colors=_clr,
                        line=dict(width=1.5, color='#0a0f1a'),
                        pad=dict(t=18, l=4, r=4, b=4),
                    ),
                    customdata=_cdat,
                    texttemplate="<b>%{label}</b>",
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Estado: %{customdata[0]}<br>"
                        "Run Life: %{customdata[1]:.0f} días<br>"
                        "Corridas: %{customdata[2]}<br>"
                        "<extra></extra>"
                    ),
                    textfont=dict(color="#ffffff", size=11),
                ))

                fig_tree.update_layout(
                    margin=dict(t=10, l=4, r=4, b=4),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=570,
                    font_family="Arial",
                    font_color="#ffffff",
                )

                # Contenedor HUD Premium
                st.markdown(
                    '<div style="background:#050c1a; border:1px solid rgba(0,229,255,0.15);'
                    ' border-radius:15px; padding:14px; margin-bottom:10px;">',
                    unsafe_allow_html=True
                )
                st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
                st.markdown("</div>", unsafe_allow_html=True)

                # ── 7. Tabla resumen colapsable por estado ─────────────────
                with st.expander("📋 VER DETALLE POR ESTADO DE POZO", expanded=False):
                    show_cols = [c for c in (hier_cols + ['ESTADO', 'RUN_LIFE', 'N_RUNS']) if c in df_pozo.columns]
                    df_show = df_pozo[show_cols].copy()
                    if 'RUN_LIFE' in df_show.columns:
                        df_show['RUN_LIFE'] = df_show['RUN_LIFE'].apply(lambda x: f"{x:.0f} d" if pd.notna(x) else "—")
                    df_show = df_show.sort_values('ESTADO')
                    render_hud_table(df_show, table_id="tabla_mapa_activos")

            except Exception as e:
                st.warning(f"Mapa de activos no disponible: {e}")

    # =========================================================================
    # FILA 5 — DETALLE CAMPAÑA (expandible)
    # =========================================================================
    with st.expander(f"📄 VER DETALLE DE CORRIDAS (CAMPAÑA ANUAL)", expanded=False):
        if 'FECHA_RUN' not in df_bd_filtered.columns:
            st.info("Columna FECHA_RUN no disponible.")
        else:
            df_det = df_bd_filtered[df_bd_filtered['FECHA_RUN'].dt.year == anio_campana].copy()
            if df_det.empty:
                st.info(f"No hay corridas registradas en {anio_campana}.")
            else:
                st.markdown(
                    f"<div style='color:#455a72;font-family:\"Arial\",sans-serif !important;"
                    f"font-size:0.6rem;margin-bottom:6px;letter-spacing:1px;'>"
                    f"Campaña {anio_campana} · {len(df_det)} corridas</div>",
                    unsafe_allow_html=True,
                )
                cols_show = [c for c in ('POZO', 'RUN', 'ACTIVO', 'CAMPO', 'BLOQUE',
                                          'ALS', 'PROVEEDOR', 'FECHA_RUN', 'RUN LIFE')
                             if c in df_det.columns]
                df_render = df_det[cols_show].copy()
                if 'FECHA_RUN' in df_render.columns:
                    df_render['FECHA_RUN'] = df_render['FECHA_RUN'].dt.strftime('%Y-%m-%d')
                if 'RUN LIFE' in df_render.columns:
                    df_render['RUN LIFE'] = df_render['RUN LIFE'].apply(
                        lambda x: f"{x:.0f} d" if pd.notna(x) else "—")
                df_render = df_render.sort_values('FECHA_RUN', ascending=False)
                render_hud_table(df_render, table_id="tabla_detalle_campana")