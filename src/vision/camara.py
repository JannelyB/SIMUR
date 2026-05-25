# src/vision/camara.py
import cv2
import os

# Ruta absoluta hacia la carpeta 'data' del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUTA_POR_DEFECTO = os.path.join(BASE_DIR, 'data', 'captura_actual.jpg')

def capturar_fotografia(ruta_guardado=RUTA_POR_DEFECTO):
    """
    Activa la cámara web, toma una foto y la guarda.
    Retorna True si fue exitoso, False si falló.
    """
    # Asegurar que la carpeta data exista
    os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)
    
    print("[Visión] Encendiendo cámara...")
    # 0 activa la cámara web predeterminada de tu computadora
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR OpenCV] No se pudo acceder a la cámara física.")
        return False
    
    # Leer un frame de la cámara
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(ruta_guardado, frame)
        print(f"[OK OpenCV] Foto guardada exitosamente en: {ruta_guardado}")
    else:
        print("[ERROR OpenCV] No se pudo capturar el frame.")
        
    cap.release()
    return ret