"""
upload_ui.py
============
Sección de carga de archivos profesional: FORMA 9, BD, parámetros.
Estados visuales claros, drag-and-drop feel, validación en tiempo real.
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
from descargar import exportar_resumen_performance
from ui.theme import get_semantic_color


def get_last_day_of_previous_month():
    """Retorna el último día del mes anterior a hoy."""
    today = datetime.now().date()
    return today.replace(day=1) - timedelta(days=1)


# Colores semánticos
GREEN = get_semantic_color("success")
GOLD  = get_semantic_color("warning")
RED   = get_semantic_color("danger")
BLUE  = get_semantic_color("info")
MUTED = "#6b7a6f"


UPLOAD_CSS = """
<style>
/* Upload cards */
.upload-card {
    background: #ffffff;
    border: 1px solid rgba(19, 118, 89, 0.15);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.upload-card:hover {
    border-color: rgba(19, 118, 89, 0.3);
    box-shadow: 0 2px 12px rgba(19,118,89,0.06);
}
.upload-card.has-file {
    border-color: #137659;
    background: linear-gradient(180deg, rgba(19,118,89,0.02) 0%, #ffffff 100%);
}
.upload-card.error {
    border-color: #c62828;
    background: linear-gradient(180deg, rgba(198,40,40,0.02) 0%, #ffffff 100%);
}

.upload-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.upload-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
}
.upload-icon.f9 { background: rgba(19,118,89,0.1); color: #137659; }
.upload-icon.bd { background: rgba(192,156,46,0.1); color: #c09c2e; }
.upload-icon.params { background: rgba(2,132,199,0.1); color: #0284c7; }

.upload-title { font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 0.7rem; color: #1f221e; text-transform: uppercase; letter-spacing: 0.8px; }
.upload-subtitle { font-family: 'Inter', sans-serif; font-size: 0.6rem; color: #6b7a6f; margin-top: 1px; }

/* Drop zone */
.drop-zone {
    border: 2px dashed rgba(19, 118, 89, 0.25);
    border-radius: 10px;
    padding: 16px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    background: rgba(19,118,89,0.02);
    position: relative;
}
.drop-zone:hover, .drop-zone.drag-over {
    border-color: #137659;
    border-style: solid;
    background: rgba(19,118,89,0.06);
}
.drop-zone.has-file {
    border-color: #137659;
    border-style: solid;
    background: rgba(19,118,89,0.04);
}
.drop-zone.error {
    border-color: #c62828;
    background: rgba(198,40,40,0.04);
}

.drop-text { font-family: 'Montserrat', sans-serif; font-size: 0.7rem; color: #5b5c55; font-weight: 600; }
.drop-hint { font-family: 'Inter', sans-serif; font-size: 0.6rem; color: #8a8d88; margin-top: 4px; }

/* File status badge */
.file-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 10px; border-radius: 20px;
    font-family: 'Montserrat', sans-serif; font-size: 0.55rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-top: 8px;
}
.file-badge.local { background: rgba(19,118,89,0.1); color: #137659; }
.file-badge.online { background: rgba(192,156,46,0.1); color: #c09c2e; }
.file-badge.error { background: rgba(198,40,40,0.1); color: #c62828; }

/* URL Input */
.url-input-group { margin-top: 10px; }
.url-label { font-family: 'Montserrat', sans-serif; font-size: 0.55rem; color: #5b5c55; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; display: block; }
.url-input-wrap { position: relative; }
.url-input-wrap input { padding-right: 36px !important; }
.url-status { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); font-size: 14px; }

/* Date inputs */
.date-row { display: flex; gap: 10px; margin-top: 8px; }
.date-field { flex: 1; }
.date-field label { font-family: 'Montserrat', sans-serif; font-size: 0.55rem; color: #5b5c55; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; display: block; margin-bottom: 3px; }
.date-field .stDateInput { margin: 0 !important; }

/* Range display */
.range-display {
    margin-top: 10px; padding: 8px 12px;
    background: rgba(19,118,89,0.05); border: 1px solid rgba(19,118,89,0.1);
    border-radius: 8px; font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem; font-weight: 700; color: #137659; text-align: center;
    letter-spacing: 0.5px;
}

/* Action button */
.calc-btn { margin-top: 14px !important; }
.calc-btn button {
    background: linear-gradient(135deg, #137659 0%, #0a4d34 100%) !important;
    border: none !important; color: #fff !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.65rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
    padding: 10px 0 !important; border-radius: 8px !important;
    box-shadow: 0 4px 16px rgba(19,118,89,0.25) !important;
    transition: all 0.2s !important;
}
.calc-btn button:hover { box-shadow: 0 6px 24px rgba(19,118,89,0.35) !important; transform: translateY(-1px) !important; }
.calc-btn button:disabled { opacity: 0.6 !important; cursor: not-allowed !important; }

/* Export button */
.export-btn { margin-top: 10px; }
.export-btn button {
    background: rgba(19,118,89,0.08) !important;
    border: 1px solid rgba(19,118,89,0.3) !important;
    color: #137659 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.6rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important;
    padding: 8px 0 !important; border-radius: 8px !important;
    transition: all 0.2s !important;
}
.export-btn button:hover { background: #137659 !important; color: #fff !important; }

/* Progress/Toast */
.upload-toast { margin-top: 8px; }
</style>
"""


def _file_status_badge(source_type: str, filename: str = ""):
    """Genera badge de estado del archivo."""
    if source_type == "local":
        return f'<span class="file-badge local">LOCAL: {filename}</span>'
    elif source_type == "online":
        return f'<span class="file-badge online">ONEDRIVE: {filename}</span>'
    elif source_type == "error":
        return f'<span class="file-badge error">ERROR: {filename}</span>'
    return ""


def _render_card(icon_class: str, title: str, subtitle: str, content_html: str) -> str:
    return f"""
    <div class="upload-card">
        <div class="upload-header">
            <div class="upload-icon {icon_class}">{icon_class[-2:].upper()}</div>
            <div>
                <div class="upload-title">{title}</div>
                <div class="upload-subtitle">{subtitle}</div>
            </div>
        </div>
        {content_html}
    </div>
    """


def render_upload_section(sidebar: bool = False):
    """
    Renderiza la sección de carga con 3 tarjetas: FORMA 9, BD, Parámetros.
    Estados visuales: vacío, local, online, error.
    """
    st.markdown(UPLOAD_CSS, unsafe_allow_html=True)

    # Estado actual de archivos en session_state
    f9_local = st.session_state.get('forma9_file')
    f9_url = st.session_state.get('url_forma9_excel', '')
    bd_local = st.session_state.get('bd_file')
    bd_url = st.session_state.get('url_bd_excel', '')

    # Determinar qué archivo se usará (prioridad: local > online)
    f9_source = None
    f9_name = ""
    if f9_local:
        f9_source = "local"
        f9_name = getattr(f9_local, 'name', 'archivo_local')
    elif f9_url:
        f9_source = "online"
        f9_name = "OneDrive"

    bd_source = None
    bd_name = ""
    if bd_local:
        bd_source = "local"
        bd_name = getattr(bd_local, 'name', 'archivo_local')
    elif bd_url:
        bd_source = "online"
        bd_name = "OneDrive"

    both_ready = bool(f9_source and bd_source)

    # ── Tarjeta 1: FORMA 9 ────────────────────────────────────────────────────
    f9_content = f"""
    <div class="drop-zone {'has-file' if f9_source else ''} {'error' if f9_source == 'error' else ''}" id="drop-f9">
        <div class="drop-text">FORMA 9</div>
        <div class="drop-hint">Arrastra archivo .csv o .xlsx<br/>o usa URL OneDrive abajo</div>
    </div>
    """
    if f9_source:
        f9_content += f"""
        <div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
            {_file_status_badge(f9_source, f9_name)}
            <button onclick="document.getElementById('drop-f9').querySelector('input[type=file]').value = ''; this.parentElement.querySelector('.file-badge').remove();" style="background:none;border:none;color:#6b7a6f;font-size:0.6rem;text-decoration:underline;cursor:pointer;">Quitar</button>
        </div>
        """
    
    # File uploader (invisible, triggered by drop zone click)
    forma9_file = st.file_uploader(
        "Subir FORMA 9", type=["csv", "xlsx"], key="forma9_file",
        label_visibility="collapsed", accept_multiple_files=False
    )
    
    # URL OneDrive
    url_forma9 = st.text_input(
        "URL OneDrive", key="url_forma9_excel",
        value="https://1drv.ms/x/c/06cc4035ad46ff97/IQAlCua1BGOXRbcSzUY0OVyzAS8KOoDNxuvUqrsORhjMcKM?e=o8FZyJ",
        placeholder="https://1drv.ms/...",
        help="Pega el enlace compartido de OneDrive",
        label_visibility="collapsed"
    )
    if url_forma9 and not f9_local:
        fname = cached_onedrive_download(url_forma9, 'forma9_online.xlsx')
        if fname:
            st.session_state['forma9_online_file'] = fname
        else:
            st.error("❌ Error descargando FORMA 9 desde OneDrive")

    st.sidebar.markdown(_render_card("f9", "FORMA 9", "Producción diaria · Días trabajados", f9_content), unsafe_allow_html=True)

    st.sidebar.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)

    # ── Tarjeta 2: BASE DE DATOS ─────────────────────────────────────────────
    bd_content = f"""
    <div class="drop-zone {'has-file' if bd_source else ''} {'error' if bd_source == 'error' else ''}" id="drop-bd">
        <div class="drop-text">BASE DE DATOS</div>
        <div class="drop-hint">Arrastra archivo .csv o .xlsx<br/>o usa URL OneDrive abajo</div>
    </div>
    """
    if bd_source:
        bd_content += f"""
        <div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">
            {_file_status_badge(bd_source, bd_name)}
            <button onclick="document.getElementById('drop-bd').querySelector('input[type=file]').value = ''; this.parentElement.querySelector('.file-badge').remove();" style="background:none;border:none;color:#6b7a6f;font-size:0.6rem;text-decoration:underline;cursor:pointer;">Quitar</button>
        </div>
        """

    bd_file = st.file_uploader(
        "Subir BD", type=["csv", "xlsx"], key="bd_file",
        label_visibility="collapsed", accept_multiple_files=False
    )

    url_bd = st.text_input(
        "URL OneDrive", key="url_bd_excel",
        value="https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=P0xf75",
        placeholder="https://1drv.ms/...",
        help="Pega el enlace compartido de OneDrive",
        label_visibility="collapsed"
    )
    if url_bd and not bd_local:
        fname = cached_onedrive_download(url_bd, 'bd_online.xlsx')
        if fname:
            st.session_state['bd_online_file'] = fname
        else:
            st.error("❌ Error descargando BD desde OneDrive")

    st.sidebar.markdown(_render_card("bd", "BASE DE DATOS", "Histórico corridas · Fallas · Pulls", bd_content), unsafe_allow_html=True)

    st.sidebar.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)

    # ── Tarjeta 3: PARÁMETROS ────────────────────────────────────────────────
    default_date = get_last_day_of_previous_month()
    default_start_date = default_date - timedelta(days=365)

    fecha_inicio = st.sidebar.date_input(
        "FECHA INICIO",
        value=st.session_state.get('fecha_ini_input', default_start_date),
        key="fecha_ini_input",
        max_value=datetime.now().date(),
        label_visibility="visible"
    )

    fecha_evaluacion = st.sidebar.date_input(
        "FECHA EVALUACIÓN",
        value=st.session_state.get('fecha_eval', default_date),
        key="fecha_eval",
        max_value=datetime.now().date(),
        label_visibility="visible"
    )

    st.sidebar.markdown(f"""
    <div class="range-display">
        {fecha_inicio.strftime('%d %b %Y').upper()} — {fecha_evaluacion.strftime('%d %b %Y').upper()}
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<div style="margin-top: 14px;"></div>', unsafe_allow_html=True)

    # ── Botón Calcular ───────────────────────────────────────────────────────
    f9_final = f9_local if f9_local else st.session_state.get('forma9_online_file')
    bd_final = bd_local if bd_local else st.session_state.get('bd_online_file')
    both_ready = bool(f9_final and bd_final)

    calcular_btn = st.sidebar.button(
        "EJECUTAR CÁLCULOS" if both_ready else "CARGAR AMBOS ARCHIVOS",
        key="calcular_btn", use_container_width=True,
        disabled=not both_ready
    )

    # ── Exportar (solo si hay datos) ─────────────────────────────────────────
    df_monthly = st.session_state.get('df_monthly_summary')
    if df_monthly is not None and not df_monthly.empty:
        st.sidebar.markdown('<div style="margin-top: 16px; padding-top: 12px; border-top: 1px solid rgba(19,118,89,0.1);"></div>', unsafe_allow_html=True)
        excel_bytes = exportar_resumen_performance(df_monthly)
        if excel_bytes:
            st.sidebar.download_button(
                label="DESCARGAR PERFORMANCE (.XLSX)",
                data=excel_bytes,
                file_name=f"ALS_Performance_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_download_excel_discreet",
                use_container_width=True
            )

    # ── Lógica de Cálculo ────────────────────────────────────────────────────
    if calcular_btn and both_ready:
        f9_input = normalize_file(f9_final)
        bd_input = normalize_file(bd_final)

        if f9_input is None or bd_input is None:
            st.error("No se pudo procesar los archivos.")
        else:
            try:
                df_forma9_raw, df_bd_raw = cargar_y_limpiar_datos(f9_input, bd_input)
                if df_forma9_raw is None or df_bd_raw is None:
                    st.error("La lectura/limpieza de los archivos falló.")
                else:
                    with st.spinner("Calculando indicadores..."):
                        df_forma9_calc, df_bd_calc = perform_initial_calculations(
                            df_forma9_raw, df_bd_raw, fecha_evaluacion
                        )
                        df_trabajo, reporte_fallas = calcular_indicadores_finales(
                            df_forma9_calc, df_bd_calc
                        )
                        reporte_runes_final, historico_run_life, verificaciones = generar_reporte_completo(
                            df_bd_calc, df_forma9_calc, fecha_evaluacion
                        )

                        save_cached_data(
                            df_bd_calc, df_forma9_calc, fecha_evaluacion,
                            reporte_runes_final, historico_run_life, reporte_fallas,
                            fecha_ini=fecha_inicio
                        )
                        st.toast("✅ Datos guardados en caché para carga rápida")

                        st.session_state['df_forma9_raw']          = df_forma9_raw
                        st.session_state['df_bd_raw']              = df_bd_raw
                        st.session_state['df_bd_calculated']       = df_bd_calc
                        st.session_state['df_forma9_calculated']   = df_forma9_calc
                        st.session_state['fecha_evaluacion_state'] = fecha_evaluacion
                        st.session_state['fecha_inicio_state']     = fecha_inicio
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
                        st.rerun()
            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")