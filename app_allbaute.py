import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="All Baute - Strategic Intelligence", layout="wide")

# --- CARGA DE DATOS DESDE GITHUB (MODO NUBE) ---
@st.cache_data
def cargar_datos_nube():
    # Leemos los CSVs de tu repositorio
    df_heatmap = pd.read_csv('df_heatmap.csv')
    df_rfm_2024 = pd.read_csv('df_rfm.csv')
    df_audit_2024 = pd.read_csv('df_audit.csv')
    # Nuevo archivo con el detalle de las fugas
    df_fugas_detalladas = pd.read_csv('df_fugas_detalladas.csv') 
    m = pd.read_csv('metricas.csv')
    
    # Extraemos valores individuales
    v_2024 = int(m.loc[m['metrica'] == 'ventas', 'valor'].values[0])
    c_2024 = int(m.loc[m['metrica'] == 'clientes', 'valor'].values[0])
    ciu_2024 = int(m.loc[m['metrica'] == 'ciudades', 'valor'].values[0])
    
    return v_2024, c_2024, ciu_2024, df_heatmap, df_rfm_2024, df_audit_2024, df_fugas_detalladas

# Ejecutamos la carga incluyendo la nueva variable
v_2024, c_2024, ciu_2024, df_heatmap, df_rfm_2024, df_audit_2024, df_fugas_detalladas = cargar_datos_nube()

fecha_corte = '2024-01-01'

# --- ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] {
        color: #c5a059 !important;
        font-weight: bold;
        font-size: 2rem;
    }
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
        font-size: 1.1rem;
    }
    .stAlert { background-color: #161b22; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
st.sidebar.image("https://allbaute.com/cdn/shop/files/LOGO_EN_BLANCO.jpg?v=1707402621&amp", width=200)
st.sidebar.header("Navegación Estratégica")
opcion = st.sidebar.selectbox("Seleccione un Pilar:", 
                              ["Resumen Ejecutivo", "Inventario & Tallas", "Segmentación de Clientes", "Auditoría Financiera"])

# --- CONTENIDO PRINCIPAL ---
st.title("🏛️ All Baute: Business Intelligence Dashboard")
st.markdown(f"**Ciclo de Auditoría:** Enero {fecha_corte[:4]} - Actualidad")

# --- PILAR 1: RESUMEN EJECUTIVO ---
if opcion == "Resumen Ejecutivo":
    st.header("📍 Estado Real de la Operación")
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Clientes Activos", f"{c_2024:,}")
    c2.metric("Ventas Auditadas", f"{v_2024:,}")
    c3.metric("Errores Corregidos", "2,218", delta="-100% Inconsistencias")
    c4.metric("Alcance Geográfico", f"{ciu_2024} Municipios")
    
    st.success("✅ **Certificación de Datos:** La base de datos ha sido depurada y normalizada satisfactoriamente.")
    st.info("💡 **Hallazgo:** Solo el 14% de la base histórica ha interactuado en 2024. Existe una oportunidad masiva de reactivación.")

# --- PILAR 2: INVENTARIO & TALLAS ---
elif opcion == "Inventario & Tallas":
    st.header("📉 Auditoría de Eficiencia de Inventario 2024")
    
    if not df_heatmap.empty:
        pivot_df = df_heatmap.pivot(index='Nom_Ciudad', columns='Talla_Solicitada', values='Unidades').fillna(0)
        top_ciudades = pivot_df.sum(axis=1).nlargest(10).index
        pivot_df = pivot_df.loc[top_ciudades]

        fig_heat = px.imshow(pivot_df, color_continuous_scale='YlGnBu', aspect="auto", text_auto=True)
        fig_heat.update_layout(title_text='Mapa de Calor: Concentración Geográfica de Ventas', template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")
        df_inv_analisis = df_heatmap.groupby('Talla_Solicitada')['Unidades'].sum().reset_index()
        df_inv_analisis['Diagnóstico'] = df_inv_analisis['Unidades'].apply(lambda x: '🔥 Alta Rotación' if x > 50 else '🧊 Capital Atrapado')
        
        fig_eficiencia = px.bar(df_inv_analisis.sort_values('Unidades', ascending=False).head(15), 
                                x='Talla_Solicitada', y='Unidades', color='Diagnóstico',
                                color_discrete_map={'🔥 Alta Rotación': '#c5a059', '🧊 Capital Atrapado': '#4a4e69'},
                                text_auto=True)
        st.plotly_chart(fig_eficiencia, use_container_width=True)
        st.error("🚨 **Hallazgo Crítico:** El 82% de las tallas no generan flujo de caja. Optimización de stock requerida.")

# --- PILAR 3: SEGMENTACIÓN DE CLIENTES ---
elif opcion == "Segmentación de Clientes":
    st.header("🌪️ Embudo de Retención de Clientes 2024")
    
    fig_funnel = go.Figure(go.Funnel(
        y = ["Prospectos / Nuevos", "Clientes Leales", "Campeones (VIP)"],
        x = [v_2024, 1688, 157], 
        textinfo = "value+percent initial",
        marker = {"color": ["#632a2a", "#a68a1c", "#2e4d3a"], "line": {"width": 1, "color": "#1e1e1e"}}
    ))
    fig_funnel.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    st.markdown("---")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1: st.error("📉 **Fuga Crítica**\n\n57% de nuevos clientes no regresan.")
    with col_info2: st.warning("🎯 **Potencial**\n\n1,688 clientes listos para escalar a VIP.")
    with col_info3: st.success("💎 **Valor VIP**\n\n157 campeones sostienen la rentabilidad.")

# --- PILAR 4: AUDITORÍA FINANCIERA ---
# --- PILAR 4: AUDITORÍA FINANCIERA ---
elif opcion == "Auditoría Financiera":
    st.header(f"⚖️ Control de Riesgo y Conciliación 2024")
    
    # Calculamos métricas reales basadas en el archivo de detalles
    n_fugas = len(df_fugas_detalladas)
    monto_riesgo = df_fugas_detalladas['Valor_Final'].sum()
    
    # Calculamos efectividad: (Ventas totales - Ventas sin factura) / Ventas totales
    efectividad = (1 - (n_fugas / v_2024)) * 100 if v_2024 > 0 else 100

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Efectividad de Facturación", f"{efectividad:.1f}%", delta=f"{n_fugas} Fugas", delta_color="inverse")
    with c2:
        st.metric("Capital en Riesgo Contable", f"${monto_riesgo:,.2f}", delta="Acción Requerida", delta_color="inverse")

    st.markdown("---")
    
    # ESTA ES LA TABLA QUE TE FALTABA MOSTRAR
    st.subheader("🔎 Detalle de Transacciones sin Respaldo Legal")
    st.write("Registros de venta que apuntan a folios de facturación inexistentes en el sistema central:")
    
    # Mostramos la tabla profesional con los 22 registros
    st.dataframe(
        df_fugas_detalladas.style.format({"Valor_Final": "${:,.2f}"}), 
        use_container_width=True
    )

    st.error(f"🚨 **Hallazgo Crítico:** Se detectaron {n_fugas} transacciones con folios 'fantasma' (ej. 149, 855). El proceso de facturación presenta vulnerabilidades de integridad.")
    
    st.info("💡 **Recomendación Senior:** Se requiere una conciliación inmediata de folios físicos contra sistema para legalizar estos ingresos.")

st.sidebar.markdown("---")
st.sidebar.caption("📊 Senior Data Consultant | All Baute 2024")
