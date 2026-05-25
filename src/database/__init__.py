# src/database/__init__.py

"""
Módulo de Base de Datos para S.I.M.U.R.
Expone las funciones principales de db_manager para que puedan ser 
importadas fácilmente desde main.py (hardware) y app.py (frontend web).
"""

from .db_manager import (
    inicializar_db,
    registrar_evento,
    obtener_estado_actual,
    obtener_historial
)

# Definimos qué funciones están disponibles al hacer 'from src.database import *'
__all__ = [
    "inicializar_db",
    "registrar_evento",
    "obtener_estado_actual",
    "obtener_historial"
]