# src/vision/detector_ia.py
import cv2
import numpy as np
import os

# Intentamos importar el intérprete. Dependiendo de cómo lo hayas instalado,
# puede llamarse de distintas maneras. Tu código original usa litert.
try:
    import ai_edge_litert.interpreter as litert
except ImportError:
    try:
        import tflite_runtime.interpreter as litert
    except ImportError:
        from tensorflow.lite.python import interpreter as litert

# Rutas absolutas para encontrar los modelos y la imagen
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUTA_MODELO = os.path.join(BASE_DIR, 'models', 'raudal_model.tflite')
RUTA_LABELS = os.path.join(BASE_DIR, 'models', 'labels.txt')
RUTA_IMAGEN_DEFAULT = os.path.join(BASE_DIR, 'data', 'captura_actual.jpg')

class DetectorRaudalIA:
    def __init__(self, model_path=RUTA_MODELO, labels_path=RUTA_LABELS):
        print("[IA] Cargando modelo neuronal...")
        
        # Validar que los archivos existan antes de intentar cargarlos
        if not os.path.exists(model_path) or not os.path.exists(labels_path):
            print(f"[ERROR IA] Faltan archivos en la carpeta 'models/'. Verifica que existan.")
            self.valido = False
            return
            
        self.valido = True
        
        # Inicializar el intérprete ligero
        self.interpreter = litert.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Extraer dimensiones (Teachable Machine suele usar 224x224)
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        
        # Cargar etiquetas
        with open(labels_path, 'r') as f:
            # Eliminamos los números que Teachable Machine pone al principio (ej: "0 Seco", "1 Raudal")
            self.labels = [line.strip() for line in f.readlines()]
            print(f"[IA] Etiquetas cargadas: {self.labels}")

    def evaluar_imagen(self, ruta_imagen=RUTA_IMAGEN_DEFAULT):
        if not self.valido:
            return False, "Modelo no cargado"
            
        img = cv2.imread(ruta_imagen)
        if img is None:
            print(f"[ERROR IA] No se encontró la imagen en {ruta_imagen}")
            return False, "ERROR_IMAGEN"
            
        # Adecuar la imagen para la red neuronal
        img_resized = cv2.resize(img, (self.width, self.height))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # Expandir dimensiones y normalizar (0 a 1)
        input_data = np.expand_dims(img_rgb, axis=0).astype(np.float32) / 255.0

        # Ejecutar inferencia
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        # Obtener resultados
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        idx_predicho = np.argmax(output_data[0])
        porcentaje = output_data[0][idx_predicho] * 100
        etiqueta_predicha = self.labels[idx_predicho].lower()
        
        print(f"[IA] Resultado: {etiqueta_predicha.upper()} ({porcentaje:.2f}%)")
        
        # LÓGICA DE DECISIÓN: Si la etiqueta contiene la palabra "raudal" o "inundado"
        es_raudal = "raudal" in etiqueta_predicha or "inundado" in etiqueta_predicha or "peligro" in etiqueta_predicha
        
        return es_raudal, etiqueta_predicha