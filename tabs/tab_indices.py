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
        if 'ACTIVO' in df_bd_untr.columns:
            df_bd_untr = df_bd_untr[df_bd_untr['ACTIVO'].astype(str).str.upper().str.strip() != 'ECUADOR']
        
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

        st.markdown("<br>", unsafe_allow_html=True)

        # --- 3. ÍNDICES DE FALLA POR BLOQUE (ANCHO COMPLETO) ---
        _filtro_activo = (
            st.session_state.get('general_bloque_filter', 'TODOS') != 'TODOS' or
            st.session_state.get('general_campo_filter', 'TODOS') != 'TODOS'
        )
        if not _filtro_activo:
            st.markdown(f"<h6 style='color:#137659; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.8rem; margin-bottom:10px;'>📊 Índice de Falla por Bloque (Rolling 12M a {pd.to_datetime(fecha_evaluacion).strftime('%Y-%m-%d')})</h6>", unsafe_allow_html=True)

        if not _filtro_activo:
            try:
                df_bloque_raw = df_bd_untr.copy()
                df_bloque_raw['FECHA_RUN'] = pd.to_datetime(df_bloque_raw['FECHA_RUN'], errors='coerce')
                df_bloque_raw['FECHA_FALLA'] = pd.to_datetime(df_bloque_raw['FECHA_FALLA'], errors='coerce')
                df_bloque_raw['FECHA_PULL'] = pd.to_datetime(df_bloque_raw['FECHA_PULL'], errors='coerce')
                df_bloque_raw['_RUN'] = df_bloque_raw['FECHA_RUN'].dt.normalize()
                df_bloque_raw['_FALL'] = df_bloque_raw['FECHA_FALLA'].dt.normalize()
                df_bloque_raw['_PULL'] = df_bloque_raw['FECHA_PULL'].dt.normalize()

                fecha_eval_dt_b = pd.to_datetime(fecha_evaluacion)
                fecha_eval_norm_b = fecha_eval_dt_b.normalize()
                fecha_12m_back_b = fecha_eval_norm_b - pd.DateOffset(months=12)

                bloques_if = []
                for bloque, grp in df_bloque_raw.groupby('BLOQUE'):
                    if pd.isna(bloque) or str(bloque).strip() == '' or str(bloque).strip().upper() in ('TODOS', 'ECUADOR'):
                        continue

                    grp_runs = grp[grp['_RUN'] <= fecha_eval_norm_b]
                    total_pozosBloque = grp_runs['POZO'].nunique() if 'POZO' in grp_runs.columns else 0
                    if total_pozosBloque == 0:
                        continue

                    fallas_12m = grp_runs[
                        (grp_runs['_FALL'].notna()) &
                        (grp_runs['_FALL'] >= fecha_12m_back_b) &
                        (grp_runs['_FALL'] <= fecha_eval_norm_b)
                    ].shape[0]

                    pozos_on_meses = []
                    for i in range(12):
                        mes_start = fecha_12m_back_b + pd.DateOffset(months=i)
                        mes_end = (mes_start + pd.offsets.MonthEnd(0)).normalize()
                        grp_mes = grp_runs[grp_runs['_RUN'] <= mes_end]
                        activos_mes = grp_mes[
                            (grp_mes['_FALL'].isna()) | (grp_mes['_FALL'] > mes_end)
                        ]['POZO'].nunique() if 'POZO' in grp_mes.columns else 0
                        pozos_on_meses.append(activos_mes)

                    promedio_on = np.mean(pozos_on_meses) if pozos_on_meses else 0
                    if_val = (fallas_12m / promedio_on * 100) if promedio_on > 0 else 0

                    bloques_if.append({
                        'bloque': str(bloque).strip(),
                        'if_pct': round(if_val, 2),
                        'if_pct_cap': min(round(if_val, 2), 100.0),
                        'fallas': fallas_12m,
                        'prom_on': int(round(promedio_on)),
                        'total': total_pozosBloque
                    })

                bloques_if.sort(key=lambda x: x['if_pct'], reverse=True)

                if bloques_if:
                    blk_names = [d['bloque'] for d in bloques_if]
                    blk_if_vals = [d['if_pct_cap'] for d in bloques_if]
                    blk_if_real = [d['if_pct'] for d in bloques_if]
                    blk_fallas = [d['fallas'] for d in bloques_if]
                    blk_on = [d['prom_on'] for d in bloques_if]
                    blk_total = [d['total'] for d in bloques_if]

                    import plotly.graph_objects as go_fig

                    hover_texts = []
                    for i, d in enumerate(bloques_if):
                        real = d['if_pct']
                        cap = d['if_pct_cap']
                        val_str = f"{real:.2f}% (>100%)" if real > 100 else f"{cap:.2f}%"
                        hover_texts.append(
                            f"<b style='color:#137659;font-size:13px'>{d['bloque']}</b><br>"
                            f"<hr style='margin:3px 0;border-color:rgba(19,118,89,0.15)'>"
                            f"IF Rolling 12M: <b>{val_str}</b><br>"
                            f"Fallas (12M): <b>{d['fallas']}</b><br>"
                            f"Pozos ON (prom): <b>{d['prom_on']}</b><br>"
                            f"Pozos Totales: <b>{d['total']}</b>"
                        )

                    bar_colors_px = []
                    for v in blk_if_vals:
                        if v <= 7.5:
                            bar_colors_px.append("#137659")
                        elif v <= 10.0:
                            bar_colors_px.append("#c09c2e")
                        else:
                            bar_colors_px.append("#c62828")

                    chart_h = max(200, min(280, len(blk_names) * 38 + 80))

                    fig_bloque = go_fig.Figure()
                    fig_bloque.add_trace(go_fig.Bar(
                        x=blk_names,
                        y=blk_if_vals,
                        marker=dict(color=bar_colors_px, line=dict(width=0)),
                        text=[f"{v:.2f}%" for v in blk_if_vals],
                        textposition="outside",
                        textfont=dict(size=9, color="#1f221e", family="Inter, sans-serif"),
                        hovertext=hover_texts,
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor="#137659",
                                        font=dict(size=10, family="Inter, sans-serif", color="#1f221e")),
                        width=0.5
                    ))

                    fig_bloque.add_hline(y=7.5, line_dash="dash", line_color="#c62828", line_width=1.5,
                                         annotation_text="Meta 7.5%", annotation_position="top right",
                                         annotation_font=dict(size=9, color="#c62828", family="Inter, sans-serif"))

                    fig_bloque.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter, sans-serif"),
                        margin=dict(l=35, r=15, t=8, b=45),
                        xaxis=dict(title="", showgrid=False, showline=True, linecolor="rgba(19,118,89,0.15)",
                                   tickfont=dict(size=9, color="#1f221e", family="Inter, sans-serif"),
                                   tickangle=0),
                        yaxis=dict(title="IF (%)", range=[0, max(blk_if_vals) * 1.3] if blk_if_vals else [0, 15],
                                   showgrid=True, gridcolor="rgba(19,118,89,0.08)", gridwidth=1,
                                   showline=False,
                                   tickfont=dict(size=8, color="#5b5c55", family="Inter, sans-serif"),
                                   ticksuffix="%"),
                        bargap=0.4,
                        showlegend=False,
                        height=chart_h
                    )

                    st.plotly_chart(fig_bloque, use_container_width=True, config={"displayModeBar": False})
            except Exception as e:
                st.warning(f"No se pudo generar el gráfico de IF por Bloque: {e}")

        # --- 4. DETALLE DE DATA (Expander con HUD Table Interactivas) ---
        with st.expander("📄 VER TABLA DE DATOS HISTÓRICOS Y RESUMEN", expanded=False):
            st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>RESUMEN DE ÍNDICES</div>", unsafe_allow_html=True)
            render_hud_table(indice_resumen_df, table_id="resumen_indices")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>DETALLE MENSUAL</div>", unsafe_allow_html=True)
            
            # Construir la tabla con las columnas y orden exactos solicitados
            df_detalle = pd.DataFrame()
            df_detalle['Mes'] = df_mensual_hist['Mes']
            df_detalle['IF Total'] = df_mensual_hist['Indice_Falla_Rolling_ON'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS'] = df_mensual_hist['Indice_Falla_Rolling_ALS_ON'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF < 1500'] = df_mensual_hist.get('Indice_Falla_Rolling_ON_1500', pd.Series([0]*len(df_mensual_hist))).apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['IF ALS < 1500'] = df_mensual_hist.get('Indice_Falla_Rolling_ALS_ON_1500', pd.Series([0]*len(df_mensual_hist))).apply(lambda x: f"{x:.2%}" if pd.notna(x) else "0.00%")
            df_detalle['Pozos On'] = df_mensual_hist['Pozos ON'].fillna(0).astype(int)
            df_detalle['Pozos Fallados'] = df_mensual_hist['Fallas Totales'].fillna(0).astype(int)
            df_detalle['Fallas < 1500'] = df_mensual_hist.get('Fallas_1500', pd.Series([0]*len(df_mensual_hist))).fillna(0).astype(int)
            df_detalle['Fallas ALS < 1500'] = df_mensual_hist.get('Fallas_ALS_1500', pd.Series([0]*len(df_mensual_hist))).fillna(0).astype(int)
            df_detalle['Fallas ALS'] = df_mensual_hist['Fallas ALS'].fillna(0).astype(int)
            df_detalle['Pozos Off'] = (df_mensual_hist['Pozos Operativos'] - df_mensual_hist['Pozos ON']).clip(lower=0).fillna(0).astype(int)
            
            # Ordenar por Mes descendente para ver lo más reciente al inicio
            df_detalle = df_detalle.sort_values(by='Mes', ascending=False).reset_index(drop=True)
            
            render_hud_table(df_detalle, table_id="detalle_mensual")
            
    except Exception as e:
        st.error(f"Error en Tab Índices: {e}")
