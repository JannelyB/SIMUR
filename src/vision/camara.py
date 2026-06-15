# src/vision/camara.py
import cv2
import os
import time

def capturar_fotografia():
    """
    Captura una fotografía utilizando la Webcam de la computadora mediante OpenCV.
    La imagen se guarda CRUDA (sin filtros) para que TensorFlow Lite 
    pueda reconocerla exactamente como fue entrenada en Teachable Machine.
    """
    print("[Visión] Encendiendo la cámara web...")
    
    cap = None
    # Probar los índices de cámara más comunes (0 suele ser la webcam integrada)
    for indice in [1]:
        cap_temp = cv2.VideoCapture(indice, cv2.CAP_DSHOW)  # Usar DirectShow para evitar problemas de bloqueo en Windows
        if cap_temp.isOpened():
            cap = cap_temp
            print(f"[Visión] Conectado a la cámara (índice {indice}).")
            break
        else:
            cap_temp.release()
            
    if cap is None or not cap.isOpened():
        print("❌ [ERROR Visión] No se pudo encontrar ni acceder a la webcam.")
        return False
        
    # Pequeña pausa de 1.5 segundos vital para que la cámara ajuste 
    # automáticamente el brillo, la exposición y el enfoque antes de la foto.
    time.sleep(1.5)
    
    # Limpiar el buffer de la cámara leyendo un par de frames ciegos
    for _ in range(3):
        cap.read()
        
    # Leer la foto real
    ret, frame = cap.read()
    
    if not ret:
        print("❌ [ERROR Visión] La cámara abrió pero no pudo tomar la fotografía.")
        cap.release()
        return False
        
    # Directorio de guardado
    directorio_datos = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    os.makedirs(directorio_datos, exist_ok=True)
    ruta_guardado = os.path.join(directorio_datos, "captura_actual.jpg")
    
    # Guardar imagen (completamente cruda)
    cv2.imwrite(ruta_guardado, frame)
    print(f"[OK OpenCV] Foto guardada exitosamente en: {ruta_guardado}")
    
    # Apagar la cámara para no saturar la computadora
    cap.release()
    return True

# Bloque de prueba individual:
# Puedes probar si funciona corriendo en terminal: python src/vision/camara.py
if __name__ == "__main__":
    capturar_fotografia()