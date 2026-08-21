"""
tabs/tab_performance.py  —  v4.2 Performance Operacional Premium
================================================================
Estética ejecutiva unificada con tab_tablero (Parex Industrial UI):
1. Hero Header ejecutivo con alcance y metadata de pozos ON.
2. Fila de KPIs de 3 capas con tipografía Source Serif 4 y halos semánticos.
3. Scatter interactivo BOPD vs Run Life efectivo con línea de tendencia.
4. Ranking Top 10 pozos por BOPD con barras degradadas y estado operativo.
5. Tendencia de producción mensual acumulada (BOPD vs Pozos ON).
6. Tabla de detalle con DataTables HUD.
"""

import json
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from data.config import COLOR_PRINCIPAL
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


def _halo(color):
    """Anillo suave + sombra proyectada bajo un icono circular."""
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    return (f"0 0 0 4px rgba({r},{g},{b},0.10), 0 4px 10px rgba({r},{g},{b},0.30), "
            f"inset 0 1px 0 rgba(255,255,255,0.28)")


def bucket_runlife(days):
    if pd.isna(days): return 'N/A'
    years = days / 365.25
    if years < 2:  return '< 2 años'
    if years < 4:  return '2 – 4 años'
    if years < 6:  return '4 – 6 años'
    return '> 6 años'


def _echarts(opts: dict, h: int, cid: str) -> str:
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;{_CARD}overflow:hidden;box-sizing:border-box;"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"),null);'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )


def render_tab_performance(df_bd_filtered, df_forma9_filtered, fecha_evaluacion):
    """Renderiza el Tab PERFORMANCE con análisis operacional y estética Parex."""

    fecha_eval = pd.to_datetime(fecha_evaluacion)

    # ── 1. PROCESAMIENTO ────────────────────────────────────────────────────
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
        df_perf = pd.DataFrame()

    if df_perf.empty:
        st.warning("⚠️ No hay pozos ON detectados para el mes de evaluación seleccionado.")
        return

    # ── ENCABEZADO EJECUTIVO (ESTILO TABLERO) ──────────────────────────────────
    _filtros = {
        'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
        'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
        'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
    }
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"

    total_bopd = df_perf['BOPD'].sum()
    avg_bopd   = df_perf['BOPD'].mean()
    max_rl     = df_perf['RUN_LIFE'].max()
    avg_efic   = df_perf['EFIC'].mean()
    n_on       = len(df_perf)

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
            <path d="M18 20V10M12 20V4M6 20v-6"/>
          </svg>
        </div>
        <div>
          <div class="tbl-hero-title">Producción y Eficiencia de Pozos ON</div>
          <div style="font-family:{_FS}; font-size:11.5px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
            <div class="tbl-hero-dot"></div>
            <span>Rendimiento volumétrico (BOPD), longevidad y eficiencia operacional</span>
          </div>
        </div>
      </div>
      <div class="tbl-hero-ctx">
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Corte Evaluación</span>
          <span class="tbl-hero-v">{fecha_eval.strftime('%B %Y').capitalize()}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Filtros Activos</span>
          <span class="tbl-hero-v">{_activos_lbl}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Producción Total</span>
          <span class="tbl-hero-v">{total_bopd:,.0f} BOPD</span>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── 2. KPI ROW (5 TARJETAS CON ELEVACIÓN _CARD Y HALOS) ───────────────────
    st.markdown(f"""
    <style>
    .perf-card {{
        {_CARD}
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 14px 10px;
        text-align: center;
        position: relative;
        transition: box-shadow 0.24s ease, transform 0.24s ease, border-color 0.24s ease;
    }}
    .perf-card:hover {{
        border-color: rgba(46,125,70,0.30);
        box-shadow: {_SH2};
        transform: translateY(-2px);
    }}
    .perf-icon {{
        width: 30px; height: 30px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 6px;
    }}
    .perf-icon.green  {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%);  box-shadow: {_halo(_G)}; }}
    .perf-icon.dark   {{ background: linear-gradient(160deg, {_G} 0%, {_G2} 100%);     box-shadow: {_halo(_G2)}; }}
    .perf-icon.gold   {{ background: linear-gradient(160deg, #E0B44C 0%, {_Y} 100%);  box-shadow: {_halo(_Y)}; }}
    .perf-icon.slate  {{ background: linear-gradient(160deg, #7A8992 0%, #5C6B73 100%); box-shadow: {_halo('#5C6B73')}; }}
    
    .perf-lbl {{ font-family: {_FS}; font-size: 9.5px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
    .perf-val {{ font-family: {_FN}; font-size: 30px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
    .perf-sub {{ font-family: {_FS}; font-size: 9.5px; color: {_T2}; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="perf-card">
            <div class="perf-icon green">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#ffffff" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
            </div>
            <div class="perf-lbl">Pozos ON</div>
            <div class="perf-val" style="color:{_G};">{n_on}</div>
            <div class="perf-sub">Con producción > 0 BOPD</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="perf-card">
            <div class="perf-icon dark">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            </div>
            <div class="perf-lbl">BOPD Total ON</div>
            <div class="perf-val" style="color:{_G2};">{total_bopd:,.0f}</div>
            <div class="perf-sub">Producción del mes</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="perf-card">
            <div class="perf-icon gold">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
            </div>
            <div class="perf-lbl">BOPD Promedio</div>
            <div class="perf-val" style="color:{_Y};">{avg_bopd:.1f}</div>
            <div class="perf-sub">Por pozo activo</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="perf-card">
            <div class="perf-icon slate">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#ffffff" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <div class="perf-lbl">Max Longevidad</div>
            <div class="perf-val" style="color:#5C6B73;">{max_rl:.0f}<span style="font-size:15px;">d</span></div>
            <div class="perf-sub">Pozo activo más longevo</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="perf-card">
            <div class="perf-icon green">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#ffffff" stroke-width="2.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
            </div>
            <div class="perf-lbl">Eficiencia Prom.</div>
            <div class="perf-val" style="color:{_G};">{avg_efic:.1f}</div>
            <div class="perf-sub">BOPD / año de vida útil</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 3. SCATTER BOPD vs RLE (izq) + RANKING TOP10 (der) ─────────────────
    col_scatter, col_rank = st.columns([6, 4], gap="medium")

    with col_scatter:
        als_colors = {'ESP': _G, 'PCP': _Y, 'BM': '#5C6B73', 'BH': _G2, 'EPCP': '#C98A2C'}
        scatter_series = []
        for als_name, grp in df_perf.groupby('ALS'):
            scatter_data = []
            for _, r in grp.iterrows():
                estado_s = "⚠️ FALLA" if r['FALLA'] else "✓ ON"
                scatter_data.append({
                    "value": [float(r['RLE']), float(r['BOPD'])],
                    "name": r['POZO'],
                    "tooltip_extra": f"{r['PROVEEDOR']} | RL: {r['RUN_LIFE']:.0f}d | Efic: {r['EFIC']:.1f} BOPD/año | {estado_s}",
                    "itemStyle": {
                        "color": als_colors.get(str(als_name), _G),
                        "borderColor": _R if r['FALLA'] else als_colors.get(str(als_name), _G),
                        "borderWidth": 2.5 if r['FALLA'] else 0,
                        "opacity": 0.85
                    }
                })
            scatter_series.append({
                "name": str(als_name), "type": "scatter",
                "data": scatter_data,
                "symbolSize": 10,
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0,
                                           "shadowColor": "rgba(0,0,0,0.25)"}}
            })
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
                    "lineStyle": {"type": "dashed", "color": _T2, "width": 1.5},
                    "itemStyle": {"color": _T2}, "symbol": "none",
                    "tooltip": {"show": False}
                })

        scatter_opts = {
            "backgroundColor": "transparent",
            "title": {"text": "SCATTER — BOPD vs RUN LIFE EFECTIVO",
                      "subtext": "Cada punto = un pozo activo | Borde rojo = en falla",
                      "left": "center", "top": 8,
                      "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"},
                      "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}},
            "tooltip": {"trigger": "item",
                        "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                        "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                        "formatter": "function(p){return '<b>'+p.data.name+'</b><br/>BOPD: <b>'+p.value[1]+'</b><br/>RLE: <b>'+p.value[0]+'d</b><br/>'+p.data.tooltip_extra;}"},
            "legend": {"bottom": 4, "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
            "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "22%", "containLabel": True},
            "xAxis": {"type": "value", "name": "Run Life Efectivo (días)",
                      "nameTextStyle": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 9},
                      "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                      "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
            "yAxis": {"type": "value", "name": "BOPD",
                      "nameTextStyle": {"color": _T2, "fontSize": 9},
                      "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                      "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
            "series": scatter_series
        }
        components.html(_echarts(scatter_opts, 390, "perf-scatter"), height=400)

    with col_rank:
        top10 = df_perf.sort_values('BOPD', ascending=True).tail(10).reset_index(drop=True)
        rank_data = []
        for _, r in top10.iterrows():
            c = _R if r['FALLA'] else _G
            rank_data.append({
                "value": float(r['BOPD']),
                "itemStyle": {"color": c, "borderRadius": [0, 5, 5, 0]}
            })
        rank_opts = {
            "backgroundColor": "transparent",
            "title": {"text": "TOP 10 POZOS — PRODUCCIÓN",
                      "subtext": "BOPD por pozo | Verde = OK, Rojo = Falla",
                      "left": "center", "top": 8,
                      "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"},
                      "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}},
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                        "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                        "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                        "formatter": "{b}: <b>{c} BOPD</b>"},
            "grid": {"left": "4%", "right": "16%", "bottom": "6%", "top": "20%", "containLabel": True},
            "xAxis": {"type": "value", "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                      "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
            "yAxis": {"type": "category", "data": top10['POZO'].tolist(),
                      "axisLabel": {"color": _T, "fontSize": 10, "fontFamily": "Inter, sans-serif"}},
            "series": [{
                "type": "bar", "data": rank_data, "barWidth": "55%",
                "label": {"show": True, "position": "right", "color": _T2,
                          "fontFamily": "Inter, sans-serif", "fontSize": 10,
                          "formatter": "{c}"}
            }]
        }
        components.html(_echarts(rank_opts, 390, "perf-rank"), height=400)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 4. TENDENCIA BOPD MENSUAL ───────────────────────────────────────────
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>"
        "📈 Tendencia de Producción Mensual (Pozos ON)</h6>",
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
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"data": ["BOPD Total", "Pozos ON"], "bottom": 4,
                           "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "6%", "bottom": "18%", "top": "8%", "containLabel": True},
                "xAxis": {"type": "category", "data": months_m,
                          "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif", "rotate": 30}},
                "yAxis": [
                    {"type": "value", "name": "BOPD Total",
                     "nameTextStyle": {"color": _T2, "fontSize": 9},
                     "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                     "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                    {"type": "value", "name": "Pozos ON", "position": "right",
                     "nameTextStyle": {"color": _Y, "fontSize": 9},
                     "axisLabel": {"color": _Y, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                     "splitLine": {"show": False}}
                ],
                "series": [
                    {"name": "BOPD Total", "type": "line", "smooth": True, "data": bopd_m,
                     "lineStyle": {"width": 2.5, "color": _G},
                     "itemStyle": {"color": _G}, "symbol": "circle", "symbolSize": 6,
                     "areaStyle": {"color": f"{_G}15"}},
                    {"name": "Pozos ON", "type": "bar", "yAxisIndex": 1, "data": pozos_m,
                     "barWidth": "35%",
                     "itemStyle": {"color": f"{_Y}80", "borderRadius": [4, 4, 0, 0]}}
                ]
            }
            components.html(_echarts(trend_opts, 260, "perf-trend"), height=270)
    except Exception as e:
        st.info(f"Sin datos de tendencia mensual disponibles. ({e})")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA DETALLE ────────────────────────────────────────────────────
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>"
        "📝 Detalle de Producción Pozos ON</h6>",
        unsafe_allow_html=True
    )
    df_render = df_perf.sort_values('BOPD', ascending=False).rename(columns={
        'POZO': 'POZO', 'BOPD': 'PROD. BOPD', 'RUN_LIFE': 'DÍAS RL',
        'RLE': 'RL EFECTIVO', 'ALS': 'TECNOLOGÍA', 'PROVEEDOR': 'PROVEEDOR',
        'EFIC': 'EFIC. (BOPD/año)', 'RANGO': 'CATEGORÍA'
    })[['POZO', 'PROD. BOPD', 'DÍAS RL', 'RL EFECTIVO', 'TECNOLOGÍA', 'PROVEEDOR', 'EFIC. (BOPD/año)', 'CATEGORÍA']]
    render_hud_table(df_render)
