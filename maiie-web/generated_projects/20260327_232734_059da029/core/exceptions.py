"""
Módulo: Exceptions
Capa: Core

Descripción:
Define las excepciones personalizadas para el sistema RAG.

Responsabilidades:
- Proporcionar una clase de excepción base (RagException).
- Definir excepciones específicas para diferentes escenarios de error.

Versión: 1.0.0
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RagException(Exception):
    """Excepción base para todos los errores en el sistema RAG."""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Inicializa la excepción base.

        Args:
            message: Mensaje de error descriptivo.
            context: Diccionario con información contextual sobre el error.
        """
        super().__init__(message)
        self.message = message
        self.context = context if context is not None else {}
        logger.error(f"{self.__class__.__name__}: {self.message}", extra={"context": self.context})

    def __str__(self) -> str:
        """Representación en cadena de la excepción."""
        if self.context:
            return f"{self.message} - Context: {self.context}"
        return self.message


class DocumentNotFound(RagException):
    """Excepción lanzada cuando un documento no se encuentra."""
    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción de documento no encontrado.

        Args:
            document_id: El ID del documento que no se encontró.
            message: Mensaje de error opcional para sobrescribir el predeterminado.
        """
        default_message = f"Document with ID '{document_id}' not found."
        super().__init__(message or default_message, {"document_id": document_id})


class DocumentAlreadyExists(RagException):
    """Excepción lanzada cuando se intenta crear un documento que ya existe."""
    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción de documento ya existente.

        Args:
            document_id: El ID del documento que ya existe.
            message: Mensaje de error opcional para sobrescribir el predeterminado.
        """
        default_message = f"Document with ID '{document_id}' already exists."
        super().__init__(message or default_message, {"document_id": document_id})


class EmbeddingGenerationError(RagException):
    """Excepción lanzada cuando falla la generación de embeddings."""
    def __init__(self, model_id: Optional[str] = None, message: Optional[str] = None):
        """
        Inicializa la excepción de error en la generación de embeddings.

        Args:
            model_id: El ID del modelo de embedding que falló.
            message: Mensaje de error opcional para sobrescribir el predeterminado.
        """
        default_message = "Failed to generate embeddings."
        if model_id:
            default_message += f" using model '{model_id}'."
        super().__init__(message or default_message, {"model_id": model_id})


class QueryError(RagException):
    """Excepción lanzada cuando ocurre un error durante una operación de consulta."""
    def __init__(self, query: str, message: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Inicializa la excepción de error de consulta.

        Args:
            query: La consulta que causó el error.
            message: Mensaje de error opcional para sobrescribir el predeterminado.
            context: Contexto adicional sobre el error.
        """
        default_message = "An error occurred during query execution."
        final_context = {"query": query, **(context if context is not None else {})}
        super().__init__(message or default_message, final_context)