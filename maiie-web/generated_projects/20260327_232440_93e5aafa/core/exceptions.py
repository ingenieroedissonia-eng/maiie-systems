"""
Módulo: Excepciones del Core
Capa: Core

Descripción:
Define las excepciones personalizadas para el sistema RAG (Retrieval-Augmented Generation).
Esto permite un manejo de errores más granular y específico del dominio.

Responsabilidades:
- Definir la excepción base `RagException`.
- Definir excepciones específicas que heredan de la base para diferentes escenarios de error.

Versión: 1.1.0
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RagException(Exception):
    """Clase base para todas las excepciones personalizadas del sistema RAG."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Inicializa la excepción base.

        Args:
            message (str): Mensaje de error descriptivo.
            context (Optional[Dict[str, Any]]): Datos adicionales para depuración.
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
        logger.debug(f"RagException raised: {self.message}, Context: {self.context}")

    def __str__(self) -> str:
        """Representación en cadena de la excepción, incluyendo el contexto si existe."""
        if self.context:
            return f"{self.message} (Context: {self.context})"
        return self.message


class DocumentNotFound(RagException):
    """
    Excepción lanzada cuando no se encuentra un documento específico.

    Esta excepción se utiliza para señalar que una operación que requiere un
    documento por su identificador no pudo localizarlo en el sistema de
    almacenamiento.
    """

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción DocumentNotFound.

        Args:
            document_id (str): El ID del documento que no se pudo encontrar.
            message (Optional[str]): Un mensaje de error personalizado. Si no se proporciona,
                                     se usará uno por defecto.
        """
        final_message = message or f"El documento con ID '{document_id}' no fue encontrado."
        context = {"document_id": document_id}
        super().__init__(final_message, context=context)
        logger.warning(f"DocumentNotFound: {final_message}")