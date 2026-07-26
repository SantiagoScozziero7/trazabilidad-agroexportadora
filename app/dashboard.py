import os
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.express as px

# ============================================================
# RUTAS Y CONEXIÓN A LA BASE DE DATOS
# ============================================================
# Calculamos las rutas a partir de la ubicación real de este archivo,
# así el dashboard funciona sin importar desde dónde se ejecute el comando.
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_db = os.path.join(carpeta_actual, "..", "database", "trazabilidad.db")
carpeta_sql = os.path.join(carpeta_actual, "..", "sql")

conexion = sqlite3.connect(ruta_db)


def leer_query(nombre_archivo):
    """Lee una query SQL desde la carpeta sql/ y devuelve el texto."""
    ruta = os.path.join(carpeta_sql, nombre_archivo)
    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()


def agregar_valores_barras(ax, barras):
    """Agrega el valor numérico al lado de cada barra horizontal."""
    for barra in barras:
        ancho = barra.get_width()
        ax.text(
            ancho,
            barra.get_y() + barra.get_height() / 2,
            f' {ancho:,.0f}',
            va='center'
        )


formateador_numeros = ticker.FuncFormatter(lambda x, pos: f'{x:,.0f}')
colores_riesgo = {'Alto': 'firebrick', 'Medio': 'goldenrod', 'Bajo': 'seagreen'}

# ============================================================
# ENCABEZADO
# ============================================================
st.title("🌱 Trazabilidad Agroexportadora")
st.markdown("""
Análisis en SQL de la relación entre **producción agrícola** y **deforestación** por 
provincia en Argentina, en el contexto de la regulación europea EUDR (que exige a los 
exportadores demostrar que sus productos no provienen de tierras recientemente deforestadas).

**Cultivos analizados:** soja, maíz y trigo · **Período:** 1969-2024
""")

st.divider()

# ============================================================
# GRÁFICO 1 — RANKING DE PRODUCCIÓN
# ============================================================
st.header("📊 Ranking de producción por provincia")
st.write("Total histórico de soja + maíz + trigo producido por provincia.")

df_ranking_produccion = pd.read_sql(leer_query("ranking_produccion.sql"), conexion)

fig1, ax1 = plt.subplots(figsize=(10, 8))
barras1 = ax1.barh(df_ranking_produccion['provincia'], df_ranking_produccion['total_produccion'])
agregar_valores_barras(ax1, barras1)
ax1.set_xlabel('Producción total (toneladas)')
ax1.invert_yaxis()
ax1.xaxis.set_major_formatter(formateador_numeros)
st.pyplot(fig1)

st.markdown("""
**Conclusión:** Buenos Aires, Córdoba y Santa Fe concentran la gran mayoría de la producción, 
muy por encima del resto. Las provincias del norte (Santiago del Estero, Salta, Chaco) 
producen relativamente poco en comparación con la zona núcleo pampeana.
""")

st.divider()

# ============================================================
# GRÁFICO 2 — RANKING DE DEFORESTACIÓN
# ============================================================
st.header("🌳 Ranking de deforestación por provincia")
st.write("Total de hectáreas de bosque nativo perdidas por provincia.")

df_ranking_deforestacion = pd.read_sql(leer_query("ranking_deforestacion.sql"), conexion)

fig2, ax2 = plt.subplots(figsize=(10, 8))
barras2 = ax2.barh(
    df_ranking_deforestacion['provincia'],
    df_ranking_deforestacion['total_deforestacion'],
    color='forestgreen'
)
agregar_valores_barras(ax2, barras2)
ax2.set_xlabel('Superficie deforestada (hectáreas)')
ax2.invert_yaxis()
ax2.xaxis.set_major_formatter(formateador_numeros)
st.pyplot(fig2)

st.markdown("""
**Conclusión:** Santiago del Estero, Formosa y Chaco lideran claramente la pérdida de bosque 
nativo. El patrón es casi inverso al de producción: las provincias líderes en deforestación 
están lejos de ser las líderes en producción.
""")

st.divider()

# ============================================================
# GRÁFICO 3 — NIVEL DE RIESGO
# ============================================================
st.header("🚦 Nivel de riesgo por provincia")
st.write("Clasificación Alto/Medio/Bajo según hectáreas deforestadas.")

df_riesgo = pd.read_sql(leer_query("clasificacion_riesgo.sql"), conexion)
df_riesgo = df_riesgo.sort_values('total_deforestacion', ascending=False)
colores = df_riesgo['nivel_riesgo'].map(colores_riesgo)

fig3, ax3 = plt.subplots(figsize=(10, 8))
barras3 = ax3.barh(df_riesgo['provincia'], df_riesgo['total_deforestacion'], color=colores)
agregar_valores_barras(ax3, barras3)
ax3.set_xlabel('Superficie deforestada (hectáreas)')
ax3.invert_yaxis()
ax3.xaxis.set_major_formatter(formateador_numeros)
st.pyplot(fig3)

st.markdown("""
**Conclusión:** 3 provincias en riesgo "Alto" (Santiago del Estero, Formosa, Chaco), 
7 en "Medio". Notable que Córdoba, líder en producción, aparece en nivel "Medio" de 
riesgo — producir mucho no es sinónimo de bajo riesgo de deforestación.
""")

st.divider()

# ============================================================
# GRÁFICO 4 — SELECTOR INTERACTIVO POR CULTIVO
# ============================================================
st.header("🌾 Riesgo por cultivo (interactivo)")
st.write("Elegí un cultivo para ver el cruce producción/deforestación específico de ese cultivo.")

df_riesgo_cultivo = pd.read_sql(leer_query("riesgo_por_cultivo.sql"), conexion)

cultivo_elegido = st.selectbox(
    "Cultivo:",
    options=df_riesgo_cultivo['cultivo'].unique()
)

df_filtrado_cultivo = df_riesgo_cultivo[df_riesgo_cultivo['cultivo'] == cultivo_elegido]
df_filtrado_cultivo = df_filtrado_cultivo.sort_values('total_produccion', ascending=False)
colores_cultivo = df_filtrado_cultivo['nivel_riesgo'].map(colores_riesgo)

fig4, ax4 = plt.subplots(figsize=(10, 8))
barras4 = ax4.barh(df_filtrado_cultivo['provincia'], df_filtrado_cultivo['total_produccion'], color=colores_cultivo)
agregar_valores_barras(ax4, barras4)
ax4.set_xlabel('Producción total (toneladas)')
ax4.set_title(f'Producción de {cultivo_elegido} por provincia, coloreado por riesgo')
ax4.invert_yaxis()
ax4.xaxis.set_major_formatter(formateador_numeros)
st.pyplot(fig4)

st.divider()

# ============================================================
# GRÁFICO 5 — EVOLUCIÓN TEMPORAL (ALTO RIESGO)
# ============================================================
st.header("📈 Evolución de producción en provincias de alto riesgo")
st.write("Serie temporal 1969-2024 para las provincias clasificadas como riesgo Alto. Pasá el mouse sobre las líneas para ver el detalle, o hacé zoom arrastrando sobre el gráfico.")

df_evolucion = pd.read_sql(leer_query("evolucion_alto_riesgo.sql"), conexion)

fig5 = px.line(
    df_evolucion,
    x='anio',
    y='total_produccion',
    color='provincia',
    markers=True,
    labels={'anio': 'Año', 'total_produccion': 'Producción (toneladas)', 'provincia': 'Provincia'}
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
**Conclusión:** Santiago del Estero muestra un crecimiento explosivo a partir del año 2000, 
coincidiendo con la expansión de la frontera agrícola sobre el Chaco Semiárido. Formosa se 
mantiene casi plana en todo el período.
""")

st.divider()

# ============================================================
# TABLA DE DATOS CRUDOS
# ============================================================
st.header("🔍 Explorar los datos")
st.write("Tabla completa del cruce producción/deforestación por provincia.")
st.dataframe(df_riesgo, use_container_width=True)

st.markdown("""
---
⚠️ **Limitación metodológica:** este análisis usa datos agregados por provincia, no 
trazabilidad exacta por lote. Es una aproximación geográfica al riesgo, no una prueba de 
que una tonelada específica provenga de tierra deforestada.
""")
