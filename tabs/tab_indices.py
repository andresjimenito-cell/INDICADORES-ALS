"""
tabs/tab_indices.py
===================
Visualización profesional de Índices de Falla y Operatividad.
Utiliza estética HUD y Zero Space Waste.
"""

import json
import re
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go_fig
from data.config import COLOR_PRINCIPAL
from core.indice_falla import calcular_indice_falla_anual
from core.mtbf import calcular_mtbf
from ui.styles import render_hud_table
from core.calculations import clasificar_razon_ia

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

# Decorador seguro para fragmentos de Streamlit (renderizado local instantáneo)
if hasattr(st, 'fragment'):
    _fragment = st.fragment
else:
    def _fragment(func):
        return func

@st.cache_data(show_spinner=False)
def _calcular_rl_agrupado_cached(df_raw, grupo_col, fecha_eval_norm, anio_prev_val, solo_fallas_als=True):
    """
    Calcula agregación de Run Life y MTBF por Campo, Bloque o Proveedor.
    Optimizado y cacheado para ejecución instantánea.
    """
    prev_yr_end = pd.to_datetime(f"{anio_prev_val}-12-31").normalize()
    EXCL_RL = {
        'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
        'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
        'MAPACHE/PERICO', 'MAPACHE-PERICO',
        'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
        'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
        'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE', 'TODOS'
    }
    res_list = []
    if grupo_col not in df_raw.columns:
        return res_list
    for grupo_val, grp_sub in df_raw.groupby(grupo_col):
        if pd.isna(grupo_val) or str(grupo_val).strip() == '' or str(grupo_val).strip().upper() in EXCL_RL:
            continue
        grp_runs_sub = grp_sub[grp_sub['_RUN'] <= fecha_eval_norm]
        tot_pozos_unicos = grp_runs_sub['POZO'].nunique() if 'POZO' in grp_runs_sub.columns else len(grp_runs_sub)
        tot_corridas = len(grp_runs_sub)
        if tot_pozos_unicos == 0 and tot_corridas == 0:
            continue
        
        grp_op = grp_runs_sub[
            (grp_runs_sub['_RUN'] <= fecha_eval_norm) &
            (grp_runs_sub['_FALL'].isna() | (grp_runs_sub['_FALL'] > fecha_eval_norm)) &
            (grp_runs_sub['_PULL'].isna() | (grp_runs_sub['_PULL'] > fecha_eval_norm))
        ]
        n_op = grp_op['POZO'].nunique() if 'POZO' in grp_op.columns else len(grp_op)
        rl_op_s = (fecha_eval_norm - pd.to_datetime(grp_op['_RUN'])).dt.days
        rl_op_val = float(rl_op_s.mean()) if len(rl_op_s) > 0 else 0.0
        rle_op_s = grp_op['_RLE']
        rle_op_val = float(rle_op_s.mean()) if len(rle_op_s) > 0 and (rle_op_s > 0).any() else rl_op_val

        desglose_op = []
        if not grp_op.empty and 'PROVEEDOR' in grp_op.columns:
            for prov_k, grp_op_p in grp_op.groupby('PROVEEDOR'):
                if pd.notna(prov_k) and str(prov_k).strip():
                    p_cnt = grp_op_p['POZO'].nunique() if 'POZO' in grp_op_p.columns else len(grp_op_p)
                    p_rl = (fecha_eval_norm - pd.to_datetime(grp_op_p['_RUN'])).dt.days.mean()
                    p_rle = grp_op_p['_RLE'].mean() if '_RLE' in grp_op_p.columns and (grp_op_p['_RLE'] > 0).any() else p_rl
                    desglose_op.append({
                        'prov': str(prov_k).strip(),
                        'pozos': p_cnt,
                        'rl': round(float(p_rl), 1) if pd.notna(p_rl) else 0.0,
                        'rle': round(float(p_rle), 1) if pd.notna(p_rle) else 0.0
                    })
            desglose_op.sort(key=lambda x: x['pozos'], reverse=True)

        if solo_fallas_als and 'INDICADOR_MTBF' in grp_runs_sub.columns:
            grp_fall = grp_runs_sub[
                (grp_runs_sub['_FALL'].notna()) &
                (grp_runs_sub['_FALL'] <= fecha_eval_norm) &
                (grp_runs_sub['INDICADOR_MTBF'] == 1)
            ]
        else:
            grp_fall = grp_runs_sub[
                (grp_runs_sub['_FALL'].notna()) &
                (grp_runs_sub['_FALL'] <= fecha_eval_norm)
            ]
        tot_fallas = len(grp_fall)
        pozos_unicos_fall = grp_fall['POZO'].nunique() if 'POZO' in grp_fall.columns else tot_fallas
        rl_fall_s = (pd.to_datetime(grp_fall['_FALL']) - pd.to_datetime(grp_fall['_RUN'])).dt.days
        rl_fall_val = float(rl_fall_s.mean()) if len(rl_fall_s) > 0 else 0.0
        rle_fall_s = grp_fall['_RLE']
        rle_fall_val = float(rle_fall_s.mean()) if len(rle_fall_s) > 0 and (rle_fall_s > 0).any() else rl_fall_val

        rl_pond_val = ((n_op * rl_op_val) + (tot_fallas * rl_fall_val)) / max(n_op + tot_fallas, 1)
        rle_pond_val = ((n_op * rle_op_val) + (tot_fallas * rle_fall_val)) / max(n_op + tot_fallas, 1)
        dias_falla_tot_val = tot_fallas * rl_fall_val
        dias_rle_falla_tot_val = tot_fallas * rle_fall_val

        desglose_fall = []
        if not grp_fall.empty and 'PROVEEDOR' in grp_fall.columns:
            for prov_k, grp_fall_p in grp_fall.groupby('PROVEEDOR'):
                if pd.notna(prov_k) and str(prov_k).strip():
                    p_fallas_cnt = len(grp_fall_p)
                    p_pozos_cnt = grp_fall_p['POZO'].nunique() if 'POZO' in grp_fall_p.columns else p_fallas_cnt
                    p_rl = (pd.to_datetime(grp_fall_p['_FALL']) - pd.to_datetime(grp_fall_p['_RUN'])).dt.days.mean()
                    p_rle = grp_fall_p['_RLE'].mean() if '_RLE' in grp_fall_p.columns and (grp_fall_p['_RLE'] > 0).any() else p_rl
                    desglose_fall.append({
                        'prov': str(prov_k).strip(),
                        'fallas': p_fallas_cnt,
                        'pozos': p_pozos_cnt,
                        'rl': round(float(p_rl), 1) if pd.notna(p_rl) else 0.0,
                        'rle': round(float(p_rle), 1) if pd.notna(p_rle) else 0.0
                    })
            desglose_fall.sort(key=lambda x: x['fallas'], reverse=True)

        grp_prev_sub = grp_sub[grp_sub['_RUN'] <= prev_yr_end]
        grp_op_prev_sub = grp_prev_sub[
            (grp_prev_sub['_RUN'] <= prev_yr_end) &
            (grp_prev_sub['_FALL'].isna() | (grp_prev_sub['_FALL'] > prev_yr_end)) &
            (grp_prev_sub['_PULL'].isna() | (grp_prev_sub['_PULL'] > prev_yr_end))
        ]
        rl_prev_sub_s = (prev_yr_end - pd.to_datetime(grp_op_prev_sub['_RUN'])).dt.days
        m_rl = round(float(rl_prev_sub_s.mean()), 1) if len(rl_prev_sub_s) > 0 else 1500.0
        rle_prev_sub_s = grp_op_prev_sub['_RLE']
        m_rle = round(float(rle_prev_sub_s.mean()), 1) if len(rle_prev_sub_s) > 0 and (rle_prev_sub_s > 0).any() else m_rl

        mtbf_flota_val, _ = calcular_mtbf(grp_sub, fecha_eval_norm)
        col_rle_sub = 'RUN_LIFE_EFECTIVO' if 'RUN_LIFE_EFECTIVO' in grp_sub.columns else 'RUN LIFE'
        mtbf_flota_efec_val, _ = calcular_mtbf(grp_sub, fecha_eval_norm, col_life=col_rle_sub) if col_rle_sub in grp_sub.columns else (mtbf_flota_val, None)

        mtbf_sf_val, _ = calcular_mtbf(grp_fall, fecha_eval_norm) if not grp_fall.empty else (0.0, None)
        mtbf_sf_efec_val, _ = calcular_mtbf(grp_fall, fecha_eval_norm, col_life=col_rle_sub) if not grp_fall.empty and col_rle_sub in grp_fall.columns else (mtbf_sf_val, None)

        if n_op > 0 or tot_fallas > 0 or (mtbf_flota_val and mtbf_flota_val > 0) or (mtbf_sf_val and mtbf_sf_val > 0):
            res_list.append({
                'nombre': str(grupo_val).strip(),
                'total_pozos_unicos': tot_pozos_unicos,
                'total_corridas': tot_corridas,
                'total': tot_pozos_unicos,
                'pozos_op': n_op,
                'tot_fallas': tot_fallas,
                'pozos_fall_unicos': pozos_unicos_fall,
                'pozos_fall': tot_fallas,
                'rl_op': round(rl_op_val, 1),
                'rle_op': round(rle_op_val, 1),
                'rl_fall': round(rl_fall_val, 1),
                'rle_fall': round(rle_fall_val, 1),
                'rl_pond': round(rl_pond_val, 1),
                'rle_pond': round(rle_pond_val, 1),
                'dias_falla_tot': dias_falla_tot_val,
                'dias_rle_falla_tot': dias_rle_falla_tot_val,
                'mtbf': round(mtbf_flota_val, 1) if mtbf_flota_val is not None else 0.0,
                'mtbf_efec': round(mtbf_flota_efec_val, 1) if mtbf_flota_efec_val is not None else 0.0,
                'mtbf_flota': round(mtbf_flota_val, 1) if mtbf_flota_val is not None else 0.0,
                'mtbf_flota_efec': round(mtbf_flota_efec_val, 1) if mtbf_flota_efec_val is not None else 0.0,
                'mtbf_sf': round(mtbf_sf_val, 1) if mtbf_sf_val is not None else 0.0,
                'mtbf_sf_efec': round(mtbf_sf_efec_val, 1) if mtbf_sf_efec_val is not None else 0.0,
                'meta_rl': m_rl,
                'meta_rle': m_rle,
                'desglose_op': desglose_op,
                'desglose_fall': desglose_fall,
            })

    tot_fall_g = sum(d['tot_fallas'] for d in res_list)
    tot_dias_f_g = sum(d['dias_falla_tot'] for d in res_list)
    tot_dias_rle_f_g = sum(d['dias_rle_falla_tot'] for d in res_list)
    
    for d in res_list:
        d['pct_fallas'] = (d['tot_fallas'] / max(tot_fall_g, 1)) * 100.0
        d['aporte_rl_fall'] = (d['tot_fallas'] / max(tot_fall_g, 1)) * d['rl_fall']
        d['aporte_rle_fall'] = (d['tot_fallas'] / max(tot_fall_g, 1)) * d['rle_fall']
        d['pct_dias_falla'] = (d['dias_falla_tot'] / max(tot_dias_f_g, 1)) * 100.0
        d['pct_dias_rle_falla'] = (d['dias_rle_falla_tot'] / max(tot_dias_rle_f_g, 1)) * 100.0

    return res_list


@_fragment
def _render_seccion_run_life_bloque(df_bloque_raw, fecha_eval_norm_b, anio_prev, fecha_eval_dt_b, EXCL_BLOQUES):
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    col_rl_head, col_rl_grp, col_rl_prov, col_rl_sel = st.columns([1.1, 0.9, 0.9, 0.9])
    with col_rl_head:
        st.markdown(f"<h6 style='color:#137659; font-family:Inter, sans-serif; font-weight:800; letter-spacing:1px; text-transform:uppercase; font-size:0.8rem; margin-top:6px; margin-bottom:10px;'>⏱️ Run Life: Pozos Operativos vs Fallados ALS (a {fecha_eval_dt_b.strftime('%Y-%m-%d')})</h6>", unsafe_allow_html=True)
    with col_rl_grp:
        has_modelo_rl = any(any(k in str(c).upper() for k in ['MODELO DE BOMBA', 'MODELO DE BOMABA', 'MODELO BOMBA', 'MODELO']) for c in df_bloque_raw.columns)
        rl_options = ["Bloque", "Campo", "Proveedor", "Modelo de Bomba"] if has_modelo_rl else ["Bloque", "Campo", "Proveedor"]
        agrupacion_rl = st.radio(
            "Agrupar por:",
            options=rl_options,
            index=0,
            horizontal=True,
            key="rl_agrupacion_selector"
        )
    with col_rl_prov:
        prov_list = ["TODOS"] + sorted([str(p).strip() for p in df_bloque_raw['PROVEEDOR'].dropna().unique() if str(p).strip() != '' and str(p).strip().upper() not in EXCL_BLOQUES]) if 'PROVEEDOR' in df_bloque_raw.columns else ["TODOS"]
        prov_filter_rl = st.selectbox(
            "Filtrar Proveedor:",
            options=prov_list,
            index=0,
            key="rl_proveedor_filter_select",
            disabled=(agrupacion_rl in ["Proveedor", "Modelo de Bomba"])
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
        col_mod_f = next((c for c in df_bloque_raw.columns if any(k in str(c).upper() for k in ['MODELO DE BOMBA', 'MODELO DE BOMABA', 'MODELO BOMBA', 'MODELO'])), 'MODELO DE BOMBA')
        if agrupacion_rl == "Proveedor":
            grupo_col_sel = 'PROVEEDOR'
            df_para_rl = df_bloque_raw.copy()
        elif agrupacion_rl == "Modelo de Bomba":
            grupo_col_sel = col_mod_f
            df_para_rl = df_bloque_raw.copy()
        elif prov_filter_rl != "TODOS":
            grupo_col_sel = 'CAMPO' if agrupacion_rl == "Campo" else 'BLOQUE'
            df_para_rl = df_bloque_raw[df_bloque_raw['PROVEEDOR'] == prov_filter_rl].copy()
        else:
            grupo_col_sel = 'CAMPO' if agrupacion_rl == "Campo" else 'BLOQUE'
            df_para_rl = df_bloque_raw.copy()

        items_rl = _calcular_rl_agrupado_cached(df_para_rl, grupo_col_sel, fecha_eval_norm_b, anio_prev, solo_fallas_als=True)

        for d in items_rl:
            if opcion_rl_bloque == "Run Life Efectivo":
                d['active_rl_op'] = d['rle_op']
                d['active_rl_fall'] = d['rle_fall']
                d['active_rl_pond'] = d['rle_pond']
                d['active_aporte_rl'] = d.get('aporte_rle_fall', 0.0)
                d['active_rl_meta'] = d['meta_rle']
                d['active_mtbf_flota'] = d['mtbf_flota_efec']
                d['active_mtbf_sf'] = d['mtbf_sf_efec']
                d['active_mtbf'] = d['mtbf_flota_efec']
                d['active_pct_dias'] = d.get('pct_dias_rle_falla', 0.0)
            else:
                d['active_rl_op'] = d['rl_op']
                d['active_rl_fall'] = d['rl_fall']
                d['active_rl_pond'] = d['rl_pond']
                d['active_aporte_rl'] = d.get('aporte_rl_fall', 0.0)
                d['active_rl_meta'] = d['meta_rl']
                d['active_mtbf_flota'] = d['mtbf_flota']
                d['active_mtbf_sf'] = d['mtbf_sf']
                d['active_mtbf'] = d['mtbf_flota']
                d['active_pct_dias'] = d.get('pct_dias_falla', 0.0)

        items_rl = [d for d in items_rl if (d.get('active_rl_op', 0) > 0 or d.get('active_rl_fall', 0) > 0 or d.get('active_mtbf_flota', 0) > 0 or d.get('active_mtbf_sf', 0) > 0)]
        items_rl.sort(key=lambda x: (x['pozos_op'], x['active_rl_op']), reverse=True)

        if items_rl:
            display_items = items_rl[:35] if (len(items_rl) > 35 and agrupacion_rl == "Campo") else items_rl
            names = [d['nombre'] for d in display_items]
            y_op = [d['active_rl_op'] for d in display_items]
            y_fall = [d['active_rl_fall'] for d in display_items]
            y_mtbf_sf = [d['active_mtbf_sf'] for d in display_items]
            y_mtbf_flota = [d['active_mtbf_flota'] for d in display_items]

            hover_op_texts = []
            hover_fall_texts = []
            hover_mtbf_sf_texts = []
            hover_mtbf_flota_texts = []
            text_op = []
            text_fall = []
            text_mtbf_sf = []
            text_mtbf_flota = []

            for d in display_items:
                prov_op_html = ""
                if d.get('desglose_op') and agrupacion_rl != "Proveedor":
                    prov_op_html = "<br><b>• Desglose por Proveedor:</b><br>" + "<br>".join(
                        [f"&nbsp;&nbsp;▫ <b>{p['prov']}</b>: {p['rle'] if opcion_rl_bloque == 'Run Life Efectivo' else p['rl']:.0f}d ({p['pozos']} pozos)" for p in d['desglose_op']]
                    )
                
                prov_fall_html = ""
                if d.get('desglose_fall') and agrupacion_rl != "Proveedor":
                    prov_fall_lines = []
                    for p in d['desglose_fall']:
                        val_d = p['rle'] if opcion_rl_bloque == 'Run Life Efectivo' else p['rl']
                        if p['fallas'] == p['pozos']:
                            prov_fall_lines.append(f"&nbsp;&nbsp;▫ <b>{p['prov']}</b>: {val_d:.0f}d ({p['fallas']} fallas)")
                        else:
                            prov_fall_lines.append(f"&nbsp;&nbsp;▫ <b>{p['prov']}</b>: {val_d:.0f}d ({p['fallas']} fallas en {p['pozos']} pozos)")
                    prov_fall_html = "<br><b>• Desglose por Proveedor:</b><br>" + "<br>".join(prov_fall_lines)

                hover_op_texts.append(
                    f"<b style='color:#137659;font-size:13px'>{d['nombre']}</b><br>"
                    f"<hr style='margin:3px 0;border-color:rgba(19,118,89,0.15)'>"
                    f"<b>🟢 POZOS OPERATIVOS ALS:</b><br>"
                    f"• N° Pozos Activos: <b>{d['pozos_op']} pozos</b><br>"
                    f"• Run Life Promedio: <b>{d['active_rl_op']:.1f} días</b><br>"
                    f"• Total Pozos en Grupo: <b>{d['total_pozos_unicos']} pozos</b> ({d['total_corridas']} corridas hist.)"
                    f"{prov_op_html}"
                )
                
                str_fall_hdr = f"• Total Fallas ALS: <b>{d['tot_fallas']} fallas</b>" if d['tot_fallas'] == d['pozos_fall_unicos'] else f"• Total Fallas ALS: <b>{d['tot_fallas']} fallas</b> (en <b>{d['pozos_fall_unicos']} pozos</b>)"
                tot_fall_ref = sum(x.get('tot_fallas', 0) for x in display_items)
                hover_fall_texts.append(
                    f"<b style='color:#c62828;font-size:13px'>{d['nombre']}</b><br>"
                    f"<hr style='margin:3px 0;border-color:rgba(198,40,40,0.15)'>"
                    f"<b>🔴 POZOS FALLADOS ALS:</b><br>"
                    f"{str_fall_hdr}<br>"
                    f"• Run Life a Falla: <b>{d['active_rl_fall']:.1f} días</b><br>"
                    f"• Peso en Fallas Globales: <b>{d.get('pct_fallas', 0.0):.1f}%</b> ({d['tot_fallas']}/{max(tot_fall_ref, 1)})<br>"
                    f"• Aporte Ponderado al RL: <b>{d.get('active_aporte_rl', 0.0):.1f} días</b>"
                    f"{prov_fall_html}"
                )
                hover_mtbf_sf_texts.append(
                    f"<b style='color:#c09c2e;font-size:13px'>{d['nombre']}</b><br>"
                    f"<hr style='margin:3px 0;border-color:rgba(192,156,46,0.15)'>"
                    f"<b>🟡 MTBF SOLO FALLAS (ALS):</b><br>"
                    f"• MTBF ({'Efectivo' if opcion_rl_bloque == 'Run Life Efectivo' else 'Estándar'}): <b>{d['active_mtbf_sf']:.1f} días</b><br>"
                    f"• Base: <b>{d['tot_fallas']} fallas reales</b> (INDICADOR_MTBF=1)<br>"
                    f"• Evalúa estrictamente la vida útil a la falla."
                )
                hover_mtbf_flota_texts.append(
                    f"<b style='color:#095139;font-size:13px'>{d['nombre']}</b><br>"
                    f"<hr style='margin:3px 0;border-color:rgba(9,81,57,0.15)'>"
                    f"<b>🌲 MTBF FLOTA TOTAL (ALS):</b><br>"
                    f"• MTBF ({'Efectivo' if opcion_rl_bloque == 'Run Life Efectivo' else 'Estándar'}): <b>{d['active_mtbf_flota']:.1f} días</b><br>"
                    f"• Base: <b>{d['total_corridas']} corridas terminadas</b> ({d['tot_fallas']} fallas + {d['total_corridas'] - d['tot_fallas']} retiros no fallados)<br>"
                    f"• Estándar SPE / ISO 14224 (con censuras R=1)."
                )
                text_op.append(f"{d['active_rl_op']:.0f}d ({d['pozos_op']} op)" if d['active_rl_op'] > 0 else "")
                text_fall.append(f"{d['active_rl_fall']:.0f}d ({d['tot_fallas']} fall)" if d['active_rl_fall'] > 0 else "")
                text_mtbf_sf.append(f"{d['active_mtbf_sf']:.0f}d (MTBF Fallas)" if d['active_mtbf_sf'] > 0 else "")
                text_mtbf_flota.append(f"{d['active_mtbf_flota']:.0f}d (MTBF Flota)" if d['active_mtbf_flota'] > 0 else "")

            chart_h_rl = 370 if len(names) <= 12 else max(370, min(500, len(names) * 16 + 190))

            fig_rl_bloque = go_fig.Figure()

            # Barra 1: Pozos Operativos
            fig_rl_bloque.add_trace(go_fig.Bar(
                x=names,
                y=y_op,
                name="🟢 Pozos Operativos (RL Actual)",
                marker=dict(
                    color=_G,
                    line=dict(color=_G2, width=1)
                ),
                text=text_op,
                textposition="outside",
                textfont=dict(size=9, color=_G, family="Inter, sans-serif"),
                hovertext=hover_op_texts,
                hoverinfo="text",
                hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_G,
                                font=dict(size=10, family="Inter, sans-serif", color=_T)),
            ))

            # Barra 2: Pozos Fallados
            fig_rl_bloque.add_trace(go_fig.Bar(
                x=names,
                y=y_fall,
                name="🔴 Pozos Fallados ALS (RL a la Falla)",
                marker=dict(
                    color=_R,
                    line=dict(color="#8e0000", width=1)
                ),
                text=text_fall,
                textposition="outside",
                textfont=dict(size=9, color=_R, family="Inter, sans-serif"),
                hovertext=hover_fall_texts,
                hoverinfo="text",
                hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_R,
                                font=dict(size=10, family="Inter, sans-serif", color=_T)),
            ))

            # Barra 3: MTBF Solo Fallas
            nombre_mtbf_sf = "🟡 MTBF Solo Fallas" if opcion_rl_bloque != "Run Life Efectivo" else "🟡 MTBF Efectivo Solo Fallas"
            fig_rl_bloque.add_trace(go_fig.Bar(
                x=names,
                y=y_mtbf_sf,
                name=nombre_mtbf_sf,
                marker=dict(
                    color=_Y,
                    line=dict(color="#A06E22", width=1)
                ),
                text=text_mtbf_sf,
                textposition="outside",
                textfont=dict(size=9, color=_Y, family="Inter, sans-serif"),
                hovertext=hover_mtbf_sf_texts,
                hoverinfo="text",
                hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_Y,
                                font=dict(size=10, family="Inter, sans-serif", color=_T)),
            ))

            # Barra 4: MTBF Flota Total
            nombre_mtbf_flota = "🌲 MTBF Flota Total (Censuras R=1)" if opcion_rl_bloque != "Run Life Efectivo" else "🌲 MTBF Efectivo Flota Total"
            fig_rl_bloque.add_trace(go_fig.Bar(
                x=names,
                y=y_mtbf_flota,
                name=nombre_mtbf_flota,
                marker=dict(
                    color=_G2,
                    line=dict(color="#102511", width=1)
                ),
                text=text_mtbf_flota,
                textposition="outside",
                textfont=dict(size=9, color=_G2, family="Inter, sans-serif"),
                hovertext=hover_mtbf_flota_texts,
                hoverinfo="text",
                hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_G2,
                                font=dict(size=10, family="Inter, sans-serif", color=_T)),
            ))

            # Línea de Meta (1500 días)
            fig_rl_bloque.add_hline(
                y=1500,
                line_dash="dash",
                line_color=_R,
                line_width=1.8,
                annotation_text="Meta 1500d (Garantía)",
                annotation_position="top left",
                annotation_font=dict(size=9.5, color=_R, family="Inter, sans-serif", weight="bold")
            )

            max_y = max(
                max(y_op) if y_op else 0,
                max(y_fall) if y_fall else 0,
                max(y_mtbf_sf) if y_mtbf_sf else 0,
                max(y_mtbf_flota) if y_mtbf_flota else 0,
                1500
            )

            fig_rl_bloque.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", color=_T, size=10),
                margin=dict(l=30, r=10, t=50, b=55),
                barmode="group",
                xaxis=dict(title="", showgrid=False, showline=True, linecolor=_BR,
                           tickfont=dict(size=9.5, color=_T, family="Inter, sans-serif"),
                           tickangle=-35 if len(names) > 8 else 0),
                yaxis=dict(title=f"{opcion_rl_bloque} / MTBF (días)", range=[0, max_y * 1.35] if max_y > 0 else [0, 1000],
                            showgrid=True, gridcolor="rgba(46,125,70,0.07)", gridwidth=1,
                            showline=False,
                            tickfont=dict(size=8.5, color=_T2, family="Inter, sans-serif"),
                            ticksuffix="d"),
                bargap=0.25,
                bargroupgap=0.06,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.03,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=9.5, family="Inter, sans-serif", color=_T),
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor=_BR,
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


@_fragment
def _render_seccion_campana_gauss(df_fallas_als_all, df_bloque_raw, fecha_eval_norm_b, fecha_eval_dt_b):
    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='background:linear-gradient(90deg, rgba(19,118,89,0.08) 0%, rgba(192,156,46,0.06) 100%); padding:12px 16px; border-radius:12px; border-left:4px solid #137659; margin-bottom:12px;'>
            <div style='display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;'>
                <div>
                    <h6 style='color:#137659; font-family:Inter, sans-serif; font-weight:800; letter-spacing:0.8px; text-transform:uppercase; font-size:0.88rem; margin:0;'>
                        🔔 CAMPANA DE GAUSS / DISTRIBUCIÓN DE FALLAS ALS
                    </h6>
                    <span style='font-size:0.75rem; color:#5b5c55; font-family:Inter, sans-serif;'>
                        Distribución de frecuencia y ajuste estadístico normal (Campana de Gauss) de los pozos fallados ALS a {fecha_eval_dt_b.strftime('%Y-%m-%d')}
                    </span>
                </div>
                <div style='background:#ffffff; padding:4px 12px; border-radius:20px; border:1px solid rgba(19,118,89,0.25); font-family:Inter, sans-serif; font-size:0.75rem; font-weight:700; color:#137659;'>
                    Total Global Fallas ALS: <b>{len(df_fallas_als_all)} eventos</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_cg_dim, col_cg_elem, col_cg_metric, col_cg_bin = st.columns([1.1, 1.3, 1.1, 0.9])
    
    has_modelo = any(any(k in str(c).upper() for k in ['MODELO DE BOMBA', 'MODELO DE BOMABA', 'MODELO BOMBA', 'MODELO']) for c in df_fallas_als_all.columns)
    dim_options = ["Global (Todos)", "Campo", "Bloque", "Proveedor", "Sistema ALS"]
    if has_modelo:
        dim_options.append("Modelo de Bomba")

    with col_cg_dim:
        cg_agrupacion = st.selectbox(
            "Filtrar por dimensión:",
            options=dim_options,
            index=1 if 'CAMPO' in df_fallas_als_all.columns else 0,
            key="cg_dim_selector"
        )

    with col_cg_elem:
        col_modelo_detected = next((c for c in df_fallas_als_all.columns if any(k in str(c).upper() for k in ['MODELO DE BOMBA', 'MODELO DE BOMABA', 'MODELO BOMBA', 'MODELO'])), 'MODELO DE BOMBA')
        col_map = {
            "Campo": 'CAMPO',
            "Bloque": 'BLOQUE',
            "Proveedor": 'PROVEEDOR',
            "Sistema ALS": 'ALS' if 'ALS' in df_fallas_als_all.columns else 'SISTEMA ALS',
            "Modelo de Bomba": col_modelo_detected
        }
        if cg_agrupacion == "Global (Todos)":
            cg_selected_val = "TODOS"
            st.selectbox("Elemento:", options=[f"Global ({len(df_fallas_als_all)} fallas)"], disabled=True, key="cg_elem_dis")
        else:
            dim_col = col_map.get(cg_agrupacion, 'CAMPO')
            if dim_col in df_fallas_als_all.columns:
                counts_by_item = df_fallas_als_all[dim_col].dropna().astype(str).str.strip().value_counts()
                counts_by_item = counts_by_item[counts_by_item.index != '']
                elem_options = ["TODOS"] + [f"{k} ({v} fallas)" for k, v in counts_by_item.items()]
                elem_raw_names = ["TODOS"] + list(counts_by_item.index)
                
                cg_selected_label = st.selectbox(
                    f"Seleccionar {cg_agrupacion}:",
                    options=elem_options,
                    index=0,
                    key=f"cg_elem_select_{cg_agrupacion}"
                )
                idx_sel = elem_options.index(cg_selected_label) if cg_selected_label in elem_options else 0
                cg_selected_val = elem_raw_names[idx_sel]
            else:
                cg_selected_val = "TODOS"
                st.selectbox("Elemento:", options=["TODOS"], disabled=True, key="cg_elem_none")

    with col_cg_metric:
        cg_metric = st.radio(
            "Métrica Run Life:",
            options=["Run Life (Días)", "Run Life Efectivo"],
            index=0,
            horizontal=True,
            key="cg_metric_selector"
        )

    with col_cg_bin:
        cg_bin_choice = st.selectbox(
            "Ancho de Bin:",
            options=["Auto", "50 días", "100 días", "150 días", "200 días"],
            index=2,
            key="cg_bin_choice"
        )

    # Filtrar el DataFrame según la selección
    if cg_agrupacion != "Global (Todos)" and cg_selected_val != "TODOS":
        dim_col = col_map.get(cg_agrupacion, 'CAMPO')
        df_cg_subset = df_fallas_als_all[df_fallas_als_all[dim_col].astype(str).str.strip() == cg_selected_val].copy()
        df_group_all_runs = df_bloque_raw[df_bloque_raw[dim_col].astype(str).str.strip() == cg_selected_val].copy() if dim_col in df_bloque_raw.columns else df_bloque_raw.copy()
        titulo_entidad = f"{cg_selected_val.upper()} ({cg_agrupacion})"
    else:
        df_cg_subset = df_fallas_als_all.copy()
        df_group_all_runs = df_bloque_raw.copy()
        titulo_entidad = "GLOBAL (TODOS LOS CAMPOS)"

    col_life_cg = 'RLE_DIAS' if cg_metric == "Run Life Efectivo" else 'RL_DIAS'
    vals_cg = df_cg_subset[col_life_cg].dropna().values
    n_cg = len(vals_cg)

    if n_cg > 0:
        mu_cg = float(np.mean(vals_cg))
        med_cg = float(np.median(vals_cg))
        sigma_cg = float(np.std(vals_cg, ddof=1)) if n_cg > 1 else 0.0
        cv_cg = (sigma_cg / mu_cg * 100.0) if mu_cg > 0 else 0.0
        min_cg = float(np.min(vals_cg))
        max_cg = float(np.max(vals_cg))
        
        fallas_inf_cnt = int(np.sum(vals_cg < 365))
        pct_inf = (fallas_inf_cnt / n_cg * 100.0)
        
        col_mtbf_calc = 'RUN_LIFE_EFECTIVO' if cg_metric == "Run Life Efectivo" else 'RUN LIFE'
        try:
            mtbf_solo_fallas, step_df_solo_fallas = calcular_mtbf(df_cg_subset, fecha_eval_norm_b, col_life=col_mtbf_calc)
        except:
            mtbf_solo_fallas, step_df_solo_fallas = mu_cg, pd.DataFrame()

        try:
            mtbf_flota, step_df_flota = calcular_mtbf(df_group_all_runs, fecha_eval_norm_b, col_life=col_mtbf_calc)
        except:
            mtbf_flota, step_df_flota = mtbf_solo_fallas, pd.DataFrame()

        # KPI Cards de Estadísticas (6 Métricas Clave)
        kpi_cg1, kpi_cg2, kpi_cg3, kpi_cg4, kpi_cg5, kpi_cg6 = st.columns(6)
        with kpi_cg1:
            st.markdown(f"""
            <div class="if-semaforo" style="border-top:3px solid #c62828; padding:10px 8px;">
                <div class="if-sem-lbl">TOTAL FALLAS ALS</div>
                <div class="if-sem-val" style="color:#c62828; font-size:1.6rem;">{n_cg}</div>
                <div class="if-sem-sub">{titulo_entidad}</div>
            </div>""", unsafe_allow_html=True)
        with kpi_cg2:
            st.markdown(f"""
            <div class="if-semaforo" style="border-top:3px solid #137659; padding:10px 8px;">
                <div class="if-sem-lbl">MEDIA (μ) RUN LIFE</div>
                <div class="if-sem-val" style="color:#137659; font-size:1.6rem;">{mu_cg:.0f}<span style="font-size:0.8rem;">d</span></div>
                <div class="if-sem-sub">Promedio Aritmético</div>
            </div>""", unsafe_allow_html=True)
        with kpi_cg3:
            st.markdown(f"""
            <div class="if-semaforo" style="border-top:3px solid #5b5c55; padding:10px 8px;">
                <div class="if-sem-lbl">MEDIANA (P50)</div>
                <div class="if-sem-val" style="color:#5b5c55; font-size:1.6rem;">{med_cg:.0f}<span style="font-size:0.8rem;">d</span></div>
                <div class="if-sem-sub">50% falló antes de este día</div>
            </div>""", unsafe_allow_html=True)
        with kpi_cg4:
            st.markdown(f"""
            <div class="if-semaforo" style="border-top:3px solid #c09c2e; padding:10px 8px;">
                <div class="if-sem-lbl">MTBF SOLO FALLAS</div>
                <div class="if-sem-val" style="color:#c09c2e; font-size:1.6rem;">{mtbf_solo_fallas:.0f}<span style="font-size:0.8rem;">d</span></div>
                <div class="if-sem-sub">Exclusivo {n_cg} Fallas</div>
            </div>""", unsafe_allow_html=True)
        with kpi_cg5:
            st.markdown(f"""
            <div class="if-semaforo" style="border-top:3px solid #095139; padding:10px 8px;">
                <div class="if-sem-lbl">MTBF FLOTA TOTAL</div>
                <div class="if-sem-val" style="color:#095139; font-size:1.6rem;">{mtbf_flota:.0f}<span style="font-size:0.8rem;">d</span></div>
                <div class="if-sem-sub">Actuarial con Censura</div>
            </div>""", unsafe_allow_html=True)
        with kpi_cg6:
            st.markdown(f"""
            <div class="if-semaforo" style="border-top:3px solid #c62828; padding:10px 8px;">
                <div class="if-sem-lbl">FALLAS &lt; 365d</div>
                <div class="if-sem-val" style="color:#c62828; font-size:1.6rem;">{pct_inf:.1f}<span style="font-size:0.8rem;">%</span></div>
                <div class="if-sem-sub">{fallas_inf_cnt} fallas prematuras</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        # Configurar el ancho de bins
        if cg_bin_choice == "50 días":
            bin_size = 50
        elif cg_bin_choice == "100 días":
            bin_size = 100
        elif cg_bin_choice == "150 días":
            bin_size = 150
        elif cg_bin_choice == "200 días":
            bin_size = 200
        else:
            iqr = np.percentile(vals_cg, 75) - np.percentile(vals_cg, 25)
            if iqr > 0 and n_cg > 1:
                h = 2 * iqr * (n_cg ** (-1/3))
                bin_size = max(50, int(round(h / 50.0) * 50))
            else:
                bin_size = 100

        max_limit_x = int(np.ceil(max_cg / bin_size) * bin_size) if max_cg > 0 else 1000
        bins = np.arange(0, max_limit_x + bin_size + 1, bin_size)
        counts, bin_edges = np.histogram(vals_cg, bins=bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

        fig_cg = go_fig.Figure()

        # 1. Barras del Histograma coloreadas por etapa de vida (Paleta Corporativa Parex)
        bar_colors = []
        hover_texts = []
        for i_b in range(len(counts)):
            b_start = bin_edges[i_b]
            b_end = bin_edges[i_b + 1]
            c_val = counts[i_b]
            pct_bin = (c_val / n_cg * 100.0) if n_cg > 0 else 0.0
            
            if b_end <= 365:
                color_bar = _R
                etapa = "Fallas Infantiles (&lt; 365 días)"
            elif b_end <= 1000:
                color_bar = _Y
                etapa = "Vida Media Inicial (365 - 1000 días)"
            elif b_end <= 1500:
                color_bar = _G
                etapa = "Vida Madura (1000 - 1500 días)"
            else:
                color_bar = _G2
                etapa = "Alta Durabilidad (&gt; 1500 días)"
                
            bar_colors.append(color_bar)
            hover_texts.append(
                f"<b>Rango:</b> {b_start:.0f} - {b_end:.0f} días<br>"
                f"<b>Fallas ALS:</b> {c_val} pozos ({pct_bin:.1f}%)<br>"
                f"<b>Etapa:</b> {etapa}"
            )

        fig_cg.add_trace(go_fig.Bar(
            x=bin_centers,
            y=counts,
            width=bin_size * 0.88,
            marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.8)", width=1.5)),
            name="Fallas Observadas",
            hovertext=hover_texts,
            hoverinfo="text",
            hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_G,
                            font=dict(size=11, family="Inter, sans-serif", color=_T)),
        ))

        # 2. Curva Real de Frecuencia Observada (KDE) - Verde Parex
        if n_cg > 1 and sigma_cg > 0:
            bw_kde = max(1.06 * sigma_cg * (n_cg ** -0.2), 60.0)
            x_kde = np.linspace(0, max_limit_x, 300)
            diff_kde = (x_kde[:, None] - vals_cg[None, :]) / bw_kde
            dens_kde = np.sum(np.exp(-0.5 * diff_kde**2), axis=1) / (n_cg * bw_kde * np.sqrt(2 * np.pi))
            y_kde = dens_kde * n_cg * bin_size

            fig_cg.add_trace(go_fig.Scatter(
                x=x_kde,
                y=y_kde,
                mode='lines',
                name="Curva Real Observada (KDE)",
                line=dict(color=_G, width=3.5, shape="spline"),
                hoverinfo="skip"
            ))

        # 3. Campana de Gauss Teórica (Ajuste Normal Simétrico) - Dorado Parex
        y_curve = np.array([])
        if sigma_cg > 0:
            x_curve = np.linspace(0, max_limit_x, 300)
            pdf_values = (1.0 / (sigma_cg * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_curve - mu_cg) / sigma_cg) ** 2)
            y_curve = pdf_values * n_cg * bin_size

            fig_cg.add_trace(go_fig.Scatter(
                x=x_curve,
                y=y_curve,
                mode='lines',
                name=f"Campana de Gauss Teórica [N({mu_cg:.0f}d, ±{sigma_cg:.0f}d)]",
                line=dict(color=_Y, width=2.5, dash='dash'),
                hoverinfo="skip"
            ))

        # 4. Líneas verticales de referencia en armonía Parex
        fig_cg.add_vline(
            x=mu_cg,
            line_dash="dash",
            line_color=_R,
            line_width=2,
            annotation_text=f"Media μ: {mu_cg:.0f}d",
            annotation_position="top left",
            annotation_font=dict(size=10, color=_R, family="Inter, sans-serif")
        )

        fig_cg.add_vline(
            x=med_cg,
            line_dash="dot",
            line_color="#5C6B73",
            line_width=2,
            annotation_text=f"Mediana P50: {med_cg:.0f}d",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#5C6B73", family="Inter, sans-serif")
        )

        if mtbf_solo_fallas and mtbf_solo_fallas > 0:
            fig_cg.add_vline(
                x=mtbf_solo_fallas,
                line_dash="dashdot",
                line_color=_Y,
                line_width=2,
                annotation_text=f"MTBF Solo Fallas: {mtbf_solo_fallas:.0f}d",
                annotation_position="bottom right",
                annotation_font=dict(size=10, color=_Y, family="Inter, sans-serif")
            )

        if mtbf_flota and mtbf_flota > 0 and abs(mtbf_flota - mtbf_solo_fallas) > 50:
            fig_cg.add_vline(
                x=mtbf_flota,
                line_dash="longdash",
                line_color=_G2,
                line_width=2,
                annotation_text=f"MTBF Flota: {mtbf_flota:.0f}d",
                annotation_position="top right",
                annotation_font=dict(size=10, color=_G2, family="Inter, sans-serif")
            )

        fig_cg.add_vline(
            x=1500,
            line_dash="dash",
            line_color=_G,
            line_width=1.5,
            annotation_text="Garantía 1500d",
            annotation_position="bottom left",
            annotation_font=dict(size=9, color=_G, family="Inter, sans-serif")
        )

        max_curve_val = float(np.max(y_curve)) if len(y_curve) > 0 else 0.0
        max_counts_val = float(np.max(counts)) if len(counts) > 0 else 0.0
        max_hist_y = max(max_counts_val, max_curve_val)

        fig_cg.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color=_T, size=10),
            margin=dict(l=30, r=15, t=50, b=45),
            xaxis=dict(
                title=f"{cg_metric} a la Falla (días)",
                range=[0, max_limit_x + bin_size],
                showgrid=True,
                gridcolor="rgba(46,125,70,0.06)",
                showline=True,
                linecolor=_BR,
                tickfont=dict(size=9, color=_T, family="Inter, sans-serif"),
                ticksuffix="d"
            ),
            yaxis=dict(
                title="Número de Fallas ALS",
                range=[0, max_hist_y * 1.25 if max_hist_y > 0 else 10],
                showgrid=True,
                gridcolor="rgba(46,125,70,0.07)",
                gridwidth=1,
                showline=False,
                tickfont=dict(size=8.5, color=_T2, family="Inter, sans-serif")
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=9.5, family="Inter, sans-serif", color=_T),
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor=_BR,
                borderwidth=1
            ),
            height=430
        )

        plotly_config_cg = {
            "displayModeBar": True,
            "displaylogo": False,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"campana_gauss_fallas_{titulo_entidad.lower()}",
                "height": 550,
                "width": 1100,
                "scale": 3
            }
        }

        # Sub-pestañas para visualizaciones avanzadas
        vista_sub_cg = st.radio(
            "Seleccionar Vista Analítica:",
            options=[
                "🔔 1. Campana de Gauss / Histograma",
                "📈 2. Curva de Supervivencia R(t) (Área = MTBF)",
                "⚖️ 3. Demostración para Gerencia (Media vs MTBF)"
            ],
            index=0,
            horizontal=True,
            key="cg_sub_vista_selector"
        )

        if vista_sub_cg == "🔔 1. Campana de Gauss / Histograma":
            st.plotly_chart(fig_cg, use_container_width=True, config=plotly_config_cg)
            
            st.markdown(f"""
            <div style='background:rgba(217,119,6,0.07); padding:12px 16px; border-radius:10px; border-left:4px solid #d97706; font-size:0.8rem; color:#1f221e; margin-top:8px;'>
                💡 <b>¿Por qué la Campana de Gauss Teórica (Línea Dorada Punteada) no coincide con la cúspide de las barras?</b><br>
                • <b>Pico Real al Inicio (Mortalidad Infantil):</b> La mayor cantidad de fallas ocurre en los primeros <b>0 a 300 días</b> ({fallas_inf_cnt} fallas &lt; 365d, {pct_inf:.1f}%), por eso las barras más altas están al extremo izquierdo (la <b style='color:#137659;'>Curva Verde Real (KDE)</b> sí abraza este pico).<br>
                • <b>Efecto de la Media (μ = {mu_cg:.0f}d):</b> La media aritmética suma todos los días y se desplaza hacia la derecha por los pozos longevos (hasta {max_cg:.0f}d). Como la campana de Gauss teórica es 100% simétrica, su cúspide se dibuja forzosamente en el valor de la Media ({mu_cg:.0f}d).<br>
                • <b>Conclusión Técnica para Gerencia:</b> Esto demuestra empíricamente que <b>las fallas de fondo ALS no son normales ni gaussianas</b>, sino asimétricas con mortalidad infantil, justificando el uso de integrales de confiabilidad actuarial en vez del promedio simple.
            </div>
            """, unsafe_allow_html=True)

        elif vista_sub_cg == "📈 2. Curva de Supervivencia R(t) (Área = MTBF)":
            try:
                fig_surv = go_fig.Figure()

                # 1. Curva Solo Fallas (Área = mtbf_solo_fallas) - Dorado Parex
                if not step_df_solo_fallas.empty and 'R(Ti)' in step_df_solo_fallas.columns:
                    col_life_s = [c for c in step_df_solo_fallas.columns if c not in ['ITEM', 'R(ti/Ti-1)', 'R(Ti)', 'R(Ti)*dt']][0]
                    xs_sf = [0.0] + [float(v) for v in step_df_solo_fallas[col_life_s].dropna()]
                    ys_sf = [100.0] + [float(v) * 100.0 for v in step_df_solo_fallas['R(Ti)'].dropna()]

                    hover_sf_texts = [f"<b>Inicio (t=0):</b> 100.0% Supervivencia"] + [
                        f"<b>Falla {row['ITEM']} ({float(row[col_life_s]):.0f}d):</b><br>"
                        f"• Supervivencia R(t): <b>{float(row['R(Ti)'])*100:.1f}%</b><br>"
                        f"• Aporte MTBF Solo Fallas: <b>+{float(row['R(Ti)*dt']):.1f}d</b>"
                        for _, row in step_df_solo_fallas.iterrows()
                    ]

                    fig_surv.add_trace(go_fig.Scatter(
                        x=xs_sf,
                        y=ys_sf,
                        mode='lines',
                        name=f"Curva R(t) Solo Fallas [Área = {mtbf_solo_fallas:.0f}d]",
                        line=dict(color="#c09c2e", width=3.5, shape="hv"),
                        fill='tozeroy',
                        fillcolor='rgba(192, 156, 46, 0.15)',
                        hovertext=hover_sf_texts,
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_Y,
                                        font=dict(size=10.5, family="Inter, sans-serif", color=_T)),
                    ))

                # 2. Curva Flota Completa con Censuras (Área = mtbf_flota) - Verde Parex
                if not step_df_flota.empty and 'R(Ti)' in step_df_flota.columns:
                    col_life_fl = [c for c in step_df_flota.columns if c not in ['ITEM', 'R(ti/Ti-1)', 'R(Ti)', 'R(Ti)*dt']][0]
                    xs_fl = [0.0] + [float(v) for v in step_df_flota[col_life_fl].dropna()]
                    ys_fl = [100.0] + [float(v) * 100.0 for v in step_df_flota['R(Ti)'].dropna()]

                    hover_fl_texts = [f"<b>Inicio Flota (t=0):</b> 100.0% Supervivencia"] + [
                        f"<b>Evento {row['ITEM']} ({float(row[col_life_fl]):.0f}d):</b><br>"
                        f"• Supervivencia Flota: <b>{float(row['R(Ti)'])*100:.1f}%</b><br>"
                        f"• Aporte MTBF Flota: <b>+{float(row['R(Ti)*dt']):.1f}d</b>"
                        for _, row in step_df_flota.iterrows()
                    ]

                    fig_surv.add_trace(go_fig.Scatter(
                        x=xs_fl,
                        y=ys_fl,
                        mode='lines',
                        name=f"Curva R(t) Flota Completa con Censura [Área = {mtbf_flota:.0f}d]",
                        line=dict(color=_G, width=3, dash='solid', shape="hv"),
                        hovertext=hover_fl_texts,
                        hoverinfo="text",
                        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor=_G,
                                        font=dict(size=10.5, family="Inter, sans-serif", color=_T)),
                    ))

                fig_surv.add_vline(
                    x=mtbf_solo_fallas,
                    line_dash="dash",
                    line_color=_Y,
                    line_width=2.5,
                    annotation_text=f"MTBF Solo Fallas: {mtbf_solo_fallas:.0f}d",
                    annotation_position="top right",
                    annotation_font=dict(size=10.5, color=_Y, family="Inter, sans-serif")
                )

                if abs(mtbf_flota - mtbf_solo_fallas) > 50:
                    fig_surv.add_vline(
                        x=mtbf_flota,
                        line_dash="longdash",
                        line_color=_G2,
                        line_width=2,
                        annotation_text=f"MTBF Flota: {mtbf_flota:.0f}d",
                        annotation_position="bottom right",
                        annotation_font=dict(size=10, color=_G2, family="Inter, sans-serif")
                    )

                fig_surv.add_vline(
                    x=mu_cg,
                    line_dash="dot",
                    line_color=_R,
                    line_width=2,
                    annotation_text=f"Media Simple: {mu_cg:.0f}d",
                    annotation_position="top left",
                    annotation_font=dict(size=10, color=_R, family="Inter, sans-serif")
                )

                fig_surv.add_vline(
                    x=med_cg,
                    line_dash="dashdot",
                    line_color="#5C6B73",
                    line_width=2,
                    annotation_text=f"Mediana: {med_cg:.0f}d",
                    annotation_position="bottom left",
                    annotation_font=dict(size=10, color="#5C6B73", family="Inter, sans-serif")
                )

                fig_surv.add_hline(
                    y=50,
                    line_dash="dot",
                    line_color=_T2,
                    line_width=1,
                    annotation_text="50% Supervivencia",
                    annotation_position="right",
                    annotation_font=dict(size=9, color=_T2, family="Inter, sans-serif")
                )

                fig_surv.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, sans-serif", color=_T, size=10),
                    margin=dict(l=35, r=15, t=50, b=45),
                    xaxis=dict(
                        title=f"{cg_metric} a la Falla (días)",
                        range=[0, max(max_limit_x, 1600)],
                        showgrid=True,
                        gridcolor="rgba(46,125,70,0.06)",
                        showline=True,
                        linecolor=_BR,
                        tickfont=dict(size=9.5, color=_T, family="Inter, sans-serif"),
                        ticksuffix="d"
                    ),
                    yaxis=dict(
                        title="Probabilidad de Supervivencia R(t) (%)",
                        range=[0, 105],
                        showgrid=True,
                        gridcolor="rgba(46,125,70,0.07)",
                        gridwidth=1,
                        showline=False,
                        tickfont=dict(size=8.5, color=_T2, family="Inter, sans-serif"),
                        ticksuffix="%"
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=9.5, family="Inter, sans-serif", color=_T),
                        bgcolor="rgba(255,255,255,0.95)",
                        bordercolor=_BR,
                        borderwidth=1
                    ),
                    height=420
                )

                st.plotly_chart(fig_surv, use_container_width=True, config=plotly_config_cg)

                st.markdown(f"""
                <div style="{_CARD} padding:12px 16px; margin-top:8px; border-left:3px solid {_G}; font-size:0.8rem; color:{_T};">
                    💡 <b>Demostración Visual de la Integral y Censura Actuarial:</b><br>
                    • <b style='color:{_Y};'>Curva Dorada (MTBF Solo Fallas = {mtbf_solo_fallas:.1f}d):</b> Calcula el área bajo la curva considerando <b>únicamente los pozos que fallaron</b>.<br>
                    • <b style='color:{_G};'>Curva Verde (MTBF Flota Total = {mtbf_flota:.1f}d):</b> Integra los retiros programados sin falla (censuras R=1), reflejando la durabilidad real de la flota antes de cualquier intervención.
                </div>
                """, unsafe_allow_html=True)
            except Exception as e_surv:
                st.warning(f"No se pudo graficar la curva de supervivencia: {e_surv}")

        elif vista_sub_cg == "⚖️ 3. Demostración para Gerencia (Media vs MTBF)":
            st.markdown(f"""
            <div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:12px; margin-top:8px;'>
                <div style='background:#ffffff; border-radius:12px; padding:14px; border:1px solid rgba(198,40,40,0.25); border-top:4px solid #c62828; box-shadow:0 2px 6px rgba(0,0,0,0.03);'>
                    <div style='font-size:0.72rem; font-weight:800; color:#c62828; text-transform:uppercase;'>1. Promedio Simple de Fallas</div>
                    <div style='font-size:1.7rem; font-weight:900; color:#c62828; margin:4px 0;'>{mu_cg:.1f} <span style='font-size:0.85rem;'>días</span></div>
                    <p style='font-size:0.76rem; color:#5b5c55; line-height:1.4; margin:0;'>
                        • Suma de días dividida entre las {n_cg} fallas.<br>
                        • <b>Limitación:</b> Sesgado a la baja por las <b>{fallas_inf_cnt} fallas infantiles (< 365d, {pct_inf:.1f}%)</b>.
                    </p>
                </div>
                <div style='background:#ffffff; border-radius:12px; padding:14px; border:1px solid rgba(91,92,85,0.25); border-top:4px solid #5b5c55; box-shadow:0 2px 6px rgba(0,0,0,0.03);'>
                    <div style='font-size:0.72rem; font-weight:800; color:#5b5c55; text-transform:uppercase;'>2. Mediana de Fallas (P50)</div>
                    <div style='font-size:1.7rem; font-weight:900; color:#5b5c55; margin:4px 0;'>{med_cg:.1f} <span style='font-size:0.85rem;'>días</span></div>
                    <p style='font-size:0.76rem; color:#5b5c55; line-height:1.4; margin:0;'>
                        • Día exacto donde el <b>50% de las bombas falló</b>.<br>
                        • Robusto frente a valores extremos pero no modela la probabilidad acumulada.
                    </p>
                </div>
                <div style='background:#ffffff; border-radius:12px; padding:14px; border:1px solid rgba(192,156,46,0.25); border-top:4px solid #c09c2e; box-shadow:0 2px 6px rgba(0,0,0,0.03);'>
                    <div style='font-size:0.72rem; font-weight:800; color:#c09c2e; text-transform:uppercase;'>3. MTBF Solo Fallas (Integral)</div>
                    <div style='font-size:1.7rem; font-weight:900; color:#c09c2e; margin:4px 0;'>{mtbf_solo_fallas:.1f} <span style='font-size:0.85rem;'>días</span></div>
                    <p style='font-size:0.76rem; color:#5b5c55; line-height:1.4; margin:0;'>
                        • <b>Tiempo medio a la falla</b> de los equipos dañados.<br>
                        • Evalúa la integral excluyendo extracciones programadas sin falla.
                    </p>
                </div>
                <div style='background:#ffffff; border-radius:12px; padding:14px; border:1px solid rgba(9,81,57,0.25); border-top:4px solid #095139; box-shadow:0 2px 6px rgba(0,0,0,0.03);'>
                    <div style='font-size:0.72rem; font-weight:800; color:#095139; text-transform:uppercase;'>4. MTBF Flota Total (SPE / ISO)</div>
                    <div style='font-size:1.7rem; font-weight:900; color:#095139; margin:4px 0;'>{mtbf_flota:.1f} <span style='font-size:0.85rem;'>días</span></div>
                    <p style='font-size:0.76rem; color:#5b5c55; line-height:1.4; margin:0;'>
                        • <b>Estándar de Confiabilidad Global</b>.<br>
                        • Considera los días trabajados por equipos sacados sin fallar (censuras R=1).
                    </p>
                </div>
            </div>

            <div style='background:#ffffff; border:1px solid rgba(19,118,89,0.25); border-radius:12px; padding:14px; margin-top:12px;'>
                <div style='font-size:0.85rem; font-weight:800; color:#137659; margin-bottom:6px;'>📢 Resumen Ejecutivo para la Gerencia:</div>
                <div style='font-size:0.8rem; color:#1f221e; line-height:1.5;'>
                    <b>1. Para responder "¿Cuánto dura un equipo ALS cuando falla?":</b> El <b>MTBF de Solo Fallas es {mtbf_solo_fallas:.1f} días</b> (frente a un promedio simple de {mu_cg:.1f}d).<br>
                    <b>2. Para responder "¿Cuál es la confiabilidad y vida esperada de toda la flota?":</b> El <b>MTBF de Flota Completa es {mtbf_flota:.1f} días</b>, ya que reconoce que los pozos extraídos por razones operativas sin falla aportaron cientos de días de servicio continuo sin avería.
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander(f"📋 VER LISTADO DE LAS {n_cg} FALLAS ALS EN {titulo_entidad}", expanded=False):
            cols_deseadas = ['POZO', 'CAMPO', 'BLOQUE', 'PROVEEDOR', 'ALS', 'FECHA_RUN', 'FECHA_FALLA', 'RL_DIAS', 'RLE_DIAS']
            cols_existentes = [c for c in cols_deseadas if c in df_cg_subset.columns]
            df_list_cg = df_cg_subset[cols_existentes].copy()
            
            if 'FECHA_RUN' in df_list_cg.columns:
                df_list_cg['FECHA_RUN'] = pd.to_datetime(df_list_cg['FECHA_RUN']).dt.strftime('%Y-%m-%d')
            if 'FECHA_FALLA' in df_list_cg.columns:
                df_list_cg['FECHA_FALLA'] = pd.to_datetime(df_list_cg['FECHA_FALLA']).dt.strftime('%Y-%m-%d')
            if 'RL_DIAS' in df_list_cg.columns:
                df_list_cg = df_list_cg.sort_values(by='RL_DIAS', ascending=True).reset_index(drop=True)
                
            rename_dict = {
                'POZO': 'Pozo',
                'CAMPO': 'Campo',
                'BLOQUE': 'Bloque',
                'PROVEEDOR': 'Proveedor',
                'ALS': 'Sistema ALS',
                'FECHA_RUN': 'Fecha Run',
                'FECHA_FALLA': 'Fecha Falla',
                'RL_DIAS': 'Run Life (días)',
                'RLE_DIAS': 'Run Life Efectivo (días)'
            }
            df_list_cg.rename(columns=rename_dict, inplace=True)
            render_hud_table(df_list_cg, table_id="listado_fallas_als_gauss")


@_fragment
def _render_seccion_dispersion_modelo_bomba(df_bloque_raw, fecha_eval_norm_b, fecha_eval_dt_b):
    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="{_CARD} padding:14px 18px; margin-bottom:12px; border-left:4px solid {_G}; box-sizing:border-box;">
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                <div>
                    <h6 style="color:{_G2}; font-family:{_FS}; font-weight:800; letter-spacing:0.8px; text-transform:uppercase; font-size:0.85rem; margin:0;">
                        🎯 DISPERSIÓN DE FALLAS Y MTBF POR MODELO DE BOMBA (SOLO FALLAS ALS)
                    </h6>
                    <span style="font-size:0.75rem; color:{_T2}; font-family:{_FS};">
                        Puntos individuales de eventos de falla (dispersión) sobre la línea de MTBF actuarial por modelo de equipo a {fecha_eval_dt_b.strftime('%Y-%m-%d')}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df_bloque_raw.empty:
        st.info("Sin datos para analizar modelos de bomba.")
        return

    # Buscar columna de Modelo de Bomba
    col_modelo = next(
        (c for c in df_bloque_raw.columns if any(k in str(c).upper().strip() for k in ['MODELO DE BOMBA', 'MODELO DE BOMABA', 'MODELO_DE_BOMBA', 'MODELO BOMBA', 'TIPO DE BOMBA', 'MODELO'])),
        None
    )

    df_eval = df_bloque_raw.copy()

    def _clean_mod_str(val):
        if pd.isna(val) or str(val).strip().upper() in ('', 'NAN', 'NONE', 'NULL', 'NAT'):
            return ''
        s = re.sub(r'[\r\n"]+', ' ', str(val)).strip()
        for sep in [' - INTAKE', ' - INATKE', ' - MOTOR', ' CUERPOS DE BOMBA', ' - 56 ETAPAS']:
            if sep in s.upper():
                idx = s.upper().find(sep)
                s = s[:idx].strip()
        return s

    # Si la columna aún no está en el dataset actual (pendiente de subida del nuevo Excel), creamos una vista preliminar con el catálogo real del cliente
    if not col_modelo or col_modelo not in df_eval.columns:
        col_modelo = '_MODELO_PREVIEW'
        def _get_demo_model(row):
            als_v = str(row.get('ALS', 'ESP')).strip().upper()
            pozo_str = str(row.get('POZO', '0')) + str(row.get('RUN', '1'))
            pozo_seed = abs(hash(pozo_str))

            cat_pcp = [
                'P-100', 'P-155', 'P30', 'P-29', 'P-110', 'P-62', 'P-23', 'P4', 'P-200', 'P-18', 
                'P-47', 'P47', 'P-12', 'P100LS', 'PLS M X SXD LS HS', 'PLSMXSSDH6', 'SN3599', 
                'TE-4199', 'DN-1749', 'TE-3299', 'D2400N'
            ]
            cat_esp = [
                'TE-900', 'TE-5500', 'TE-2700', 'TD-6000', 'TE-3300', 'TD-1200', 'TA-900', 'TE-4200',
                'KC-15500', 'DN-1750', 'DN-1400', 'TE-1500', 'TD-1750', 'TE-7000', 'S8000N', 'S6000N',
                'TD-2200', 'TD-850', 'S8500N', 'SN8500', 'H15500N', 'GN-4000', '18H', 'TE-11000',
                'TD-1250', 'SN6000', 'DN1050', 'H28000N', 'SN3600', 'D2400N', 'ARCMPTE5500', 'SN8000',
                'GN5200', 'H21500N', 'S3600N', 'TD-3000', 'TE-330', 'NB(1100-1800)H', 'S2600N',
                'TA-2200', 'D1800N', 'NF(1300-2000)H', 'NH(1000-1600)H', 'NHV760', 'DN1800', 'TA-1200',
                'NH(1600-2300)H', 'TE5500', 'NH(2500-3100)H', 'NHV(790-1000)H', 'NHV380', 'NHV1200',
                'NH(4400-5000)H', 'NB(630-1000)H', 'TD-460', 'NP(3100-4400)H', 'D1400N', 'D1050N',
                'SN-2600', 'TA-2700', 'G4000N', 'FLEX-47', 'ESP-3600', 'ESP-7000', 'D460N', 'ESP9000',
                'NP(1900-2500)H', 'NP(4700-6300)H', 'FLEX17.5', 'S11000N', 'S4000N', 'D4300N',
                'NH(790-1000)H', 'NP(7900-10100)H', 'NJV7600', 'NJ9400', 'FLEX-80', 'FLEX8', 'TD-4300',
                'RCD4000NX', 'D725N', 'D1150N', 'NP(11300-15100)H', 'D1750N', 'NHV260', 'J12000R',
                'D4000NX', 'GN4000', 'NB(2000-3100)H', '5500', 'TE1500', 'J12000N', 'WH20000',
                'NP(4400-5700)H', 'NBV(250-500)H', 'NHV5300', '7000CP', 'ESPB538-3600', 'B538-1500',
                'ESPB538-5000', 'NLV1900', 'WH-20000', 'NLV1000SCMP', 'B400-1050CW', 'ESPB400-1050',
                'B400-2400CW5M', 'D800N', 'NH3000', 'FLEX-27', 'D1000NX', '538-7000', 'B538-3600',
                'NHV250', 'RCD1000NX', 'S2000N', 'WE1500', 'WD3000', 'WE-8500', 'WE-5500', 'WE-1500',
                'REDACONTINUUMPUMP', 'WE7000', 'WH-15000', 'WD1750', 'WG-4000', 'WG4000', 'E8000LS',
                'E1000', 'WE-2700', 'RCXLF', 'E2000', 'WE-1500R'
            ]
            cat_bm = [
                'BOMBA 30-250-RWBFR-24-3', '30-250-RXBAIP-32-3', 'BOMBA 30-200-RXBM-24-3',
                '30-250-RXBFR-34-3', '30-175-RHBM(AIP)-34-3', 'BOMBA 30-200-RXB(AIP)',
                '30-200-RXBM-34-5', 'BOMBA 30-250-RXBC-36-3', 'BOMBA 30-175-RHBF'
            ]
            cat_bh = [
                'STP - DIRECTA - 12N', 'STP - 9.3 #/ft N80 - 2.81 L', 'STP - DIRECTA - 11K',
                'STP - Bomba Jet Directa 2.81" 12K STP 33/13', 'STP - DIRECTA - 12K',
                'STP - Bomba Jet Directa 2.81" 12K STP JCE-19009', 'STP - Bomba Jet Directa - 11L',
                'STP - Bomba Jet Directa 3-1/2" x 2.81 + Closure valve - 12K',
                'STP - Bomba Jet Directa 2.81" 12K JCE-19009',
                'STP - Bomba Jet Directa 2,81" con extensión CMD + closure valve',
                'STP - Bomba Jet Directa 3-1/2" x 2.81 + Closure valve - 12N',
                'STP - JET CLAW CMD 2,81" - 12M', 'STP - JET CLAW CMD 2,81" - 12L',
                'STP - Bomba Sistema jet pack off 3 1/2" x 2,992"', 'STP - DIRECTA - 12M',
                'STP - Jet Pump - 12M', 'STP - Jet Pump - 12R', 'STP - JET CLAW 3 1/2X2.81" F.D.E. - 12L',
                'STP - PUMP JET CLAW® CONVENTIONAL 2-7/8" x 2,31" SEAL - 12K',
                'STP - PUMP JET CLAW® CONVENTIONAL 2-7/8" x 2,31" SEAL - 11J'
            ]
            cat_epcp = [
                'P-100', 'P-155', 'P-110', 'P-62', 'P-200', 'P-18', 'P-47', 'P100LS'
            ]

            if 'ESP' in als_v:
                return cat_esp[pozo_seed % len(cat_esp)]
            elif 'EPCP' in als_v:
                return cat_epcp[pozo_seed % len(cat_epcp)]
            elif 'PCP' in als_v:
                return cat_pcp[pozo_seed % len(cat_pcp)]
            elif 'BM' in als_v:
                return cat_bm[pozo_seed % len(cat_bm)]
            elif 'BH' in als_v:
                return cat_bh[pozo_seed % len(cat_bh)]
            else:
                return cat_esp[pozo_seed % len(cat_esp)]

        df_eval['_MODELO_PREVIEW'] = df_eval.apply(_get_demo_model, axis=1)
        
        st.markdown("""
        <div style='background:rgba(217,119,6,0.08); border-radius:10px; border-left:4px solid #d97706; padding:10px 14px; margin-bottom:12px; font-size:0.78rem; color:#1f221e;'>
            💡 <b>MODO VISTA PREVIA ACTIVO:</b> Como tu archivo actual aún no tiene la nueva columna, se muestran modelos de bomba clasificados según el catálogo ALS del cliente (ESP, PCP, BM, BH, EPCP). Tan pronto cargues tu nuevo Excel con la columna <b>'MODELO DE BOMBA'</b> o <b>'MODELO DE BOMABA'</b>, esta gráfica se vinculará directamente a tus datos reales.
        </div>
        """, unsafe_allow_html=True)
    else:
        df_eval[col_modelo] = df_eval[col_modelo].apply(_clean_mod_str)

    # Filtrar solo fallas ALS válidas (INDICADOR_MTBF == 1, fecha_falla <= fecha_eval)
    mask_fallas = (
        (df_eval['_RUN'] <= fecha_eval_norm_b) &
        (df_eval['_FALL'].notna()) &
        (df_eval['_FALL'] <= fecha_eval_norm_b) &
        (df_eval['INDICADOR_MTBF'] == 1) &
        (df_eval[col_modelo].notna()) &
        (df_eval[col_modelo].astype(str).str.strip() != '') &
        (df_eval[col_modelo].astype(str).str.upper().str.strip() != 'NAN')
    )
    df_fallas_als = df_eval[mask_fallas].copy()

    if df_fallas_als.empty:
        st.info("No se registraron eventos de falla ALS con modelo asignado para la fecha seleccionada.")
        return

    # Calcular Run Life a la Falla
    if 'RUN LIFE @ FALLA' in df_fallas_als.columns:
        df_fallas_als['RL_DIAS'] = pd.to_numeric(df_fallas_als['RUN LIFE @ FALLA'], errors='coerce')
    elif 'RUN LIFE' in df_fallas_als.columns:
        df_fallas_als['RL_DIAS'] = pd.to_numeric(df_fallas_als['RUN LIFE'], errors='coerce')
    else:
        df_fallas_als['RL_DIAS'] = (pd.to_datetime(df_fallas_als['_FALL']) - pd.to_datetime(df_fallas_als['_RUN'])).dt.days

    mask_bad_rl = df_fallas_als['RL_DIAS'].isna() | (df_fallas_als['RL_DIAS'] < 0)
    if mask_bad_rl.any():
        df_fallas_als.loc[mask_bad_rl, 'RL_DIAS'] = (
            pd.to_datetime(df_fallas_als.loc[mask_bad_rl, '_FALL']) - 
            pd.to_datetime(df_fallas_als.loc[mask_bad_rl, '_RUN'])
        ).dt.days

    df_fallas_als['MODELO_LIMPIO'] = df_fallas_als[col_modelo].astype(str).str.strip().str.upper()

    # Controles superiores: 1. Sistema ALS, 2. Cantidad de Modelos, 3. Ordenamiento
    col_c1, col_c2, col_c3 = st.columns([1.2, 1.2, 1.2])
    with col_c1:
        als_unique = ["TODOS"]
        if 'ALS' in df_fallas_als.columns:
            als_unique += sorted([str(x).strip() for x in df_fallas_als['ALS'].dropna().unique() if str(x).strip() and str(x).strip().upper() != 'NAN'])
        als_sel = st.selectbox("Filtrar Sistema ALS:", options=als_unique, index=1 if "ESP" in als_unique else 0, key="tab_ind_mb_als_select")

    # Filtrar primero por el sistema ALS seleccionado para no mezclar tecnologías
    if als_sel != "TODOS" and 'ALS' in df_fallas_als.columns:
        df_fallas_als_filtered = df_fallas_als[df_fallas_als['ALS'].astype(str).str.strip() == als_sel].copy()
    else:
        df_fallas_als_filtered = df_fallas_als.copy()

    # Calcular MTBF Global a Falla para el sistema ALS seleccionado
    mtbf_global_sf, _ = calcular_mtbf(df_fallas_als_filtered, fecha_eval_norm_b) if not df_fallas_als_filtered.empty else (0.0, None)

    with col_c2:
        top_n_opt = st.selectbox(
            "Modelos a Mostrar:",
            options=["Top 10 Modelos Más Utilizados", "Top 15 Modelos Más Utilizados", "Top 20 Modelos Más Utilizados", "Top 30 Modelos Más Utilizados", "Modelos con ≥ 2 Fallas", "Todos los Modelos"],
            index=1,
            key="tab_ind_mb_top_n_select"
        )
    with col_c3:
        sort_opt = st.selectbox(
            "Ordenar Eje X por:",
            options=["Frecuencia de Fallas (Mayor a Menor)", "MTBF (Mayor a Menor)", "MTBF (Menor a Mayor)", "Nombre Alfabético"],
            index=0,
            key="tab_ind_mb_sort_select"
        )

    # Contar ocurrencias por modelo dentro del sistema filtrado
    counts = df_fallas_als_filtered['MODELO_LIMPIO'].value_counts()
    
    if "Top 10" in top_n_opt:
        selected_models = list(counts.head(10).index)
    elif "Top 15" in top_n_opt:
        selected_models = list(counts.head(15).index)
    elif "Top 20" in top_n_opt:
        selected_models = list(counts.head(20).index)
    elif "Top 30" in top_n_opt:
        selected_models = list(counts.head(30).index)
    elif "≥ 2 Fallas" in top_n_opt:
        selected_models = list(counts[counts >= 2].index)
    else:
        selected_models = list(counts.index)

    df_filtered_models = df_fallas_als_filtered[df_fallas_als_filtered['MODELO_LIMPIO'].isin(selected_models)].copy()

    if df_filtered_models.empty:
        st.info(f"Sin eventos de falla para el sistema ALS '{als_sel}'.")
        return

    # Calcular MTBF Solo Fallas y estadísticas por cada modelo
    model_stats = []
    for mod in selected_models:
        sub_m = df_filtered_models[df_filtered_models['MODELO_LIMPIO'] == mod]
        if sub_m.empty:
            continue
        mtbf_val, _ = calcular_mtbf(sub_m, fecha_eval_norm_b)
        rls = sub_m['RL_DIAS'].dropna().values
        n_ev = len(rls)
        mean_rl = float(np.mean(rls)) if n_ev > 0 else 0.0
        med_rl = float(np.median(rls)) if n_ev > 0 else 0.0
        min_rl = float(np.min(rls)) if n_ev > 0 else 0.0
        max_rl = float(np.max(rls)) if n_ev > 0 else 0.0
        tech = sub_m['ALS'].iloc[0] if 'ALS' in sub_m.columns and pd.notna(sub_m['ALS'].iloc[0]) else "ALS"

        model_stats.append({
            'modelo': mod,
            'fallas': n_ev,
            'mtbf': round(mtbf_val, 1) if mtbf_val else round(mean_rl, 1),
            'prom_rl': round(mean_rl, 1),
            'med_rl': round(med_rl, 1),
            'min_rl': round(min_rl, 1),
            'max_rl': round(max_rl, 1),
            'tech': tech
        })

    # Ordenar según la opción seleccionada
    if sort_opt == "Frecuencia de Fallas (Mayor a Menor)":
        model_stats.sort(key=lambda x: x['fallas'], reverse=True)
    elif sort_opt == "MTBF (Mayor a Menor)":
        model_stats.sort(key=lambda x: x['mtbf'], reverse=True)
    elif sort_opt == "MTBF (Menor a Mayor)":
        model_stats.sort(key=lambda x: x['mtbf'], reverse=False)
    else:
        model_stats.sort(key=lambda x: x['modelo'], reverse=False)

    ordered_model_names = [m['modelo'] for m in model_stats]
    model_idx_map = {name: i for i, name in enumerate(ordered_model_names)}

    # Crear gráfico Plotly
    fig_mb = go_fig.Figure()

    # 1. Puntos de dispersión (Scatter de cada falla individual con jitter)
    scatter_x = []
    scatter_y = []
    scatter_hover = []
    np.random.seed(42)

    for _, r in df_filtered_models.iterrows():
        mod = r['MODELO_LIMPIO']
        if mod not in model_idx_map:
            continue
        base_x = model_idx_map[mod]
        # Jitter sutil horizontal entre -0.20 y +0.20
        jitter = np.random.uniform(-0.20, 0.20)
        final_x = base_x + jitter
        val_y = r['RL_DIAS']

        pozo_str = r.get('POZO', 'N/A')
        campo_str = r.get('CAMPO', 'N/A')
        bloque_str = r.get('BLOQUE', 'N/A')
        prov_str = r.get('PROVEEDOR', 'N/A')
        als_str = r.get('ALS', 'N/A')
        ffall_str = pd.to_datetime(r['_FALL']).strftime('%Y-%m-%d') if pd.notna(r['_FALL']) else 'N/A'
        frun_str = pd.to_datetime(r['_RUN']).strftime('%Y-%m-%d') if pd.notna(r['_RUN']) else 'N/A'

        scatter_x.append(final_x)
        scatter_y.append(val_y)
        scatter_hover.append(
            f"<b style='color:#c62828; font-size:13px'>{pozo_str}</b> ({mod})<br>"
            f"<hr style='margin:3px 0; border-color:rgba(198,40,40,0.15)'>"
            f"• <b>Run Life a la Falla:</b> {val_y:.0f} días<br>"
            f"• <b>Sistema ALS:</b> {als_str} | <b>Proveedor:</b> {prov_str}<br>"
            f"• <b>Campo:</b> {campo_str} | <b>Bloque:</b> {bloque_str}<br>"
            f"• <b>Fecha Run:</b> {frun_str}<br>"
            f"• <b>Fecha Falla:</b> {ffall_str}"
        )

    # Añadir traza de Dispersión
    fig_mb.add_trace(go_fig.Scatter(
        x=scatter_x,
        y=scatter_y,
        mode='markers',
        name='🔴 Eventos de Falla ALS (Dispersión)',
        marker=dict(
            size=8,
            color='rgba(198, 40, 40, 0.65)',
            line=dict(color='#c62828', width=1)
        ),
        hovertext=scatter_hover,
        hoverinfo='text',
        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor="#c62828",
                        font=dict(size=10, family="Inter, sans-serif", color="#1f221e")),
    ))

    # 2. Línea y Diamantes de MTBF Solo Fallas
    mtbf_xs = [model_idx_map[m['modelo']] for m in model_stats]
    mtbf_ys = [m['mtbf'] for m in model_stats]
    mtbf_hover = [
        f"<b style='color:#c09c2e; font-size:13px'>{m['modelo']}</b><br>"
        f"<hr style='margin:3px 0; border-color:rgba(192,156,46,0.15)'>"
        f"• <b>MTBF Solo Fallas:</b> {m['mtbf']:.1f} días<br>"
        f"• <b>Total Fallas Registradas:</b> {m['fallas']} pozos<br>"
        f"• <b>Run Life Promedio:</b> {m['prom_rl']:.1f} días<br>"
        f"• <b>Mediana (P50):</b> {m['med_rl']:.1f} días<br>"
        f"• <b>Rango RL:</b> {m['min_rl']:.0f}d - {m['max_rl']:.0f}d"
        for m in model_stats
    ]
    mtbf_labels = [f"{m['mtbf']:.0f}d" for m in model_stats]

    fig_mb.add_trace(go_fig.Scatter(
        x=mtbf_xs,
        y=mtbf_ys,
        mode='lines+markers+text',
        name=f'🟡 Línea MTBF Solo Fallas ({als_sel})',
        line=dict(color='#c09c2e', width=3.5),
        marker=dict(
            symbol='diamond',
            size=11,
            color='#c09c2e',
            line=dict(color='#8c6e18', width=1.5)
        ),
        text=mtbf_labels,
        textposition='top center',
        textfont=dict(size=10, color='#1f221e', family='Inter, sans-serif'),
        hovertext=mtbf_hover,
        hoverinfo='text',
        hoverlabel=dict(bgcolor="rgba(255,255,255,0.97)", bordercolor="#c09c2e",
                        font=dict(size=11, family="Inter, sans-serif", color="#1f221e")),
    ))

    # 3. Línea de MTBF Global a Falla (en vez de meta 1500d)
    if mtbf_global_sf and mtbf_global_sf > 0:
        fig_mb.add_hline(
            y=mtbf_global_sf,
            line_dash="dash",
            line_color="#137659",
            line_width=2.5,
            annotation_text=f"MTBF Global a Falla ({als_sel}): {mtbf_global_sf:.0f}d",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#137659", family="Inter, sans-serif")
        )

    max_y_val = max(max(scatter_y) if scatter_y else 0, max(mtbf_ys) if mtbf_ys else 0, mtbf_global_sf if mtbf_global_sf else 500)

    fig_mb.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1f221e", size=10),
        margin=dict(l=35, r=15, t=50, b=70),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(ordered_model_names))),
            ticktext=ordered_model_names,
            tickangle=-35 if len(ordered_model_names) > 6 else 0,
            showgrid=True,
            gridcolor="rgba(19,118,89,0.06)",
            showline=True,
            linecolor="rgba(19,118,89,0.2)",
            tickfont=dict(size=9, color="#1f221e", family="Inter, sans-serif"),
        ),
        yaxis=dict(
            title="Run Life a la Falla / MTBF (días)",
            range=[0, max_y_val * 1.25 if max_y_val > 0 else 1000],
            showgrid=True,
            gridcolor="rgba(19,118,89,0.08)",
            gridwidth=1,
            showline=False,
            tickfont=dict(size=8, color="#5b5c55", family="Inter, sans-serif"),
            ticksuffix="d"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10, family="Inter, sans-serif", color="#1f221e"),
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="rgba(19,118,89,0.2)",
            borderwidth=1
        ),
        height=470
    )

    plotly_config_mb = {
        "displayModeBar": True,
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": f"dispersion_fallas_mtbf_por_modelo_{als_sel.lower()}",
            "height": 600,
            "width": 1100,
            "scale": 3
        }
    }
    st.plotly_chart(fig_mb, use_container_width=True, config=plotly_config_mb)

    # Tabla resumen por modelo de bomba
    with st.expander(f"📋 RESUMEN TABULAR DE MTBF Y FALLAS POR MODELO DE BOMBA ({als_sel})", expanded=False):
        df_tab_modelos = pd.DataFrame([
            {
                'Modelo de Bomba': m['modelo'],
                'Tecnología ALS': m['tech'],
                'Fallas Registradas': m['fallas'],
                'MTBF Solo Fallas (días)': f"{m['mtbf']:.1f}d",
                'Run Life Promedio (días)': f"{m['prom_rl']:.1f}d",
                'Mediana P50 (días)': f"{m['med_rl']:.1f}d",
                'Mínimo RL (días)': f"{m['min_rl']:.0f}d",
                'Máximo RL (días)': f"{m['max_rl']:.0f}d",
            } for m in model_stats
        ])
        render_hud_table(df_tab_modelos, table_id=f"resumen_modelos_bomba_mtbf_{als_sel}")


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
        EXCLUIDOS = {
            'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
            'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
            'MAPACHE/PERICO', 'MAPACHE-PERICO',
            'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
            'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
            'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE', 'TODOS'
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
        
        # ── ENCABEZADO EJECUTIVO (ESTILO TABLERO) ──────────────────────────────────
        _filtros_ind = {
            'ACTIVO':    st.session_state.get('general_activo_filter',    'TODOS'),
            'BLOQUE':    st.session_state.get('general_bloque_filter',    'TODOS'),
            'CAMPO':     st.session_state.get('general_campo_filter',     'TODOS'),
            'ALS':       st.session_state.get('general_als_filter',       'TODOS'),
        }
        _activos_lbl_ind = " · ".join(v for v in _filtros_ind.values() if v != 'TODOS') or "Todos los activos"
        fecha_eval_dt_ind = pd.to_datetime(fecha_evaluacion)

        hero_html_ind = f"""
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
                <line x1="18" y1="20" x2="18" y2="10"/>
                <line x1="12" y1="20" x2="12" y2="4"/>
                <line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
            </div>
            <div>
              <div class="tbl-hero-title">Índices de Falla y Operatividad Anualizada</div>
              <div style="font-family:{_FS}; font-size:11.5px; color:rgba(255,255,255,0.72); display:flex; align-items:center; gap:6px;">
                <div class="tbl-hero-dot"></div>
                <span>Tasa de falla rolling 12 meses, campanas de Gauss y dispersión de modelos</span>
              </div>
            </div>
          </div>
          <div class="tbl-hero-ctx">
            <div class="tbl-hero-item">
              <span class="tbl-hero-k">Corte Evaluación</span>
              <span class="tbl-hero-v">{fecha_eval_dt_ind.strftime('%d/%m/%Y')}</span>
            </div>
            <div class="tbl-hero-item">
              <span class="tbl-hero-k">Filtros Activos</span>
              <span class="tbl-hero-v">{_activos_lbl_ind}</span>
            </div>
            <div class="tbl-hero-item">
              <span class="tbl-hero-k">Meta Corporativa IF</span>
              <span class="tbl-hero-v">≤ 7.5%</span>
            </div>
          </div>
        </div>
        """
        st.markdown(hero_html_ind, unsafe_allow_html=True)

        # ── 1. KPI SEMÁFOROS (4 TARJETAS CON ELEVACIÓN _CARD Y HALOS) ────────────
        st.markdown(f"""
        <style>
        .if-card {{
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
        .if-card:hover {{
            border-color: rgba(46,125,70,0.30);
            box-shadow: {_SH2};
            transform: translateY(-2px);
        }}
        .if-icon {{
            width: 32px; height: 32px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 6px;
        }}
        .if-lbl {{ font-family: {_FS}; font-size: 10px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: {_T2}; margin-bottom: 2px; }}
        .if-val {{ font-family: {_FN}; font-size: 32px; font-weight: 700; line-height: 1.05; letter-spacing: -0.5px; }}
        .if-sub {{ font-family: {_FS}; font-size: 10px; color: {_T2}; margin-top: 4px; }}
        .if-badge {{
            font-family: {_FS}; font-size: 8.5px; font-weight: 700;
            padding: 2px 8px; border-radius: 12px; margin-top: 4px; display: inline-block;
            letter-spacing: 0.4px;
        }}
        </style>""", unsafe_allow_html=True)

        def get_val_num(ind_name):
            try:
                raw = indice_resumen_df[indice_resumen_df['Indicador'] == ind_name]['Valor'].values[0]
                return float(str(raw).replace('%','').strip()) / 100
            except: return 0.0

        def get_prev_if(col_name, df_hist):
            try:
                vals = df_mensual_hist[col_name].dropna().values
                return float(vals[-2]) if len(vals) >= 2 else float(vals[-1])
            except: return 0.0

        META_IF = 0.075  # 7.5%

        def _semaforo_card(label, val_num, prev_num, meta=META_IF):
            if val_num <= meta:
                color = _G
                bg = _G3
                dot_label = '● OK'
            elif val_num <= meta * 1.33:
                color = _Y
                bg = _Y2
                dot_label = '● ALERTA'
            else:
                color = _R
                bg = _R2
                dot_label = '● CRÍTICO'

            delta = val_num - prev_num
            delta_s = f"{'▲' if delta > 0 else '▼'} {abs(delta)*100:.2f}pp vs mes ant."
            delta_c = _R if delta > 0 else _G
            delta_bg = _R2 if delta > 0 else _G3

            return f"""<div class="if-card">
                <div class="if-icon" style="background:{color}; box-shadow:{_halo(color)};">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                </div>
                <div class="if-lbl">{label}</div>
                <div class="if-val" style="color:{color};">{val_num*100:.2f}<span style="font-size:16px;">%</span></div>
                <span class="if-badge" style="background:{bg}; color:{color}; border:1px solid {color}50;">{dot_label}</span>
                <div class="if-sub" style="color:{delta_c}; font-weight:600;">{delta_s}</div>
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

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

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
                "title": {"text": "EVOLUCIÓN DE ÍNDICES (Rolling 12M)", "left": "center", "top": 8,
                          "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"},
                          "subtext": f"Media histórica: {if_mean:.2f}% | Alerta si supera {(if_mean+if_std):.2f}%",
                          "subtextStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}},
                "textStyle": {"fontFamily": "Inter, sans-serif"},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}, "axisPointer": {"type": "cross"}},
                "legend": {"data": ["I.F. Total", "I.F. ALS", "I.F. <1500", "I.F. ALS <1500"], "bottom": 4,
                           "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "4%", "bottom": "18%", "top": "22%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx,
                           "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif", "rotate": 30}}],
                "yAxis": [{"type": "value",
                           "axisLabel": {"formatter": "{value}%", "color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5},
                           "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}}],
                "series": [
                    {"name": "I.F. Total", "type": "line", "smooth": True, "data": val_if_on,
                     "itemStyle": {"color": _G}, "lineStyle": {"width": 2.5, "color": _G},
                     "areaStyle": {"color": f"{_G}12"},
                     "markPoint": {"data": mark_points, "label": {"show": False}},
                     "markLine": {"silent": True, "data": [
                         {"yAxis": 7.5, "label": {"show": True, "formatter": "Meta 7.5%",
                                                   "color": _R, "fontSize": 9, "fontFamily": "Inter, sans-serif"},
                          "lineStyle": {"color": _R, "type": "dashed", "width": 1.8}}
                     ]}},
                    {"name": "I.F. ALS", "type": "line", "smooth": True, "data": val_if_als,
                     "itemStyle": {"color": _Y}, "lineStyle": {"width": 2.5, "color": _Y}},
                    {"name": "I.F. <1500", "type": "line", "smooth": True, "data": val_if_on_1500,
                     "itemStyle": {"color": "#5C6B73"}, "lineStyle": {"width": 1.8, "type": "dashed", "color": "#5C6B73"}},
                    {"name": "I.F. ALS <1500", "type": "line", "smooth": True, "data": val_if_als_1500,
                     "itemStyle": {"color": _G2}, "lineStyle": {"width": 1.8, "type": "dashed", "color": _G2}}
                ]
            }
            components.html(f'<div id="echarts-if-line" style="width:100%;height:370px;{_CARD}overflow:hidden;box-sizing:border-box;"></div>'
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
                "title": {"text": "TENDENCIA OPERATIVIDAD VS EVENTOS", "left": "center", "top": 8,
                          "textStyle": {"color": _G2, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "800"}},
                "textStyle": {"fontFamily": "Inter, sans-serif"},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _BR,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"data": ["Pozos Operativos", "Eventos Totales"], "bottom": 4,
                           "textStyle": {"color": _T2, "fontSize": 9.5, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "8%", "bottom": "18%", "top": "18%", "containLabel": True},
                "xAxis": [{"type": "category", "data": months_idx, "axisLabel": {"color": _T2, "fontSize": 8.5, "fontFamily": "Inter, sans-serif", "rotate": 30}}],
                "yAxis": [
                    {"type": "value", "name": "POZOS", "nameTextStyle": {"color": _T2, "fontSize": 9}, "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif", "fontSize": 8.5}, "splitLine": {"lineStyle": {"color": "rgba(46,125,70,0.06)"}}},
                    {"type": "value", "name": "EVENTOS", "position": "right", "nameTextStyle": {"color": _Y, "fontSize": 9}, "axisLabel": {"color": _Y, "fontFamily": "Inter, sans-serif", "fontSize": 8.5}, "splitLine": {"show": False}}
                ],
                "series": [
                    {"name": "Pozos Operativos", "type": "line", "smooth": True, "data": p_ops,
                     "itemStyle": {"color": _G}, "lineStyle": {"width": 2.5, "color": _G},
                     "areaStyle": {"color": f"{_G}15"}},
                    {"name": "Eventos Totales", "type": "bar", "yAxisIndex": 1, "data": f_tots,
                     "barWidth": "35%",
                     "itemStyle": {"color": f"{_Y}85", "borderRadius": [4, 4, 0, 0]}}
                ]
            }
            components.html(f'<div id="echarts-op-fallas" style="width:100%;height:370px;{_CARD}overflow:hidden;box-sizing:border-box;"></div>'
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
        fecha_eval_norm_b = fecha_eval_dt_b.normalize()
        anio_eval = fecha_eval_dt_b.year
        anio_prev = anio_eval - 1
        df_bloque_raw = df_bd_untr.copy() if df_bd_untr is not None else pd.DataFrame()
        EXCL_BLOQUES = {
            'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
            'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
            'MAPACHE/PERICO', 'MAPACHE-PERICO',
            'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3',
            'RIO META', 'RIO_META', 'RÍO META', 'RÍO_META',
            'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 'EL DIFÍCIL NE', 'TODOS'
        }

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
                df_bloque_raw = df_bd_untr.copy() if df_bd_untr is not None else pd.DataFrame()

                # Excluir pozos/equipos entregados, Flujo Natural y bloques excluidos
                mask_entregado_blk = pd.Series(False, index=df_bloque_raw.index)
                for col in df_bloque_raw.columns:
                    mask_entregado_blk |= df_bloque_raw[col].astype(str).str.upper().str.contains('ENTREG', na=False)
                df_bloque_raw = df_bloque_raw[~mask_entregado_blk].copy()

                for col_als in ('ALS', 'SISTEMA ALS', 'SISTEMA_ALS', 'METODO', 'METODO DE LEVANTAMIENTO'):
                    if col_als in df_bloque_raw.columns:
                        es_fn_blk = df_bloque_raw[col_als].astype(str).str.strip().str.upper().isin(
                            ['FN', 'FLUJO NATURAL', 'FLUJO_NATURAL', 'F.N.', 'FLUJO NAT']
                        )
                        df_bloque_raw = df_bloque_raw[~es_fn_blk].copy()

                for col_filter in ('ACTIVO', 'BLOQUE', 'CAMPO'):
                    if col_filter in df_bloque_raw.columns:
                        df_bloque_raw = df_bloque_raw[~df_bloque_raw[col_filter].astype(str).str.upper().str.strip().isin(EXCL_BLOQUES)].copy()

                df_bloque_raw['FECHA_RUN'] = pd.to_datetime(df_bloque_raw['FECHA_RUN'], errors='coerce')
                df_bloque_raw['FECHA_FALLA'] = pd.to_datetime(df_bloque_raw['FECHA_FALLA'], errors='coerce')
                df_bloque_raw['FECHA_PULL'] = pd.to_datetime(df_bloque_raw['FECHA_PULL'], errors='coerce')
                df_bloque_raw['_RUN'] = pd.to_datetime(df_bloque_raw['FECHA_RUN']).dt.normalize()
                df_bloque_raw['_FALL'] = pd.to_datetime(df_bloque_raw['FECHA_FALLA']).dt.normalize()
                df_bloque_raw['_PULL'] = pd.to_datetime(df_bloque_raw['FECHA_PULL']).dt.normalize()

                if 'RUN_LIFE_EFECTIVO' not in df_bloque_raw.columns:
                    df_bloque_raw['RUN_LIFE_EFECTIVO'] = df_bloque_raw['RUN LIFE'] if 'RUN LIFE' in df_bloque_raw.columns else 0
                df_bloque_raw['RUN_LIFE_EFECTIVO'] = pd.to_numeric(df_bloque_raw['RUN_LIFE_EFECTIVO'], errors='coerce').fillna(0)

                calc_rle = (pd.to_datetime(df_bloque_raw['FECHA_FALLA']) - pd.to_datetime(df_bloque_raw['FECHA_RUN'])).dt.days
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
                    if pd.isna(bloque) or str(bloque).strip() == '' or str(bloque).strip().upper() in EXCL_BLOQUES:
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
                    rl_s = (fecha_eval_norm_b - pd.to_datetime(grp_activos_now['_RUN'])).dt.days
                    rl_val = float(rl_s.mean()) if len(rl_s) > 0 else 0.0

                    rle_s = grp_activos_now['_RLE']
                    rle_val = float(rle_s.mean()) if len(rle_s) > 0 and (rle_s > 0).any() else rl_val

                    # Pozos Fallados
                    grp_fallados_all = grp_runs[
                        (grp_runs['_FALL'].notna()) &
                        (grp_runs['_FALL'] <= fecha_eval_norm_b)
                    ]
                    pozos_fall_cnt = grp_fallados_all['POZO'].nunique() if 'POZO' in grp_fallados_all.columns else len(grp_fallados_all)
                    rl_fall_s = (pd.to_datetime(grp_fallados_all['_FALL']) - pd.to_datetime(grp_fallados_all['_RUN'])).dt.days
                    rl_fall_val = float(rl_fall_s.mean()) if len(rl_fall_s) > 0 else 0.0
                    rle_fall_s = grp_fallados_all['_RLE']
                    rle_fall_val = float(rle_fall_s.mean()) if len(rle_fall_s) > 0 and (rle_fall_s > 0).any() else rl_fall_val

                    # Metas de Run Life del Año Anterior
                    grp_activos_prev = grp_runs_prev[
                        (grp_runs_prev['_RUN'] <= prev_year_end) &
                        (grp_runs_prev['_FALL'].isna() | (grp_runs_prev['_FALL'] > prev_year_end)) &
                        (grp_runs_prev['_PULL'].isna() | (grp_runs_prev['_PULL'] > prev_year_end))
                    ]
                    rl_prev_s = (prev_year_end - pd.to_datetime(grp_activos_prev['_RUN'])).dt.days
                    rl_prev_val = rl_prev_s.mean() if len(rl_prev_s) > 0 else 0.0

                    rle_prev_s = grp_activos_prev['_RLE']
                    rle_prev_val = float(rle_prev_s.mean()) if len(rle_prev_s) > 0 and (rle_prev_s > 0).any() else rl_prev_val

                    meta_rl = round(rl_prev_val, 1) if rl_prev_val > 0 else 1500.0
                    meta_rle = round(rle_prev_val, 1) if rle_prev_val > 0 else 1500.0

                    mtbf_b, _ = calcular_mtbf(grp, fecha_eval_norm_b)
                    col_rle_b = 'RUN_LIFE_EFECTIVO' if 'RUN_LIFE_EFECTIVO' in grp.columns else 'RUN LIFE'
                    mtbf_efec_b, _ = calcular_mtbf(grp, fecha_eval_norm_b, col_life=col_rle_b) if col_rle_b in grp.columns else (mtbf_b, None)

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
                        'mtbf': round(mtbf_b, 1) if mtbf_b is not None else 0.0,
                        'mtbf_efec': round(mtbf_efec_b, 1) if mtbf_efec_b is not None else 0.0,
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

        # --- 3.1 RUN LIFE POR CAMPO / BLOQUE / PROVEEDOR ---
        items_rl = []
        agrupacion_rl = "Campo"
        if not _filtro_activo:
            _render_seccion_run_life_bloque(df_bloque_raw, fecha_eval_norm_b, anio_prev, fecha_eval_dt_b, EXCL_BLOQUES)
            items_rl = _calcular_rl_agrupado_cached(df_bloque_raw, 'CAMPO', fecha_eval_norm_b, anio_prev, solo_fallas_als=True)

        # --- 3.2 CAMPANA DE GAUSS / DISTRIBUCIÓN DE FALLAS ALS ---
        try:
            df_fallas_als_all = df_bloque_raw[
                (df_bloque_raw['_RUN'] <= fecha_eval_norm_b) &
                (df_bloque_raw['_FALL'].notna()) &
                (df_bloque_raw['_FALL'] <= fecha_eval_norm_b) &
                (df_bloque_raw['INDICADOR_MTBF'] == 1)
            ].copy()

            if not df_fallas_als_all.empty:
                if 'RUN LIFE @ FALLA' in df_fallas_als_all.columns:
                    col_rl_f = 'RUN LIFE @ FALLA'
                elif 'RUN LIFE FALLA' in df_fallas_als_all.columns:
                    col_rl_f = 'RUN LIFE FALLA'
                elif 'RUN LIFE' in df_fallas_als_all.columns:
                    col_rl_f = 'RUN LIFE'
                else:
                    col_rl_f = None
                
                if col_rl_f and col_rl_f in df_fallas_als_all.columns:
                    df_fallas_als_all['RL_DIAS'] = pd.to_numeric(df_fallas_als_all[col_rl_f], errors='coerce')
                else:
                    df_fallas_als_all['RL_DIAS'] = (pd.to_datetime(df_fallas_als_all['_FALL']) - pd.to_datetime(df_fallas_als_all['_RUN'])).dt.days
                
                mask_calc = df_fallas_als_all['RL_DIAS'].isna() | (df_fallas_als_all['RL_DIAS'] <= 0)
                if mask_calc.any():
                    df_fallas_als_all.loc[mask_calc, 'RL_DIAS'] = (
                        pd.to_datetime(df_fallas_als_all.loc[mask_calc, '_FALL']) - 
                        pd.to_datetime(df_fallas_als_all.loc[mask_calc, '_RUN'])
                    ).dt.days

                df_fallas_als_all['RLE_DIAS'] = np.where(
                    df_fallas_als_all['_RLE'] > 0,
                    df_fallas_als_all['_RLE'],
                    df_fallas_als_all['RL_DIAS']
                )
                df_fallas_als_all = df_fallas_als_all[df_fallas_als_all['RL_DIAS'] >= 0].copy()

                _render_seccion_campana_gauss(df_fallas_als_all, df_bloque_raw, fecha_eval_norm_b, fecha_eval_dt_b)
        except Exception as e:
            st.warning(f"No se pudo generar la Campana de Gauss: {e}")

        # --- 3.3 DISPERSIÓN DE FALLAS VS MTBF POR MODELO DE BOMBA ---
        try:
            _render_seccion_dispersion_modelo_bomba(df_bloque_raw, fecha_eval_norm_b, fecha_eval_dt_b)
        except Exception as e:
            st.warning(f"No se pudo generar la Dispersión por Modelo de Bomba: {e}")

        # Tabla 2: Resumen de Run Life por Campo / Bloque / Proveedor
        st.markdown("<br>", unsafe_allow_html=True)
        lbl_tabla_rl = f"RESUMEN DE RUN LIFE Y MTBF (OPERATIVOS VS FALLADOS ALS) POR {agrupacion_rl.upper()}" if 'agrupacion_rl' in locals() else "RESUMEN DE RUN LIFE Y MTBF"
        st.markdown(f"<div style='color:#137659; font-family:Arial, sans-serif !important; margin-bottom:10px;'>{lbl_tabla_rl}</div>", unsafe_allow_html=True)
        
        tabla_rl_data = items_rl if ('items_rl' in locals() and items_rl) else (bloques_if if 'bloques_if' in locals() else [])
        if tabla_rl_data:
            df_rl_tab = pd.DataFrame([
                {
                    (agrupacion_rl if 'agrupacion_rl' in locals() else 'Bloque'): b.get('nombre', b.get('bloque', '')),
                    'Pozos Únicos': b.get('total_pozos_unicos', b.get('total', 0)),
                    'Total Corridas': b.get('total_corridas', b.get('total', 0)),
                    'Pozos Operativos': b.get('pozos_op', b.get('prom_on', 0)),
                    'Run Life Op (días)': f"{b.get('rl_op', b.get('rl', 0)):.1f}d",
                    'Run Life Ef. Op (días)': f"{b.get('rle_op', b.get('rl_efectivo', 0)):.1f}d",
                    'Fallas ALS': b.get('tot_fallas', b.get('fallas_als', b.get('fallas_tot', 0))),
                    'Run Life Fallas ALS (días)': f"{b.get('rl_fall', 0):.1f}d",
                    'Run Life Ef. Fallas (días)': f"{b.get('rle_fall', 0):.1f}d",
                    '% Peso Fallas': f"{b.get('pct_fallas', 0):.1f}%",
                    'Aporte al RL Global': f"{b.get('aporte_rl_fall', 0):.1f}d",
                    'MTBF (días)': f"{b.get('mtbf', 0):.1f}d",
                    'MTBF Efectivo (días)': f"{b.get('mtbf_efec', 0):.1f}d",
                    f"Meta R.L. ({anio_prev if 'anio_prev' in locals() else 2025})": f"{b.get('meta_rl', 0):.1f}d",
                    f"Meta R.L. Ef. ({anio_prev if 'anio_prev' in locals() else 2025})": f"{b.get('meta_rle', 0):.1f}d"
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
