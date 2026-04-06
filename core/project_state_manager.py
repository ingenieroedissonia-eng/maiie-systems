"""
MAIIE System V2 - Project State Manager
Modulo: Estado del proyecto durante ejecucion de submisiones
Capa: Core
Version: 1.0.0
"""

import logging
from typing import Dict, Optional, List

logger = logging.getLogger("MAIIE.ProjectStateManager")


class ProjectStateManager:
    """
    Mantiene el estado del proyecto durante la ejecucion del PlannerExecutor.
    Registra que archivos han sido generados y sus contenidos,
    permitiendo al AUDITOR verificar dependencias reales entre archivos.
    """

    def __init__(self):
        self._archivos: Dict[str, str] = {}

    def registrar(self, ruta: str, contenido: str) -> None:
        self._archivos[ruta] = contenido
        logger.info(f"Archivo registrado en estado del proyecto: {ruta}")

    def existe(self, ruta: str) -> bool:
        return ruta in self._archivos

    def obtener(self, ruta: str) -> Optional[str]:
        return self._archivos.get(ruta)

    def listar(self) -> List[str]:
        return list(self._archivos.keys())

    def resumen(self) -> str:
        if not self._archivos:
            return "Proyecto vacio"
        lineas = ["ARCHIVOS GENERADOS EN EL PROYECTO:"]
        for ruta in sorted(self._archivos.keys()):
            lineas.append(f"  - {ruta}")
        return "\n".join(lineas)

    def reset(self) -> None:
        self._archivos.clear()
        logger.info("Estado del proyecto reiniciado")