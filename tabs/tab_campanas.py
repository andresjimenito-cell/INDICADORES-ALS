"""
tabs/tab_campanas.py
====================
Visualización detallada de Campañas de Intervención.
Permite filtrar por año de campaña, muestra KPIs consolidados,
gráficos de corridas vs fallas y detalles de pozos con estilo HUD.
"""

import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from calculations import clasificar_razon_ia, clasificar_runlife

# Colores Corporativos Parex
_CYAN    = "#137659"
_RED     = "#c62828"
_MAGENTA = "#c09c2e"

def _mini_metric(label: str, value: str, color: str) -> str:
    """Micro-tarjeta para conteos dentro de la campaña."""
    return f"""
<div style="background:{color}0d; border:1px solid {color}25; border-radius:6px; padding:5px 10px; margin-bottom:4px;">
    <div style="color:{color}; font-size:0.48rem; font-weight:700; letter-spacing:2px; text-transform:uppercase; font-family:'Arial', sans-serif !important;">{label}</div>
    <div style="font-size:1.3rem; font-weight:900; color:#1f221e; line-height:1.1;">{value}</div>
</div>"""

def _echarts_html(options: dict, height: int, chart_id: str) -> str:
    """Wrapper para ECharts."""
    return f"""
<div id="{chart_id}" style="width:100%;height:{height}px;background:#ffffff;border-radius:12px;border:1px solid rgba(19, 118, 89, 0.15);overflow:hidden;"></div>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script>
(function(){{
    var el = document.getElementById('{chart_id}');
    var myChart = echarts.init(el, null);
    var option = {json.dumps(options)};
    myChart.setOption(option);
    window.addEventListener('resize', function() {{
        myChart.resize();
    }});
}})();
</script>"""

def render_campanas_table(df_camp, table_id="campanas_table"):
    """Renderiza la tabla de detalles con estilo HUD y resalta los pozos fallados."""
    if df_camp.empty:
        st.info("Sin datos para mostrar en la tabla.")
        return

    # Preparamos los datos
    rows = []
    col_razon = 'RAZON_DE_PULL' if 'RAZON_DE_PULL' in df_camp.columns else ('RAZON ESPECIFICA PULL' if 'RAZON ESPECIFICA PULL' in df_camp.columns else None)
    
    for _, row in df_camp.iterrows():
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
            
        is_falla = row.get('Falla', 0)
        if is_falla == 1:
            estado_badge = '<span class="badge-custom badge-fallado">⚠️ FALLADO</span>'
            run_life = (ff - fr).days if pd.notna(ff) and pd.notna(fr) else '-'
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
    
    <div style="background: #ffffff; padding:8px; border:1px solid rgba(19, 118, 89, 0.2); border-radius:10px; box-shadow: 0 4px 6px rgba(0,0,0,0.03); width:100%; box-sizing:border-box; overflow:hidden;">
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
                "scrollY": "400px",
                "scrollCollapse": true,
                "paging": false,
                "order": [],
                "language": {{ "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                "dom": 'Bft',
                "buttons": [
                    {{
                        extend: 'copy',
                        text: '📋 Copiar Tabla',
                        className: 'hud-copy-btn'
                    }}
                ],
                "createdRow": function(row, data, dataIndex) {{
                    if (data[7] && data[7].indexOf("FALLADO") !== -1) {{
                        $(row).css("background-color", "rgba(198, 40, 40, 0.05)");
                        $('td', row).css("border-bottom", "1px solid rgba(198, 40, 40, 0.2)");
                    }}
                }}
            }});
        }});
    </script>
    """, height=min(500, 110 + len(df_camp) * 36))

def render_tab_campanas(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, selected_activo):
    """Renderiza la pestaña de Campañas."""
    
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    
    # Cargar datos sin procesar de st.session_state
    df_bd_raw = st.session_state.get('df_bd_calculated')
    df_forma9_raw = st.session_state.get('df_forma9_calculated')
    
    df_bd_untr = df_bd_raw.copy() if df_bd_raw is not None else df_bd_filtered.copy()
    if 'ACTIVO' in df_bd_untr.columns:
        df_bd_untr = df_bd_untr[df_bd_untr['ACTIVO'].astype(str).str.upper().str.strip() != 'ECUADOR']
        
    # Aplicar filtros globales de st.session_state
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
            
    df_bd_untr['FECHA_RUN'] = pd.to_datetime(df_bd_untr['FECHA_RUN'], errors='coerce')
    df_bd_untr['FECHA_FALLA'] = pd.to_datetime(df_bd_untr['FECHA_FALLA'], errors='coerce')
    df_bd_untr['FECHA_PULL'] = pd.to_datetime(df_bd_untr['FECHA_PULL'], errors='coerce')
    
    # Extraer los años de campaña disponibles
    years = sorted(df_bd_untr['FECHA_RUN'].dt.year.dropna().unique().astype(int))
    if not years:
        st.warning("⚠️ No hay campañas disponibles en los datos filtrados.")
        return
        
    # Dropdown selectbox para la campaña
    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    default_year = fecha_eval_dt.year
    if default_year not in years:
        default_year = years[-1]
        
    c_sel, c_metrics = st.columns([1.2, 3], gap="large")
    
    with c_sel:
        st.markdown("<div style='height:5px;'></div>", unsafe_allow_html=True)
        selected_years = st.multiselect(
            "📅 Seleccionar Años de Campaña",
            options=years,
            default=[default_year],
            key="campanas_year_select"
        )
        
    if not selected_years:
        st.info("Por favor, selecciona al menos una campaña.")
        return
        
    # Filtrar corridas para las campañas seleccionadas
    df_camp = df_bd_untr[df_bd_untr['FECHA_RUN'].dt.year.isin(selected_years)].copy()
    
    df_camp['Mes']   = df_camp['FECHA_RUN'].dt.strftime('%Y-%m')
    df_camp['Tipo']  = (df_camp['RUN'].apply(lambda x: 'Nuevo' if x == 1 else 'WS')
                        if 'RUN' in df_camp.columns else 'Otro')
    df_camp['Falla'] = df_camp['FECHA_FALLA'].notna().astype(int)
    
    val_nuevos = df_camp[df_camp['RUN'] == 1].shape[0] if 'RUN' in df_camp.columns else 0
    val_ws     = df_camp[df_camp['RUN'] > 1].shape[0] if 'RUN' in df_camp.columns else 0
    val_fallas = df_camp[df_camp['Falla'] == 1].shape[0]
    
    with c_metrics:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(_mini_metric("Nuevos", f"{val_nuevos}", _CYAN), unsafe_allow_html=True)
        with m2:
            st.markdown(_mini_metric("Well Service", f"{val_ws}", _MAGENTA), unsafe_allow_html=True)
        with m3:
            st.markdown(_mini_metric("Fallas de Campaña", f"{val_fallas}", _RED), unsafe_allow_html=True)
            
    st.markdown("<hr style='border:0; height:1px; background:linear-gradient(to right, transparent, rgba(19, 118,89, 0.2), transparent); margin:15px 0;'>", unsafe_allow_html=True)
    
    # Fila de Gráfico y Tabla
    col_chart, col_table = st.columns([1, 1.25], gap="medium")
    
    with col_chart:
        st.markdown(f"<h5 style='color:{_CYAN}; font-family:Arial, sans-serif !important; margin-bottom:10px;'>📈 CORRELACIÓN CORRIDAS VS FALLAS (MENSUAL)</h5>", unsafe_allow_html=True)
        
        # Generar meses
        unique_months = []
        for y in sorted(selected_years):
            unique_months.extend([f"{y}-{str(m).zfill(2)}" for m in range(1, 13)])
        
        if not df_camp.empty:
            df_res = (df_camp.groupby(['Mes', 'Tipo'])
                             .size()
                             .unstack(fill_value=0)
                             .reindex(unique_months, fill_value=0))
            
            df_fall_by_type = (df_camp[df_camp['Falla'] == 1]
                               .groupby(['Mes', 'Tipo'])
                               .size()
                               .unstack(fill_value=0)
                               .reindex(unique_months, fill_value=0))
            
            _MES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            cats = [f"{_MES[int(m[5:7]) - 1]}-{m[2:4]}" for m in df_res.index]
            d_nv = df_res['Nuevo'].tolist() if 'Nuevo' in df_res.columns else [0]*len(cats)
            d_ws = df_res['WS'].tolist()    if 'WS'    in df_res.columns else [0]*len(cats)
            
            d_fl_nuevo = df_fall_by_type['Nuevo'].tolist() if 'Nuevo' in df_fall_by_type.columns else [0]*len(cats)
            d_fl_ws    = df_fall_by_type['WS'].tolist() if 'WS' in df_fall_by_type.columns else [0]*len(cats)
        else:
            _MES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            cats = [f"{_MES[m-1]}-{str(y)[2:4]}" for y in sorted(selected_years) for m in range(1, 13)]
            d_nv = d_ws = d_fl_nuevo = d_fl_ws = [0]*len(cats)
            
        opts_camp = {
            "backgroundColor": "#ffffff",
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.95)",
                "borderColor": "rgba(19,118,89,0.15)",
                "textStyle": {"color": "#1f221e", "fontSize": 11},
            },
            "legend": {
                "data": ["Nuevos", "Well Service", "Fallas Nuevos", "Fallas WS"],
                "textStyle": {"color": "#1f221e", "fontSize": 8},
                "bottom": 0,
                "itemHeight": 6,
                "itemGap": 10,
            },
            "grid": {
                "top": "12%", "left": "2%", "right": "2%",
                "bottom": "20%", "containLabel": True,
            },
            "xAxis": {
                "type": "category",
                "data": cats,
                "axisLabel": {"color": "#1f221e", "fontSize": 8},
                "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.15)"}},
                "axisTick": {"show": False},
            },
            "yAxis": [
                {
                    "type": "value",
                    "name": "Corridas",
                    "nameTextStyle": {"color": "#1f221e", "fontSize": 8},
                    "axisLabel": {"color": "#1f221e", "fontSize": 7},
                    "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)", "type": "dashed"}},
                },
                {
                    "type": "value",
                    "name": "Fallas",
                    "nameTextStyle": {"color": "#c62828", "fontSize": 8},
                    "axisLabel": {"color": "#c62828", "fontSize": 7},
                    "splitLine": {"show": False},
                    "min": 0,
                }
            ],
            "series": [
                {
                    "name": "Nuevos", "type": "bar", "stack": "total",
                    "data": d_nv, "barMaxWidth": 18,
                    "itemStyle": {
                        "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                  "colorStops": [
                                      {"offset": 0, "color": "#137659"},
                                      {"offset": 1, "color": "#095139"},
                                  ]}
                    }
                },
                {
                    "name": "Well Service", "type": "bar", "stack": "total",
                    "data": d_ws, "barMaxWidth": 18,
                    "itemStyle": {
                        "color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                  "colorStops": [
                                      {"offset": 0, "color": "#c09c2e"},
                                      {"offset": 1, "color": "#9b791e"},
                                  ]}
                    }
                },
                {
                    "name": "Fallas Nuevos", "type": "line",
                    "yAxisIndex": 1,
                    "data": d_fl_nuevo, "smooth": True,
                    "symbol": "circle", "symbolSize": 5,
                    "lineStyle": {"width": 2, "color": "#c62828"},
                    "itemStyle": {"color": "#c62828", "borderWidth": 2, "borderColor": "#fff"}
                },
                {
                    "name": "Fallas WS", "type": "line",
                    "yAxisIndex": 1,
                    "data": d_fl_ws, "smooth": True,
                    "symbol": "circle", "symbolSize": 5,
                    "lineStyle": {"width": 2, "color": "#ff7043", "type": "dashed"},
                    "itemStyle": {"color": "#ff7043", "borderWidth": 2, "borderColor": "#fff"}
                }
            ]
        }
        
        components.html(_echarts_html(opts_camp, 380, "chart_campana_tab"), height=400)
        
        # Calcular estadísticas de la mini-tabla de resumen
        fallados_nuevos = df_camp[(df_camp['RUN'] == 1) & (df_camp['Falla'] == 1)].shape[0] if not df_camp.empty else 0
        fallados_ws     = df_camp[(df_camp['RUN'] > 1) & (df_camp['Falla'] == 1)].shape[0] if not df_camp.empty else 0
        
        pct_nuevos = (fallados_nuevos / val_nuevos * 100) if val_nuevos > 0 else 0.0
        pct_ws     = (fallados_ws / val_ws * 100) if val_ws > 0 else 0.0
        
        total_corridas = val_nuevos + val_ws
        total_falladas = fallados_nuevos + fallados_ws
        pct_total  = (total_falladas / total_corridas * 100) if total_corridas > 0 else 0.0
        
        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <table style="width:100%; border-collapse:collapse; border-radius:8px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15); font-family:Arial, sans-serif; font-size:11px; text-align:center; background:#ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
          <thead>
            <tr style="background-color:rgba(19, 118, 89, 0.08); color:#137659; font-weight:bold;">
              <th style="padding:8px; border-bottom:1px solid rgba(19, 118, 89, 0.15); text-align:left;">⚙️ TIPO DE CORRIDA</th>
              <th style="padding:8px; border-bottom:1px solid rgba(19, 118, 89, 0.15);">🚀 TOTAL CORRIDAS</th>
              <th style="padding:8px; border-bottom:1px solid rgba(19, 118, 89, 0.15);">⚠️ CORRIDAS FALLADAS</th>
              <th style="padding:8px; border-bottom:1px solid rgba(19, 118, 89, 0.15);">📈 TASA DE FALLAS</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="padding:8px; font-weight:bold; color:#137659; text-align:left; border-bottom:1px solid rgba(19, 118, 89, 0.08);">🆕 NUEVO (Corrida = 1)</td>
              <td style="padding:8px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{val_nuevos}</td>
              <td style="padding:8px; color:#c62828; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{fallados_nuevos}</td>
              <td style="padding:8px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08); color:#c62828;">{pct_nuevos:.1f}%</td>
            </tr>
            <tr style="background-color:rgba(192, 156, 46, 0.02);">
              <td style="padding:8px; font-weight:bold; color:#c09c2e; text-align:left; border-bottom:1px solid rgba(19, 118, 89, 0.08);">🛠️ WELL SERVICE (Corrida > 1)</td>
              <td style="padding:8px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{val_ws}</td>
              <td style="padding:8px; color:#c62828; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{fallados_ws}</td>
              <td style="padding:8px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08); color:#c62828;">{pct_ws:.1f}%</td>
            </tr>
            <tr style="background-color:rgba(19, 118, 89, 0.05); font-weight:bold;">
              <td style="padding:8px; text-align:left;">📊 RESUMEN CAMPAÑA</td>
              <td style="padding:8px;">{total_corridas}</td>
              <td style="padding:8px; color:#c62828;">{total_falladas}</td>
              <td style="padding:8px; color:#137659;">{pct_total:.1f}%</td>
            </tr>
          </tbody>
        </table>
        """, unsafe_allow_html=True)
        
    with col_table:
        st.markdown(f"<h5 style='color:{_CYAN}; font-family:Arial, sans-serif !important; margin-bottom:10px;'>📋 DETALLE DE POZOS CORRIDAS Y FALLAS</h5>", unsafe_allow_html=True)
        render_campanas_table(df_camp)

        # === NUEVO GRÁFICO: DISTRIBUCIÓN DE FALLAS POR CATEGORÍA Y ETAPA ===
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='color:{_CYAN}; font-family:Arial, sans-serif !important; margin-bottom:10px;'>🎯 DISTRIBUCIÓN DE FALLAS: CATEGORÍA VS ETAPA DE VIDA</h5>", unsafe_allow_html=True)
        
        df_fallas = df_camp[df_camp['Falla'] == 1].copy()
        if not df_fallas.empty:
            # Clasificar causa y etapa
            if 'RAZON_DE_PULL' in df_fallas.columns:
                col_razon = 'RAZON_DE_PULL'
            elif 'RAZON ESPECIFICA PULL' in df_fallas.columns:
                col_razon = 'RAZON ESPECIFICA PULL'
            else:
                col_razon = None
                
            def obtener_causa_dist(row_fallas):
                sub_tipo = row_fallas.get('SUB TIPO DE FALLA')
                if pd.notna(sub_tipo) and str(sub_tipo).strip() != '':
                    return clasificar_razon_ia(str(sub_tipo))
                razon = row_fallas.get(col_razon) if col_razon else None
                return clasificar_razon_ia(str(razon)) if pd.notna(razon) and str(razon).strip() != '' else 'Otros'
            
            df_fallas['Causa_Cat'] = df_fallas.apply(obtener_causa_dist, axis=1)
                
            df_fallas['Etapa_Cat'] = df_fallas['RUN LIFE'].apply(clasificar_runlife) if 'RUN LIFE' in df_fallas.columns else 'N/A'
            
            causas_orden = ['Eléctrica', 'Mecánica', 'Tubería', 'Yacimiento', 'Otros']
            etapas_orden = ['Infantil', 'Prematura', 'En Garantía', 'Sin Garantía', 'N/A']
            
            df_dist = df_fallas.groupby(['Causa_Cat', 'Etapa_Cat']).size().unstack(fill_value=0)
            
            # Reindexar para asegurar orden
            for c in causas_orden:
                if c not in df_dist.index: df_dist.loc[c] = 0
            for e in etapas_orden:
                if e not in df_dist.columns: df_dist[e] = 0
                
            df_dist = df_dist.loc[causas_orden, etapas_orden]
            
            # Colores para las etapas
            etapa_colors = {
                'Infantil': '#d32f2f',
                'Prematura': '#c09c2e',
                'En Garantía': '#137659',
                'Sin Garantía': '#5b5c55',
                'N/A': '#9e9e9e'
            }
            
            series_data = []
            for etapa in etapas_orden:
                series_data.append({
                    "name": etapa,
                    "type": "bar",
                    "stack": "total",
                    "barMaxWidth": 50,
                    "itemStyle": {"color": etapa_colors[etapa]},
                    "data": df_dist[etapa].tolist()
                })
                
            # Añadir markLine para dividir ALS de No-ALS
            # La división está entre 'Mecánica' (index 1) y 'Tubería' (index 2) -> x = 1.5
            series_data[-1]["markLine"] = {
                "symbol": "none",
                "lineStyle": {"color": "#c62828", "type": "dashed", "width": 2},
                "label": {"show": True, "position": "middle", "formatter": "ALS ⬅️ | ➡️ Externas", "color": "#c62828", "fontSize": 12, "fontWeight": "bold"},
                "data": [{"xAxis": 1.5}]
            }
            
            opts_dist = {
                "backgroundColor": "#ffffff",
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "backgroundColor": "rgba(255,255,255,0.95)",
                    "borderColor": "rgba(19,118,89,0.15)",
                    "textStyle": {"color": "#1f221e", "fontSize": 12},
                },
                "legend": {
                    "data": etapas_orden,
                    "bottom": 0,
                    "textStyle": {"color": "#1f221e", "fontSize": 11}
                },
                "grid": {
                    "top": "15%", "left": "3%", "right": "4%", "bottom": "15%", "containLabel": True
                },
                "xAxis": {
                    "type": "category",
                    "data": causas_orden,
                    "axisLabel": {"color": "#1f221e", "fontSize": 11, "fontWeight": "bold"},
                    "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.3)"}}
                },
                "yAxis": {
                    "type": "value",
                    "name": "Cantidad de Fallas",
                    "nameTextStyle": {"color": "#1f221e", "fontSize": 11},
                    "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.1)", "type": "dashed"}}
                },
                "series": series_data
            }
            
            components.html(_echarts_html(opts_dist, 400, "chart_dist_fallas"), height=420)
        else:
            st.info("No hay fallas registradas en la(s) campaña(s) seleccionada(s) para mostrar la distribución.")
