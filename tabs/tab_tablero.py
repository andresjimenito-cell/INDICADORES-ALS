"""
tabs/tab_tablero.py  —  v4.2 Ultra Refined Minimalist Dashboard
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
    border-radius: 20px;
    border: 1.5px solid rgba(19,118,89,0.18);
    box-shadow: 0 2px 8px rgba(19,118,89,0.06), 0 8px 32px rgba(19,118,89,0.08);
    padding: 16px 14px;
    height: 480px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: box-shadow 0.3s ease;
}

.tbl-panel-lateral:hover {
    box-shadow: 0 4px 16px rgba(19,118,89,0.10), 0 12px 40px rgba(19,118,89,0.12);
}

.tbl-sec-title-lat {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 800;
    color: #137659;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-left: 3px solid #137659;
    padding-left: 9px;
    margin-bottom: 2px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── ALS EN FONDO Card ── */
.tbl-kpi-fondo-card {
    background: linear-gradient(135deg, #f8fdfb 0%, #ffffff 100%);
    border: 1.5px solid rgba(19,118,89,0.14);
    border-radius: 16px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 120px;
    box-sizing: border-box;
    transition: border-color 0.25s, transform 0.2s;
    position: relative;
    overflow: hidden;
}

.tbl-kpi-fondo-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #137659, #0a4d34, #137659);
    border-radius: 16px 16px 0 0;
}

.tbl-kpi-fondo-card:hover {
    border-color: rgba(19,118,89,0.28);
    transform: translateY(-1px);
}

/* ── Icono Petrolero ── */
.tbl-pump-icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
}

.tbl-pump-icon {
    width: 45px;
    height: 45px;
    opacity: 0.65;
    filter: drop-shadow(0 2px 4px rgba(19,118,89,0.15));
}

/* ── Mini Bar Chart para ALS ── */
.tbl-mini-chart-container {
    display: flex;
    gap: 6px;
    align-items: flex-end;
    height: 90px;
    padding: 0 2px;
}

.tbl-mini-bar-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 22px;
}

.tbl-mini-bar-val {
    font-family: 'Inter', sans-serif;
    font-size: 7.5px;
    font-weight: 700;
    color: #455a72;
    margin-bottom: 2px;
    white-space: nowrap;
}

.tbl-mini-bar-track {
    width: 9px;
    height: 42px;
    background: #c62828;
    border-radius: 3px;
    display: flex;
    flex-direction: column-reverse;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.tbl-mini-bar-fill {
    width: 100%;
    background: linear-gradient(180deg, #1db87b 0%, #137659 100%);
    transition: height 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.tbl-mini-bar-label {
    font-family: 'Inter', sans-serif;
    font-size: 8px;
    font-weight: 800;
    color: #137659;
    margin-top: 3px;
}

/* ── Info ALS EN FONDO ── */
.tbl-info-fondo {
    text-align: right;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.tbl-info-fondo-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 9px;
    font-weight: 800;
    color: #455a72;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.tbl-info-fondo-val {
    font-family: 'Inter', sans-serif;
    font-size: 30px;
    font-weight: 900;
    color: #1f221e;
    line-height: 1;
    margin-top: 3px;
    letter-spacing: -1px;
}

/* ── Grid Inferior ── */
.tbl-grid-bottom {
    display: flex;
    gap: 10px;
    height: 290px;
}

/* ── Tarjetas Genéricas ── */
.tbl-card-base {
    background: #ffffff;
    border: 1.5px solid rgba(19,118,89,0.13);
    border-radius: 16px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 10px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.tbl-card-base:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(19,118,89,0.10);
    border-color: rgba(19,118,89,0.25);
}

/* ── Tarjeta Fallados (Izquierda, Alta) ── */
.tbl-card-fallados {
    width: 48%;
    height: 100%;
    border-color: rgba(198,40,40,0.20);
    justify-content: space-between;
    padding: 14px 8px;
    background: linear-gradient(160deg, #fff 60%, #fff9f9 100%);
    position: relative;
    overflow: hidden;
}

.tbl-card-fallados::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #c62828, #e57373);
    border-radius: 16px 16px 0 0;
}

.tbl-card-fallados:hover {
    border-color: rgba(198,40,40,0.32);
    box-shadow: 0 6px 20px rgba(198,40,40,0.08);
}

.tbl-icon-circle-red {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #ffebee 0%, #ffd9d9 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #c62828;
    box-shadow: 0 3px 10px rgba(198,40,40,0.15);
}

.tbl-fallados-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 800;
    color: #1f221e;
    letter-spacing: 0.8px;
    margin-top: 6px;
    text-transform: uppercase;
}

.tbl-fallados-val {
    font-family: 'Inter', sans-serif;
    font-size: 36px;
    font-weight: 900;
    color: #c62828;
    line-height: 1;
    margin-top: 2px;
    letter-spacing: -1.5px;
}

.tbl-fallados-atrib {
    border-top: 1px dashed rgba(198,40,40,0.2);
    padding-top: 7px;
    width: 100%;
    margin-top: 6px;
}

.tbl-fallados-atrib-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 7.5px;
    font-weight: 700;
    color: #455a72;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1.2;
}

.tbl-fallados-atrib-val {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 900;
    color: #c62828;
    margin-top: 2px;
    letter-spacing: -0.5px;
}

/* ── Columna Derecha (Operativos, Activos, Inactivos) ── */
.tbl-col-operativos {
    width: 52%;
    display: flex;
    flex-direction: column;
    gap: 10px;
    height: 100%;
}

/* ── Tarjeta Operativos ── */
.tbl-card-operativos {
    height: 135px;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    border-color: rgba(19,118,89,0.22);
    padding: 8px 12px;
    background: linear-gradient(135deg, #f8fdfb 0%, #ffffff 100%);
    position: relative;
    overflow: hidden;
}

.tbl-card-operativos::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #137659, #1db87b);
    border-radius: 16px 16px 0 0;
}

.tbl-card-operativos:hover {
    border-color: rgba(19,118,89,0.35);
    box-shadow: 0 6px 20px rgba(19,118,89,0.10);
}

.tbl-icon-circle-green {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #e8f5ee 0%, #c5e8d5 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    color: #137659;
    box-shadow: 0 3px 10px rgba(19,118,89,0.15);
}

.tbl-op-info {
    text-align: right;
}

.tbl-op-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 800;
    color: #1f221e;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.tbl-op-val {
    font-family: 'Inter', sans-serif;
    font-size: 32px;
    font-weight: 900;
    color: #137659;
    line-height: 1;
    margin-top: 3px;
    letter-spacing: -1px;
}

/* ── Fila de Activos / Inactivos ── */
.tbl-row-act-inact {
    display: flex;
    gap: 10px;
    height: 145px;
}

.tbl-card-sub {
    flex: 1;
    height: 100%;
    padding: 12px 6px;
    justify-content: space-between;
}

.tbl-icon-circle-subgreen {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #c2ebd9, #a0d9c0);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: #0f7d58;
    box-shadow: 0 2px 8px rgba(19,118,89,0.12);
}

.tbl-icon-circle-subyellow {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #fff3cd, #ffe58a);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: #c09c2e;
    box-shadow: 0 2px 8px rgba(192,156,46,0.15);
}

.tbl-sub-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 8px;
    font-weight: 800;
    color: #455a72;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-top: 4px;
}

.tbl-sub-val {
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    font-weight: 900;
    line-height: 1;
    margin-top: 2px;
    letter-spacing: -0.5px;
}

/* ── Animación de entrada para números ── */
@keyframes countUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

.tbl-info-fondo-val,
.tbl-fallados-val,
.tbl-op-val,
.tbl-sub-val,
.tbl-fallados-atrib-val {
    animation: countUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) both;
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

    # ── Ignorar fecha_ini y usar sólo fecha_evaluacion para el Tablero ──────
    df_raw = st.session_state.get('df_bd_calculated')
    if df_raw is not None:
        df_resumen = df_raw.copy()
        if 'ACTIVO' in df_resumen.columns:
            df_resumen = df_resumen[df_resumen['ACTIVO'].astype(str).str.upper().str.strip() != 'ECUADOR']
        for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col in df_resumen.columns:
                df_resumen[col] = pd.to_datetime(df_resumen[col], errors='coerce')
        df_resumen = df_resumen[df_resumen['FECHA_RUN'].dt.normalize() <= fecha_eval_date].copy()
        df_resumen.loc[df_resumen['FECHA_FALLA'].dt.normalize() > fecha_eval_date, 'FECHA_FALLA'] = pd.NaT
        
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
            if val != 'TODOS' and col in df_resumen.columns:
                df_resumen = df_resumen[df_resumen[col] == val]
    else:
        df_resumen = df_bd_filtered.copy()
        for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col in df_resumen.columns:
                df_resumen[col] = pd.to_datetime(df_resumen[col], errors='coerce')

    df = df_resumen.copy()
    df['_RUN']  = df['FECHA_RUN'].dt.normalize()
    df['_FALL'] = df['FECHA_FALLA'].dt.normalize() if 'FECHA_FALLA' in df.columns else pd.NaT
    df['_PULL'] = df['FECHA_PULL'].dt.normalize()  if 'FECHA_PULL'  in df.columns else pd.NaT

    # ── ALS en fondo ─────────────────────────────────────────────────────────
    mask_fondo = (df['_RUN'] <= fecha_eval_date) & (df['_PULL'].isna() | (df['_PULL'] > fecha_eval_date))
    df_fondo = df[mask_fondo]
    als_fondo = df_fondo['POZO'].nunique() if 'POZO' in df_fondo.columns else 0

    # ── Fallados y operativos ────────────────────────────────────────────────
    df_falla = df_fondo[df_fondo['_FALL'].notna() & (df_fondo['_FALL'] <= fecha_eval_date)]
    als_fallados  = df_falla['POZO'].nunique() if 'POZO' in df_falla.columns else 0
    als_operativos = df_fondo[df_fondo['_FALL'].isna() | (df_fondo['_FALL'] > fecha_eval_date)]['POZO'].nunique() if 'POZO' in df_fondo.columns else 0

    # ── Breakdown por tipo ALS ───────────────────────────────────────────────
    als_breakdown = {}
    if 'ALS' in df_fondo.columns:
        for t in ALS_TIPOS:
            sub  = df_fondo[df_fondo['ALS'].astype(str).str.strip().str.upper() == t]
            tot  = sub['POZO'].nunique() if 'POZO' in sub.columns else 0
            fall = sub[sub['_FALL'].notna() & (sub['_FALL'] <= fecha_eval_date)]['POZO'].nunique() if 'POZO' in sub.columns else 0
            als_breakdown[t] = {'total': tot, 'op': tot - fall}

    # ── Activos / Inactivos ────
    df_f9_raw = st.session_state.get('df_forma9_calculated')
    if df_f9_raw is not None:
        df_forma9_untr = df_f9_raw.copy()
        df_forma9_untr['FECHA_FORMA9'] = pd.to_datetime(df_forma9_untr['FECHA_FORMA9'], errors='coerce')
        pozos_en_resumen = df_resumen['POZO'].unique() if 'POZO' in df_resumen.columns else []
        df_forma9_untr = df_forma9_untr[df_forma9_untr['POZO'].isin(pozos_en_resumen)].copy()
    else:
        df_forma9_untr = df_forma9_filtered.copy()

    df_f9 = df_forma9_untr.copy()
    df_f9 = df_f9[(df_f9['FECHA_FORMA9'].dt.month == mes_eval) & (df_f9['FECHA_FORMA9'].dt.year == anio_eval)]

    activos = inactivos = 0
    if not df_f9.empty and 'FECHA_FORMA9' in df_f9.columns:
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

    # ── Serie IF mensual ─
    if_cats, if_vals, on_vals, off_vals = [], [], [], []
    if_actual = 0.0

    try:
        from indice_falla import calcular_indice_falla_anual
        _, df_mensual_if = calcular_indice_falla_anual(
            df.copy(), df_forma9_untr.copy(), fecha_evaluacion
        )

        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        df_yr = df_mensual_if.tail(12).copy()

        for _, row in df_yr.iterrows():
            m_str = row['Mes']
            m_idx = int(m_str[5:7]) - 1
            label = f"{_MESES[m_idx]}-{m_str[2:4]}"
            if_cats.append(label)
            on_m   = int(row.get('Pozos ON', 0))
            if_roll = float(row.get('Indice_Falla_Rolling_ALS_ON', 0.0)) * 100.0
            if_vals.append(if_roll)
            on_vals.append(on_m)
            off_m  = max(int(row.get('Pozos Operativos', on_m)) - on_m, 0)
            off_vals.append(off_m)

        last_row = df_mensual_if.tail(1)
        if not last_row.empty:
            if_actual = float(last_row['Indice_Falla_Rolling_ALS_ON'].iloc[0]) * 100.0
        elif if_vals:
            if_actual = if_vals[-1]

    except Exception as _e_if:
        _MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        from dateutil.relativedelta import relativedelta
        start_m = fecha_eval_dt - relativedelta(months=11)
        for i in range(12):
            curr_date = start_m + relativedelta(months=i)
            m = curr_date.month
            y = curr_date.year
            last_day = calendar.monthrange(y, m)[1]
            end_m_ts = pd.Timestamp(year=y, month=m, day=last_day).normalize()
            fallas_m = int(df[
                (df['_FALL'].dt.month == m) & (df['_FALL'].dt.year == y)
            ].shape[0])
            on_m = 0
            if not df_forma9_untr.empty and 'FECHA_FORMA9' in df_forma9_untr.columns:
                df_f9c = df_forma9_untr.copy()
                df_f9c['_F9'] = pd.to_datetime(df_f9c['FECHA_FORMA9'], errors='coerce').dt.normalize()
                dias_c = 'DIAS TRABAJADOS' if 'DIAS TRABAJADOS' in df_f9c.columns else None
                mm = (df_f9c['_F9'].dt.month == m) & (df_f9c['_F9'].dt.year == y)
                if dias_c:
                    mm = mm & (df_f9c[dias_c].fillna(0) > 0)
                on_m = int(df_f9c[mm]['POZO'].nunique())
            op_m = int(df[
                (df['_RUN'] <= end_m_ts) &
                (df['_FALL'].isna() | (df['_FALL'] > end_m_ts)) &
                (df['_PULL'].isna() | (df['_PULL'] > end_m_ts))
            ]['POZO'].nunique()) if 'POZO' in df.columns else 0
            if_cats.append(f"{_MESES[m - 1]}-{str(y)[2:4]}")
            if_m = (fallas_m / max(on_m, 1)) * 100.0
            if_vals.append(if_m)
            on_vals.append(on_m)
            off_vals.append(max(op_m - on_m, 0))
        if_actual = if_vals[-1] if if_vals else 0.0

    if_max = max(max(if_vals) * 1.3, META_IF * 2, 20) if if_vals else 20

    # ── MTBF ─────────────────────────────────────────────────────────────────
    try:
        mtbf_val, _ = mtbf_mod.calcular_mtbf(df, fecha_evaluacion)
        mtbf_val = float(mtbf_val) if mtbf_val and not np.isnan(float(mtbf_val)) else 0.0
    except Exception:
        mtbf_val = 0.0

    # ── RunLife promedio ──────────────────────────────────────────────────────
    rl_col = next((c for c in ('RUN LIFE', 'RUN_LIFE', 'RUNLIFE') if c in df.columns), None)
    rl_val = float(df[rl_col].dropna().mean()) if rl_col else 0.0
    if np.isnan(rl_val):
        rl_val = 0.0

    # ── Distribución RunLife ─────────────────────────────────────────────────
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
        fecha_ini_str = st.session_state.get('fecha_inicio_state')
        if fecha_ini_str is not None:
            fecha_ini_dt = pd.to_datetime(fecha_ini_str).normalize()
        else:
            fecha_ini_dt = fecha_eval_date - pd.DateOffset(years=1)
            
        fallas_als = int((df_resumen['INDICADOR_MTBF'] == 1).sum()) if df_resumen is not None else 0
        
        if df_resumen is not None and not df_resumen.empty:
            fallas_totales = int(df_resumen[
                (df_resumen['FECHA_FALLA'].notna()) &
                (df_resumen['FECHA_FALLA'].dt.normalize() >= fecha_ini_dt) &
                (df_resumen['FECHA_FALLA'].dt.normalize() <= fecha_eval_date)
            ].shape[0])
            
            limit_365 = fecha_eval_date - pd.Timedelta(days=365)
            df_recent = df_resumen[df_resumen['FECHA_FALLA'] >= limit_365]
            pozos_fallados_rec = df_recent['POZO'].nunique() if not df_recent.empty else 0
            idx_sev = (len(df_recent) / pozos_fallados_rec) if pozos_fallados_rec > 0 else 0.0
        else:
            fallas_totales = 0
            idx_sev = 0.0

        # Barras verticales ALS con animación CSS
        mini_bars_html = ""
        for t in ALS_TIPOS:
            bd_info = als_breakdown.get(t, {'total': 0, 'op': 0})
            tot = bd_info['total']
            op = bd_info['op']
            op_pct = (op / tot * 100) if tot > 0 else 0
            mini_bars_html += (
                f'<div class="tbl-mini-bar-col">'
                f'<div class="tbl-mini-bar-val">{op}/{tot}</div>'
                f'<div class="tbl-mini-bar-track">'
                f'<div class="tbl-mini-bar-fill" style="height: {op_pct:.1f}%;"></div>'
                f'</div>'
                f'<div class="tbl-mini-bar-label">{t}</div>'
                f'</div>'
            )

        kpi_panel_html = f"""
<div class="tbl-panel-lateral">
  <div class="tbl-sec-title-lat">Resumen Operativo</div>
  
  <!-- ALS EN FONDO PANEL -->
  <div class="tbl-kpi-fondo-card">
    <div class="tbl-pump-icon-container">
      <svg class="tbl-pump-icon" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="73" width="80" height="6" fill="#137659"/>
        <path d="M12.5 73 L22 58 L28.5 58 L32.5 73 Z" fill="#137659"/>
        <path d="M9.5 57.5 C9.5 47.5 17.5 39.5 22 39.5 C23 39.5 24 40.5 23.5 42.5 C21.5 49.5 14.5 56.5 11 58.5 C10.5 58.8 9.5 58.5 9.5 57.5 Z" fill="#1f221e"/>
        <circle cx="22" cy="58" r="2.5" fill="#ffffff"/>
        <path d="M35 73 L47.5 30 L52.5 30 L65 73 H59 L50 42 L41 73 Z" fill="#137659"/>
        <path d="M46.5 33 L53.5 33 M44.5 40 L55.5 40 M42 49 L58 49 M39.5 58 L60.5 58 M37.5 67 L62.5 67" stroke="#137659" stroke-width="1.8"/>
        <path d="M47.5 30 L59 73 M52.5 30 L41 73" stroke="#137659" stroke-width="1.2"/>
        <path d="M27.5 20.5 L73 31.5 L71.5 36.5 L26 25.5 Z" fill="#1f221e"/>
        <path d="M72 31.5 C75 22.5 83 23 85 32 C86.5 38 85.5 45.5 84 52.5 L79.5 52.5 C81.5 46.5 81.5 37 77.5 33 Z" fill="#1f221e"/>
        <circle cx="82" cy="29" r="1" fill="#ffffff"/>
        <circle cx="83.5" cy="35" r="1" fill="#ffffff"/>
        <circle cx="83.5" cy="41" r="1" fill="#ffffff"/>
        <circle cx="82.5" cy="47" r="1" fill="#ffffff"/>
        <line x1="85" y1="32" x2="85" y2="70" stroke="#1f221e" stroke-width="1.8"/>
        <rect x="82.5" y="70" width="5" height="3" fill="#137659"/>
        <line x1="27" y1="23" x2="11" y2="52" stroke="#1f221e" stroke-width="2"/>
        <circle cx="27" cy="23" r="2.5" fill="#1f221e"/>
        <circle cx="11" cy="52" r="2" fill="#1f221e"/>
      </svg>
    </div>
    
    <div class="tbl-mini-chart-container">
      {mini_bars_html}
    </div>
    
    <div class="tbl-info-fondo">
      <div class="tbl-info-fondo-lbl">ALS EN FONDO</div>
      <div class="tbl-info-fondo-val">{als_fondo:,}</div>
    </div>
  </div>

  <div class="tbl-grid-bottom">
    
    <!-- ALS FALLADOS -->
    <div class="tbl-card-base tbl-card-fallados">
      <div class="tbl-icon-circle-red">⚠️</div>
      <div>
        <div class="tbl-fallados-lbl">Pozos Fallados</div>
        <div class="tbl-fallados-val">{als_fallados:,}</div>
      </div>
      
      <div class="tbl-fallados-atrib">
        <div class="tbl-fallados-atrib-lbl">Fallas Periodo</div>
        <div class="tbl-fallados-atrib-val">{fallas_totales}</div>
      </div>
      
      <div class="tbl-fallados-atrib" style="border-top: 1px dashed rgba(198,40,40,0.2); padding-top: 6px; width: 100%;">
        <div class="tbl-fallados-atrib-lbl">I. Severidad</div>
        <div class="tbl-fallados-atrib-val">{idx_sev:.2f}</div>
      </div>
    </div>
    
    <!-- COLUMNA DERECHA -->
    <div class="tbl-col-operativos">
      
      <div class="tbl-card-base tbl-card-operativos">
        <div class="tbl-icon-circle-green">✅</div>
        <div class="tbl-op-info">
          <div class="tbl-op-lbl">ALS OPERATIVOS</div>
          <div class="tbl-op-val">{als_operativos:,}</div>
        </div>
      </div>
      
      <div class="tbl-row-act-inact">
        
        <div class="tbl-card-base tbl-card-sub">
          <div class="tbl-icon-circle-subgreen">▶️</div>
          <div>
            <div class="tbl-sub-lbl">ACTIVOS</div>
            <div class="tbl-sub-val" style="color: #0f7d58;">{activos:,}</div>
          </div>
        </div>
        
        <div class="tbl-card-base tbl-card-sub">
          <div class="tbl-icon-circle-subyellow">⏸️</div>
          <div>
            <div class="tbl-sub-lbl">INACTIVOS</div>
            <div class="tbl-sub-val" style="color: #c09c2e;">{inactivos:,}</div>
          </div>
        </div>
        
      </div>
      
    </div>
    
  </div>
</div>
""".replace("\n", " ")

        st.markdown(kpi_panel_html, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # COLUMNA 2: GAUGE IF + TENDENCIA ANUAL
    # ─────────────────────────────────────────────────────────────────────────
    with col_c:
        col2_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .tbl-panel {{
            background: #ffffff;
            border-radius: 20px;
            border: 1.5px solid rgba(19,118,89,0.18);
            box-shadow: 0 2px 8px rgba(19,118,89,0.06), 0 8px 32px rgba(19,118,89,0.08);
            padding: 16px;
            height: 480px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-panel::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #137659 0%, #1db87b 50%, #137659 100%);
            border-radius: 20px 20px 0 0;
        }}
        .tbl-sec-title {{
            font-size: 11px;
            font-weight: 800;
            color: #137659;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            border-left: 3px solid #137659;
            padding-left: 9px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .chart-container {{
            width: 100%;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>
    <div class="tbl-panel">
        <div class="tbl-sec-title">Índice de Falla (IF ALS ON)</div>
        <div id="gauge_if" class="chart-container" style="height: 190px;"></div>
        <div id="chart_if_anual" class="chart-container" style="height: 230px;"></div>
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
                animation: true,
                animationDuration: 1200,
                animationEasing: "cubicOut",
                series: [{{
                    type: "gauge",
                    startAngle: 205,
                    endAngle: -25,
                    min: 0,
                    max: maxVal,
                    center: ["50%", "54%"],
                    radius: "82%",
                    splitNumber: 4,
                    axisLine: {{
                        lineStyle: {{
                            width: 10,
                            color: arcColors,
                            shadowBlur: 4,
                            shadowColor: "rgba(19,118,89,0.15)"
                        }}
                    }},
                    progress: {{
                        show: false
                    }},
                    pointer: {{
                        itemStyle: {{ color: "{_T}", shadowBlur: 4, shadowColor: "rgba(31,34,30,0.3)" }},
                        width: 4,
                        length: "62%"
                    }},
                    axisTick: {{ show: false }},
                    splitLine: {{ show: false }},
                    axisLabel: {{ show: false }},
                    anchor: {{
                        show: true,
                        showAbove: true,
                        size: 8,
                        itemStyle: {{
                            borderWidth: 2,
                            borderColor: "{_T}",
                            color: "#fff",
                            shadowBlur: 3,
                            shadowColor: "rgba(0,0,0,0.2)"
                        }}
                    }},
                    detail: {{
                        valueAnimation: true,
                        formatter: function(val) {{ return val.toFixed(2) + "%"; }},
                        color: valColor,
                        fontSize: 20,
                        fontWeight: "900",
                        fontFamily: "Inter, sans-serif",
                        offsetCenter: [0, "30%"],
                        borderRadius: 4,
                        padding: [4, 8]
                    }},
                    title: {{
                        show: true,
                        offsetCenter: [0, "63%"],
                        color: "{_T2}",
                        fontSize: 9,
                        fontWeight: "700",
                        fontFamily: "Inter, sans-serif"
                    }},
                    data: [{{ value: value, name: "Meta IF: ≤ " + meta + "%" }}]
                }}]
            }};
            
            var chartG = echarts.init(document.getElementById('gauge_if'));
            chartG.setOption(gaugeOpt);

            var trendOpt = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 900,
                animationEasing: "cubicOut",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "cross", crossStyle: {{ color: "rgba(19,118,89,0.3)" }} }},
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(19,118,89,0.2)",
                    borderWidth: 1,
                    borderRadius: 10,
                    padding: [8, 12],
                    textStyle: {{ color: "{_T}", fontSize: 11, fontFamily: "Inter, sans-serif" }},
                    extraCssText: "box-shadow: 0 4px 16px rgba(19,118,89,0.12);"
                }},
                legend: {{
                    data: ["Pozos ON", "Pozos OFF", "IF (%)"],
                    bottom: 0,
                    itemHeight: 7,
                    itemGap: 12,
                    textStyle: {{ color: "{_T2}", fontSize: 9, fontFamily: "Inter, sans-serif" }}
                }},
                grid: {{ top: "8%", left: "3%", right: "8%", bottom: "18%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(if_cats)},
                    axisLabel: {{ color: "{_T2}", fontSize: 8, fontFamily: "Inter, sans-serif" }},
                    axisLine: {{ lineStyle: {{ color: "rgba(19,118,89,0.12)" }} }},
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
                        itemStyle: {{
                            color: {{
                                type: "linear",
                                x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    {{ offset: 0, color: "#1db87b" }},
                                    {{ offset: 1, color: "{_G}" }}
                                ]
                            }},
                            borderRadius: [3, 3, 0, 0]
                        }}
                    }},
                    {{
                        name: "Pozos OFF",
                        type: "bar",
                        stack: "pozos",
                        data: {json.dumps(off_vals)},
                        barMaxWidth: 16,
                        itemStyle: {{
                            color: "rgba(198,40,40,0.18)",
                            borderRadius: [3, 3, 0, 0]
                        }}
                    }},
                    {{
                        name: "IF (%)",
                        type: "line",
                        yAxisIndex: 1,
                        data: {json.dumps(if_vals)},
                        smooth: 0.5,
                        symbol: "circle",
                        symbolSize: 6,
                        lineStyle: {{ color: "{_R}", width: 2.5, shadowBlur: 6, shadowColor: "rgba(198,40,40,0.2)" }},
                        itemStyle: {{ color: "{_R}", borderColor: "#fff", borderWidth: 2 }},
                        areaStyle: {{
                            color: {{
                                type: "linear",
                                x: 0, y: 0, x2: 0, y2: 1,
                                colorStops: [
                                    {{ offset: 0, color: "rgba(198,40,40,0.15)" }},
                                    {{ offset: 1, color: "rgba(198,40,40,0.01)" }}
                                ]
                            }}
                        }},
                        markLine: {{
                            silent: true,
                            lineStyle: {{ color: "{_G}", type: "dashed", width: 1.5, opacity: 0.7 }},
                            data: [{{ yAxis: meta, name: "Meta" }}],
                            label: {{
                                formatter: "Meta " + meta + "%",
                                color: "{_G}",
                                fontSize: 8,
                                fontWeight: "700",
                                position: "end"
                            }}
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
    # COLUMNA 3: GAUGES MTBF + RUNLIFE + DISTRIBUCIÓN
    # ─────────────────────────────────────────────────────────────────────────
    with col_r:
        rl_bar_colors = [_G, _G2, _Y, _R]
        total_rl = max(sum(rl_counts), 1)
        rl_pcts  = [round(v / total_rl * 100, 1) for v in rl_counts]

        col3_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .tbl-panel {{
            background: #ffffff;
            border-radius: 20px;
            border: 1.5px solid rgba(19,118,89,0.18);
            box-shadow: 0 2px 8px rgba(19,118,89,0.06), 0 8px 32px rgba(19,118,89,0.08);
            padding: 16px;
            height: 480px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }}
        .tbl-panel::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #137659 0%, #1db87b 50%, #137659 100%);
            border-radius: 20px 20px 0 0;
        }}
        .tbl-sec-title {{
            font-size: 11px;
            font-weight: 800;
            color: #137659;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            border-left: 3px solid #137659;
            padding-left: 9px;
            margin-bottom: 6px;
        }}
        .gauges-row {{
            display: flex;
            justify-content: space-between;
            height: 190px;
            flex-shrink: 0;
        }}
        .gauge-col {{
            width: 48%;
            height: 100%;
        }}
        .chart-container {{
            width: 100%;
            flex-shrink: 0;
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
        <div id="chart_rl" class="chart-container" style="height: 230px;"></div>
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

            function makeGaugeOpt(val, meta, maxV, metaPct, arcColors, valColor, title, unit) {{
                return {{
                    backgroundColor: "transparent",
                    animation: true,
                    animationDuration: 1200,
                    animationEasing: "cubicOut",
                    series: [{{
                        type: "gauge",
                        startAngle: 205,
                        endAngle: -25,
                        min: 0,
                        max: maxV,
                        center: ["50%", "50%"],
                        radius: "88%",
                        splitNumber: 3,
                        axisLine: {{
                            lineStyle: {{
                                width: 10,
                                color: arcColors,
                                shadowBlur: 4,
                                shadowColor: "rgba(19,118,89,0.15)"
                            }}
                        }},
                        pointer: {{
                            itemStyle: {{
                                color: "{_T}",
                                shadowBlur: 4,
                                shadowColor: "rgba(31,34,30,0.3)"
                            }},
                            width: 4,
                            length: "60%"
                        }},
                        axisTick: {{ show: false }},
                        splitLine: {{ show: false }},
                        axisLabel: {{ show: false }},
                        anchor: {{
                            show: true,
                            size: 8,
                            itemStyle: {{
                                borderWidth: 2,
                                borderColor: "{_T}",
                                color: "#fff",
                                shadowBlur: 3,
                                shadowColor: "rgba(0,0,0,0.2)"
                            }}
                        }},
                        detail: {{
                            valueAnimation: true,
                            formatter: function(v) {{ return v.toFixed(1) + unit; }},
                            color: valColor,
                            fontSize: 15,
                            fontWeight: "900",
                            fontFamily: "Inter, sans-serif",
                            offsetCenter: [0, "32%"]
                        }},
                        title: {{
                            show: true,
                            offsetCenter: [0, "66%"],
                            color: "{_T2}",
                            fontSize: 8,
                            fontWeight: "700",
                            fontFamily: "Inter, sans-serif"
                        }},
                        data: [{{ value: val, name: title + "\\n(Meta: " + meta + ")" }}]
                    }}]
                }};
            }}
            
            var chartMTBF = echarts.init(document.getElementById('gauge_mtbf'));
            chartMTBF.setOption(makeGaugeOpt(
                mtbfVal, mtbfMeta, {mtbf_max}, mtbfMetaPct,
                mtbfColors, mtbfColor, "MTBF", " d"
            ));

            var rlVal = {rl_val};
            var rlMeta = {META_RL};
            var rlMetaPct = rlMeta / {rl_max};
            var rlColors = [[rlMetaPct, "{_R}"], [1.0, "{_G}"]];
            var rlColor = (rlVal >= rlMeta) ? "{_G}" : "{_R}";

            var chartRL = echarts.init(document.getElementById('gauge_rl'));
            chartRL.setOption(makeGaugeOpt(
                rlVal, rlMeta, {rl_max}, rlMetaPct,
                rlColors, rlColor, "RunLife", " d"
            ));

            var distOpt = {{
                backgroundColor: "transparent",
                animation: true,
                animationDuration: 900,
                animationEasing: "cubicOut",
                tooltip: {{
                    trigger: "axis",
                    axisPointer: {{ type: "shadow" }},
                    backgroundColor: "rgba(255,255,255,0.98)",
                    borderColor: "rgba(19,118,89,0.2)",
                    borderWidth: 1,
                    borderRadius: 10,
                    padding: [8, 12],
                    textStyle: {{ color: "{_T}", fontSize: 11, fontFamily: "Inter, sans-serif" }},
                    extraCssText: "box-shadow: 0 4px 16px rgba(19,118,89,0.12);",
                    formatter: function(p) {{
                        var b = p[0];
                        return b.name + "<br/>Pozos: <b>" + b.value + "</b>";
                    }}
                }},
                grid: {{ top: "14%", left: "2%", right: "4%", bottom: "14%", containLabel: true }},
                xAxis: {{
                    type: "category",
                    data: {json.dumps(rl_bins)},
                    axisLabel: {{ color: "{_T2}", fontSize: 8, fontFamily: "Inter, sans-serif", interval: 0 }},
                    axisLine: {{ lineStyle: {{ color: "rgba(19,118,89,0.12)" }} }},
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
                        {{
                            value: {rl_counts[0]},
                            itemStyle: {{
                                color: {{
                                    type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                    colorStops: [
                                        {{ offset: 0, color: "#1db87b" }},
                                        {{ offset: 1, color: "{rl_bar_colors[0]}" }}
                                    ]
                                }},
                                borderRadius: [5, 5, 0, 0],
                                shadowBlur: 4,
                                shadowColor: "rgba(19,118,89,0.15)"
                            }},
                            label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", fontFamily: "Inter, sans-serif", formatter: "{rl_counts[0]}\\n{rl_pcts[0]}%" }}
                        }},
                        {{
                            value: {rl_counts[1]},
                            itemStyle: {{
                                color: {{
                                    type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                    colorStops: [
                                        {{ offset: 0, color: "#148c6a" }},
                                        {{ offset: 1, color: "{rl_bar_colors[1]}" }}
                                    ]
                                }},
                                borderRadius: [5, 5, 0, 0],
                                shadowBlur: 4,
                                shadowColor: "rgba(10,77,52,0.15)"
                            }},
                            label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", fontFamily: "Inter, sans-serif", formatter: "{rl_counts[1]}\\n{rl_pcts[1]}%" }}
                        }},
                        {{
                            value: {rl_counts[2]},
                            itemStyle: {{
                                color: {{
                                    type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                    colorStops: [
                                        {{ offset: 0, color: "#d4b44a" }},
                                        {{ offset: 1, color: "{rl_bar_colors[2]}" }}
                                    ]
                                }},
                                borderRadius: [5, 5, 0, 0],
                                shadowBlur: 4,
                                shadowColor: "rgba(192,156,46,0.15)"
                            }},
                            label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", fontFamily: "Inter, sans-serif", formatter: "{rl_counts[2]}\\n{rl_pcts[2]}%" }}
                        }},
                        {{
                            value: {rl_counts[3]},
                            itemStyle: {{
                                color: {{
                                    type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                    colorStops: [
                                        {{ offset: 0, color: "#e57373" }},
                                        {{ offset: 1, color: "{rl_bar_colors[3]}" }}
                                    ]
                                }},
                                borderRadius: [5, 5, 0, 0],
                                shadowBlur: 4,
                                shadowColor: "rgba(198,40,40,0.15)"
                            }},
                            label: {{ show: true, position: "top", color: "{_T}", fontSize: 9, fontWeight: "700", fontFamily: "Inter, sans-serif", formatter: "{rl_counts[3]}\\n{rl_pcts[3]}%" }}
                        }}
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

    # ── TICKER HORIZONTAL DE DATOS (TELEPROMPTER / MARQUEE STYLE) ────────────────
    ticker_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    body {{
        margin: 0;
        padding: 0;
        background: transparent;
        overflow: hidden;
    }}
    
    .ticker-wrapper {{
        width: 100%;
        background: linear-gradient(90deg, rgba(255,255,255,0.98) 0%, rgba(248,253,251,0.99) 50%, rgba(255,255,255,0.98) 100%);
        border: 1px solid rgba(19, 118, 89, 0.14);
        border-radius: 10px;
        padding: 6px 14px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(19, 118, 89, 0.04);
        display: flex;
        align-items: center;
        box-sizing: border-box;
        height: 38px;
    }}
    
    .ticker-title {{
        font-family: 'Inter', sans-serif;
        font-size: 0.6rem;
        font-weight: 850;
        color: #137659;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-right: 2px solid rgba(19, 118, 89, 0.22);
        padding-right: 12px;
        margin-right: 12px;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;
    }}
    
    .ticker-content-container {{
        overflow: hidden;
        white-space: nowrap;
        width: 100%;
        position: relative;
    }}
    
    .ticker-marquee {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 35s linear infinite;
    }}
    
    .ticker-item {{
        display: inline-block;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        color: #1f221e;
        margin-right: 40px;
    }}
    
    .ticker-label {{
        color: #64748b;
        font-weight: 600;
        font-size: 0.62rem;
        margin-right: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .ticker-val {{
        color: #137659;
    }}
    
    .ticker-val.warning {{
        color: #c09c2e;
    }}
    
    .ticker-val.danger {{
        color: #c62828;
    }}
    
    @keyframes marquee {{
        0%   {{ transform: translate3d(0, 0, 0); }}
        100% {{ transform: translate3d(-100%, 0, 0); }}
    }}
    </style>
    
    <div class="ticker-wrapper">
        <div class="ticker-title">📡 ESTADO ALS</div>
        <div class="ticker-content-container">
            <div class="ticker-marquee">
                <span class="ticker-item"><span class="ticker-label">ALS EN FONDO:</span><span class="ticker-val">{als_fondo:,} POZOS</span></span>
                <span class="ticker-item"><span class="ticker-label">ACTIVOS OPERATIVOS:</span><span class="ticker-val">{als_operativos:,} POZOS ({(als_operativos/max(1,als_fondo)*100):.1f}%)</span></span>
                <span class="ticker-item"><span class="ticker-label">ALS FALLADOS:</span><span class="ticker-val danger">{als_fallados:,} POZOS ({(als_fallados/max(1,als_fondo)*100):.1f}%)</span></span>
                <span class="ticker-item"><span class="ticker-label">FALLAS DEL PERIODO:</span><span class="ticker-val danger">{fallas_totales} EVENTOS</span></span>
                <span class="ticker-item"><span class="ticker-label">MTBF EFECTIVO:</span><span class="ticker-val warning">{mtbf_val:.1f} DÍAS</span></span>
                <span class="ticker-item"><span class="ticker-label">RUN LIFE PROMEDIO:</span><span class="ticker-val">{rl_val:.1f} DÍAS</span></span>
                <span class="ticker-item"><span class="ticker-label">DISPONIBILIDAD OPERATIVA:</span><span class="ticker-val">{disp_oper:.1f}%</span></span>
                <span class="ticker-item"><span class="ticker-label">UTILIZACIÓN DE EQUIPOS:</span><span class="ticker-val">{uso_oper:.1f}%</span></span>
            </div>
        </div>
    </div>
    """
    st.components.v1.html(ticker_html, height=42, scrolling=False)