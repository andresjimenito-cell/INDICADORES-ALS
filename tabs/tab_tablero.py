"""
tabs/tab_tablero.py  —  v2 Premium
===================================
Tablero Ejecutivo estilo analítico industrial.
Tres paneles: KPIs operativos | Gauge IF + tendencia | Gauge MTBF/RL + distribución RunLife
Todos los valores son calculados en tiempo real desde los datos filtrados.
"""

import json, calendar
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

import mtbf as mtbf_mod

# ── Paleta corporativa Parex ─────────────────────────────────────────────────
_G   = "#137659"        # Verde principal
_G2  = "#0a4d34"        # Verde oscuro
_G3  = "#e8f5ee"        # Verde muy claro (fondo)
_R   = "#c62828"        # Rojo falla
_R2  = "#ffebee"        # Rojo claro fondo
_Y   = "#c09c2e"        # Dorado acento
_Y2  = "#fdf8ec"        # Dorado fondo
_T   = "#1f221e"        # Texto oscuro
_T2  = "#455a72"        # Texto suave
_W   = "#ffffff"
_BG  = "#f5f7f6"

META_IF   = 7.5
META_MTBF = 2190
META_RL   = 1500
ALS_TIPOS = ['ESP', 'PCP', 'EPCP', 'BM', 'BH']


# ─────────────────────────────────────────────────────────────────────────────
def _css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

/* ── Contenedor panel ── */
.tbl-panel {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid rgba(19,118,89,0.12);
    box-shadow: 0 4px 20px rgba(19,118,89,0.07), 0 1px 4px rgba(0,0,0,0.04);
    padding: 16px 18px;
    height: 100%;
}

/* ── Sección título ── */
.tbl-sec-title {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.52rem;
    font-weight: 800;
    color: #455a72;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    border-left: 3px solid #137659;
    padding-left: 8px;
    margin: 14px 0 8px 0;
}

/* ── KPI grande ── */
.tbl-kpi-big {
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(135deg, rgba(19,118,89,0.04) 0%, rgba(192,156,46,0.04) 100%);
    border: 1px solid rgba(19,118,89,0.14);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
}
.tbl-kpi-icon {
    font-size: 2.2rem;
    line-height: 1;
    flex-shrink: 0;
}
.tbl-kpi-content { flex: 1; min-width: 0; }
.tbl-kpi-label {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.5rem;
    font-weight: 700;
    color: #455a72;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.tbl-kpi-value {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 2.1rem;
    font-weight: 900;
    line-height: 1;
    color: #137659;
}

/* ── ALS breakdown pills ── */
.tbl-pills {
    display: flex;
    gap: 5px;
    margin-top: 8px;
    flex-wrap: wrap;
}
.tbl-pill {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: rgba(19,118,89,0.07);
    border: 1px solid rgba(19,118,89,0.18);
    border-radius: 8px;
    padding: 4px 8px;
    min-width: 44px;
    flex: 1;
}
.tbl-pill-name {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.42rem;
    font-weight: 800;
    color: #137659;
    letter-spacing: 1px;
}
.tbl-pill-val {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 1rem;
    font-weight: 900;
    color: #1f221e;
    line-height: 1.2;
}
.tbl-pill-sub {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.38rem;
    color: #455a72;
    letter-spacing: 0.5px;
}

/* ── Dos columnas stat ── */
.tbl-stat-row {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
}
.tbl-stat-card {
    flex: 1;
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
    border: 1px solid;
}
.tbl-stat-icon {
    font-size: 1.4rem;
    line-height: 1;
    margin-bottom: 3px;
}
.tbl-stat-label {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.44rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.tbl-stat-value {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 1.5rem;
    font-weight: 900;
    line-height: 1;
}

/* ── Barra de progreso ── */
.tbl-prog-wrap {
    background: rgba(19,118,89,0.07);
    border-radius: 4px;
    height: 7px;
    overflow: hidden;
    margin-top: 5px;
}
.tbl-prog-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}
.tbl-prog-card {
    background: #f9fbfa;
    border: 1px solid rgba(19,118,89,0.12);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.tbl-prog-label {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.5rem;
    font-weight: 700;
    color: #455a72;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.tbl-prog-value {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 1.35rem;
    font-weight: 900;
    line-height: 1.2;
    float: right;
    margin-top: -1px;
}

/* ── Gauge card ── */
.tbl-gauge-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid rgba(19,118,89,0.12);
    box-shadow: 0 2px 12px rgba(19,118,89,0.06);
    padding: 4px 4px 0 4px;
    text-align: center;
    margin-bottom: 8px;
}
.tbl-gauge-title {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 0.52rem;
    font-weight: 800;
    color: #455a72;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-top: 8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
def _chart_html(opts: dict, height: int, cid: str) -> str:
    return f"""
<div id="{cid}" style="width:100%;height:{height}px;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
(function(){{
  var el=document.getElementById('{cid}');
  var c=echarts.init(el,null,{{renderer:'canvas'}});
  c.setOption({json.dumps(opts, ensure_ascii=False)});
  new ResizeObserver(function(){{c.resize();}}).observe(el);
}})();
</script>"""


def _gauge_html(value, meta, label, higher_is_better: bool, max_val, cid) -> str:
    """Gauge con aguja estilo velocímetro, colores según sentido del KPI."""
    meta_pct = meta / max_val
    if higher_is_better:
        arc_colors = [[meta_pct, _R], [1.0, _G]]
    else:
        arc_colors = [[meta_pct, _G], [1.0, _R]]

    val_color = _G if (value >= meta if higher_is_better else value <= meta) else _R
    val_rounded = int(round(value))

    opts = {
        "backgroundColor": _W,
        "series": [{
            "type": "gauge",
            "startAngle": 205,
            "endAngle": -25,
            "min": 0,
            "max": max_val,
            "center": ["50%", "62%"],
            "radius": "88%",
            "splitNumber": 4,
            "axisLine": {
                "lineStyle": {
                    "width": 18,
                    "color": arc_colors,
                    "shadowBlur": 8,
                    "shadowColor": "rgba(0,0,0,0.08)"
                }
            },
            "pointer": {
                "itemStyle": {"color": _T},
                "width": 5,
                "length": "72%",
                "offsetCenter": [0, 0],
            },
            "axisTick": {
                "distance": -22,
                "length": 7,
                "lineStyle": {"color": "#fff", "width": 2}
            },
            "splitLine": {
                "distance": -28,
                "length": 14,
                "lineStyle": {"color": "#fff", "width": 3}
            },
            "axisLabel": {
                "color": _T2,
                "distance": 30,
                "fontSize": 8,
                "fontFamily": "Inter, Arial, sans-serif",
                "fontWeight": "600",
            },
            "anchor": {
                "show": True,
                "showAbove": True,
                "size": 12,
                "itemStyle": {"borderWidth": 3, "borderColor": _T, "color": _W}
            },
            "detail": {
                "valueAnimation": True,
                "formatter": f"{val_rounded}",
                "color": val_color,
                "fontSize": 28,
                "fontWeight": "900",
                "fontFamily": "Inter, Arial, sans-serif",
                "offsetCenter": [0, "22%"],
                "borderRadius": 6,
            },
            "title": {
                "show": True,
                "offsetCenter": [0, "48%"],
                "color": _T2,
                "fontSize": 9,
                "fontWeight": "700",
                "fontFamily": "Inter, Arial, sans-serif",
            },
            "data": [{"value": round(value, 1), "name": f"Meta {label}: {meta}"}],
        }]
    }
    return _chart_html(opts, 200, cid)


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
    _css()

    fecha_eval_dt   = pd.to_datetime(fecha_evaluacion)
    fecha_eval_date = fecha_eval_dt.normalize()
    mes_eval        = fecha_eval_dt.month
    anio_eval       = fecha_eval_dt.year

    # ── Normalizar fechas ────────────────────────────────────────────────────
    for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
        if col in df_bd_filtered.columns:
            df_bd_filtered[col] = pd.to_datetime(df_bd_filtered[col], errors='coerce')

    df = df_bd_filtered.copy()
    df['_RUN']  = df['FECHA_RUN'].dt.normalize()
    df['_FALL'] = df['FECHA_FALLA'].dt.normalize() if 'FECHA_FALLA' in df.columns else pd.NaT
    df['_PULL'] = df['FECHA_PULL'].dt.normalize()  if 'FECHA_PULL'  in df.columns else pd.NaT

    # ── ALS en fondo ─────────────────────────────────────────────────────────
    mask_fondo = (df['_RUN'] <= fecha_eval_date) & (df['_PULL'].isna() | (df['_PULL'] > fecha_eval_date))
    df_fondo = df[mask_fondo]
    als_fondo = len(df_fondo)

    # ── Fallados y operativos ────────────────────────────────────────────────
    mask_falla    = df_fondo['_FALL'].notna() & (df_fondo['_FALL'] <= fecha_eval_date)
    als_fallados  = int(mask_falla.sum())
    als_operativos = als_fondo - als_fallados

    # ── Breakdown por tipo ALS ───────────────────────────────────────────────
    als_breakdown = {}
    if 'ALS' in df_fondo.columns:
        for t in ALS_TIPOS:
            sub  = df_fondo[df_fondo['ALS'].astype(str).str.strip().str.upper() == t]
            tot  = len(sub)
            fall = int((sub['_FALL'].notna() & (sub['_FALL'] <= fecha_eval_date)).sum())
            als_breakdown[t] = {'total': tot, 'op': tot - fall}

    # ── Activos / Inactivos (Forma 9) ────────────────────────────────────────
    activos = inactivos = 0
    if not df_forma9_filtered.empty and 'FECHA_FORMA9' in df_forma9_filtered.columns:
        df_f9     = df_forma9_filtered.copy()
        df_f9['_F9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
        dias_col  = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9.columns else None
        mask_on   = (df_f9['_F9'].dt.month == mes_eval) & (df_f9['_F9'].dt.year == anio_eval)
        if dias_col:
            mask_on = mask_on & (df_f9[dias_col].fillna(0) > 0)
        pozos_on  = set(df_f9[mask_on]['POZO'].astype(str).str.strip().unique())
        pozos_op  = set(df_fondo['POZO'].astype(str).str.strip().unique()) if 'POZO' in df_fondo.columns else set()
        activos   = len(pozos_op & pozos_on)
        inactivos = len(pozos_op - pozos_on)
    else:
        activos   = als_operativos
        inactivos = 0

    total_pozos  = max(activos + inactivos, 1)
    disp_oper    = activos   / total_pozos * 100
    uso_oper     = als_operativos / max(als_fondo, 1) * 100

    # ── Serie IF mensual — fórmula oficial: Fallas ALS (RLE<1500) / Pozos ON ─
    #    Usa calcular_indice_falla_anual del módulo indice_falla.py
    if_cats, if_vals, on_vals, off_vals = [], [], [], []
    if_actual = 0.0

    try:
        from indice_falla import calcular_indice_falla_anual
        _, df_mensual_if = calcular_indice_falla_anual(
            df_bd_filtered.copy(), df_forma9_filtered.copy(), fecha_evaluacion
        )

        # Filtrar solo los meses del año en evaluación
        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        df_yr = df_mensual_if[
            df_mensual_if['Mes'].str.startswith(str(anio_eval))
        ].copy()

        for _, row in df_yr.iterrows():
            m_str = row['Mes']           # 'YYYY-MM'
            m_idx = int(m_str[5:7]) - 1  # 0-based month index
            if_cats.append(_MESES[m_idx])
            # Índice mensual: Fallas_ALS_1500 / Pozos_ON  (sin rolling para el chart mensual)
            on_m   = int(row.get('Pozos ON', 0))
            fall_m = int(row.get('Fallas_ALS_1500', 0))
            if_m   = round(fall_m / max(on_m, 1), 4)   # valor entre 0 y 1 aprox
            if_vals.append(round(if_m, 4))
            on_vals.append(on_m)
            off_m  = max(int(row.get('Pozos Operativos', on_m)) - on_m, 0)
            off_vals.append(off_m)

        # Valor actual: usar el rolling 12-meses más reciente (Indice_Falla_Rolling_ALS_ON_1500)
        last_row = df_mensual_if[
            df_mensual_if['Indice_Falla_Rolling_ALS_ON_1500'].notna()
        ].tail(1)
        if not last_row.empty:
            if_actual = round(float(last_row['Indice_Falla_Rolling_ALS_ON_1500'].iloc[0]), 4)
        elif if_vals:
            if_actual = if_vals[-1]

    except Exception as _e_if:
        # Fallback: cálculo simplificado (fallas totales / pozos ON del mes)
        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        for m in range(1, mes_eval + 1):
            last_day = calendar.monthrange(anio_eval, m)[1]
            end_m_ts = pd.Timestamp(year=anio_eval, month=m, day=last_day).normalize()
            fallas_m = int(df[
                (df['_FALL'].dt.month == m) & (df['_FALL'].dt.year == anio_eval)
            ].shape[0])
            on_m = 0
            if not df_forma9_filtered.empty and 'FECHA_FORMA9' in df_forma9_filtered.columns:
                df_f9c = df_forma9_filtered.copy()
                df_f9c['_F9'] = pd.to_datetime(df_f9c['FECHA_FORMA9'], errors='coerce').dt.normalize()
                dias_c = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9c.columns else None
                mm = (df_f9c['_F9'].dt.month == m) & (df_f9c['_F9'].dt.year == anio_eval)
                if dias_c:
                    mm = mm & (df_f9c[dias_c].fillna(0) > 0)
                on_m = int(df_f9c[mm]['POZO'].nunique())
            op_m = int(df[
                (df['_RUN'] <= end_m_ts) &
                (df['_FALL'].isna() | (df['_FALL'] > end_m_ts)) &
                (df['_PULL'].isna() | (df['_PULL'] > end_m_ts))
            ]['POZO'].nunique()) if 'POZO' in df.columns else 0
            if_cats.append(_MESES[m - 1])
            if_m = round(fallas_m / max(on_m, 1) / 100, 4)
            if_vals.append(if_m)
            on_vals.append(on_m)
            off_vals.append(max(op_m - on_m, 0))
        if_actual = if_vals[-1] if if_vals else 0.0

    # Escalar a % si todos son ≤ 1 (la fórmula da ratio, mostramos ×100)
    if if_vals and max(if_vals) <= 1.5:
        if_vals   = [round(v * 100, 2) for v in if_vals]
        if_actual = round(if_actual * 100, 2)

    if_max = max(max(if_vals) * 1.4, META_IF * 2, 20) if if_vals else 30

    # ── MTBF ─────────────────────────────────────────────────────────────────
    try:
        mtbf_val, _ = mtbf_mod.calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        mtbf_val = float(mtbf_val) if mtbf_val and not np.isnan(float(mtbf_val)) else 0.0
    except Exception:
        mtbf_val = 0.0

    # ── RunLife promedio de pozos en fondo ───────────────────────────────────
    rl_col = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in df_fondo.columns), None)
    rl_val = float(df_fondo[rl_col].dropna().mean()) if rl_col else 0.0
    if np.isnan(rl_val):
        rl_val = 0.0

    # ── Distribución RunLife (en días) ───────────────────────────────────────
    rl_bins   = ['< 2 años', '2 – 4 años', '4 – 6 años', '> 6 años']
    rl_limites = [0, 730, 1460, 2190, 99999]
    rl_counts  = [0, 0, 0, 0]
    if rl_col:
        rl_data = df_fondo[rl_col].dropna()
        for i in range(4):
            rl_counts[i] = int(((rl_data >= rl_limites[i]) & (rl_data < rl_limites[i+1])).sum())

    mtbf_max = max(mtbf_val * 1.5, META_MTBF * 1.6, 4000)
    rl_max   = max(rl_val   * 1.5, META_RL   * 1.6, 3000)

    # ═════════════════════════════════════════════════════════════════════════
    # LAYOUT 3 PANELES
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1.05, 1.35, 1.25])

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL IZQUIERDO — KPIs OPERATIVOS
    # ─────────────────────────────────────────────────────────────────────────
    with col_l:

        # Construir pills de ALS
        pills_html = "".join([
            f"""<div class="tbl-pill">
                  <div class="tbl-pill-name">{t}</div>
                  <div class="tbl-pill-val">{als_breakdown.get(t,{}).get('total',0)}</div>
                  <div class="tbl-pill-sub">{als_breakdown.get(t,{}).get('op',0)} op</div>
                </div>"""
            for t in ALS_TIPOS
        ])

        st.markdown(f"""
<div class="tbl-panel">

  <!-- ALS EN FONDO -->
  <div class="tbl-kpi-big">
    <div class="tbl-kpi-icon">🛢️</div>
    <div class="tbl-kpi-content">
      <div class="tbl-kpi-label">ALS EN FONDO</div>
      <div class="tbl-kpi-value">{als_fondo:,}</div>
      <div class="tbl-pills">{pills_html}</div>
    </div>
  </div>

  <!-- FALLADOS / OPERATIVOS -->
  <div class="tbl-stat-row">
    <div class="tbl-stat-card" style="background:{_R2};border-color:rgba(198,40,40,0.25);">
      <div class="tbl-stat-icon">⚠️</div>
      <div class="tbl-stat-label" style="color:{_R};">ALS FALLADOS</div>
      <div class="tbl-stat-value" style="color:{_R};">{als_fallados:,}</div>
    </div>
    <div class="tbl-stat-card" style="background:{_G3};border-color:rgba(19,118,89,0.25);">
      <div class="tbl-stat-icon">✅</div>
      <div class="tbl-stat-label" style="color:{_G};">ALS OPERATIVOS</div>
      <div class="tbl-stat-value" style="color:{_G};">{als_operativos:,}</div>
    </div>
  </div>

  <!-- ACTIVOS / INACTIVOS -->
  <div class="tbl-stat-row">
    <div class="tbl-stat-card" style="background:{_G3};border-color:rgba(19,118,89,0.2);">
      <div class="tbl-stat-icon">▶️</div>
      <div class="tbl-stat-label" style="color:{_G};">ACTIVOS</div>
      <div class="tbl-stat-value" style="color:{_G};">{activos:,}</div>
    </div>
    <div class="tbl-stat-card" style="background:{_Y2};border-color:rgba(192,156,46,0.25);">
      <div class="tbl-stat-icon">⏸️</div>
      <div class="tbl-stat-label" style="color:{_Y};">INACTIVOS</div>
      <div class="tbl-stat-value" style="color:{_Y};">{inactivos:,}</div>
    </div>
  </div>

  <!-- DISPONIBILIDAD OPERACIONAL -->
  <div class="tbl-prog-card">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div class="tbl-prog-label">DISPONIBILIDAD OPERACIONAL</div>
      <div class="tbl-prog-value" style="color:{'#137659' if disp_oper>=75 else ('#c09c2e' if disp_oper>=50 else '#c62828')};">{disp_oper:.0f}%</div>
    </div>
    <div class="tbl-prog-wrap">
      <div class="tbl-prog-fill" style="width:{min(disp_oper,100):.1f}%;background:{'#137659' if disp_oper>=75 else ('#c09c2e' if disp_oper>=50 else '#c62828')};"></div>
    </div>
  </div>

  <!-- USO OPERATIVO -->
  <div class="tbl-prog-card">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div class="tbl-prog-label">USO OPERATIVO</div>
      <div class="tbl-prog-value" style="color:{'#137659' if uso_oper>=60 else ('#c09c2e' if uso_oper>=40 else '#c62828')};">{uso_oper:.0f}%</div>
    </div>
    <div class="tbl-prog-wrap">
      <div class="tbl-prog-fill" style="width:{min(uso_oper,100):.1f}%;background:{'#137659' if uso_oper>=60 else ('#c09c2e' if uso_oper>=40 else '#c62828')};"></div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL CENTRAL — GAUGE IF + TENDENCIA ANUAL
    # ─────────────────────────────────────────────────────────────────────────
    with col_c:
        st.markdown('<div class="tbl-panel">', unsafe_allow_html=True)

        # Gauge IF (menor es mejor → verde izquierda, rojo derecha)
        st.markdown('<div class="tbl-gauge-card"><div class="tbl-gauge-title">ÍNDICE DE FALLA (IF)</div>', unsafe_allow_html=True)
        components.html(
            _gauge_html(if_actual, META_IF, "IF", higher_is_better=False,
                        max_val=if_max, cid="gauge_if"),
            height=210, scrolling=False
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Gráfico IF anual — barras (ON/OFF) + línea IF
        opts_if = {
            "backgroundColor": _W,
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.97)",
                "borderColor": "rgba(19,118,89,0.2)",
                "textStyle": {"color": _T, "fontSize": 11},
            },
            "legend": {
                "data": ["Pozos ON", "Pozos OFF", "IF (%)"],
                "bottom": 0, "itemHeight": 7, "itemGap": 12,
                "textStyle": {"color": _T2, "fontSize": 8, "fontFamily": "Inter, Arial, sans-serif"},
            },
            "grid": {"top": "6%", "left": "3%", "right": "8%", "bottom": "22%", "containLabel": True},
            "xAxis": {
                "type": "category", "data": if_cats,
                "axisLabel": {"color": _T2, "fontSize": 8, "fontFamily": "Inter, Arial, sans-serif"},
                "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.15)"}},
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
                    "min": 0,
                }
            ],
            "series": [
                {
                    "name": "Pozos ON", "type": "bar", "stack": "pozos",
                    "data": on_vals, "barMaxWidth": 22,
                    "itemStyle": {"color": "rgba(19,118,89,0.75)", "borderRadius": [3, 3, 0, 0]},
                },
                {
                    "name": "Pozos OFF", "type": "bar", "stack": "pozos",
                    "data": off_vals, "barMaxWidth": 22,
                    "itemStyle": {"color": "rgba(198,40,40,0.3)", "borderRadius": [3, 3, 0, 0]},
                },
                {
                    "name": "IF (%)", "type": "line", "yAxisIndex": 1,
                    "data": if_vals, "smooth": True,
                    "symbol": "circle", "symbolSize": 6,
                    "lineStyle": {"color": _R, "width": 2.5},
                    "itemStyle": {"color": _R, "borderColor": _W, "borderWidth": 2},
                    "areaStyle": {"color": "rgba(198,40,40,0.05)"},
                    "markLine": {
                        "silent": True,
                        "lineStyle": {"color": _G, "type": "dashed", "width": 1.5},
                        "data": [{"yAxis": META_IF, "name": f"Meta {META_IF}%"}],
                        "label": {
                            "formatter": f"Meta {META_IF}%",
                            "color": _G, "fontSize": 8,
                            "fontFamily": "Inter, Arial, sans-serif"
                        },
                    }
                }
            ]
        }
        st.markdown(f"<div class='tbl-sec-title'>IF EN EL ÚLTIMO AÑO — {anio_eval}</div>", unsafe_allow_html=True)
        components.html(_chart_html(opts_if, 230, "chart_if_anual"), height=242, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL DERECHO — GAUGES MTBF + RL + DISTRIBUCIÓN RUNLIFE
    # ─────────────────────────────────────────────────────────────────────────
    with col_r:
        st.markdown('<div class="tbl-panel">', unsafe_allow_html=True)

        # Dos gauges lado a lado
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="tbl-gauge-card"><div class="tbl-gauge-title">MTBF (días)</div>', unsafe_allow_html=True)
            components.html(
                _gauge_html(mtbf_val, META_MTBF, "MTBF", higher_is_better=True,
                            max_val=mtbf_max, cid="gauge_mtbf"),
                height=210, scrolling=False
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with g2:
            st.markdown('<div class="tbl-gauge-card"><div class="tbl-gauge-title">RUNLIFE (días)</div>', unsafe_allow_html=True)
            components.html(
                _gauge_html(rl_val, META_RL, "RL", higher_is_better=True,
                            max_val=rl_max, cid="gauge_rl"),
                height=210, scrolling=False
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # Gráfico distribución RunLife
        rl_bar_colors = [_R, _Y, _G2, _G]
        total_rl = max(sum(rl_counts), 1)
        rl_pcts  = [round(v / total_rl * 100, 1) for v in rl_counts]

        opts_rl = {
            "backgroundColor": _W,
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.97)",
                "borderColor": "rgba(19,118,89,0.2)",
                "textStyle": {"color": _T, "fontSize": 11},
                "formatter": (
                    "function(p){"
                    "  var b=p[0];"
                    "  return b.name+'<br/>Pozos: <b>'+b.value+'</b>'"
                    "}"
                ),
            },
            "grid": {"top": "8%", "left": "2%", "right": "4%", "bottom": "22%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": rl_bins,
                "axisLabel": {
                    "color": _T2, "fontSize": 7, "interval": 0,
                    "fontFamily": "Inter, Arial, sans-serif",
                    "rotate": 15,
                },
                "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.15)"}},
                "axisTick": {"show": False},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": _T2, "fontSize": 7},
                "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)", "type": "dashed"}},
            },
            "series": [{
                "type": "bar",
                "data": [
                    {"value": v,
                     "itemStyle": {"color": c, "borderRadius": [5, 5, 0, 0]},
                     "label": {
                         "show": True,
                         "position": "top",
                         "color": _T,
                         "fontSize": 10,
                         "fontWeight": "700",
                         "fontFamily": "Inter, Arial, sans-serif",
                         "formatter": f"{v}\n{p}%",
                     }}
                    for v, c, p in zip(rl_counts, rl_bar_colors, rl_pcts)
                ],
                "barWidth": "48%",
            }]
        }
        st.markdown(f"<div class='tbl-sec-title'>DISTRIBUCIÓN RUNLIFE — POZOS EN FONDO</div>", unsafe_allow_html=True)
        components.html(_chart_html(opts_rl, 235, "chart_rl"), height=248, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)
