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
# La funcionalidad de generación de diapositivas con IA ha sido eliminada.
# Si necesitas exportar a PowerPoint en el futuro, podemos agregar una
# función limpia que use `python-pptx` sin dependencias de IA.
