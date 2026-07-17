"""
tabs/tab_fallas.py  —  v2.0 Análisis de Fallas Premium
=======================================================
Mejoras:
1. KPI row renovado con diseño premium y divisor de periodo
2. Pareto de causas de falla (análisis 80/20) — gráfico combinado barras + línea acumulada
3. Tabla de eventos de alto impacto (70% del ancho) — DataTables con badges
4. Timeline de eventos por mes (gráfico de burbujas / scatter temporal)
5. Plan de Acción visual — cards editables con estado e icono
6. Registro detallado en expander
"""

import json
from datetime import timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from data.config import COLOR_PRINCIPAL
from core.calculations import clasificar_razon_ia, highlight_problema
from ui.styles import render_hud_table

_G  = "#137659"
_G2 = "#0a4d34"
_Y  = "#c09c2e"
_R  = "#c62828"
_T  = "#1f221e"
_T2 = "#455a72"


def clasificar_runlife(rl):
    try: rl = float(rl)
    except: return 'N/A'
    if rl <= 30:  return 'Infantil'
    if rl <= 90:  return 'Prematura'
    if rl <= 1100: return 'En Garantía'
    return 'Sin Garantía'


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


def render_tab_fallas(df_bd_filtered, fecha_evaluacion):
    """Renderiza el Tab FALLAS con análisis profundo y estética premium."""

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

    # ── 1. KPI GRID ─────────────────────────────────────────────────────────
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

    st.markdown("""
    <style>
    .falla-kpi { background:#ffffff; border:1px solid rgba(19,118,89,0.12); border-radius:14px;
        padding:14px 16px; display:flex; flex-direction:column; align-items:center;
        text-align:center; position:relative; overflow:hidden;
        box-shadow:0 2px 8px rgba(0,0,0,0.04); transition:transform 0.2s,box-shadow 0.2s; }
    .falla-kpi:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.08); }
    .falla-kpi-lbl { font-family:'Inter',sans-serif; font-size:0.58rem; font-weight:800;
        letter-spacing:1.2px; text-transform:uppercase; color:#5b5c55; margin-bottom:4px; }
    .falla-kpi-val { font-family:'Inter',sans-serif; font-size:1.9rem; font-weight:900; line-height:1.1; }
    .falla-kpi-sub { font-family:'Inter',sans-serif; font-size:0.6rem; color:#94a3b8; margin-top:4px; }
    .section-divider { display:flex; align-items:center; gap:10px; margin:4px 0 10px; }
    .section-divider-line { flex:1; height:1px; background:rgba(19,118,89,0.15); }
    .section-divider-text { font-family:'Inter',sans-serif; font-size:0.58rem; font-weight:800;
        letter-spacing:2px; text-transform:uppercase; color:#5b5c55; white-space:nowrap; }
    </style>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="falla-kpi" style="border-top:3px solid {_G};">
            <div class="falla-kpi-lbl">Total Eventos Hist.</div>
            <div class="falla-kpi-val" style="color:{_G};">{total_fallas_rango}</div>
            <div class="falla-kpi-sub">Todos los registros</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="falla-kpi" style="border-top:3px solid {_G2};">
            <div class="falla-kpi-lbl">Fallas ALS (Total)</div>
            <div class="falla-kpi-val" style="color:{_G2};">{fallas_als}</div>
            <div class="falla-kpi-sub">INDICADOR_MTBF = 1</div></div>''', unsafe_allow_html=True)
    with c3:
        color_als = _R if inf_rate > 60 else (_Y if inf_rate > 40 else _G)
        st.markdown(f'''<div class="falla-kpi" style="border-top:3px solid {_Y};">
            <div class="falla-kpi-lbl">Periodo: {fecha_ini_label}→{fecha_eval_label}</div>
            <div class="falla-kpi-val" style="color:{_Y};">{fallas_als_periodo}</div>
            <div class="falla-kpi-sub">Fallas ALS en el periodo</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="falla-kpi" style="border-top:3px solid {color_als};">
            <div class="falla-kpi-lbl">Tasa ALS / Total</div>
            <div class="falla-kpi-val" style="color:{color_als};">{inf_rate:.0f}<span style="font-size:1rem;">%</span></div>
            <div class="falla-kpi-sub">{fallas_periodo} eventos totales periodo</div></div>''', unsafe_allow_html=True)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 2. PARETO DE CAUSAS (50%) + TABLA DE EVENTOS (50%) ─────────────────
    col_pareto, col_tabla = st.columns([5, 5], gap="medium")

    with col_pareto:
        # Construir Pareto con los datos del ultimo año
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
                                  "subtext": "Regla 80/20 — Últimos 12 meses",
                                  "left": "center", "top": 4,
                                  "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"},
                                  "subtextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
                        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                                    "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                                    "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                        "legend": {"data": ["Frecuencia", "% Acumulado"], "bottom": 0,
                                   "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                        "grid": {"left": "3%", "right": "8%", "bottom": "18%", "top": "22%", "containLabel": True},
                        "xAxis": {"type": "category", "data": conteo['Causa'].tolist(),
                                  "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif",
                                                "rotate": 25, "interval": 0}},
                        "yAxis": [
                            {"type": "value", "name": "Frecuencia",
                             "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                             "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                            {"type": "value", "name": "%Acum", "min": 0, "max": 100,
                             "axisLabel": {"formatter": "{value}%", "color": _T2, "fontFamily": "Inter, sans-serif"},
                             "splitLine": {"show": False}}
                        ],
                        "series": [
                            {"name": "Frecuencia", "type": "bar",
                             "data": [{"value": int(r), "itemStyle": {"color": bar_colors[i], "borderRadius": [5, 5, 0, 0]}}
                                       for i, r in enumerate(conteo['N'].tolist())],
                             "barWidth": "55%",
                             "label": {"show": True, "position": "top", "color": _T2,
                                       "fontFamily": "Inter, sans-serif", "fontSize": 10}},
                            {"name": "% Acumulado", "type": "line", "yAxisIndex": 1,
                             "data": conteo['Acum'].tolist(), "smooth": False,
                             "lineStyle": {"width": 2.5, "color": _Y},
                             "itemStyle": {"color": _Y}, "symbol": "circle", "symbolSize": 6,
                             "label": {"show": True, "position": "top", "formatter": "{c}%",
                                       "color": _Y, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                             # Línea vertical del 80%
                             "markLine": {"silent": True, "data": [{"yAxis": 80}],
                                          "lineStyle": {"type": "dashed", "color": _R, "width": 1.5},
                                          "label": {"show": True, "formatter": "80%", "color": _R, "fontSize": 9}}}
                        ]
                    }
                    components.html(_echarts(pareto_opts, 400, "fallas-pareto"), height=420)
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
                ff_str = ff.strftime('%Y-%m-%d') if pd.notna(ff) else '<span style="color:#94a3b8;">-</span>'
                fp    = row.get('FECHA_PULL')
                fp_str = fp.strftime('%Y-%m-%d') if pd.notna(fp) else '<span style="color:#137659;font-weight:bold;">PEND.</span>'
                razon = str(row.get(col_razon, '')) if col_razon else ''
                run_val = row.get('RUN', 1)
                tipo_badge = '<span class="badge-custom badge-nuevo">PERFORADO</span>' if run_val == 1 else '<span class="badge-custom badge-ws">WS</span>'
                if pd.notna(ff):
                    estado_badge = '<span class="badge-custom badge-fallado">⚠ FALLA</span>'
                    run_life = (ff - fr).days if pd.notna(fr) else '-'
                    sub_tipo = row.get('SUB TIPO DE FALLA')
                    if pd.notna(sub_tipo) and str(sub_tipo).strip():
                        causa = clasificar_razon_ia(str(sub_tipo))
                    else:
                        causa = clasificar_razon_ia(razon) if razon.strip() else 'Desc.'
                        if pd.isna(fp): causa = f"Posible {causa}"
                else:
                    estado_badge = '<span class="badge-custom badge-operativo">✓ OK</span>'
                    run_life = '<span style="color:#94a3b8;">-</span>'
                    causa = '<span style="color:#94a3b8;">-</span>'
                rows.append({'Pozo': pozo, 'F.Run': fr_str, 'F.Falla': ff_str, 'F.Pull': fp_str,
                             'RL(d)': str(run_life), 'Causa': causa, 'Tipo': tipo_badge, 'Estado': estado_badge})

            rows = sorted(rows, key=lambda x: 0 if '⚠' in x['Estado'] else 1)
            df_html = pd.DataFrame(rows)
            html_tbl = df_html.to_html(index=False, table_id="fallas_main_table",
                                        classes='display nowrap hud-table', escape=False)
            components.html(f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
                @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
                body {{ margin:0; padding:0; background:transparent; color:#1f221e; font-family:'Inter',sans-serif; }}
                .dataTables_wrapper {{ color:#1f221e !important; width:100% !important; }}
                .dataTables_filter input {{ background:#ffffff; border:1px solid #137659; color:#1f221e;
                    border-radius:6px; padding:4px 10px; font-size:11px; font-family:'Inter',sans-serif; }}
                .dataTables_filter label {{ color:#5b5c55; font-size:11px; font-family:'Inter',sans-serif; }}
                button.dt-button {{ background:rgba(19,118,89,0.07) !important; border:1px solid rgba(19,118,89,0.35) !important;
                    color:#137659 !important; font-family:'Inter',sans-serif !important; font-size:10px !important;
                    padding:4px 14px !important; border-radius:20px !important; text-transform:uppercase !important;
                    cursor:pointer; transition:0.25s; }}
                button.dt-button:hover {{ background:#137659 !important; color:#ffffff !important; }}
                table.dataTable {{ width:100% !important; }}
                table.dataTable thead th {{ background:rgba(19,118,89,0.08); color:#137659;
                    font-family:'Inter',sans-serif; font-size:10px; font-weight:800;
                    letter-spacing:0.8px; padding:7px 8px; white-space:nowrap; text-transform:uppercase; }}
                table.dataTable tbody td {{ border-bottom:1px solid rgba(19,118,89,0.07);
                    padding:6px 8px; font-size:11px; color:#1f221e; }}
                .dataTables_info, .dataTables_paginate {{ color:#5b5c55 !important; font-size:10px; }}
                .badge-custom {{ display:inline-block; padding:2px 7px; font-size:8px; font-weight:700;
                    border-radius:10px; text-align:center; text-transform:uppercase;
                    letter-spacing:0.5px; white-space:nowrap; font-family:'Inter',sans-serif; }}
                .badge-nuevo {{ background:rgba(19,118,89,0.1); color:#137659; border:1px solid rgba(19,118,89,0.3); }}
                .badge-ws {{ background:rgba(192,156,46,0.1); color:#c09c2e; border:1px solid rgba(192,156,46,0.3); }}
                .badge-fallado {{ background:rgba(198,40,40,0.1); color:#c62828; border:1px solid rgba(198,40,40,0.3); }}
                .badge-operativo {{ background:rgba(46,125,50,0.1); color:#2e7d32; border:1px solid rgba(46,125,50,0.3); }}
            </style>
            <div style="background:#ffffff;padding:8px;border:1px solid rgba(19,118,89,0.15);
                border-radius:12px;box-shadow:0 2px 6px rgba(0,0,0,0.04);width:100%;box-sizing:border-box;overflow:hidden;">
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
                    "buttons": [{{ extend: 'copy', text: '📋 Copiar', className: 'hud-copy-btn' }}],
                    "createdRow": function(row, data, dataIndex) {{
                        if (data[7] && data[7].indexOf("⚠") !== -1) {{
                            $(row).css("background-color", "rgba(198,40,40,0.04)");
                        }}
                    }}
                }});
            }});
            </script>
            """, height=430)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 3. TIMELINE DE FALLAS POR MES ───────────────────────────────────────
    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:0.7rem;font-weight:800;"
        "letter-spacing:1.5px;text-transform:uppercase;color:#137659;margin-bottom:8px;'>"
        "📅 Línea de Tiempo de Fallas (últimos 18 meses)</div>",
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
            pal = [_R, _Y, _G, '#5b5c55', '#095139', '#a28834', '#c09c2e', '#2e7d32']

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
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"data": causas_all, "bottom": 0,
                           "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle",
                           "type": "scroll"},
                "grid": {"left": "3%", "right": "4%", "bottom": "22%", "top": "8%", "containLabel": True},
                "xAxis": {"type": "category", "data": months_all,
                          "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif", "rotate": 30}},
                "yAxis": {"type": "value", "name": "Fallas",
                          "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                          "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                "series": tl_series
            }
            components.html(_echarts(tl_opts, 280, "fallas-timeline"), height=300)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 4. PLAN DE ACCIÓN (Cards Visuales) ─────────────────────────────────
    st.markdown(
        "<div style='font-family:Inter,sans-serif;font-size:0.7rem;font-weight:800;"
        "letter-spacing:1.5px;text-transform:uppercase;color:#137659;margin-bottom:10px;'>"
        "📋 Plan de Acción y Mitigación de Fallas</div>",
        unsafe_allow_html=True
    )
    plan_cols = st.columns(3)
    plan_items = [
        ("plan_bombas",    "input_bombas",    "⚙️", "Tecnología de Bombas",        "Metalurgia y recubrimientos",   _G),
        ("plan_arena",     "input_arena",     "⏳", "Manejo de Sólidos",           "Equipos para arena y sólidos",  _Y),
        ("plan_proveedor", "input_proveedor", "🤝", "Gestión de Proveedores",      "Estrategia de suministro",      "#5b5c55"),
    ]
    for col, (sk, wk, icon, title, sub, color) in zip(plan_cols, plan_items):
        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{color}08 0%,#ffffff 100%);
                border:1.5px solid {color}25;border-top:3px solid {color};border-radius:12px;
                padding:10px 14px 6px;margin-bottom:6px;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-family:'Inter',sans-serif;font-size:1.1rem;">{icon}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.62rem;font-weight:800;
                    letter-spacing:1px;text-transform:uppercase;color:{color};margin:4px 0 1px;">{title}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#94a3b8;">{sub}</div>
            </div>""", unsafe_allow_html=True)
            st.session_state[sk] = st.text_area("", value=st.session_state[sk], key=wk,
                                                  height=80, label_visibility="collapsed")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # ── 5. DETALLE HISTÓRICO COMPLETO ───────────────────────────────────────
    with st.expander("📝 REGISTRO DETALLADO DE FALLAS & ANÁLISIS", expanded=False):
        if not reporte_fallas.empty:
            render_hud_table(reporte_fallas.head(100))
        else:
            st.info("No hay detalles adicionales.")
