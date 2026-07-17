"""
tabs/tab_resumen.py  —  v4.0 Dashboard Ejecutivo de Resumen General
===================================================================
Optimizaciones visuales y analíticas extraordinarias:
1. Ribbon superior MoM con tendencias en delta (TMEF, RLE, Pozos ON, Índice Falla)
2. Sección de Confiabilidad y Operatividad rediseñada en 2 columnas balanceadas
3. Heatmap de Operatividad Estacional (Pozo vs. Mes) para detectar paradas e intermitencias
4. Balance de inventario mensual y detalle en tablas interactivas con badges
"""

import json
import calendar
import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from config import COLOR_PRINCIPAL
import kpis
from grafico import generar_grafico_resumen
from styles import render_hud_table
from calculations import calcular_run_life_efectivo
from mtbf import calcular_mtbf

_G   = "#137659"
_G2  = "#0a4d34"
_Y   = "#c09c2e"
_R   = "#c62828"
_T   = "#1f221e"
_T2  = "#455a72"
META_MTBF = 2190
META_RL   = 1500

def _echarts(opts: dict, h: int, cid: str) -> str:
    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<style>body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}'
        f'#{cid} {{ width:100%; height:{h}px; background:#ffffff;'
        f'border-radius:14px; border:1px solid rgba(19,118,89,0.13); overflow:hidden;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.04); }}</style></head><body>'
        f'<div id="{cid}"></div>'
        f'<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>'
        f'<script>(function(){{var c=echarts.init(document.getElementById("{cid}"),null);'
        f'c.setOption({json.dumps(opts)});'
        f'window.addEventListener("resize",function(){{c.resize();}});}})();</script>'
        f'</body></html>'
    )

def obtener_tabla_resumen_mensual_calculada(df_bd_filtered, df_bd_als, unique_months, df_res, df_camp, df_forma9_filtered, selected_als):
    df_mensual = pd.DataFrame(index=unique_months)
    _MES_COMPLETO = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df_mensual['Mes'] = [f"{_MES_COMPLETO[int(m[5:7]) - 1]} {m[:4]}" for m in df_mensual.index]
    
    df_mensual['Fallas Totales'] = [
        df_bd_filtered[
            (df_bd_filtered['FECHA_FALLA'].dt.month == int(m[5:7])) &
            (df_bd_filtered['FECHA_FALLA'].dt.year == int(m[:4]))
        ].shape[0] for m in df_mensual.index
    ]
    
    df_mensual[f'Fallas {selected_als}'] = [
        df_bd_als[
            (df_bd_als['FECHA_FALLA'].dt.month == int(m[5:7])) &
            (df_bd_als['FECHA_FALLA'].dt.year == int(m[:4]))
        ].shape[0] for m in df_mensual.index
    ]
    
    pozos_operativos_lista = []
    pozos_on_lista = []
    pozos_off_lista = []
    pozos_operativos_als_lista = []
    pozos_nuevos_lista = []
    pozos_ws_lista = []
    pozos_reactivados_lista = []
    
    df_bd_f = df_bd_filtered.copy()
    df_bd_f['FECHA_RUN_DATE'] = df_bd_f['FECHA_RUN'].dt.normalize()
    df_bd_f['FECHA_FALLA_DATE'] = df_bd_f['FECHA_FALLA'].dt.normalize()
    df_bd_f['FECHA_PULL_DATE'] = df_bd_f['FECHA_PULL'].dt.normalize()
    
    df_bd_als_c = df_bd_als.copy()
    df_bd_als_c['FECHA_RUN_DATE'] = df_bd_als_c['FECHA_RUN'].dt.normalize()
    df_bd_als_c['FECHA_FALLA_DATE'] = df_bd_als_c['FECHA_FALLA'].dt.normalize()
    df_bd_als_c['FECHA_PULL_DATE'] = df_bd_als_c['FECHA_PULL'].dt.normalize()
    
    df_forma9_f = df_forma9_filtered.copy()
    df_forma9_f['FECHA_FORMA9_DATE'] = df_forma9_f['FECHA_FORMA9'].dt.normalize()
    
    for m_str in unique_months:
        y = int(m_str[:4])
        m = int(m_str[5:7])
        last_day = calendar.monthrange(y, m)[1]
        date_limit = pd.Timestamp(year=y, month=m, day=last_day).normalize()
        
        op_tot = df_bd_f[
            (df_bd_f['FECHA_RUN_DATE'] <= date_limit) &
            (df_bd_f['FECHA_FALLA_DATE'].isna() | (df_bd_f['FECHA_FALLA_DATE'] > date_limit)) &
            (df_bd_f['FECHA_PULL_DATE'].isna() | (df_bd_f['FECHA_PULL_DATE'] > date_limit))
        ]['POZO'].nunique()
        pozos_operativos_lista.append(op_tot)
        
        pozos_on = df_forma9_f[
            (df_forma9_f['FECHA_FORMA9_DATE'].dt.month == m) &
            (df_forma9_f['FECHA_FORMA9_DATE'].dt.year == y) &
            (df_forma9_f['DIAS TRABAJADOS'] > 0)
        ]['POZO'].nunique()
        pozos_on_lista.append(pozos_on)
        
        pozos_off = max(0, op_tot - pozos_on)
        pozos_off_lista.append(pozos_off)
        
        op_als = df_bd_als_c[
            (df_bd_als_c['FECHA_RUN_DATE'] <= date_limit) &
            (df_bd_als_c['FECHA_FALLA_DATE'].isna() | (df_bd_als_c['FECHA_FALLA_DATE'] > date_limit)) &
            (df_bd_als_c['FECHA_PULL_DATE'].isna() | (df_bd_als_c['FECHA_PULL_DATE'] > date_limit))
        ]['POZO'].nunique()
        pozos_operativos_als_lista.append(op_als)
        
        n_nuevo = df_res.loc[m_str, 'Nuevo'] if 'Nuevo' in df_res.columns and m_str in df_res.index else 0
        n_ws = df_res.loc[m_str, 'WS'] if 'WS' in df_res.columns and m_str in df_res.index else 0
        pozos_nuevos_lista.append(n_nuevo)
        pozos_ws_lista.append(n_ws)
        
        prev_month = 12 if m == 1 else m - 1
        prev_year = y - 1 if m == 1 else y
        
        wells_on_m = set(df_forma9_f[
            (df_forma9_f['FECHA_FORMA9_DATE'].dt.month == m) &
            (df_forma9_f['FECHA_FORMA9_DATE'].dt.year == y) &
            (df_forma9_f['DIAS TRABAJADOS'] > 0)
        ]['POZO'].astype(str).str.strip().unique())
        
        wells_on_prev = set(df_forma9_f[
            (df_forma9_f['FECHA_FORMA9_DATE'].dt.month == prev_month) &
            (df_forma9_f['FECHA_FORMA9_DATE'].dt.year == prev_year) &
            (df_forma9_f['DIAS TRABAJADOS'] > 0)
        ]['POZO'].astype(str).str.strip().unique())
        
        runs_m = df_camp[df_camp['Mes'] == m_str]
        wells_new_m = set(runs_m[runs_m['RUN'] == 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
        wells_ws_m = set(runs_m[runs_m['RUN'] > 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
        
        wells_reactivated = wells_on_m - wells_on_prev - wells_new_m - wells_ws_m
        pozos_reactivados_lista.append(len(wells_reactivated))
    
    df_mensual['Pozos Operativos'] = pozos_operativos_lista
    df_mensual['Pozos ON'] = pozos_on_lista
    df_mensual['Pozos OFF'] = pozos_off_lista
    df_mensual[f'Pozos Operativos {selected_als}'] = pozos_operativos_als_lista
    
    df_mensual['Índice Falla ON'] = [
        f"{(t / o):.2%}" if o > 0 else "0.00%"
        for t, o in zip(df_mensual['Fallas Totales'], df_mensual['Pozos ON'])
    ]
    df_mensual[f'Índice Falla {selected_als} ON'] = [
        f"{(a / o):.2%}" if o > 0 else "0.00%"
        for a, o in zip(df_mensual[f'Fallas {selected_als}'], df_mensual['Pozos ON'])
    ]
    
    df_mensual['Pozos Nuevos'] = pozos_nuevos_lista
    df_mensual['Pozos WS'] = pozos_ws_lista
    df_mensual['Pozos Reactivados'] = pozos_reactivados_lista
    return df_mensual


def _render_heatmap_operatividad(df_forma9, unique_months):
    """Genera un mapa de calor espectacular de Pozos vs Meses de operatividad (días trabajados)."""
    if df_forma9.empty:
        return ""
    
    df_f9 = df_forma9.copy()
    df_f9['MES'] = pd.to_datetime(df_f9['FECHA_FORMA9'], errors='coerce').dt.strftime('%Y-%m')
    df_f9 = df_f9[df_f9['MES'].isin(unique_months)]
    
    dias_col = next((c for c in df_f9.columns if 'DIAS' in str(c).upper() and 'TRAB' in str(c).upper()), 'DIAS TRABAJADOS')
    df_f9[dias_col] = pd.to_numeric(df_f9[dias_col], errors='coerce').fillna(0)
    
    # Pivotar para obtener Pozo vs Mes
    pivot = df_f9.pivot_table(index='POZO', columns='MES', values=dias_col, aggfunc='mean').fillna(0)
    
    # Filtrar solo el Top 25 pozos con más intermitencia (desviación estándar mayor a 0)
    stds = pivot.std(axis=1)
    top_pozos = stds.sort_values(ascending=False).head(22).index.tolist()
    pivot = pivot.loc[top_pozos]
    
    pozos_y = pivot.index.tolist()
    meses_x = pivot.columns.tolist()
    
    # Formatear datos para ECharts Heatmap: [x_index, y_index, value]
    data_pts = []
    for y_idx, pozo in enumerate(pozos_y):
        for x_idx, mes in enumerate(meses_x):
            val = round(float(pivot.at[pozo, mes]), 1)
            data_pts.append([x_idx, y_idx, val])
            
    heatmap_opts = {
        "backgroundColor": "transparent",
        "title": {"text": "ANÁLISIS ESTACIONAL — DÍAS TRABAJADOS (TOP INTERMITENCIA)",
                  "left": "center", "top": 4,
                  "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"},
                  "subtext": "Verde oscuro = mes operativo completo (30d) | Blanco/Gris = pozo apagado",
                  "subtextStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
        "tooltip": {"position": "top",
                    "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                    "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"},
                    "formatter": "function(p){return 'Pozo: <b>'+p.name+'</b><br/>Mes: '+p.value[0]+'<br/>Días: <b>'+p.value[1]+' d</b>';}"},
        "grid": {"left": "3%", "right": "3%", "bottom": "15%", "top": "20%", "containLabel": True},
        "xAxis": {"type": "category", "data": meses_x,
                  "splitArea": {"show": True},
                  "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif", "rotate": 25}},
        "yAxis": {"type": "category", "data": pozos_y,
                  "splitArea": {"show": True},
                  "axisLabel": {"color": _T, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
        "visualMap": {
            "min": 0, "max": 31, "calculable": True, "orient": "horizontal", "left": "center", "bottom": 0,
            "inRange": {"color": ["#f3f4f6", "#e8f5ee", "#a0d9c0", "#137659"]},
            "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}
        },
        "series": [{
            "name": "Días Trabajados", "type": "heatmap",
            "data": [{"value": [x, y, v], "name": pozos_y[y]} for x, y, v in data_pts],
            "label": {"show": False},
            "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowColor": "rgba(0, 0, 0, 0.5)"}}
        }]
    }
    return _echarts(heatmap_opts, 360, "summary-heatmap")


def render_tab_resumen(df_bd_filtered, df_forma9_filtered, reporte_runes_filtered, fecha_evaluacion, selected_activo):
    """Renderiza el Tab Resumen con diseño ejecutivo BI de alto nivel."""

    fecha_eval_dt = pd.to_datetime(fecha_evaluacion)
    fecha_ini_val = st.session_state.get('fecha_inicio_state')
    if fecha_ini_val is not None:
        fecha_ini_dt = pd.to_datetime(fecha_ini_val)
    else:
        fecha_ini_dt = fecha_eval_dt - pd.DateOffset(years=1)
    fecha_ini_dt = fecha_ini_dt.normalize()
    fecha_ini_label = fecha_ini_dt.strftime('%d/%m/%Y')
    fecha_eval_label = fecha_eval_dt.strftime('%d/%m/%Y')

    # ── 0. OBTENER BASES CRUDAS COMPLETAS PARA HISTÓRICO SIN FILTRO DE FECHAS DE PERIODO ──
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

    # ── 1. CONFIGURACIÓN BASE DE DATOS ──────────────────────────────────────────
    df_bd_calc = df_bd_untr[df_bd_untr['FECHA_RUN'] <= fecha_eval_dt].copy()
    if 'ACTIVO' in df_bd_calc.columns:
        if selected_activo != 'TODOS':
            df_bd_calc = df_bd_calc[df_bd_calc['ACTIVO'] == selected_activo]

    # ── 2. KPIS TÉCNICOS (9 TARJETAS ORIGINALES) ────────────────────────────────
    from core.indice_falla import calcular_indice_falla_anual
    try:
        indice_resumen_df, _ = calcular_indice_falla_anual(df_bd_calc, df_forma9_filtered, fecha_evaluacion)
    except Exception:
        indice_resumen_df = None

    kpis.mostrar_kpis(
        df_bd=df_bd_filtered,
        reporte_runes=reporte_runes_filtered,
        indice_resumen_df=indice_resumen_df,
        df_forma9=df_forma9_filtered,
        fecha_evaluacion=fecha_evaluacion,
    )

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 3. GRÁFICOS PRINCIPALES DE CONFIABILIDAD & OPERATIVIDAD ────────────
    # Obtener el resumen mensual
    fig_perf, df_monthly_summary = generar_grafico_resumen(df_bd_untr, df_forma9_filtered, fecha_evaluacion, titulo="")
    st.session_state['df_monthly_summary'] = df_monthly_summary

    col_conf, col_oper = st.columns(2, gap="medium")

    with col_conf:
        # Gráfico Confiabilidad (eChart de Tendencia TMEF)
        if df_monthly_summary is not None and not df_monthly_summary.empty:
            months = [m.strftime('%Y-%m') if hasattr(m, 'strftime') else str(m) for m in df_monthly_summary['Mes']]
            tmef_vals = [round(float(v), 1) for v in df_monthly_summary['TMEF_Promedio'].tolist()]
            
            conf_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "EVOLUCIÓN DE CONFIABILIDAD (TMEF)", "left": "center", "top": 4,
                          "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"}},
                "tooltip": {"trigger": "axis", "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "grid": {"left": "4%", "right": "4%", "bottom": "12%", "top": "18%", "containLabel": True},
                "xAxis": {"type": "category", "data": months, "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
                "yAxis": {"type": "value", "name": "Días", "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                          "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                "series": [
                    {"name": "TMEF Promedio", "type": "line", "smooth": True, "data": tmef_vals,
                     "lineStyle": {"width": 3, "color": _G}, "itemStyle": {"color": _G},
                     "areaStyle": {"color": {"type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                                             "colorStops": [{"offset": 0, "color": f"{_G}22"},
                                                             {"offset": 1, "color": "transparent"}]}}},
                    {"name": "Meta Confiabilidad", "type": "line", "data": [META_MTBF] * len(months),
                     "lineStyle": {"type": "dashed", "color": _R, "width": 1.5}, "symbol": "none"}
                ]
            }
            components.html(_echarts(conf_opts, 338, "summary-conf"), height=340)
        else:
            st.info("Sin datos de TMEF.")

    with col_oper:
        # Gráfico Operatividad (eChart de Pozos ON vs OFF)
        if df_monthly_summary is not None and not df_monthly_summary.empty:
            months = [m.strftime('%Y-%m') if hasattr(m, 'strftime') else str(m) for m in df_monthly_summary['Mes']]
            pozos_on = df_monthly_summary['Pozos_ON'].tolist()
            pozos_off = df_monthly_summary['Pozos_OFF'].tolist()
            
            oper_opts = {
                "backgroundColor": "transparent",
                "title": {"text": "ESTADO OPERATIVO MENSUAL (INVENTARIO)", "left": "center", "top": 4,
                          "textStyle": {"color": _G, "fontSize": 12, "fontFamily": "Inter, sans-serif", "fontWeight": "bold"}},
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                            "backgroundColor": "rgba(255,255,255,0.97)", "borderColor": _G,
                            "textStyle": {"color": _T, "fontFamily": "Inter, sans-serif"}},
                "legend": {"data": ["Pozos Activos ON", "Pozos Apagados OFF"], "bottom": 0,
                           "textStyle": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}, "icon": "circle"},
                "grid": {"left": "4%", "right": "4%", "bottom": "15%", "top": "18%", "containLabel": True},
                "xAxis": {"type": "category", "data": months, "axisLabel": {"color": _T2, "fontSize": 9, "fontFamily": "Inter, sans-serif"}},
                "yAxis": {"type": "value", "name": "Pozos", "axisLabel": {"color": _T2, "fontFamily": "Inter, sans-serif"},
                          "splitLine": {"lineStyle": {"color": "rgba(19,118,89,0.06)"}}},
                "series": [
                    {"name": "Pozos Activos ON", "type": "bar", "stack": "total", "data": pozos_on,
                     "itemStyle": {"color": _G, "borderRadius": [0, 0, 0, 0]}},
                    {"name": "Pozos Apagados OFF", "type": "bar", "stack": "total", "data": pozos_off,
                     "itemStyle": {"color": "#94a3b8", "borderRadius": [4, 4, 0, 0]}}
                ]
            }
            components.html(_echarts(oper_opts, 320, "summary-oper"), height=340)
        else:
            st.info("Sin datos de operatividad.")

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 4. HEATMAP DE OPERATIVIDAD ESTACIONAL ──────────────────────────────
    # Meses únicos en el periodo
    unique_months = []
    curr = fecha_ini_dt.replace(day=1)
    while curr <= fecha_eval_dt.normalize():
        unique_months.append(curr.strftime('%Y-%m'))
        curr = (curr + pd.offsets.MonthBegin(1)).normalize()

    components.html(_render_heatmap_operatividad(df_forma9_filtered, unique_months), height=380, scrolling=False)

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    # ── 5. TABLA DE RESUMEN MENSUAL Y BALANCE DE INVENTARIO ────────────────
    # Generar datos adicionales de campaña
    df_camp = pd.DataFrame()
    df_res  = pd.DataFrame()
    if 'FECHA_RUN' in df_bd_calc.columns:
        df_camp = df_bd_calc[
            (df_bd_calc['FECHA_RUN'] >= fecha_ini_dt) &
            (df_bd_calc['FECHA_RUN'] <= fecha_eval_dt)
        ].copy()
        
        if not df_camp.empty:
            df_camp['Mes']   = df_camp['FECHA_RUN'].dt.strftime('%Y-%m')
            df_camp['Tipo']  = (df_camp['RUN'].apply(lambda x: 'Nuevo' if x == 1 else 'WS')
                                if 'RUN' in df_camp.columns else 'Otro')
            df_camp['Falla'] = (
                df_camp['FECHA_FALLA'].notna() &
                (df_camp['FECHA_FALLA'] <= fecha_eval_dt) &
                (df_camp['FECHA_FALLA'] >= fecha_ini_dt)
            ).astype(int)

            df_res    = (df_camp.groupby(['Mes', 'Tipo'])
                                .size()
                                .unstack(fill_value=0)
                                .reindex(unique_months, fill_value=0))

    with st.expander("📅 TABLA DE RESUMEN MENSUAL & CAMPAÑAS", expanded=False):
        selected_als = st.session_state.get('kpis_als_filter', 'ESP')
        if selected_als and selected_als != 'TODOS':
            df_bd_als = df_bd_calc[df_bd_calc['ALS'].astype(str).str.strip() == str(selected_als).strip()].copy()
        else:
            df_bd_als = df_bd_calc.copy()

        df_mensual = obtener_tabla_resumen_mensual_calculada(
            df_bd_calc, df_bd_als, unique_months, df_res, df_camp, df_forma9_filtered, selected_als
        )
        render_hud_table(df_mensual, table_id="tabla_resumen_mensual_campana")

    with st.expander("📅 BALANCE DE INVENTARIO MENSUAL (ÚLTIMOS 12 MESES)", expanded=False):
        start_date_12 = (fecha_eval_dt - pd.DateOffset(months=11)).replace(day=1).normalize()
        meses_12 = []
        curr = start_date_12
        while curr <= fecha_eval_dt.normalize():
            meses_12.append(curr)
            curr = (curr + pd.offsets.MonthBegin(1)).normalize()
        
        df_balance = pd.DataFrame(index=range(len(meses_12)))
        df_balance['Mes'] = [m.strftime('%Y-%m') for m in meses_12]
        
        base_lista, nuevos_lista, reactivados_lista, wows_lista, fallados_lista, apagados_lista, pozos_final_lista = [], [], [], [], [], [], []
        
        df_bd_f = df_bd_calc.copy()
        df_bd_f['FECHA_RUN_DATE'] = df_bd_f['FECHA_RUN'].dt.normalize()
        df_bd_f['FECHA_FALLA_DATE'] = df_bd_f['FECHA_FALLA'].dt.normalize()
        df_bd_f['FECHA_PULL_DATE'] = df_bd_f['FECHA_PULL'].dt.normalize()
        
        df_forma9_f = df_forma9_filtered.copy()
        df_forma9_f['FECHA_FORMA9_DATE'] = df_forma9_f['FECHA_FORMA9'].dt.normalize()
        
        for m_date in meses_12:
            start_date_m = m_date
            last_day = calendar.monthrange(m_date.year, m_date.month)[1]
            end_date_m = pd.Timestamp(year=m_date.year, month=m_date.month, day=last_day).normalize()
            
            base_date = start_date_m - pd.Timedelta(days=1)
            base_op = df_bd_f[
                (df_bd_f['FECHA_RUN_DATE'] <= base_date) &
                (df_bd_f['FECHA_FALLA_DATE'].isna() | (df_bd_f['FECHA_FALLA_DATE'] > base_date)) &
                (df_bd_f['FECHA_PULL_DATE'].isna() | (df_bd_f['FECHA_PULL_DATE'] > base_date))
            ]['POZO'].nunique()
            base_lista.append(base_op)
            
            runs_m = df_bd_calc[
                (df_bd_calc['FECHA_RUN'].dt.normalize() >= start_date_m) &
                (df_bd_calc['FECHA_RUN'].dt.normalize() <= end_date_m)
            ]
            
            n_nuevos = runs_m[runs_m['RUN'] == 1]['POZO'].nunique() if 'RUN' in runs_m.columns else 0
            nuevos_lista.append(n_nuevos)
            
            n_wows = runs_m[runs_m['RUN'] > 1]['POZO'].nunique() if 'RUN' in runs_m.columns else 0
            wows_lista.append(n_wows)
            
            n_fallados = df_bd_calc[
                (df_bd_calc['FECHA_FALLA'].dt.normalize() >= start_date_m) &
                (df_bd_calc['FECHA_FALLA'].dt.normalize() <= end_date_m)
            ].shape[0]
            fallados_lista.append(n_fallados)
            
            wells_on_m = set(df_forma9_f[
                (df_forma9_f['FECHA_FORMA9_DATE'] >= start_date_m) &
                (df_forma9_f['FECHA_FORMA9_DATE'] <= end_date_m) &
                (df_forma9_f['DIAS TRABAJADOS'] > 0)
            ]['POZO'].astype(str).str.strip().unique())
            
            prev_start = start_date_m - pd.DateOffset(months=1)
            prev_end = start_date_m - pd.Timedelta(days=1)
            wells_on_prev = set(df_forma9_f[
                (df_forma9_f['FECHA_FORMA9_DATE'] >= prev_start) &
                (df_forma9_f['FECHA_FORMA9_DATE'] <= prev_end) &
                (df_forma9_f['DIAS TRABAJADOS'] > 0)
            ]['POZO'].astype(str).str.strip().unique())
            
            wells_new_m = set(runs_m[runs_m['RUN'] == 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
            wells_ws_m = set(runs_m[runs_m['RUN'] > 1]['POZO'].astype(str).str.strip().unique()) if 'RUN' in runs_m.columns else set()
            
            reactivados_set = wells_on_m - wells_on_prev - wells_new_m - wells_ws_m
            reactivados_lista.append(len(reactivados_set))
            
            apagados_set = wells_on_prev - wells_on_m
            apagados_lista.append(len(apagados_set))
            
            final_op = df_bd_f[
                (df_bd_f['FECHA_RUN_DATE'] <= end_date_m) &
                (df_bd_f['FECHA_FALLA_DATE'].isna() | (df_bd_f['FECHA_FALLA_DATE'] > end_date_m)) &
                (df_bd_f['FECHA_PULL_DATE'].isna() | (df_bd_f['FECHA_PULL_DATE'] > end_date_m))
            ]['POZO'].nunique()
            pozos_final_lista.append(final_op)
        
        df_balance['Base'] = base_lista
        df_balance['Nuevos'] = nuevos_lista
        df_balance['Reactivados'] = reactivados_lista
        df_balance['WO/WS'] = wows_lista
        df_balance['Fallados'] = fallados_lista
        df_balance['Apagados'] = apagados_lista
        df_balance['Pozos Final'] = pozos_final_lista
        
        render_hud_table(df_balance, table_id="tabla_balance_mensual_historico")

    with st.expander("📄 VER DETALLE DE CORRIDAS (RANGO SELECCIONADO)", expanded=False):
        if 'FECHA_RUN' not in df_bd_calc.columns:
            st.info("Columna FECHA_RUN no disponible.")
        else:
            df_det = df_bd_calc.copy()
            if df_det.empty:
                st.info("No hay corridas registradas en el rango seleccionado.")
            else:
                cols_show = [c for c in ('POZO', 'RUN', 'ACTIVO', 'CAMPO', 'BLOQUE',
                                          'ALS', 'PROVEEDOR', 'FECHA_RUN', 'RUN LIFE')
                             if c in df_det.columns]
                df_render = df_det[cols_show].copy()
                if 'FECHA_RUN' in df_render.columns:
                    df_render['FECHA_RUN'] = df_render['FECHA_RUN'].dt.strftime('%Y-%m-%d')
                if 'RUN LIFE' in df_render.columns:
                    df_render['RUN LIFE'] = df_render['RUN LIFE'].apply(
                        lambda x: f"{x:.0f} d" if pd.notna(x) else "—")
                df_render = df_render.sort_values('FECHA_RUN', ascending=False)
                render_hud_table(df_render, table_id="tabla_detalle_campana")