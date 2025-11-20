import pandas as pd
import matplotlib.pyplot as plt
import io
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils.dataframe import dataframe_to_rows
import tempfile

def exportar_excel_con_graficas(tablas: dict, graficas: dict) -> bytes:
    """
    Exporta un archivo Excel con varias hojas de tablas y gráficas.
    tablas: dict con nombre_hoja: DataFrame
    graficas: dict con nombre_hoja: figura matplotlib
    Devuelve el contenido binario del archivo Excel.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = list(tablas.keys())[0]
    # Agregar la primera tabla
    for r in dataframe_to_rows(tablas[ws.title], index=False, header=True):
        ws.append(r)
    # Agregar el resto de tablas
    for nombre, df in list(tablas.items())[1:]:
        ws2 = wb.create_sheet(title=nombre)
        for r in dataframe_to_rows(df, index=False, header=True):
            ws2.append(r)
    # Guardar gráficas como imágenes temporales y agregarlas
    for nombre, fig in graficas.items():
        img_path = tempfile.mktemp(suffix='.png')
        fig.savefig(img_path, bbox_inches='tight')
        ws_img = wb.create_sheet(title=f"Grafica_{nombre}")
        img = XLImage(img_path)
        img.width = 600
        img.height = 340
        ws_img.add_image(img, 'A1')
    # Guardar a bytes
    with io.BytesIO() as output:
        wb.save(output)
        return output.getvalue()

# Ejemplo de uso en Streamlit:
# import streamlit as st
# from descargar import exportar_excel_con_graficas
# if st.button('Descargar Reporte Completo'):
#     excel_bytes = exportar_excel_con_graficas({'Tabla1': df1, 'Tabla2': df2}, {'Graf1': fig1, 'Graf2': fig2})
#     st.download_button('Descargar Excel', data=excel_bytes, file_name='reporte_completo.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# ===================== GENERAR DIAPOSITIVAS CON IA =====================
import google.generativeai as genai
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN


def generar_diapositivas_ia(tablas: dict, resumen_kpis: dict, api_key: str, titulo: str = "Reporte de Indicadores ALS", graficas: dict = None) -> bytes:
    """
    Genera un archivo PowerPoint (.pptx) con resumen ejecutivo de los KPIs, tablas y gráficas usando IA de Google.
    tablas: dict de nombre_hoja: DataFrame
    resumen_kpis: dict de nombre_kpi: valor
    graficas: dict de nombre_grafica: figura matplotlib o ruta a imagen
    api_key: clave de API de Google Generative AI
    Devuelve el contenido binario del archivo pptx.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

    prs = Presentation()
    # Portada
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = titulo
    slide.placeholders[1].text = "Reporte generado automáticamente con IA"

    # Slide de KPIs principales
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "KPIs Principales"
    tf = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(8.5), Inches(4)).text_frame
    for k, v in resumen_kpis.items():
        p = tf.add_paragraph()
        p.text = f"{k}: {v}"
        p.font.size = Pt(20)
    tf.paragraphs[0].font.bold = True

    # Slide de resumen IA
    prompt = f"Resume en máximo 5 puntos los hallazgos clave de los siguientes KPIs y tablas: {resumen_kpis}. Usa lenguaje ejecutivo y claro."
    try:
        response = model.generate_content(prompt)
        resumen_ia = response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        resumen_ia = f"No se pudo generar resumen IA: {e}"
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Resumen Ejecutivo IA"
    slide.placeholders[1].text = resumen_ia

    # Slides para cada tabla
    for nombre, df in tablas.items():
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = f"Tabla: {nombre}"
        tf = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(8.5), Inches(4)).text_frame
        tf.word_wrap = True
        preview = df.head(10).to_string(index=False)
        for line in preview.split('\n'):
            p = tf.add_paragraph()
            p.text = line
            p.font.size = Pt(12)

    # Slides para gráficas
    if graficas:
        for nombre, fig in graficas.items():
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = f"Gráfica: {nombre}"
            # Guardar la figura como imagen temporal si es matplotlib o plotly
            import tempfile, os
            img_path = None
            try:
                if hasattr(fig, 'savefig'):
                    # matplotlib
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                        fig.savefig(tmpfile.name, bbox_inches='tight')
                        img_path = tmpfile.name
                elif hasattr(fig, 'write_image'):
                    # plotly
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
                        fig.write_image(tmpfile.name)
                        img_path = tmpfile.name
                elif isinstance(fig, str) and os.path.exists(fig):
                    img_path = fig
                if img_path:
                    left = Inches(1)
                    top = Inches(1.5)
                    slide.shapes.add_picture(img_path, left, top, width=Inches(7))
                    os.remove(img_path)
            except Exception as e:
                tf = slide.shapes.add_textbox(Inches(0.5), Inches(2), Inches(8.5), Inches(1)).text_frame
                tf.text = f"No se pudo mostrar la gráfica: {e}"

    output = io.BytesIO()
    prs.save(output)
    return output.getvalue()
