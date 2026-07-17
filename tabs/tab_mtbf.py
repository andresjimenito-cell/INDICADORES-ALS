"""
tabs/tab_mtbf.py  —  v2.0 Análisis de Confiabilidad Premium
============================================================
Mejoras:
1. KPI row con comparativas delta vs meta
2. Histograma de distribución Run Life (5 bins con colorimetría de riesgo)
3. Curva de Supervivencia simplificada (Kaplan-Meier) por tecnología ALS
4. Comparativa MTBF vs Meta por Activo (barras horizontales con línea meta)
5. Tabla detallada de eventos con DataTables
"""

import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
from mtbf import calcular_mtbf
from calculations import calcular_run_life_efectivo, generar_historico_run_life
from styles import render_hud_table

_G   = "#137659"
_G2  = "#0a4d34"
_Y   = "#c09c2e"
_R   = "#c62828"
_T   = "#1f221e"
_T2  = "#455a72"
META_MTBF = 2190   # días

def _echarts(opts: dict, h: int, cid: str) -> str:
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;background:#ffffff;'
        f'border-radius:14px;border:1px solid rgba(19,118,89,0.13);overflow:hidden;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.04);"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"),null);'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )

def _kaplan_meier(df_bd):
    """Calcula la curva de supervivencia simplificada por tecnología ALS."""
    curves = {}
    als_list = ['ESP', 'PCP', 'BM', 'BH', 'EPCP'] if 'ALS' in df_bd.columns else ['GLOBAL']
    colors_map = {'ESP': _G, 'PCP': _Y, 'BM': '#5b5c55', 'BH': '#095139', 'EPCP': '#c09c2e', 'GLOBAL': _G}

    for als in als_list:
        if 'ALS' in df_bd.columns:
            sub = df_bd[df_bd['ALS'].astype(str).str.strip() == als].copy()
        else:
            sub = df_bd.copy()
        if len(sub) < 3:
            continue
        # Solo corridas finalizadas (falladas o extraídas)
        ended = sub[sub['FECHA_FALLA'].notna() | sub['FECHA_PULL'].notna()].copy()
        if ended.empty:
            continue
        rl = ended['RUN LIFE'].dropna().sort_values().values
        n = len(rl)
        # Kaplan-Meier simplificado: S(t) = product((n-i)/(n-i+1)) para eventos
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
    """Renderiza el Tab MTBF — Análisis de Confiabilidad Premium."""

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

    pct_meta = (mtbf_global / META_MTBF * 100) if META_MTBF > 0 else 0
    color_meta = _G if pct_meta >= 100 else (_Y if pct_meta >= 70 else _R)

    # ── 2. KPI ROW (4 tarjetas con delta vs meta) ───────────────────────────
    st.markdown("""
    <style>
    .mtbf-kpi { background:#ffffff; border:1px solid rgba(19,118,89,0.13); border-radius:14px;
        padding:14px 16px; display:flex; flex-direction:column; align-items:center;
        text-align:center; position:relative; overflow:hidden;
        box-shadow:0 2px 8px rgba(0,0,0,0.04);
        transition:transform 0.2s, box-shadow 0.2s; }
    .mtbf-kpi::before { content:''; position:absolute; top:0;left:0;right:0;height:3px; }
    .mtbf-kpi:hover { transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,0.08); }
    .mtbf-kpi-lbl { font-family:'Inter',sans-serif; font-size:0.58rem; font-weight:800;
        letter-spacing:1.2px; text-transform:uppercase; color:#5b5c55; margin-bottom:4px; }
    .mtbf-kpi-val { font-family:'Inter',sans-serif; font-size:1.8rem; font-weight:900;
        line-height:1.1; letter-spacing:-0.5px; }
    .mtbf-kpi-sub { font-family:'Inter',sans-serif; font-size:0.6rem; color:#94a3b8;
        margin-top:4px; }
    .mtbf-badge { font-family:'Inter',sans-serif; font-size:0.58rem; font-weight:700;
        padding:2px 8px; border-radius:20px; margin-top:5px; display:inline-block; }
    </style>""", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    def _color_badge(val, meta, unit="d"):
        pct = val / meta * 100 if meta else 0
        c = _G if pct >= 100 else (_Y if pct >= 70 else _R)
        arrow = "▲" if pct >= 100 else ("◆" if pct >= 70 else "▼")
        return f'<span class="mtbf-badge" style="background:{c}18;color:{c};border:1px solid {c}40;">{arrow} {pct:.0f}% META</span>'

    with k1:
        badge = _color_badge(mtbf_global, META_MTBF)
        st.markdown(f'''<div class="mtbf-kpi" style="border-top:3px solid {_G};">
            <div class="mtbf-kpi-lbl">TMEF Global</div>
            <div class="mtbf-kpi-val" style="color:{_G};">{mtbf_global:.0f}<span style="font-size:1rem;">d</span></div>
            {badge}<div class="mtbf-kpi-sub">Meta: {META_MTBF} días</div></div>''', unsafe_allow_html=True)
    with k2:
        badge = _color_badge(mtbf_efectivo_global, META_MTBF)
        st.markdown(f'''<div class="mtbf-kpi" style="border-top:3px solid {_G2};">
            <div class="mtbf-kpi-lbl">TMEF Efectivo</div>
            <div class="mtbf-kpi-val" style="color:{_G2};">{mtbf_efectivo_global:.0f}<span style="font-size:1rem;">d</span></div>
            {badge}<div class="mtbf-kpi-sub">Basado en RLE efectivo</div></div>''', unsafe_allow_html=True)
    with k3:
        badge = _color_badge(rl_total, 1500)
        st.markdown(f'''<div class="mtbf-kpi" style="border-top:3px solid {_Y};">
            <div class="mtbf-kpi-lbl">RL Promedio</div>
            <div class="mtbf-kpi-val" style="color:{_Y};">{rl_total:.0f}<span style="font-size:1rem;">d</span></div>
            {badge}<div class="mtbf-kpi-sub">Meta: 1,500 días</div></div>''', unsafe_allow_html=True)
    with k4:
        badge = _color_badge(rl_efec, 1500)
        st.markdown(f'''<div class="mtbf-kpi" style="border-top:3px solid {_G};">
            <div class="mtbf-kpi-lbl">RL Efectivo</div>
            <div class="mtbf-kpi-val" style="color:{_G};">{rl_efec:.0f}<span style="font-size:1rem;">d</span></div>
            {badge}<div class="mtbf-kpi-sub">Basado en Forma 9</div></div>''', unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 3. ROW: HISTOGRAMA RL + CURVA DE SUPERVIVENCIA ─────────────────────
    col_hist, col_km = st.columns(2, gap="medium")

    with col_hist:
        # Histograma de distribución Run Life con bins de riesgo
        if not df_bd_filtered.empty and 'RUN LIFE' in df_bd_filtered.columns:
            rl_vals = df_bd_filtered['RUN LIFE'].dropna()
            bins    = [0, 90, 365, 730, 1460, float('inf')]
            labels  = ['< 90d\n(Crítico)', '90–365d\n(Prematuro)', '1–2 años\n(Normal)',
                       '2–4 años\n(Bueno)', '> 4 años\n(Óptimo)']
            bin_colors = ['#c62828', '#c09c2e', '#455a72', '#137659', '#0a4d34']
            counts = pd.cut(rl_vals, bins=bins, labels=labels).value_counts().reindex(labels).fillna(0).astype(int)
            pcts   = (counts / counts.sum() * 100).round(1)

            hist_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "DISTRIBUCIÓN DE RUN LIFE", "left": "center", "top": 6,
                          "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"}},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                            "formatter": "{b}<br/>Pozos: <b>{c}</b>"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "18%", "containLabel": True},
                "xAxis": {"type": "category", "data": labels,
                          "axisLabel": {"color": _T2, "fontSize": 10, "fontFamily": "Inter, sans-serif",
                                        "interval": 0, "rich": {}}},
                "yAxis": {"type": "value", "name": "Pozos",
                          "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                          "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                "series": [{
                    "type": "bar", "data": counts.tolist(),
                    "barWidth": "55%",
                    "itemStyle": {"borderRadius": [6, 6, 0, 0],
                                  "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                            "colorStops": []}},
                    "label": {"show": True, "position": "top", "color": _T2,
                              "fontFamily": "Inter, sans-serif", "fontSize": 11, "fontWeight": "bold",
                              "formatter": "{c}"},
                }]
            }
            # Colorear cada barra individualmente
            bar_data = [{"value": int(counts[l]), "itemStyle": {"color": bin_colors[i],
                         "borderRadius": [6, 6, 0, 0]}} for i, l in enumerate(labels)]
            hist_opts["series"][0]["data"] = bar_data
            del hist_opts["series"][0]["itemStyle"]

            components.html(_echarts(hist_opts, 350, "mtbf-hist"), height=370)
        else:
            st.info("Sin datos de Run Life disponibles.")

    with col_km:
        # Curva de Supervivencia (Kaplan-Meier simplificada)
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
                    "areaStyle": {"color": f"{curve['color']}0D"}
                })
            # Línea de referencia 50%
            km_series.append({
                "name": "50% supervivencia", "type": "line",
                "data": [[0, 50], [max(max(c['x']) for c in km_curves.values()), 50]],
                "lineStyle": {"type": "dashed", "color": "#94a3b8", "width": 1.5},
                "itemStyle": {"color": "#94a3b8"}, "symbol": "none",
                "label": {"show": False}
            })
            km_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "CURVA DE SUPERVIVENCIA (KM)", "left": "center", "top": 6,
                          "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"},
                          "subtext": "Probabilidad de no falla a lo largo del tiempo",
                          "subtextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
                "tooltip": {"trigger": "axis",
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                            "formatter": "function(p){return p.map(s=>`${s.seriesName}: <b>${s.value[1]}%</b>`).join('<br/>');}"},
                "legend": {"bottom": 0, "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "22%", "containLabel": True},
                "xAxis": {"type": "value", "name": "Días",
                          "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                          "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                "yAxis": {"type": "value", "name": "Supervivencia %", "min": 0, "max": 100,
                          "axisLabel": {"formatter": "{value}%", "color": _T2, "fontFamily": "Inter, sans-serif"},
                          "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                "series": km_series
            }
            components.html(_echarts(km_opts, 350, "mtbf-km"), height=370)
        else:
            st.info("Insuficientes datos para la curva de supervivencia.")

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 4. ROW: MTBF POR ACTIVO VS META + TENDENCIA RL ─────────────────────
    col_activo, col_trend = st.columns(2, gap="medium")

    with col_activo:
        if 'ACTIVO' in df_bd_filtered.columns and not df_bd_filtered.empty:
            try:
                activos_list = [a for a in df_bd_filtered['ACTIVO'].dropna().unique()
                                if str(a).upper().strip() not in ('ECUADOR', '')]
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
                    "title": {"text": "MTBF POR ACTIVO VS META", "left": "center", "top": 6,
                              "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"}},
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                                "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                                "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                                "formatter": "{b}: <b>{c} días</b>"},
                    "grid": {"left": "4%", "right": "15%", "bottom": "8%", "top": "18%", "containLabel": True},
                    "xAxis": {"type": "value", "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                              "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                    "yAxis": {"type": "category", "data": df_act['ACTIVO'].tolist(),
                              "axisLabel": {"color": _T, "fontSize": 11, "fontFamily": "Inter, sans-serif"}},
                    "series": [
                        {"name": "MTBF", "type": "bar", "data": bar_act_data, "barWidth": "55%",
                         "label": {"show": True, "position": "right", "color": _T2,
                                   "fontFamily": "Inter, sans-serif", "formatter": "{c}d"}},
                        {"name": "Meta", "type": "line",
                         "data": [[META_MTBF, a] for a in df_act['ACTIVO'].tolist()],
                         "lineStyle": {"type": "dashed", "color": _R, "width": 2},
                         "itemStyle": {"color": _R}, "symbol": "none",
                         "markLine": {"silent": True, "data": [{"xAxis": META_MTBF, "label":
                                       {"show": True, "formatter": f"Meta {META_MTBF}d",
                                        "color": _R, "fontSize": 9},
                                       "lineStyle": {"color": _R, "type": "dashed", "width": 2}}]}}
                    ]
                }
                components.html(_echarts(act_opts, 350, "mtbf-activo"), height=370)
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
            colors_act = [_G, _Y, '#5b5c55', '#095139', '#a28834', '#c62828']
            trend_series = []
            for i, act in enumerate(activos[:5]):
                df_a = historico_rl[historico_rl['ACTIVO'] == act] if 'ACTIVO' in historico_rl.columns else historico_rl
                data_a = [round(float(df_a[df_a['Mes_Str'] == m]['Tiempo Op. Promedio'].values[0]), 1)
                          if len(df_a[df_a['Mes_Str'] == m]) > 0 else None for m in months]
                c = colors_act[i % len(colors_act)]
                trend_series.append({
                    "name": act, "type": "line", "smooth": True, "data": data_a,
                    "itemStyle": {"color": c}, "lineStyle": {"width": 2.5, "color": c},
                    "symbol": "circle", "symbolSize": 5,
                    "areaStyle": {"color": f"{c}10"}
                })
            # Línea meta
            trend_series.append({
                "name": "Meta 1500d", "type": "line",
                "data": [1500] * len(months),
                "lineStyle": {"type": "dashed", "color": _R, "width": 1.5},
                "itemStyle": {"color": _R}, "symbol": "none"
            })
            trend_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "TENDENCIA LONGEVIDAD POR ACTIVO", "left": "center", "top": 6,
                          "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"}},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"bottom": 0, "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "18%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months,
                           "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "rotate": 30, "fontSize": 9}}],
                "yAxis": [{"type": "value", "name": "Días",
                           "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                           "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}}],
                "series": trend_series
            }
            components.html(_echarts(trend_opts, 350, "mtbf-trend"), height=370)
        else:
            st.info("Sin histórico de Run Life disponible.")

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA DETALLADA ──────────────────────────────────────────────────
    st.markdown(
        "<h5 style='color:#137659;font-family:Inter,sans-serif;font-weight:800;"
        "letter-spacing:1px;text-transform:uppercase;font-size:0.75rem;"
        "margin-bottom:8px;'>📋 Análisis Detallado de Eventos</h5>",
        unsafe_allow_html=True
    )
    if step_df is not None and not step_df.empty:
        render_hud_table(step_df.head(60))
    else:
        st.info("No hay detalles de cálculo disponibles.")
