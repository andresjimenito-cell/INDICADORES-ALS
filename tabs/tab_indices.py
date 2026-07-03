"""
tabs/tab_indices.py
===================
Visualización profesional de Índices de Falla y Operatividad.
Utiliza estética HUD y Zero Space Waste.
"""

import json
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
        
        razon = row.get(col_razon, '') if col_razon else ''
        
        run_val = row.get('RUN', 1)
        if run_val == 1:
            tipo_badge = '<span class="badge-custom badge-nuevo">NUEVO</span>'
        else:
            tipo_badge = '<span class="badge-custom badge-ws">WELL SERVICE</span>'
            
        is_falla = 1 if pd.notna(ff) else 0
        if is_falla == 1:
            estado_badge = '<span class="badge-custom badge-fallado">⚠️ FALLADO</span>'
            run_life = (ff - fr).days if pd.notna(ff) and pd.notna(fr) else '-'
            causa = clasificar_razon_ia(str(razon)) if pd.notna(razon) and str(razon).strip() != '' else 'Desconocida'
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

    try:
        indice_resumen_df, df_mensual_hist = calcular_indice_falla_anual(
            df_bd_filtered,
            df_forma9_filtered,
            fecha_evaluacion,
            fecha_inicio
        )
        
        # --- 1. KPI GRID (Resumen de Índices) ---
        
        # Extraer valores para las tarjetas
        def get_val(ind_name):
            try: return indice_resumen_df[indice_resumen_df['Indicador'] == ind_name]['Valor'].values[0]
            except: return "0%"

        # --- 1. KPI GRID (Resumen de Índices en fila única) ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">📊</div><div class="kpi-label">I.F. TOTAL</div><div class="kpi-value" style="color:#137659;">{get_val("Índice de Falla Total")}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚙️</div><div class="kpi-label">I.F. ALS</div><div class="kpi-value" style="color:#c09c2e;">{get_val("Índice de Falla ALS")}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🔋</div><div class="kpi-label">I.F. ON</div><div class="kpi-value" style="color:#095139;">{get_val("Índice de Falla ON")}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⚡</div><div class="kpi-label">I.F. ALS ON</div><div class="kpi-value" style="color:#137659;">{get_val("Índice de Falla ALS ON")}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

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
            echarts_line = {
                "backgroundColor": "transparent",
                "title": {"text": "EVOLUCIÓN DE ÍNDICES", "left": "center", "top": 0,
                          "textStyle": {"color": "#137659", "fontSize": 13, "fontFamily": "Arial, sans-serif", "fontWeight": "bold"}},
                "textStyle": {"fontFamily": "Arial, sans-serif"},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.95)", "borderColor": "#137659",
                            "textStyle": {"color": "#1f221e", "fontFamily": "Arial, sans-serif"}, "axisPointer": {"type": "cross"}},
                "legend": {"data": ["I.F. Total", "I.F. ALS", "I.F. <1500", "I.F. ALS <1500"], "bottom": 0,
                           "textStyle": {"color": "#475569", "fontSize": 9, "fontFamily": "Arial, sans-serif"}},
                "grid": {"left": "3%", "right": "4%", "bottom": "18%", "top": "15%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": "#475569", "fontSize": 9, "fontFamily": "Arial, sans-serif"}}],
                "yAxis": [{"type": "value", "axisLabel": {"formatter": "{value}%", "color": "#475569", "fontFamily": "Arial, sans-serif"},
                           "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.05)"}}}],
                "series": [
                    {"name": "I.F. Total",    "type": "line", "smooth": True, "data": val_if_on,    "itemStyle": {"color": "#137659"}, "lineStyle": {"width": 3}, "areaStyle": {"color": "rgba(19,118,89,0.05)"}},
                    {"name": "I.F. ALS",      "type": "line", "smooth": True, "data": val_if_als,   "itemStyle": {"color": "#c09c2e"}, "lineStyle": {"width": 3}},
                    {"name": "I.F. <1500",    "type": "line", "smooth": True, "data": val_if_on_1500,  "itemStyle": {"color": "#5b5c55"}, "lineStyle": {"width": 2, "type": "dashed"}},
                    {"name": "I.F. ALS <1500","type": "line", "smooth": True, "data": val_if_als_1500, "itemStyle": {"color": "#095139"}, "lineStyle": {"width": 2, "type": "dashed"}}
                ]
            }
            import json as _json
            components.html(f'<div id="echarts-if-line" style="width:100%;height:360px;background:#ffffff;border-radius:15px;overflow:hidden;border:1px solid rgba(19,118,89,0.15);"></div>'
                            f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
                            f'<script>(function(){{var c=echarts.init(document.getElementById("echarts-if-line"),null);c.setOption({_json.dumps(echarts_line)});window.addEventListener("resize",function(){{c.resize();}});}})();</script>',
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

        # --- 3. DETALLE DE DATA (Expander con HUD Table Interactivas) ---
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
