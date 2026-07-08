"""
tabs/tab_fallas.py
==================
Análisis de Fallas con Estética HUD.
Visualización de severidad, distribución temporal y clasificación IA.
Typology aligned with 'Indices & Fallas' (Spectacular UI).
"""

import json
from datetime import timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from data.config import COLOR_PRINCIPAL
from core.calculations import clasificar_razon_ia, highlight_problema
from ui.styles import render_hud_table

def clasificar_runlife(rl):
    """Categoriza el Run Life en etapas HUD."""
    try: rl = float(rl)
    except: return 'N/A'
    if rl <= 30: return 'Infantil'
    if rl <= 90: return 'Prematura'
    if rl <= 1100: return 'En Garantía'
    return 'Sin Garantía'

def render_tab_fallas(df_bd_filtered, fecha_evaluacion):
    """Renderiza el Tab FALLAS con alta densidad HUD Profesional."""
    if 'plan_bombas' not in st.session_state:
        st.session_state['plan_bombas'] = "Uso de bombas con coating y recubrimiento en carburo de tungsteno y nitruración"
    if 'plan_arena' not in st.session_state:
        st.session_state['plan_arena'] = "Uso de equipo para arena como Sand Lift, Sand Maze, etc."
    if 'plan_proveedor' not in st.session_state:
        st.session_state['plan_proveedor'] = "Cambio de proveedor para componentes críticos"
    
    if st.session_state.get('reporte_fallas') is None or st.session_state['reporte_fallas'].empty:
        st.info("Sin datos de fallas.")
        return

    reporte_fallas = st.session_state['reporte_fallas']
    fecha_eval = pd.to_datetime(fecha_evaluacion)
    
    # 1. KPI GRID: HISTÓRICO | PERIODO EVALUADO
    # --- Cálculos ---
    total_fallas_rango = len(reporte_fallas)
    fallas_als = df_bd_filtered[df_bd_filtered['INDICADOR_MTBF'] == 1].shape[0] if df_bd_filtered is not None else 0

    fecha_ini_str = st.session_state.get('fecha_inicio_state')
    fecha_ini_dt = pd.to_datetime(fecha_ini_str).normalize() if fecha_ini_str else fecha_eval - pd.DateOffset(years=1)
    fecha_ini_label = fecha_ini_dt.strftime('%d/%m/%Y')
    fecha_eval_label = fecha_eval.strftime('%d/%m/%Y')

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
    else:
        fallas_als_periodo = 0
        fallas_periodo = 0

    col_hist, col_peri = st.columns(2)

    with col_hist:
        st.markdown("""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <div style="flex:1; height:1px; background:rgba(91,92,85,0.2);"></div>
                <span style="color:#5b5c55; font-size:9px; font-weight:700; letter-spacing:2px; text-transform:uppercase; font-family:Arial,sans-serif;">📁 HISTÓRICO GENERAL</span>
                <div style="flex:1; height:1px; background:rgba(91,92,85,0.2);"></div>
            </div>""", unsafe_allow_html=True)
        hc1, hc2 = st.columns(2)
        with hc1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🚨</div><div class="kpi-label">TOTAL EVENTOS</div><div class="kpi-value" style="color:#137659;">{total_fallas_rango}</div></div>', unsafe_allow_html=True)
        with hc2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚙️</div><div class="kpi-label">FALLAS ALS</div><div class="kpi-value" style="color:#095139;">{fallas_als}</div></div>', unsafe_allow_html=True)

    with col_peri:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <div style="flex:1; height:1px; background:rgba(19,118,89,0.3);"></div>
                <span style="color:#137659; font-size:9px; font-weight:700; letter-spacing:2px; text-transform:uppercase; font-family:Arial,sans-serif;">📅 PERIODO: {fecha_ini_label} → {fecha_eval_label}</span>
                <div style="flex:1; height:1px; background:rgba(19,118,89,0.3);"></div>
            </div>""", unsafe_allow_html=True)
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown(f'<div class="kpi-card" style="border-color:rgba(19,118,89,0.4);"><div class="kpi-icon">🔥</div><div class="kpi-label">FALLAS ALS PERIODO</div><div class="kpi-value" style="color:#c09c2e;">{fallas_als_periodo}</div></div>', unsafe_allow_html=True)
        with pc2:
            st.markdown(f'<div class="kpi-card" style="border-color:rgba(19,118,89,0.4);"><div class="kpi-icon">⏳</div><div class="kpi-label">FALLAS PERIODO</div><div class="kpi-value" style="color:#137659;">{fallas_periodo}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)


    # 2. LAYOUT 25% GRÁFICA | 75% TABLA
    detalles = []
    if df_bd_filtered is not None:
        mask = (df_bd_filtered['FECHA_FALLA'] >= (fecha_eval - timedelta(days=365)))
        for _, run in df_bd_filtered[mask].iterrows():
            razon = run.get('RAZON ESPECIFICA PULL', '')
            sub_tipo = run.get('SUB TIPO DE FALLA')
            val_to_classify = sub_tipo if pd.notna(sub_tipo) and str(sub_tipo).strip() != '' else razon
            clasif = clasificar_razon_ia(str(val_to_classify)) if val_to_classify else 'Otros'
            if clasif == 'Desconocida':
                clasif = 'Otros'
            detalles.append({
                'Pozo': run['POZO'],
                'Vida': run['RUN LIFE'],
                'Clasif': clasif,
                'Etapa': clasificar_runlife(run['RUN LIFE'])
            })
    df_det = pd.DataFrame(detalles)

    col_chart, col_table = st.columns([3, 7])

    with col_chart:
        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
        if not df_det.empty:
            conteo = df_det.groupby(['Etapa', 'Clasif']).size().reset_index(name='Cant')
            etapas = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía']
            tipos = sorted(df_det['Clasif'].unique().tolist())
            
            series = []
            colors = {'Infantil': '#d32f2f', 'Prematura': '#c09c2e', 'En Garantía': '#137659', 'Sin Garantía': '#5b5c55'}
            for et in etapas:
                data = [int(conteo[(conteo['Etapa'] == et) & (conteo['Clasif'] == t)]['Cant'].values[0]) if len(conteo[(conteo['Etapa'] == et) & (conteo['Clasif'] == t)]) > 0 else None for t in tipos]
                series.append({
                    "name": et, "type": "bar", "stack": "total", "data": data,
                    "label": {"show": True, "position": "inside", "color": "#ffffff", "fontSize": 11, "fontWeight": "bold"},
                    "itemStyle": {"color": colors.get(et), "borderRadius": [2, 2, 0, 0]}
                })

            echarts_dist = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "DISTRIBUCIÓN\nETAPA DE VIDA",
                    "left": "center",
                    "top": 0,
                    "textStyle": {
                        "color": "#137659",
                        "fontSize": 11,
                        "fontFamily": "Arial, sans-serif",
                        "fontWeight": "bold"
                    }
                },
                "textStyle": {"fontFamily": "Arial, sans-serif"},
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(255, 255, 255, 0.95)",
                    "borderColor": "#137659",
                    "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}
                },
                "legend": {"bottom": 0, "textStyle": {"color": "#475569", "fontSize": 9, "fontFamily": "Arial, sans-serif"}, "icon": "circle"},
                "grid": {"left": "3%", "right": "4%", "bottom": "20%", "top": "8%", "containLabel": True},
                "xAxis": [{"type": "category", "data": tipos, "axisLabel": {"color": "#475569", "rotate": 25, "fontSize": 9, "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [{"type": "value", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif", "fontSize": 9}, "splitLine": {"lineStyle": {"color": "rgba(19, 118, 89, 0.05)"}}}],
                "series": series
            }
            components.html(f'<div id="echarts-fallas-dist" style="width:100%; height:370px; background:#ffffff; border-radius:15px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15);"></div><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script><script>(function(){{var myChart=echarts.init(document.getElementById("echarts-fallas-dist"),null);myChart.setOption({json.dumps(echarts_dist)});window.addEventListener("resize",function(){{myChart.resize();}});}})();</script>', height=400)

    with col_table:
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
            col_razon = 'RAZON_DE_PULL' if 'RAZON_DE_PULL' in df_bd_eval.columns else ('RAZON ESPECIFICA PULL' if 'RAZON ESPECIFICA PULL' in df_bd_eval.columns else None)
            for _, row in df_bd_eval.iterrows():
                pozo = str(row.get('POZO', ''))
                fr = row.get('FECHA_RUN')
                fr_str = fr.strftime('%Y-%m-%d') if pd.notna(fr) else ''
                ff = row.get('FECHA_FALLA')
                ff_str = ff.strftime('%Y-%m-%d') if pd.notna(ff) else '<span style="color:#94a3b8;">-</span>'
                fp = row.get('FECHA_PULL')
                fp_str = fp.strftime('%Y-%m-%d') if pd.notna(fp) else '<span style="color:#137659; font-weight:bold;">PENDIENTE</span>'
                razon = row.get(col_razon, '') if col_razon else ''
                run_val = row.get('RUN', 1)
                tipo_badge = '<span class="badge-custom badge-nuevo">PERFORADO</span>' if run_val == 1 else '<span class="badge-custom badge-ws">WELL SERVICE</span>'
                if pd.notna(ff):
                    estado_badge = '<span class="badge-custom badge-fallado">⚠️ FALLADO</span>'
                    run_life = (ff - fr).days if pd.notna(fr) else '-'
                    sub_tipo = row.get('SUB TIPO DE FALLA')
                    if pd.notna(sub_tipo) and str(sub_tipo).strip() != '':
                        causa = clasificar_razon_ia(str(sub_tipo))
                    else:
                        causa = clasificar_razon_ia(str(razon)) if pd.notna(razon) and str(razon).strip() != '' else 'Desconocida'
                        if pd.isna(fp):
                            causa = f"Posible {causa}"
                else:
                    estado_badge = '<span class="badge-custom badge-operativo">✅ OPERATIVO</span>'
                    run_life = '<span style="color:#94a3b8;">-</span>'
                    causa = '<span style="color:#94a3b8;">-</span>'
                rows.append({'Pozo': pozo, 'Fecha Run': fr_str, 'Fecha Falla': ff_str, 'Fecha Pull': fp_str,
                             'Run Life (días)': str(run_life), 'Causa Raíz': causa, 'Tipo': tipo_badge, 'Estado': estado_badge})

            # Ordenar para que '⚠️ FALLADO' aparezca primero
            rows = sorted(rows, key=lambda x: 0 if '⚠️ FALLADO' in x['Estado'] else 1)
            df_html = pd.DataFrame(rows)
            html_table = df_html.to_html(index=False, table_id="fallas_main_table", classes='display nowrap hud-table', escape=False)

            components.html(f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap');
                @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
                @import url('https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css');
                body {{ margin:0; padding:0; background: transparent; color: #1f221e; font-family: 'Montserrat', sans-serif; }}
                .dataTables_wrapper {{ color: #1f221e !important; width:100% !important; }}
                .dataTables_filter input {{ background: #ffffff; border: 1px solid #137659; color: #1f221e; border-radius: 5px; padding: 4px 8px; font-size:11px; }}
                .dataTables_filter label {{ color: #5b5c55; font-size:11px; }}
                button.dt-button {{
                    background: rgba(19, 118, 89, 0.08) !important;
                    border: 1px solid rgba(19, 118, 89, 0.4) !important;
                    color: #137659 !important;
                    font-family: 'Montserrat' !important;
                    font-size: 10px !important;
                    padding: 4px 12px !important;
                    border-radius: 20px !important;
                    text-transform: uppercase !important;
                    cursor: pointer;
                    transition: 0.3s;
                }}
                button.dt-button:hover {{ background: #137659 !important; color: #ffffff !important; }}
                table.dataTable {{ width: 100% !important; }}
                table.dataTable thead th {{ background: rgba(19, 118, 89, 0.1); color: #137659; font-family: 'Montserrat'; font-size: 10px; padding: 6px 8px; white-space: nowrap; }}
                table.dataTable tbody td {{ border-bottom: 1px solid rgba(19, 118, 89, 0.08); padding: 6px 8px; font-size: 11px; color: #1f221e; }}
                .dataTables_info, .dataTables_paginate {{ color: #5b5c55 !important; font-size: 10px; }}
                .dataTables_scrollBody {{ overflow-x: auto !important; }}
                .badge-custom {{ display: inline-block; padding: 2px 6px; font-size: 8px; font-weight: 700; border-radius: 10px; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap; }}
                .badge-nuevo {{ background-color: rgba(19, 118, 89, 0.12); color: #137659; border: 1px solid rgba(19, 118, 89, 0.3); }}
                .badge-ws {{ background-color: rgba(192, 156, 46, 0.12); color: #c09c2e; border: 1px solid rgba(192, 156, 46, 0.3); }}
                .badge-fallado {{ background-color: rgba(198, 40, 40, 0.12); color: #c62828; border: 1px solid rgba(198, 40, 40, 0.3); }}
                .badge-operativo {{ background-color: rgba(46, 125, 50, 0.12); color: #2e7d32; border: 1px solid rgba(46, 125, 50, 0.3); }}
            </style>
            <div style="background:#ffffff; padding:8px; border:1px solid rgba(19,118,89,0.2); border-radius:10px; box-shadow:0 2px 4px rgba(0,0,0,0.04); width:100%; box-sizing:border-box; overflow:hidden;">
                {html_table}
            </div>
            <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
            <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('#fallas_main_table').DataTable({{
                        "scrollX": true,
                        "scrollY": "320px",
                        "scrollCollapse": true,
                        "pageLength": 50,
                        "paging": false,
                        "order": [],
                        "language": {{ "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                        "dom": 'Bft',
                        "buttons": [{{ extend: 'copy', text: '📋 Copiar', className: 'hud-copy-btn' }}],
                        "createdRow": function(row, data, dataIndex) {{
                            if (data[7] && data[7].indexOf("FALLADO") !== -1) {{
                                $(row).css("background-color", "rgba(198, 40, 40, 0.05)");
                            }}
                        }}
                    }});
                }});
            </script>
            """, height=400)

    st.markdown("<br><hr style='border:0; height:1px; background:linear-gradient(to right, transparent, rgba(19, 118, 89, 0.2), transparent); margin:15px 0;'>", unsafe_allow_html=True)

    # --- 3. SECCIÓN PLAN DE ACCIÓN ---
    st.markdown("<h5 style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>📋 PLAN DE ACCIÓN Y MITIGACIÓN DE FALLAS</h5>", unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.session_state['plan_bombas'] = st.text_area(
            "⚙️ Tecnología de Bombas (Recubrimiento y Metalurgia):",
            value=st.session_state['plan_bombas'],
            key="input_bombas",
            height=100
        )
    with col_p2:
        st.session_state['plan_arena'] = st.text_area(
            "⏳ Manejo de Sólidos (Equipos para Arena):",
            value=st.session_state['plan_arena'],
            key="input_arena",
            height=100
        )
    with col_p3:
        st.session_state['plan_proveedor'] = st.text_area(
            "🤝 Gestión de Proveedores (Estrategia de Suministro):",
            value=st.session_state['plan_proveedor'],
            key="input_proveedor",
            height=100
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. DETALLE DE EVENTOS (Expander con HUD Table)
    with st.expander("📝 REGISTRO DETALLADO DE FALLAS & ANÁLISIS", expanded=False):
        if not reporte_fallas.empty:
            render_hud_table(reporte_fallas.head(100))
        else:
            st.info("No hay detalles adicionales.")
