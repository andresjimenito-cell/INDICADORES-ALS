"""
tabs/tab_campanas.py  —  v4.2 Campañas de Intervención Premium
==============================================================
Estética ejecutiva unificada con tab_tablero (Parex Industrial UI):
1. Hero Header ejecutivo con información contextual del periodo y filtros.
2. Tarjetas KPI de 3 capas con tipografía Source Serif 4 y halos circulares.
3. Gráfico interactivo ECharts de Corridas vs Fallas por mes con gradientes suaves.
4. Distribución de fallas por etapa de vida útil con markline ALS.
5. Tabla HUD con badges inline, DataTables y estética ejecutiva.
"""

import json
import calendar
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from core.calculations import clasificar_razon_ia, clasificar_runlife
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


def _echarts_html(options: dict, height: int, chart_id: str) -> str:
    """Wrapper para ECharts con estilo unificado."""
    return f"""
    <div id="{chart_id}" style="width:100%;height:{height}px;{_CARD}overflow:hidden;box-sizing:border-box;"></div>
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
        ff_str = ff.strftime('%Y-%m-%d') if pd.notna(ff) else '<span style="color:#707070;">-</span>'
        fp = row.get('FECHA_PULL')
        fp_str = fp.strftime('%Y-%m-%d') if pd.notna(fp) else '<span style="color:#2E7D46; font-weight:bold;">PENDIENTE</span>'
        razon = str(row.get(col_razon, '')) if col_razon else ''
        
        run_val = row.get('RUN', 1)
        tipo_badge = '<span class="badge-custom badge-nuevo">NUEVO</span>' if run_val == 1 else '<span class="badge-custom badge-ws">WS</span>'
            
        is_falla = row.get('Falla', 0)
        if is_falla == 1:
            estado_badge = '<span class="badge-custom badge-fallado">FALLA</span>'
            run_life = (ff - fr).days if pd.notna(ff) and pd.notna(fr) else '-'
            sub_tipo = row.get('SUB TIPO DE FALLA')
            if pd.notna(sub_tipo) and str(sub_tipo).strip() != '':
                causa = clasificar_razon_ia(str(sub_tipo))
            else:
                causa = clasificar_razon_ia(razon) if razon.strip() != '' else 'Desconocida'
                if pd.isna(fp):
                    causa = f"Posible {causa}"
        else:
            estado_badge = '<span class="badge-custom badge-operativo">OK</span>'
            run_life = '<span style="color:#707070;">-</span>'
            causa = '<span style="color:#707070;">-</span>'
            
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
        @import url('{_FONTS_URL}');
        @import url('https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css');
        
        body {{ background: transparent; color: {_T}; font-family: {_FS}; margin:0; padding:0; }}
        .dataTables_wrapper {{ color: {_T} !important; }}
        .dataTables_filter input {{ 
            background: #ffffff; 
            border: 1px solid {_BR}; 
            color: {_T}; 
            border-radius: 8px; 
            padding: 5px 10px; 
            font-size: 11px;
            font-family: {_FS};
            outline: none;
            transition: border-color 0.2s;
        }}
        .dataTables_filter input:focus {{ border-color: {_G}; }}
        .dataTables_filter label {{ color: {_T2}; font-size: 11px; font-family: {_FS}; }}
        table.dataTable {{ width: 100% !important; }}
        table.dataTable thead th {{ 
            background: rgba(46, 125, 70, 0.08); 
            color: {_G2}; 
            font-family: {_FS}; 
            font-size: 10px; 
            font-weight: 800; 
            text-transform: uppercase; 
            letter-spacing: 0.6px; 
            padding: 8px 10px; 
            border-bottom: 1px solid {_BR} !important;
        }}
        table.dataTable tbody td {{ 
            border-bottom: 1px solid rgba(220, 226, 216, 0.6); 
            padding: 7px 10px; 
            font-size: 11px; 
            color: {_T}; 
            font-family: {_FS};
        }}
        .dataTables_info, .dataTables_paginate {{ color: {_T2} !important; font-size: 10.5px; font-family: {_FS}; }}
        
        .badge-custom {{
            display: inline-block;
            padding: 2px 8px;
            font-size: 8.5px;
            font-weight: 700;
            border-radius: 12px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }}
        .badge-nuevo {{ background-color: {_G3}; color: {_G2}; border: 1px solid rgba(46, 125, 70, 0.3); }}
        .badge-ws {{ background-color: {_Y2}; color: {_Y}; border: 1px solid rgba(201, 138, 44, 0.3); }}
        .badge-fallado {{ background-color: {_R2}; color: {_R}; border: 1px solid rgba(192, 57, 43, 0.3); }}
        .badge-operativo {{ background-color: {_G3}; color: {_G}; border: 1px solid rgba(46, 125, 70, 0.3); }}
    </style>
    
    <div style="{_CARD} padding:10px; box-sizing:border-box; width:100%; overflow:hidden;">
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
                    if (data[7] && data[7].indexOf("FALLA") !== -1) {{
                        $(row).css("background-color", "rgba(192, 57, 43, 0.04)");
                    }}
                }}
            }});
        }});
    </script>
    """, height=380)


def render_tab_campanas(df_bd_filtered, df_forma9_filtered, fecha_evaluacion, selected_activo):
    """Renderiza la pestaña de Campañas con la estética unificada de tab_tablero."""
    
    df_bd_raw = st.session_state.get('df_bd_calculated')
    df_bd_untr = df_bd_raw.copy() if df_bd_raw is not None else df_bd_filtered.copy()
    EXCLUIDOS = {
        'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
        'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
        'MAPACHE/PERICO', 'MAPACHE-PERICO',
        'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
        'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
        'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE'
    }
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
            
    df_bd_untr['FECHA_RUN'] = pd.to_datetime(df_bd_untr['FECHA_RUN'], errors='coerce')
    df_bd_untr['FECHA_FALLA'] = pd.to_datetime(df_bd_untr['FECHA_FALLA'], errors='coerce')
    df_bd_untr['FECHA_PULL'] = pd.to_datetime(df_bd_untr['FECHA_PULL'], errors='coerce')
    
    years = sorted(df_bd_untr['FECHA_RUN'].dt.year.dropna().unique().astype(int))
    if not years:
        st.warning("No hay campanas disponibles en los datos filtrados.")
        return
        
    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    default_year = fecha_eval_dt.year
    if default_year not in years:
        default_year = years[-1]
        
    c_sel, c_blank = st.columns([2, 4])
    with c_sel:
        selected_years = st.multiselect(
            "📅 Seleccionar Años de Campaña:",
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
    
    tasa_exito = ((total_corridas - val_fallas) / total_corridas * 100) if total_corridas > 0 else 0
    extraidos = df_camp[df_camp['FECHA_PULL'].notna()].shape[0]
    activas = total_corridas - extraidos

    # ── ENCABEZADO EJECUTIVO (ESTILO TABLERO) ──────────────────────────────────
    anios_str = ", ".join(str(y) for y in sorted(selected_years))
    _activos_lbl = " · ".join(v for v in _filtros.values() if v != 'TODOS') or "Todos los activos"
    
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
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
          </svg>
        </div>
        <div>
          <div class="tbl-hero-title">Campañas de Intervención e Instalación</div>
          <div style="font-family:{_FS}; font-size:11.5px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
            <div class="tbl-hero-dot"></div>
            <span>Efectividad y supervivencia de corridas nuevas vs intervenciones</span>
          </div>
        </div>
      </div>
      <div class="tbl-hero-ctx">
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Campaña(s)</span>
          <span class="tbl-hero-v">{anios_str}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Filtros Activos</span>
          <span class="tbl-hero-v">{_activos_lbl}</span>
        </div>
        <div class="tbl-hero-item">
          <span class="tbl-hero-k">Total Instalaciones</span>
          <span class="tbl-hero-v">{total_corridas} pozos</span>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # ── KPI ROW (4 TARJETAS CON ELEVACIÓN _CARD Y HALOS) ─────────────────────
    st.markdown(f"""
    <style>
    .camp-card {{
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
    .camp-card:hover {{
        border-color: rgba(46,125,70,0.30);
        box-shadow: {_SH2};
        transform: translateY(-2px);
    }}
    .camp-icon {{
        width: 32px; height: 32px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 6px;
    }}
    .camp-icon.green  {{ background: linear-gradient(160deg, #4CA46A 0%, {_G} 100%);  box-shadow: {_halo(_G)}; }}
    .camp-icon.dark   {{ background: linear-gradient(160deg, {_G} 0%, {_G2} 100%);     box-shadow: {_halo(_G2)}; }}
    .camp-icon.gold   {{ background: linear-gradient(160deg, #E0B44C 0%, {_Y} 100%);  box-shadow: {_halo(_Y)}; }}
    .camp-icon.red    {{ background: linear-gradient(160deg, #D9584A 0%, {_R} 100%);  box-shadow: {_halo(_R)}; }}
    
    .camp-lbl {{ font-family: {_FS}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
    .camp-val {{ font-family: {_FN}; font-size: 32px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
    .camp-sub {{ font-family: {_FS}; font-size: 10px; color: {_T2}; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="camp-card">
            <div class="camp-icon green">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            </div>
            <div class="camp-lbl">Corridas Nuevas</div>
            <div class="camp-val" style="color:{_G};">{val_nuevos}</div>
            <div class="camp-sub">Primera instalación (Run = 1)</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="camp-card">
            <div class="camp-icon gold">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
            </div>
            <div class="camp-lbl">Corridas WS</div>
            <div class="camp-val" style="color:{_Y};">{val_ws}</div>
            <div class="camp-sub">Intervenciones (Run > 1)</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="camp-card">
            <div class="camp-icon red">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01"/></svg>
            </div>
            <div class="camp-lbl">Fallas Registradas</div>
            <div class="camp-val" style="color:{_R};">{val_fallas}</div>
            <div class="camp-sub">{val_fallas/total_corridas*100:.1f}% tasa de falla</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="camp-card">
            <div class="camp-icon dark">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <div class="camp-lbl">Tasa de Éxito</div>
            <div class="camp-val" style="color:{_G2};">{tasa_exito:.1f}<span style="font-size:16px;">%</span></div>
            <div class="camp-sub">{activas} activas | {extraidos} extraídos</div>
        </div>
        """, unsafe_allow_html=True)
            
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    
    # ── FILA: GRÁFICO Y TABLA DE EVENTOS ─────────────────────────────────────
    col_chart, col_table = st.columns([1, 1], gap="medium")
    
    with col_chart:
        st.markdown(f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800; letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>Correlacion Corridas vs Fallas (Mensual)</h6>", unsafe_allow_html=True)
        
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
                "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                "textStyle": {"color": _T, "fontSize": 11, "fontFamily": "Inter, sans-serif"},
            },
            "legend": {
                "data": ["Corridas Nuevas", "Intervenciones WS", "Fallas Nuevos", "Fallas WS"],
                "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"},
                "bottom": 4, "icon": "circle"
            },
            "grid": {"top": "12%", "left": "3%", "right": "3%", "bottom": "18%", "containLabel": True},
            "xAxis": {
                "type": "category", "data": cats,
                "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif", "rotate": 25},
                "axisLine": {"lineStyle": {"color": _BR}}
            },
            "yAxis": [
                {
                    "type": "value", "name": "Corridas",
                    "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                    "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif"},
                    "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}},
                },
                {
                    "type": "value", "name": "Fallas", "position": "right",
                    "nameTextStyle": {"color": _R, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                    "axisLabel": {"color": _R, "fontSize": 8.5, "fontFamily": "Inter, sans-serif"},
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
                    "lineStyle": {"width": 2.2, "color": _R}, "itemStyle": {"color": _R}
                },
                {
                    "name": "Fallas WS", "type": "line", "yAxisIndex": 1, "data": d_fl_ws, "smooth": True,
                    "lineStyle": {"width": 2.2, "color": "#E67E22", "type": "dashed"}, "itemStyle": {"color": "#E67E22"}
                }
            ]
        }
        
        components.html(_echarts_html(opts_camp, 370, "chart_campana_tab"), height=380)

    with col_table:
        st.markdown(f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800; letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>📋 Detalle de Corridas y Eventos de la Campaña</h6>", unsafe_allow_html=True)
        render_campanas_table(df_camp)

    # ── TABLA RESUMEN DE CAMPAÑA ──────────────────────────────────────────────
    fallados_nuevos = df_camp[(df_camp['RUN'] == 1) & (df_camp['Falla'] == 1)].shape[0] if not df_camp.empty else 0
    fallados_ws     = df_camp[(df_camp['RUN'] > 1) & (df_camp['Falla'] == 1)].shape[0] if not df_camp.empty else 0
    
    pct_nuevos = (fallados_nuevos / val_nuevos * 100) if val_nuevos > 0 else 0.0
    pct_ws     = (fallados_ws / val_ws * 100) if val_ws > 0 else 0.0
    
    total_falladas = fallados_nuevos + fallados_ws
    pct_total  = (total_falladas / total_corridas * 100) if total_corridas > 0 else 0.0
    
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="{_CARD} padding:14px 18px; box-sizing:border-box; margin-bottom:12px;">
      <table style="width:100%; border-collapse:collapse; font-family:{_FS}; font-size:11px; text-align:center;">
        <thead>
          <tr style="background-color:rgba(46, 125, 70, 0.08); color:{_G2}; font-weight:800; text-transform:uppercase; letter-spacing:0.6px;">
            <th style="padding:8px 10px; border-bottom:1px solid {_BR}; text-align:left; border-radius:6px 0 0 6px;">Tipo de Corrida</th>
            <th style="padding:8px 10px; border-bottom:1px solid {_BR};">Total Corridas</th>
            <th style="padding:8px 10px; border-bottom:1px solid {_BR};">Corridas Falladas</th>
            <th style="padding:8px 10px; border-bottom:1px solid {_BR}; border-radius:0 6px 6px 0;">Tasa de Fallas</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style="padding:8px 10px; font-weight:700; color:{_G2}; text-align:left; border-bottom:1px solid rgba(220, 226, 216, 0.6);">NUEVO (Corrida = 1)</td>
            <td style="padding:8px 10px; font-weight:700; font-family:{_FN}; font-size:13px; border-bottom:1px solid rgba(220, 226, 216, 0.6);">{val_nuevos}</td>
            <td style="padding:8px 10px; color:{_R}; font-weight:700; font-family:{_FN}; font-size:13px; border-bottom:1px solid rgba(220, 226, 216, 0.6);">{fallados_nuevos}</td>
            <td style="padding:8px 10px; font-weight:700; border-bottom:1px solid rgba(220, 226, 216, 0.6); color:{_R};">{pct_nuevos:.1f}%</td>
          </tr>
          <tr style="background-color:rgba(201, 138, 44, 0.03);">
            <td style="padding:8px 10px; font-weight:700; color:{_Y}; text-align:left; border-bottom:1px solid rgba(220, 226, 216, 0.6);">WELL SERVICE (Corrida > 1)</td>
            <td style="padding:8px 10px; font-weight:700; font-family:{_FN}; font-size:13px; border-bottom:1px solid rgba(220, 226, 216, 0.6);">{val_ws}</td>
            <td style="padding:8px 10px; color:{_R}; font-weight:700; font-family:{_FN}; font-size:13px; border-bottom:1px solid rgba(220, 226, 216, 0.6);">{fallados_ws}</td>
            <td style="padding:8px 10px; font-weight:700; border-bottom:1px solid rgba(220, 226, 216, 0.6); color:{_R};">{pct_ws:.1f}%</td>
          </tr>
          <tr style="background-color:rgba(46, 125, 70, 0.06); font-weight:800;">
            <td style="padding:8px 10px; text-align:left; color:{_G2}; border-radius:0 0 0 6px;">TOTAL CAMPANA</td>
            <td style="padding:8px 10px; font-family:{_FN}; font-size:14px; color:{_T};">{total_corridas}</td>
            <td style="padding:8px 10px; color:{_R}; font-family:{_FN}; font-size:14px;">{total_falladas}</td>
            <td style="padding:8px 10px; color:{_G2}; font-size:12px; border-radius:0 0 6px 0;">{pct_total:.1f}%</td>
          </tr>
        </tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    # ── DISTRIBUCIÓN DE FALLAS POR CATEGORÍA Y ETAPA ─────────────────────────
    df_fallas = df_camp[df_camp['Falla'] == 1].copy()
    if not df_fallas.empty:
        st.markdown(f"<h6 style='color:{_G2}; font-family:{_FS}; font-weight:800; letter-spacing:0.8px; text-transform:uppercase; font-size:0.75rem; margin-bottom:8px;'>Distribucion de Fallas: Categoria vs Etapa de Vida</h6>", unsafe_allow_html=True)
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
        etapa_colors = {'Infantil': _R, 'Prematura': _Y, 'En Garantía': _G, 'Sin Garantía': '#5C6B73', 'N/A': '#B0B8B0'}
        
        series_data = []
        for etapa in etapas_orden:
            series_data.append({
                "name": etapa, "type": "bar", "stack": "total", "barMaxWidth": 36,
                "itemStyle": {"color": etapa_colors[etapa]},
                "data": df_dist[etapa].tolist()
            })
            
        series_data[-1]["markLine"] = {
            "symbol": "none",
            "lineStyle": {"color": _R, "type": "dashed", "width": 1.5},
            "label": {"show": True, "position": "middle", "formatter": "ALS <- | -> Externas", "color": _R, "fontSize": 10, "fontWeight": "bold", "fontFamily": "Inter, sans-serif"},
            "data": [{"xAxis": 1.5}]
        }
        
        opts_dist = {
            "backgroundColor": "transparent",
            "tooltip": {
                "trigger": "axis", "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                "textStyle": {"color": _T, "fontSize": 11, "fontFamily": "Inter, sans-serif"},
            },
            "legend": {"data": etapas_orden, "bottom": 4, "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
            "grid": {"top": "12%", "left": "3%", "right": "4%", "bottom": "16%", "containLabel": True},
            "xAxis": {
                "type": "category", "data": causas_orden,
                "axisLabel": {"color": _T, "fontSize": 10.5, "fontWeight": "600", "fontFamily": "Inter, sans-serif"},
                "axisLine": {"lineStyle": {"color": _BR}}
            },
            "yAxis": {
                "type": "value", "name": "Fallas",
                "nameTextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 9},
                "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}
            },
            "series": series_data
        }
        
        components.html(_echarts_html(opts_dist, 380, "chart_dist_fallas"), height=390)
