"""
tabs/tab_indices.py
===================
Visualización profesional de Índices de Falla y Operatividad.
Utiliza estética HUD y Zero Space Waste.
"""

import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go_fig
from config import COLOR_PRINCIPAL
from indice_falla import calcular_indice_falla_anual
from styles import render_hud_table
from calculations import clasificar_razon_ia

def render_general_table(df_bd, table_id="general_table"):
    """Renderiza la tabla de detalles generales con estilo HUD (scrollX activado)."""
    if df_bd.empty:
        st.info("Sin datos para mostrar en la tabla.")
        return

    # Preparamos los datos
    rows = []
    col_razon = 'RAZON_DE_PULL' if 'RAZON_DE_PULL' in df_bd.columns else ('RAZON ESPECIFICA PULL' if 'RAZON ESPECIFICA PULL' in df_bd.columns else None)
    
    for _, row in df_bd.iterrows():
        pozo = str(row.get('POZO', ''))
        
        fr = row.get('FECHA_RUN')
        fr_str = fr.strftime('%Y-%m-%d') if pd.notna(fr) else ''
        
        ff = row.get('FECHA_FALLA')
        ff_str = ff.strftime('%Y-%m-%d') if pd.notna(ff) else '<span style="color:#94a3b8;">-</span>'
        
        fp = row.get('FECHA_PULL')
        fp_str = fp.strftime('%Y-%m-%d') if pd.notna(fp) else '<span style="color:#137659; font-weight:bold;">PENDIENTE</span>'
        
        razon = str(row.get(col_razon, '')) if col_razon else ''
        
        run_val = row.get('RUN', 1)
        if run_val == 1:
            tipo_badge = '<span class="badge-custom badge-nuevo">NUEVO</span>'
        else:
            tipo_badge = '<span class="badge-custom badge-ws">WELL SERVICE</span>'
            
        is_falla = 1 if pd.notna(ff) else 0
        if is_falla == 1:
            estado_badge = '<span class="badge-custom badge-fallado">⚠️ FALLADO</span>'
            run_life = (ff - fr).days if pd.notna(ff) and pd.notna(fr) else '-'
            causa = clasificar_razon_ia(razon) if razon.strip() != '' else 'Desconocida'
            if pd.isna(fp):
                causa = f"Posible {causa}"
        else:
            estado_badge = '<span class="badge-custom badge-operativo">✅ OPERATIVO</span>'
            run_life = '<span style="color:#94a3b8;">-</span>'
            causa = '<span style="color:#94a3b8;">-</span>'
            
        rows.append({
            'Pozo': pozo,
            'Fecha Run': fr_str,
            'Fecha Falla': ff_str,
            'Fecha Pull': fp_str,
            'Run Life (días)': str(run_life),
            'Causa Raíz': causa,
            'Tipo': tipo_badge,
            'Estado': estado_badge
        })
        
    df_html = pd.DataFrame(rows)
    html_table = df_html.to_html(index=False, table_id=table_id, classes='display nowrap hud-table', escape=False)
    
    components.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;700&display=swap');
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        @import url('https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css');
        
        body {{ background: transparent; color: #1f221e; font-family: 'Montserrat', sans-serif; }}
        .dataTables_wrapper {{ color: #1f221e !important; }}
        .dataTables_filter input {{ background: #ffffff; border: 1px solid #137659; color: #1f221e; border-radius: 5px; padding: 5px; }}
        
        button.dt-button {{
            background: rgba(19, 118, 89, 0.08) !important;
            border: 1px solid rgba(19, 118, 89, 0.4) !important;
            color: #137659 !important;
            font-family: 'Montserrat' !important;
            font-size: 10px !important;
            padding: 5px 15px !important;
            border-radius: 20px !important;
            text-transform: uppercase !important;
            cursor: pointer;
            transition: 0.3s;
        }}
        button.dt-button:hover {{
            background: #137659 !important;
            color: #ffffff !important;
        }}

        table.dataTable thead th {{ background: rgba(19, 118, 89, 0.1); color: #137659; font-family: 'Montserrat'; font-size: 11px; }}
        table.dataTable tbody td {{ border-bottom: 1px solid rgba(19, 118, 89, 0.08); padding: 8px; font-size: 12px; color: #1f221e; }}
        .dataTables_info, .dataTables_paginate {{ color: #5b5c55 !important; font-size: 11px; }}
        
        /* Badges */
        .badge-custom {{
            display: inline-block;
            padding: 3px 8px;
            font-size: 9px;
            font-weight: 700;
            border-radius: 12px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge-nuevo {{
            background-color: rgba(19, 118, 89, 0.12);
            color: #137659;
            border: 1px solid rgba(19, 118, 89, 0.3);
        }}
        .badge-ws {{
            background-color: rgba(192, 156, 46, 0.12);
            color: #c09c2e;
            border: 1px solid rgba(192, 156, 46, 0.3);
        }}
        .badge-fallado {{
            background-color: rgba(198, 40, 40, 0.12);
            color: #c62828;
            border: 1px solid rgba(198, 40, 40, 0.3);
        }}
        .badge-operativo {{
            background-color: rgba(46, 125, 50, 0.12);
            color: #2e7d32;
            border: 1px solid rgba(46, 125, 50, 0.3);
        }}
    </style>
    
    <div style="background: #ffffff; padding:10px; border:1px solid rgba(19, 118, 89, 0.2); border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.03); width: 100%; overflow-x: auto;">
        {html_table}
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('#{table_id}').DataTable({{
                "scrollX": true,
                "pageLength": 10,
                "order": [],
                "language": {{ "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                "dom": 'Bfrtip',
                "buttons": [
                    {{
                        extend: 'copy',
                        text: '📋 Copiar Tabla',
                        className: 'hud-copy-btn'
                    }}
                ],
                "createdRow": function(row, data, dataIndex) {{
                    if (data[7].indexOf("FALLADO") !== -1) {{
                        $(row).css("background-color", "rgba(198, 40, 40, 0.05)");
                        $('td', row).css("border-bottom", "1px solid rgba(198, 40, 40, 0.2)");
                    }}
                }}
            }});
        }});
    </script>
    """, height=550)

def render_tab_indices(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, selected_activo, fecha_inicio=None):
    """Renderiza el contenido completo del Tab INDICES & DATA con estilo HUD."""
    
    if df_bd_filtered.empty or df_forma9_filtered.empty:
        st.warning("Datos insuficientes para calcular índices.")
        return

    # Use the full history (date-unfiltered) for accurate rolling average calculations
    df_raw = st.session_state.get('df_bd_calculated')
    df_f9_raw = st.session_state.get('df_forma9_calculated')
    
    if df_raw is not None and df_f9_raw is not None:
        df_bd_untr = df_raw.copy()
        EXCLUIDOS = {'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL'}
        for col_filter in ('ACTIVO', 'BLOQUE', 'CAMPO'):
            if col_filter in df_bd_untr.columns and EXCLUIDOS:
                df_bd_untr = df_bd_untr[~df_bd_untr[col_filter].astype(str).str.upper().str.strip().isin(EXCLUIDOS)]
        
        _filtros = {
            'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
            'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
            'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
            'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
            'PROVEEDOR': st.session_state.get('general_proveedor_filter', 'TODOS'),
            'NICK':      st.session_state.get('general_nick_filter',      'TODOS'),
        }
        for col, val in _filtros.items():
            if val != 'TODOS' and col in df_bd_untr.columns:
                df_bd_untr = df_bd_untr[df_bd_untr[col] == val]
                
        df_forma9_untr = df_f9_raw.copy()
        pozos_en_resumen = df_bd_untr['POZO'].unique() if 'POZO' in df_bd_untr.columns else []
        df_forma9_untr = df_forma9_untr[df_forma9_untr['POZO'].isin(pozos_en_resumen)].copy()
    else:
        df_bd_untr = df_bd_filtered.copy()
        df_forma9_untr = df_forma9_filtered.copy()

    try:
        indice_resumen_df, df_mensual_hist = calcular_indice_falla_anual(
            df_bd_untr,
            df_forma9_untr,
            fecha_evaluacion,
            fecha_inicio
        )
        
        # --- 1. KPI SEMÁFOROS PREMIUM con comparativa vs mes anterior ---
        st.markdown("""
        <style>
        .if-semaforo { background:#ffffff; border:1px solid rgba(19,118,89,0.12); border-radius:16px;
            padding:14px 16px; display:flex; flex-direction:column; align-items:center; text-align:center;
            position:relative; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.04);
            transition:transform 0.2s,box-shadow 0.2s; }
        .if-semaforo:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(0,0,0,0.08); }
        .if-sem-lbl { font-family:'Inter',sans-serif; font-size:0.58rem; font-weight:800;
            letter-spacing:1.2px; text-transform:uppercase; color:#5b5c55; margin-bottom:6px; }
        .if-sem-val { font-family:'Inter',sans-serif; font-size:2rem; font-weight:900; line-height:1.1; }
        .if-sem-dot { width:12px; height:12px; border-radius:50%; margin:6px auto 2px;
            box-shadow:0 0 8px currentColor; }
        .if-sem-delta { font-family:'Inter',sans-serif; font-size:0.65rem; font-weight:700;
            padding:2px 8px; border-radius:20px; margin-top:4px; display:inline-block; }
        .if-sem-sub { font-family:'Inter',sans-serif; font-size:0.58rem; color:#94a3b8; margin-top:3px; }
        </style>""", unsafe_allow_html=True)

        def get_val_num(ind_name):
            """Retorna el IF como número flotante (0-1)."""
            try:
                raw = indice_resumen_df[indice_resumen_df['Indicador'] == ind_name]['Valor'].values[0]
                return float(str(raw).replace('%','').strip()) / 100
            except: return 0.0

        def get_prev_if(col_name, df_hist):
            """Retorna el IF del mes anterior (penúltimo mes disponible)."""
            try:
                vals = df_mensual_hist[col_name].dropna().values
                return float(vals[-2]) if len(vals) >= 2 else float(vals[-1])
            except: return 0.0

        META_IF = 0.075  # 7.5%

        def _semaforo_card(label, val_num, prev_num, meta=META_IF):
            """Construye un KPI card con semáforo y delta."""
            if val_num <= meta:          color = '#137659';  dot_label = '● VERDE'
            elif val_num <= meta * 1.33: color = '#c09c2e';  dot_label = '● ALERTA'
            else:                         color = '#c62828';  dot_label = '● ROJO'
            delta = val_num - prev_num
            delta_s = f"{'▲' if delta > 0 else '▼'} {abs(delta)*100:.2f}pp vs mes ant."
            delta_c = '#c62828' if delta > 0 else '#137659'
            return f"""<div class="if-semaforo" style="border-top:3px solid {color};">
                <div class="if-sem-lbl">{label}</div>
                <div class="if-sem-val" style="color:{color};">{val_num*100:.2f}<span style="font-size:1rem;">%</span></div>
                <div class="if-sem-dot" style="background:{color};color:{color};"></div>
                <span style="font-family:'Inter',sans-serif;font-size:0.6rem;font-weight:700;color:{color};">{dot_label}</span>
                <div class="if-sem-delta" style="background:{delta_c}15;color:{delta_c};border:1px solid {delta_c}40;">{delta_s}</div>
                <div class="if-sem-sub">Meta: {meta*100:.1f}%</div>
            </div>"""

        if_on    = get_val_num('Índice de Falla Total')
        if_als   = get_val_num('Índice de Falla ALS')
        if_on2   = get_val_num('Índice de Falla ON')
        if_als2  = get_val_num('Índice de Falla ALS ON')
        prev_on  = get_prev_if('Indice_Falla_Rolling_ON', df_mensual_hist)
        prev_als = get_prev_if('Indice_Falla_Rolling_ALS_ON', df_mensual_hist)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(_semaforo_card('I.F. Total (Rolling)', if_on, prev_on), unsafe_allow_html=True)
        with c2: st.markdown(_semaforo_card('I.F. ALS (Rolling)', if_als, prev_als), unsafe_allow_html=True)
        with c3: st.markdown(_semaforo_card('I.F. ON (Pozos ON)', if_on2, prev_on), unsafe_allow_html=True)
        with c4: st.markdown(_semaforo_card('I.F. ALS ON (<1500d)', if_als2, prev_als), unsafe_allow_html=True)

        st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

        # --- 2. GRÁFICOS DE TENDENCIA ---
        df_mensual_grafico = df_mensual_hist.copy()
        if fecha_inicio is None:
            fecha_inicio = st.session_state.get('fecha_inicio_state')
        if fecha_inicio is not None:
            limite_inicio = pd.to_datetime(fecha_inicio).strftime('%Y-%m')
            df_mensual_grafico = df_mensual_grafico[df_mensual_grafico['Mes'] >= limite_inicio].copy()

        months_idx = [str(m) for m in df_mensual_grafico['Mes']]
        val_if_on  = [round(float(x)*100, 2) for x in df_mensual_grafico['Indice_Falla_Rolling_ON'].tolist()]
        val_if_als = [round(float(x)*100, 2) for x in df_mensual_grafico['Indice_Falla_Rolling_ALS_ON'].tolist()]
        val_if_on_1500  = [round(float(x)*100, 2) for x in df_mensual_grafico.get('Indice_Falla_Rolling_ON_1500',  pd.Series([0]*len(df_mensual_grafico))).tolist()]
        val_if_als_1500 = [round(float(x)*100, 2) for x in df_mensual_grafico.get('Indice_Falla_Rolling_ALS_ON_1500', pd.Series([0]*len(df_mensual_grafico))).tolist()]

        g_left, g_right = st.columns(2)

        with g_left:
            # Calcular media + desviación estándar para alertas estadísticas
            import json as _json
            import numpy as _np
            if_arr = _np.array(val_if_on, dtype=float)
            if_mean = float(_np.nanmean(if_arr)) if len(if_arr) > 0 else 0
            if_std  = float(_np.nanstd(if_arr))  if len(if_arr) > 0 else 0
            # Marcar meses con IF > mean + 1std como alertas
            alert_months = [i for i, v in enumerate(val_if_on) if v > (if_mean + if_std)]

            mark_points = []
            for idx in alert_months:
                if idx < len(months_idx):
                    mark_points.append({
                        "coord": [months_idx[idx], val_if_on[idx]],
                        "symbol": "pin", "symbolSize": 30,
                        "itemStyle": {"color": "#c62828"},
                        "label": {"show": False}
                    })

            echarts_line = {
                "backgroundColor": "transparent",
                "title": {"text": "EVOLUCIÓN DE ÍNDICES (Rolling 12M)", "left": "center", "top": 4,
                          "textStyle": {"color": "#137659", "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"},
                          "subtext": f"Media histórica: {if_mean:.2f}% | Alerta si supera {(if_mean+if_std):.2f}%",
                          "subtextStyle": {"color": "#5b5c55", "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
                "textStyle": {"fontFamily": "Inter, sans-serif"},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": "#137659",
                            "textStyle": {"color": "#1f221e", "fontFamily": "Inter, sans-serif"}, "axisPointer": {"type": "cross"}},
                "legend": {"data": ["I.F. Total", "I.F. ALS", "I.F. <1500", "I.F. ALS <1500"], "bottom": 0,
                           "textStyle": {"color": "#5b5c55", "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "3%", "right": "4%", "bottom": "18%", "top": "20%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx,
                           "axisLabel": {"color": "#5b5c55", "fontSize": 9, "fontFamily": "Inter, sans-serif", "rotate": 30}}],
                "yAxis": [{"type": "value",
                           "axisLabel": {"formatter": "{value}%", "color": "#5b5c55", "fontFamily": "Inter, sans-serif"},
                           "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}}],
                "series": [
                    {"name": "I.F. Total", "type": "line", "smooth": True, "data": val_if_on,
                     "itemStyle": {"color": "#137659"}, "lineStyle": {"width": 3},
                     "areaStyle": {"color": "rgba(19,118,89,0.06)"},
                     "markPoint": {"data": mark_points, "label": {"show": False}},
                     "markLine": {"silent": True, "data": [
                         {"yAxis": 7.5, "label": {"show": True, "formatter": "Meta 7.5%",
                                                   "color": "#c62828", "fontSize": 9},
                          "lineStyle": {"color": "#c62828", "type": "dashed", "width": 2}}
                     ]}},
                    {"name": "I.F. ALS", "type": "line", "smooth": True, "data": val_if_als,
                     "itemStyle": {"color": "#c09c2e"}, "lineStyle": {"width": 3}},
                    {"name": "I.F. <1500", "type": "line", "smooth": True, "data": val_if_on_1500,
                     "itemStyle": {"color": "#5b5c55"}, "lineStyle": {"width": 2, "type": "dashed"}},
                    {"name": "I.F. ALS <1500", "type": "line", "smooth": True, "data": val_if_als_1500,
                     "itemStyle": {"color": "#095139"}, "lineStyle": {"width": 2, "type": "dashed"}}
                ]
            }
            components.html(f'<div id="echarts-if-line" style="width:100%;height:370px;background:#ffffff;'
                            f'border-radius:14px;overflow:hidden;border:1px solid rgba(19,118,89,0.13);'
                            f'box-shadow:0 2px 8px rgba(0,0,0,0.04);"></div>'
                            f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
                            f'<script>(function(){{var c=echarts.init(document.getElementById("echarts-if-line"),null);'
                            f'c.setOption({_json.dumps(echarts_line)});'
                            f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>',
                            height=380)

        with g_right:
            p_ops  = df_mensual_grafico['Pozos Operativos'].tolist()
            f_tots = df_mensual_grafico['Fallas Totales'].tolist()
            echarts_op = {
                "backgroundColor": "transparent",
                "title": {"text": "TENDENCIA OPERATIVIDAD VS EVENTOS", "left": "center", "top": 0,
                          "textStyle": {"color": "#137659", "fontSize": 13, "fontFamily": "Arial, sans-serif", "fontWeight": "bold"}},
                "textStyle": {"fontFamily": "Arial, sans-serif"},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.95)", "borderColor": "#137659",
                            "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}},
                "legend": {"data": ["Pozos Operativos", "Eventos Totales"], "bottom": 0,
                           "textStyle": {"color": "#475569", "fontSize": 10, "fontFamily": "Arial, sans-serif"}, "icon": "circle"},
                "grid": {"left": "3%", "right": "8%", "bottom": "18%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": "#475569", "fontSize": 9, "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [
                    {"type": "value", "name": "POZOS",   "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}, "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.05)"}}},
                    {"type": "value", "name": "EVENTOS", "position": "right", "axisLabel": {"color": "#475569", "fontFamily": "Arial, sans-serif"}, "splitLine": {"show": False}}
                ],
                "series": [
                    {"name": "Pozos Operativos", "type": "line", "smooth": True, "data": p_ops,
                     "itemStyle": {"color": "#137659"}, "lineStyle": {"width": 3},
                     "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                             "colorStops": [{"offset": 0, "color": "rgba(19,118,89,0.15)"}, {"offset": 1, "color": "transparent"}]}}},
                    {"name": "Eventos Totales", "type": "bar", "yAxisIndex": 1, "data": f_tots,
                     "itemStyle": {"color": "rgba(192,156,46,0.8)", "borderRadius": [4, 4, 0, 0]}}
                ]
            }
            components.html(f'<div id="echarts-op-fallas" style="width:100%;height:360px;background:#ffffff;border-radius:15px;overflow:hidden;border:1px solid rgba(19,118,89,0.15);"></div>'
                            f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
                            f'<script>(function(){{var c=echarts.init(document.getElementById("echarts-op-fallas"),null);c.setOption({_json.dumps(echarts_op)});window.addEventListener("resize",function(){{c.resize();}});}})();</script>',
                            height=380)

        # --- 3. ÍNDICES DE FALLA Y RUN LIFE POR BLOQUE ---
        _filtro_activo = (
            st.session_state.get('general_bloque_filter', 'TODOS') != 'TODOS' or
            st.session_state.get('general_campo_filter', 'TODOS') != 'TODOS'
        )
        bloques_if = []
        fecha_eval_dt_b = pd.to_datetime(fecha_evaluacion)
        anio_eval = fecha_eval_dt_b.year
        anio_prev = anio_eval - 1

        if not _filtro_activo:
            col_b_head, col_b_sel = st.columns([1, 1])
            with col_b_head:
                st.markdown(f"<h6 style='color:#137659; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.8rem; margin-top:6px; margin-bottom:10px;'>📊 Índice de Falla por Bloque (Rolling 12M a {fecha_eval_dt_b.strftime('%Y-%m-%d')})</h6>", unsafe_allow_html=True)
            with col_b_sel:
                opcion_if_bloque = st.radio(
                    "Tipo de Falla por Bloque:",
                    options=["Fallas ALS", "Fallas Totales"],
                    index=0,
                    horizontal=True,
                    key="if_bloque_metric_selector"
                )

            try:
                df_bloque_raw = df_bd_untr.copy()

                # Excluir pozos/equipos entregados y Flujo Natural
                mask_entregado_blk = pd.Series(False, index=df_bloque_raw.index)
                for col in df_bloque_raw.columns:
                    mask_entregado_blk |= df_bloque_raw[col].astype(str).str.upper().str.contains('ENTREGAD', na=False)
                df_bloque_raw = df_bloque_raw[~mask_entregado_blk].copy()

                for col_als in ('ALS', 'SISTEMA ALS', 'SISTEMA_ALS', 'METODO', 'METODO DE LEVANTAMIENTO'):
                    if col_als in df_bloque_raw.columns:
                        es_fn_blk = df_bloque_raw[col_als].astype(str).str.strip().str.upper().isin(
                            ['FN', 'FLUJO NATURAL', 'FLUJO_NATURAL', 'F.N.', 'FLUJO NAT']
                        )
                        df_bloque_raw = df_bloque_raw[~es_fn_blk].copy()

                df_bloque_raw['FECHA_RUN'] = pd.to_datetime(df_bloque_raw['FECHA_RUN'], errors='coerce')
                df_bloque_raw['FECHA_FALLA'] = pd.to_datetime(df_bloque_raw['FECHA_FALLA'], errors='coerce')
                df_bloque_raw['FECHA_PULL'] = pd.to_datetime(df_bloque_raw['FECHA_PULL'], errors='coerce')
                df_bloque_raw['_RUN'] = df_bloque_raw['FECHA_RUN'].dt.normalize()
                df_bloque_raw['_FALL'] = df_bloque_raw['FECHA_FALLA'].dt.normalize()
                df_bloque_raw['_PULL'] = df_bloque_raw['FECHA_PULL'].dt.normalize()

                if 'RUN_LIFE_EFECTIVO' not in df_bloque_raw.columns:
                    df_bloque_raw['RUN_LIFE_EFECTIVO'] = df_bloque_raw['RUN LIFE'] if 'RUN LIFE' in df_bloque_raw.columns else 0
                df_bloque_raw['RUN_LIFE_EFECTIVO'] = pd.to_numeric(df_bloque_raw['RUN_LIFE_EFECTIVO'], errors='coerce').fillna(0)

                calc_rle = (df_bloque_raw['FECHA_FALLA'] - df_bloque_raw['FECHA_RUN']).dt.days
                df_bloque_raw['_RLE'] = np.where(df_bloque_raw['RUN_LIFE_EFECTIVO'] > 0, df_bloque_raw['RUN_LIFE_EFECTIVO'], calc_rle.fillna(0))

                if 'INDICADOR_MTBF' not in df_bloque_raw.columns:
                    df_bloque_raw['INDICADOR_MTBF'] = 0

                if df_forma9_untr is not None and not df_forma9_untr.empty:
                    df_f9_b = df_forma9_untr.copy()
                    df_f9_b['FECHA_FORMA9'] = pd.to_datetime(df_f9_b['FECHA_FORMA9'], errors='coerce')
                    df_f9_b['FECHA_FORMA9_NORM'] = df_f9_b['FECHA_FORMA9'].dt.normalize()
                else:
                    df_f9_b = None

                fecha_eval_norm_b = fecha_eval_dt_b.normalize()
                first_month_b = (fecha_eval_norm_b.replace(day=1) - pd.DateOffset(months=11)).normalize()

                prev_year_start = pd.to_datetime(f"{anio_prev}-01-01").normalize()
                prev_year_end = pd.to_datetime(f"{anio_prev}-12-31").normalize()

                for bloque, grp in df_bloque_raw.groupby('BLOQUE'):
                    EXCLUIDOS = {'TODOS', 'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL'}
                    if pd.isna(bloque) or str(bloque).strip() == '' or str(bloque).strip().upper() in EXCLUIDOS:
                        continue

                    grp_runs = grp[grp['_RUN'] <= fecha_eval_norm_b]
                    total_pozosBloque = grp_runs['POZO'].nunique() if 'POZO' in grp_runs.columns else 0
                    if total_pozosBloque == 0:
                        continue

                    # 1. Fallas en la ventana de 12 meses
                    fallas_12m_tot = grp_runs[
                        (grp_runs['_FALL'].notna()) &
                        (grp_runs['_FALL'] >= first_month_b) &
                        (grp_runs['_FALL'] <= fecha_eval_norm_b)
                    ]
                    fallas_tot = fallas_12m_tot.shape[0]
                    fallas_als = fallas_12m_tot[fallas_12m_tot['INDICADOR_MTBF'] == 1].shape[0]

                    fallas_12m_1500 = fallas_12m_tot[fallas_12m_tot['_RLE'] < 1500]
                    fallas_1500 = fallas_12m_1500.shape[0]
                    fallas_als_1500 = fallas_12m_1500[fallas_12m_1500['INDICADOR_MTBF'] == 1].shape[0]

                    fallas_12m_mas1500 = fallas_12m_tot[fallas_12m_tot['_RLE'] >= 1500]
                    fallas_mas1500 = fallas_12m_mas1500.shape[0]
                    fallas_als_mas1500 = fallas_12m_mas1500[fallas_12m_mas1500['INDICADOR_MTBF'] == 1].shape[0]

                    # 2. Fallas en el Año Anterior (Año Prev) para cálculo de Meta dinámica
                    grp_runs_prev = grp[grp['_RUN'] <= prev_year_end]
                    fallas_prev_tot_df = grp_runs_prev[
                        (grp_runs_prev['_FALL'].notna()) &
                        (grp_runs_prev['_FALL'] >= prev_year_start) &
                        (grp_runs_prev['_FALL'] <= prev_year_end)
                    ]
                    fallas_prev_tot = fallas_prev_tot_df.shape[0]
                    fallas_prev_als = fallas_prev_tot_df[fallas_prev_tot_df['INDICADOR_MTBF'] == 1].shape[0]

                    fallas_prev_1500_df = fallas_prev_tot_df[fallas_prev_tot_df['_RLE'] < 1500]
                    fallas_prev_1500 = fallas_prev_1500_df.shape[0]
                    fallas_prev_als_1500 = fallas_prev_1500_df[fallas_prev_1500_df['INDICADOR_MTBF'] == 1].shape[0]

                    fallas_prev_mas1500_df = fallas_prev_tot_df[fallas_prev_tot_df['_RLE'] >= 1500]
                    fallas_prev_mas1500 = fallas_prev_mas1500_df.shape[0]
                    fallas_prev_als_mas1500 = fallas_prev_mas1500_df[fallas_prev_mas1500_df['INDICADOR_MTBF'] == 1].shape[0]

                    # 3. Promedio de pozos activos ON por mes (12M y Año Anterior)
                    pozos_on_meses = []
                    pozos_on_prev_meses = []
                    pozos_bloque_set = set(grp_runs['POZO'].unique()) if 'POZO' in grp_runs.columns else set()

                    for i in range(12):
                        mes_start = (first_month_b + pd.DateOffset(months=i)).replace(day=1).normalize()
                        mes_end = (mes_start + pd.offsets.MonthEnd(0)).normalize()

                        if df_f9_b is not None and not df_f9_b.empty and 'FECHA_FORMA9_NORM' in df_f9_b.columns:
                            f9_mes = df_f9_b[
                                (df_f9_b['FECHA_FORMA9_NORM'] >= mes_start) &
                                (df_f9_b['FECHA_FORMA9_NORM'] <= mes_end) &
                                (df_f9_b['DIAS TRABAJADOS'] > 0)
                            ]
                            pozos_f9_set = set(f9_mes['POZO'].unique()) if 'POZO' in f9_mes.columns else set()
                            activos_set = pozos_bloque_set & pozos_f9_set
                            activos_mes = len(activos_set)
                        else:
                            grp_mes = grp_runs[grp_runs['_RUN'] <= mes_end]
                            activos_mes = grp_mes[
                                (grp_mes['_FALL'].isna()) | (grp_mes['_FALL'] > mes_end)
                            ]['POZO'].nunique() if 'POZO' in grp_mes.columns else 0

                        pozos_on_meses.append(activos_mes)

                    # Pozos ON para los 12 meses del Año Anterior
                    for m in range(1, 13):
                        p_start = pd.to_datetime(f"{anio_prev}-{m:02d}-01").normalize()
                        p_end = (p_start + pd.offsets.MonthEnd(0)).normalize()
                        if df_f9_b is not None and not df_f9_b.empty and 'FECHA_FORMA9_NORM' in df_f9_b.columns:
                            f9_m_prev = df_f9_b[
                                (df_f9_b['FECHA_FORMA9_NORM'] >= p_start) &
                                (df_f9_b['FECHA_FORMA9_NORM'] <= p_end) &
                                (df_f9_b['DIAS TRABAJADOS'] > 0)
                            ]
                            p_f9_set = set(f9_m_prev['POZO'].unique()) if 'POZO' in f9_m_prev.columns else set()
                            p_activos_set = pozos_bloque_set & p_f9_set
                            pozos_on_prev_meses.append(len(p_activos_set))
                        else:
                            grp_prev_m = grp_runs_prev[grp_runs_prev['_RUN'] <= p_end]
                            act_p = grp_prev_m[
                                (grp_prev_m['_FALL'].isna()) | (grp_prev_m['_FALL'] > p_end)
                            ]['POZO'].nunique() if 'POZO' in grp_prev_m.columns else 0
                            pozos_on_prev_meses.append(act_p)

                    promedio_on = np.mean(pozos_on_meses) if pozos_on_meses else 0
                    prom_on_prev = np.mean(pozos_on_prev_meses) if pozos_on_prev_meses else 0

                    # Denominador común Pozos ON para todos los IFs
                    if_tot_val = (fallas_tot / promedio_on * 100) if promedio_on > 0 else 0.0
                    if_als_val = (fallas_als / promedio_on * 100) if promedio_on > 0 else 0.0
                    
                    if_1500_val = (fallas_1500 / promedio_on * 100) if promedio_on > 0 else 0.0
                    if_als_1500_val = (fallas_als_1500 / promedio_on * 100) if promedio_on > 0 else 0.0

                    if_mas1500_val = (fallas_mas1500 / promedio_on * 100) if promedio_on > 0 else 0.0
                    if_als_mas1500_val = (fallas_als_mas1500 / promedio_on * 100) if promedio_on > 0 else 0.0

                    # Metas dinámicas por tipo de I.F. basadas en el año anterior
                    if_prev_tot_val = (fallas_prev_tot / prom_on_prev * 100) if prom_on_prev > 0 else 0.0
                    if_prev_als_val = (fallas_prev_als / prom_on_prev * 100) if prom_on_prev > 0 else 0.0
                    if_prev_1500_val = (fallas_prev_1500 / prom_on_prev * 100) if prom_on_prev > 0 else 0.0
                    if_prev_als_1500_val = (fallas_prev_als_1500 / prom_on_prev * 100) if prom_on_prev > 0 else 0.0
                    if_prev_mas1500_val = (fallas_prev_mas1500 / prom_on_prev * 100) if prom_on_prev > 0 else 0.0
                    if_prev_als_mas1500_val = (fallas_prev_als_mas1500 / prom_on_prev * 100) if prom_on_prev > 0 else 0.0

                    meta_tot = round(if_prev_tot_val, 2) if if_prev_tot_val > 0 else 7.5
                    meta_als = round(if_prev_als_val, 2) if if_prev_als_val > 0 else 7.5
                    meta_1500 = round(if_prev_1500_val, 2) if if_prev_1500_val > 0 else 7.5
                    meta_als_1500 = round(if_prev_als_1500_val, 2) if if_prev_als_1500_val > 0 else 7.5
                    meta_mas1500 = round(if_prev_mas1500_val, 2) if if_prev_mas1500_val > 0 else 7.5
                    meta_als_mas1500 = round(if_prev_als_mas1500_val, 2) if if_prev_als_mas1500_val > 0 else 7.5

                    # 4. Run Life por Bloque
                    grp_activos_now = grp_runs[
                        (grp_runs['_RUN'] <= fecha_eval_norm_b) &
                        (grp_runs['_FALL'].isna() | (grp_runs['_FALL'] > fecha_eval_norm_b)) &
                        (grp_runs['_PULL'].isna() | (grp_runs['_PULL'] > fecha_eval_norm_b))
                    ]
                    pozos_op_cnt = grp_activos_now['POZO'].nunique() if 'POZO' in grp_activos_now.columns else len(grp_activos_now)
                    rl_s = (fecha_eval_norm_b - grp_activos_now['_RUN']).dt.days
                    rl_val = float(rl_s.mean()) if len(rl_s) > 0 else 0.0

                    rle_s = grp_activos_now['_RLE']
                    rle_val = float(rle_s.mean()) if len(rle_s) > 0 and (rle_s > 0).any() else rl_val

                    # Pozos Fallados
                    grp_fallados_all = grp_runs[
                        (grp_runs['_FALL'].notna()) &
                        (grp_runs['_FALL'] <= fecha_eval_norm_b)
                    ]
                    pozos_fall_cnt = grp_fallados_all['POZO'].nunique() if 'POZO' in grp_fallados_all.columns else len(grp_fallados_all)
                    rl_fall_s = (grp_fallados_all['_FALL'] - grp_fallados_all['_RUN']).dt.days
                    rl_fall_val = float(rl_fall_s.mean()) if len(rl_fall_s) > 0 else 0.0
                    rle_fall_s = grp_fallados_all['_RLE']
                    rle_fall_val = float(rle_fall_s.mean()) if len(rle_fall_s) > 0 and (rle_fall_s > 0).any() else rl_fall_val

                    # Metas de Run Life del Año Anterior
                    grp_activos_prev = grp_runs_prev[
                        (grp_runs_prev['_RUN'] <= prev_year_end) &
                        (grp_runs_prev['_FALL'].isna() | (grp_runs_prev['_FALL'] > prev_year_end)) &
                        (grp_runs_prev['_PULL'].isna() | (grp_runs_prev['_PULL'] > prev_year_end))
                    ]
                    rl_prev_s = (prev_year_end - grp_activos_prev['_RUN']).dt.days
                    rl_prev_val = float(rl_prev_s.mean()) if len(rl_prev_s) > 0 else 0.0

                    rle_prev_s = grp_activos_prev['_RLE']
                    rle_prev_val = float(rle_prev_s.mean()) if len(rle_prev_s) > 0 and (rle_prev_s > 0).any() else rl_prev_val

                    meta_rl = round(rl_prev_val, 1) if rl_prev_val > 0 else 1500.0
                    meta_rle = round(rle_prev_val, 1) if rle_prev_val > 0 else 1500.0

                    bloques_if.append({
                        'bloque': str(bloque).strip(),
                        'total': total_pozosBloque,
                        'prom_on': round(promedio_on),
                        'pozos_op': pozos_op_cnt,
                        'pozos_fall': pozos_fall_cnt,
                        'fallas_tot': fallas_tot,
                        'fallas_als': fallas_als,
                        'fallas_1500': fallas_1500,
                        'fallas_als_1500': fallas_als_1500,
                        'fallas_mas1500': fallas_mas1500,
                        'fallas_als_mas1500': fallas_als_mas1500,
                        'if_total': round(if_tot_val, 2),
                        'if_als': round(if_als_val, 2),
                        'if_1500': round(if_1500_val, 2),
                        'if_als_1500': round(if_als_1500_val, 2),
                        'if_mas1500': round(if_mas1500_val, 2),
                        'if_als_mas1500': round(if_als_mas1500_val, 2),
                        'meta_tot': meta_tot,
                        'meta_als': meta_als,
                        'meta_1500': meta_1500,
                        'meta_als_1500': meta_als_1500,
                        'meta_mas1500': meta_mas1500,
                        'meta_als_mas1500': meta_als_mas1500,
                        'rl': round(rl_val, 1),
                        'rl_efectivo': round(rle_val, 1),
                        'rl_fall': round(rl_fall_val, 1),
                        'rl_fall_efectivo': round(rle_fall_val, 1),
                        'meta_rl': meta_rl,
                        'meta_rle': meta_rle
                    })

                # Preparar datos para los tres gráficos (Total, <1500d y >=1500d)
                es_als = (opcion_if_bloque == "Fallas ALS")
                
                bloques_total = []
                bloques_m1500 = []
                bloques_p1500 = []

                for d in bloques_if:
                    tot_card = {
                        'bloque': d['bloque'],
                        'total': d['total'],
                        'prom_on': d['prom_on'],
                        'fallas': d['fallas_als'] if es_als else d['fallas_tot'],
                        'if_val': d['if_als'] if es_als else d['if_total'],
                        'meta': d['meta_als'] if es_als else d['meta_tot']
                    }
                    bloques_total.append(tot_card)

                    m15 = {
                        'bloque': d['bloque'],
                        'total': d['total'],
                        'prom_on': d['prom_on'],
                        'fallas': d['fallas_als_1500'] if es_als else d['fallas_1500'],
                        'if_val': d['if_als_1500'] if es_als else d['if_1500'],
                        'meta': d['meta_als_1500'] if es_als else d['meta_1500']
                    }
                    bloques_m1500.append(m15)

                    p15 = {
                        'bloque': d['bloque'],
                        'total': d['total'],
                        'prom_on': d['prom_on'],
                        'fallas': d['fallas_als_mas1500'] if es_als else d['fallas_mas1500'],
                        'if_val': d['if_als_mas1500'] if es_als else d['if_mas1500'],
                        'meta': d['meta_als_mas1500'] if es_als else d['meta_mas1500']
                    }
                    bloques_p1500.append(p15)

                def _render_bullet_card_html(items_list, titulo_card, ocultar_c=False, es_sin_garantia=False, es_total=False):
                    items_filtered = [x for x in items_list if not (ocultar_c and x.get('if_val', 0) == 0)]
                    items_sorted = sorted(items_filtered, key=lambda x: x['if_val'], reverse=True)
                    if not items_sorted:
                        return "<div style='padding:20px; text-align:center; color:#5b5c55; font-size:12px;'>No hay bloques con datos para mostrar en esta categoría.</div>"

                    max_val = max([x['if_val'] for x in items_sorted] + [35.0])

                    rows_html = []
                    for idx, item in enumerate(items_sorted):
                        blk = item['bloque']
                        val = item['if_val']
                        meta = item['meta']

                        if val == 0:
                            bar_color = "transparent"
                            val_color = "#5b5c55"
                        elif es_sin_garantia:
                            # En pozos sin garantía (RL >= 1500d), haber alcanzado >= 1500d es un logro positivo (Verde)
                            bar_color = "#1b7a4b"
                            val_color = "#1f221e"
                        else:
                            # En pozos en garantía (RL < 1500d) o Total: fallar temprano/alto es negativo (Rojo/Ámbar)
                            if val >= 20.0 or (meta > 0 and val > meta * 1.5):
                                bar_color = "#b73229"  # Rojo (Crítico)
                                val_color = "#1f221e"
                            elif val >= 10.0 or (meta > 0 and val > meta):
                                bar_color = "#c67d26"  # Ámbar / Ocre (Alerta)
                                val_color = "#1f221e"
                            else:
                                bar_color = "#1b7a4b"  # Verde (Bajo índice de fallas)
                                val_color = "#1f221e"

                        bar_w = min(max((val / max_val) * 100, 0), 100) if val > 0 else 0
                        val_str = f"{val:.2f}%".replace('.', ',')
                        n_fallas = item.get('fallas', 0)
                        n_prom_on = item.get('prom_on', 0)
                        ratio_str = f"{n_fallas}/{n_prom_on}"

                        row_bg = "#f3f7f4" if (idx % 2 == 0) else "#ffffff"

                        row_html = (
                            f'<div style="display:flex; align-items:center; padding:6px 8px; background:{row_bg}; border-radius:4px; margin-bottom:3px; font-family:\'Inter\', sans-serif;">'
                            f'<div style="width:85px; font-size:10px; font-weight:800; color:#1f221e; text-transform:uppercase; letter-spacing:0.4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{blk} — Fallas: {n_fallas} | Pozos ON Promedio: {n_prom_on}">{blk}</div>'
                            f'<div style="flex:1; margin:0 6px; position:relative; height:14px; background:#ebebeb; border-radius:4px; display:flex; align-items:center;">'
                            f'<div style="position:absolute; left:0; top:0; bottom:0; width:{bar_w:.1f}%; background:{bar_color}; border-radius:4px; transition:width 0.4s ease;"></div>'
                            f'</div>'
                            f'<div style="min-width:85px; text-align:right; white-space:nowrap;">'
                            f'<span style="font-size:11px; font-weight:800; color:{val_color}; font-family:\'Inter\', monospace;">{val_str}</span>'
                            f'<span style="font-size:9px; font-weight:600; color:#5b5c55; font-family:\'Inter\', monospace; margin-left:3px;">({ratio_str})</span>'
                            f'</div>'
                            f'</div>'
                        )
                        rows_html.append(row_html)

                    card_html = (
                        f'<div style="background:#ffffff; border:1px solid rgba(19,118,89,0.18); border-radius:12px; padding:14px 12px; box-shadow:0 2px 10px rgba(0,0,0,0.03); margin-bottom:14px;">'
                        f'<div style="color:#0f3e2e; font-family:\'Inter\', sans-serif; font-size:11.5px; font-weight:800; letter-spacing:0.4px; text-transform:uppercase; margin-bottom:10px; line-height:1.35; padding-bottom:8px; border-bottom:1px solid rgba(19,118,89,0.12);">'
                        f'{titulo_card}'
                        f'</div>'
                        f'<div style="display:flex; flex-direction:column;">'
                        f'{"".join(rows_html)}'
                        f'</div>'
                        f'</div>'
                    )
                    return card_html

                col_top_sel1, col_top_sel2 = st.columns([2, 1])
                with col_top_sel2:
                    ocultar_0 = st.checkbox("Ocultar bloques en 0,00%", value=False, key="chk_ocultar_0_if")

                col_g1, col_g2, col_g3 = st.columns(3)
                tipo_lbl = "ALS" if es_als else "TOTAL"
                
                with col_g1:
                    lbl_tot = f"📊 ÍNDICE DE FALLA (IF) {tipo_lbl} TOTAL"
                    html_tot = _render_bullet_card_html(bloques_total, lbl_tot, ocultar_c=ocultar_0, es_total=True)
                    st.markdown(html_tot, unsafe_allow_html=True)

                with col_g2:
                    lbl_m15 = f"⏱️ ÍNDICE DE FALLA (IF) {tipo_lbl} &lt; 1500d — EN GARANTÍA"
                    html_m15 = _render_bullet_card_html(bloques_m1500, lbl_m15, ocultar_c=ocultar_0, es_sin_garantia=False)
                    st.markdown(html_m15, unsafe_allow_html=True)

                with col_g3:
                    lbl_p15 = f"🏅 ÍNDICE DE FALLA (IF) {tipo_lbl} ≥ 1500d — VIDA CUMPLIDA"
                    html_p15 = _render_bullet_card_html(bloques_p1500, lbl_p15, ocultar_c=ocultar_0, es_sin_garantia=True)
                    st.markdown(html_p15, unsafe_allow_html=True)

            except Exception as e:
                st.warning(f"No se pudo generar los gráficos de IF por Bloque: {e}")

        # Función auxiliar para calcular Run Life agrupado (por Campo o Bloque)
        def _calcular_rl_agrupado(df_raw, grupo_col, fecha_eval_norm, anio_prev_val):
            prev_yr_end = pd.to_datetime(f"{anio_prev_val}-12-31").normalize()
            EXCL_RL = {'TODOS', 'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL'}
            res_list = []
            if grupo_col not in df_raw.columns:
                return res_list
            for grupo_val, grp_sub in df_raw.groupby(grupo_col):
                if pd.isna(grupo_val) or str(grupo_val).strip() == '' or str(grupo_val).strip().upper() in EXCL_RL:
                    continue
                grp_runs_sub = grp_sub[grp_sub['_RUN'] <= fecha_eval_norm]
                tot_p = grp_runs_sub['POZO'].nunique() if 'POZO' in grp_runs_sub.columns else len(grp_runs_sub)
                if tot_p == 0:
                    continue
                
                # Pozos Operativos
                grp_op = grp_runs_sub[
                    (grp_runs_sub['_RUN'] <= fecha_eval_norm) &
                    (grp_runs_sub['_FALL'].isna() | (grp_runs_sub['_FALL'] > fecha_eval_norm)) &
                    (grp_runs_sub['_PULL'].isna() | (grp_runs_sub['_PULL'] > fecha_eval_norm))
                ]
                n_op = grp_op['POZO'].nunique() if 'POZO' in grp_op.columns else len(grp_op)
                rl_op_s = (fecha_eval_norm - grp_op['_RUN']).dt.days
                rl_op_val = float(rl_op_s.mean()) if len(rl_op_s) > 0 else 0.0
                rle_op_s = grp_op['_RLE']
                rle_op_val = float(rle_op_s.mean()) if len(rle_op_s) > 0 and (rle_op_s > 0).any() else rl_op_val

                # Pozos Fallados
                grp_fall = grp_runs_sub[
                    (grp_runs_sub['_FALL'].notna()) &
                    (grp_runs_sub['_FALL'] <= fecha_eval_norm)
                ]
                n_fall = grp_fall['POZO'].nunique() if 'POZO' in grp_fall.columns else len(grp_fall)
                rl_fall_s = (grp_fall['_FALL'] - grp_fall['_RUN']).dt.days
                rl_fall_val = float(rl_fall_s.mean()) if len(rl_fall_s) > 0 else 0.0
                rle_fall_s = grp_fall['_RLE']
                rle_fall_val = float(rle_fall_s.mean()) if len(rle_fall_s) > 0 and (rle_fall_s > 0).any() else rl_fall_val

                # Metas año anterior
                grp_prev_sub = grp_sub[grp_sub['_RUN'] <= prev_yr_end]
                grp_op_prev_sub = grp_prev_sub[
                    (grp_prev_sub['_RUN'] <= prev_yr_end) &
                    (grp_prev_sub['_FALL'].isna() | (grp_prev_sub['_FALL'] > prev_yr_end)) &
                    (grp_prev_sub['_PULL'].isna() | (grp_prev_sub['_PULL'] > prev_yr_end))
                ]
                rl_prev_sub_s = (prev_yr_end - grp_op_prev_sub['_RUN']).dt.days
                m_rl = round(float(rl_prev_sub_s.mean()), 1) if len(rl_prev_sub_s) > 0 else 1500.0
                rle_prev_sub_s = grp_op_prev_sub['_RLE']
                m_rle = round(float(rle_prev_sub_s.mean()), 1) if len(rle_prev_sub_s) > 0 and (rle_prev_sub_s > 0).any() else m_rl

                if n_op > 0 or n_fall > 0:
                    res_list.append({
                        'nombre': str(grupo_val).strip(),
                        'total': tot_p,
                        'pozos_op': n_op,
                        'pozos_fall': n_fall,
                        'rl_op': round(rl_op_val, 1),
                        'rle_op': round(rle_op_val, 1),
                        'rl_fall': round(rl_fall_val, 1),
                        'rle_fall': round(rle_fall_val, 1),
                        'meta_rl': m_rl,
                        'meta_rle': m_rle,
                    })
            return res_list

        # --- 3.1 RUN LIFE POR CAMPO / BLOQUE (COMPARATIVA OPERATIVOS VS FALLADOS) ---
        items_rl = []
        agrupacion_rl = "Campo"
        if not _filtro_activo:
            st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
            col_rl_head, col_rl_grp, col_rl_sel = st.columns([1.2, 0.9, 0.9])
            with col_rl_head:
                st.markdown(f"<h6 style='color:#137659; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.8rem; margin-top:6px; margin-bottom:10px;'>⏱️ Run Life: Pozos Operativos vs Fallados (a {fecha_eval_dt_b.strftime('%Y-%m-%d')})</h6>", unsafe_allow_html=True)
            with col_rl_grp:
                agrupacion_rl = st.radio(
                    "Agrupar por:",
                    options=["Campo", "Bloque"],
                    index=0,
                    horizontal=True,
                    key="rl_agrupacion_selector"
                )
            with col_rl_sel:
                opcion_rl_bloque = st.radio(
                    "Métrica de R.L.:",
                    options=["Run Life", "Run Life Efectivo"],
                    index=0,
                    horizontal=True,
                    key="rl_bloque_metric_selector"
                )

            try:
                grupo_col_sel = 'CAMPO' if agrupacion_rl == "Campo" else 'BLOQUE'
                items_rl = _calcular_rl_agrupado(df_bloque_raw, grupo_col_sel, fecha_eval_norm_b, anio_prev)

                for d in items_rl:
                    if opcion_rl_bloque == "Run Life Efectivo":
                        d['active_rl_op'] = d['rle_op']
                        d['active_rl_fall'] = d['rle_fall']
                        d['active_rl_meta'] = d['meta_rle']
                    else:
                        d['active_rl_op'] = d['rl_op']
                        d['active_rl_fall'] = d['rl_fall']
                        d['active_rl_meta'] = d['meta_rl']

                # Filtrar con al menos 1 pozo operativo o fallado y ordenar por pozos operativos desc
                items_rl = [d for d in items_rl if (d.get('active_rl_op', 0) > 0 or d.get('active_rl_fall', 0) > 0)]
                items_rl.sort(key=lambda x: (x['pozos_op'], x['active_rl_op']), reverse=True)

                if items_rl:
                    # Si se agrupa por campo y hay muchos, mostrar los campos más representativos o todos
                    display_items = items_rl[:35] if (len(items_rl) > 35 and agrupacion_rl == "Campo") else items_rl
                    names = [d['nombre'] for d in display_items]
                    y_op = [d['active_rl_op'] for d in display_items]
                    y_fall = [d['active_rl_fall'] for d in display_items]

                    hover_op_texts = []
                    hover_fall_texts = []
                    text_op = []
                    text_fall = []

                    for d in display_items:
                        hover_op_texts.append(
                            f"<b style='color:#137659;font-size:13px'>{d['nombre']}</b><br>"
                            f"<hr style='margin:3px 0;border-color:rgba(19,118,89,0.15)'>"
                            f"<b>🟢 POZOS OPERATIVOS:</b><br>"
                            f"• N° Pozos Activos: <b>{d['pozos_op']}</b><br>"
                            f"• Run Life Promedio: <b>{d['active_rl_op']:.1f} días</b><br>"
                            f"• Total Pozos Históricos: <b>{d['total']}</b>"
                        )
                        hover_fall_texts.append(
                            f"<b style='color:#c62828;font-size:13px'>{d['nombre']}</b><br>"
                            f"<hr style='margin:3px 0;border-color:rgba(198,40,40,0.15)'>"
                            f"<b>🔴 POZOS FALLADOS:</b><br>"
                            f"• N° Pozos Fallados: <b>{d['pozos_fall']}</b><br>"
                            f"• Run Life a Falla: <b>{d['active_rl_fall']:.1f} días</b><br>"
                            f"• Total Pozos Históricos: <b>{d['total']}</b>"
                        )
                        text_op.append(f"{d['active_rl_op']:.0f}d ({d['pozos_op']} op)" if d['active_rl_op'] > 0 else "")
                        text_fall.append(f"{d['active_rl_fall']:.0f}d ({d['pozos_fall']} fall)" if d['active_rl_fall'] > 0 else "")

                    chart_h_rl = 360 if len(names) <= 12 else max(360, min(480, len(names) * 16 + 180))

                    fig_rl_bloque = go_fig.Figure()

                    # Barra 1: Pozos Operativos
                    fig_rl_bloque.add_trace(go_fig.Bar(
                        x=names,
                        y=y_op,
                        name="🟢 Pozos Operativos (RL Actual)",
                        marker=dict(
                            color="#137659",
                            line=dict(color="#095139", width=1)
                        ),
                        text=text_op,
                        textposition="outside",
                        textfont=dict(size=9, color="#137659", family="Inter, sans-serif"),
                        hovertext=hover_op_texts,
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor="#137659",
                                        font=dict(size=10, family="Inter, sans-serif", color="#1f221e")),
                    ))

                    # Barra 2: Pozos Fallados
                    fig_rl_bloque.add_trace(go_fig.Bar(
                        x=names,
                        y=y_fall,
                        name="🔴 Pozos Fallados (RL a la Falla)",
                        marker=dict(
                            color="#c62828",
                            line=dict(color="#8e0000", width=1)
                        ),
                        text=text_fall,
                        textposition="outside",
                        textfont=dict(size=9, color="#c62828", family="Inter, sans-serif"),
                        hovertext=hover_fall_texts,
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor="#c62828",
                                        font=dict(size=10, family="Inter, sans-serif", color="#1f221e")),
                    ))

                    max_y = max(max(y_op) if y_op else 0, max(y_fall) if y_fall else 0)

                    fig_rl_bloque.update_layout(
                        barmode="group",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif"),
                        margin=dict(l=35, r=15, t=32, b=75 if len(names) > 8 else 45),
                        xaxis=dict(title="", showgrid=False, showline=True, linecolor="rgba(19,118,89,0.15)",
                                   tickfont=dict(size=9, color="#1f221e", family="Inter, sans-serif"),
                                   tickangle=-35 if len(names) > 8 else 0),
                        yaxis=dict(title=f"{opcion_rl_bloque} (días)", range=[0, max_y * 1.35] if max_y > 0 else [0, 1000],
                                   showgrid=True, gridcolor="rgba(19,118,89,0.08)", gridwidth=1,
                                   showline=False,
                                   tickfont=dict(size=8, color="#5b5c55", family="Inter, sans-serif"),
                                   ticksuffix="d"),
                        bargap=0.28,
                        bargroupgap=0.08,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=10, family="Inter, sans-serif", color="#1f221e"),
                            bgcolor="rgba(255,255,255,0.9)",
                            bordercolor="rgba(19,118,89,0.2)",
                            borderwidth=1
                        ),
                        height=chart_h_rl
                    )

                    plotly_config_rl = {
                        "displayModeBar": True,
                        "displaylogo": False,
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": f"run_life_por_{agrupacion_rl.lower()}",
                            "height": 550,
                            "width": 1100,
                            "scale": 3
                        }
                    }
                    st.plotly_chart(fig_rl_bloque, use_container_width=True, config=plotly_config_rl)
            except Exception as e:
                st.warning(f"No se pudo generar el gráfico de Run Life: {e}")

        # --- 4. DETALLE DE DATA (Expander con HUD Table Interactivas) ---
        with st.expander("📄 VER TABLA DE DATOS HISTÓRICOS Y RESUMEN", expanded=False):
            st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>RESUMEN DE ÍNDICES GENERALES</div>", unsafe_allow_html=True)
            render_hud_table(indice_resumen_df, table_id="resumen_indices")
            
            # Tabla 1: Resumen de Índices de Falla por Bloque
            if 'bloques_if' in locals() and bloques_if:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>RESUMEN DE ÍNDICES DE FALLA POR BLOQUE (ROLLING 12M)</div>", unsafe_allow_html=True)
                df_bloque_tab = pd.DataFrame([
                    {
                        'Bloque': b['bloque'],
                        'Pozos Totales': b['total'],
                        'Pozos ON (Prom)': b['prom_on'],
                        'Fallas (12M)': b['fallas_tot'],
                        'Fallas ALS (12M)': b['fallas_als'],
                        'Fallas < 1500d': b['fallas_1500'],
                        'Fallas ALS < 1500d': b['fallas_als_1500'],
                        'Fallas ≥ 1500d': b['fallas_mas1500'],
                        'Fallas ALS ≥ 1500d': b['fallas_als_mas1500'],
                        'IF Total': f"{b['if_total']:.2f}%",
                        'IF ALS': f"{b['if_als']:.2f}%",
                        'IF < 1500d': f"{b['if_1500']:.2f}%",
                        'IF ALS < 1500d': f"{b['if_als_1500']:.2f}%",
                        'IF ≥ 1500d': f"{b['if_mas1500']:.2f}%",
                        'IF ALS ≥ 1500d': f"{b['if_als_mas1500']:.2f}%"
                    } for b in bloques_if
                ])
                render_hud_table(df_bloque_tab, table_id="resumen_bloques_if")

                # Tabla 2: Resumen de Run Life por Campo / Bloque
                st.markdown("<br>", unsafe_allow_html=True)
                lbl_tabla_rl = f"RESUMEN DE RUN LIFE (OPERATIVOS VS FALLADOS) POR {agrupacion_rl.upper()}" if 'agrupacion_rl' in locals() else "RESUMEN DE RUN LIFE"
                st.markdown(f"<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>{lbl_tabla_rl}</div>", unsafe_allow_html=True)
                
                tabla_rl_data = items_rl if ('items_rl' in locals() and items_rl) else bloques_if
                df_rl_tab = pd.DataFrame([
                    {
                        (agrupacion_rl if 'agrupacion_rl' in locals() else 'Bloque'): b.get('nombre', b.get('bloque', '')),
                        'Pozos Totales': b['total'],
                        'Pozos Operativos': b.get('pozos_op', b.get('prom_on', 0)),
                        'Run Life Op (días)': f"{b.get('rl_op', b.get('rl', 0)):.1f}d",
                        'Run Life Ef. Op (días)': f"{b.get('rle_op', b.get('rl_efectivo', 0)):.1f}d",
                        'Pozos Fallados': b.get('pozos_fall', b.get('fallas_tot', 0)),
                        'Run Life Fallados (días)': f"{b.get('rl_fall', 0):.1f}d",
                        'Run Life Ef. Fallados (días)': f"{b.get('rle_fall', 0):.1f}d",
                        f"Meta R.L. ({anio_prev})": f"{b.get('meta_rl', 0):.1f}d",
                        f"Meta R.L. Ef. ({anio_prev})": f"{b.get('meta_rle', 0):.1f}d"
                    } for b in tabla_rl_data
                ])
                render_hud_table(df_rl_tab, table_id="resumen_rl_operativo_fallado")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>DETALLE MENSUAL</div>", unsafe_allow_html=True)
            
            # Construir la tabla con las columnas solicitadas
            df_detalle = pd.DataFrame()
            df_detalle['Mes'] = df_mensual_hist['Mes']
            df_detalle['Pozos Operativos'] = df_mensual_hist['Pozos Operativos'].fillna(0).astype(int)
            df_detalle['IF Total Op'] = df_mensual_hist['Indice_Falla_Rolling_Total'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS Op'] = df_mensual_hist['Indice_Falla_Rolling_ALS_Total'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['Pozos On'] = df_mensual_hist['Pozos ON'].fillna(0).astype(int)
            df_detalle['IF ON'] = df_mensual_hist['Indice_Falla_Rolling_ON'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS ON'] = df_mensual_hist['Indice_Falla_Rolling_ALS_ON'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF < 1500'] = df_mensual_hist.get('Indice_Falla_Rolling_ON_1500', pd.Series([0]*len(df_mensual_hist))).apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS < 1500'] = df_mensual_hist.get('Indice_Falla_Rolling_ALS_ON_1500', pd.Series([0]*len(df_mensual_hist))).apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['Pozos Off'] = (df_mensual_hist['Pozos Operativos'] - df_mensual_hist['Pozos ON']).clip(lower=0).fillna(0).astype(int)
            df_detalle['Pozos Fallados'] = df_mensual_hist['Fallas Totales'].fillna(0).astype(int)
            df_detalle['Fallas ALS'] = df_mensual_hist['Fallas ALS'].fillna(0).astype(int)
            df_detalle['Fallas < 1500'] = df_mensual_hist.get('Fallas_1500', pd.Series([0]*len(df_mensual_hist))).fillna(0).astype(int)
            df_detalle['Fallas ALS < 1500'] = df_mensual_hist.get('Fallas_ALS_1500', pd.Series([0]*len(df_mensual_hist))).fillna(0).astype(int)
            
            # Ordenar por Mes descendente para ver lo más reciente al inicio
            df_detalle = df_detalle.sort_values(by='Mes', ascending=False).reset_index(drop=True)
            
            render_hud_table(df_detalle, table_id="detalle_mensual")
            
    except Exception as e:
        st.error(f"Error en Tab Índices: {e}")
