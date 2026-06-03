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

_SURFACE  = "#ffffff"
_BORDER   = "rgba(19, 118, 89, 0.15)"
_RADIUS   = "8px"

# Paleta de acento por KPI
_CYAN    = "#137659"
_GREEN   = "#2e7d32"
_RED     = "#c62828"
_MAGENTA = "#c09c2e"


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
::-webkit-scrollbar-thumb { background: rgba(19, 118, 89, 0.25); border-radius: 4px; }

/* ── Expander sin bordes gruesos ── */
.streamlit-expanderHeader {
    font-family: 'Arial', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    color: #137659 !important;
    letter-spacing: 1.5px;
    background: rgba(19, 118, 89, 0.05) !important;
    border: 1px solid rgba(19, 118, 89, 0.15) !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(19, 118, 89, 0.1) !important;
    border-top: none !important;
    border-radius: 0 0 6px 6px !important;
    background: #ffffff !important;
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
    <div style="font-size:1.3rem; font-weight:900; color:#1f221e; line-height:1.1;">{value}</div>
</div>"""


def _echarts_html(options: dict, height: int, chart_id: str) -> str:
    """Wrapper mínimo para ECharts con tema claro y contenedor premium."""
    return f"""
<div id="{chart_id}" style="width:100%;height:{height}px;background:#ffffff;border-radius:12px;border:1px solid rgba(19, 118, 89, 0.15);overflow:hidden;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
(function(){{
    var el = document.getElementById('{chart_id}');
    var chart = echarts.init(el, null, {{renderer:'canvas'}});
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
    
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # FILA 2 — TRES COLUMNAS: Tiempo de Vida | Operatividad | Campaña 2026
    # =========================================================================

    # Pre-calcular datos de campaña antes de abrir columnas
    df_camp = pd.DataFrame()
    df_res  = pd.DataFrame()
    df_fall = pd.Series(dtype=int)
    idx_meses = range(1, 1)
    val_total_corr = val_nuevos = val_ws = val_fallas = val_extraidos = val_activos = 0
    cats = d_nv = d_ws = d_fl = []

    if 'FECHA_RUN' in df_bd_filtered.columns:
        df_camp = df_bd_filtered[df_bd_filtered['FECHA_RUN'].dt.year == anio_campana].copy()
        if not df_camp.empty:
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

            df_nv_df = df_camp[df_camp['RUN'] == 1] if 'RUN' in df_camp.columns else pd.DataFrame()
            df_ws_df = df_camp[df_camp['RUN'] >  1] if 'RUN' in df_camp.columns else df_camp
            val_total_corr = len(df_camp)
            val_nuevos     = len(df_nv_df)
            val_ws         = len(df_ws_df)
            val_fallas     = df_camp[df_camp['Falla'] == 1].shape[0]
            val_extraidos  = df_camp[df_camp['FECHA_PULL'].notna()].shape[0]
            val_activos    = val_total_corr - val_extraidos

    col_vida, col_oper, col_camp = st.columns(3)

    with col_vida:
        _section_title("▸ Tiempo de Vida", _CYAN)
        if not df_monthly_summary.empty:
            render_premium_echarts_run_life(df_monthly_summary, titulo="")
        else:
            st.info("Sin datos.")

    with col_oper:
        _section_title("▸ Operatividad", _CYAN)
        if not df_monthly_summary.empty:
            render_premium_echarts_pozos(df_monthly_summary, titulo="")
        else:
            st.info("Sin datos.")

    with col_camp:
        _section_title(f"▸ Campaña {anio_campana}", _CYAN)
        if df_camp.empty:
            st.info(f"Sin corridas en {anio_campana}.")
        else:
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(_mini_metric("Nuevos", str(val_nuevos), _CYAN), unsafe_allow_html=True)
            with m2:
                st.markdown(_mini_metric("WS", str(val_ws), _MAGENTA), unsafe_allow_html=True)

            st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

            opts_camp = {
                "backgroundColor": "#ffffff",
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(255,255,255,0.95)",
                    "borderColor": "rgba(19,118,89,0.15)",
                    "textStyle": {"color": "#1f221e", "fontSize": 11},
                },
                "legend": {
                    "data": ["Nuevos", "Well Service", "Fallas"],
                    "textStyle": {"color": "#1f221e", "fontSize": 8},
                    "bottom": 0,
                    "itemHeight": 6,
                    "itemGap": 10,
                },
                "grid": {
                    "top": "8%", "left": "2%", "right": "2%",
                    "bottom": "20%", "containLabel": True,
                },
                "xAxis": {
                    "type": "category",
                    "data": cats,
                    "axisLabel": {"color": "#1f221e", "fontSize": 7},
                    "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.15)"}},
                    "axisTick": {"show": False},
                },
                "yAxis": {
                    "type": "value",
                    "axisLabel": {"color": "#1f221e", "fontSize": 7},
                    "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)", "type": "dashed"}},
                },
                "series": [
                    {
                        "name": "Nuevos", "type": "bar", "stack": "total",
                        "data": d_nv, "barMaxWidth": 18,
                        "itemStyle": {
                            "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                      "colorStops": [
                                          {"offset": 0, "color": "#137659"},
                                          {"offset": 1, "color": "#095139"},
                                      ]}
                        }
                    },
                    {
                        "name": "Well Service", "type": "bar", "stack": "total",
                        "data": d_ws, "barMaxWidth": 18,
                        "itemStyle": {
                            "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                      "colorStops": [
                                          {"offset": 0, "color": "#c09c2e"},
                                          {"offset": 1, "color": "#9b791e"},
                                      ]}
                        }
                    },
                    {
                        "name": "Fallas", "type": "line",
                        "data": d_fl, "smooth": True,
                        "symbol": "circle", "symbolSize": 5,
                        "lineStyle": {"width": 2, "color": "#c62828"},
                        "itemStyle": {"color": "#c62828", "borderWidth": 2, "borderColor": "#fff"}
                    }
                ]
            }

            opts_run_stats = {
                "backgroundColor": "#ffffff",
                "title": {
                    "text": "📊 EJECUCIÓN",
                    "left": "center", "top": 2,
                    "textStyle": {"color": "#137659", "fontSize": 9, "fontFamily": "Arial, sans-serif", "fontWeight": "bold"}
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(255,255,255,0.95)",
                    "borderColor": "rgba(19,118,89,0.15)",
                    "textStyle": {"color": "#1f221e"}
                },
                "grid": {"top": "18%", "left": "3%", "right": "18%", "bottom": "8%", "containLabel": True},
                "xAxis": {"type": "value", "splitLine": {"show": False}, "axisLabel": {"show": False}},
                "yAxis": {
                    "type": "category",
                    "data": ["EXTRAÍDOS", "ACTIVOS", "FALLAS", "WS", "NUEVOS", "TOTAL"],
                    "axisLabel": {"color": "#455a72", "fontSize": 7, "fontFamily": "Arial, sans-serif"}
                },
                "series": [{
                    "type": "bar",
                    "data": [
                        {"value": val_extraidos,   "itemStyle": {"color": "#94a3b8"}},
                        {"value": val_activos,     "itemStyle": {"color": "#137659"}},
                        {"value": val_fallas,      "itemStyle": {"color": "#c62828"}},
                        {"value": val_ws,          "itemStyle": {"color": "#c09c2e"}},
                        {"value": val_nuevos,      "itemStyle": {"color": "#8fbc8f"}},
                        {"value": val_total_corr,  "itemStyle": {"color": "#5b8c5a"}}
                    ],
                    "label": {"show": True, "position": "right", "color": "#1f221e", "fontSize": 8, "fontFamily": "Arial, sans-serif"},
                    "barMaxWidth": 12,
                    "itemStyle": {"borderRadius": [0, 4, 4, 0]}
                }]
            }

            components.html(_echarts_html(opts_camp,     165, "chart_campana"),    height=178)
            components.html(_echarts_html(opts_run_stats, 155, "chart_run_stats"), height=168)

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    # =========================================================================
    # FILA 3 — TABLA DE RESUMEN MENSUAL DE CAMPAÑA (colapsada)
    # =========================================================================
    if 'FECHA_RUN' in df_bd_filtered.columns and not df_camp.empty:
        with st.expander("📅 TABLA DE RESUMEN MENSUAL DE CAMPAÑA", expanded=False):
            selected_als = st.session_state.get('kpis_als_filter', 'ESP')

            if selected_als and selected_als != 'TODOS':
                df_bd_als = df_bd_filtered[df_bd_filtered['ALS'].astype(str).str.strip() == str(selected_als).strip()].copy()
            else:
                df_bd_als = df_bd_filtered.copy()

            df_mensual = pd.DataFrame(index=idx_meses)
            _MES_COMPLETO = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            df_mensual['Mes'] = [_MES_COMPLETO[m - 1] for m in df_mensual.index]
            
            # Fallas Totales del mes
            df_mensual['Fallas Totales'] = [
                df_bd_filtered[
                    (df_bd_filtered['FECHA_FALLA'].dt.month == m) &
                    (df_bd_filtered['FECHA_FALLA'].dt.year == anio_campana)
                ].shape[0] for m in df_mensual.index
            ]
            
            # Fallas ALS del mes (para el ALS seleccionado)
            df_mensual[f'Fallas {selected_als}'] = [
                df_bd_als[
                    (df_bd_als['FECHA_FALLA'].dt.month == m) &
                    (df_bd_als['FECHA_FALLA'].dt.year == anio_campana)
                ].shape[0] for m in df_mensual.index
            ]
            
            import calendar
            pozos_operativos_lista = []
            pozos_on_lista = []
            pozos_off_lista = []
            pozos_operativos_als_lista = []
            pozos_nuevos_lista = []
            pozos_ws_lista = []
            pozos_reactivados_lista = []
            
            df_bd_f = df_bd_filtered.copy()
            df_bd_f['FECHA_RUN_DATE'] = df_bd_f['FECHA_RUN'].dt.normalize()
            df_bd_f['FECHA_FALLA_DATE'] = df_bd_f['FECHA_FALLA'].dt.normalize()
            df_bd_f['FECHA_PULL_DATE'] = df_bd_f['FECHA_PULL'].dt.normalize()
            
            df_bd_als_c = df_bd_als.copy()
            df_bd_als_c['FECHA_RUN_DATE'] = df_bd_als_c['FECHA_RUN'].dt.normalize()
            df_bd_als_c['FECHA_FALLA_DATE'] = df_bd_als_c['FECHA_FALLA'].dt.normalize()
            df_bd_als_c['FECHA_PULL_DATE'] = df_bd_als_c['FECHA_PULL'].dt.normalize()
            
            df_forma9_f = df_forma9_filtered.copy()
            df_forma9_f['FECHA_FORMA9_DATE'] = df_forma9_f['FECHA_FORMA9'].dt.normalize()
            
            for m in idx_meses:
                last_day = calendar.monthrange(anio_campana, m)[1]
                date_limit = pd.Timestamp(year=anio_campana, month=m, day=last_day).normalize()
                
                # 1. Pozos Operativos Totales
                op_tot = df_bd_f[
                    (df_bd_f['FECHA_RUN_DATE'] <= date_limit) &
                    (df_bd_f['FECHA_FALLA_DATE'].isna() | (df_bd_f['FECHA_FALLA_DATE'] > date_limit)) &
                    (df_bd_f['FECHA_PULL_DATE'].isna() | (df_bd_f['FECHA_PULL_DATE'] > date_limit))
                ]['POZO'].nunique()
                pozos_operativos_lista.append(op_tot)
                
                # 2. Pozos ON
                pozos_on = df_forma9_f[
                    (df_forma9_f['FECHA_FORMA9_DATE'].dt.month == m) &
                    (df_forma9_f['FECHA_FORMA9_DATE'].dt.year == anio_campana) &
                    (df_forma9_f['DIAS TRABAJADOS'] > 0)
                ]['POZO'].nunique()
                pozos_on_lista.append(pozos_on)
                
                # 3. Pozos OFF
                pozos_off = max(0, op_tot - pozos_on)
                pozos_off_lista.append(pozos_off)
                
                # 4. Pozos Operativos ALS
                op_als = df_bd_als_c[
                    (df_bd_als_c['FECHA_RUN_DATE'] <= date_limit) &
                    (df_bd_als_c['FECHA_FALLA_DATE'].isna() | (df_bd_als_c['FECHA_FALLA_DATE'] > date_limit)) &
                    (df_bd_als_c['FECHA_PULL_DATE'].isna() | (df_bd_als_c['FECHA_PULL_DATE'] > date_limit))
                ]['POZO'].nunique()
                pozos_operativos_als_lista.append(op_als)
                
                # 5. Pozos nuevos e intervenciones (WS)
                n_nuevo = df_res.loc[m, 'Nuevo'] if 'Nuevo' in df_res.columns and m in df_res.index else 0
                n_ws = df_res.loc[m, 'WS'] if 'WS' in df_res.columns and m in df_res.index else 0
                pozos_nuevos_lista.append(n_nuevo)
                pozos_ws_lista.append(n_ws)
                
                # 6. Reactivaciones (ON en este mes, no ON en el anterior, sin nuevas corridas / WS en este mes)
                prev_month = 12 if m == 1 else m - 1
                prev_year = anio_campana - 1 if m == 1 else anio_campana
                
                wells_on_m = set(df_forma9_f[
                    (df_forma9_f['FECHA_FORMA9_DATE'].dt.month == m) &
                    (df_forma9_f['FECHA_FORMA9_DATE'].dt.year == anio_campana) &
                    (df_forma9_f['DIAS TRABAJADOS'] > 0)
                ]['POZO'].astype(str).str.strip().unique())
                
                wells_on_prev = set(df_forma9_f[
                    (df_forma9_f['FECHA_FORMA9_DATE'].dt.month == prev_month) &
                    (df_forma9_f['FECHA_FORMA9_DATE'].dt.year == prev_year) &
                    (df_forma9_f['DIAS TRABAJADOS'] > 0)
                ]['POZO'].astype(str).str.strip().unique())
                
                runs_m = df_camp[df_camp['FECHA_RUN'].dt.month == m]
                wells_new_m = set(runs_m[runs_m['RUN'] == 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
                wells_ws_m = set(runs_m[runs_m['RUN'] > 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
                
                wells_reactivated = wells_on_m - wells_on_prev - wells_new_m - wells_ws_m
                pozos_reactivados_lista.append(len(wells_reactivated))
            
            df_mensual['Pozos Operativos'] = pozos_operativos_lista
            df_mensual['Pozos ON'] = pozos_on_lista
            df_mensual['Pozos OFF'] = pozos_off_lista
            df_mensual[f'Pozos Operativos {selected_als}'] = pozos_operativos_als_lista
            
            df_mensual['Índice Falla ON'] = [
                f"{(t / o):.2%}" if o > 0 else "0.00%"
                for t, o in zip(df_mensual['Fallas Totales'], df_mensual['Pozos ON'])
            ]
            df_mensual[f'Índice Falla {selected_als} ON'] = [
                f"{(a / o):.2%}" if o > 0 else "0.00%"
                for a, o in zip(df_mensual[f'Fallas {selected_als}'], df_mensual['Pozos ON'])
            ]
            
            df_mensual['Pozos Nuevos'] = pozos_nuevos_lista
            df_mensual['Pozos WS'] = pozos_ws_lista
            df_mensual['Pozos Reactivados'] = pozos_reactivados_lista
            
            render_hud_table(df_mensual, table_id="tabla_resumen_mensual_campana")

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

    # --- TABLA DE BALANCE DE INVENTARIO MENSUAL (ÚLTIMOS 12 MESES) ---
    with st.expander("📅 BALANCE DE INVENTARIO MENSUAL (ÚLTIMOS 12 MESES)", expanded=False):
        import calendar
        start_date_12 = (fecha_eval_dt - pd.DateOffset(months=11)).replace(day=1).normalize()
        
        meses_12 = []
        curr = start_date_12
        while curr <= fecha_eval_dt.normalize():
            meses_12.append(curr)
            curr = (curr + pd.offsets.MonthBegin(1)).normalize()
        
        df_balance = pd.DataFrame(index=range(len(meses_12)))
        df_balance['Mes'] = [m.strftime('%Y-%m') for m in meses_12]
        
        base_lista = []
        nuevos_lista = []
        reactivados_lista = []
        wows_lista = []
        fallados_lista = []
        apagados_lista = []
        pozos_final_lista = []
        
        df_bd_f = df_bd_filtered.copy()
        df_bd_f['FECHA_RUN_DATE'] = df_bd_f['FECHA_RUN'].dt.normalize()
        df_bd_f['FECHA_FALLA_DATE'] = df_bd_f['FECHA_FALLA'].dt.normalize()
        df_bd_f['FECHA_PULL_DATE'] = df_bd_f['FECHA_PULL'].dt.normalize()
        
        df_forma9_f = df_forma9_filtered.copy()
        df_forma9_f['FECHA_FORMA9_DATE'] = df_forma9_f['FECHA_FORMA9'].dt.normalize()
        
        for m_date in meses_12:
            start_date_m = m_date
            last_day = calendar.monthrange(m_date.year, m_date.month)[1]
            end_date_m = pd.Timestamp(year=m_date.year, month=m_date.month, day=last_day).normalize()
            
            # 1. Base (Operativos al inicio del mes)
            base_date = start_date_m - pd.Timedelta(days=1)
            base_op = df_bd_f[
                (df_bd_f['FECHA_RUN_DATE'] <= base_date) &
                (df_bd_f['FECHA_FALLA_DATE'].isna() | (df_bd_f['FECHA_FALLA_DATE'] > base_date)) &
                (df_bd_f['FECHA_PULL_DATE'].isna() | (df_bd_f['FECHA_PULL_DATE'] > base_date))
            ]['POZO'].nunique()
            base_lista.append(base_op)
            
            runs_m = df_bd_filtered[
                (df_bd_filtered['FECHA_RUN'].dt.normalize() >= start_date_m) &
                (df_bd_filtered['FECHA_RUN'].dt.normalize() <= end_date_m)
            ]
            
            # 2. Nuevos (RUN == 1)
            n_nuevos = runs_m[runs_m['RUN'] == 1]['POZO'].nunique() if 'RUN' in runs_m.columns else 0
            nuevos_lista.append(n_nuevos)
            
            # 3. WO/WS (RUN > 1)
            n_wows = runs_m[runs_m['RUN'] > 1]['POZO'].nunique() if 'RUN' in runs_m.columns else 0
            wows_lista.append(n_wows)
            
            # 4. Fallados
            n_fallados = df_bd_filtered[
                (df_bd_filtered['FECHA_FALLA'].dt.normalize() >= start_date_m) &
                (df_bd_filtered['FECHA_FALLA'].dt.normalize() <= end_date_m)
            ].shape[0]
            fallados_lista.append(n_fallados)
            
            # 5. Reactivados & Apagados
            wells_on_m = set(df_forma9_f[
                (df_forma9_f['FECHA_FORMA9_DATE'] >= start_date_m) &
                (df_forma9_f['FECHA_FORMA9_DATE'] <= end_date_m) &
                (df_forma9_f['DIAS TRABAJADOS'] > 0)
            ]['POZO'].astype(str).str.strip().unique())
            
            prev_start = start_date_m - pd.DateOffset(months=1)
            prev_end = start_date_m - pd.Timedelta(days=1)
            wells_on_prev = set(df_forma9_f[
                (df_forma9_f['FECHA_FORMA9_DATE'] >= prev_start) &
                (df_forma9_f['FECHA_FORMA9_DATE'] <= prev_end) &
                (df_forma9_f['DIAS TRABAJADOS'] > 0)
            ]['POZO'].astype(str).str.strip().unique())
            
            wells_new_m = set(runs_m[runs_m['RUN'] == 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
            wells_ws_m = set(runs_m[runs_m['RUN'] > 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
            
            reactivados_set = wells_on_m - wells_on_prev - wells_new_m - wells_ws_m
            reactivados_lista.append(len(reactivados_set))
            
            apagados_set = wells_on_prev - wells_on_m
            apagados_lista.append(len(apagados_set))
            
            # 6. Pozos Final
            final_op = df_bd_f[
                (df_bd_f['FECHA_RUN_DATE'] <= end_date_m) &
                (df_bd_f['FECHA_FALLA_DATE'].isna() | (df_bd_f['FECHA_FALLA_DATE'] > end_date_m)) &
                (df_bd_f['FECHA_PULL_DATE'].isna() | (df_bd_f['FECHA_PULL_DATE'] > end_date_m))
            ]['POZO'].nunique()
            pozos_final_lista.append(final_op)
        
        df_balance['Base'] = base_lista
        df_balance['Nuevos'] = nuevos_lista
        df_balance['Reactivados'] = reactivados_lista
        df_balance['WO/WS'] = wows_lista
        df_balance['Fallados'] = fallados_lista
        df_balance['Apagados'] = apagados_lista
        df_balance['Pozos Final'] = pozos_final_lista
        
        render_hud_table(df_balance, table_id="tabla_balance_mensual_historico")

    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

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