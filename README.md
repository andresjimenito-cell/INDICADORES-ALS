# 🚀 Sistema Frontera Energy

Sistema integral de evaluación técnica, económica y energética para diseños de Bombas Sumergibles Eléctricas (ESP) y monitoreo de indicadores de Sistemas Artificiales de Levantamiento (ALS).

## ✨ Características Principales

### 📊 Módulo INDICADORES ALS
- **MTBF (Mean Time Between Failures)**: Cálculo de tiempo medio entre fallos
- **Índices de Falla**: Análisis anual de tasas de fallos por causa
- **KPIs**: Indicadores clave de desempeño
- **Reportes**: Generación de reportes detallados de performance
- **Clasificación de Fallos**: Categorización automática por tipo (Mecánica, Eléctrica, Tubería, Yacimiento)

### ⚙️ Módulo EVALUACIÓN ESP
- **Evaluación Técnica**: Análisis de cumplimiento de especificaciones de diseño
- **Análisis Económico**: Comparativa de costos por categoría y tamaño de tubería
  - FULL PRICE
  - R-R-I-G-O
  - ALTERNATIVA AHORRO
- **Cálculo TLCC**: Total Life Cycle Cost (PMM y AM)
- **Ranking de Proveedores**: Sistema de puntuación integral (Económico 40pts, Técnico 35pts, Energético 25pts)
- **Análisis Energético**: Evaluación de costos operacionales
- **Reportes Ejecutivos**: Resumen visual de recomendaciones

## 🎨 Interfaz Visual

La aplicación utiliza un tema **cyberpunk/dark mode** moderno con:
- 🟢 Color primario: Verde neón (#00FF99)
- 🔵 Color acento: Azul ciber (#00D9FF)
- ⚫ Fondo animado con efecto de flujo dinámico
- 🎯 Tarjetas con efecto frosted glass
- ✨ Sombras y gradientes elegantes

## 🛠️ Requisitos Técnicos

- **Python**: 3.8 o superior
- **Dependencias**: Ver `requirements.txt`

## 📦 Instalación

### Opción 1: Instalación Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/sistema-frontera-energy.git
cd sistema-frontera-energy

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

### Opción 2: Instalación Directa

```bash
pip install -r requirements.txt
```

## 🚀 Uso

### Iniciar la aplicación:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

### Credenciales de Prueba:

| Usuario | Contraseña | Acceso |
|---------|-----------|--------|
| lenin | 1 | Total |
| practicante | 2 | Total |
| invitado | 3 | Total |
| jaime | 1 | Total |

## 📁 Estructura del Proyecto

```
sistema-frontera-energy/
│
├── app.py                    # 🎯 Aplicación principal - Dashboard de control
├── evaluacion.py             # ⚙️ Módulo de evaluación ESP
├── INDICADORES.py            # 📊 Módulo de indicadores ALS
│
├── theme.py                  # 🎨 Configuración de tema y colores
├── mtbf.py                   # 📈 Cálculos de MTBF
├── kpis.py                   # 📊 Cálculos de KPIs
├── indice_falla.py          # 📉 Cálculos de índices de falla
├── grafico.py               # 📊 Utilidades de gráficos
├── descargar.py             # 💾 Funciones de descarga
│
├── requirements.txt          # 📦 Dependencias del proyecto
├── README.md                # 📖 Este archivo
└── .gitignore               # 🚫 Archivos ignorados por git
```

## 🔑 Funcionalidades Clave

### Dashboard Principal
- Sistema de autenticación seguro
- Acceso a dos módulos principales
- Verificación de disponibilidad de módulos
- Información del sistema y usuario activo

### INDICADORES ALS
- Carga de archivos FORMA 9 (CSV/XLSX)
- Carga de base de datos principal
- Parámetros de evaluación personalizables
- Gráficos interactivos con Plotly
- Exportación de reportes

### EVALUACIÓN ESP
- Carga múltiple de propuestas Excel
- Menú lateral mejorado con estilo cyberpunk
- Análisis en 5 secciones:
  1. 📋 Resumen Ejecutivo
  2. ⚡ TLCC PMM
  3. ⚡ TLCC AM
  4. 💰 Costos
  5. 🛠️ EV Técnica
- Tablas comparativas con formato dinámico
- Gráficos radar y barras interactivos
- Recomendaciones basadas en puntuación integral

## 📊 Sistemas de Evaluación

### Scoring Integral (100 puntos)
- **Económico**: 40 puntos (mejor precio por categoría)
- **Técnico**: 35 puntos (cumplimiento de especificaciones)
- **Energético**: 25 puntos (eficiencia de costos operacionales)

### Categorías Económicas
- FULL PRICE: Propuesta completa sin descuentos
- R-R-I-G-O: Oferta con repotenciamiento y reingeniería
- ALTERNATIVA AHORRO: Opción económica optimizada

### Tuberías Soportadas
- 3-1/2"
- 4-1/2"

## 🌐 Publicación en Streamlit Cloud

Para publicar tu aplicación en la nube:

1. Sube tu código a GitHub
2. Ve a [streamlit.io/cloud](https://streamlit.io/cloud)
3. Conecta tu cuenta GitHub
4. Selecciona este repositorio
5. La app estará disponible en: `https://nombre-app.streamlit.app`

## 📝 Notas Técnicas

- **Framework**: Streamlit (interfaz web)
- **Base de datos**: Archivos Excel/CSV
- **Visualización**: Plotly (gráficos interactivos)
- **Manejo de datos**: Pandas y NumPy
- **Tema**: CSS personalizado con animaciones suaves

## 🐛 Solución de Problemas

### La app no inicia
```bash
# Verifica que Streamlit esté instalado
pip install streamlit --upgrade

# Verifica que estés en la carpeta correcta
cd "ruta\del\proyecto"
```

### Error de archivo no encontrado
- Asegúrate de que los archivos Excel tengan el formato correcto
- Verifica que las rutas de los archivos sean accesibles

### Problemas de rendimiento
- Reduce el número de filas en las bases de datos
- Cierra otras aplicaciones pesadas
- Usa archivos Excel más optimizados

## 📚 Documentación de Entrada de Datos

### Formato Excel Requerido para INDICADORES ALS

**FORMA 9:**
- Columnas: Pozo, Fecha, Equipo, Parámetros técnicos
- Frecuencia: Datos mensuales/trimestrales

**Base de Datos:**
- Columnas: ID, Nombre, Tipo, Estado, Causa de Fallo
- Historial completo de equipos y eventos

### Formato Excel Requerido para EVALUACIÓN ESP

- Proveedor y nombre de bomba en encabezados
- Tabla de costos con estructura específica (FULL PRICE, R-R-I-G-O, ALTERNATIVA)
- Datos técnicos de diseño
- Costos energéticos (TLCC PMM y AM)

## 📞 Soporte

Para reportar bugs o sugerir mejoras:
1. Abre un [Issue](../../issues) en GitHub
2. Describe el problema detalladamente
3. Incluye pasos para reproducir

## 📄 Licencia

Este proyecto está bajo la licencia **MIT** - Eres libre de usar, modificar y distribuir este software.

Ver archivo [LICENSE](LICENSE) para detalles completos.

## 👨‍💻 Desarrollado por

Sistema desarrollado para análisis integral de ofertas de proveedores en la industria de levantamiento artificial.

**Versión**: 1.0.0  
**Última actualización**: Noviembre 2025

---

## 🎯 Roadmap Futuro

- [ ] Base de datos integrada (PostgreSQL/SQLite)
- [ ] Exportación a PDF de reportes
- [ ] Historial de evaluaciones
- [ ] Gráficos de tendencias históricas
- [ ] API REST para integración externa
- [ ] Autenticación OAuth2
- [ ] Dashboard de estadísticas globales

---

**¡Gracias por usar Sistema Frontera Energy!** 🚀✨
