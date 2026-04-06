"""
Módulo: Exceptions
Capa: Core

Descripción:
Define las excepciones personalizadas para el dominio de la aplicación RAG.
Estas excepciones permiten un manejo de errores más granular y específico
en toda la aplicación.

Responsabilidades:
- Proporcionar una excepción base `RagException`.
- Definir excepciones específicas como `DocumentNotFound` y `DocumentAlreadyExists`.

Versión: 1.0.0
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RagException(Exception):
    """Excepción base para todos los errores personalizados en la aplicación."""

    def __init__(self, message: str):
        """
        Inicializa la excepción base.

        Args:
            message (str): El mensaje de error detallado.
        """
        self.message = message
        super().__init__(self.message)
        logger.error(f"{self.__class__.__name__}: {message}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}')"


class DocumentNotFound(RagException):
    """
    Excepción lanzada cuando no se encuentra un documento específico.
    """

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción de documento no encontrado.

        Args:
            document_id (str): El ID del documento que no se pudo encontrar.
            message (Optional[str]): Mensaje de error personalizado. Si es None,
                                     se genera un mensaje por defecto.
        """
        self.document_id = document_id
        if message is None:
            message = f"El documento con ID '{document_id}' no fue encontrado."
        super().__init__(message)

    def __repr__(self) -> str:
        return f"DocumentNotFound(document_id='{self.document_id}')"


class DocumentAlreadyExists(RagException):
    """
    Excepción lanzada al intentar crear un documento que ya existe.
    """

    def __init__(self, document_id: str, message: Optional[str] = None):
        """
        Inicializa la excepción de documento ya existente.

        Args:
            document_id (str): El ID del documento que ya existe.
            message (Optional[str]): Mensaje de error personalizado. Si es None,
                                     se genera un mensaje por defecto.
        """
        self.document_id = document_id
        if message is None:
            message = f"El documento con ID '{document_id}' ya existe."
        super().__init__(message)

    def __repr__(self) -> str:
        return f"DocumentAlreadyExists(document_id='{self.document_id}')"