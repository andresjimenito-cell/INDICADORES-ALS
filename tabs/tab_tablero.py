"""
tabs/tab_tablero.py
===================
Tablero Ejecutivo — Dashboard estilo analítico.

Secciones:
  1. Panel Izquierdo  — KPIs operativos (ALS en fondo, fallados, operativos, activos/inactivos, disponibilidad, uso operativo)
  2. Panel Central    — Gauge IF (Índice de Falla) + gráfico tendencia anual
  3. Panel Derecho    — Gauge MTBF + Gauge RunLife + distribución por rangos
"""

import json
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

import mtbf as mtbf_mod


# ─────────────────────────────────────────────────────────────────────────────
# PALETA & CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────

_G   = "#137659"   # Verde Parex
_G2  = "#2e7d32"   # Verde oscuro
_R   = "#c62828"   # Rojo falla
_Y   = "#c09c2e"   # Dorado/amarillo
_BG  = "#ffffff"
_T   = "#1f221e"   # Texto oscuro
_T2  = "#455a72"   # Texto suave
_BD  = "rgba(19,118,89,0.15)"

# Metas por defecto (ajustables)
META_IF   = 7.5
META_MTBF = 2190
META_RL   = 1500


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _css() -> None:
    st.markdown("""
<style>
/* ── Tablero: tarjetas ── */
.tb-card {
    background: #ffffff;
    border: 1px solid rgba(19,118,89,0.18);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    box-shadow: 0 1px 6px rgba(19,118,89,0.06);
}
.tb-kpi-label {
    font-family: Arial, sans-serif;
    font-size: 0.52rem;
    font-weight: 700;
    color: #455a72;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.tb-kpi-value {
    font-family: Arial, sans-serif;
    font-size: 2rem;
    font-weight: 900;
    line-height: 1.1;
}
.tb-kpi-sub {
    font-family: Arial, sans-serif;
    font-size: 0.52rem;
    color: #455a72;
    letter-spacing: 1px;
    margin-top: 2px;
}
.tb-mini-row {
    display: flex;
    gap: 8px;
}
.tb-mini-card {
    flex: 1;
    background: #f8faf9;
    border: 1px solid rgba(19,118,89,0.12);
    border-radius: 8px;
    padding: 7px 10px;
    text-align: center;
}
.tb-mini-label {
    font-family: Arial, sans-serif;
    font-size: 0.45rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #455a72;
}
.tb-mini-value {
    font-family: Arial, sans-serif;
    font-size: 1.2rem;
    font-weight: 900;
}
.tb-bar-wrap {
    height: 6px;
    background: rgba(19,118,89,0.1);
    border-radius: 3px;
    margin-top: 4px;
    overflow: hidden;
}
.tb-bar-fill {
    height: 100%;
    border-radius: 3px;
}
.tb-section-title {
    font-family: Arial, sans-serif;
    font-size: 0.55rem;
    font-weight: 700;
    color: #137659;
    letter-spacing: 2px;
    text-transform: uppercase;
    border-left: 2px solid #137659;
    padding: 2px 0 2px 8px;
    margin: 12px 0 8px 0;
}
.tb-als-breakdown {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 6px;
}
.tb-als-pill {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: rgba(19,118,89,0.06);
    border: 1px solid rgba(19,118,89,0.15);
    border-radius: 6px;
    padding: 4px 8px;
    min-width: 48px;
}
.tb-als-pill-name {
    font-family: Arial, sans-serif;
    font-size: 0.42rem;
    font-weight: 700;
    color: #137659;
    letter-spacing: 1px;
}
.tb-als-pill-val {
    font-family: Arial, sans-serif;
    font-size: 0.9rem;
    font-weight: 900;
    color: #1f221e;
}
.tb-als-pill-op {
    font-family: Arial, sans-serif;
    font-size: 0.38rem;
    color: #455a72;
}
</style>
""", unsafe_allow_html=True)


def _echarts(opts: dict, height: int, chart_id: str) -> str:
    return f"""
<div id="{chart_id}" style="width:100%;height:{height}px;background:#ffffff;border-radius:10px;border:1px solid {_BD};overflow:hidden;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
(function(){{
    var el = document.getElementById('{chart_id}');
    var chart = echarts.init(el, null, {{renderer:'canvas'}});
    chart.setOption({json.dumps(opts)});
    new ResizeObserver(function(){{ chart.resize(); }}).observe(el);
}})();
</script>"""


def _gauge(value, meta, label, color_bueno, color_malo, max_val, chart_id) -> str:
    """Gauge tipo velocímetro."""
    color = color_bueno if value >= meta else color_malo
    pct   = min(value / max_val, 1.0)
    opts  = {
        "backgroundColor": "#ffffff",
        "series": [{
            "type": "gauge",
            "startAngle": 210,
            "endAngle": -30,
            "min": 0,
            "max": max_val,
            "splitNumber": 5,
            "radius": "88%",
            "center": ["50%", "58%"],
            "axisLine": {
                "lineStyle": {
                    "width": 14,
                    "color": [
                        [meta / max_val, _R],
                        [1.0,            _G],
                    ]
                }
            },
            "pointer": {
                "itemStyle": {"color": "#1f221e"},
                "length": "68%",
                "width": 4,
            },
            "axisTick":   {"show": False},
            "splitLine":  {"show": False},
            "axisLabel":  {"show": False},
            "detail": {
                "valueAnimation": True,
                "formatter": f"{{value}}",
                "color":     color,
                "fontSize":  28,
                "fontWeight":"900",
                "fontFamily":"Arial, sans-serif",
                "offsetCenter": [0, "15%"],
            },
            "title": {
                "show": True,
                "offsetCenter": [0, "40%"],
                "color": _T2,
                "fontSize": 9,
                "fontFamily": "Arial, sans-serif",
                "fontWeight": "700",
                "formatter": f"Meta {label}: {meta}",
            },
            "data": [{"value": round(value, 1), "name": f"Meta {label}: {meta}"}],
        }]
    }
    return _echarts(opts, 200, chart_id)


# ─────────────────────────────────────────────────────────────────────────────
# RENDER PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def render_tab_tablero(
    df_bd_filtered,
    df_forma9_filtered,
    reporte_runes_filtered,
    fecha_evaluacion,
    selected_activo,
):
    """Dashboard Ejecutivo — Tablero Analítico."""

    _css()

    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    fecha_eval_date = fecha_eval_dt.normalize()
    anio = fecha_eval_dt.year

    # ── Pre-procesar fechas ──────────────────────────────────────────────────
    for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
        if col in df_bd_filtered.columns:
            df_bd_filtered[col] = pd.to_datetime(df_bd_filtered[col], errors='coerce')

    df_bd_filtered['_RUN']  = df_bd_filtered['FECHA_RUN'].dt.normalize()
    df_bd_filtered['_FALL'] = df_bd_filtered['FECHA_FALLA'].dt.normalize()
    df_bd_filtered['_PULL'] = df_bd_filtered['FECHA_PULL'].dt.normalize()

    # ── KPIs base ───────────────────────────────────────────────────────────
    df_run = df_bd_filtered[
        (df_bd_filtered['_RUN'] <= fecha_eval_date) &
        (df_bd_filtered['_PULL'].isna() | (df_bd_filtered['_PULL'] > fecha_eval_date))
    ]
    als_fondo    = len(df_run)
    als_fallados = df_run[df_run['_FALL'].notna() & (df_run['_FALL'] <= fecha_eval_date)].shape[0]
    als_oper     = als_fondo - als_fallados

    # Activos (ON) / Inactivos (OFF) — basado en Forma 9 del mes actual
    mes_eval = fecha_eval_dt.month
    anio_eval = fecha_eval_dt.year
    if not df_forma9_filtered.empty and 'FECHA_FORMA9' in df_forma9_filtered.columns:
        df_f9 = df_forma9_filtered.copy()
        df_f9['_F9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
        pozos_on_set = set(df_f9[
            (df_f9['_F9'].dt.month == mes_eval) &
            (df_f9['_F9'].dt.year == anio_eval) &
            (df_f9.get('DIAS TRABAJADOS', pd.Series([1]*len(df_f9))).fillna(0) > 0)
        ]['POZO'].astype(str).str.strip().unique())
        pozos_oper_set = set(df_run['POZO'].astype(str).str.strip().unique()) if 'POZO' in df_run.columns else set()
        activos   = len(pozos_oper_set & pozos_on_set)
        inactivos = len(pozos_oper_set - pozos_on_set)
    else:
        activos   = als_oper
        inactivos = 0

    total_pozos = activos + inactivos if (activos + inactivos) > 0 else 1
    disp_oper   = activos / total_pozos * 100
    uso_oper    = als_oper / max(als_fondo, 1) * 100

    # ── Breakdown por tipo ALS ───────────────────────────────────────────────
    als_tipos = ['ESP', 'PCP', 'EPCP', 'BM', 'BH']
    als_breakdown = {}
    if 'ALS' in df_run.columns:
        for t in als_tipos:
            sub = df_run[df_run['ALS'].astype(str).str.strip().str.upper() == t]
            tot = len(sub)
            fall = sub[sub['_FALL'].notna() & (sub['_FALL'] <= fecha_eval_date)].shape[0]
            als_breakdown[t] = {'total': tot, 'op': tot - fall}

    # ── IF anual ─────────────────────────────────────────────────────────────
    _MES_ABR = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    if_cats, if_vals, pozos_on_vals = [], [], []

    for m in range(1, mes_eval + 1):
        import calendar
        last_day  = calendar.monthrange(anio_eval, m)[1]
        end_m     = pd.Timestamp(year=anio_eval, month=m, day=last_day).normalize()

        fallas_m = df_bd_filtered[
            (df_bd_filtered['_FALL'].dt.month == m) &
            (df_bd_filtered['_FALL'].dt.year == anio_eval)
        ].shape[0]

        on_m = 0
        if not df_forma9_filtered.empty and 'FECHA_FORMA9' in df_forma9_filtered.columns:
            df_f9c = df_forma9_filtered.copy()
            df_f9c['_F9'] = pd.to_datetime(df_f9c['FECHA_FORMA9'], errors='coerce').dt.normalize()
            on_m = df_f9c[
                (df_f9c['_F9'].dt.month == m) &
                (df_f9c['_F9'].dt.year == anio_eval) &
                (df_f9c.get('DIAS TRABAJADOS', pd.Series([1]*len(df_f9c))).fillna(0) > 0)
            ]['POZO'].nunique()

        if_m = round(fallas_m / max(on_m, 1) * 100, 2)
        if_cats.append(_MES_ABR[m - 1])
        if_vals.append(if_m)
        pozos_on_vals.append(on_m)

    if_actual = if_vals[-1] if if_vals else 0

    # ── MTBF ────────────────────────────────────────────────────────────────
    try:
        mtbf_val, _ = mtbf_mod.calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        mtbf_val = round(float(mtbf_val), 0) if mtbf_val else 0
    except Exception:
        mtbf_val = 0

    # ── RunLife actual (promedio) ────────────────────────────────────────────
    if 'RUN LIFE' in df_bd_filtered.columns:
        rl_val = round(df_run['RUN LIFE'].dropna().mean(), 0) if 'RUN LIFE' in df_run.columns else 0
    elif 'RUN_LIFE' in df_bd_filtered.columns:
        rl_val = round(df_run['RUN_LIFE'].dropna().mean(), 0) if 'RUN_LIFE' in df_run.columns else 0
    else:
        rl_val = 0
    if pd.isna(rl_val):
        rl_val = 0

    # ── Distribución RunLife ─────────────────────────────────────────────────
    rl_col = 'RUN LIFE' if 'RUN LIFE' in df_run.columns else ('RUN_LIFE' if 'RUN_LIFE' in df_run.columns else None)
    rl_bins  = ['< 2 años', '2 @ 4 años', '4 @ 6 años', '> 6 años']
    rl_pozos = [0, 0, 0, 0]

    if rl_col:
        rl_data = df_run[rl_col].dropna()
        rl_pozos[0] = int((rl_data < 730).sum())
        rl_pozos[1] = int(((rl_data >= 730) & (rl_data < 1460)).sum())
        rl_pozos[2] = int(((rl_data >= 1460) & (rl_data < 2190)).sum())
        rl_pozos[3] = int((rl_data >= 2190).sum())

    # ═════════════════════════════════════════════════════════════════════════
    # LAYOUT: 3 paneles (izq 28% | centro 38% | der 34%)
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    col_izq, col_mid, col_der = st.columns([1.1, 1.4, 1.3])

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL IZQUIERDO — KPIs OPERATIVOS
    # ─────────────────────────────────────────────────────────────────────────
    with col_izq:

        # ── ALS EN FONDO ────────────────────────────────────────────────────
        st.markdown(f"""
<div class="tb-card">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="font-size:2rem;opacity:0.7;">🛢️</div>
    <div style="flex:1;">
      <div style="display:flex;justify-content:space-between;align-items:flex-end;">
        <div>
          <div class="tb-kpi-label">ALS EN FONDO</div>
          <div class="tb-kpi-value" style="color:{_G};">{als_fondo:,}</div>
        </div>
      </div>
      <div class="tb-als-breakdown">
        {''.join([
            f'<div class="tb-als-pill"><div class="tb-als-pill-name">{t}</div><div class="tb-als-pill-val">{als_breakdown.get(t,{}).get("total",0)}</div><div class="tb-als-pill-op">{als_breakdown.get(t,{}).get("op",0)} op</div></div>'
            for t in als_tipos
        ])}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── ALS FALLADOS + OPERATIVOS ────────────────────────────────────────
        st.markdown(f"""
<div class="tb-mini-row">
  <div class="tb-mini-card" style="border-left:3px solid {_R};">
    <div class="tb-mini-label" style="color:{_R};">⚠ ALS FALLADOS</div>
    <div class="tb-mini-value" style="color:{_R};">{als_fallados:,}</div>
  </div>
  <div class="tb-mini-card" style="border-left:3px solid {_G};">
    <div class="tb-mini-label" style="color:{_G};">✔ ALS OPERATIVOS</div>
    <div class="tb-mini-value" style="color:{_G};">{als_oper:,}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        # ── ACTIVOS / INACTIVOS ──────────────────────────────────────────────
        st.markdown(f"""
<div class="tb-mini-row">
  <div class="tb-mini-card" style="border-left:3px solid {_G};">
    <div style="display:flex;align-items:center;gap:4px;justify-content:center;">
      <span style="font-size:1rem;">▶</span>
      <div>
        <div class="tb-mini-label" style="color:{_G};">ACTIVOS</div>
        <div class="tb-mini-value" style="color:{_G};">{activos:,}</div>
      </div>
    </div>
  </div>
  <div class="tb-mini-card" style="border-left:3px solid {_Y};">
    <div style="display:flex;align-items:center;gap:4px;justify-content:center;">
      <span style="font-size:1rem;">⏸</span>
      <div>
        <div class="tb-mini-label" style="color:{_Y};">INACTIVOS</div>
        <div class="tb-mini-value" style="color:{_Y};">{inactivos:,}</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

        # ── DISPONIBILIDAD OPERACIONAL ───────────────────────────────────────
        disp_color = _G if disp_oper >= 75 else (_Y if disp_oper >= 50 else _R)
        st.markdown(f"""
<div class="tb-card">
  <div class="tb-kpi-label">DISPONIBILIDAD OPERACIONAL</div>
  <div style="display:flex;align-items:baseline;gap:6px;">
    <div class="tb-kpi-value" style="font-size:1.5rem;color:{disp_color};">{disp_oper:.0f}%</div>
  </div>
  <div class="tb-bar-wrap">
    <div class="tb-bar-fill" style="width:{min(disp_oper,100):.0f}%;background:{disp_color};"></div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── USO OPERATIVO ────────────────────────────────────────────────────
        uso_color = _G if uso_oper >= 60 else (_Y if uso_oper >= 40 else _R)
        st.markdown(f"""
<div class="tb-card">
  <div class="tb-kpi-label">USO OPERATIVO</div>
  <div style="display:flex;align-items:baseline;gap:6px;">
    <div class="tb-kpi-value" style="font-size:1.5rem;color:{uso_color};">{uso_oper:.0f}%</div>
  </div>
  <div class="tb-bar-wrap">
    <div class="tb-bar-fill" style="width:{min(uso_oper,100):.0f}%;background:{uso_color};"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL CENTRAL — GAUGE IF + TENDENCIA ANUAL
    # ─────────────────────────────────────────────────────────────────────────
    with col_mid:

        # Gauge IF
        gauge_if = _gauge(
            value=if_actual,
            meta=META_IF,
            label="IF",
            color_bueno=_G,
            color_malo=_R,
            max_val=max(max(if_vals) * 1.3, META_IF * 2, 20) if if_vals else 30,
            chart_id="gauge_if"
        )
        components.html(gauge_if, height=215)

        # Tendencia IF anual
        max_if = max(if_vals) if if_vals else 10
        opts_if = {
            "backgroundColor": "#ffffff",
            "tooltip": {
                "trigger": "axis",
                "backgroundColor": "rgba(255,255,255,0.95)",
                "borderColor": _BD,
                "textStyle": {"color": _T, "fontSize": 10},
            },
            "legend": {
                "data": ["Pozos ON", "Pozos Off", "IF ALS"],
                "bottom": 0, "itemHeight": 6,
                "textStyle": {"color": _T2, "fontSize": 8},
            },
            "grid": {"top": "8%", "left": "8%", "right": "4%", "bottom": "18%", "containLabel": True},
            "xAxis": {
                "type": "category", "data": if_cats,
                "axisLabel": {"color": _T2, "fontSize": 8},
                "axisLine": {"lineStyle": {"color": _BD}},
                "axisTick": {"show": False},
            },
            "yAxis": [
                {
                    "type": "value", "name": "Pozos",
                    "nameTextStyle": {"color": _T2, "fontSize": 7},
                    "axisLabel": {"color": _T2, "fontSize": 7},
                    "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)", "type": "dashed"}},
                },
                {
                    "type": "value", "name": "IF %",
                    "nameTextStyle": {"color": _R, "fontSize": 7},
                    "axisLabel": {"color": _R, "fontSize": 7},
                    "splitLine": {"show": False},
                }
            ],
            "series": [
                {
                    "name": "Pozos ON", "type": "bar", "stack": "pozos",
                    "data": pozos_on_vals, "barMaxWidth": 20,
                    "itemStyle": {"color": "rgba(19,118,89,0.65)", "borderRadius": [2,2,0,0]},
                },
                {
                    "name": "IF ALS", "type": "line", "yAxisIndex": 1,
                    "data": if_vals, "smooth": True,
                    "symbol": "circle", "symbolSize": 5,
                    "lineStyle": {"color": _R, "width": 2},
                    "itemStyle": {"color": _R, "borderColor": "#fff", "borderWidth": 2},
                    "markLine": {
                        "silent": True,
                        "lineStyle": {"color": _G, "type": "dashed", "width": 1.5},
                        "data": [{"yAxis": META_IF, "name": f"Meta {META_IF}"}],
                        "label": {"formatter": f"Meta {META_IF}", "color": _G, "fontSize": 8},
                    }
                }
            ]
        }
        st.markdown(f"<div class='tb-section-title'>IF EN EL ÚLTIMO AÑO</div>", unsafe_allow_html=True)
        components.html(_echarts(opts_if, 220, "chart_if_anual"), height=232)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL DERECHO — MTBF + RUNLIFE GAUGES + DISTRIBUCIÓN
    # ─────────────────────────────────────────────────────────────────────────
    with col_der:

        # Dos gauges lado a lado
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            mtbf_max = max(mtbf_val * 1.4, META_MTBF * 1.5, 3000)
            components.html(
                _gauge(mtbf_val, META_MTBF, "MTBF", _G, _R, mtbf_max, "gauge_mtbf"),
                height=215
            )
        with g_col2:
            rl_max = max(rl_val * 1.4, META_RL * 1.5, 2500)
            components.html(
                _gauge(rl_val, META_RL, "RL", _G, _R, rl_max, "gauge_rl"),
                height=215
            )

        # Distribución RunLife por rangos
        rl_colors = [_R, _Y, _G2, _G]
        opts_rl = {
            "backgroundColor": "#ffffff",
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.95)",
                "borderColor": _BD,
                "textStyle": {"color": _T, "fontSize": 10},
            },
            "legend": {
                "data": ["# Pozos"],
                "bottom": 0, "itemHeight": 6,
                "textStyle": {"color": _T2, "fontSize": 8},
            },
            "grid": {"top": "8%", "left": "4%", "right": "4%", "bottom": "18%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": rl_bins,
                "axisLabel": {"color": _T2, "fontSize": 7},
                "axisLine": {"lineStyle": {"color": _BD}},
                "axisTick": {"show": False},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": _T2, "fontSize": 7},
                "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)", "type": "dashed"}},
            },
            "series": [{
                "name": "# Pozos",
                "type": "bar",
                "data": [
                    {"value": v, "itemStyle": {"color": c}}
                    for v, c in zip(rl_pozos, rl_colors)
                ],
                "barMaxWidth": 40,
                "label": {
                    "show": True, "position": "top",
                    "color": _T, "fontSize": 9, "fontWeight": "700",
                    "fontFamily": "Arial, sans-serif"
                },
                "itemStyle": {"borderRadius": [4, 4, 0, 0]},
                "markLine": {
                    "silent": True,
                    "lineStyle": {"color": _Y, "type": "dashed", "width": 1.5},
                    "data": [{"type": "average", "name": "Promedio"}],
                    "label": {"formatter": "Prom", "color": _Y, "fontSize": 8},
                }
            }]
        }
        st.markdown(f"<div class='tb-section-title'>DISTRIBUCIÓN RUNLIFE</div>", unsafe_allow_html=True)
        components.html(_echarts(opts_rl, 220, "chart_rl_dist"), height=232)
