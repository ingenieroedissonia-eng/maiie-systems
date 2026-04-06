"""
Módulo: Exceptions
Capa: Core

Descripción:
Define las excepciones personalizadas para el sistema RAG.
Estas excepciones permiten un manejo de errores más granular y específico
del dominio en toda la aplicación.

Responsabilidades:
- Definir la excepción base `RagException`.
- Definir excepciones específicas que heredan de la base para diferentes
  escenarios de error (e.g., documento no encontrado, error de embedding).

Versión: 1.0.0
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RagException(Exception):
    """Clase base para excepciones en la aplicación RAG."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Inicializa la excepción base.

        Args:
            message: Mensaje de error descriptivo.
            context: Un diccionario con contexto adicional sobre el error.
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
        logger.error(
            f"RagException: {self.message}",
            extra={"exception_context": self.context}
        )

    def __str__(self) -> str:
        """Representación en cadena de la excepción."""
        if self.context:
            return f"{self.message} (Contexto: {self.context})"
        return self.message


class DocumentNotFound(RagException):
    """Excepción lanzada cuando un documento no se encuentra en el sistema."""

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción de documento no encontrado.

        Args:
            document_id: El ID del documento que no fue encontrado.
            message: Un mensaje descriptivo opcional.
        """
        self.document_id = document_id
        if message is None:
            message = f"El documento con ID '{self.document_id}' no fue encontrado."

        context = {"document_id": self.document_id}
        super().__init__(message, context=context)


class DocumentAlreadyExists(RagException):
    """Excepción lanzada al intentar crear un documento que ya existe."""

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción de documento ya existente.

        Args:
            document_id: El ID del documento que ya existe.
            message: Un mensaje descriptivo opcional.
        """
        self.document_id = document_id
        if message is None:
            message = f"El documento con ID '{self.document_id}' ya existe."

        context = {"document_id": self.document_id}
        super().__init__(message, context=context)


class EmbeddingGenerationError(RagException):
    """Excepción lanzada cuando falla la generación de embeddings."""

    def __init__(self, document_id: str, model_used: str, original_error: Optional[Exception] = None, message: Optional[str] = None):
        """
        Inicializa la excepción de error de generación de embedding.

        Args:
            document_id: El ID del documento para el cual falló la generación.
            model_used: El nombre del modelo de embedding que se estaba utilizando.
            original_error: La excepción original que causó el fallo, si la hubo.