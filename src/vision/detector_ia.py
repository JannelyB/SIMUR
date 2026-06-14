import cv2
import numpy as np
import os
import random
import time
import importlib

# Intentar cargar la librería de TFLite
litert = None
for module_name in ('tensorflow.lite.python.interpreter', 'tflite_runtime.interpreter'):
    try:
        litert = importlib.import_module(module_name)
        break
    except ImportError:
        continue

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUTA_MODELO = os.path.join(BASE_DIR, 'models', 'raudal_model.tflite')
RUTA_LABELS = os.path.join(BASE_DIR, 'models', 'labels.txt')
RUTA_IMAGEN_DEFAULT = os.path.join(BASE_DIR, 'data', 'captura_actual.jpg')

class DetectorRaudalIA:
    def __init__(self, model_path=RUTA_MODELO, labels_path=RUTA_LABELS):
        print("[IA] Inicializando módulo de Visión...")
        self.modo_simulacion = False
        
        # Validación estricta: Si no hay modelo, NO permitimos simulaciones aleatorias
        # que provoquen falsos positivos en producción.
        if not os.path.exists(model_path):
            print(f"[ERROR IA] Modelo no encontrado en: {model_path}")
            print("[CRÍTICO] MODO DE SEGURIDAD ACTIVADO: El sistema no activará alarmas sin IA real.")
            self.modo_simulacion = True 
            self.interpreter = None
            return
            
        try:
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
            print(f"[ERROR IA] Fallo crítico al cargar modelo: {e}")
            self.modo_simulacion = True

    def evaluar_imagen(self, ruta_imagen=RUTA_IMAGEN_DEFAULT):
        if self.modo_simulacion:
            print("[IA] ADVERTENCIA: El sistema está en modo seguro. No se puede confirmar el raudal.")
            # Retornamos False obligatoriamente para evitar falsos positivos
            return False, "SISTEMA_SIN_MODELO_IA"
            
        img = cv2.imread(ruta_imagen)
        if img is None:
            return False, "ERROR_IMAGEN_NO_ENCONTRADA"
            
        img_resized = cv2.resize(img, (self.width, self.height))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        input_data = np.expand_dims(img_rgb, axis=0).astype(np.float32) / 255.0

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        idx_predicho = np.argmax(output_data[0])
        porcentaje = output_data[0][idx_predicho] * 100
        etiqueta_predicha = self.labels[idx_predicho].lower()
        
        # Filtro estricto: solo activamos si supera un 70% de confianza
        es_raudal = ("raudal" in etiqueta_predicha or "inundado" in etiqueta_predicha) and porcentaje > 70.0
        
        print(f"[IA Real] Predicción: {etiqueta_predicha.upper()} ({porcentaje:.2f}%)")
        return es_raudal, etiqueta_predicha