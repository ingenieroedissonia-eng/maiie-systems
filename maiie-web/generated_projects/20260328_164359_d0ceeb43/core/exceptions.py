"""
Modulo: Exceptions
Capa: Core

Descripcion:
Define las excepciones personalizadas del dominio para la aplicacion.

Responsabilidades:
- Proporcionar una jerarquia de excepciones clara.
- Definir excepciones especificas del negocio como DocumentNotFound.

Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ApplicationException(Exception):
    """
    Clase base para todas las excepciones personalizadas de la aplicacion.

    Permite un manejo de errores mas estructurado y la adicion de contexto
    adicional a las excepciones, facilitando el debugging y el logging.
    """
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Inicializa la excepcion de la aplicacion.

        Args:
            message (str): El mensaje de error principal y legible para humanos.
            context (Optional[Dict[str, Any]]): Un diccionario con contexto
                                                 adicional sobre el error,
                                                 como identificadores o valores
                                                 relevantes.
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        logger.debug(
            "ApplicationException raised: %s, Context: %s",
            self.message,
            self.context
        )

    def __str__(self) -> str:
        """
        Devuelve la representacion en cadena de la excepcion.

        Returns:
            str: El mensaje de error, incluyendo el contexto si esta presente.
        """
        if self.context:
            return f"{self.message} (Context: {self.context})"
        return self.message


class DocumentNotFound(ApplicationException):
    """
    Excepcion lanzada cuando no se encuentra un documento especifico.

    Esta excepcion se debe capturar en las capas superiores (como la API)
    para devolver una respuesta adecuada al cliente, por ejemplo, un
    codigo de estado HTTP 404 Not Found.
    """
    def __init__(
        self,
        document_id: str,
        message: Optional[str] = None
    ) -> None:
        """
        Inicializa la excepcion DocumentNotFound.

        Args:
            document_id (str): El ID del documento que no se pudo encontrar.
            message (Optional[str]): Mensaje de error personalizado. Si no se
                                     proporciona, se genera uno por defecto.
        """
        final_message = message or f"Document with ID '{document_id}' not found."
        context = {"document_id": document_id}
        super().__init__(message=final_message, context=context)
        self.document_id = document_id
        logger.warning(
            "DocumentNotFound: No document found for ID %s", self.document_id
        )