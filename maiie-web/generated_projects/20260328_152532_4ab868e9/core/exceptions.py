"""
Modulo: Exceptions
Capa: Core

Descripcion:
Define las excepciones personalizadas para la capa de dominio del gestor de documentos.
Estas excepciones proporcionan un manejo de errores semantico y especifico del negocio,
permitiendo un control de flujo mas claro en los casos de uso y en la capa de API.

Responsabilidades:
- Definir una excepcion base para todas las excepciones del dominio.
- Definir excepciones especificas como DocumentNotFound para escenarios de error concretos.

Version: 1.0.0
"""

import logging
from typing import Any

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

class DocumentManagerException(Exception):
    """
    Clase base para todas las excepciones personalizadas del gestor de documentos.

    Permite agrupar todos los errores de dominio bajo un tipo común, facilitando
    la captura de errores a nivel de aplicación.
    """
    def __init__(self, message: str, **kwargs: Any):
        """
        Inicializa la excepcion base.

        Args:
            message (str): El mensaje de error principal.
            **kwargs: Atributos adicionales para logging o depuracion.
        """
        self.message = message
        self.details = kwargs
        super().__init__(self.message)
        logger.debug(f"Raised {self.__class__.__name__}: {message}, Details: {kwargs}")

    def __str__(self) -> str:
        """Representacion en cadena de la excepcion."""
        return f"{self.__class__.__name__}: {self.message}"


class DocumentNotFound(DocumentManagerException):
    """
    Excepcion lanzada cuando un documento especifico no se encuentra en el sistema.

    Esta excepcion debe ser capturada para manejar casos donde una busqueda por ID
    u otro identificador unico no devuelve resultados, permitiendo a la capa
    superior (e.g., la API) devolver una respuesta adecuada como un 404 Not Found.

    Atributos:
        document_id (str): El identificador del documento que no fue encontrado.
    """
    def __init__(self, document_id: str):
        """
        Inicializa la excepcion DocumentNotFound.

        Args:
            document_id (str): El ID del documento que no se pudo encontrar.
        """
        self.document_id = document_id
        message = f"El documento con el ID '{document_id}' no fue encontrado."
        super().__init__(message, document_id=document_id)
        logger.warning(message)