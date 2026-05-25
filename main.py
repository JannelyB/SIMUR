# main.py
import time
import sys
import os

# Aseguramos que Python encuentre nuestros módulos en la carpeta 'src'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database import inicializar_db, registrar_evento
from src.hardware import medir_distancia, activar_alerta_roja, activar_alerta_verde
from src.vision import capturar_fotografia, DetectorRaudalIA

# --- CONFIGURACIONES GLOBALES ---
UMBRAL_PELIGRO_CM = 15.0  # Si el agua está a menos de 15cm del sensor, hay posible peligro
TIEMPO_ESPERA = 3         # Segundos entre cada lectura del sensor

def main():
    print("="*60)
    print(" 🚀 INICIANDO SISTEMA S.I.M.U.R. (NÚCLEO PRINCIPAL) 🚀")
    print("="*60)

    # 1. Preparar la Base de Datos
    inicializar_db()

    # 2. Inicializar la Inteligencia Artificial
    detector = DetectorRaudalIA()

    # 3. Conexión Serial al Arduino 
    # (Lo dejamos en None para que use el Modo Simulación por ahora. 
    # Cuando conectes el Arduino, aquí pondremos la ruta, ej: conexion = serial.Serial('COM3', 9600))
    conexion_arduino = None 

    # Variable para no llenar la base de datos con el mismo evento a cada segundo
    estado_anterior = None

    print("\n[Sistema] Entrando en ciclo de monitoreo continuo. (Presiona Ctrl+C para salir)\n")

    while True:
        try:
            # --- FASE 1: ENTRADA (Percepción) ---
            distancia = medir_distancia(conexion_arduino)

            # --- FASE 2: DECISIÓN (Procesamiento Lógico) ---
            if distancia <= UMBRAL_PELIGRO_CM:
                print(f"\n⚠️ [ALERTA] Nivel crítico detectado ({distancia} cm). Iniciando validación visual...")
                
                # Tomar foto de la calle
                foto_ok = capturar_fotografia()

                if foto_ok:
                    # Validación Secundaria con Inteligencia Artificial
                    es_raudal, etiqueta = detector.evaluar_imagen()

                    if es_raudal:
                        # --- FASE 3: ACCIÓN (Raudal Confirmado) ---
                        activar_alerta_roja(conexion_arduino)
                        
                        # Guardar en BD solo si acaba de cambiar a Rojo
                        if estado_anterior != "ROJO":
                            registrar_evento(distancia, validacion_ia=True, estado_alerta="ROJO")
                            estado_anterior = "ROJO"
                    else:
                        # --- FASE 3: ACCIÓN (Falso Positivo) ---
                        print(f"✅ [IA] Falso positivo descartado. Se detectó: '{etiqueta}'. Manteniendo vía segura.")
                        activar_alerta_verde(conexion_arduino)
                        
                        if estado_anterior != "VERDE":
                            registrar_evento(distancia, validacion_ia=False, estado_alerta="VERDE")
                            estado_anterior = "VERDE"
                else:
                    print("❌ [ERROR] No se pudo validar con la cámara.")

            else:
                # --- FASE 3: ACCIÓN (Seguro / Lejos del umbral) ---
                activar_alerta_verde(conexion_arduino)
                
                # Guardar en BD solo si acaba de cambiar a Verde
                if estado_anterior != "VERDE":
                    registrar_evento(distancia, validacion_ia=False, estado_alerta="VERDE")
                    estado_anterior = "VERDE"

            # Esperar unos segundos antes de la siguiente medición
            time.sleep(TIEMPO_ESPERA)

        except KeyboardInterrupt:
            # Captura cuando el usuario presiona Ctrl+C en la consola
            print("\n🛑 [Sistema] Apagando S.I.M.U.R. Monitoreo detenido.")
            break
        except Exception as e:
            print(f"\n[ERROR CRÍTICO] {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()