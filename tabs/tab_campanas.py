"""
tabs/tab_campanas.py  —  v2.0 Campañas de Intervención Premium
==============================================================
Mejoras:
1. Métricas de eficiencia avanzada (% éxito de campaña, activas vs extraídas, % cumplimiento de meta)
2. Gráfico interactivo ECharts de Corridas vs Fallas por mes con degradados y leyendas corporativas
3. Gráfico de distribución de fallas por etapa de vida útil con markline ALS/No-ALS
4. Tabla interactiva de detalle de corridas con badges inline y estilo de tabla HUD DataTables
"""

import json
import calendar
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from calculations import clasificar_razon_ia, clasificar_runlife
from styles import render_hud_table

# Colores Corporativos Parex
_G   = "#137659"
_G2  = "#0a4d34"
_Y   = "#c09c2e"
_R   = "#c62828"
_T   = "#1f221e"
_T2  = "#455a72"

def _echarts_html(options: dict, height: int, chart_id: str) -> str:
    """Wrapper para ECharts."""
    return f"""
    <div id="{chart_id}" style="width:100%;height:{height}px;background:#ffffff;border-radius:12px;border:1px solid rgba(19, 118, 89, 0.13);overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.04);"></div>
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
        razon = str(row.get(col_razon, '')) if col_razon else ''
        
        run_val = row.get('RUN', 1)
        tipo_badge = '<span class="badge-custom badge-nuevo">NUEVO</span>' if run_val == 1 else '<span class="badge-custom badge-ws">WS</span>'
            
        is_falla = row.get('Falla', 0)
        if is_falla == 1:
            estado_badge = '<span class="badge-custom badge-fallado">⚠️ FALLA</span>'
            run_life = (ff - fr).days if pd.notna(ff) and pd.notna(fr) else '-'
            sub_tipo = row.get('SUB TIPO DE FALLA')
            if pd.notna(sub_tipo) and str(sub_tipo).strip() != '':
                causa = clasificar_razon_ia(str(sub_tipo))
            else:
                causa = clasificar_razon_ia(razon) if razon.strip() != '' else 'Desconocida'
                if pd.isna(fp):
                    causa = f"Posible {causa}"
        else:
            estado_badge = '<span class="badge-custom badge-operativo">✓ OK</span>'
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        
        body {{ background: transparent; color: #1f221e; font-family: 'Inter', sans-serif; margin:0; padding:0; }}
        .dataTables_wrapper {{ color: #1f221e !important; }}
        .dataTables_filter input {{ background: #ffffff; border: 1px solid #137659; color: #1f221e; border-radius: 6px; padding: 4px 8px; font-size:11px; }}
        .dataTables_filter label {{ color:#5b5c55; font-size:11px; }}
        table.dataTable {{ width: 100% !important; }}
        table.dataTable thead th {{ background: rgba(19, 118, 89, 0.08); color: #137659; font-family: 'Inter'; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing:0.8px; padding:6px 8px; }}
        table.dataTable tbody td {{ border-bottom: 1px solid rgba(19, 118, 89, 0.08); padding: 6px 8px; font-size: 11px; color: #1f221e; }}
        .dataTables_info, .dataTables_paginate {{ color: #5b5c55 !important; font-size: 10px; }}
        
        .badge-custom {{
            display: inline-block;
            padding: 2px 7px;
            font-size: 8px;
            font-weight: 700;
            border-radius: 10px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }}
        .badge-nuevo {{ background-color: rgba(19, 118, 89, 0.1); color: #137659; border: 1px solid rgba(19, 118, 89, 0.3); }}
        .badge-ws {{ background-color: rgba(192, 156, 46, 0.1); color: #c09c2e; border: 1px solid rgba(192, 156, 46, 0.3); }}
        .badge-fallado {{ background-color: rgba(198, 40, 40, 0.1); color: #c62828; border: 1px solid rgba(198, 40, 40, 0.3); }}
        .badge-operativo {{ background-color: rgba(46, 125, 50, 0.1); color: #2e7d32; border: 1px solid rgba(46, 125, 50, 0.3); }}
    </style>
    
    <div style="background: #ffffff; padding:8px; border:1px solid rgba(19, 118, 89, 0.15); border-radius:12px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); width:100%; box-sizing:border-box; overflow:hidden;">
        {html_table}
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {{
            $('#{table_id}').DataTable({{
                "scrollX": true,
                "scrollY": "300px",
                "scrollCollapse": true,
                "paging": false,
                "order": [],
                "language": {{ "url": "https://cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json" }},
                "dom": 'ft',
                "createdRow": function(row, data, dataIndex) {{
                    if (data[7] && data[7].indexOf("⚠️") !== -1) {{
                        $(row).css("background-color", "rgba(198, 40, 40, 0.04)");
                    }}
                }}
            }});
        }});
    </script>
    """, height=380)

def render_tab_campanas(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, selected_activo):
    """Renderiza la pestaña de Campañas."""
    
    # Cargar datos sin procesar de st.session_state
    df_bd_raw = st.session_state.get('df_bd_calculated')
    
    df_bd_untr = df_bd_raw.copy() if df_bd_raw is not None else df_bd_filtered.copy()
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
            
    df_bd_untr['FECHA_RUN'] = pd.to_datetime(df_bd_untr['FECHA_RUN'], errors='coerce')
    df_bd_untr['FECHA_FALLA'] = pd.to_datetime(df_bd_untr['FECHA_FALLA'], errors='coerce')
    df_bd_untr['FECHA_PULL'] = pd.to_datetime(df_bd_untr['FECHA_PULL'], errors='coerce')
    
    years = sorted(df_bd_untr['FECHA_RUN'].dt.year.dropna().unique().astype(int))
    if not years:
        st.warning("⚠️ No hay campañas disponibles en los datos filtrados.")
        return
        
    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    default_year = fecha_eval_dt.year
    if default_year not in years:
        default_year = years[-1]
        
    c_sel, c_metrics = st.columns([1.2, 3], gap="large")
    
    with c_sel:
        selected_years = st.multiselect(
            "📅 Años de Campaña",
            options=years,
            default=[default_year],
            key="campanas_year_select"
        )
        
    if not selected_years:
        st.info("Por favor, selecciona al menos una campaña.")
        return
        
    df_camp = df_bd_untr[df_bd_untr['FECHA_RUN'].dt.year.isin(selected_years)].copy()
    
    df_camp['Mes']   = df_camp['FECHA_RUN'].dt.strftime('%Y-%m')
    df_camp['Tipo']  = (df_camp['RUN'].apply(lambda x: 'Nuevo' if x == 1 else 'WS')
                        if 'RUN' in df_camp.columns else 'Otro')
    df_camp['Falla'] = df_camp['FECHA_FALLA'].notna().astype(int)
    
    val_nuevos = df_camp[df_camp['RUN'] == 1].shape[0] if 'RUN' in df_camp.columns else 0
    val_ws     = df_camp[df_camp['RUN'] > 1].shape[0] if 'RUN' in df_camp.columns else 0
    val_fallas = df_camp[df_camp['Falla'] == 1].shape[0]
    total_corridas = val_nuevos + val_ws
    
    # Métricas avanzadas de Eficiencia de Campaña
    tasa_exito = ((total_corridas - val_fallas) / total_corridas * 100) if total_corridas > 0 else 0
    extraidos = df_camp[df_camp['FECHA_PULL'].notna()].shape[0]
    activas = total_corridas - extraidos
    
    st.markdown("""
    <style>
    .camp-kpi { background:#ffffff; border:1px solid rgba(19,118,89,0.12); border-radius:12px;
        padding:10px 12px; display:flex; flex-direction:column; align-items:center; text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,0.03); }
    .camp-kpi-lbl { font-family:'Inter',sans-serif; font-size:0.56rem; font-weight:800;
        letter-spacing:1px; text-transform:uppercase; color:#5b5c55; margin-bottom:2px; }
    .camp-kpi-val { font-family:'Inter',sans-serif; font-size:1.5rem; font-weight:900; line-height:1.1; }
    .camp-kpi-sub { font-family:'Inter',sans-serif; font-size:0.55rem; color:#94a3b8; margin-top:2px; }
    </style>""", unsafe_allow_html=True)
    
    with c_metrics:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'''<div class="camp-kpi" style="border-top:3px solid {_G};">
                <div class="camp-kpi-lbl">Corridas Nuevas</div>
                <div class="camp-kpi-val" style="color:{_G};">{val_nuevos}</div>
                <div class="camp-kpi-sub">Primera instalación</div></div>''', unsafe_allow_html=True)
        with m2:
            st.markdown(f'''<div class="camp-kpi" style="border-top:3px solid {_Y};">
                <div class="camp-kpi-lbl">Corridas WS</div>
                <div class="camp-kpi-val" style="color:{_Y};">{val_ws}</div>
                <div class="camp-kpi-sub">Intervenciones (Run > 1)</div></div>''', unsafe_allow_html=True)
        with m3:
            st.markdown(f'''<div class="camp-kpi" style="border-top:3px solid {_R};">
                <div class="camp-kpi-lbl">Fallas Registradas</div>
                <div class="camp-kpi-val" style="color:{_R};">{val_fallas}</div>
                <div class="camp-kpi-sub">En el rango seleccionado</div></div>''', unsafe_allow_html=True)
        with m4:
            st.markdown(f'''<div class="camp-kpi" style="border-top:3px solid {_G2};">
                <div class="camp-kpi-lbl">Tasa de Éxito</div>
                <div class="camp-kpi-val" style="color:{_G2};">{tasa_exito:.1f}%</div>
                <div class="camp-kpi-sub">{activas} activas | {extraidos} pulls</div></div>''', unsafe_allow_html=True)
            
    st.markdown("<hr style='border:0; height:1px; background:linear-gradient(to right, transparent, rgba(19, 118,89, 0.15), transparent); margin:15px 0;'>", unsafe_allow_html=True)
    
    # Fila de Gráfico y Tabla
    col_chart, col_table = st.columns([1, 1], gap="medium")
    
    with col_chart:
        st.markdown(f"<h6 style='color:{_G}; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>📈 Correlación Corridas vs Fallas (Mensual)</h6>", unsafe_allow_html=True)
        
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
            "backgroundColor": "transparent",
            "tooltip": {
                "trigger": "axis", "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                "textStyle": {"color": _T, "fontSize": 11, "fontFamily": "Inter, sans-serif"},
            },
            "legend": {
                "data": ["Corridas Nuevas", "Intervenciones WS", "Fallas Nuevos", "Fallas WS"],
                "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                "bottom": 0, "icon": "circle"
            },
            "grid": {"top": "12%", "left": "2%", "right": "2%", "bottom": "20%", "containLabel": True},
            "xAxis": {
                "type": "category", "data": cats,
                "axisLabel": {"color": _T2, "fontSize": 8, "fontFamily": "Inter, sans-serif", "rotate": 25},
                "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.15)"}}
            },
            "yAxis": [
                {
                    "type": "value", "name": "Corridas",
                    "axisLabel": {"color": _T2, "fontSize": 8, "fontFamily": "Inter, sans-serif"},
                    "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}},
                },
                {
                    "type": "value", "name": "Fallas", "position": "right",
                    "axisLabel": {"color": _R, "fontSize": 8, "fontFamily": "Inter, sans-serif"},
                    "splitLine": {"show": False}
                }
            ],
            "series": [
                {
                    "name": "Corridas Nuevas", "type": "bar", "stack": "total", "data": d_nv, "barMaxWidth": 14,
                    "itemStyle": {"color": _G, "borderRadius": [0, 0, 0, 0]}
                },
                {
                    "name": "Intervenciones WS", "type": "bar", "stack": "total", "data": d_ws, "barMaxWidth": 14,
                    "itemStyle": {"color": _Y, "borderRadius": [3, 3, 0, 0]}
                },
                {
                    "name": "Fallas Nuevos", "type": "line", "yAxisIndex": 1, "data": d_fl_nuevo, "smooth": True,
                    "lineStyle": {"width": 2, "color": _R}, "itemStyle": {"color": _R}
                },
                {
                    "name": "Fallas WS", "type": "line", "yAxisIndex": 1, "data": d_fl_ws, "smooth": True,
                    "lineStyle": {"width": 2, "color": "#ff7043", "type": "dashed"}, "itemStyle": {"color": "#ff7043"}
                }
            ]
        }
        
        components.html(_echarts_html(opts_camp, 370, "chart_campana_tab"), height=380)

    with col_table:
        st.markdown(f"<h6 style='color:{_G}; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>📋 Detalle de Corridas y Eventos de la Campaña</h6>", unsafe_allow_html=True)
        render_campanas_table(df_camp)

    # === TABLA RESUMEN DE CAMPAÑA (ANCHO COMPLETO, DEBAJO DE AMBAS COLUMNAS) ===
    fallados_nuevos = df_camp[(df_camp['RUN'] == 1) & (df_camp['Falla'] == 1)].shape[0] if not df_camp.empty else 0
    fallados_ws     = df_camp[(df_camp['RUN'] > 1) & (df_camp['Falla'] == 1)].shape[0] if not df_camp.empty else 0
    
    pct_nuevos = (fallados_nuevos / val_nuevos * 100) if val_nuevos > 0 else 0.0
    pct_ws     = (fallados_ws / val_ws * 100) if val_ws > 0 else 0.0
    
    total_falladas = fallados_nuevos + fallados_ws
    pct_total  = (total_falladas / total_corridas * 100) if total_corridas > 0 else 0.0
    
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <table style="width:100%; border-collapse:collapse; border-radius:8px; overflow:hidden; border:1px solid rgba(19, 118, 89, 0.15); font-family:Inter, sans-serif; font-size:10px; text-align:center; background:#ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
      <thead>
        <tr style="background-color:rgba(19, 118, 89, 0.08); color:#137659; font-weight:bold;">
          <th style="padding:6px; border-bottom:1px solid rgba(19, 118, 89, 0.15); text-align:left;">⚙️ TIPO DE CORRIDA</th>
          <th style="padding:6px; border-bottom:1px solid rgba(19, 118, 89, 0.15);">🚀 TOTAL CORRIDAS</th>
          <th style="padding:6px; border-bottom:1px solid rgba(19, 118, 89, 0.15);">⚠️ CORRIDAS FALLADAS</th>
          <th style="padding:6px; border-bottom:1px solid rgba(19, 118, 89, 0.15);">📈 TASA DE FALLAS</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:6px; font-weight:bold; color:#137659; text-align:left; border-bottom:1px solid rgba(19, 118, 89, 0.08);">🆕 NUEVO (Corrida = 1)</td>
          <td style="padding:6px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{val_nuevos}</td>
          <td style="padding:6px; color:#c62828; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{fallados_nuevos}</td>
          <td style="padding:6px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08); color:#c62828;">{pct_nuevos:.1f}%</td>
        </tr>
        <tr style="background-color:rgba(192, 156, 46, 0.02);">
          <td style="padding:6px; font-weight:bold; color:#c09c2e; text-align:left; border-bottom:1px solid rgba(19, 118, 89, 0.08);">🛠️ WELL SERVICE (Corrida > 1)</td>
          <td style="padding:6px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{val_ws}</td>
          <td style="padding:6px; color:#c62828; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08);">{fallados_ws}</td>
          <td style="padding:6px; font-weight:bold; border-bottom:1px solid rgba(19, 118, 89, 0.08); color:#c62828;">{pct_ws:.1f}%</td>
        </tr>
        <tr style="background-color:rgba(19, 118, 89, 0.05); font-weight:bold;">
          <td style="padding:6px; text-align:left;">📊 RESUMEN CAMPAÑA</td>
          <td style="padding:6px;">{total_corridas}</td>
          <td style="padding:6px; color:#c62828;">{total_falladas}</td>
          <td style="padding:6px; color:#137659;">{pct_total:.1f}%</td>
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)

    # === DISTRIBUCIÓN DE FALLAS POR CATEGORÍA Y ETAPA ===
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    df_fallas = df_camp[df_camp['Falla'] == 1].copy()
    if not df_fallas.empty:
        st.markdown(f"<h6 style='color:{_G}; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>🎯 Distribución de Fallas: Categoría vs Etapa de Vida</h6>", unsafe_allow_html=True)
        col_razon = 'RAZON_DE_PULL' if 'RAZON_DE_PULL' in df_fallas.columns else ('RAZON ESPECIFICA PULL' if 'RAZON ESPECIFICA PULL' in df_fallas.columns else None)
            
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
        for c in causas_orden:
            if c not in df_dist.index: df_dist.loc[c] = 0
        for e in etapas_orden:
            if e not in df_dist.columns: df_dist[e] = 0
            
        df_dist = df_dist.loc[causas_orden, etapas_orden]
        etapa_colors = {'Infantil': _R, 'Prematura': _Y, 'En Garantía': _G, 'Sin Garantía': '#5b5c55', 'N/A': '#94a3b8'}
        
        series_data = []
        for etapa in etapas_orden:
            series_data.append({
                "name": etapa, "type": "bar", "stack": "total", "barMaxWidth": 40,
                "itemStyle": {"color": etapa_colors[etapa]},
                "data": df_dist[etapa].tolist()
            })
            
        series_data[-1]["markLine"] = {
            "symbol": "none",
            "lineStyle": {"color": _R, "type": "dashed", "width": 1.5},
            "label": {"show": True, "position": "middle", "formatter": "ALS ⬅️ | ➡️ Externas", "color": _R, "fontSize": 10, "fontWeight": "bold"},
            "data": [{"xAxis": 1.5}]
        }
        
        opts_dist = {
            "backgroundColor": "transparent",
            "tooltip": {
                "trigger": "axis", "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                "textStyle": {"color": _T, "fontSize": 12, "fontFamily": "Inter, sans-serif"},
            },
            "legend": {"data": etapas_orden, "bottom": 0, "textStyle": {"color": _T2, "fontSize": 10, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
            "grid": {"top": "15%", "left": "3%", "right": "4%", "bottom": "15%", "containLabel": True},
            "xAxis": {
                "type": "category", "data": causas_orden,
                "axisLabel": {"color": _T, "fontSize": 11, "fontWeight": "bold", "fontFamily": "Inter, sans-serif"},
                "axisLine": {"lineStyle": {"color": "rgba(19,118,89,0.3)"}}
            },
            "yAxis": {
                "type": "value", "name": "Fallas",
                "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.1)", "type": "dashed"}}
            },
            "series": series_data
        }
        
        components.html(_echarts_html(opts_dist, 380, "chart_dist_fallas"), height=400)
