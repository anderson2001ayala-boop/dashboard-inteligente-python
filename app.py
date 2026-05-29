
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# ===================== CONFIGURACIÓN =====================
st.set_page_config(
    page_title="Dashboard de Ventas Profesional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo oscuro profesional
st.markdown("""
<style>
    .main {background-color: #0E1117;}
    h1 {color: #00B4D8;}
    .stPlotlyChart {background-color: #1A1F2E;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard de Ventas Profesional")
st.markdown("**Análisis Comercial en Tiempo Real**")

# ===================== CARGA DE DATOS =====================
st.sidebar.header("📂 Cargar tus Datos")

uploaded_file = st.sidebar.file_uploader(
    "Sube tu archivo CSV o Excel", 
    type=["csv", "xlsx", "xls"]
)

@st.cache_data
def cargar_datos(file):
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            return df
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return None
    else:
        # Datos de ejemplo
        st.info("Usando datos de ejemplo. Sube tu archivo para usar datos reales.")
        df = pd.DataFrame({
            'Fecha': pd.date_range(start='2025-01-01', periods=300, freq='D'),
            'Region': ['Norte', 'Sur', 'Este', 'Oeste'] * 75,
            'Producto': ['Laptop', 'Celular', 'Tablet', 'Monitor', 'Audífonos'] * 60,
            'Vendedor': ['Carlos', 'Ana', 'Miguel', 'Laura', 'Roberto'] * 60,
            'Ventas': [1250, 890, 650, 420, 180] * 60,
            'Cantidad': [5, 12, 8, 15, 25] * 60,
        })
        return df

df = cargar_datos(uploaded_file)

if df is None:
    st.stop()

# Convertir Fecha si existe
if 'Fecha' in df.columns:
    df['Fecha'] = pd.to_datetime(df['Fecha'])

# ===================== FILTROS =====================
st.sidebar.header("🔍 Filtros")

# Filtros
if 'Region' in df.columns:
    regiones = st.sidebar.multiselect("Región", df['Region'].unique(), default=df['Region'].unique())

if 'Vendedor' in df.columns:
    vendedores = st.sidebar.multiselect("Vendedor", df['Vendedor'].unique(), default=df['Vendedor'].unique())

if 'Fecha' in df.columns:
    fecha_min = df['Fecha'].min().date()
    fecha_max = df['Fecha'].max().date()
    fecha_rango = st.sidebar.date_input("Rango de Fechas", [fecha_min, fecha_max])

if 'Ventas' in df.columns:
    venta_min, venta_max = st.sidebar.slider(
        "Monto de Venta ($)", 
        float(df['Ventas'].min()), 
        float(df['Ventas'].max()), 
        (float(df['Ventas'].min()), float(df['Ventas'].max()))
    )

# Aplicar filtros
df_filtrado = df.copy()

if 'Region' in df.columns:
    df_filtrado = df_filtrado[df_filtrado['Region'].isin(regiones)]
if 'Vendedor' in df.columns:
    df_filtrado = df_filtrado[df_filtrado['Vendedor'].isin(vendedores)]
if 'Fecha' in df.columns and len(fecha_rango) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado['Fecha'].dt.date >= fecha_rango[0]) & 
        (df_filtrado['Fecha'].dt.date <= fecha_rango[1])
    ]
if 'Ventas' in df.columns:
    df_filtrado = df_filtrado[(df_filtrado['Ventas'] >= venta_min) & (df_filtrado['Ventas'] <= venta_max)]

# ===================== KPIs =====================
st.subheader("📈 Indicadores Clave")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Ventas Totales", f"${df_filtrado['Ventas'].sum():,.0f}")
with c2:
    st.metric("📦 Pedidos", len(df_filtrado))
with c3:
    st.metric("🎟️ Ticket Promedio", f"${df_filtrado['Ventas'].mean():.0f}")
with c4:
    st.metric("📦 Unidades", df_filtrado['Cantidad'].sum() if 'Cantidad' in df_filtrado.columns else "N/A")

# ===================== GRÁFICOS =====================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolución", "🥧 Distribución", "🏆 Top", "📤 Exportar"])

with tab1:
    if 'Fecha' in df_filtrado.columns:
        ventas_mes = df_filtrado.resample('ME', on='Fecha')['Ventas'].sum().reset_index()
        fig = px.line(ventas_mes, x='Fecha', y='Ventas', title="Evolución de Ventas")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        if 'Region' in df_filtrado.columns:
            st.plotly_chart(px.pie(df_filtrado, names='Region', values='Ventas', title="Por Región"), use_container_width=True)
    with col2:
        if 'Producto' in df_filtrado.columns:
            st.plotly_chart(px.pie(df_filtrado, names='Producto', values='Ventas', title="Por Producto"), use_container_width=True)

with tab3:
    if 'Producto' in df_filtrado.columns:
        top = df_filtrado.groupby('Producto')['Ventas'].sum().nlargest(10)
        st.plotly_chart(px.bar(top, title="Top 10 Productos"), use_container_width=True)

with tab4:
    st.subheader("Exportar Reporte")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Descargar Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_filtrado.to_excel(writer, index=False)
            st.download_button("Descargar Excel", output.getvalue(), 
                             f"Reporte_Ventas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        if st.button("📥 Descargar CSV"):
            csv = df_filtrado.to_csv(index=False).encode()
            st.download_button("Descargar CSV", csv, 
                             f"Reporte_Ventas_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

st.caption("Dashboard creado con ❤️ en Python + Streamlit")
