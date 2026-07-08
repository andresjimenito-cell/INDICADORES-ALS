"""
Módulo de Exportación a PDF para INDICADORES ALS v3.2
Mejoras: Tema Claro (Light Mode), Código Robusto para generación de gráficas y Layout Compacto.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE COLORES ---
COLOR_TITULO = colors.HexColor('#1a1f3a')     
COLOR_ENCABEZADO_TABLA = colors.HexColor('#2C3E50')
COLOR_TEXTO_TABLA_HEAD = colors.white
COLOR_FILA_PAR = colors.HexColor('#F4F6F7')
COLOR_TEXTO_BODY = colors.HexColor('#2C3E50')

def plotly_to_image_bytes(fig, width=900, height=450, scale=3):
    """
    Convierte gráfica a 'Light Mode' garantizando visibilidad total (High Contrast).
    Reemplaza colores neón por paleta oscura de impresión.
    """
    try:
        if fig is None:
            return None
            
        img_fig = go.Figure(fig)
        
        # 1. Aplicar template base claro (resetea fondos oscuros y ejes)
        img_fig.update_layout(template='plotly_white')
        
        # 2. Ajustes de Fondo y Fuente Global
        negro = '#2C3E50'
        img_fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial", color=negro, size=14),
            margin=dict(l=40, r=40, t=50, b=40),
            autosize=False,
            width=width,
            height=height,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color=negro, size=12),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#bdc3c7',
                borderwidth=1
            )
        )

        # 3. Forzar estilo de Ejes (sin romper rangos ni configuraciones de doble eje)
        img_fig.update_xaxes(
            showgrid=True, gridcolor='#E5E8E8', zerolinecolor='#E5E8E8',
            title_font=dict(color=negro), tickfont=dict(color=negro),
            linecolor=negro
        )
        img_fig.update_yaxes(
            showgrid=True, gridcolor='#E5E8E8', zerolinecolor='#E5E8E8',
            title_font=dict(color=negro), tickfont=dict(color=negro),
            linecolor=negro
        )
        
        # 4. PALETA DE ALTO CONTRASTE (Para reemplazar neones)
        # Secuencia: Azul Fuerte, Naranja, Verde Oscuro, Púrpura, Rojo
        CONTRAST_PALETTE = ['#004d99', '#d35400', '#145a32', '#6c3483', '#c0392b', '#7f8c8d']
        
        # Re-colorear trazas secuencialmente para asegurar visibilidad
        for i, trace in enumerate(img_fig.data):
            try:
                # Obtener color de la paleta (ciclar si hay muchos)
                new_color = CONTRAST_PALETTE[i % len(CONTRAST_PALETTE)]
                
                # Forzar color en Líneas y Marcadores
                if hasattr(trace, 'line'):
                    # Respetar dash si existe, solo cambiar color y ancho
                    width = trace.line.width if hasattr(trace.line, 'width') and trace.line.width else 3
                    dash = trace.line.dash if hasattr(trace.line, 'dash') else 'solid'
                    trace.update(line=dict(color=new_color, width=width, dash=dash))
                    
                if hasattr(trace, 'marker'):
                    # Si tiene marcador, actualizarlo
                    trace.update(marker=dict(color=new_color))
                    # Caso especial para barras: quitar borde o ponerlo mismo color
                    if trace.type == 'bar':
                         trace.update(marker=dict(line=dict(color=new_color, width=0)))
    
                # Asegurar opacidad total
                trace.update(opacity=1)
            except Exception:
                pass 

        img_bytes = img_fig.to_image(format="png", width=width, height=height, scale=scale, engine="kaleido")
        return img_bytes
        
    except Exception as e:
        print(f"Error convirtiendo gráfica: {e}")
        return None
        
    except Exception as e:
        print(f"Error convirtiendo gráfica: {e}")
        return None

class PDFReportGenerator:
    def __init__(self, filename="reporte.pdf"):
        self.filename = filename
        self.buffer = io.BytesIO()
        
        # Márgenes estrechos para "Compacto"
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.4*inch,
            leftMargin=0.4*inch,
            topMargin=0.4*inch,
            bottomMargin=0.4*inch
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=COLOR_TITULO,
            alignment=TA_CENTER,
            spaceAfter=2
        ))
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=15
        ))
        self.styles.add(ParagraphStyle(
            name='CellText',
            parent=self.styles['Normal'],
            fontSize=7,
            leading=8,
            textColor=COLOR_TEXTO_BODY
        ))
        self.styles.add(ParagraphStyle(
            name='ChartTitle',
            parent=self.styles['Heading3'],
            fontSize=10,
            textColor=COLOR_TITULO,
            alignment=TA_LEFT,
            spaceAfter=2
        ))

    def add_header_info(self, title, subtitle, date_val):
        d_str = date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val)
        self.story.append(Paragraph(title, self.styles['MainTitle']))
        self.story.append(Paragraph(f"{subtitle}  |  Fecha Corte: {d_str}", self.styles['SubTitle']))

    def add_kpis_compact(self, kpis):
        # Tabla de fila única para ahorrar espacio vertical
        data = []
        headers = []
        values = []
        for k, v in kpis.items():
            headers.append(Paragraph(f"<b>{k}</b>", self.styles['CellText']))
            val = f"{v:.2f}" if isinstance(v, float) else str(v)
            values.append(Paragraph(f"<b>{val}</b>", self.styles['CellText']))
            
        data = [headers, values]
        
        # Calcular anchos
        w = 7.5*inch / len(kpis)
        t = Table(data, colWidths=[w]*len(kpis))
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_ENCABEZADO_TABLA),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0,1), (-1,1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, COLOR_TITULO),
        ]))
        self.story.append(t)
        self.story.append(Spacer(1, 0.2*inch))

    def add_chart_section(self, fig, title, height=200):
        # Gráfica compacta
        self.story.append(Paragraph(title, self.styles['ChartTitle']))
        img_bytes = plotly_to_image_bytes(fig, width=900, height=int(height*2.5)) 
        if img_bytes:
            # Display size
            aspect = 900 / (height*2.5)
            d_w = 7.5*inch
            d_h = d_w / aspect
            self.story.append(Image(io.BytesIO(img_bytes), width=d_w, height=d_h))
        self.story.append(Spacer(1, 0.1*inch))

    def add_table_compact(self, df, title, max_rows=15):
        if df is None or df.empty: return
        self.story.append(Paragraph(title, self.styles['ChartTitle']))
        
        d = df.head(max_rows).copy()
        data = [[Paragraph(f"<b>{c}</b>", self.styles['CellText']) for c in d.columns]]
        for _, row in d.iterrows():
            r = []
            for item in row:
                txt = str(item)
                if len(txt) > 30: txt = txt[:27]+"..."
                r.append(Paragraph(txt, self.styles['CellText']))
            data.append(r)
            
        col_w = 7.5*inch / len(d.columns)
        t = Table(data, colWidths=[col_w]*len(d.columns))
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_ENCABEZADO_TABLA),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [COLOR_FILA_PAR, colors.white]),
            ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        self.story.append(t)
        self.story.append(Spacer(1, 0.1*inch))

    def generate(self):
        self.doc.build(self.story)
        return self.buffer.getvalue()

def generar_reporte_completo_pdf(
    fecha_evaluacion, kpis_principales, 
    fig_resumen_anual=None, fig_torta_fallas=None, fig_fallas_activo=None, fig_runlife=None,
    df_pozos_problema=None, df_fallas_mensuales=None,
    active_selection="TODOS", **kwargs
):
    pdf = PDFReportGenerator()
    
    # --- PÁGINA 1: DASHBOARD EJECUTIVO ---
    pdf.add_header_info("DASHBOARD INDICADORES ALS", f"Activo: {active_selection}", fecha_evaluacion)
    
    # Kpis (Compacto - horizontal)
    if kpis_principales:
        pdf.add_kpis_compact(kpis_principales)
    
    # Gráficas Principales
    if fig_resumen_anual:
        pdf.story.append(Spacer(1, 0.3*inch))
        pdf.add_chart_section(fig_resumen_anual, "Resumen Anual (Run Life, Pozos, TMEF)", height=280)
        
    if fig_fallas_activo:
        pdf.story.append(Spacer(1, 0.3*inch))
        pdf.add_chart_section(fig_fallas_activo, "Fallas por Activo", height=220)
        
    # --- PÁGINA 2: ANÁLISIS Y DATOS ---
    pdf.story.append(PageBreak())
    pdf.add_header_info("DETALLE DE FALLAS", "Análisis Causa Raíz y Listados", fecha_evaluacion)
    
    if fig_torta_fallas:
        pdf.story.append(Spacer(1, 0.3*inch))
        pdf.add_chart_section(fig_torta_fallas, "Distribución Tipos de Falla", height=200)
    
    if fig_runlife:
        pdf.story.append(Spacer(1, 0.3*inch))
        pdf.add_chart_section(fig_runlife, "Clasificación Run Life", height=200)
        
    # Tablas
    if df_pozos_problema is not None:
        pdf.story.append(Spacer(1, 0.3*inch))
        pdf.add_table_compact(df_pozos_problema, "Top Pozos Problemas", max_rows=10)
        
    if df_fallas_mensuales is not None:
        cols_show = [c for c in df_fallas_mensuales.columns if c in ['Mes', 'Pozo', 'Fallas Totales', 'Tipo']]
        if cols_show:
            pdf.add_table_compact(df_fallas_mensuales[cols_show], "Registro Reciente", max_rows=15)
        else:
            pdf.add_table_compact(df_fallas_mensuales, "Registro Fallas", max_rows=10)

    return pdf.generate()
