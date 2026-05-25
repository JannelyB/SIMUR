# inicializar.py
import sys
import os

# Forzamos a Python a mirar primero en esta carpeta (Prioridad 0)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db_manager import inicializar_db, registrar_evento, obtener_historial

print("Iniciando la creación de la Base de Datos S.I.M.U.R...")

# 1. Crea el archivo .db y la tabla
inicializar_db()

# 2. Insertamos un par de datos de prueba para ver que funciona
print("Insertando datos de prueba...")
registrar_evento(nivel_agua_cm=2.5, validacion_ia=False, estado_alerta="VERDE")
registrar_evento(nivel_agua_cm=18.0, validacion_ia=True, estado_alerta="ROJO")

# 3. Leemos los datos para confirmar
print("\n--- Historial Registrado ---")
historial = obtener_historial(limite=5)
for registro in historial:
    print(f"ID: {registro['id_registro']} | Hora: {registro['timestamp']} | Nivel: {registro['nivel_agua_cm']}cm | Alerta: {registro['estado_alerta']}")

print("\n¡Proceso terminado con éxito!")