"""
tabs/tab_tablero.py  —  v4.1 Ultra Refined Minimalist Dashboard
==============================================================
Tablero Ejecutivo de Alto Impacto con estética industrial Parex.
Presenta 3 columnas simétricas de 480px de altura:
1. Resumen de Operaciones: Tarjeta premium con KPIs en fondo, pills ALS, estados operativos, activos, inactivos y barras de progreso.
2. Índice de Falla (IF < 1500 RLE): Velocímetro minimalista de precisión + Historial mensual de pozos y tasa IF (con degradados y sombras de área).
3. Desempeño y Vida Útil: Velocímetros limpios de MTBF y RunLife + Distribución de longevidad de pozos activos (con degradados y etiquetas flotantes).
"""

import json, calendar
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

import mtbf as mtbf_mod

# ── Paleta Corporativa Parex ─────────────────────────────────────────────────
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

META_IF   = 7.5
META_MTBF = 2190
META_RL   = 1500
ALS_TIPOS = ['ESP', 'PCP', 'EPCP', 'BM', 'BH']

def _css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Panel KPI Lateral ── */
.tbl-panel-lateral {
    background: #ffffff;
    border-radius: 16px;
    border: 1.5px solid rgba(19,118,89,0.2);
    box-shadow: 0 4px 20px rgba(19,118,89,0.08);
    padding: 18px 16px;
    height: 480px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.tbl-sec-title-lat {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 800;
    color: #137659;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-left: 4px solid #137659;
    padding-left: 8px;
    margin-bottom: 8px;
}

/* ── KPI Principal ── */
.tbl-kpi-main {
    background: linear-gradient(135deg, rgba(19,118,89,0.05) 0%, rgba(192,156,46,0.05) 100%);
    border: 1px solid rgba(19,118,89,0.15);
    border-radius: 12px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.tbl-kpi-main-icon {
    font-size: 28px;
    line-height: 1;
}
.tbl-kpi-main-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 700;
    color: #455a72;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.tbl-kpi-main-val {
    font-family: 'Inter', sans-serif;
    font-size: 26px;
    font-weight: 900;
    color: #137659;
    line-height: 1.1;
}

/* ── Pills ALS ── */
.tbl-pills-container {
    display: flex;
    gap: 4px;
    margin-top: 6px;
}
.tbl-pill-box {
    background: rgba(19,118,89,0.06);
    border: 1px solid rgba(19,118,89,0.15);
    border-radius: 8px;
    padding: 4px;
    flex: 1;
    text-align: center;
    transition: all 0.2s ease;
}
.tbl-pill-box:hover {
    background: rgba(19,118,89,0.12);
    transform: translateY(-1px);
}
.tbl-pill-name {
    font-family: 'Inter', sans-serif;
    font-size: 8px;
    font-weight: 800;
    color: #137659;
}
.tbl-pill-val {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 900;
    color: #1f221e;
    line-height: 1.1;
}
.tbl-pill-sub {
    font-family: 'Inter', sans-serif;
    font-size: 8px;
    color: #455a72;
}

/* ── Grid de Medidores ── */
.tbl-row-stats {
    display: flex;
    gap: 8px;
}
.tbl-stat-item {
    flex: 1;
    border-radius: 10px;
    padding: 8px 10px;
    text-align: center;
    border: 1px solid;
    transition: all 0.2s ease;
}
.tbl-stat-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
}
.tbl-stat-item-icon {
    font-size: 18px;
    margin-bottom: 2px;
}
.tbl-stat-item-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.tbl-stat-item-val {
    font-family: 'Inter', sans-serif;
    font-size: 20px;
    font-weight: 900;
    line-height: 1.1;
}

/* ── Barras de Progreso ── */
.tbl-prog-card {
    background: #fdfdfd;
    border: 1px solid rgba(19,118,89,0.12);
    border-radius: 10px;
    padding: 8px 10px;
}
.tbl-prog-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 9px;
    font-weight: 700;
    color: #455a72;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.tbl-prog-val {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 900;
    float: right;
}
.tbl-prog-track {
    background: rgba(19,118,89,0.08);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    margin-top: 4px;
}
.tbl-prog-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}
</style>
""", unsafe_allow_html=True)

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

    # ── Activos / Inactivos (Fórmula corregida idéntica al Resumen) ────────────
    activos = inactivos = 0
    if not df_forma9_filtered.empty and 'FECHA_FORMA9' in df_forma9_filtered.columns:
        df_f9     = df_forma9_filtered.copy()
        df_f9['_F9'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.normalize()
        dias_col  = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9.columns else None
        mask_on   = (df_f9['_F9'].dt.month == mes_eval) & (df_f9['_F9'].dt.year == anio_eval)
        if dias_col:
            mask_on = mask_on & (df_f9[dias_col].fillna(0) > 0)
        pozos_on  = set(df_f9[mask_on]['POZO'].astype(str).str.strip().unique())
        
        activos   = len(pozos_on)
        inactivos = max(0, als_operativos - activos)
    else:
        activos   = als_operativos
        inactivos = 0

    total_pozos  = max(activos + inactivos, 1)
    disp_oper    = activos   / total_pozos * 100
    uso_oper     = als_operativos / max(als_fondo, 1) * 100

    # ── Serie IF mensual — fórmula oficial: Indice_Falla_Rolling_ALS_ON_1500 ─
    if_cats, if_vals, on_vals, off_vals = [], [], [], []
    if_actual = 0.0

    try:
        from indice_falla import calcular_indice_falla_anual
        _, df_mensual_if = calcular_indice_falla_anual(
            df_bd_filtered.copy(), df_forma9_filtered.copy(), fecha_evaluacion
        )

        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        df_yr = df_mensual_if[
            df_mensual_if['Mes'].str.startswith(str(anio_eval))
        ].copy()

        for _, row in df_yr.iterrows():
            m_str = row['Mes']           # 'YYYY-MM'
            m_idx = int(m_str[5:7]) - 1  # 0-based month index
            if_cats.append(_MESES[m_idx])
            on_m   = int(row.get('Pozos ON', 0))
            if_roll = float(row.get('Indice_Falla_Rolling_ALS_ON_1500', 0.0)) * 100.0
            if_vals.append(if_roll)
            on_vals.append(on_m)
            off_m  = max(int(row.get('Pozos Operativos', on_m)) - on_m, 0)
            off_vals.append(off_m)

        last_row = df_mensual_if.tail(1)
        if not last_row.empty:
            if_actual = float(last_row['Indice_Falla_Rolling_ALS_ON_1500'].iloc[0]) * 100.0
        elif if_vals:
            if_actual = if_vals[-1]

    except Exception as _e_if:
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
            if_m = (fallas_m / max(on_m, 1)) * 100.0
            if_vals.append(if_m)
            on_vals.append(on_m)
            off_vals.append(max(op_m - on_m, 0))
        if_actual = if_vals[-1] if if_vals else 0.0

    if_max = max(max(if_vals) * 1.3, META_IF * 2, 20) if if_vals else 20

    # ── MTBF ─────────────────────────────────────────────────────────────────
    try:
        mtbf_val, _ = mtbf_mod.calcular_mtbf(df_bd_filtered, fecha_evaluacion)
        mtbf_val = float(mtbf_val) if mtbf_val and not np.isnan(float(mtbf_val)) else 0.0
    except Exception:
        mtbf_val = 0.0

    # ── RunLife promedio (tiempo de vida total) ──────────────────────────────
    rl_col = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in df_bd_filtered.columns), None)
    rl_val = float(df_bd_filtered[rl_col].dropna().mean()) if rl_col else 0.0
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

    mtbf_max = max(mtbf_val * 1.4, META_MTBF * 1.5, 3000)
    rl_max   = max(rl_val   * 1.4, META_RL   * 1.5, 2500)

    # ═════════════════════════════════════════════════════════════════════════
    # LAYOUT DE 3 COLUMNAS SIMÉTRICAS
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 1.25, 1.25], gap="medium")

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 1: KPIs OPERATIVOS (RENDERIZADO HTML COMPLETO)
    # ─────────────────────────────────────────────────────────────────────────
    with col_l:
        pills_html = "".join([
            f"""<div class="tbl-pill-box">
                  <div class="tbl-pill-name">{t}</div>
                  <div class="tbl-pill-val">{als_breakdown.get(t,{}).get('total',0)}</div>
                  <div class="tbl-pill-sub">{als_breakdown.get(t,{}).get('op',0)} op</div>
                </div>"""
            for t in ALS_TIPOS
        ])

        st.markdown(f"""
<div class="tbl-panel-lateral">
  <div class="tbl-sec-title-lat">Resumen Operativo</div>
  
  <!-- ALS EN FONDO -->
  <div class="tbl-kpi-main">
    <div class="tbl-kpi-main-icon">🛢️</div>
    <div style="flex:1;">
      <div class="tbl-kpi-main-lbl">ALS EN FONDO</div>
      <div class="tbl-kpi-main-val">{als_fondo:,}</div>
      <div class="tbl-pills-container">{pills_html}</div>
    </div>
  </div>

  <!-- ESTADOS DE FALLAS Y OPERATIVOS -->
  <div class="tbl-row-stats">
    <div class="tbl-stat-item" style="background:{_R2}; border-color:rgba(198,40,40,0.25);">
      <div class="tbl-stat-item-icon">⚠️</div>
      <div class="tbl-stat-item-lbl" style="color:{_R};">ALS FALLADOS</div>
      <div class="tbl-stat-item-val" style="color:{_R};">{als_fallados:,}</div>
    </div>
    <div class="tbl-stat-item" style="background:{_G3}; border-color:rgba(19,118,89,0.25);">
      <div class="tbl-stat-item-icon">✅</div>
      <div class="tbl-stat-item-lbl" style="color:{_G};">OPERATIVOS</div>
      <div class="tbl-stat-item-val" style="color:{_G};">{als_operativos:,}</div>
    </div>
  </div>

  <!-- ESTADOS DE TRABAJO (ACTIVOS/INACTIVOS) -->
  <div class="tbl-row-stats">
    <div class="tbl-stat-item" style="background:{_G3}; border-color:rgba(19,118,89,0.2);">
      <div class="tbl-stat-item-icon">▶️</div>
      <div class="tbl-stat-item-lbl" style="color:{_G};">ACTIVOS</div>
      <div class="tbl-stat-item-val" style="color:{_G};">{activos:,}</div>
    </div>
    <div class="tbl-stat-item" style="background:{_Y2}; border-color:rgba(192,156,46,0.25);">
      <div class="tbl-stat-item-icon">⏸️</div>
      <div class="tbl-stat-item-lbl" style="color:{_Y};">INACTIVOS</div>
      <div class="tbl-stat-item-val" style="color:{_Y};">{inactivos:,}</div>
    </div>
  </div>

  <!-- DISPONIBILIDAD -->
  <div class="tbl-prog-card">
    <div>
      <span class="tbl-prog-lbl">DISPONIBILIDAD OPERACIONAL</span>
      <span class="tbl-prog-val" style="color:{_G if disp_oper>=75 else (_Y if disp_oper>=50 else _R)};">{disp_oper:.0f}%</span>
    </div>
    <div class="tbl-prog-track">
      <div class="tbl-prog-bar" style="width:{min(disp_oper,100):.1f}%; background:{_G if disp_oper>=75 else (_Y if disp_oper>=50 else _R)};"></div>
    </div>
  </div>

  <!-- USO OPERATIVO -->
  <div class="tbl-prog-card">
    <div>
      <span class="tbl-prog-lbl">USO OPERATIVO</span>
      <span class="tbl-prog-val" style="color:{_G if uso_oper>=60 else (_Y if uso_oper>=40 else _R)};">{uso_oper:.0f}%</span>
    </div>
    <div class="tbl-prog-track">
      <div class="tbl-prog-bar" style="width:{min(uso_oper,100):.1f}%; background:{_G if uso_oper>=60 else (_Y if uso_oper>=40 else _R)};"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 2: GAUGE IF + TENDENCIA ANUAL (COMPONENTE HTML UNIFICADO)
    # ─────────────────────────────────────────────────────────────────────────
    with col_c:
        col2_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .tbl-panel {{
            background: #ffffff;
            border-radius: 16px;
            border: 1.5px solid rgba(19,118,89,0.2);
            box-shadow: 0 4px 20px rgba(19,118,89,0.08);
            padding: 16px;
            height: 480px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .tbl-sec-title {{
            font-size: 13px;
            font-weight: 800;
            color: #137659;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-left: 4px solid #137659;
            padding-left: 8px;
            margin-bottom: 5px;
        }}
        .chart-container {{
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Índice de Falla (IF &lt; 1500 ALS)</div>
        <div id="gauge_if" class="chart-container" style="height: 195px;"></div>
        <div id="chart_if_anual" class="chart-container" style="height: 225px;"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var value = {if_actual};
            var meta = {META_IF};
            var maxVal = {if_max};
            var metaPct = meta / maxVal;
            
            var arcColors = [[metaPct, "{_G}"], [1.0, "{_R}"]];
            var valColor = (value <= meta) ? "{_G}" : "{_R}";
            
            var gaugeOpt = {{
                backgroundColor: "transparent",
                series: [{{
                    type: "gauge",
                    startAngle: 200,
                    endAngle: -20,
                    min: 0,
                    max: maxVal,
                    center: ["50%", "52%"],
                    radius: "80%",
                    splitNumber: 4,
                    axisLine: {{ lineStyle: {{ width: 8, color: arcColors }} }},
                    pointer: {{ itemStyle: {{ color: "{_T}" }}, width: 3, length: "65%" }},
                    axisTick: {{ show: false }},
                    splitLine: {{ show: false }},
                    axisLabel: {{ show: false }},
                    anchor: {{ show: true, showAbove: true, size: 6, itemStyle: {{ borderWidth: 1.5, borderColor: "{_T}", color: "#fff" }} }},
                    detail: {{
                        valueAnimation: true,
                        formatter: function(val) {{ return val.toFixed(2) + "%"; }},
                        color: valColor,
                        fontSize: 18,
                        fontWeight: "900",
                        offsetCenter: [0, "32%"]
                    }},
                    title: {{ show: true, offsetCenter: [0, "65%"], color: "{_T2}", fontSize: 9, fontWeight: "700" }},
                    data: [{{ value: value, name: "Meta IF: <= " + meta + "%" }}]
                }}]
            }};
            
            var chartG = echarts.init(document.getElementById('gauge_if'));
            chartG.setOption(gaugeOpt);

            var trendOpt = {{
                backgroundColor: "transparent",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "shadow" }},
                    backgroundColor: "rgba(255,255,255,0.96)",
                    borderColor: "rgba(19,118,89,0.15)",
                    textStyle: {{ color: "{_T}", fontSize: 10 }}
                }},
                legend: {{
                    data: ["Pozos ON", "Pozos OFF", "IF (%)"],
                    bottom: 0,
                    itemHeight: 7,
                    itemGap: 10,
                    textStyle: {{ color: "{_T2}", fontSize: 8, fontFamily: "Inter, sans-serif" }}
                }},
                grid: {{ top: "12%", left: "3%", right: "8%", bottom: "20%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(if_cats)},
                    axisLabel: {{ color: "{_T2}", fontSize: 8 }},
                    axisLine: {{ lineStyle: {{ color: "rgba(19,118,89,0.15)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: [
                    {{
                        type: "value",
                        name: "Pozos",
                        nameTextStyle: {{ color: "{_T2}", fontSize: 8 }},
                        axisLabel: {{ color: "{_T2}", fontSize: 8 }},
                        splitLine: {{ lineStyle: {{ color: "rgba(19,118,89,0.06)", type: "dashed" }} }}
                    }},
                    {{
                        type: "value",
                        name: "IF %",
                        nameTextStyle: {{ color: "{_R}", fontSize: 8 }},
                        axisLabel: {{ color: "{_R}", fontSize: 8 }},
                        splitLine: {{ show: false }},
                        min: 0
                    }}
                ],
                series: [
                    {{
                        name: "Pozos ON",
                        type: "bar",
                        stack: "pozos",
                        data: {json.dumps(on_vals)},
                        barMaxWidth: 16,
                        itemStyle: {{ color: "rgba(19,118,89,0.75)", borderRadius: [2, 2, 0, 0] }}
                    }},
                    {{
                        name: "Pozos OFF",
                        type: "bar",
                        stack: "pozos",
                        data: {json.dumps(off_vals)},
                        barMaxWidth: 16,
                        itemStyle: {{ color: "rgba(198,40,40,0.3)", borderRadius: [2, 2, 0, 0] }}
                    }},
                    {{
                        name: "IF (%)",
                        type: "line",
                        yAxisIndex: 1,
                        data: {json.dumps(if_vals)},
                        smooth: true,
                        symbol: "circle",
                        symbolSize: 5,
                        lineStyle: {{ color: "{_R}", width: 2.2 }},
                        itemStyle: {{ color: "{_R}", borderColor: "#fff", borderWidth: 1.5 }},
                        areaStyle: {{ color: "rgba(198,40,40,0.04)" }},
                        markLine: {{
                            silent: true,
                            lineStyle: {{ color: "{_G}", type: "dashed", width: 1.2 }},
                            data: [{{ yAxis: meta, name: "Meta" }}],
                            label: {{ formatter: "Meta " + meta + "%", color: "{_G}", fontSize: 7, position: "end" }}
                        }}
                    }}
                ]
            }};
            
            var chartT = echarts.init(document.getElementById('chart_if_anual'));
            chartT.setOption(trendOpt);

            window.addEventListener('resize', function() {{
                chartG.resize();
                chartT.resize();
            }});
        }})();
    </script>
</body>
</html>
"""
        components.html(col2_html, height=480, scrolling=False)

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 3: GAUGES MTBF + RUNLIFE + DISTRIBUCIÓN (COMPONENTE HTML UNIFICADO)
    # ─────────────────────────────────────────────────────────────────────────
    with col_r:
        rl_bar_colors = [_R, _Y, _G2, _G]
        total_rl = max(sum(rl_counts), 1)
        rl_pcts  = [round(v / total_rl * 100, 1) for v in rl_counts]

        col3_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .tbl-panel {{
            background: #ffffff;
            border-radius: 16px;
            border: 1.5px solid rgba(19,118,89,0.2);
            box-shadow: 0 4px 20px rgba(19,118,89,0.08);
            padding: 16px;
            height: 480px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .tbl-sec-title {{
            font-size: 13px;
            font-weight: 800;
            color: #137659;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-left: 4px solid #137659;
            padding-left: 8px;
            margin-bottom: 5px;
        }}
        .gauges-row {{
            display: flex;
            justify-content: space-between;
            height: 195px;
        }}
        .gauge-col {{
            width: 48%;
            height: 100%;
        }}
        .chart-container {{
            width: 100%;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Desempeño (MTBF &amp; RunLife)</div>
        <div class="gauges-row">
            <div id="gauge_mtbf" class="gauge-col"></div>
            <div id="gauge_rl" class="gauge-col"></div>
        </div>
        <div id="chart_rl" class="chart-container" style="height: 225px;"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        (function() {{
            var mtbfVal = {mtbf_val};
            var mtbfMeta = {META_MTBF};
            var mtbfMax = {mtbf_max};
            var mtbfMetaPct = mtbfMeta / mtbfMax;
            
            var mtbfColors = [[mtbfMetaPct, "{_R}"], [1.0, "{_G}"]];
            var mtbfColor = (mtbfVal >= mtbfMeta) ? "{_G}" : "{_R}";
            
            var mtbfOpt = {{
                backgroundColor: "transparent",
                series: [{{
                    type: "gauge",
                    startAngle: 200,
                    endAngle: -20,
                    min: 0,
                    max: mtbfMax,
                    center: ["50%", "50%"],
                    radius: "85%",
                    splitNumber: 3,
                    axisLine: {{ lineStyle: {{ width: 8, color: mtbfColors }} }},
                    pointer: {{ itemStyle: {{ color: "{_T}" }}, width: 3, length: "65%" }},
                    axisTick: {{ show: false }},
                    splitLine: {{ show: false }},
                    axisLabel: {{ show: false }},
                    anchor: {{ show: true, size: 6, itemStyle: {{ borderWidth: 1.5, borderColor: "{_T}", color: "#fff" }} }},
                    detail: {{
                        valueAnimation: true,
                        formatter: function(val) {{ return val.toFixed(1) + " d"; }},
                        color: mtbfColor,
                        fontSize: 16,
                        fontWeight: "900",
                        offsetCenter: [0, "32%"]
                    }},
                    title: {{ show: true, offsetCenter: [0, "65%"], color: "{_T2}", fontSize: 8, fontWeight: "700" }},
                    data: [{{ value: mtbfVal, name: "MTBF\\n(Meta: " + mtbfMeta + ")" }}]
                }}]
            }};
            
            var chartMTBF = echarts.init(document.getElementById('gauge_mtbf'));
            chartMTBF.setOption(mtbfOpt);

            var rlVal = {rl_val};
            var rlMeta = {META_RL};
            var rlMax = {rl_max};
            var rlMetaPct = rlMeta / rlMax;
            
            var rlColors = [[rlMetaPct, "{_R}"], [1.0, "{_G}"]];
            var rlColor = (rlVal >= rlMeta) ? "{_G}" : "{_R}";
            
            var rlOpt = {{
                backgroundColor: "transparent",
                series: [{{
                    type: "gauge",
                    startAngle: 200,
                    endAngle: -20,
                    min: 0,
                    max: rlMax,
                    center: ["50%", "50%"],
                    radius: "85%",
                    splitNumber: 3,
                    axisLine: {{ lineStyle: {{ width: 8, color: rlColors }} }},
                    pointer: {{ itemStyle: {{ color: "{_T}" }}, width: 3, length: "65%" }},
                    axisTick: {{ show: false }},
                    splitLine: {{ show: false }},
                    axisLabel: {{ show: false }},
                    anchor: {{ show: true, size: 6, itemStyle: {{ borderWidth: 1.5, borderColor: "{_T}", color: "#fff" }} }},
                    detail: {{
                        valueAnimation: true,
                        formatter: function(val) {{ return val.toFixed(1) + " d"; }},
                        color: rlColor,
                        fontSize: 16,
                        fontWeight: "900",
                        offsetCenter: [0, "32%"]
                    }},
                    title: {{ show: true, offsetCenter: [0, "65%"], color: "{_T2}", fontSize: 8, fontWeight: "700" }},
                    data: [{{ value: rlVal, name: "RunLife\\n(Meta: " + rlMeta + ")" }}]
                }}]
            }};
            
            var chartRL = echarts.init(document.getElementById('gauge_rl'));
            chartRL.setOption(rlOpt);

            var distOpt = {{
                backgroundColor: "transparent",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "shadow" }},
                    backgroundColor: "rgba(255,255,255,0.96)",
                    borderColor: "rgba(19,118,89,0.15)",
                    textStyle: {{ color: "{_T}", fontSize: 10 }},
                    formatter: function(p) {{
                        var b = p[0];
                        return b.name + "<br/>Pozos: <b>" + b.value + "</b>";
                    }}
                }},
                grid: {{ top: "10%", left: "2%", right: "4%", bottom: "20%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(rl_bins)},
                    axisLabel: {{ color: "{_T2}", fontSize: 8, interval: 0 }},
                    axisLine: {{ lineStyle: {{ color: "rgba(19,118,89,0.15)" }} }},
                    axisTick: {{ show: false }}
                }},
                yAxis: {{
                    type: "value",
                    axisLabel: {{ color: "{_T2}", fontSize: 8 }},
                    splitLine: {{ lineStyle: {{ color: "rgba(19,118,89,0.06)", type: "dashed" }} }}
                }},
                series: [{{
                    type: "bar",
                    data: [
                        {{ value: {rl_counts[0]}, itemStyle: {{ color: "{rl_bar_colors[0]}", borderRadius: [4, 4, 0, 0] }}, label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", formatter: "{rl_counts[0]}\\n{rl_pcts[0]}%" }} }},
                        {{ value: {rl_counts[1]}, itemStyle: {{ color: "{rl_bar_colors[1]}", borderRadius: [4, 4, 0, 0] }}, label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", formatter: "{rl_counts[1]}\\n{rl_pcts[1]}%" }} }},
                        {{ value: {rl_counts[2]}, itemStyle: {{ color: "{rl_bar_colors[2]}", borderRadius: [4, 4, 0, 0] }}, label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", formatter: "{rl_counts[2]}\\n{rl_pcts[2]}%" }} }},
                        {{ value: {rl_counts[3]}, itemStyle: {{ color: "{rl_bar_colors[3]}", borderRadius: [4, 4, 0, 0] }}, label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", formatter: "{rl_counts[3]}\\n{rl_pcts[3]}%" }} }}
                    ],
                    barWidth: "45%"
                }}]
            }};
            
            var chartDist = echarts.init(document.getElementById('chart_rl'));
            chartDist.setOption(distOpt);

            window.addEventListener('resize', function() {{
                chartMTBF.resize();
                chartRL.resize();
                chartDist.resize();
            }});
        }})();
    </script>
</body>
</html>
"""
        components.html(col3_html, height=480, scrolling=False)
