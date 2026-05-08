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
    # FILA 4 — TREEMAP 100%
    # =========================================================================
    _section_title("▸ Mapa de Activos", _CYAN)

    if df_bd_filtered.empty:
        st.info("Sin datos para el treemap.")
    else:
        hier_cols = [c for c in ('ACTIVO', 'BLOQUE', 'CAMPO', 'POZO') if c in df_bd_filtered.columns]
        color_col = 'RUN LIFE' if 'RUN LIFE' in df_bd_filtered.columns else None

        if len(hier_cols) >= 2:
            try:
                fig_tree = px.treemap(
                    df_bd_filtered,
                    path=hier_cols,
                    color=color_col if color_col else hier_cols[0],
                    color_continuous_scale=[
                        [0.0, '#060a1e'], [0.2, '#003566'], [0.5, '#0077b6'],
                        [0.8, '#00f2ff'], [1.0, '#00ffa3']
                    ] if color_col else None,
                    hover_data={color_col: ':.0f'} if color_col else None,
                )
                fig_tree.update_layout(
                    margin=dict(t=30, l=10, r=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=600,
                    coloraxis_showscale=True,
                    coloraxis_colorbar=dict(
                        title="DÍAS DE VIDA",
                        title_font_size=11,
                        title_font_color="#00f2ff",
                        thicknessmode="pixels", thickness=15,
                        lenmode="fraction", len=0.8,
                        yanchor="middle", y=0.5,
                        tickfont=dict(size=10, color="#cfd8dc"),
                        outlinewidth=0
                    ),
                    font_family="Arial",
                    font_color="#ffffff",
                )
                fig_tree.update_traces(
                    textinfo="label+value",
                    texttemplate="<span style='color:#00f2ff'><b>%{label}</b></span><br>%{value}",
                    textfont=dict(size=14, color="white"),
                    marker=dict(
                        line=dict(width=1.5, color='rgba(0, 242, 255, 0.4)'),
                    ),
                    hovertemplate='<b>%{label}</b><br>Métrica: %{value}<br>Días: %{color:.0f}d'
                )
                # Envolver Plotly en un contenedor HUD Premium
                st.markdown("""<div style="background:#060a1e; border:1px solid rgba(0,242,255,0.15); border-radius:15px; padding:12px; margin-bottom:10px;">""", unsafe_allow_html=True)
                st.plotly_chart(fig_tree, use_container_width=True, config={'displayModeBar': True, 'scrollZoom': True})
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Treemap no disponible: {e}")
        else:
            st.info("Se necesitan al menos 2 columnas jerárquicas (ACTIVO, BLOQUE, CAMPO).")

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