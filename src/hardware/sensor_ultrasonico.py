# src/hardware/sensor_ultrasonico.py
import random
import time

def medir_distancia(conexion_serial=None):
    """
    Lee la distancia desde el sensor HC-SR04.
    """
    if conexion_serial is None:
        # --- MODO SIMULACIÓN ---
        distancia_simulada = round(random.uniform(5.0, 25.0), 1)
        print(f"[Hardware] (Simulado) Distancia del sensor: {distancia_simulada} cm")
        time.sleep(0.1) 
        return distancia_simulada
    else:
        # --- MODO ARDUINO REAL ---
        try:
            conexion_serial.write(b'GET_DISTANCIA\n')
            respuesta = conexion_serial.readline().decode('utf-8').strip()
            distancia_real = float(respuesta)
            print(f"[Hardware] Distancia real leída: {distancia_real} cm")
            return distancia_real
        except Exception as e:
            print(f"[ERROR Hardware] Fallo de comunicación con sensor HC-SR04: {e}")
            return 25.0 

def medir_lluvia(conexion_serial=None):
    """
    Lee los milímetros de lluvia acumulados en el pluviómetro.
    """
    if conexion_serial is None:
        # --- MODO SIMULACIÓN ---
        lluvia_simulada = round(random.uniform(0.0, 5.0), 1)
        print(f"[Hardware] (Simulado) Lluvia acumulada: {lluvia_simulada} mm")
        return lluvia_simulada
    else:
        # --- MODO ARDUINO REAL ---
        try:
            conexion_serial.write(b'GET_LLUVIA\n')
            respuesta = conexion_serial.readline().decode('utf-8').strip()
            lluvia_real = float(respuesta)
            print(f"[Hardware] Lluvia real acumulada: {lluvia_real} mm")
            return lluvia_real
        except Exception as e:
            print(f"[ERROR Hardware] Fallo de comunicación con pluviómetro: {e}")
            return 0.0