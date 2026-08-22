"""
upload_ui.py
============
Sección de carga de archivos: FORMA 9, BD, parámetros.
Diseñado para funcionar en POPOVER del sidebar (compacto) y modo página.
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


# CSS solo para componentes dentro del popover/sidebar
POPOVER_CSS = """
<style>
/* Cards compactas para popover */
.pop-card {
    background: #ffffff;
    border: 1px solid rgba(19, 118, 89, 0.12);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
}
.pop-card.has-file { border-color: #137659; }
.pop-card.error { border-color: #c62828; }

.pop-header {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 6px;
}
.pop-icon {
    width: 26px; height: 26px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; flex-shrink: 0;
}
.pop-icon.f9 { background: rgba(19,118,89,0.1); color: #137659; }
.pop-icon.bd { background: rgba(192,156,46,0.1); color: #c09c2e; }
.pop-icon.params { background: rgba(2,132,199,0.1); color: #0284c7; }

.pop-title { font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 0.6rem; color: #1f221e; text-transform: uppercase; letter-spacing: 0.6px; }

/* Drop zone compacta */
.pop-drop {
    border: 2px dashed rgba(19, 118, 89, 0.2);
    border-radius: 8px;
    padding: 10px 8px;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    background: rgba(19,118,89,0.02);
    margin-bottom: 6px;
}
.pop-drop:hover { border-color: #137659; background: rgba(19,118,89,0.04); }
.pop-drop.has-file { border-color: #137659; border-style: solid; background: rgba(19,118,89,0.03); }
.pop-drop.error { border-color: #c62828; background: rgba(198,40,40,0.03); }

.pop-drop-text { font-family: 'Montserrat', sans-serif; font-size: 0.62rem; color: #1f221e; font-weight: 700; }
.pop-drop-hint { font-family: 'Inter', sans-serif; font-size: 0.55rem; color: #8a8d88; margin-top: 2px; }

/* Badge estado archivo */
.pop-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 8px; border-radius: 16px;
    font-family: 'Montserrat', sans-serif; font-size: 0.5rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.4px;
    margin-top: 4px;
}
.pop-badge.local { background: rgba(19,118,89,0.1); color: #137659; }
.pop-badge.online { background: rgba(192,156,46,0.1); color: #c09c2e; }
.pop-badge.error { background: rgba(198,40,40,0.1); color: #c62828; }

/* URL input */
.pop-url-label { font-family: 'Montserrat', sans-serif; font-size: 0.5rem; color: #5b5c55; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 3px; display: block; }

/* Date inputs compactos */
.pop-date-row { display: flex; gap: 6px; margin-top: 6px; }
.pop-date-field { flex: 1; }
.pop-date-field .stDateInput > div { padding: 0 !important; }

/* Range display */
.pop-range {
    margin-top: 8px; padding: 6px 10px;
    background: rgba(19,118,89,0.05); border: 1px solid rgba(19,118,89,0.08);
    border-radius: 6px; font-family: 'Montserrat', sans-serif;
    font-size: 0.6rem; font-weight: 700; color: #137659; text-align: center;
    letter-spacing: 0.4px;
}

/* Botón calcular */
.pop-calc-btn { margin-top: 10px; }
.pop-calc-btn button {
    background: linear-gradient(135deg, #137659 0%, #0a4d34 100%) !important;
    border: none !important; color: #fff !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.6rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.8px !important;
    padding: 8px 0 !important; border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(19,118,89,0.2) !important;
}
.pop-calc-btn button:disabled { opacity: 0.5 !important; cursor: not-allowed !important; }

/* Export button */
.pop-export-btn { margin-top: 8px; }
.pop-export-btn button {
    background: rgba(19,118,89,0.06) !important;
    border: 1px solid rgba(19,118,89,0.2) !important;
    color: #137659 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.55rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
    padding: 6px 0 !important; border-radius: 6px !important;
}
.pop-export-btn button:hover { background: #137659 !important; color: #fff !important; }

/* Fix popover width */
section[data-testid="stSidebar"] div[data-testid="stPopover"] > div {
    min-width: 320px !important;
}
</style>
"""


def _file_badge(source_type: str, filename: str = ""):
    if source_type == "local":
        return f'<span style="display:inline-flex;align-items:center;gap:4px;padding:2px 6px;border-radius:12px;font-family:Montserrat,sans-serif;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.3px;background:rgba(19,118,89,0.1);color:#137659;">LOCAL: {filename}</span>'
    elif source_type == "online":
        return f'<span style="display:inline-flex;align-items:center;gap:4px;padding:2px 6px;border-radius:12px;font-family:Montserrat,sans-serif;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.3px;background:rgba(192,156,46,0.1);color:#c09c2e;">ONEDRIVE: {filename}</span>'
    elif source_type == "error":
        return f'<span style="display:inline-flex;align-items:center;gap:4px;padding:2px 6px;border-radius:12px;font-family:Montserrat,sans-serif;font-size:0.48rem;font-weight:700;text-transform:uppercase;letter-spacing:0.3px;background:rgba(198,40,40,0.1);color:#c62828;">ERROR: {filename}</span>'
    return ""


def render_upload_section(sidebar: bool = False):
    """
    Renderiza la sección de carga en POPOVER del sidebar.
    Estados: vacío, local, online, error.
    """
    ctx = st.sidebar if sidebar else st

    # Inyectar CSS una vez
    ctx.markdown(POPOVER_CSS, unsafe_allow_html=True)

    # Estado actual — siempre leer de st.session_state (st.sidebar no lo tiene)
    f9_local = st.session_state.get('forma9_file')
    f9_url   = st.session_state.get('url_forma9_excel', '')
    bd_local = st.session_state.get('bd_file')
    bd_url   = st.session_state.get('url_bd_excel', '')

    f9_source = None
    f9_name = ""
    if f9_local:
        f9_source, f9_name = "local", getattr(f9_local, 'name', 'archivo')
    elif f9_url:
        f9_source, f9_name = "online", "OneDrive"

    bd_source = None
    bd_name = ""
    if bd_local:
        bd_source, bd_name = "local", getattr(bd_local, 'name', 'archivo')
    elif bd_url:
        bd_source, bd_name = "online", "OneDrive"

    f9_final   = f9_local if f9_local else st.session_state.get('forma9_online_file')
    bd_final   = bd_local if bd_local else st.session_state.get('bd_online_file')
    both_ready = bool(f9_final and bd_final)


    # ── TARJETA 1: FORMA 9 ──────────────────────────────────────────────────
    with ctx.container():
        ctx.markdown(f"""
        <div class="pop-card {'has-file' if f9_source else ''}">
            <div class="pop-header">
                <div class="pop-icon f9">F9</div>
                <div class="pop-title">FORMA 9</div>
            </div>
            <div class="pop-drop {'has-file' if f9_source else ''}">
                <div class="pop-drop-text">FORMA 9</div>
                <div class="pop-drop-hint">.csv / .xlsx · Arrastra o usa URL</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # File uploader (oculto visualmente, funcional)
        f9_file = ctx.file_uploader("Subir F9", type=["csv", "xlsx"], key="forma9_file", label_visibility="collapsed")
        
        # Badge estado
        if f9_source:
            ctx.markdown(f'<div style="margin-top:4px;">{_file_badge(f9_source, f9_name)}</div>', unsafe_allow_html=True)

        # URL OneDrive
        url_f9 = ctx.text_input(
            "URL OneDrive", key="url_forma9_excel",
            value="https://1drv.ms/x/c/06cc4035ad46ff97/IQAlCua1BGOXRbcSzUY0OVyzAS8KOoDNxuvUqrsORhjMcKM?e=o8FZyJ",
            placeholder="https://1drv.ms/...", label_visibility="collapsed"
        )
        if url_f9 and not f9_local:
            fname = cached_onedrive_download(url_f9, 'forma9_online.xlsx')
            if fname:
                st.session_state['forma9_online_file'] = fname
            else:
                ctx.error("❌ Error descargando F9")

    ctx.markdown('<div style="margin:6px 0;"></div>', unsafe_allow_html=True)

    # ── TARJETA 2: BASE DE DATOS ───────────────────────────────────────────
    with ctx.container():
        bd_source = None
        bd_name = ""
        if bd_local:
            bd_source, bd_name = "local", getattr(bd_local, 'name', 'archivo')
        elif bd_url:
            bd_source, bd_name = "online", "OneDrive"

        ctx.markdown(f"""
        <div class="pop-card {'has-file' if bd_source else ''}">
            <div class="pop-header">
                <div class="pop-icon bd">BD</div>
                <div class="pop-title">BASE DE DATOS</div>
            </div>
            <div class="pop-drop {'has-file' if bd_source else ''}">
                <div class="pop-drop-text">BASE DE DATOS</div>
                <div class="pop-drop-hint">.csv / .xlsx · Arrastra o usa URL</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bd_file = ctx.file_uploader("Subir BD", type=["csv", "xlsx"], key="bd_file", label_visibility="collapsed")

        if bd_source:
            ctx.markdown(f'<div style="margin-top:4px;">{_file_badge(bd_source, bd_name)}</div>', unsafe_allow_html=True)

        url_bd = ctx.text_input(
            "URL OneDrive", key="url_bd_excel",
            value="https://1drv.ms/x/c/06cc4035ad46ff97/IQBFUqV7GWUfTqIPciLZeNEIAdlrMygqQITAR9Ku5frPrZE?e=P0xf75",
            placeholder="https://1drv.ms/...", label_visibility="collapsed"
        )
        if url_bd and not bd_local:
            fname = cached_onedrive_download(url_bd, 'bd_online.xlsx')
            if fname:
                st.session_state['bd_online_file'] = fname
            else:
                ctx.error("❌ Error descargando BD")

    ctx.markdown('<div style="margin:6px 0;"></div>', unsafe_allow_html=True)

    # ── TARJETA 3: PARÁMETROS ──────────────────────────────────────────────
    default_date = datetime.now().date().replace(day=1) - timedelta(days=1)
    default_start = default_date - timedelta(days=365)

    f_ini  = ctx.date_input("FECHA INICIO",       value=st.session_state.get('fecha_ini_input', default_start), key="fecha_ini_input", max_value=datetime.now().date())
    f_eval = ctx.date_input("FECHA EVALUACIÓN",   value=st.session_state.get('fecha_eval', default_date),      key="fecha_eval",      max_value=datetime.now().date())

    ctx.markdown(f'<div class="pop-range">{f_ini.strftime("%d %b %Y").upper()} — {f_eval.strftime("%d %b %Y").upper()}</div>', unsafe_allow_html=True)

    # ── BOTÓN CALCULAR ─────────────────────────────────────────────────────
    f9_f  = f9_local if f9_local else st.session_state.get('forma9_online_file')
    bd_f  = bd_local if bd_local else st.session_state.get('bd_online_file')
    ready = bool(f9_f and bd_f)

    calc = ctx.button("EJECUTAR CÁLCULOS" if ready else "CARGAR AMBOS", key="calcular_btn", use_container_width=True, disabled=not ready)

    # ── EXPORTAR ───────────────────────────────────────────────────────────
    df_m = st.session_state.get('df_monthly_summary')
    if df_m is not None and not df_m.empty:
        ctx.markdown('<div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(19,118,89,0.1);"></div>', unsafe_allow_html=True)
        xb = exportar_resumen_performance(df_m)
        if xb:
            ctx.download_button("DESCARGAR PERFORMANCE (.XLSX)", data=xb, file_name=f"ALS_Performance_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="btn_dl_excel_pop", use_container_width=True)

    # ── LÓGICA CÁLCULO ─────────────────────────────────────────────────────
    if calc and ready:
        f9_in = normalize_file(f9_f)
        bd_in = normalize_file(bd_f)
        if f9_in is None or bd_in is None:
            ctx.error("No se pudo procesar los archivos.")
        else:
            try:
                f9_raw, bd_raw = cargar_y_limpiar_datos(f9_in, bd_in)
                if f9_raw is None or bd_raw is None:
                    ctx.error("Lectura/limpieza falló.")
                else:
                    with ctx.spinner("Calculando indicadores..."):
                        f9_calc, bd_calc = perform_initial_calculations(f9_raw, bd_raw, f_eval)
                        df_trab, rep_f = calcular_indicadores_finales(f9_calc, bd_calc)
                        rep_r, hist_rl, verif = generar_reporte_completo(bd_calc, f9_calc, f_eval)
                        save_cached_data(bd_calc, f9_calc, f_eval, rep_r, hist_rl, rep_f, fecha_ini=f_ini)
                        ctx.toast("✅ Datos guardados en caché")

                        st.session_state.update({
                            'df_forma9_raw': f9_raw, 'df_bd_raw': bd_raw,
                            'df_bd_calculated': bd_calc, 'df_forma9_calculated': f9_calc,
                            'fecha_evaluacion_state': f_eval, 'fecha_inicio_state': f_ini,
                            'reporte_runes': rep_r, 'historico_run_life': hist_rl,
                            'reporte_fallas': rep_f, 'df_trabajo': df_trab, 'verificaciones': verif,
                            'unique_als': sorted(bd_calc['ALS'].dropna().unique().tolist()) if 'ALS' in bd_calc.columns else [],
                            'unique_activos': sorted(bd_calc['ACTIVO'].dropna().unique().tolist()) if 'ACTIVO' in bd_calc.columns else [],
                        })
                        show_success_box("Cálculos finalizados correctamente.")
                        ctx.rerun()
            except Exception as e:
                ctx.error(f"Error: {e}")