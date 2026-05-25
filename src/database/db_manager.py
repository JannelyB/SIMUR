# src/database/db_manager.py

import sqlite3
import os
from datetime import datetime

# Calculamos la ruta absoluta hacia la carpeta 'data' en la raíz del proyecto
# Esto asegura que sin importar desde dónde ejecutes el código, la BD siempre
# se guardará en SIMUR_Project/data/simur_logs.db
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_POR_DEFECTO = os.path.join(DIRECTORIO_ACTUAL, '..', '..', 'data', 'simur_logs.db')

def inicializar_db(ruta_db=RUTA_POR_DEFECTO):
    """
    Crea la base de datos SQLite y la tabla 'registro_raudales' si no existen.
    Esta función debe llamarse al iniciar el sistema (main.py).
    """
    # Aseguramos que la carpeta 'data' exista antes de crear el archivo
    os.makedirs(os.path.dirname(ruta_db), exist_ok=True)
    
    # Conectamos a la base de datos (se crea el archivo si no existe)
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    
    # Creamos la tabla principal según el Documento MVP
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_raudales (
            id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            nivel_agua_cm REAL NOT NULL,
            validacion_ia BOOLEAN NOT NULL,
            estado_alerta VARCHAR(20) NOT NULL
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print(f"[DB] Base de datos lista en: {os.path.normpath(ruta_db)}")


def registrar_evento(nivel_agua_cm, validacion_ia, estado_alerta, ruta_db=RUTA_POR_DEFECTO):
    """
    Inserta una nueva lectura del sensor en la base de datos.
    
    Parámetros:
    - nivel_agua_cm (float): Distancia o nivel medido por el HC-SR04.
    - validacion_ia (bool): True si TFLite confirma raudal, False si no.
    - estado_alerta (str): "VERDE", "AMARILLO" o "ROJO".
    """
    try:
        # Agregamos timeout=5.0 para evitar errores de "Database is locked" 
        # si la web está leyendo la DB al mismo tiempo que el hardware escribe
        conexion = sqlite3.connect(ruta_db, timeout=5.0)
        cursor = conexion.cursor()
        
        # Capturamos la hora exacta del sistema local
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO registro_raudales (timestamp, nivel_agua_cm, validacion_ia, estado_alerta)
            VALUES (?, ?, ?, ?)
        ''', (ahora, nivel_agua_cm, validacion_ia, estado_alerta))
        
        conexion.commit()
        conexion.close()
        print(f"[DB] Evento registrado: {ahora} | Nivel: {nivel_agua_cm}cm | Alerta: {estado_alerta}")
    except sqlite3.Error as e:
        print(f"[DB ERROR] Fallo al registrar evento: {e}")

def obtener_estado_actual(ruta_db=RUTA_POR_DEFECTO):
    """
    Devuelve el registro más reciente. 
    Es utilizado por el Frontend (Streamlit) para saber de qué color 
    pintar el marcador en el mapa.
    """
    if not os.path.exists(ruta_db):
        return None
        
    conexion = sqlite3.connect(ruta_db)
    # Convertimos los resultados a diccionarios en lugar de tuplas para facilitar su uso
    conexion.row_factory = sqlite3.Row 
    cursor = conexion.cursor()
    
    cursor.execute('''
        SELECT * FROM registro_raudales
        ORDER BY id_registro DESC
        LIMIT 1
    ''')
    
    registro = cursor.fetchone()
    conexion.close()
    
    if registro:
        return dict(registro)
    return None


def obtener_historial(limite=50, ruta_db=RUTA_POR_DEFECTO):
    """
    Devuelve los últimos N registros.
    Útil para el panel de control (Dashboard) de la PMT.
    """
    if not os.path.exists(ruta_db):
        return []
        
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    cursor.execute('''
        SELECT * FROM registro_raudales
        ORDER BY id_registro DESC
        LIMIT ?
    ''', (limite,))
    
    registros = [dict(fila) for fila in cursor.fetchall()]
    conexion.close()
    
    return registros


def obtener_estadisticas(ruta_db=RUTA_POR_DEFECTO):
    """
    Calcula estadísticas básicas para el Dashboard de la PMT.
    Devuelve el total de mediciones y cuántas de ellas han sido alertas ROJAS.
    """
    if not os.path.exists(ruta_db):
        return {"total": 0, "alertas_rojas": 0}
        
    try:
        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()
        
        # Total de registros históricos
        cursor.execute('SELECT COUNT(*) FROM registro_raudales')
        total_eventos = cursor.fetchone()[0]
        
        # Total de alertas de peligro detectadas
        cursor.execute('SELECT COUNT(*) FROM registro_raudales WHERE estado_alerta = "ROJO"')
        alertas_rojas = cursor.fetchone()[0]
        
        conexion.close()
        return {"total": total_eventos, "alertas_rojas": alertas_rojas}
    except sqlite3.Error as e:
        print(f"[DB ERROR] No se pudieron obtener las estadísticas: {e}")
        return {"total": 0, "alertas_rojas": 0}


def limpiar_historial(ruta_db=RUTA_POR_DEFECTO):
    """
    Borra todos los registros de la base de datos.
    Muy útil para limpiar los datos antes de la defensa o tras pruebas de la maqueta.
    """
    if not os.path.exists(ruta_db):
        return
        
    try:
        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()
        cursor.execute('DELETE FROM registro_raudales')
        
        # Opcional: Reiniciar el contador del ID automático
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="registro_raudales"')
        
        conexion.commit()
        conexion.close()
        print("[DB] Historial de raudales limpiado exitosamente.")
    except sqlite3.Error as e:
        print(f"[DB ERROR] Error al limpiar el historial: {e}")

# Bloque de prueba: Si ejecutas este archivo directamente, probará la BD.
if __name__ == "__main__":
    print("--- Prueba de Base de Datos S.I.M.U.R ---")
    inicializar_db()
    registrar_evento(16.5, True, "ROJO")
    estado = obtener_estado_actual()
    print(f"Estado actual recuperado: {estado}")
    
    stats = obtener_estadisticas()
    print(f"Estadísticas recuperadas: {stats}")
    
    # Descomentar la siguiente línea para limpiar la DB antes de la presentación
    # limpiar_historial()