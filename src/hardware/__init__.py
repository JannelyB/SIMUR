# src/hardware/__init__.py

"""
Módulo de Hardware para S.I.M.U.R.
Expone las funciones para interactuar con el sensor ultrasónico y las luces LED.
"""

from .sensor_ultrasonico import medir_distancia
from .alarmas_led import activar_alerta_roja, activar_alerta_verde

__all__ = [
    "medir_distancia",
    "activar_alerta_roja",
    "activar_alerta_verde"
]