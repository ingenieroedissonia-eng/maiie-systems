"""
MAIIE System V2
Mission Data Contract
Define la estructura de datos de una misión.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Mission:

    # Identidad de la misión
    mission_id: str
    timestamp: datetime

    # Entrada del usuario
    orden_usuario: str

    # Resultados del pipeline
    arquitectura: Optional[str] = None
    implementacion: Optional[str] = None
    auditoria: Optional[str] = None

    # Estado final
    aprobado: bool = False
    iteracion_final: int = 0

    # Artefacto generado
    artefacto_codigo: Optional[str] = None