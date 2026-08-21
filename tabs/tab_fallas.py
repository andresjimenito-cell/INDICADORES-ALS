"""
tabs/tab_fallas.py  —  v4.2 Análisis de Fallas Premium
======================================================
Estética ejecutiva unificada con tab_tablero (Parex Industrial UI):
1. Hero Header ejecutivo con alcance y periodo de evaluación.
2. Fila de KPIs de 3 capas con tipografía Source Serif 4 y halos semánticos.
3. Pareto de causas de falla (análisis 80/20) con barras redondeadas y línea suave.
4. Tabla interactiva de eventos con DataTables y badges de estado.
5. Timeline de eventos mensuales en gráfico apilado ECharts.
6. Plan de Acción con tarjetas ejecutivas.
"""

import json
from datetime import timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from data.config import COLOR_PRINCIPAL
from core.calculations import clasificar_razon_ia, highlight_problema
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


def clasificar_runlife(rl):
    try: rl = float(rl)
    except: return 'N/A'
    if rl <= 30:   return 'Infantil'
    if rl <= 90:   return 'Prematura'
    if rl <= 1100: return 'En Garantía'
    return 'Sin Garantía'


def _echarts(opts: dict, h: int, cid: str) -> str:
    return (
        f'<div id="{cid}" style="width:100%;height:{h}px;{_CARD}overflow:hidden;box-sizing:border-box;"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"),null);'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
    )


def render_tab_fallas(df_bd_filtered, fecha_evaluacion):
    """Renderiza el Tab FALLAS con análisis profundo y estética ejecutiva Parex."""

    # ── Defaults de sesión ──────────────────────────────────────────────────
    if 'plan_bombas'    not in st.session_state:
        st.session_state['plan_bombas']    = "Uso de bombas con coating y recubrimiento en carburo de tungsteno y nitruración"
    if 'plan_arena'     not in st.session_state:
        st.session_state['plan_arena']     = "Uso de equipo para arena como Sand Lift, Sand Maze, etc."
    if 'plan_proveedor' not in st.session_state:
        st.session_state['plan_proveedor'] = "Cambio de proveedor para componentes críticos"

    if st.session_state.get('reporte_fallas') is None or st.session_state['reporte_fallas'].empty:
        st.info("Sin datos de fallas.")
        return

    reporte_fallas = st.session_state['reporte_fallas']
    fecha_eval     = pd.to_datetime(fecha_evaluacion)
    fecha_ini_str  = st.session_state.get('fecha_inicio_state')
    fecha_ini_dt   = pd.to_datetime(fecha_ini_str).normalize() if fecha_ini_str else fecha_eval - pd.DateOffset(years=1)
    fecha_ini_label = fecha_ini_dt.strftime('%d/%m/%Y')
    fecha_eval_label = fecha_eval.strftime('%d/%m/%Y')

    total_fallas_rango = len(reporte_fallas)
    fallas_als = df_bd_filtered[df_bd_filtered['INDICADOR_MTBF'] == 1].shape[0] if df_bd_filtered is not None else 0

    if df_bd_filtered is not None and not df_bd_filtered.empty:
        fallas_als_periodo = int(df_bd_filtered[
            (df_bd_filtered['FECHA_FALLA'].notna()) &
            (df_bd_filtered['FECHA_FALLA'] >= fecha_ini_dt) &
            (df_bd_filtered['FECHA_FALLA'] <= fecha_eval) &
            (df_bd_filtered['INDICADOR_MTBF'] == 1)
        ].shape[0])
        fallas_periodo = int(df_bd_filtered[
            (df_bd_filtered['FECHA_FALLA'].notna()) &
            (df_bd_filtered['FECHA_FALLA'] >= fecha_ini_dt) &
            (df_bd_filtered['FECHA_FALLA'] <= fecha_eval)
        ].shape[0])
        inf_rate = fallas_als / fallas_periodo * 100 if fallas_periodo > 0 else 0
    else:
        fallas_als_periodo = fallas_periodo = 0
        inf_rate = 0

    # ── ENCABEZADO EJECUTIVO (ESTILO TABLERO) ──────────────────────────────────
    _filtros = {
        'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
        'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
        'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
        'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
    }
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"
    periodo_lbl = f"{fecha_ini_label} — {fecha_eval_label}"

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
            <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <div>
          <div class="tbl-hero-title">Análisis Causa Raíz y Gestión de Fallas</div>
          <div style="font-family:{_FS}; font-size:11.5px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
            <div class="tbl-hero-dot"></div>
            <span>Diagnóstico de causas de pull, Pareto 80/20 y plan de mitigación</span>
          </div>
        </div>
      </div>
      <div class="tbl-hero-ctx">
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Periodo Evaluado</span>
          <span class="tbl-hero-v">{periodo_lbl}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Filtros Activos</span>
          <span class="tbl-hero-v">{_activos_lbl}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Fallas Periodo</span>
          <span class="tbl-hero-v">{fallas_periodo} eventos</span>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # ── 1. KPI GRID (4 TARJETAS CON ELEVACIÓN _CARD Y HALOS) ─────────────────
    st.markdown(f"""
    <style>
    .falla-card {{
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
    .falla-card:hover {{
        border-color: rgba(46,125,70,0.30);
        box-shadow: {_SH2};
        transform: translateY(-2px);
    }}
    .falla-icon {{
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 6px;
    }}
    .falla-icon.green  {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%);  box-shadow: {_halo(_G)}; }}
    .falla-icon.dark   {{ background: linear-gradient(160deg, {_G} 0%, {_G2} 100%);     box-shadow: {_halo(_G2)}; }}
    .falla-icon.gold   {{ background: linear-gradient(160deg, #E0B44C 0%, {_Y} 100%);  box-shadow: {_halo(_Y)}; }}
    .falla-icon.red    {{ background: linear-gradient(160deg, #D9584A 0%, {_R} 100%);  box-shadow: {_halo(_R)}; }}
    
    .falla-lbl {{ font-family: {_FS}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
    .falla-val {{ font-family: {_FN}; font-size: 32px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
    .falla-sub {{ font-family: {_FS}; font-size: 10px; color: {_T2}; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="falla-card">
            <div class="falla-icon dark">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            </div>
            <div class="falla-lbl">Total Histórico</div>
            <div class="falla-val" style="color:{_G2};">{total_fallas_rango}</div>
            <div class="falla-sub">Todos los registros del dataset</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="falla-card">
            <div class="falla-icon red">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            </div>
            <div class="falla-lbl">Fallas ALS (Total)</div>
            <div class="falla-val" style="color:{_R};">{fallas_als}</div>
            <div class="falla-sub">INDICADOR_MTBF = 1</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="falla-card">
            <div class="falla-icon gold">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            </div>
            <div class="falla-lbl">Fallas ALS Periodo</div>
            <div class="falla-val" style="color:{_Y};">{fallas_als_periodo}</div>
            <div class="falla-sub">Filtro de fecha activa</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        color_als = _R if inf_rate > 60 else (_Y if inf_rate > 40 else _G)
        st.markdown(f"""
        <div class="falla-card">
            <div class="falla-icon green">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div class="falla-lbl">Tasa ALS / Total</div>
            <div class="falla-val" style="color:{color_als};">{inf_rate:.0f}<span style="font-size:16px;">%</span></div>
            <div class="falla-sub">{fallas_periodo} eventos totales en periodo</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 2. PARETO DE CAUSAS (50%) + TABLA DE EVENTOS (50%) ─────────────────
    col_pareto, col_tabla = st.columns([5, 5], gap="medium")

    with col_pareto:
        if df_bd_filtered is not None and not df_bd_filtered.empty:
            mask_fallas = (
                (df_bd_filtered['FECHA_FALLA'].notna()) &
                (pd.to_datetime(df_bd_filtered['FECHA_FALLA'], errors='coerce') >= (fecha_eval - timedelta(days=365))) &
                (pd.to_datetime(df_bd_filtered['FECHA_FALLA'], errors='coerce') <= fecha_eval)
            )
            df_f = df_bd_filtered[mask_fallas].copy()

            if not df_f.empty:
                col_razon = next((c for c in ['SUB TIPO DE FALLA', 'RAZON ESPECIFICA PULL', 'RAZON_DE_PULL']
                                  if c in df_f.columns), None)
                if col_razon:
                    df_f['Causa'] = df_f[col_razon].apply(
                        lambda x: clasificar_razon_ia(str(x)) if pd.notna(x) and str(x).strip() else 'Desconocida')
                    conteo = df_f['Causa'].value_counts().reset_index()
                    conteo.columns = ['Causa', 'N']
                    conteo = conteo.sort_values('N', ascending=False).head(10).reset_index(drop=True)
                    conteo['Acum'] = (conteo['N'].cumsum() / conteo['N'].sum() * 100).round(1)

                    bar_colors = [_R if i < 2 else (_Y if i < 5 else _G) for i in range(len(conteo))]
                    pareto_opts = {
                        "backgroundColor": "transparent",
                        "title": {"text": "PARETO DE CAUSAS DE FALLA (12M)",
                                  "subtext": "Regla 80/20 — Concentración de fallas",
                                  "left": "center", "top": 8,
                                  "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"},
                                  "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}},
                        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                                    "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                                    "textStyle": {"color": _T, "fontSize": 11, "fontFamily": "Inter, sans-serif"}},
                        "legend": {"data": ["Frecuencia", "% Acumulado"], "bottom": 4,
                                   "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                        "grid": {"left": "4%", "right": "8%", "bottom": "18%", "top": "22%", "containLabel": True},
                        "xAxis": {"type": "category", "data": conteo['Causa'].tolist(),
                                  "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif",
                                                "rotate": 25, "interval": 0}},
                        "yAxis": [
                            {"type": "value", "name": "Frecuencia",
                             "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                             "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif"},
                             "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                            {"type": "value", "name": "% Acum", "min": 0, "max": 100,
                             "nameTextStyle": {"color": _Y, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                             "axisLabel": {"formatter": "{value}%", "color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif"},
                             "splitLine": {"show": False}}
                        ],
                        "series": [
                            {"name": "Frecuencia", "type": "bar",
                             "data": [{"value": int(r), "itemStyle": {"color": bar_colors[i], "borderRadius": [4, 4, 0, 0]}}
                                       for i, r in enumerate(conteo['N'].tolist())],
                             "barWidth": "50%",
                             "label": {"show": True, "position": "top", "color": _T2,
                                       "fontFamily": "Inter, sans-serif", "fontSize": 9.5}},
                            {"name": "% Acumulado", "type": "line", "yAxisIndex": 1,
                             "data": conteo['Acum'].tolist(), "smooth": True,
                             "lineStyle": {"width": 2.5, "color": _Y},
                             "itemStyle": {"color": _Y}, "symbol": "circle", "symbolSize": 6,
                             "label": {"show": True, "position": "top", "formatter": "{c}%",
                                       "color": _Y, "fontSize": 8.5, "fontFamily": "Inter, sans-serif"},
                             "markLine": {"silent": True, "data": [{"yAxis": 80}],
                                          "lineStyle": {"type": "dashed", "color": _R, "width": 1.5},
                                          "label": {"show": True, "formatter": "80% (Pareto)", "color": _R, "fontSize": 9, "fontFamily": "Inter, sans-serif"}}}
                        ]
                    }
                    components.html(_echarts(pareto_opts, 390, "fallas-pareto"), height=400)
                else:
                    st.info("Sin columna de razón de falla disponible.")
            else:
                st.info("Sin fallas en los últimos 12 meses.")
        else:
            st.info("Sin datos disponibles.")

    with col_tabla:
        if df_bd_filtered is not None and not df_bd_filtered.empty:
            mask_run = pd.to_datetime(df_bd_filtered['FECHA_RUN'], errors='coerce').dt.normalize() <= fecha_eval
            mask_falla = pd.to_datetime(df_bd_filtered['FECHA_FALLA'], errors='coerce').dt.normalize() >= fecha_ini_dt
            mask_activos = pd.to_datetime(df_bd_filtered['FECHA_FALLA'], errors='coerce').isna()
            df_bd_eval = df_bd_filtered[mask_run & (mask_falla | mask_activos)].copy()
        else:
            df_bd_eval = pd.DataFrame()

        if df_bd_eval.empty:
            st.info("Sin datos para el periodo evaluado.")
        else:
            rows = []
            col_razon = next((c for c in ['RAZON_DE_PULL', 'RAZON ESPECIFICA PULL'] if c in df_bd_eval.columns), None)
            for _, row in df_bd_eval.iterrows():
                pozo  = str(row.get('POZO', ''))
                fr    = row.get('FECHA_RUN')
                fr_str = fr.strftime('%Y-%m-%d') if pd.notna(fr) else ''
                ff    = row.get('FECHA_FALLA')
                ff_str = ff.strftime('%Y-%m-%d') if pd.notna(ff) else '<span style="color:#707070;">-</span>'
                fp    = row.get('FECHA_PULL')
                fp_str = fp.strftime('%Y-%m-%d') if pd.notna(fp) else '<span style="color:#2E7D46;font-weight:bold;">PEND.</span>'
                razon = str(row.get(col_razon, '')) if col_razon else ''
                run_val = row.get('RUN', 1)
                tipo_badge = '<span class="badge-custom badge-nuevo">PERFORADO</span>' if run_val == 1 else '<span class="badge-custom badge-ws">WS</span>'
                if pd.notna(ff):
                    estado_badge = '<span class="badge-custom badge-fallado">FALLA</span>'
                    run_life = (ff - fr).days if pd.notna(fr) else '-'
                    sub_tipo = row.get('SUB TIPO DE FALLA')
                    if pd.notna(sub_tipo) and str(sub_tipo).strip():
                        causa = clasificar_razon_ia(str(sub_tipo))
                    else:
                        causa = clasificar_razon_ia(razon) if razon.strip() else 'Desc.'
                        if pd.isna(fp): causa = f"Posible {causa}"
                else:
                    estado_badge = '<span class="badge-custom badge-operativo">OK</span>'
                    run_life = '<span style="color:#707070;">-</span>'
                    causa = '<span style="color:#707070;">-</span>'
                rows.append({'Pozo': pozo, 'F.Run': fr_str, 'F.Falla': ff_str, 'F.Pull': fp_str,
                             'RL(d)': str(run_life), 'Causa': causa, 'Tipo': tipo_badge, 'Estado': estado_badge})

            rows = sorted(rows, key=lambda x: 0 if '⚠️' in x['Estado'] else 1)
            df_html = pd.DataFrame(rows)
            html_tbl = df_html.to_html(index=False, table_id="fallas_main_table",
                                        classes='display nowrap hud-table', escape=False)
            components.html(f"""
            <style>
                @import url('{_FONTS_URL}');
                @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
                body {{ margin:0; padding:0; background:transparent; color:{_T}; font-family:{_FS}; }}
                .dataTables_wrapper {{ color:{_T} !important; width:100% !important; }}
                .dataTables_filter input {{ 
                    background:#ffffff; border:1px solid {_BR}; color:{_T};
                    border-radius:8px; padding:4px 10px; font-size:11px; font-family:{_FS}; outline:none; }}
                .dataTables_filter input:focus {{ border-color:{_G}; }}
                .dataTables_filter label {{ color:{_T2}; font-size:11px; font-family:{_FS}; }}
                button.dt-button {{ 
                    background:rgba(46,125,70,0.08) !important; border:1px solid rgba(46,125,70,0.3) !important;
                    color:{_G2} !important; font-family:{_FS} !important; font-size:10px !important; font-weight:700 !important;
                    padding:4px 14px !important; border-radius:20px !important; text-transform:uppercase !important;
                    cursor:pointer; transition:all 0.2s ease; }}
                button.dt-button:hover {{ background:{_G} !important; color:#ffffff !important; }}
                table.dataTable {{ width:100% !important; }}
                table.dataTable thead th {{ 
                    background:rgba(46,125,70,0.08); color:{_G2};
                    font-family:{_FS}; font-size:10px; font-weight:800;
                    letter-spacing:0.6px; padding:8px 9px; white-space:nowrap; text-transform:uppercase; 
                    border-bottom:1px solid {_BR} !important; }}
                table.dataTable tbody td {{ 
                    border-bottom:1px solid rgba(220,226,216,0.6);
                    padding:6px 9px; font-size:11px; color:{_T}; }}
                .dataTables_info, .dataTables_paginate {{ color:{_T2} !important; font-size:10px; font-family:{_FS}; }}
                .badge-custom {{ 
                    display:inline-block; padding:2px 7px; font-size:8px; font-weight:700;
                    border-radius:10px; text-align:center; text-transform:uppercase;
                    letter-spacing:0.5px; white-space:nowrap; font-family:{_FS}; }}
                .badge-nuevo {{ background:{_G3}; color:{_G2}; border:1px solid rgba(46,125,70,0.3); }}
                .badge-ws {{ background:{_Y2}; color:{_Y}; border:1px solid rgba(201,138,44,0.3); }}
                .badge-fallado {{ background:{_R2}; color:{_R}; border:1px solid rgba(192,57,43,0.3); }}
                .badge-operativo {{ background:{_G3}; color:{_G}; border:1px solid rgba(46,125,70,0.3); }}
            </style>
            <div style="{_CARD} padding:10px; box-sizing:border-box; width:100%; overflow:hidden;">
                {html_tbl}
            </div>
            <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
            <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
            <script>
            $(document).ready(function() {{
                $('#fallas_main_table').DataTable({{
                    "scrollX": true, "scrollY": "340px", "scrollCollapse": true,
                    "pageLength": 50, "paging": false, "order": [],
                    "language": {{ "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                    "dom": 'Bft',
                    "buttons": [{{ extend: 'copy', text: '📋 Copiar Tabla', className: 'hud-copy-btn' }}],
                    "createdRow": function(row, data, dataIndex) {{
                        if (data[7] && data[7].indexOf("⚠️") !== -1) {{
                            $(row).css("background-color", "rgba(192,57,43,0.04)");
                        }}
                    }}
                }});
            }});
            </script>
            """, height=400)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 3. TIMELINE DE FALLAS POR MES ───────────────────────────────────────
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>"
        "📅 Línea de Tiempo de Fallas (últimos 18 meses)</h6>",
        unsafe_allow_html=True
    )
    if df_bd_filtered is not None and not df_bd_filtered.empty:
        df_tl = df_bd_filtered[df_bd_filtered['FECHA_FALLA'].notna()].copy()
        df_tl['MES'] = pd.to_datetime(df_tl['FECHA_FALLA'], errors='coerce').dt.to_period('M').astype(str)
        cutoff = (fecha_eval - pd.DateOffset(months=18)).strftime('%Y-%m')
        df_tl = df_tl[df_tl['MES'] >= cutoff]
        if not df_tl.empty:
            col_razon_tl = next((c for c in ['SUB TIPO DE FALLA', 'RAZON ESPECIFICA PULL', 'RAZON_DE_PULL']
                                 if c in df_tl.columns), None)
            if col_razon_tl:
                df_tl['Causa'] = df_tl[col_razon_tl].apply(
                    lambda x: clasificar_razon_ia(str(x)) if pd.notna(x) and str(x).strip() else 'Desconocida')
            else:
                df_tl['Causa'] = 'Desconocida'
            tl_pivot = df_tl.groupby(['MES', 'Causa']).size().reset_index(name='N')
            months_all = sorted(tl_pivot['MES'].unique().tolist())
            causas_all = sorted(tl_pivot['Causa'].unique().tolist())
            pal = [_R, _Y, _G, '#5C6B73', _G2, '#C98A2C', '#223A5E', '#4CA46A']

            tl_series = []
            for i, causa in enumerate(causas_all):
                sub = tl_pivot[tl_pivot['Causa'] == causa]
                data_pts = []
                for m in months_all:
                    n = int(sub[sub['MES'] == m]['N'].values[0]) if len(sub[sub['MES'] == m]) > 0 else 0
                    if n > 0:
                        data_pts.append([m, n])
                if data_pts:
                    c = pal[i % len(pal)]
                    tl_series.append({
                        "name": causa, "type": "bar", "stack": "total",
                        "data": [int(sub[sub['MES'] == m]['N'].values[0]) if len(sub[sub['MES'] == m]) > 0 else 0
                                 for m in months_all],
                        "itemStyle": {"color": c, "borderRadius": [3, 3, 0, 0] if causa == causas_all[-1] else [0, 0, 0, 0]},
                        "label": {"show": False}
                    })

            tl_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "", "left": "center", "top": 4},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"data": causas_all, "bottom": 4,
                           "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle",
                           "type": "scroll"},
                "grid": {"left": "3%", "right": "4%", "bottom": "20%", "top": "8%", "containLabel": True},
                "xAxis": {"type": "category", "data": months_all,
                          "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif", "rotate": 30}},
                "yAxis": {"type": "value", "name": "Fallas",
                          "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                          "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                          "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                "series": tl_series
            }
            components.html(_echarts(tl_opts, 280, "fallas-timeline"), height=290)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # ── 4. PLAN DE ACCIÓN (Cards Visuales) ─────────────────────────────────
    st.markdown(
        f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800;"
        "letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:10px;'>"
        "📋 Plan de Acción y Mitigación de Fallas</h6>",
        unsafe_allow_html=True
    )
    plan_cols = st.columns(3)
    plan_items = [
        ("plan_bombas",    "input_bombas",    "⚙️", "Tecnología de Bombas",        "Metalurgia y recubrimientos",   _G),
        ("plan_arena",     "input_arena",     "⏳", "Manejo de Sólidos",           "Equipos para arena y sólidos",  _Y),
        ("plan_proveedor", "input_proveedor", "🤝", "Gestión de Proveedores",      "Estrategia de suministro",      "#5C6B73"),
    ]
    for col, (sk, wk, icon, title, sub, color) in zip(plan_cols, plan_items):
        with col:
            st.markdown(f"""
            <div style="{_CARD} padding:12px 16px 8px; margin-bottom:8px;">
                <div style="font-size:1.2rem; margin-bottom:2px;">{icon}</div>
                <div style="font-family:{_FS}; font-size:11px; font-weight:800;
                    letter-spacing:0.6px; text-transform:uppercase; color:{color}; margin-bottom:2px;">{title}</div>
                <div style="font-family:{_FS}; font-size:10px; color:{_T2}; margin-bottom:6px;">{sub}</div>
            </div>""", unsafe_allow_html=True)
            st.session_state[sk] = st.text_area(f"Plan {title}", value=st.session_state[sk], key=wk,
                                                height=80, label_visibility="collapsed")

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # ── 5. DETALLE HISTÓRICO COMPLETO ───────────────────────────────────────
    with st.expander("📝 REGISTRO DETALLADO DE FALLAS & ANÁLISIS", expanded=False):
        if not reporte_fallas.empty:
            render_hud_table(reporte_fallas.head(100))
        else:
            st.info("No hay detalles adicionales.")
