# web/app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import sqlite3
import pandas as pd
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SIMUR - Dashboard", page_icon="🌧️", layout="wide")

# Rutas seguras a la base de datos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'data', 'simur_logs.db')

# Coordenadas de prueba (Punto crítico simulado: Av. Eusebio Ayala)
LATITUD_NODO = -25.2985
LONGITUD_NODO = -57.6105

def obtener_datos():
    """Lee la base de datos SQLite y devuelve el último registro y el historial."""
    if not os.path.exists(DB_PATH):
        return None, pd.DataFrame()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        # Último estado registrado
        ultimo = pd.read_sql_query("SELECT * FROM registro_raudales ORDER BY id_registro DESC LIMIT 1", conn)
        # Historial de los últimos 15 eventos
        historial = pd.read_sql_query("SELECT * FROM registro_raudales ORDER BY id_registro DESC LIMIT 15", conn)
        conn.close()
        
        if not ultimo.empty:
            return ultimo.iloc[0], historial
        return None, historial
    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")
        return None, pd.DataFrame()

def main():
    # Encabezado
    st.title("🌧️ S.I.M.U.R. - Monitoreo Urbano de Raudales")
    st.markdown("### Panel de Control Ciudadano y PMT (Asunción)")

    # Botón de actualización
    if st.button("🔄 Actualizar Datos en Tiempo Real"):
        st.rerun()

    ultimo_registro, historial_df = obtener_datos()

    # Variables por defecto
    estado_actual = "DESCONOCIDO"
    nivel_agua = 0.0
    fecha_hora = "Sin datos"
    color_pin = "gray"
    icono_pin = "info-sign"

    if ultimo_registro is not None:
        estado_actual = ultimo_registro['estado_alerta']
        nivel_agua = ultimo_registro['nivel_agua_cm']
        fecha_hora = ultimo_registro['timestamp']
        
        # Lógica de colores para el mapa
        if estado_actual == "ROJO":
            color_pin = "red"
            icono_pin = "warning-sign"
        elif estado_actual == "VERDE":
            color_pin = "green"
            icono_pin = "ok-circle"

    # --- DISEÑO A DOS COLUMNAS ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📍 Mapa de Riesgo en Tiempo Real")
        
        # Crear el mapa base centrado en Asunción
        mapa = folium.Map(location=[-25.295, -57.62], zoom_start=13)
        
        # Configurar el mensaje emergente (Popup) del pin
        if estado_actual == "ROJO":
            popup_html = f"<b>¡PELIGRO! Zona Inundada</b><br>Distancia al agua: {nivel_agua} cm<br>Hora: {fecha_hora}"
        elif estado_actual == "VERDE":
            popup_html = f"<b>Vía Segura</b><br>Distancia al agua: {nivel_agua} cm<br>Hora: {fecha_hora}"
        else:
            popup_html = "Nodo S.I.M.U.R. - Sin conexión"

        # Colocar el Pin interactivo en el mapa
        folium.Marker(
            [LATITUD_NODO, LONGITUD_NODO],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip="Punto Crítico 1 (Click para ver)",
            icon=folium.Icon(color=color_pin, icon=icono_pin)
        ).add_to(mapa)

        # Mostrar el mapa en Streamlit
        st_folium(mapa, width=700, height=500)

    with col2:
        st.subheader("📊 Estado Actual del Nodo")
        
        # Tarjeta de alerta gigante
        if estado_actual == "ROJO":
            st.error(f"🚨 **ALERTA ROJA ACTIVA**\n\nEvite transitar por esta intersección. Riesgo validado por IA.")
        elif estado_actual == "VERDE":
            st.success(f"✅ **VÍA SEGURA**\n\nEl tránsito es fluido y seguro.")
        else:
            st.warning("⚠️ Sin datos recientes.")

        # Métricas
        st.metric(label="Distancia medida (Sensor HC-SR04)", value=f"{nivel_agua} cm")
        st.caption(f"Última lectura: {fecha_hora}")

        st.divider()
        
        # Historial para la PMT
        st.subheader("📋 Historial de Eventos (PMT)")
        if not historial_df.empty:
            # Mostramos una tabla bonita y limpia
            st.dataframe(
                historial_df[['timestamp', 'nivel_agua_cm', 'estado_alerta']], 
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No hay registros en la base de datos.")

if __name__ == "__main__":
    main()