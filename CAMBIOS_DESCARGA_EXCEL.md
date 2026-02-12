# Funcionalidad de Descarga a Excel - Gráficas de Indicadores ALS

## 📋 Resumen de Cambios

Se ha añadido funcionalidad de descarga a Excel para **cuatro gráficas principales** de indicadores: **Tiempo de Vida y TEMF**, **Pozos e Índices**, **Resumen Performance Completo**, y **Producción (BOPD) vs Tiempo de Vida**, permitiendo exportar los datos para análisis externo y creación de gráficas personalizadas.

## ✨ Características Implementadas

### 1. **Gráfica de Tiempo de Vida y TEMF** (grafico_run_life.py)
- **Botón de descarga**: "📥 Descargar datos en Excel"
- **Archivo generado**: `tiempo_vida_temf.xlsx`
- **Datos incluidos**:
  - Mes
  - Tiempo de Vida Promedio (días)
  - Tiempo de Vida Total (días)
  - TMEF Promedio (días)
  - Tiempo de Vida Efectivo Total (días)
  - Tiempo de Vida Efectivo Fallados (días)

### 2. **Gráfica de Pozos e Índices** (grafico_run_life.py)
- **Botón de descarga**: "📥 Descargar datos en Excel"
- **Archivo generado**: `pozos_indices.xlsx`
- **Datos incluidos**:
  - Mes
  - Pozos Activos
  - Pozos Inactivos
  - Índice de Falla ON (%)
  - Índice de Falla ALS ON (%)

### 3. **Gráfica de Resumen Performance Completo** (grafico.py)
- **Botón de descarga**: "📥 Descargar datos completos en Excel"
- **Archivo generado**: `resumen_performance_completo.xlsx`
- **Datos incluidos** (todos los datos mensuales):
  - Mes
  - Pozos Operativos
  - Pozos Activos
  - Pozos Inactivos
  - Tiempo de Vida Promedio (días)
  - Tiempo de Vida Total (días)
  - TMEF Promedio (días)
  - Tiempo de Vida Efectivo Total (días)
  - Tiempo de Vida Efectivo Fallados (días)
  - Índice de Falla ON (%)
  - Índice de Falla ALS ON (%)

### 4. **Gráfica de Producción (BOPD) vs Tiempo de Vida** (INDICADORES.py) ⭐ **NUEVO + MEJORADO**
- **Botón de descarga**: "📥 Descargar datos en Excel"
- **Archivo generado**: `produccion_bopd_vs_tiempo_vida.xlsx`
- **Hojas incluidas**:
  - **BOPD vs Tiempo de Vida** (resumen por rango):
    - Rango de Tiempo de Vida
    - Producción Total (BOPD)
    - Cantidad de Pozos
  - **Detalle por Pozo** (datos individuales):
    - Pozo
    - Producción (BOPD)
    - Tiempo de Vida (días)
    - Rango de Tiempo de Vida
- **Mejoras visuales implementadas**:
  - ✨ Título premium "PRODUCCIÓN vs TIEMPO DE VIDA"
  - 📊 Valores de BOPD mostrados directamente en las barras
  - 🎨 Gradientes de color en las barras para mejor impacto visual
  - 💫 Sombras y efectos de profundidad
  - 🎯 Tooltip mejorado con colores y formato profesional
  - 📏 Ejes con etiquetas claras y colores distintivos
  - 🌈 Fondo con gradiente sutil para mejor presentación

## 🔧 Detalles Técnicos

### Archivos Modificados
- **`grafico_run_life.py`**: Se modificaron las funciones `render_premium_echarts_run_life()` y `render_premium_echarts_pozos()`
- **`grafico.py`**: Se modificó la función `render_premium_echarts()` para incluir descarga de datos completos
- **`INDICADORES.py`**: Se mejoró significativamente la sección de "Producción (BOPD) vs Tiempo de Vida" en el tab_performance (líneas 2676-2770)

### Dependencias Utilizadas
- `pandas`: Para manipulación de datos
- `openpyxl`: Para generación de archivos Excel (ya estaba en requirements.txt)
- `io.BytesIO`: Para manejo de datos en memoria
- `streamlit.download_button`: Para crear los botones de descarga

### Implementación
1. **Preparación de datos**: Se extraen las columnas relevantes del DataFrame mensual
2. **Renombrado de columnas**: Se renombran las columnas para mejor legibilidad en español
3. **Conversión de formatos**: Los índices se convierten a porcentaje para facilitar la interpretación
4. **Generación de Excel**: Se utiliza `pd.ExcelWriter` con el motor `openpyxl`
5. **Botón de descarga**: Se crea un botón de Streamlit que permite descargar el archivo

## 📊 Beneficios

1. **Análisis Externo**: Los usuarios pueden abrir los datos en Excel para crear gráficas personalizadas
2. **Reportes**: Facilita la creación de reportes y presentaciones
3. **Datos Limpios**: Las columnas están renombradas en español con descripciones claras
4. **Formato Estándar**: Archivos .xlsx compatibles con Excel, Google Sheets, etc.

## 🎯 Uso

1. Navega a la sección de gráficas en la aplicación
2. Localiza las gráficas de "T. VIDA & TMEF" y "POZOS & ÍNDICES"
3. Haz clic en el botón "📥 Descargar datos en Excel" debajo de cada gráfica
4. El archivo se descargará automáticamente a tu carpeta de descargas
5. Abre el archivo en Excel para crear tus propias visualizaciones

## ✅ Estado

- ✅ Funcionalidad implementada
- ✅ Aplicación ejecutándose correctamente
- ✅ Botones de descarga operativos
- ✅ Archivos Excel generados con formato correcto
