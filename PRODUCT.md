# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Gerentes y supervisores de campo de Parex Resources. Usan el dashboard en reuniones de revisión de performance, tomas de decisión de intervención en pozos, y reportes de confiabilidad. Necesitan scanear estado de activos rápido, identificar pozos problemáticos, y exportar evidencia para reportes ejecutivos.

## Product Purpose

Dashboard de indicadores ALS (Artificial Lift Systems) para monitorear performance y confiabilidad de pozos con bombas. Calcula métricas propietarias: Run Life Efectivo, Índice de Falla Anual, MTBF con Kaplan-Meier. Permite detectar pozos en degradación, priorizar workovers, y reportar KPIs de confiabilidad a dirección.

Success = decisiones de intervención más rápidas y basadas en datos; reducción de downtime no planificado.

## Positioning

Única herramienta que combina: (1) algoritmos propietarios de Parex para Run Life Efectivo e Índice de Falla Anual, (2) integración automática OneDrive con cache offline para trabajo en campo sin conexión, (3) visualizaciones especializadas oil & gas (heatmaps operatividad, curvas Kaplan-Meier, ECharts premium) en una sola interfaz Streamlit desplegable internamente.

## Operating Context

- Reuniones semanales/mensuales de performance de activos
- Trabajo en campo con conectividad intermitente (cache offline crítico)
- Exportación a Excel con gráficos embebidos para reportes formales
- Datos fuente: archivos Excel maestros en OneDrive corporativo
- Múltiples tabs: Resumen, Índices, MTBF, Fallas, Performance, Campañas, Tablero

## Capabilities and Constraints

- Framework: Streamlit (fijo, no migrable)
- Data pipeline: Excel → OneDrive → cache local → pandas → cálculos → UI
- Cálculos core: MTBF (Weibull/Kaplan-Meier), Run Life Efectivo, Índice Falla Anual, clasificación IA de razones de falla
- Visualizaciones: Plotly, ECharts (via streamlit-echarts), heatmaps custom
- Export: Excel con gráficos (openpyxl + xlsxwriter + kaleido)
- Tema: Solo modo claro corporativo Parex
- No autenticación robusta (login simple actual)

## Brand Commitments

- Nombre: "INDICADORES ALS" / Parex Resources
- Colores obligatorios: Primary #137659 (verde Parex), Secondary #c09c2e (dorado Parex), Accent #095139
- Tipografía: Sistema nativo Streamlit (sin fuente custom)
- Logo: Parex Resources (buscado via get_base64_image en ui_helpers)

## Evidence on Hand

- App funcional en `app.py` con 7 tabs implementados
- Cálculos validados en `core/` (mtbf, run_life_efectivo, indice_falla, calculations)
- Tema visual en `ui/theme.py` con paleta Parex
- Componentes UI en `ui/` (kpis, sidebar, header, styles, upload)
- Gráficos en `grafico.py` y `grafico_run_life.py`
- Datos de prueba en `cache_data/` y `saved_uploads/`

## Product Principles

1. **Scanability first** — gerentes deben entender estado de activos en <10 segundos
2. **Offline-capable** — campo sin conexión no puede bloquear decisiones
3. **Export-ready** — cada vista debe poder ir a reporte ejecutivo sin rework
4. **Cálculos auditables** — trazabilidad de fórmulas propietarias vs estándares
5. **Consistencia visual Parex** — todo respeta brand guide sin excepciones

## Accessibility & Inclusion

- Contraste WCAG AA mínimo en paleta corporativa
- Tamaños de fuente legibles en pantallas de laptop de campo (13-15")
- Navegación por teclado en tabs y sidebar
- Estados vacíos y de carga claros (sin spinners genéricos)