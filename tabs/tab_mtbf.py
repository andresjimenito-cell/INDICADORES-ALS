"""
tabs/tab_mtbf.py  —  v4.2 Análisis de Confiabilidad y Performance Premium
========================================================================
Estética ejecutiva unificada con tab_tablero (Parex Industrial UI):
1. Hero Header ejecutivo con alcance y metadata de confiabilidad.
2. Fila de KPIs de 3 capas con tipografía Source Serif 4, halos y badges de meta.
3. Histograma de distribución Run Life (bins de riesgo con bordes redondeados).
4. Curva de Supervivencia (Kaplan-Meier) por tecnología ALS con áreas degradadas.
5. Comparativa MTBF vs Meta por Activo y tendencia de longevidad.
6. Tabla detallada de eventos con DataTables.
"""

import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go_fig
from data.config import COLOR_PRINCIPAL
from core.mtbf import calcular_mtbf
from core.calculations import calcular_run_life_efectivo, generar_historico_run_life
from ui.styles import render_hud_table

# ── Paleta Corporativa Parex ─────────────────────────────────────────────────
_G   = "#2E7D46"        # Verde principal
_G2  = "#1F4620"        # Verde oscuro
_G3  = "#EEF3EA"        # Verde muy claro (fondo)
_R   = "#C0392B"        # Rojo falla
_R2  = "#FBE8E6"        # Rojo claro fondo
_Y   = "#C98A2C"        # Dorado acento
_Y2  = "#FDF6E9"        # Dorado fondo
_T   = "#262626"        # Texto oscuro
_T2  = "#707070"        # Texto suave
_W   = "#ffffff"
_N   = "#223A5E"        # Azul petróleo
_BR  = "#DCE2D8"        # Borde hairline de tarjeta
_BG  = "#F7F8F5"        # Fondo tenue

_FS  = "'Inter', 'Segoe UI', Calibri, Arial, sans-serif"
_FN  = "'Source Serif 4', Cambria, Georgia, 'Times New Roman', serif"
_FONTS_URL = ("https://fonts.googleapis.com/css2?"
              "family=Inter:wght@400;500;600;700;800&"
              "family=Source+Serif+4:opsz,wght@8..60,600;8..60,700;8..60,900&display=swap")

_SH1 = ("0 1px 2px rgba(31,70,32,0.05), 0 4px 12px rgba(126,143,124,0.13), "
        "inset 0 1px 0 rgba(255,255,255,0.9)")
_SH2 = ("0 2px 5px rgba(31,70,32,0.07), 0 14px 32px rgba(126,143,124,0.22), "
        "inset 0 1px 0 rgba(255,255,255,0.9)")

_CARD = (f"background:linear-gradient(180deg,#ffffff 0%,#FCFDFA 100%);"
         f"border:1px solid {_BR};border-radius:13px;box-shadow:{_SH1};")

META_MTBF = 2190   # días
META_RL   = 1500   # días


def _halo(color):
    """Anillo suave + sombra proyectada bajo un icono circular."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return (f"0 0 0 4px rgba({r},{g},{b},0.10), 0 4px 10px rgba({r},{g},{b},0.30), "
            f"inset 0 1px 0 rgba(255,255,255,0.28)")


def _echarts(opts: dict, h: int, cid: str) -> str:
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;{_CARD}overflow:hidden;box-sizing:border-box;"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"),null);'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )


def _kaplan_meier(df_bd):
    """Calcula la curva de supervivencia simplificada por tecnología ALS."""
    curves = {}
    als_list = ['ESP', 'PCP', 'BM', 'BH', 'EPCP'] if 'ALS' in df_bd.columns else ['GLOBAL']
    colors_map = {'ESP': _G, 'PCP': _Y, 'BM': '#5C6B73', 'BH': _G2, 'EPCP': '#C98A2C', 'GLOBAL': _G}

    for als in als_list:
        if 'ALS' in df_bd.columns:
            sub = df_bd[df_bd['ALS'].astype(str).str.strip() == als].copy()
        else:
            sub = df_bd.copy()
        if len(sub) < 3:
            continue
        ended = sub[sub['FECHA_FALLA'].notna() | sub['FECHA_PULL'].notna()].copy()
        if ended.empty:
            continue
        rl = ended['RUN LIFE'].dropna().sort_values().values
        n = len(rl)
        surv = 1.0
        xs: list[float] = [0.0]
        ys: list[float] = [100.0]
        for i, t in enumerate(rl):
            surv *= (n - i - 1) / (n - i) if (n - i) > 0 else 0
            xs.append(float(t))
            ys.append(round(surv * 100, 1))
        curves[als] = {'x': xs, 'y': ys, 'color': colors_map.get(als, _G)}
    return curves


def render_tab_mtbf(df_bd_filtered, df_forma9_filtered, fecha_evaluacion,
                    verificaciones_filtered, selected_activo):
    """Renderiza el Tab PERFORMANCE / MTBF con estética ejecutiva Parex."""

    # ── 1. CÁLCULOS BASE ────────────────────────────────────────────────────
    try:
        mtbf_global, step_df = calcular_mtbf(df_bd_filtered, fecha_evaluacion)
    except Exception:
        mtbf_global, step_df = 0, pd.DataFrame()

    mtbf_efectivo_global = 0
    if not df_bd_filtered.empty:
        try:
            mtbf_efectivo_global, _ = calcular_mtbf(df_bd_filtered, fecha_evaluacion,
                                                     col_life='RUN_LIFE_EFECTIVO')
        except Exception:
            pass

    rl_total = df_bd_filtered['RUN LIFE'].mean() if not df_bd_filtered.empty else 0
    rl_efec = 0
    try:
        rl_efec, _ = calcular_run_life_efectivo(df_bd_filtered, df_forma9_filtered, fecha_evaluacion)
    except Exception:
        pass

    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    _filtros = {
        'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
        'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
        'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
    }
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"

    # ── ENCABEZADO EJECUTIVO (ESTILO TABLERO) ──────────────────────────────────
    hero_html = f"""
    <style>
    @import url('{_FONTS_URL}');
    .tbl-hero {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 22px;
        background:
            radial-gradient(120% 180% at 0% 0%, rgba(76,164,106,0.42) 0%, rgba(31,70,32,0) 55%),
            linear-gradient(110deg, {_G2} 0%, #17381A 45%, {_G2} 100%);
        border-radius: 14px;
        padding: 14px 22px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(31,70,32,0.13), 0 16px 38px rgba(31,70,32,0.24), inset 0 1px 0 rgba(255,255,255,0.16);
    }}
    .tbl-hero-brand {{ display: flex; align-items: center; gap: 14px; position: relative; z-index: 1; flex-shrink: 0; }}
    .tbl-hero-mark {{
        width: 42px; height: 42px; border-radius: 11px;
        background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.24);
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.30), 0 4px 12px rgba(0,0,0,0.18);
    }}
    .tbl-hero-title {{ font-family: {_FN}; font-size: 20px; font-weight: 700; color: #ffffff; line-height: 1.15; }}
    .tbl-hero-dot {{ width: 6px; height: 6px; border-radius: 50%; background: #6FD08C; box-shadow: 0 0 0 3px rgba(111,208,140,0.22); }}
    .tbl-hero-ctx {{ display: flex; align-items: stretch; position: relative; z-index: 1; flex: 1; justify-content: flex-end; }}
    .tbl-hero-item {{ padding: 0 16px; border-left: 1px solid rgba(255,255,255,0.15); display: flex; flex-direction: column; justify-content: center; gap: 2px; }}
    .tbl-hero-k {{ font-family: {_FS}; font-size: 9px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: rgba(255,255,255,0.55); }}
    .tbl-hero-v {{ font-family: {_FS}; font-size: 12.5px; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 6px; }}
    </style>
    <div class="tbl-hero">
      <div class="tbl-hero-brand">
        <div class="tbl-hero-mark">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        </div>
        <div>
          <div class="tbl-hero-title">Performance y Confiabilidad Operativa (MTBF)</div>
          <div style="font-family:{_FS}; font-size:11.5px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
            <div class="tbl-hero-dot"></div>
            <span>Tiempo medio entre fallas, longevidad Run Life y curvas de supervivencia</span>
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
          <span class="tbl-hero-k">Meta MTBF</span>
          <span class="tbl-hero-v">{META_MTBF} días</span>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── 2. KPI ROW (4 TARJETAS CON ELEVACIÓN _CARD, HALOS Y BADGES) ──────────
    st.markdown(f"""
    <style>
    .mtbf-card {{
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
    .mtbf-card:hover {{
        border-color: rgba(46,125,70,0.30);
        box-shadow: {_SH2};
        transform: translateY(-2px);
    }}
    .mtbf-icon {{
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 6px;
    }}
    .mtbf-icon.green  {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%);  box-shadow: {_halo(_G)}; }}
    .mtbf-icon.dark   {{ background: linear-gradient(160deg, {_G} 0%, {_G2} 100%);     box-shadow: {_halo(_G2)}; }}
    .mtbf-icon.gold   {{ background: linear-gradient(160deg, #E0B44C 0%, {_Y} 100%);  box-shadow: {_halo(_Y)}; }}
    
    .mtbf-lbl {{ font-family: {_FS}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
    .mtbf-val {{ font-family: {_FN}; font-size: 32px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
    .mtbf-sub {{ font-family: {_FS}; font-size: 10px; color: {_T2}; margin-top: 4px; }}
    .mtbf-badge {{
        font-family: {_FS}; font-size: 8.5px; font-weight: 700;
        padding: 2px 8px; border-radius: 12px; margin-top: 4px; display: inline-block;
        letter-spacing: 0.4px;
    }}
    </style>
    """, unsafe_allow_html=True)

    def _color_badge(val, meta, unit="d"):
        pct = (val / meta * 100) if meta else 0
        c = _G if pct >= 100 else (_Y if pct >= 70 else _R)
        bg = _G3 if pct >= 100 else (_Y2 if pct >= 70 else _R2)
        arrow = "▲" if pct >= 100 else ("◆" if pct >= 70 else "▼")
        return f'<span class="mtbf-badge" style="background:{bg}; color:{c}; border:1px solid {c}50;">{arrow} {pct:.0f}% META</span>'

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        badge = _color_badge(mtbf_global, META_MTBF)
        st.markdown(f"""
        <div class="mtbf-card">
            <div class="mtbf-icon green">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="mtbf-lbl">TMEF Global</div>
            <div class="mtbf-val" style="color:{_G};">{mtbf_global:.0f}<span style="font-size:16px;">d</span></div>
            {badge}
            <div class="mtbf-sub">Meta: {META_MTBF} días</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        badge = _color_badge(mtbf_efectivo_global, META_MTBF)
        st.markdown(f"""
        <div class="mtbf-card">
            <div class="mtbf-icon dark">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <div class="mtbf-lbl">TMEF Efectivo</div>
            <div class="mtbf-val" style="color:{_G2};">{mtbf_efectivo_global:.0f}<span style="font-size:16px;">d</span></div>
            {badge}
            <div class="mtbf-sub">Basado en RLE efectivo</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        badge = _color_badge(rl_total, META_RL)
        st.markdown(f"""
        <div class="mtbf-card">
            <div class="mtbf-icon gold">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
            </div>
            <div class="mtbf-lbl">RL Promedio</div>
            <div class="mtbf-val" style="color:{_Y};">{rl_total:.0f}<span style="font-size:16px;">d</span></div>
            {badge}
            <div class="mtbf-sub">Meta: {META_RL} días</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        badge = _color_badge(rl_efec, META_RL)
        st.markdown(f"""
        <div class="mtbf-card">
            <div class="mtbf-icon green">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
            </div>
            <div class="mtbf-lbl">RL Efectivo</div>
            <div class="mtbf-val" style="color:{_G};">{rl_efec:.0f}<span style="font-size:16px;">d</span></div>
            {badge}
            <div class="mtbf-sub">Días reales en Forma 9</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 3. ROW: HISTOGRAMA RL + CURVA DE SUPERVIVENCIA ─────────────────────
    col_hist, col_km = st.columns(2, gap="medium")

    with col_hist:
        if not df_bd_filtered.empty and 'RUN LIFE' in df_bd_filtered.columns:
            rl_vals = df_bd_filtered['RUN LIFE'].dropna()
            bins    = [0, 90, 365, 730, 1460, float('inf')]
            labels  = ['< 90d\n(Crítico)', '90–365d\n(Prematuro)', '1–2 años\n(Normal)',
                       '2–4 años\n(Bueno)', '> 4 años\n(Óptimo)']
            bin_colors = [_R, _Y, '#5C6B73', _G, _G2]
            counts = pd.cut(rl_vals, bins=bins, labels=labels).value_counts().reindex(labels).fillna(0).astype(int)

            hist_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "DISTRIBUCIÓN DE RUN LIFE", "left": "center", "top": 8,
                          "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"}},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                            "formatter": "{b}<br/>Pozos: <b>{c}</b>"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "18%", "containLabel": True},
                "xAxis": {"type": "category", "data": labels,
                          "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif", "interval": 0}},
                "yAxis": {"type": "value", "name": "Pozos",
                          "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                          "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                          "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                "series": [{
                    "type": "bar", "data": [{"value": int(counts[l]), "itemStyle": {"color": bin_colors[i], "borderRadius": [5, 5, 0, 0]}} for i, l in enumerate(labels)],
                    "barWidth": "50%",
                    "label": {"show": True, "position": "top", "color": _T2,
                              "fontFamily": "Inter, sans-serif", "fontSize": 10, "fontWeight": "bold",
                              "formatter": "{c}"},
                }]
            }
            components.html(_echarts(hist_opts, 350, "mtbf-hist"), height=360)
        else:
            st.info("Sin datos de Run Life disponibles.")

    with col_km:
        km_curves = _kaplan_meier(df_bd_filtered) if not df_bd_filtered.empty else {}
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
                "label": {"show": False}
            })
            km_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "CURVA DE SUPERVIVENCIA (KM)", "left": "center", "top": 8,
                          "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"},
                          "subtext": "Probabilidad de supervivencia por tecnología ALS",
                          "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}},
                "tooltip": {"trigger": "axis",
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                            "formatter": "function(p){return p.map(s=>`${s.seriesName}: <b>${s.value[1]}%</b>`).join('<br/>');}"},
                "legend": {"bottom": 4, "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "22%", "containLabel": True},
                "xAxis": {"type": "value", "name": "Días",
                          "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                          "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                          "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                "yAxis": {"type": "value", "name": "Supervivencia %", "min": 0, "max": 100,
                          "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                          "axisLabel": {"formatter": "{value}%", "color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                          "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                "series": km_series
            }
            components.html(_echarts(km_opts, 350, "mtbf-km"), height=360)
        else:
            st.info("Insuficientes datos para la curva de supervivencia.")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 4. ROW: MTBF POR ACTIVO VS META + TENDENCIA RL ─────────────────────
    col_activo, col_trend = st.columns(2, gap="medium")

    with col_activo:
        if 'ACTIVO' in df_bd_filtered.columns and not df_bd_filtered.empty:
            try:
                EXCLUIDOS = {
                    'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
                    'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
                    'MAPACHE/PERICO', 'MAPACHE-PERICO',
                    'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
                    'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
                    'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE'
                }
                activos_list = [a for a in df_bd_filtered['ACTIVO'].dropna().unique()
                                if str(a).upper().strip() not in EXCLUIDOS and str(a).strip() != '']
                rows_act = []
                for act in activos_list:
                    sub = df_bd_filtered[df_bd_filtered['ACTIVO'] == act]
                    m, _ = calcular_mtbf(sub, fecha_evaluacion)
                    rows_act.append({'ACTIVO': act, 'MTBF': round(m, 0)})
                df_act = pd.DataFrame(rows_act).sort_values('MTBF', ascending=True)

                bar_act_data = []
                for _, r in df_act.iterrows():
                    c = _G if r['MTBF'] >= META_MTBF else (_Y if r['MTBF'] >= META_MTBF * 0.7 else _R)
                    bar_act_data.append({"value": r['MTBF'], "itemStyle": {"color": c, "borderRadius": [0, 5, 5, 0]}})

                act_opts = {
                    "backgroundColor": "transparent",
                    "title": {"text": "MTBF POR ACTIVO VS META", "left": "center", "top": 8,
                              "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"}},
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                                "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                                "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                                "formatter": "{b}: <b>{c} días</b>"},
                    "grid": {"left": "4%", "right": "15%", "bottom": "8%", "top": "18%", "containLabel": True},
                    "xAxis": {"type": "value", "nameTextStyle": {"color": _T2, "fontSize": 9},
                              "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                              "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                    "yAxis": {"type": "category", "data": df_act['ACTIVO'].tolist(),
                              "axisLabel": {"color": _T, "fontSize": 10.5, "fontFamily": "Inter, sans-serif"}},
                    "series": [
                        {"name": "MTBF", "type": "bar", "data": bar_act_data, "barWidth": "50%",
                         "label": {"show": True, "position": "right", "color": _T2,
                                   "fontFamily": "Inter, sans-serif", "fontSize": 10, "formatter": "{c}d"}},
                        {"name": "Meta", "type": "line",
                         "data": [[META_MTBF, a] for a in df_act['ACTIVO'].tolist()],
                         "lineStyle": {"type": "dashed", "color": _R, "width": 2},
                         "itemStyle": {"color": _R}, "symbol": "none",
                         "markLine": {"silent": True, "data": [{"xAxis": META_MTBF, "label":
                                       {"show": True, "formatter": f"Meta {META_MTBF}d",
                                        "color": _R, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                                       "lineStyle": {"color": _R, "type": "dashed", "width": 2}}]}}
                    ]
                }
                components.html(_echarts(act_opts, 350, "mtbf-activo"), height=360)
            except Exception as e:
                st.warning(f"Error calculando MTBF por activo: {e}")
        else:
            st.info("Sin columna ACTIVO disponible.")

    with col_trend:
        historico_rl = generar_historico_run_life(df_bd_filtered, fecha_evaluacion)
        if historico_rl is not None and not historico_rl.empty:
            historico_rl['Mes_Str'] = pd.to_datetime(historico_rl['Mes'], errors='coerce').dt.strftime('%Y-%m')
            months = sorted(historico_rl['Mes_Str'].unique().tolist())
            activos = sorted(df_bd_filtered['ACTIVO'].unique().tolist()) if 'ACTIVO' in df_bd_filtered.columns else ['GLOBAL']
            colors_act = [_G, _Y, '#5C6B73', _G2, '#C98A2C', _R]
            trend_series = []
            for i, act in enumerate(activos[:5]):
                df_a = historico_rl[historico_rl['ACTIVO'] == act] if 'ACTIVO' in historico_rl.columns else historico_rl
                data_a = [round(float(df_a[df_a['Mes_Str'] == m]['Tiempo Op. Promedio'].values[0]), 1)
                          if len(df_a[df_a['Mes_Str'] == m]) > 0 else None for m in months]
                c = colors_act[i % len(colors_act)]
                trend_series.append({
                    "name": act, "type": "line", "smooth": True, "data": data_a,
                    "itemStyle": {"color": c}, "lineStyle": {"width": 2.2, "color": c},
                    "symbol": "circle", "symbolSize": 5,
                    "areaStyle": {"color": f"{c}0F"}
                })
            trend_series.append({
                "name": "Meta 1500d", "type": "line",
                "data": [1500] * len(months),
                "lineStyle": {"type": "dashed", "color": _R, "width": 1.5},
                "itemStyle": {"color": _R}, "symbol": "none"
            })
            trend_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "TENDENCIA LONGEVIDAD POR ACTIVO", "left": "center", "top": 8,
                          "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"}},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"bottom": 4, "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "18%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months,
                           "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "rotate": 30, "fontSize": 8.5}}],
                "yAxis": [{"type": "value", "name": "Días",
                           "nameTextStyle": {"color": _T2, "fontSize": 9},
                           "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                           "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}}],
                "series": trend_series
            }
            components.html(_echarts(trend_opts, 350, "mtbf-trend"), height=360)
        else:
            st.info("Sin histórico de Run Life disponible.")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA DETALLADA ──────────────────────────────────────────────────
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem;"
        "margin-bottom:8px;'>📋 Análisis Detallado de Eventos</h6>",
        unsafe_allow_html=True
    )
    if step_df is not None and not step_df.empty:
        render_hud_table(step_df.head(60))
    else:
        st.info("No hay detalles de cálculo disponibles.")
