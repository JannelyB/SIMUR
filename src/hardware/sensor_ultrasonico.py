# src/hardware/sensor_ultrasonico.py

import random
import time

def medir_distancia(conexion_serial=None):
    """
    Lee la distancia desde el sensor HC-SR04.
    
    Parámetros:
    - conexion_serial: Objeto serial (pyserial) conectado al Arduino.
                       Si es None, funciona en Modo Simulación.
                       
    Retorna:
    - float: Distancia en centímetros.
    """
    if conexion_serial is None:
        # --- MODO SIMULACIÓN ---
        # Útil para programar el MVP sin tener la maqueta conectada
        
        # Simulamos que el fondo del recipiente está a 25 cm.
        # Si llueve, el número baja (ej. 10 cm = peligro).
        distancia_simulada = round(random.uniform(5.0, 25.0), 1)
        print(f"[Hardware] (Simulado) Distancia del sensor: {distancia_simulada} cm")
        
        # Pequeña pausa para simular el tiempo de lectura del sensor real
        time.sleep(0.5) 
        return distancia_simulada
        
    else:
        # --- MODO ARDUINO REAL ---
        try:
            # Enviamos el comando al Arduino para que lea el sensor
            conexion_serial.write(b'GET_DISTANCIA\n')
            
            # Leemos la respuesta del Arduino
            respuesta = conexion_serial.readline().decode('utf-8').strip()
            distancia_real = float(respuesta)
            
            print(f"[Hardware] Distancia real leída: {distancia_real} cm")
            return distancia_real
            
        except Exception as e:
            print(f"[ERROR Hardware] Fallo de comunicación con sensor: {e}")
            # Si hay error, retornamos un valor alto (seguro) para no disparar falsa alarma
            return 25.0