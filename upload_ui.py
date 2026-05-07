"""
upload_ui.py
============
Sección de carga de archivos: FORMA 9, BD, parámetros de evaluación
y botón de cálculo. Guarda resultados en st.session_state.
"""

from datetime import datetime, timedelta

import streamlit as st

from data_loader import (
    cached_onedrive_download,
    cargar_y_limpiar_datos,
    normalize_file,
    save_cached_data,
)
from calculations import (
    perform_initial_calculations,
    calcular_indicadores_finales,
    generar_reporte_completo,
)
from styles import show_success_box


def get_last_day_of_previous_month():
    """Retorna el último día del mes anterior a hoy."""
    today = datetime.now().date()
    return today.replace(day=1) - timedelta(days=1)


def render_upload_section():
    """
    Renderiza el expander de carga de archivos con sus 3 tarjetas:
    FORMA 9, BD y Parámetros de Evaluación.
    Gestiona toda la lógica del botón 'Calcular'.
    """
    # Determinar si expandir (sin datos calculados)
    expander_state = st.session_state.get('df_bd_calculated') is None

    with st.expander("📂 Carga de Archivos y Parámetros", expanded=expander_state):
        col_f9, col_bd, col_params = st.columns([1, 1, 1])

    # --- Tarjeta 1: FORMA 9 ---
    with col_f9:
        st.markdown("""
        <div class='compact-card'><span>Carga de FORMA 9 🗃️</span></div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='upload-area'>", unsafe_allow_html=True)
            forma9_file = st.file_uploader("FORMA 9 (.csv/.xlsx)", type=["csv", "xlsx"], key="forma9_file")
            st.markdown("</div>", unsafe_allow_html=True)
            url_forma9 = st.text_input(
                "URL F9", key="url_forma9_excel",
                value="https://1drv.ms/x/c/06cc4035ad46ff97/IQAlCua1BGOXRbcSzUY0OVyzAS8KOoDNxuvUqrsORhjMcKM?e=o8FZyJ",
                help="URL pública de FORMA 9 (OneDrive/SharePoint).",
            )
            forma9_online_file = None
            if url_forma9:
                fname = cached_onedrive_download(url_forma9, 'forma9_online.xlsx')
                if fname:
                    forma9_online_file = fname
                    show_success_box("F9 online descargada OK (Caché).")
                else:
                    st.error("F9 online error: No se pudo descargar el archivo desde OneDrive.")

    # --- Tarjeta 2: BD ---
    with col_bd:
        st.markdown("""
        <div class='compact-card'><span>Carga  Base de Datos 🗃️</span></div>
        """, unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='upload-area'>", unsafe_allow_html=True)
            bd_file = st.file_uploader("BD (.csv o .xlsx)", type=["csv", "xlsx"], key="bd_file")
            st.markdown("</div>", unsafe_allow_html=True)
            url_bd = st.text_input(
                "URL BD", key="url_bd_excel",
                value="https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=P0xf75",
                help="URL pública de BD (OneDrive/SharePoint).",
            )
            bd_online_file = None
            if url_bd:
                fname = cached_onedrive_download(url_bd, 'bd_online.xlsx')
                if fname:
                    bd_online_file = fname
                    show_success_box("BD online descargada OK (Caché).")
                else:
                    st.error("BD online error: No se pudo descargar el archivo desde OneDrive.")

    # --- Tarjeta 3: Parámetros ---
    with col_params:
        st.markdown("""
        <div class='compact-card'><span>Parámetros de Evaluación ⚙️</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <style>
        .fecha-alerta {
            padding:0.5rem 1rem; background-color:var(--secondary-background-color);
            border-radius:8px; margin-bottom:0.5rem; font-weight:700;
            color:var(--text-color); box-shadow:0 1px 3px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

        default_date = get_last_day_of_previous_month()

        with st.container(border=True):
            fecha_evaluacion = st.date_input(
                "🗓️ Fecha de Evaluación",
                value=default_date,
                key="fecha_eval",
                disabled=False,
                max_value=default_date,
            )
            try:
                fecha_formateada_num = fecha_evaluacion.strftime("%d-%m-%Y")
            except Exception:
                fecha_formateada_num = str(fecha_evaluacion)

            st.markdown("---")
            st.markdown(f"""
            <div class="fecha-alerta">
                <div><span>FECHA EVALUAR:</span> <b>{fecha_formateada_num}</b></div>
                <div style="margin-top:0.25rem;font-size:0.95rem;">No superar esta fecha.</div>
            </div>
            """, unsafe_allow_html=True)

            calcular_btn = st.button("🚀 Calcular Datos Iniciales", key="calcular_btn", use_container_width=True)

        # Determinar archivos finales
        forma9_final = forma9_file if forma9_file is not None else forma9_online_file
        bd_final     = bd_file     if bd_file     is not None else bd_online_file

        # --- Lógica de Cálculo ---
        if forma9_final and bd_final:
            show_success_box("¡Ambos archivos cargados!")
            if calcular_btn:
                forma9_input = normalize_file(forma9_final)
                bd_input     = normalize_file(bd_final)

                if forma9_input is None or bd_input is None:
                    st.error("No se pudo procesar los archivos.")
                else:
                    try:
                        df_forma9_raw, df_bd_raw = cargar_y_limpiar_datos(forma9_input, bd_input)
                        if df_forma9_raw is None or df_bd_raw is None:
                            st.error("La lectura/limpieza de los archivos falló.")
                        else:
                            df_forma9_calc, df_bd_calc = perform_initial_calculations(
                                df_forma9_raw, df_bd_raw, fecha_evaluacion
                            )
                            df_trabajo, reporte_fallas = calcular_indicadores_finales(
                                df_forma9_calc, df_bd_calc
                            )
                            reporte_runes_final, historico_run_life, verificaciones = generar_reporte_completo(
                                df_bd_calc, df_forma9_calc, fecha_evaluacion
                            )

                            # Guardar en caché y session_state
                            save_cached_data(
                                df_bd_calc, df_forma9_calc, fecha_evaluacion,
                                reporte_runes_final, historico_run_life, reporte_fallas,
                            )
                            st.toast("Datos guardados en caché para carga rápida", icon="💾")

                            st.session_state['df_forma9_raw']          = df_forma9_raw
                            st.session_state['df_bd_raw']              = df_bd_raw
                            st.session_state['df_bd_calculated']       = df_bd_calc
                            st.session_state['df_forma9_calculated']   = df_forma9_calc
                            st.session_state['fecha_evaluacion_state'] = fecha_evaluacion
                            st.session_state['reporte_runes']          = reporte_runes_final
                            st.session_state['historico_run_life']     = historico_run_life
                            st.session_state['reporte_fallas']         = reporte_fallas
                            st.session_state['df_trabajo']             = df_trabajo
                            st.session_state['verificaciones']         = verificaciones

                            st.session_state['unique_als'] = (
                                sorted(df_bd_calc['ALS'].dropna().unique().tolist())
                                if 'ALS' in df_bd_calc.columns else []
                            )
                            st.session_state['unique_activos'] = (
                                sorted(df_bd_calc['ACTIVO'].dropna().unique().tolist())
                                if 'ACTIVO' in df_bd_calc.columns else []
                            )
                            show_success_box("Cálculos finalizados correctamente.")
                    except Exception as e:
                        st.error(f"Error durante el procesamiento: {e}")
