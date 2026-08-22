"""
tabs/tab_performance.py  —  Performance y Producción de Pozos ON
================================================================
Módulo izquierdo de la pestaña Performance: foco en productividad y eficiencia operacional.
Estructura simétrica alineada con tab_mtbf.py:
1. Encabezado Hero Ejecutivo (Producción & Eficiencia)
2. 3 KPIs Hero (Pozos ON, BOPD Total, Eficiencia Promedio)
3. Gráfica Principal (Scatter BOPD vs Run Life Efectivo — 340px)
4. Gráfica Secundaria (Aporte de Producción por Rango de Longevidad — 270px)
5. Tabla Accionable (Top 5 Productores de Mayor Aporte)
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

# ── Tokens de Color y Estilo Simétricos (Parex Clásico) ─────────────────────
_G  = "#2E7D46"   # Verde Principal
_G2 = "#1F4620"   # Verde Oscuro
_G3 = "#EAF4EF"   # Fondo Verde
_Y  = "#C98A2C"   # Dorado / Warning
_Y2 = "#FCF6E9"   # Fondo Dorado
_R  = "#C0392B"   # Rojo / Alerta
_R2 = "#FDEDEC"   # Fondo Rojo
_B  = "#0284C7"   # Azul Info
_B2 = "#E0F2FE"   # Fondo Azul
_T  = "#1F221E"   # Texto Principal
_T2 = "#5B5C55"   # Texto Secundario
_BR = "rgba(46,125,70,0.15)"

_FS = "'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
_FN = "'Source Serif 4', Georgia, serif"
_FONTS_URL = ("https://fonts.googleapis.com/css2?"
              "family=Inter:wght@400;500;600;700;800&"
              "family=Source+Serif+4:opsz,wght@8..60,600;8..60,700;8..60,900&display=swap")

_SH1 = "0 1px 3px rgba(31,70,32,0.06), 0 6px 16px rgba(31,70,32,0.08)"
_SH2 = "0 2px 6px rgba(31,70,32,0.09), 0 12px 28px rgba(31,70,32,0.13)"
_CARD = f"background:#ffffff; border:1px solid {_BR}; border-radius:16px; box-shadow:{_SH1};"


def _halo(c):
    return f"0 0 0 4px {c}1A, 0 4px 12px {c}33"


def _echarts(opts: dict, h: int, cid: str) -> str:
    # Sanitizar json para evitar NaN no válidos
    opts_json = json.dumps(opts).replace('NaN', '0.0').replace('null', '0')
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var el=document.getElementById("{cid}");if(!el)return;'
        f'var c=echarts.init(el);'
        f'c.setOption({opts_json});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )


def bucket_runlife(days):
    if pd.isna(days) or days is None: return '< 2 años'
    try:
        years = float(days) / 365.25
        if years < 2: return '< 2 años'
        if years < 4: return '2–4 años'
        if years < 6: return '4–6 años'
        return '> 6 años'
    except Exception:
        return '< 2 años'


def _render_custom_table(df_table, title=""):
    """Renderiza una tabla ejecutiva rápida, ligera y con estilo nativo Parex."""
    if df_table is None or df_table.empty:
        st.info("Sin datos para mostrar.")
        return

    cols = list(df_table.columns)
    rows_html = ""
    for _, row in df_table.iterrows():
        cells_html = ""
        for c in cols:
            val = str(row[c])
            style = "padding: 8px 10px; font-size: 11.5px; border-bottom: 1px solid rgba(46,125,70,0.08);"
            if c in ('BOPD', 'RLE (d)', 'RL (d)', 'Efic.'):
                style += f" text-align: right; font-weight: 600; font-family: {_FS}; color: {_T};"
            elif c == 'Pozo':
                style += f" font-weight: 700; font-family: {_FS}; color: {_G2};"
            elif c in ('Estado', 'Alerta'):
                if 'FALLA' in val.upper():
                    badge = f'<span style="background:{_R2}; color:{_R}; font-weight:700; padding:2px 7px; border-radius:10px; border:1px solid {_R}40; font-size:9.5px;">{val}</span>'
                elif 'OK' in val.upper():
                    badge = f'<span style="background:{_G3}; color:{_G}; font-weight:700; padding:2px 7px; border-radius:10px; border:1px solid {_G}40; font-size:9.5px;">{val}</span>'
                else:
                    badge = f'<span style="background:{_Y2}; color:{_Y}; font-weight:700; padding:2px 7px; border-radius:10px; border:1px solid {_Y}40; font-size:9.5px;">{val}</span>'
                cells_html += f'<td style="{style} text-align:center;">{badge}</td>'
                continue
            else:
                style += f" font-family: {_FS}; color: {_T2};"
            cells_html += f'<td style="{style}">{val}</td>'
        rows_html += f"<tr>{cells_html}</tr>"

    headers_html = "".join([
        f'<th style="background:{_G3}; color:{_G2}; font-family:{_FS}; font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.6px; padding:8px 10px; border-bottom:1.5px solid {_BR}; text-align:{"right" if c in ("BOPD", "RLE (d)", "RL (d)", "Efic.") else ("center" if c in ("Estado", "Alerta") else "left")};">{c}</th>'
        for c in cols
    ])

    table_html = f"""
    <div style="{_CARD} padding:0; overflow:hidden; margin-top:4px;">
        <table style="width:100%; border-collapse:collapse; text-align:left;">
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


def render_tab_performance(df_bd_filtered, df_forma9_filtered, fecha_evaluacion):
    """Renderiza el módulo izquierdo de PERFORMANCE con simetría total a MTBF y Tablero."""
    fecha_eval = pd.Timestamp(fecha_evaluacion)
    fecha_eval_dt = fecha_eval.normalize()

    # ── 1. CARGA Y FILTRADO EXACTO (ALINEADO CON TABLERO E ÍNDICES) ───────────
    df_raw = st.session_state.get('df_bd_calculated')
    df_f9_raw = st.session_state.get('df_forma9_calculated')

    _filtros = {
        'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
        'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
        'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
        'PROVEEDOR': st.session_state.get('general_proveedor_filter', 'TODOS'),
        'NICK':      st.session_state.get('general_nick_filter',      'TODOS'),
    }

    if df_raw is not None:
        bd = df_raw.copy()
        EXCLUIDOS = {
            'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
            'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
            'MAPACHE/PERICO', 'MAPACHE-PERICO',
            'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
            'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
            'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE', 'TODOS'
        }
        for col_filter in ('ACTIVO', 'BLOQUE', 'CAMPO'):
            if col_filter in bd.columns and EXCLUIDOS:
                bd = bd[~bd[col_filter].astype(str).str.upper().str.strip().isin(EXCLUIDOS)]
        for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col in bd.columns:
                bd[col] = pd.to_datetime(bd[col], errors='coerce')
        bd = bd[bd['FECHA_RUN'].dt.normalize() <= fecha_eval_dt].copy()
        bd.loc[bd['FECHA_FALLA'].dt.normalize() > fecha_eval_dt, 'FECHA_FALLA'] = pd.NaT
        
        for col, val in _filtros.items():
            if val != 'TODOS' and col in bd.columns:
                bd = bd[bd[col] == val]
    else:
        bd = df_bd_filtered.copy() if df_bd_filtered is not None else pd.DataFrame()
        for col in ('FECHA_RUN', 'FECHA_FALLA', 'FECHA_PULL'):
            if col in bd.columns:
                bd[col] = pd.to_datetime(bd[col], errors='coerce')

    if df_f9_raw is not None:
        df_forma9_untr = df_f9_raw.copy()
        df_forma9_untr['FECHA_FORMA9'] = pd.to_datetime(df_forma9_untr['FECHA_FORMA9'], errors='coerce')
        pozos_en_resumen = bd['POZO'].astype(str).str.strip().unique() if 'POZO' in bd.columns else []
        df_forma9_untr = df_forma9_untr[df_forma9_untr['POZO'].astype(str).str.strip().isin(pozos_en_resumen)].copy()
    else:
        df_forma9_untr = df_forma9_filtered.copy() if df_forma9_filtered is not None else pd.DataFrame()
        if 'FECHA_FORMA9' in df_forma9_untr.columns:
            df_forma9_untr['FECHA_FORMA9'] = pd.to_datetime(df_forma9_untr['FECHA_FORMA9'], errors='coerce')

    # ── 2. PROCESAMIENTO DE PRODUCCIÓN Y POZOS ON ───────────────────────────
    try:
        if not df_forma9_untr.empty and 'FECHA_FORMA9' in df_forma9_untr.columns:
            df_month = df_forma9_untr[
                (df_forma9_untr['FECHA_FORMA9'].dt.year  == fecha_eval.year) &
                (df_forma9_untr['FECHA_FORMA9'].dt.month == fecha_eval.month)
            ].copy()
        else:
            df_month = pd.DataFrame()

        bopd_col = next((c for c in df_month.columns if any(k in str(c).upper() for k in ['BOPD', 'PETROLEO DIA', 'PETROLEO_DIA'])), None)
        dias_col = next((c for c in df_month.columns if 'DIAS' in str(c).upper()), None)
        mask_dias = (pd.to_numeric(df_month[dias_col], errors='coerce').fillna(0) > 0) if dias_col else pd.Series(True, index=df_month.index)
        
        fluid_cols = [c for c in df_month.columns if any(k in str(c).upper() for k in ['BOPD', 'BFPD', 'BWPD', 'PETROLEO', 'FLUIDO', 'AGUA'])]
        if fluid_cols:
            mask_fluid = pd.Series(False, index=df_month.index)
            for fc in fluid_cols:
                mask_fluid = mask_fluid | (pd.to_numeric(df_month[fc], errors='coerce').fillna(0) > 0)
        else:
            mask_fluid = pd.Series(True, index=df_month.index)

        df_on = df_month[mask_dias & mask_fluid].copy()
        pozos_validos = set(bd['POZO'].astype(str).str.strip().unique()) if 'POZO' in bd.columns else None
        if pozos_validos is not None and not df_on.empty:
            df_on = df_on[df_on['POZO'].astype(str).str.strip().isin(pozos_validos)].copy()

        if bopd_col and not df_on.empty:
            df_on[bopd_col] = pd.to_numeric(df_on[bopd_col], errors='coerce').fillna(0.0)
            df_on['POZO_STR'] = df_on['POZO'].astype(str).str.strip()
            df_sum = df_on.groupby('POZO_STR', as_index=False).agg({bopd_col: 'mean'})
            df_sum.rename(columns={'POZO_STR': 'POZO', bopd_col: 'BOPD'}, inplace=True)
        elif not df_on.empty:
            df_on['POZO_STR'] = df_on['POZO'].astype(str).str.strip()
            df_sum = pd.DataFrame({'POZO': df_on['POZO_STR'].unique(), 'BOPD': 0.0})
        else:
            df_sum = pd.DataFrame(columns=['POZO', 'BOPD'])

        # Pre-indexar BD para lookup por pozo
        bd['_P_NORM'] = bd['POZO'].astype(str).str.strip() if 'POZO' in bd.columns else pd.Series(dtype=str)
        bd_sorted = bd.sort_values('FECHA_RUN', ascending=False) if 'FECHA_RUN' in bd.columns else bd

        results = []
        for _, row in df_sum.iterrows():
            pozo = str(row['POZO']).strip()
            bopd = float(row.get('BOPD', 0.0) or 0.0)
            pozo_data = bd_sorted[bd_sorted['_P_NORM'] == pozo] if not bd.empty and '_P_NORM' in bd_sorted.columns else pd.DataFrame()
            if not pozo_data.empty:
                last = pozo_data.iloc[0]
                raw_rl = last.get('RUN LIFE')
                raw_rle = last.get('RUN_LIFE_EFECTIVO')
                rl = float(raw_rl) if pd.notna(raw_rl) and raw_rl is not None else 0.0
                rle = float(raw_rle) if pd.notna(raw_rle) and raw_rle is not None else rl
                if pd.isna(rle) or rle < 0: rle = 0.0
                if pd.isna(rl) or rl < 0: rl = 0.0

                als = str(last.get('ALS', 'N/A'))
                if als in ('nan', 'None', ''): als = 'N/A'
                prov = str(last.get('PROVEEDOR', 'N/A'))
                if prov in ('nan', 'None', ''): prov = 'N/A'

                falla = bool(pd.notna(last.get('FECHA_FALLA')))
                efic = round(bopd / (rle / 365.25), 1) if rle and rle > 0 else 0.0
                results.append({'POZO': pozo, 'BOPD': round(bopd, 1), 'RUN_LIFE': rl,
                                 'RLE': rle, 'ALS': als, 'PROVEEDOR': prov,
                                 'FALLA': falla, 'EFIC': efic, 'RANGO': bucket_runlife(rl)})
            else:
                results.append({'POZO': pozo, 'BOPD': round(bopd, 1), 'RUN_LIFE': 0.0,
                                 'RLE': 0.0, 'ALS': 'N/A', 'PROVEEDOR': 'N/A',
                                 'FALLA': False, 'EFIC': 0.0, 'RANGO': bucket_runlife(0)})

        df_perf = pd.DataFrame(results)

    except Exception as e:
        st.error(f"Error procesando performance: {e}")
        return

    if df_perf.empty:
        st.warning("No hay pozos ON con producción detectados para el mes seleccionado.")
        return

    total_bopd = float(df_perf['BOPD'].sum())
    avg_bopd   = float(df_perf['BOPD'].mean()) if len(df_perf) > 0 else 0.0
    avg_efic   = float(df_perf['EFIC'].mean()) if len(df_perf) > 0 else 0.0
    n_on       = len(df_perf)
    n_falla    = int(df_perf['FALLA'].sum())

    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"

    # ── 1. ENCABEZADO HERO SIMÉTRICO ──────────────────────────────────────────
    hero_html = f"""
    <style>
    @import url('{_FONTS_URL}');
    .tbl-hero-perf {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        background:
            radial-gradient(120% 180% at 0% 0%, rgba(76,164,106,0.38) 0%, rgba(19,118,89,0) 55%),
            linear-gradient(110deg, #137659 0%, #0d4e3b 50%, #137659 100%);
        border-radius: 14px;
        padding: 14px 20px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(19,118,89,0.13), 0 14px 34px rgba(19,118,89,0.22), inset 0 1px 0 rgba(255,255,255,0.16);
    }}
    .tbl-hero-brand {{ display: flex; align-items: center; gap: 14px; position: relative; z-index: 1; flex-shrink: 0; }}
    .tbl-hero-mark-perf {{
        width: 42px; height: 42px; border-radius: 11px;
        background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.24);
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.30), 0 4px 12px rgba(0,0,0,0.18);
    }}
    .tbl-hero-title {{ font-family: {_FN}; font-size: 19px; font-weight: 700; color: #ffffff; line-height: 1.15; }}
    .tbl-hero-dot-perf {{ width: 6px; height: 6px; border-radius: 50%; background: #6FD08C; box-shadow: 0 0 0 3px rgba(111,208,140,0.22); }}
    .tbl-hero-ctx {{ display: flex; align-items: stretch; position: relative; z-index: 1; flex: 1; justify-content: flex-end; }}
    .tbl-hero-item {{ padding: 0 14px; border-left: 1px solid rgba(255,255,255,0.15); display: flex; flex-direction: column; justify-content: center; gap: 2px; }}
    .tbl-hero-k {{ font-family: {_FS}; font-size: 8.5px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; color: rgba(255,255,255,0.55); }}
    .tbl-hero-v {{ font-family: {_FS}; font-size: 12px; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 6px; }}
    </style>
    <div class="tbl-hero-perf">
      <div class="tbl-hero-brand">
        <div class="tbl-hero-mark-perf">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 20V10M12 20V4M6 20v-6"/>
          </svg>
        </div>
        <div>
          <div class="tbl-hero-title">Producción y Eficiencia Operacional</div>
          <div style="font-family:{_FS}; font-size:11px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
            <div class="tbl-hero-dot-perf"></div>
            <span>Monitoreo de tasa de petróleo, longevidad y productividad por pozo</span>
          </div>
        </div>
      </div>
      <div class="tbl-hero-ctx">
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Corte Evaluación</span>
          <span class="tbl-hero-v">{fecha_eval.strftime('%d/%m/%Y')}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Filtros Activos</span>
          <span class="tbl-hero-v">{_activos_lbl}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Producción Neta</span>
          <span class="tbl-hero-v">{total_bopd:,.0f} BOPD</span>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── 2. FILA DE 3 KPIS HERO SIMÉTRICA ───────────────────────────────────────
    st.markdown(f"""
    <style>
    .perf-kpi-card {{
        {_CARD}
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 14px 12px;
        text-align: center;
        position: relative;
        transition: box-shadow 0.24s ease, transform 0.24s ease, border-color 0.24s ease;
    }}
    .perf-kpi-card:hover {{
        border-color: rgba(46,125,70,0.30);
        box-shadow: {_SH2};
        transform: translateY(-2px);
    }}
    .perf-kpi-icon {{
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 6px;
    }}
    .perf-kpi-icon.green {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%); box-shadow: {_halo(_G)}; }}
    .perf-kpi-icon.gold  {{ background: linear-gradient(160deg, #E0B44C 0%, {_Y} 100%); box-shadow: {_halo(_Y)}; }}
    .perf-kpi-icon.blue  {{ background: linear-gradient(160deg, #38BDF8 0%, {_B} 100%); box-shadow: {_halo(_B)}; }}

    .perf-kpi-lbl {{ font-family: {_FS}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
    .perf-kpi-val {{ font-family: {_FN}; font-size: 32px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
    .perf-kpi-sub {{ font-family: {_FS}; font-size: 10px; color: {_T2}; margin-top: 4px; }}
    .perf-kpi-badge {{
        font-family: {_FS}; font-size: 8.5px; font-weight: 700;
        padding: 2px 8px; border-radius: 12px; margin-top: 4px; display: inline-block;
        letter-spacing: 0.4px;
    }}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="perf-kpi-card">
            <div class="perf-kpi-icon green">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
            </div>
            <div class="perf-kpi-lbl">Pozos ON</div>
            <div class="perf-kpi-val" style="color:{_G};">{n_on}</div>
            <span class="perf-kpi-badge" style="background:{_G3}; color:{_G}; border:1px solid {_G}50;">● OPERATIVOS</span>
            <div class="perf-kpi-sub">Con producción de fluido > 0</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="perf-kpi-card">
            <div class="perf-kpi-icon gold">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="perf-kpi-lbl">BOPD Total</div>
            <div class="perf-kpi-val" style="color:{_Y};">{total_bopd:,.0f}</div>
            <span class="perf-kpi-badge" style="background:{_Y2}; color:{_Y}; border:1px solid {_Y}50;">▲ PRODUCCIÓN</span>
            <div class="perf-kpi-sub">Tasa acumulada mes actual</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="perf-kpi-card">
            <div class="perf-kpi-icon blue">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
            </div>
            <div class="perf-kpi-lbl">Eficiencia Prom.</div>
            <div class="perf-kpi-val" style="color:{_B};">{avg_efic:.1f}</div>
            <span class="perf-kpi-badge" style="background:{_B2}; color:{_B}; border:1px solid {_B}50;">◆ BOPD / AÑO</span>
            <div class="perf-kpi-sub">Promedio de productividad</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 3. GRÁFICA PRINCIPAL: SCATTER BOPD VS RUN LIFE EFECTIVO (340px) ──────
    als_colors = {'ESP': _G, 'PCP': _Y, 'BM': '#5C6B73', 'BH': _G2, 'EPCP': _Y}
    scatter_series = []
    for als_name, grp in df_perf.groupby('ALS'):
        scatter_data = []
        for _, r in grp.iterrows():
            estado_s = "FALLA" if r['FALLA'] else "ON"
            rle_val = float(r['RLE']) if pd.notna(r['RLE']) else 0.0
            bopd_val = float(r['BOPD']) if pd.notna(r['BOPD']) else 0.0
            rl_val = float(r['RUN_LIFE']) if pd.notna(r['RUN_LIFE']) else 0.0
            efic_val = float(r['EFIC']) if pd.notna(r['EFIC']) else 0.0

            scatter_data.append({
                "value": [rle_val, bopd_val],
                "name": str(r['POZO']),
                "tooltip_extra": f"{r['PROVEEDOR']} | RL: {rl_val:.0f}d | Efic: {efic_val:.1f} BOPD/año | {estado_s}",
                "itemStyle": {
                    "color": als_colors.get(str(als_name), _G),
                    "borderColor": _R if r['FALLA'] else als_colors.get(str(als_name), _G),
                    "borderWidth": 2.5 if r['FALLA'] else 0,
                    "opacity": 0.88
                }
            })
        scatter_series.append({
            "name": str(als_name), "type": "scatter",
            "data": scatter_data, "symbolSize": 10,
            "emphasis": {"itemStyle": {"shadowBlur": 12, "shadowColor": "rgba(0,0,0,0.25)"}}
        })

    # Línea de tendencia
    if len(df_perf) > 3:
        try:
            df_clean = df_perf[['RLE', 'BOPD']].dropna()
            df_clean = df_clean[(df_clean['RLE'] > 0) | (df_clean['BOPD'] > 0)]
            x_arr = df_clean['RLE'].to_numpy(dtype=float)
            y_arr = df_clean['BOPD'].to_numpy(dtype=float)
            if len(x_arr) > 2 and (x_arr.max() > x_arr.min()):
                coef = np.polyfit(x_arr, y_arr, 1)
                x_min, x_max = float(x_arr.min()), float(x_arr.max())
                scatter_series.append({
                    "name": "Tendencia", "type": "line",
                    "data": [[x_min, round(float(np.polyval(coef, x_min)), 1)],
                             [x_max, round(float(np.polyval(coef, x_max)), 1)]],
                    "lineStyle": {"type": "dashed", "color": _T2, "width": 1.5},
                    "itemStyle": {"color": _T2}, "symbol": "none",
                    "tooltip": {"show": False}
                })
        except Exception:
            pass

    scatter_opts = {
        "backgroundColor": "transparent",
        "title": {"text": "DISPERSIÓN: BOPD VS RUN LIFE EFECTIVO", "left": "center", "top": 8,
                  "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": _FS, "fontWeight": "800"},
                  "subtext": "Productividad por pozo vs longevidad efectiva",
                  "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": _FS}},
        "tooltip": {"trigger": "item", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                    "textStyle": {"color": _T, "fontFamily": _FS},
                    "formatter": "function(p){return '<b>'+p.data.name+'</b><br/>BOPD: <b>'+p.value[1]+'</b><br/>RLE: <b>'+p.value[0]+'d</b><br/>'+p.data.tooltip_extra;}"},
        "legend": {"bottom": 4, "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": _FS}, "icon": "circle"},
        "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "20%", "containLabel": True},
        "xAxis": {"type": "value", "name": "Run Life Efectivo (días)",
                  "nameTextStyle": {"color": _T2, "fontFamily": _FS, "fontSize": 9},
                  "axisLabel": {"color": _T2, "fontFamily": _FS, "fontSize": 8.5},
                  "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
        "yAxis": {"type": "value", "name": "BOPD",
                  "nameTextStyle": {"color": _T2, "fontSize": 9},
                  "axisLabel": {"color": _T2, "fontFamily": _FS, "fontSize": 8.5},
                  "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
        "series": scatter_series
    }
    components.html(_echarts(scatter_opts, 330, "perf-scatter"), height=340)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 4. GRÁFICA SECUNDARIA: APORTE POR RANGO DE RUN LIFE (270px) ───────────
    rl_brackets = ['< 2 años', '2–4 años', '4–6 años', '> 6 años']
    df_bracket = df_perf.groupby('RANGO').agg({'POZO': 'count', 'BOPD': 'sum'}).reindex(rl_brackets).fillna(0)
    bracket_colors = [_G, _G2, _Y, _R]
    bopd_map = df_bracket['BOPD'].to_dict()

    bopd_bracket_opts = {
        "backgroundColor": "transparent",
        "title": {"text": "PRODUCCIÓN POR RANGO DE RUN LIFE", "left": "center", "top": 8,
                  "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": _FS, "fontWeight": "800"},
                  "subtext": "Aporte de petróleo (BOPD) y conteo de pozos",
                  "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": _FS}},
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                    "textStyle": {"color": _T, "fontFamily": _FS},
                    "formatter": "{b}<br/>BOPD: <b>{c}</b>"},
        "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "22%", "containLabel": True},
        "xAxis": {"type": "category", "data": rl_brackets,
                  "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": _FS, "interval": 0}},
        "yAxis": {"type": "value", "name": "BOPD",
                  "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": _FS},
                  "axisLabel": {"color": _T2, "fontFamily": _FS, "fontSize": 8.5},
                  "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
        "series": [{
            "type": "bar",
            "data": [{"value": round(float(bopd_map.get(l, 0.0) or 0.0), 1),
                      "itemStyle": {"color": bracket_colors[i], "borderRadius": [5, 5, 0, 0]}}
                     for i, l in enumerate(rl_brackets)],
            "barWidth": "50%",
            "label": {"show": True, "position": "top", "color": _T2,
                      "fontFamily": _FS, "fontSize": 10, "fontWeight": "bold",
                      "formatter": "{c} BOPD"},
        }]
    }
    components.html(_echarts(bopd_bracket_opts, 260, "perf-bopd-bracket"), height=270)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA ACCIONABLE: TOP 5 PRODUCTORES (HUD MATCHING MTBF) ────────────
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem;"
        "margin-bottom:8px;'>🏆 Top 5 Pozos Productores (Mayor Aporte)</h6>",
        unsafe_allow_html=True
    )
    top5 = df_perf.nlargest(5, 'BOPD')[['POZO', 'BOPD', 'RLE', 'EFIC', 'ALS', 'FALLA']].copy()
    top5['ESTADO'] = top5['FALLA'].map({True: '⚠ FALLA', False: 'OK'})
    top5['BOPD'] = top5['BOPD'].apply(lambda x: f"{float(x):,.1f}")
    top5['RLE (d)'] = top5['RLE'].apply(lambda x: f"{float(x):.0f}d")
    top5['Efic.'] = top5['EFIC'].apply(lambda x: f"{float(x):.1f}")
    top5['Tec.'] = top5['ALS']
    top5['Estado'] = top5['ESTADO']
    _render_custom_table(top5[['Pozo', 'BOPD', 'RLE (d)', 'Efic.', 'Tec.', 'Estado']], title="Top 5 Productores")