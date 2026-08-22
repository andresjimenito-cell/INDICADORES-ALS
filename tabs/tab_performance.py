"""
tabs/tab_performance.py  —  Performance Operacional Simplificada
================================================================
Foco: decisiones rápidas — ¿qué pozos son eficientes y cuáles necesitan atención?
Estructura:
1. Hero compacto (alcance + producción total)
2. 3 KPIs hero (Pozos ON, BOPD Total, Eficiencia Promedio)
3. Scatter BOPD vs Run Life Efectivo (identifica pozos ineficientes)
4. Tabla accionable: Top productores + Bottom productores (alertas)
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from ui.styles import render_hud_table
from ui.theme import get_semantic_color

# ── Paleta Semántica (de theme.py) ─────────────────────────────────────────────
GREEN  = get_semantic_color("success")   # #137659
GOLD   = get_semantic_color("warning")   # #c09c2e
RED    = get_semantic_color("danger")    # #c62828
BLUE   = get_semantic_color("info")      # #0284c7
MUTED  = "#6b7a6f"
TEXT   = "#1f221e"
BG_CARD = "#ffffff"
BORDER = "rgba(19, 118, 89, 0.15)"

_FS  = "'Inter', 'Segoe UI', Calibri, Arial, sans-serif"
_FN  = "'Source Serif 4', Cambria, Georgia, serif"
_FONTS_URL = ("https://fonts.googleapis.com/css2?"
              "family=Inter:wght@400;500;600;700;800&"
              "family=Source+Serif+4:opsz,wght@8..60,600;8..60,700;8..60,900&display=swap")

_SHADOW = "0 1px 3px rgba(19,118,89,0.08), 0 4px 12px rgba(19,118,89,0.10)"
_SHADOW_H = "0 4px 16px rgba(19,118,89,0.15), 0 8px 24px rgba(19,118,89,0.18)"
_CARD = (f"background:#ffffff;border:1px solid {BORDER};border-radius:14px;box-shadow:{_SHADOW};")


def _echarts(opts: dict, h: int, cid: str) -> str:
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"));'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )


def bucket_runlife(days):
    if pd.isna(days): return 'N/A'
    years = days / 365.25
    if years < 2: return '< 2 años'
    if years < 4: return '2–4 años'
    if years < 6: return '4–6 años'
    return '> 6 años'


def render_tab_performance(df_bd_filtered, df_forma9_filtered, fecha_evaluacion):
    """Renderiza PERFORMANCE: 3 KPIs + 1 Scatter accionable + Tabla Top/Bottom."""
    fecha_eval = pd.to_datetime(fecha_evaluacion)

    # ── 1. PROCESAMIENTO ────────────────────────────────────────────────────────
    try:
        df_f9 = df_forma9_filtered.copy()
        df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9.get('FECHA_FORMA9'), errors='coerce')

        df_month = df_f9[
            (df_f9['FECHA_FORMA9'].dt.year  == fecha_eval.year) &
            (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)
        ].copy()

        bopd_col = next((c for c in df_month.columns if 'BOPD' in str(c).upper() or 'PETROLEO DIA' in str(c).upper() or 'PETROLEO_DIA' in str(c).upper()), None)

        if bopd_col:
            df_month[bopd_col] = pd.to_numeric(df_month[bopd_col], errors='coerce').fillna(0)
            df_on = df_month[df_month[bopd_col] > 0].copy()
            df_sum = df_on.groupby('POZO', as_index=False).agg({bopd_col: 'mean'})
            df_sum.rename(columns={bopd_col: 'BOPD'}, inplace=True)
        else:
            df_sum = pd.DataFrame(columns=['POZO', 'BOPD'])

        bd = df_bd_filtered.copy()
        bd['FECHA_RUN'] = pd.to_datetime(bd.get('FECHA_RUN'), errors='coerce')
        bd['FECHA_FALLA'] = pd.to_datetime(bd.get('FECHA_FALLA'), errors='coerce')

        results = []
        for _, row in df_sum.iterrows():
            pozo, bopd = row['POZO'], row['BOPD']
            pozo_data = bd[bd['POZO'] == pozo].sort_values('FECHA_RUN', ascending=False)
            if not pozo_data.empty:
                last = pozo_data.iloc[0]
                rl   = last.get('RUN LIFE', 0) or 0
                rle  = last.get('RUN_LIFE_EFECTIVO', rl) or rl
                als  = str(last.get('ALS', 'N/A'))
                prov = str(last.get('PROVEEDOR', 'N/A'))
                falla = pd.notna(last.get('FECHA_FALLA'))
                efic = round(bopd / (rle / 365.25), 1) if rle and rle > 0 else 0
                results.append({'POZO': pozo, 'BOPD': round(bopd, 1), 'RUN_LIFE': rl,
                                 'RLE': rle, 'ALS': als, 'PROVEEDOR': prov,
                                 'FALLA': falla, 'EFIC': efic, 'RANGO': bucket_runlife(rl)})

        df_perf = pd.DataFrame(results)

    except Exception as e:
        st.error(f"Error procesando performance: {e}")
        return

    if df_perf.empty:
        st.warning("No hay pozos ON detectados para el mes de evaluación seleccionado.")
        return

    # ── 2. HERO COMPACTO ────────────────────────────────────────────────────────
    _filtros = {
        'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
        'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
        'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
    }
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"

    total_bopd = df_perf['BOPD'].sum()
    avg_bopd   = df_perf['BOPD'].mean()
    avg_efic   = df_perf['EFIC'].mean()
    n_on       = len(df_perf)
    n_falla    = int(df_perf['FALLA'].sum())

    st.markdown(f"""
    <style>
    @import url('{_FONTS_URL}');
    .perf-hero {{
        display: flex; align-items: center; justify-content: space-between; gap: 16px;
        background: linear-gradient(135deg, {GREEN} 0%, #0a4d34 100%);
        border-radius: 12px; padding: 12px 20px; margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(19,118,89,0.15), 0 8px 24px rgba(19,118,89,0.18);
    }}
    .perf-hero-left {{ display: flex; align-items: center; gap: 14px; flex: 1; }}
    .perf-hero-icon {{ width: 38px; height: 38px; border-radius: 10px;
        background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
        display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
    .perf-hero-title {{ font-family: {_FN}; font-size: 16px; font-weight: 700; color: #fff; line-height: 1.2; }}
    .perf-hero-sub {{ font-family: {_FS}; font-size: 10px; color: rgba(255,255,255,0.75); margin-top: 2px; }}
    .perf-hero-right {{ display: flex; gap: 24px; align-items: center; flex-wrap: wrap; }}
    .perf-hero-item {{ text-align: right; }}
    .perf-hero-k {{ font-family: {_FS}; font-size: 8.5px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: rgba(255,255,255,0.6); }}
    .perf-hero-v {{ font-family: {_FS}; font-size: 14px; font-weight: 700; color: #fff; }}
    </style>
    <div class="perf-hero">
      <div class="perf-hero-left">
        <div class="perf-hero-icon">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2.2">
            <path d="M18 20V10M12 20V4M6 20v-6"/>
          </svg>
        </div>
        <div>
          <div class="perf-hero-title">Producción y Eficiencia — Pozos ON</div>
          <div class="perf-hero-sub">{fecha_eval.strftime('%B %Y').capitalize()} · {_activos_lbl}</div>
        </div>
      </div>
      <div class="perf-hero-right">
        <div class="perf-hero-item"><div class="perf-hero-k">Producción Total</div><div class="perf-hero-v">{total_bopd:,.0f} BOPD</div></div>
        <div class="perf-hero-item"><div class="perf-hero-k">Pozos Activos</div><div class="perf-hero-v">{n_on}</div></div>
        <div class="perf-hero-item"><div class="perf-hero-k">En Falla</div><div class="perf-hero-v" style="color:#ffcccc;">{n_falla}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. 3 KPIs HERO ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <style>
    .kpi3 {{ {_CARD} display:flex; flex-direction:column; align-items:center; justify-content:center; padding:16px 12px; text-align:center; transition:box-shadow .2s, transform .2s, border-color .2s; }}
    .kpi3:hover {{ border-color:{GREEN}; box-shadow:{_SHADOW_H}; transform:translateY(-2px); }}
    .kpi3-icon {{ width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:8px; }}
    .kpi3-icon.green {{ background:linear-gradient(135deg, #4CA46A, {GREEN}); box-shadow:0 0 0 4px rgba(19,118,89,0.12), 0 4px 12px rgba(19,118,89,0.25); }}
    .kpi3-icon.gold {{ background:linear-gradient(135deg, #E0B44C, {GOLD}); box-shadow:0 0 0 4px rgba(192,156,46,0.12), 0 4px 12px rgba(192,156,46,0.25); }}
    .kpi3-icon.blue {{ background:linear-gradient(135deg, #4FA3E0, {BLUE}); box-shadow:0 0 0 4px rgba(2,132,199,0.12), 0 4px 12px rgba(2,132,199,0.25); }}
    .kpi3-lbl {{ font-family:{_FS}; font-size:9.5px; font-weight:700; letter-spacing:0.8px; text-transform:uppercase; color:{MUTED}; margin-bottom:4px; }}
    .kpi3-val {{ font-family:{_FN}; font-size:28px; font-weight:700; line-height:1.05; letter-spacing:-0.5px; }}
    .kpi3-sub {{ font-family:{_FS}; font-size:9px; color:{MUTED}; margin-top:4px; }}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi3">
            <div class="kpi3-icon green"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2.2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg></div>
            <div class="kpi3-lbl">Pozos ON</div>
            <div class="kpi3-val" style="color:{GREEN};">{n_on}</div>
            <div class="kpi3-sub">Con producción > 0 BOPD</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi3">
            <div class="kpi3-icon gold"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2.2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg></div>
            <div class="kpi3-lbl">BOPD Total</div>
            <div class="kpi3-val" style="color:{GOLD};">{total_bopd:,.0f}</div>
            <div class="kpi3-sub">Producción mes actual</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi3">
            <div class="kpi3-icon blue"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2.2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg></div>
            <div class="kpi3-lbl">Eficiencia Prom.</div>
            <div class="kpi3-val" style="color:{BLUE};">{avg_efic:.1f}</div>
            <div class="kpi3-sub">BOPD / año de vida útil</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── 4. SCATTER BOPD vs RLE (PRINCIPAL — ACCIONABLE) ────────────────────────
    st.markdown(f"""
    <h6 style="color:{GREEN}; font-family:{_FS}; font-weight:800; letter-spacing:0.6px; text-transform:uppercase; font-size:0.7rem; margin-bottom:8px;">
        Pozos: Eficiencia vs Longevidad — ¿Qué pozos producen bien por su vida útil?
    </h6>
    """, unsafe_allow_html=True)

    als_colors = {'ESP': GREEN, 'PCP': GOLD, 'BM': '#5C6B73', 'BH': '#095139', 'EPCP': GOLD}
    scatter_series = []
    for als_name, grp in df_perf.groupby('ALS'):
        scatter_data = []
        for _, r in grp.iterrows():
            estado_s = "FALLA" if r['FALLA'] else "ON"
            scatter_data.append({
                "value": [float(r['RLE']), float(r['BOPD'])],
                "name": r['POZO'],
                "tooltip_extra": f"{r['PROVEEDOR']} | RL: {r['RUN_LIFE']:.0f}d | Efic: {r['EFIC']:.1f} BOPD/año | {estado_s}",
                "itemStyle": {
                    "color": als_colors.get(str(als_name), GREEN),
                    "borderColor": RED if r['FALLA'] else als_colors.get(str(als_name), GREEN),
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
        df_clean = df_perf[['RLE', 'BOPD']].dropna()
        x_arr = df_clean['RLE'].to_numpy(dtype=float)
        y_arr = df_clean['BOPD'].to_numpy(dtype=float)
        if len(x_arr) > 0:
            coef = np.polyfit(x_arr, y_arr, 1)
            x_min, x_max = float(x_arr.min()), float(x_arr.max())
            scatter_series.append({
                "name": "Tendencia", "type": "line",
                "data": [[x_min, round(float(np.polyval(coef, x_min)), 1)],
                         [x_max, round(float(np.polyval(coef, x_max)), 1)]],
                "lineStyle": {"type": "dashed", "color": MUTED, "width": 1.5},
                "itemStyle": {"color": MUTED}, "symbol": "none",
                "tooltip": {"show": False}
            })

    scatter_opts = {
        "backgroundColor": "transparent",
        "tooltip": {"trigger": "item", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": BORDER,
                    "textStyle": {"color": TEXT, "fontFamily": _FS},
                    "formatter": "function(p){return '<b>'+p.data.name+'</b><br/>BOPD: <b>'+p.value[1]+'</b><br/>RLE: <b>'+p.value[0]+'d</b><br/>'+p.data.tooltip_extra;}"},
        "legend": {"bottom": 4, "textStyle": {"color": MUTED, "fontSize": 9, "fontFamily": _FS}, "icon": "circle"},
        "grid": {"left": "4%", "right": "4%", "bottom": "16%", "top": "6%", "containLabel": True},
        "xAxis": {"type": "value", "name": "Run Life Efectivo (días)",
                  "nameTextStyle": {"color": MUTED, "fontFamily": _FS, "fontSize": 9},
                  "axisLabel": {"color": MUTED, "fontFamily": _FS, "fontSize": 8.5},
                  "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
        "yAxis": {"type": "value", "name": "BOPD",
                  "nameTextStyle": {"color": MUTED, "fontSize": 9},
                  "axisLabel": {"color": MUTED, "fontFamily": _FS, "fontSize": 8.5},
                  "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
        "series": scatter_series
    }
    components.html(_echarts(scatter_opts, 380, "perf-scatter"), height=390)

    # ── 5. TABLA: TOP 5 PRODUCTORES + BOTTOM 5 (ALERTAS) ────────────────────────
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    
    col_top, col_bottom = st.columns(2, gap="medium")
    
    with col_top:
        st.markdown(f"""
        <h6 style="color:{GREEN}; font-family:{_FS}; font-weight:800; letter-spacing:0.6px; text-transform:uppercase; font-size:0.7rem; margin-bottom:6px;">
            Top 5 Productores
        </h6>""", unsafe_allow_html=True)
        top5 = df_perf.nlargest(5, 'BOPD')[['POZO', 'BOPD', 'RLE', 'EFIC', 'ALS', 'FALLA']].copy()
        top5['ESTADO'] = top5['FALLA'].map({True: '⚠ FALLA', False: 'OK'})
        top5 = top5.rename(columns={'POZO': 'Pozo', 'BOPD': 'BOPD', 'RLE': 'RLE (d)', 'EFIC': 'Efic.', 'ALS': 'Tec.', 'ESTADO': 'Estado'})
        render_hud_table(top5[['Pozo', 'BOPD', 'RLE (d)', 'Efic.', 'Tec.', 'Estado']])

    with col_bottom:
        st.markdown(f"""
        <h6 style="color:{RED}; font-family:{_FS}; font-weight:800; letter-spacing:0.6px; text-transform:uppercase; font-size:0.7rem; margin-bottom:6px;">
            Bottom 5 — Revisar
        </h6>""", unsafe_allow_html=True)
        bottom5 = df_perf.nsmallest(5, 'EFIC')[['POZO', 'BOPD', 'RLE', 'EFIC', 'ALS', 'FALLA']].copy()
        bottom5['ESTADO'] = bottom5['FALLA'].map({True: '⚠ FALLA', False: 'BAJA EFIC.'})
        bottom5 = bottom5.rename(columns={'POZO': 'Pozo', 'BOPD': 'BOPD', 'RLE': 'RLE (d)', 'EFIC': 'Efic.', 'ALS': 'Tec.', 'ESTADO': 'Alerta'})
        render_hud_table(bottom5[['Pozo', 'BOPD', 'RLE (d)', 'Efic.', 'Tec.', 'Alerta']])

    # ── 6. INSIGHT AUTOMÁTICO ───────────────────────────────────────────────────
    if n_falla > 0 or avg_efic < 50:
        st.markdown(f"""
        <div style="background:rgba(192,156,46,0.08); border-left:4px solid {GOLD}; padding:12px 16px; border-radius:8px; margin-top:16px;">
            <div style="color:{GOLD}; font-family:{_FS}; font-size:0.65rem; font-weight:800; letter-spacing:1px; text-transform:uppercase;">Insight</div>
            <div style="color:{TEXT}; font-size:0.85rem; margin-top:4px; line-height:1.5;">
                {"⚠ " + str(n_falla) + " pozo(s) en falla. " if n_falla > 0 else ""}
                {"Eficiencia promedio baja (" + f"{avg_efic:.1f}" + " BOPD/año). " if avg_efic < 50 else ""}
                Revisar pozos en <b>Bottom 5</b> para intervención o workover.
            </div>
        </div>
        """, unsafe_allow_html=True)