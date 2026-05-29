# src/vision/detector_ia.py
import cv2
import numpy as np
import os
import random
import time

try:
    import tensorflow.lite.python.interpreter as litert
except ImportError:
    try:
        import tflite_runtime.interpreter as litert
    except ImportError:
        pass # Si falla, usaremos el modo simulación

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUTA_MODELO = os.path.join(BASE_DIR, 'models', 'raudal_model.tflite')
RUTA_LABELS = os.path.join(BASE_DIR, 'models', 'labels.txt')
RUTA_IMAGEN_DEFAULT = os.path.join(BASE_DIR, 'data', 'captura_actual.jpg')

class DetectorRaudalIA:
    def __init__(self, model_path=RUTA_MODELO, labels_path=RUTA_LABELS):
        print("[IA] Inicializando módulo de Visión...")
        self.modo_simulacion = False
        
        # Validar si el modelo existe y si tiene un tamaño válido (más de 10 bytes)
        if not os.path.exists(model_path) or os.path.getsize(model_path) < 10:
            print("[WARNING IA] Modelo TFLite vacío o no encontrado.")
            print("[WARNING IA] -> ACTIVANDO IA EN MODO SIMULACIÓN <-")
            self.modo_simulacion = True
            return
            
        try:
            # Intentar cargar el modelo real
            self.interpreter = litert.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.height = self.input_details[0]['shape'][1]
            self.width = self.input_details[0]['shape'][2]
            
            with open(labels_path, 'r') as f:
                self.labels = [line.strip() for line in f.readlines()]
            print("[IA] Modelo real cargado con éxito.")
                
        except Exception as e:
            print(f"[WARNING IA] Error al cargar modelo real: {e}")
            print("[WARNING IA] -> ACTIVANDO IA EN MODO SIMULACIÓN <-")
            self.modo_simulacion = True

    def evaluar_imagen(self, ruta_imagen=RUTA_IMAGEN_DEFAULT):
        if self.modo_simulacion:
            # --- MODO SIMULACIÓN (Cuando no tienes el modelo web) ---
            print("[IA Simulada] Analizando los píxeles de la foto...")
            time.sleep(1) # Simulamos que la computadora está "pensando"
            
            # Simularemos que la IA confirma el raudal el 80% de las veces
            es_raudal = random.choice([True, True, True, True, False])
            
            if es_raudal:
                etiqueta = "1 Raudal Detectado (Simulado)"
                print(f"[IA Simulada] Resultado: {etiqueta} (98.5%)")
            else:
                etiqueta = "0 Basura/Seco (Simulado)"
                print(f"[IA Simulada] Resultado: Falso Positivo / {etiqueta} (85.2%)")
                
            return es_raudal, etiqueta
            
        # --- MODO REAL (Se activará solo cuando pongas tu modelo real en la carpeta) ---
        img = cv2.imread(ruta_imagen)
        if img is None:
            return False, "ERROR_IMAGEN"
            
        img_resized = cv2.resize(img, (self.width, self.height))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        input_data = np.expand_dims(img_rgb, axis=0).astype(np.float32) / 255.0

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        idx_predicho = np.argmax(output_data[0])
        porcentaje = output_data[0][idx_predicho] * 100
        etiqueta_predicha = self.labels[idx_predicho].lower()
        
        es_raudal = "raudal" in etiqueta_predicha or "inundado" in etiqueta_predicha or "peligro" in etiqueta_predicha
        print(f"[IA Real] Resultado: {etiqueta_predicha.upper()} ({porcentaje:.2f}%)")
        return es_raudal, etiqueta_predicha