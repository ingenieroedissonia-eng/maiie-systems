"""
Módulo: Exceptions
Capa: Core

Descripción:
Define las excepciones personalizadas para el sistema RAG (Retrieval-Augmented Generation).
Estas excepciones permiten un manejo de errores más granular y específico del dominio.

Responsabilidades:
- Proveer una excepción base `RagException` para todos los errores del sistema.
- Definir excepciones específicas para escenarios comunes como documentos no encontrados,
  documentos duplicados, errores de embedding y errores de consulta.

Versión: 1.2.0
"""

import logging
from typing import Any, Dict, Optional

# Configuración básica del logger para este módulo
logger = logging.getLogger(__name__)


class RagException(Exception):
    """Excepción base para todos los errores controlados en la aplicación RAG."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Inicializa la excepción.

        Args:
            message: El mensaje de error principal.
            context: Un diccionario con información contextual sobre el error.
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
        logger.debug(f"RagException raised: {message}, Context: {self.context}")

    def __str__(self) -> str:
        """Representación en cadena de la excepción."""
        if self.context:
            return f"{self.message} (Context: {self.context})"
        return self.message


class DocumentNotFound(RagException):
    """Excepción lanzada cuando un documento específico no se encuentra."""

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción DocumentNotFound.

        Args:
            document_id: El ID del documento que no fue encontrado.
            message: Mensaje de error personalizado. Si es None, se usa uno por defecto.
        """
        final_message = message or f"Document with ID '{document_id}' not found."
        context = {"document_id": document_id}
        super().__init__(final_message, context)


class DocumentAlreadyExists(RagException):
    """Excepción lanzada al intentar añadir un documento que ya existe."""

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción DocumentAlreadyExists.

        Args:
            document_id: El ID del documento que ya existe.
            message: Mensaje de error personalizado. Si es None, se usa uno por defecto.
        """
        final_message = message or f"Document with ID '{document_id}' already exists."
        context = {"document_id": document_id}
        super().__init__(final_message, context)