"""
tabs/tab_mtbf.py  —  Confiabilidad y Longevidad Operativa (MTBF / RL)
====================================================================
Módulo derecho de la pestaña Performance: foco en confiabilidad, MTBF y supervivencia de fondo.
Estructura simétrica alineada con tab_performance.py:
1. Encabezado Hero Ejecutivo (Confiabilidad & Longevidad)
2. 3 KPIs Hero (TMEF Global, RL Promedio, RL Efectivo)
3. Gráfica Principal (Curva de Supervivencia Kaplan-Meier — 340px)
4. Gráfica Secundaria (Distribución de Corridas por Run Life — 270px)
5. Tabla Accionable (Bottom 5 Pozos en Alerta / Menor Longevidad)
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from core.mtbf import calcular_mtbf
from core.run_life_efectivo import calcular_run_life_efectivo
from ui.styles import render_hud_table

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
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"));'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )


def _kaplan_meier(df_bd):
    """Calcula curvas de supervivencia Kaplan-Meier por tipo de ALS."""
    if df_bd is None or df_bd.empty or 'RUN LIFE' not in df_bd.columns:
        return {}

    als_col = next((c for c in ('ALS', 'SISTEMA_ALS', 'TIPO_ALS') if c in df_bd.columns), None)
    if not als_col:
        return {}

    palette = {'ESP': _G, 'PCP': _Y, 'BM': '#5C6B73', 'BH': _G2, 'EPCP': _Y}
    curves = {}

    for als, grp in df_bd.groupby(als_col):
        als_str = str(als).strip().upper()
        if not als_str or als_str in ('NAN', 'NONE', 'N/A'):
            continue

        times = pd.to_numeric(grp['RUN LIFE'], errors='coerce').dropna().values
        if len(times) < 2:
            continue

        events = (grp['FECHA_FALLA'].notna() if 'FECHA_FALLA' in grp.columns
                  else pd.Series([True] * len(grp))).values[:len(times)]

        order = np.argsort(times)
        t_sorted = times[order]
        e_sorted = np.array(events)[order]

        unique_t, counts = np.unique(t_sorted, return_counts=True)
        surv = 1.0
        n_at_risk = len(t_sorted)
        x_vals = [0]
        y_vals = [100.0]

        for ut in unique_t:
            mask_t = (t_sorted == ut)
            d_i = np.sum(e_sorted[mask_t])
            if n_at_risk > 0:
                surv *= (1.0 - d_i / n_at_risk)
            x_vals.append(float(ut))
            y_vals.append(round(surv * 100.0, 1))
            n_at_risk -= len(mask_t)

        curves[als_str] = {
            'x': x_vals,
            'y': y_vals,
            'color': palette.get(als_str, _G)
        }

    return curves


def render_tab_mtbf(df_bd_filtered, df_forma9_filtered, fecha_evaluacion,
                    verificaciones_filtered=None, selected_activo="TODOS"):
    """Renderiza el módulo derecho de PERFORMANCE con simetría total a Producción."""
    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)

    # ── 1. CÁLCULOS BASE DE CONFIABILIDAD ────────────────────────────────────
    try:
        mtbf_global, step_df = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
    except Exception:
        mtbf_global, step_df = 0, pd.DataFrame()

    mtbf_efectivo_global = 0
    if df_bd_filtered is not None and not df_bd_filtered.empty:
        try:
            mtbf_efectivo_global, _ = calcular_mtbf(df_bd_filtered, fecha_evaluacion, col_life='RUN_LIFE_EFECTIVO')
        except Exception:
            pass

    rl_total = df_bd_filtered['RUN LIFE'].mean() if df_bd_filtered is not None and not df_bd_filtered.empty and 'RUN LIFE' in df_bd_filtered.columns else 0
    rl_efec = 0
    try:
        rl_efec, _ = calcular_run_life_efectivo(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
    except Exception:
        pass

    _filtros = {
        'ACTIVO': st.session_state.get('general_activo_filter', 'TODOS'),
        'BLOQUE': st.session_state.get('general_bloque_filter', 'TODOS'),
        'CAMPO':  st.session_state.get('general_campo_filter',  'TODOS'),
        'ALS':    st.session_state.get('general_als_filter',    'TODOS'),
    }
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"

    # ── 1. ENCABEZADO HERO SIMÉTRICO ──────────────────────────────────────────
    hero_html = f"""
    <style>
    @import url('{_FONTS_URL}');
    .tbl-hero-mtbf {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        background:
            radial-gradient(120% 180% at 0% 0%, rgba(76,164,106,0.38) 0%, rgba(31,70,32,0) 55%),
            linear-gradient(110deg, #1F4620 0%, #17381A 50%, #1F4620 100%);
        border-radius: 14px;
        padding: 14px 20px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(31,70,32,0.13), 0 14px 34px rgba(31,70,32,0.22), inset 0 1px 0 rgba(255,255,255,0.16);
    }}
    .tbl-hero-brand {{ display: flex; align-items: center; gap: 14px; position: relative; z-index: 1; flex-shrink: 0; }}
    .tbl-hero-mark-mtbf {{
        width: 42px; height: 42px; border-radius: 11px;
        background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.24);
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.30), 0 4px 12px rgba(0,0,0,0.18);
    }}
    .tbl-hero-title {{ font-family: {_FN}; font-size: 19px; font-weight: 700; color: #ffffff; line-height: 1.15; }}
    .tbl-hero-dot-mtbf {{ width: 6px; height: 6px; border-radius: 50%; background: #6FD08C; box-shadow: 0 0 0 3px rgba(111,208,140,0.22); }}
    .tbl-hero-ctx {{ display: flex; align-items: stretch; position: relative; z-index: 1; flex: 1; justify-content: flex-end; }}
    .tbl-hero-item {{ padding: 0 14px; border-left: 1px solid rgba(255,255,255,0.15); display: flex; flex-direction: column; justify-content: center; gap: 2px; }}
    .tbl-hero-k {{ font-family: {_FS}; font-size: 8.5px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; color: rgba(255,255,255,0.55); }}
    .tbl-hero-v {{ font-family: {_FS}; font-size: 12px; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 6px; }}
    </style>
    <div class="tbl-hero-mtbf">
      <div class="tbl-hero-brand">
        <div class="tbl-hero-mark-mtbf">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        </div>
        <div>
          <div class="tbl-hero-title">Confiabilidad & Longevidad (MTBF / RL)</div>
          <div style="font-family:{_FS}; font-size:11px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
            <div class="tbl-hero-dot-mtbf"></div>
            <span>Tiempo medio entre fallas, longevidad y supervivencia de fondo</span>
          </div>
        </div>
      </div>
      <div class="tbl-hero-ctx">
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Corte Evaluación</span>
          <span class="tbl-hero-v">{fecha_eval_dt.strftime('%d/%m/%Y')}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Filtros Activos</span>
          <span class="tbl-hero-v">{_activos_lbl}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">TMEF Global</span>
          <span class="tbl-hero-v">{mtbf_global:.0f} días</span>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── 2. FILA DE 3 KPIS HERO SIMÉTRICA ───────────────────────────────────────
    st.markdown(f"""
    <style>
    .mtbf-kpi-card {{
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
    .mtbf-kpi-card:hover {{
        border-color: rgba(46,125,70,0.30);
        box-shadow: {_SH2};
        transform: translateY(-2px);
    }}
    .mtbf-kpi-icon {{
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 6px;
    }}
    .mtbf-kpi-icon.green {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%); box-shadow: {_halo(_G)}; }}
    .mtbf-kpi-icon.gold  {{ background: linear-gradient(160deg, #E0B44C 0%, {_Y} 100%); box-shadow: {_halo(_Y)}; }}
    .mtbf-kpi-icon.blue  {{ background: linear-gradient(160deg, #38BDF8 0%, {_B} 100%); box-shadow: {_halo(_B)}; }}

    .mtbf-kpi-lbl {{ font-family: {_FS}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
    .mtbf-kpi-val {{ font-family: {_FN}; font-size: 32px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
    .mtbf-kpi-sub {{ font-family: {_FS}; font-size: 10px; color: {_T2}; margin-top: 4px; }}
    .mtbf-kpi-badge {{
        font-family: {_FS}; font-size: 8.5px; font-weight: 700;
        padding: 2px 8px; border-radius: 12px; margin-top: 4px; display: inline-block;
        letter-spacing: 0.4px;
    }}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="mtbf-kpi-card">
            <div class="mtbf-kpi-icon green">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="mtbf-kpi-lbl">TMEF Global</div>
            <div class="mtbf-kpi-val" style="color:{_G};">{mtbf_global:.0f}<span style="font-size:16px;">d</span></div>
            <span class="mtbf-kpi-badge" style="background:{_G3}; color:{_G}; border:1px solid {_G}50;">● OPERATIVO</span>
            <div class="mtbf-kpi-sub">Tiempo Medio Entre Fallas</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="mtbf-kpi-card">
            <div class="mtbf-kpi-icon gold">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
            </div>
            <div class="mtbf-kpi-lbl">RL Promedio</div>
            <div class="mtbf-kpi-val" style="color:{_Y};">{rl_total:.0f}<span style="font-size:16px;">d</span></div>
            <span class="mtbf-kpi-badge" style="background:{_Y2}; color:{_Y}; border:1px solid {_Y}50;">▲ LONGEVIDAD</span>
            <div class="mtbf-kpi-sub">Días promedio en pozo</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="mtbf-kpi-card">
            <div class="mtbf-kpi-icon blue">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
            </div>
            <div class="mtbf-kpi-lbl">RL Efectivo</div>
            <div class="mtbf-kpi-val" style="color:{_B};">{rl_efec:.0f}<span style="font-size:16px;">d</span></div>
            <span class="mtbf-kpi-badge" style="background:{_B2}; color:{_B}; border:1px solid {_B}50;">◆ REAL FORMA 9</span>
            <div class="mtbf-kpi-sub">Días reales trabajados</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 3. GRÁFICA PRINCIPAL: CURVA DE SUPERVIVENCIA KAPLAN-MEIER (340px) ─────
    km_curves = _kaplan_meier(df_bd_filtered) if df_bd_filtered is not None and not df_bd_filtered.empty else {}
    if km_curves:
        km_series = []
        for als, curve in km_curves.items():
            km_series.append({
                "name": als, "type": "line", "smooth": False,
                "step": "end",
                "data": [[x, y] for x, y in zip(curve['x'], curve['y'])],
                "itemStyle": {"color": curve['color']},
                "lineStyle": {"width": 2.5, "color": curve['color']},
                "symbol": "none",
                "areaStyle": {"color": f"{curve['color']}0F"}
            })
        km_series.append({
            "name": "50% supervivencia", "type": "line",
            "data": [[0, 50], [max(max(c['x']) for c in km_curves.values()), 50]],
            "lineStyle": {"type": "dashed", "color": _T2, "width": 1.5},
            "itemStyle": {"color": _T2}, "symbol": "none",
            "tooltip": {"show": False}
        })
        km_opts = {
            "backgroundColor": "transparent",
            "title": {"text": "CURVA DE SUPERVIVENCIA (KAPLAN-MEIER)", "left": "center", "top": 8,
                      "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": _FS, "fontWeight": "800"},
                      "subtext": "Probabilidad de supervivencia por tecnología ALS",
                      "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": _FS}},
            "tooltip": {"trigger": "axis",
                        "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                        "textStyle": {"color": _T, "fontFamily": _FS},
                        "formatter": "function(p){return p.map(s=>`${s.seriesName}: <b>${s.value[1]}%</b>`).join('<br/>');}"},
            "legend": {"bottom": 4, "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": _FS}, "icon": "circle"},
            "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "20%", "containLabel": True},
            "xAxis": {"type": "value", "name": "Días de Operación",
                      "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": _FS},
                      "axisLabel": {"color": _T2, "fontFamily": _FS, "fontSize": 8.5},
                      "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
            "yAxis": {"type": "value", "name": "Supervivencia %", "min": 0, "max": 100,
                      "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": _FS},
                      "axisLabel": {"formatter": "{value}%", "color": _T2, "fontFamily": _FS, "fontSize": 8.5},
                      "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
            "series": km_series
        }
        components.html(_echarts(km_opts, 330, "mtbf-km"), height=340)
    else:
        st.info("Insuficientes datos para calcular curvas de supervivencia.")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 4. GRÁFICA SECUNDARIA: DISTRIBUCIÓN DE CORRIDAS POR RUN LIFE (270px) ──
    if df_bd_filtered is not None and not df_bd_filtered.empty and 'RUN LIFE' in df_bd_filtered.columns:
        rl_vals = df_bd_filtered['RUN LIFE'].dropna()
        bins    = [0, 90, 365, 730, 1460, float('inf')]
        labels  = ['< 90d\n(Crítico)', '90–365d\n(Prematuro)', '1–2 años\n(Normal)',
                   '2–4 años\n(Bueno)', '> 4 años\n(Óptimo)']
        bin_colors = [_R, _Y, '#5C6B73', _G, _G2]
        counts = pd.cut(rl_vals, bins=bins, labels=labels).value_counts().reindex(labels).fillna(0).astype(int)

        hist_opts = {
            "backgroundColor": "transparent",
            "title": {"text": "DISTRIBUCIÓN DE CORRIDAS (RUN LIFE)", "left": "center", "top": 8,
                      "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": _FS, "fontWeight": "800"},
                      "subtext": "Clasificación según longevidad en pozo",
                      "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": _FS}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                        "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                        "textStyle": {"color": _T, "fontFamily": _FS},
                        "formatter": "{b}<br/>Corridas: <b>{c}</b>"},
            "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "22%", "containLabel": True},
            "xAxis": {"type": "category", "data": labels,
                      "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": _FS, "interval": 0}},
            "yAxis": {"type": "value", "name": "Corridas",
                      "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": _FS},
                      "axisLabel": {"color": _T2, "fontFamily": _FS, "fontSize": 8.5},
                      "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
            "series": [{
                "type": "bar",
                "data": [{"value": int(counts[l]), "itemStyle": {"color": bin_colors[i], "borderRadius": [5, 5, 0, 0]}} for i, l in enumerate(labels)],
                "barWidth": "50%",
                "label": {"show": True, "position": "top", "color": _T2,
                          "fontFamily": _FS, "fontSize": 10, "fontWeight": "bold",
                          "formatter": "{c} corridas"},
            }]
        }
        components.html(_echarts(hist_opts, 260, "mtbf-hist"), height=270)
    else:
        st.info("Sin datos de Run Life disponibles.")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA ACCIONABLE: BOTTOM 5 / POZOS EN ALERTA (HUD MATCHING TOP 5) ──
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem;"
        "margin-bottom:8px;'>⚠️ Bottom 5 Pozos — Oportunidad de Optimización / Alerta</h6>",
        unsafe_allow_html=True
    )
    if df_bd_filtered is not None and not df_bd_filtered.empty and 'RUN LIFE' in df_bd_filtered.columns:
        df_rec = df_bd_filtered.sort_values('FECHA_RUN', ascending=False).copy()
        bottom5 = df_rec.nsmallest(5, 'RUN LIFE')[['POZO', 'RUN LIFE', 'ALS', 'FECHA_FALLA', 'PROVEEDOR']].copy()
        bottom5['ESTADO'] = bottom5['FECHA_FALLA'].apply(lambda x: '⚠ FALLA' if pd.notna(x) else 'LONGEVIDAD BAJA')
        bottom5['RUN LIFE'] = bottom5['RUN LIFE'].apply(lambda x: f"{x:.0f}d" if pd.notna(x) else "0d")
        bottom5 = bottom5.rename(columns={'POZO': 'Pozo', 'RUN LIFE': 'RL (d)', 'ALS': 'Tec.', 'PROVEEDOR': 'Prov.', 'ESTADO': 'Alerta'})
        render_hud_table(bottom5[['Pozo', 'RL (d)', 'Tec.', 'Prov.', 'Alerta']])
    else:
        st.info("No hay datos para la tabla de eventos.")
