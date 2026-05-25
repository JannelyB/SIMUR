# src/hardware/alarmas_led.py

def activar_alerta_roja(conexion_serial=None):
    """
    Enciende el LED Rojo y el Buzzer (Alarma de Raudal).
    Apaga el LED Verde.
    """
    if conexion_serial is None:
        # --- MODO SIMULACIÓN ---
        print("\n🔴 [Actuador] (Simulado) -> ALARMA FÍSICA ACTIVADA (LED Rojo / Buzzer ON)")
    else:
        # --- MODO ARDUINO REAL ---
        try:
            # Enviamos el comando 'SET_ROJO' al Arduino
            conexion_serial.write(b'SET_ROJO\n')
            print("🔴 [Actuador] Comando enviado a Arduino: Alarma FÍSICA ON")
        except Exception as e:
            print(f"[ERROR Actuador] No se pudo activar la alarma: {e}")


def activar_alerta_verde(conexion_serial=None):
    """
    Enciende el LED Verde (Vía Segura).
    Apaga el LED Rojo y el Buzzer.
    """
    if conexion_serial is None:
        # --- MODO SIMULACIÓN ---
        print("\n🟢 [Actuador] (Simulado) -> VÍA SEGURA (LED Verde ON)")
    else:
        # --- MODO ARDUINO REAL ---
        try:
            # Enviamos el comando 'SET_VERDE' al Arduino
            conexion_serial.write(b'SET_VERDE\n')
            print("🟢 [Actuador] Comando enviado a Arduino: Vía Segura ON")
        except Exception as e:
            print(f"[ERROR Actuador] No se pudo activar vía segura: {e}")