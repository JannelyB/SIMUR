    SIMUR_Project/
    │
    ├── data/                       # Carpeta para almacenar datos locales
    │   └── simur_logs.db           # Archivo de la base de datos SQLite (se crea solo)
    │
    ├── models/                     # Carpeta para los archivos de Inteligencia Artificial
    │   ├── raudal_model.tflite     # Modelo de red neuronal (TensorFlow Lite)
    │   └── labels.txt              # Etiquetas del modelo (ej. 0: Seco, 1: Inundado)
    │
    ├── src/                        # Código fuente (Módulos principales)
    │   ├── __init__.py             # Hace que la carpeta 'src' sea un módulo de Python
    │   │
    │   ├── hardware/               # Fase de ENTRADA y ACCIÓN física
    │   │   ├── __init__.py
    │   │   ├── sensor_ultrasonico.py # Lógica para leer la distancia del HC-SR04
    │   │   └── alarmas_led.py      # Lógica para encender luces/buzzer vía GPIO
    │   │
    │   ├── vision/                 # Fase de PERCEPCIÓN VISUAL
    │   │   ├── __init__.py
    │   │   ├── camara.py           # Script de OpenCV para tomar la foto
    │   │   └── detector_ia.py      # Carga TFLite y evalúa la foto
    │   │
    │   └── database/               # Almacenamiento
    │       ├── __init__.py
    │       └── db_manager.py       # Funciones para guardar eventos en SQLite
    ├── web/                        <-- NUEVA CARPETA PARA EL FRONTEND
    │   └── app.py  
    │
    ├── config.py                   # Configuraciones globales (pines, umbrales)
    ├── main.py                     # EL NÚCLEO: Ejecuta todo el sistema
    ├── requirements.txt            # Lista de librerías instaladas
    └── README.md                   # Instrucciones para arrancar el proyecto