# src/vision/__init__.py

"""
Módulo de Visión Artificial para S.I.M.U.R.
Expone las funciones de cámara y el detector de IA.
"""

from .camara import capturar_fotografia
from .detector_ia import DetectorRaudalIA

__all__ = [
    "capturar_fotografia",
    "DetectorRaudalIA"
]