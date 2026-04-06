"""
Modulo: core.use_cases
Capa: Core

Descripcion:
Contiene la logica de negocio y los casos de uso especificos de la aplicacion.
Orquesta el flujo de datos entre las entidades y los repositorios para cumplir
con los requisitos de negocio.

Responsabilidades:
- Implementar casos de uso de la aplicacion.
- Validar datos de entrada para los casos de uso.
- Coordinar con la capa de infraestructura a traves de interfaces.

Version: 1.0.0
"""

import logging
from dataclasses import dataclass
from typing import Optional

# Estas son dependencias de otros modulos dentro de la capa Core.
# Se asume que existen y seran implementadas en otras submisiones.
from .document import Document
from .exceptions import DocumentRepositoryError, InvalidDocumentDataError
from .interfaces import DocumentRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddDocumentRequest:
    """
    Data Transfer Object para agregar un nuevo documento.
    Representa los datos de entrada para el caso de uso AddDocument.
    Es inmutable para garantizar la integridad de los datos de la solicitud.
    """
    title: str
    content: str


class AddDocument:
    """
    Caso de uso para agregar un nuevo documento al sistema.
    """

    def __init__(self, document_repository: DocumentRepository):
        """
        Inicializa el caso de uso AddDocument con sus dependencias.

        Args:
            document_repository: Una instancia de una clase que implementa
                                 la interfaz DocumentRepository.
        """
        if not isinstance(document_repository, DocumentRepository):
            msg = "document_repository must be an instance of DocumentRepository"
            logger.error(msg)
            raise TypeError(msg)
        self.document_repository = document_repository
        logger.info("AddDocument use case initialized successfully.")

    def _validate_request(self, request: AddDocumentRequest) -> None:
        """
        Valida los datos de entrada para la solicitud de agregar documento.

        Args:
            request: El DTO AddDocumentRequest.

        Raises:
            InvalidDocumentDataError: Si el titulo o el contenido estan vacios o son invalidos.
        """
        logger.debug(f"Validating request data for title: '{request.title}'")
        if not request.title or not request.title.strip():
            raise InvalidDocumentDataError("Document title cannot be empty.")
        if not request.content or not request.content.strip():
            raise InvalidDocumentDataError("Document content cannot be empty.")
        logger.debug("Request data is valid.")

    def execute(self, request: AddDocumentRequest) -> Document:
        """
        Ejecuta el caso de uso para agregar un nuevo documento.

        Args:
            request: Un objeto AddDocumentRequest que contiene los datos del documento.

        Returns:
            La entidad Document recien creada.

        Raises:
            InvalidDocumentDataError: Si los datos proporcionados son invalidos.
            DocumentRepositoryError: Si ocurre un error durante la persistencia.
        """
        logger.info(f"Executing AddDocument use case for title: '{request.title}'")
        self._validate_request(request)

        try:
            new_document = Document(
                id=None,
                title=request.title.strip(),
                content=request.content.strip()
            )

            logger.debug("Attempting to save new document via repository.")
            created_document = self.document_repository.save(new_document)

            if not created_document or not created_document.id:
                raise DocumentRepositoryError(
                    "Repository failed to return a created document with an ID."
                )

            logger.info(f"Successfully created document with ID: {created_document.id}")
            return created_document

        except InvalidDocumentDataError as e:
            logger.warning(f"Invalid document data provided: {e}")
            raise

        except Exception as e:
            logger.error(f"An unexpected repository error occurred: {e}", exc_info=True)
            raise DocumentRepositoryError(
                f"Failed to save document due to a repository error: {e}"
            ) from e