"""
calculations.py
===============
Cálculos puros de indicadores: matemática y lógica de negocio.
SIN código de UI. SIN llamadas a st.* (excepto decoradores de caché).
"""

import unicodedata
from datetime import timedelta

import numpy as np
import pandas as pd
import streamlit as st

from indice_falla import calcular_indice_falla_anual          # noqa: F401  (reexportado)
from run_life_efectivo import calcular_run_life_efectivo
from config import COLOR_PRINCIPAL
import tema


# ===========================================================================
# 1. CLASIFICACIÓN POR PALABRAS CLAVE
# ===========================================================================

def clasificar_razon_ia(razon: str) -> str:
    """Clasifica la razón de pull usando palabras clave normalizadas."""
    if not isinstance(razon, str):
        return 'Desconocida'
    razon_norm = (
        unicodedata.normalize('NFKD', razon)
        .encode('ascii', 'ignore')
        .decode('utf-8')
        .lower()
    )
    palabras_mecanica   = ['mecanic','eje','rotura','desgaste','rodamient','sello','acople','engranaje','mecanico','mecanica']
    palabras_electrica  = ['electri','bomba','cable','aislamiento','motor','corto','bobina','fase','desbalanceado','electrica','electrico','variador','tablero','aterrizado','control','ALS']
    palabras_tuberia    = ['tuberia','casing','varilla','tubing','liner','fuga','pinchazo','conexion','tubo','perforacion']
    palabras_yacimiento = ['yacimiento','abandono','agua','rediseño','recañoneo','ws','wo','solidos','arena','incrustacion','parafina','asfalteno','presion','flujo','formacion','economico','produccion']

    if any(w in razon_norm for w in palabras_mecanica):
        return 'Mecánica'
    if any(w in razon_norm for w in palabras_electrica):
        return 'Eléctrica'
    if any(w in razon_norm for w in palabras_tuberia):
        return 'Tubería'
    if any(w in razon_norm for w in palabras_yacimiento):
        return 'Yacimiento'
    return 'Otra'


# ===========================================================================
# 2. CÁLCULOS INICIALES (Run Life, NICK, PROVEEDOR en FORMA9)
# ===========================================================================

@st.cache_data(show_spinner="Procesando cálculos iniciales...")
def perform_initial_calculations(df_forma9, df_bd, fecha_evaluacion):
    """
    Realiza los cálculos iniciales en BD y luego en FORMA 9 de manera vectorizada.
    Anclado a la fecha de evaluación.
    Retorna (df_forma9_copy, df_bd).
    """
    if fecha_evaluacion is None:
        try:
            if df_forma9 is not None and 'FECHA_FORMA9' in df_forma9.columns:
                tmp = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
                if not tmp.dropna().empty:
                    fecha_evaluacion = tmp.max()
        except Exception:
            fecha_evaluacion = None

    fecha_evaluacion = pd.to_datetime(fecha_evaluacion)

    df_bd['RUN LIFE'] = np.where(
        df_bd['FECHA_FALLA'].notna(),
        (df_bd['FECHA_FALLA'] - df_bd['FECHA_RUN']).dt.days,
        np.where(
            df_bd['FECHA_PULL'].notna(),
            (df_bd['FECHA_PULL'] - df_bd['FECHA_RUN']).dt.days,
            np.where(
                df_bd['FECHA_PULL'].isna(),
                (fecha_evaluacion - df_bd['FECHA_RUN']).dt.days,
                np.nan,
            ),
        ),
    )

    df_bd['NICK'] = df_bd['POZO'].astype(str) + '-' + df_bd['RUN'].astype(str)
    df_forma9['FECHA_FORMA9'] = pd.to_datetime(df_forma9['FECHA_FORMA9'])
    df_forma9_copy = df_forma9.copy()
    df_bd_filtered = df_bd[df_bd['FECHA_RUN'] <= fecha_evaluacion].copy()

    merged_df = pd.merge(
        df_forma9_copy.reset_index(),
        df_bd_filtered[['POZO', 'RUN', 'PROVEEDOR', 'FECHA_RUN', 'FECHA_PULL']],
        on='POZO', how='left',
    )
    merged_df['is_match'] = (
        (merged_df['FECHA_FORMA9'] >= merged_df['FECHA_RUN']) &
        (merged_df['FECHA_FORMA9'] <  merged_df['FECHA_PULL'].fillna(pd.to_datetime(fecha_evaluacion)))
    )
    best_matches_idx = merged_df[merged_df['is_match']].groupby('index')['FECHA_RUN'].idxmax()
    best_matches_df  = merged_df.loc[best_matches_idx]

    df_forma9_copy['RUN']      = best_matches_df.set_index('index')['RUN']
    df_forma9_copy['PROVEEDOR'] = best_matches_df.set_index('index')['PROVEEDOR']
    df_forma9_copy[['RUN', 'PROVEEDOR']] = df_forma9_copy[['RUN', 'PROVEEDOR']].fillna('NO DATA✍️')
    df_forma9_copy['NICK'] = df_forma9_copy['POZO'].astype(str) + '-' + df_forma9_copy['RUN'].astype(str)

    run_life_efectivo_promedio = 0.0
    try:
        run_life_efectivo_promedio, df_bd = calcular_run_life_efectivo(df_bd, df_forma9, fecha_evaluacion)
    except Exception as e:
        print(f"[ERROR] calcular_run_life_efectivo: {e}")

    df_bd.attrs['run_life_efectivo_promedio'] = run_life_efectivo_promedio
    return df_forma9_copy, df_bd


# ===========================================================================
# 3. INDICADORES FINALES (Run Life Operativo + Fallas Mensuales)
# ===========================================================================

def calcular_indicadores_finales(df_forma9, df_bd):
    """
    Calcula Run Life Operativo (suma de DIAS TRABAJADOS por NICK) y
    agrupa fallas por mes.
    Retorna (df_trabajo, fallas_mensuales).
    """
    run_life_operativo = df_forma9.groupby('NICK')['DIAS TRABAJADOS'].sum().reset_index()
    run_life_operativo.rename(columns={'DIAS TRABAJADOS': 'RUN LIFE OPERATIVO'}, inplace=True)
    df_bd = pd.merge(df_bd, run_life_operativo, on='NICK', how='left').fillna({'RUN LIFE OPERATIVO': 0})

    df_fallas = df_bd[df_bd['FECHA_FALLA'].notna()].copy()
    df_fallas['MES'] = df_fallas['FECHA_FALLA'].dt.to_period('M')
    fallas_mensuales = df_fallas.groupby('MES')['NICK'].count().reset_index()
    fallas_mensuales.rename(columns={'NICK': 'Numero de Fallas'}, inplace=True)
    fallas_mensuales['MES'] = fallas_mensuales['MES'].dt.to_timestamp()

    df_trabajo = df_bd.copy()
    return df_trabajo, fallas_mensuales


# ===========================================================================
# 4. REPORTE COMPLETO (RUNES + Run Life)
# ===========================================================================

@st.cache_data(show_spinner="Generando reporte detallado...")
def generar_reporte_completo(df_bd, df_forma9, fecha_evaluacion):
    """
    Genera el reporte de RUNES. Todos los cálculos están anclados a fecha_evaluacion.
    Retorna (reporte_runes, reporte_run_life, verificaciones).
    """
    if fecha_evaluacion is None:
        try:
            if df_forma9 is not None and 'FECHA_FORMA9' in df_forma9.columns:
                tmp = pd.to_datetime(df_forma9['FECHA_FORMA9'], errors='coerce')
                if not tmp.dropna().empty:
                    fecha_evaluacion = tmp.max()
        except Exception:
            fecha_evaluacion = None

    fecha_evaluacion = pd.to_datetime(fecha_evaluacion).normalize()

    df_bd['FECHA_PULL_DATE']  = pd.to_datetime(df_bd['FECHA_PULL'],  errors='coerce')
    df_bd['FECHA_FALLA_DATE'] = pd.to_datetime(df_bd['FECHA_FALLA'], errors='coerce')
    df_bd['FECHA_RUN_DATE']   = pd.to_datetime(df_bd['FECHA_RUN'],   errors='coerce')

    df_bd_eval = df_bd[df_bd['FECHA_RUN_DATE'].dt.normalize() <= fecha_evaluacion].copy()

    extraidos_count  = df_bd_eval[df_bd_eval['FECHA_PULL_DATE'].dt.normalize() <= fecha_evaluacion].shape[0]
    running_count    = df_bd_eval[
        (df_bd_eval['FECHA_RUN_DATE'].dt.normalize() <= fecha_evaluacion) &
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.normalize() > fecha_evaluacion))
    ].shape[0]
    fallados_count   = df_bd_eval[
        (df_bd_eval['FECHA_FALLA_DATE'].dt.normalize() <= fecha_evaluacion) &
        (df_bd_eval['FECHA_PULL_DATE'].isna() | (df_bd_eval['FECHA_PULL_DATE'].dt.normalize() > fecha_evaluacion))
    ].shape[0]
    pozos_operativos = df_bd_eval[
        (df_bd_eval['FECHA_FALLA_DATE'].isna() | (df_bd_eval['FECHA_FALLA_DATE'].dt.normalize() > fecha_evaluacion)) &
        (df_bd_eval['FECHA_PULL_DATE'].isna()  | (df_bd_eval['FECHA_PULL_DATE'].dt.normalize()  > fecha_evaluacion))
    ].shape[0]

    df_forma9_eval = df_forma9[
        (df_forma9['FECHA_FORMA9'].dt.normalize() >= (fecha_evaluacion - pd.Timedelta(days=30))) &
        (df_forma9['FECHA_FORMA9'].dt.normalize() <= fecha_evaluacion)
    ]
    pozos_on  = df_forma9_eval[df_forma9_eval['DIAS TRABAJADOS'] > 0]['POZO'].nunique()
    pozos_off = abs(pozos_operativos - pozos_on)
    totales_count = extraidos_count + running_count

    reporte_runes = pd.DataFrame({
        'Categoría': ['Extraídos', 'En Fondo', 'Fallados', 'Pozos ON', 'Pozos OFF', 'Pozos Operativos', 'Totales'],
        'Conteo':    [extraidos_count, running_count, fallados_count, pozos_on, pozos_off, pozos_operativos, totales_count],
    })

    verificaciones = {
        'On + Off = Operativos':          pozos_on + pozos_off == pozos_operativos,
        'Fallados + Operativos = En Fondo': fallados_count + pozos_operativos == running_count,
        'En Fondo + Extraídos = Totales': running_count + extraidos_count == totales_count,
    }

    mask_ended_eval = (
        ((df_bd_eval['FECHA_PULL_DATE'].notna())  & (df_bd_eval['FECHA_PULL_DATE'].dt.normalize()  <= fecha_evaluacion)) |
        ((df_bd_eval['FECHA_FALLA_DATE'].notna()) & (df_bd_eval['FECHA_FALLA_DATE'].dt.normalize() <= fecha_evaluacion))
    )
    run_life_apagados_fallados = df_bd_eval[mask_ended_eval]['RUN LIFE'].mean()
    run_life_general           = df_bd_eval['RUN LIFE'].mean()

    reporte_run_life = pd.DataFrame({
        'Categoría': ['Tiempo de Vida Promedio (Fallados+Ext)', 'Tiempo de vida General'],
        'Valor':     [run_life_apagados_fallados, run_life_general],
    })

    try:
        run_life_efectivo_val, df_rle_result = calcular_run_life_efectivo(df_bd_eval, df_forma9, fecha_evaluacion)
        rle_fallados_val = (
            df_rle_result[mask_ended_eval]['RUN_LIFE_EFECTIVO'].mean()
            if not df_rle_result[mask_ended_eval].empty else 0.0
        )
        reporte_run_life = pd.concat([
            reporte_run_life,
            pd.DataFrame({
                'Categoría': ['Tiempo de vida Efectivo (TODOS)', 'Tiempo de vida efectivo de equipos fallados'],
                'Valor':     [run_life_efectivo_val, rle_fallados_val],
            }),
        ], ignore_index=True)
    except Exception as e:
        print(f"[WARNING] No se pudo agregar Run Life Efectivo al reporte: {e}")

    return reporte_runes, reporte_run_life, verificaciones


# ===========================================================================
# 5. HISTÓRICO RUN LIFE POR ACTIVO
# ===========================================================================

@st.cache_data(show_spinner="Calculando histórico de Run Life...")
def generar_historico_run_life(df_bd_calculated, fecha_evaluacion):
    """
    Calcula el run life promedio mensual acumulado por ACTIVO.
    Considera todos los RUNs FALLADOS o FINALIZADOS (Pull) hasta el cierre de cada mes.
    Retorna DataFrame con columnas ['Mes', 'ACTIVO', 'Tiempo Op. Promedio'].
    """
    end_date   = pd.to_datetime(fecha_evaluacion)
    start_date = end_date - timedelta(days=365 * 3)
    meses      = pd.date_range(start=start_date, end=end_date, freq='MS')
    historico  = []

    df_bd = df_bd_calculated.copy()
    df_bd['FECHA_PULL_DT']  = pd.to_datetime(df_bd.get('FECHA_PULL'),  errors='coerce') if 'FECHA_PULL'  in df_bd.columns else pd.NaT
    df_bd['FECHA_FALLA_DT'] = pd.to_datetime(df_bd.get('FECHA_FALLA'), errors='coerce') if 'FECHA_FALLA' in df_bd.columns else pd.NaT

    if 'RUN LIFE' not in df_bd.columns:
        df_bd['RUN LIFE'] = np.where(
            df_bd['FECHA_FALLA_DT'].notna(),
            (df_bd['FECHA_FALLA_DT'] - pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')).dt.days,
            np.where(
                df_bd['FECHA_PULL_DT'].notna(),
                (df_bd['FECHA_PULL_DT'] - pd.to_datetime(df_bd['FECHA_RUN'], errors='coerce')).dt.days,
                np.nan,
            ),
        )

    for mes in meses:
        fin_mes    = mes + pd.offsets.MonthEnd(0)
        mask_ended = (
            ((df_bd['FECHA_FALLA_DT'].notna()) & (df_bd['FECHA_FALLA_DT'] <= fin_mes)) |
            ((df_bd['FECHA_PULL_DT'].notna())  & (df_bd['FECHA_PULL_DT']  <= fin_mes))
        )
        ended_runs = df_bd[mask_ended].copy()

        if not ended_runs.empty:
            if 'ACTIVO' in ended_runs.columns:
                promedio = ended_runs.groupby('ACTIVO')['RUN LIFE'].mean().reset_index()
                promedio['Mes'] = fin_mes
                promedio.rename(columns={'RUN LIFE': 'Tiempo Op. Promedio'}, inplace=True)
                historico.append(promedio)
            else:
                val = ended_runs['RUN LIFE'].mean()
                historico.append(pd.DataFrame({'Mes': [fin_mes], 'ACTIVO': ['Global'], 'Tiempo Op. Promedio': [val]}))

    if historico:
        df_historico = pd.concat(historico, ignore_index=True)
        return df_historico[['Mes', 'ACTIVO', 'Tiempo Op. Promedio']]
    return pd.DataFrame(columns=['Mes', 'ACTIVO', 'Tiempo Op. Promedio'])


# ===========================================================================
# 6. UTILIDADES DE ESTILO (sin UI directa, usadas por tabs)
# ===========================================================================

def highlight_problema(s):
    """Función de estilo para filas con más de una falla (uso con df.style.apply)."""
    try:
        val = s.get('Cantidad de Fallas', 0)
        is_problema = float(val) > 1 if val is not None else False
    except (ValueError, TypeError):
        is_problema = False

    if is_problema:
        def _hex_to_rgb(h):
            h = h.lstrip('#')
            if len(h) == 6:
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            return (0, 0, 0)

        def _luminance(rgb_tuple):
            r_v, g_v, b_v = [c / 255.0 for c in rgb_tuple]
            def _adjust(v):
                return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
            return 0.2126 * _adjust(r_v) + 0.7152 * _adjust(g_v) + 0.0722 * _adjust(b_v)

        try:
            lum        = _luminance(_hex_to_rgb(COLOR_PRINCIPAL))
            text_color = tema.COLOR_NEGRO if lum > 0.5 else tema.COLOR_BLANCO
        except Exception:
            text_color = 'white'

        return [f'background-color: {COLOR_PRINCIPAL}; color: {text_color}; font-weight: bold;'] * len(s)
    return [''] * len(s)
