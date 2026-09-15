# 💳 Control de Finanzas Personales

Una aplicación web interactiva desarrollada con **Streamlit** y **Python** para gestionar ingresos, gastos y visualizar el balance financiero global y mensual mediante el consumo de una API REST.

## Características Principales

* **Resumen en Tiempo Real:** Métricas del mes actual (ingresos, gastos, valor neto) y saldo histórico acumulado.
* **Registro de Movimientos:** Formulario intuitivo para añadir transacciones y gestionar categorías automáticamente.
* **Historial Visual:** Tabla ordenada cronológicamente con codificación de colores para ingresos (verde) y gastos (rojo).
* **Gráficos Interactivos:** Distribución por categorías (gráfico de dona) y análisis de evolución histórica mediante Plotly.
* **Filtro Mensual:** Desglose detallado de cualquier periodo seleccionado.

## Tecnologías Utilizadas

| Componente | Tecnología |
| :--- | :--- |
| **Interfaz** | Streamlit |
| **Visualización** | Plotly Express & Graph Objects |
| **Procesamiento de datos** | Pandas |
| **Backend / API** | FastAPI (Desplegado en Render) |
| **Lenguaje** | Python 3.x |

## Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
   cd tu-repositorio

2. **Instalar dependencias:**
   ```bash
    pip install streamlit requests pandas 
    
3. **Lanzar la aplicación:**
   ```bash
    streamlit run app.py
