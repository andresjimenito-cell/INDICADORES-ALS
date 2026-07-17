"""
tabs/tab_performance.py  —  v2.0 Performance Operacional Premium
================================================================
Mejoras:
1. KPI row con delta vs mes anterior
2. Scatter interactivo BOPD vs Run Life efectivo (por pozo, con tooltip enriquecido)
3. Tendencia BOPD mensual total (de Forma 9 × Días trabajados)
4. Ranking Top 10 pozos por BOPD con estado operativo coloreado
5. Métrica de eficiencia: BOPD / año de vida útil
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
from styles import render_hud_table

_G  = "#137659"
_G2 = "#0a4d34"
_Y  = "#c09c2e"
_R  = "#c62828"
_T  = "#1f221e"
_T2 = "#455a72"


def bucket_runlife(days):
    if pd.isna(days): return 'N/A'
    years = days / 365.25
    if years < 2:  return '< 2 años'
    if years < 4:  return '2 - 4 años'
    if years < 6:  return '4 - 6 años'
    return '> 6 años'


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


def render_tab_performance(df_bd_filtered, df_forma9_filtered, fecha_evaluacion):
    """Renderiza el Tab PERFORMANCE con análisis de profundidad operacional."""

    fecha_eval = pd.to_datetime(fecha_evaluacion)

    # ── 1. PROCESAMIENTO ────────────────────────────────────────────────────
    try:
        df_f9 = df_forma9_filtered.copy()
        df_f9['FECHA_FORMA9'] = pd.to_datetime(df_f9.get('FECHA_FORMA9'), errors='coerce')

        # Mes actual de evaluación
        df_month = df_f9[
            (df_f9['FECHA_FORMA9'].dt.year  == fecha_eval.year) &
            (df_f9['FECHA_FORMA9'].dt.month == fecha_eval.month)
        ].copy()

        bopd_col = next((c for c in df_month.columns if 'BOPD' in str(c).upper() or 'PETROLEO DIA' in str(c).upper() or 'PETROLEO_DIA' in str(c).upper()), None)
        dias_col = next((c for c in df_month.columns if 'DIAS' in str(c).upper() and 'TRAB' in str(c).upper()), None)

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
        df_perf = pd.DataFrame()

    if df_perf.empty:
        st.warning("⚠️ No hay pozos ON detectados para el mes de evaluación seleccionado.")
        return

    # ── 2. KPI ROW ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .perf-kpi { background:#ffffff; border:1px solid rgba(19,118,89,0.12); border-radius:14px;
        padding:14px 16px; display:flex; flex-direction:column; align-items:center;
        text-align:center; position:relative; overflow:hidden;
        box-shadow:0 2px 8px rgba(0,0,0,0.04); transition:transform 0.2s,box-shadow 0.2s; }
    .perf-kpi:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.08); }
    .perf-kpi-lbl { font-family:'Inter',sans-serif; font-size:0.58rem; font-weight:800;
        letter-spacing:1.2px; text-transform:uppercase; color:#5b5c55; margin-bottom:4px; }
    .perf-kpi-val { font-family:'Inter',sans-serif; font-size:1.8rem; font-weight:900; line-height:1.1; }
    .perf-kpi-sub { font-family:'Inter',sans-serif; font-size:0.6rem; color:#94a3b8; margin-top:4px; }
    </style>""", unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    total_bopd = df_perf['BOPD'].sum()
    avg_bopd   = df_perf['BOPD'].mean()
    max_rl     = df_perf['RUN_LIFE'].max()
    avg_efic   = df_perf['EFIC'].mean()
    n_on       = len(df_perf)

    with c1:
        st.markdown(f'''<div class="perf-kpi" style="border-top:3px solid {_G};">
            <div class="perf-kpi-lbl">Pozos ON (mes)</div>
            <div class="perf-kpi-val" style="color:{_G};">{n_on}</div>
            <div class="perf-kpi-sub">Con producción > 0 BOPD</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="perf-kpi" style="border-top:3px solid {_G2};">
            <div class="perf-kpi-lbl">BOPD Total ON</div>
            <div class="perf-kpi-val" style="color:{_G2};">{total_bopd:.0f}</div>
            <div class="perf-kpi-sub">Producción acumulada mes</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="perf-kpi" style="border-top:3px solid {_Y};">
            <div class="perf-kpi-lbl">BOPD Promedio</div>
            <div class="perf-kpi-val" style="color:{_Y};">{avg_bopd:.1f}</div>
            <div class="perf-kpi-sub">Por pozo activo</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="perf-kpi" style="border-top:3px solid #5b5c55;">
            <div class="perf-kpi-lbl">Max Longevidad</div>
            <div class="perf-kpi-val" style="color:#5b5c55;">{max_rl:.0f}<span style="font-size:1rem;">d</span></div>
            <div class="perf-kpi-sub">Pozo más longevo activo</div></div>''', unsafe_allow_html=True)
    with c5:
        st.markdown(f'''<div class="perf-kpi" style="border-top:3px solid {_G};">
            <div class="perf-kpi-lbl">Eficiencia Promedio</div>
            <div class="perf-kpi-val" style="color:{_G};">{avg_efic:.1f}</div>
            <div class="perf-kpi-sub">BOPD / año de vida útil</div></div>''', unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 3. SCATTER BOPD vs RLE (izq) + RANKING TOP10 (der) ─────────────────
    col_scatter, col_rank = st.columns([6, 4], gap="medium")

    with col_scatter:
        als_colors = {'ESP': _G, 'PCP': _Y, 'BM': '#5b5c55', 'BH': '#095139', 'EPCP': '#a28834'}
        scatter_series = []
        for als_name, grp in df_perf.groupby('ALS'):
            scatter_data = []
            for _, r in grp.iterrows():
                estado_s = "⚠ FALLA" if r['FALLA'] else "✓ ON"
                scatter_data.append({
                    "value": [float(r['RLE']), float(r['BOPD'])],
                    "name": r['POZO'],
                    "tooltip_extra": f"{r['PROVEEDOR']} | RL: {r['RUN_LIFE']:.0f}d | Efic: {r['EFIC']:.1f} BOPD/año | {estado_s}",
                    "itemStyle": {
                        "color": als_colors.get(str(als_name), _G),
                        "borderColor": _R if r['FALLA'] else als_colors.get(str(als_name), _G),
                        "borderWidth": 2.5 if r['FALLA'] else 0,
                        "opacity": 0.8
                    }
                })
            scatter_series.append({
                "name": str(als_name), "type": "scatter",
                "data": scatter_data,
                "symbolSize": 10,
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0,
                                           "shadowColor": "rgba(0,0,0,0.3)"}}
            })
        # Línea de tendencia lineal simple
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
                    "lineStyle": {"type": "dashed", "color": "#94a3b8", "width": 1.5},
                    "itemStyle": {"color": "#94a3b8"}, "symbol": "none",
                    "tooltip": {"show": False}
                })

        scatter_opts = {
            "backgroundColor": "transparent",
            "title": {"text": "SCATTER — BOPD vs RUN LIFE EFECTIVO",
                      "subtext": "Cada punto = un pozo | Borde rojo = en falla",
                      "left": "center", "top": 4,
                      "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"},
                      "subtextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
            "tooltip": {"trigger": "item",
                        "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                        "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                        "formatter": "function(p){return p.data.name+'<br/>BOPD: <b>'+p.value[1]+'</b><br/>RLE: <b>'+p.value[0]+'d</b><br/>'+p.data.tooltip_extra;}"},
            "legend": {"bottom": 0, "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
            "grid": {"left": "4%", "right": "4%", "bottom": "16%", "top": "22%", "containLabel": True},
            "xAxis": {"type": "value", "name": "Run Life Efectivo (días)",
                      "nameTextStyle": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 10},
                      "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                      "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
            "yAxis": {"type": "value", "name": "BOPD",
                      "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                      "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
            "series": scatter_series
        }
        components.html(_echarts(scatter_opts, 400, "perf-scatter"), height=420)

    with col_rank:
        top10 = df_perf.sort_values('BOPD', ascending=True).tail(10).reset_index(drop=True)
        rank_data = []
        for _, r in top10.iterrows():
            c = _R if r['FALLA'] else _G
            rank_data.append({
                "value": float(r['BOPD']),
                "itemStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 1, "y2": 0,
                                         "colorStops": [{"offset": 0, "color": c},
                                                         {"offset": 1, "color": f"{c}20"}]},
                              "borderRadius": [0, 6, 6, 0]}
            })
        rank_opts = {
            "backgroundColor": "transparent",
            "title": {"text": "TOP 10 POZOS — BOPD",
                      "subtext": "Verde = operativo | Rojo = en falla",
                      "left": "center", "top": 4,
                      "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"},
                      "subtextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                        "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                        "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                        "formatter": "{b}: <b>{c} BOPD</b>"},
            "grid": {"left": "4%", "right": "16%", "bottom": "6%", "top": "20%", "containLabel": True},
            "xAxis": {"type": "value", "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                      "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
            "yAxis": {"type": "category", "data": top10['POZO'].tolist(),
                      "axisLabel": {"color": _T, "fontSize": 10, "fontFamily": "Inter, sans-serif"}},
            "series": [{
                "type": "bar", "data": rank_data, "barWidth": "60%",
                "label": {"show": True, "position": "right", "color": _T2,
                          "fontFamily": "Inter, sans-serif", "fontSize": 10,
                          "formatter": "{c}"}
            }]
        }
        components.html(_echarts(rank_opts, 400, "perf-rank"), height=420)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 4. TENDENCIA BOPD MENSUAL ───────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:0.7rem;font-weight:800;"
        "letter-spacing:1.5px;text-transform:uppercase;color:#137659;margin-bottom:8px;'>"
        "📈 Tendencia de Producción Mensual (Pozos ON)</div>",
        unsafe_allow_html=True
    )
    try:
        df_f9_all = df_forma9_filtered.copy()
        df_f9_all['FECHA_FORMA9'] = pd.to_datetime(df_f9_all.get('FECHA_FORMA9'), errors='coerce')
        bopd_col_all = next((c for c in df_f9_all.columns if 'BOPD' in str(c).upper() or 'PETROLEO DIA' in str(c).upper() or 'PETROLEO_DIA' in str(c).upper()), None)
        if bopd_col_all:
            df_f9_all[bopd_col_all] = pd.to_numeric(df_f9_all[bopd_col_all], errors='coerce').fillna(0)
            df_f9_all['MES'] = df_f9_all['FECHA_FORMA9'].dt.to_period('M').astype(str)
            df_mon = df_f9_all[df_f9_all[bopd_col_all] > 0].groupby('MES').agg(
                BOPD_TOTAL=(bopd_col_all, 'sum'),
                POZOS_ON=('POZO', 'nunique')
            ).reset_index().sort_values('MES')
            months_m = df_mon['MES'].tolist()
            bopd_m   = [round(float(v), 1) for v in df_mon['BOPD_TOTAL'].tolist()]
            pozos_m  = df_mon['POZOS_ON'].tolist()

            trend_opts = {
                "backgroundColor": "transparent",
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"data": ["BOPD Total", "Pozos ON"], "bottom": 0,
                           "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "6%", "bottom": "18%", "top": "8%", "containLabel": True},
                "xAxis": {"type": "category", "data": months_m,
                          "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif", "rotate": 30}},
                "yAxis": [
                    {"type": "value", "name": "BOPD Total",
                     "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                     "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                    {"type": "value", "name": "Pozos ON", "position": "right",
                     "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                     "splitLine": {"show": False}}
                ],
                "series": [
                    {"name": "BOPD Total", "type": "line", "smooth": True, "data": bopd_m,
                     "lineStyle": {"width": 3, "color": _G},
                     "itemStyle": {"color": _G}, "symbol": "circle", "symbolSize": 6,
                     "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                             "colorStops": [{"offset": 0, "color": f"{_G}30"},
                                                             {"offset": 1, "color": "transparent"}]}}},
                    {"name": "Pozos ON", "type": "bar", "yAxisIndex": 1, "data": pozos_m,
                     "barWidth": "40%",
                     "itemStyle": {"color": f"{_Y}70", "borderRadius": [4, 4, 0, 0]}}
                ]
            }
            components.html(_echarts(trend_opts, 260, "perf-trend"), height=280)
    except Exception as e:
        st.info(f"Sin datos de tendencia mensual disponibles. ({e})")

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA DETALLE ────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:0.7rem;font-weight:800;"
        "letter-spacing:1.5px;text-transform:uppercase;color:#137659;margin-bottom:8px;'>"
        "📝 Detalle de Producción Pozos ON</div>",
        unsafe_allow_html=True
    )
    df_render = df_perf.sort_values('BOPD', ascending=False).rename(columns={
        'POZO': 'POZO', 'BOPD': 'PROD. BOPD', 'RUN_LIFE': 'DÍAS RL',
        'RLE': 'RL EFECTIVO', 'ALS': 'TECNOLOGÍA', 'PROVEEDOR': 'PROVEEDOR',
        'EFIC': 'EFIC. (BOPD/año)', 'RANGO': 'CATEGORÍA'
    })[['POZO', 'PROD. BOPD', 'DÍAS RL', 'RL EFECTIVO', 'TECNOLOGÍA', 'PROVEEDOR', 'EFIC. (BOPD/año)', 'CATEGORÍA']]
    render_hud_table(df_render)
