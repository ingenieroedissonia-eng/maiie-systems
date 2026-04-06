"""
Modulo: Use Cases
Capa: Core

Descripcion:
Contiene los casos de uso de la aplicacion, que orquestan la logica de negocio
y coordinan las entidades y los repositorios.

Responsabilidades:
- Implementar la logica de negocio de alto nivel.
- Servir como punto de entrada para las acciones del sistema desde la capa de aplicacion.

Version: 1.0.0
"""

import logging
from typing import Optional

# Las dependencias se declaran como imports normales.
# Se asume que estos modulos existen y seran proporcionados por el sistema.
from core.document import Document
from core.exceptions import DocumentAlreadyExists
from infrastructure.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class AddDocumentUseCase:
    """
    Caso de uso para anadir un nuevo documento al sistema.

    Este caso de uso se encarga de validar la entrada, verificar que el
    documento no exista previamente y, si todo es correcto, persistirlo
    a traves del repositorio de documentos.
    """

    def __init__(self, document_repository: DocumentRepository):
        """
        Inicializa el caso de uso con una implementacion del repositorio de documentos.

        Args:
            document_repository (DocumentRepository): Una instancia de un repositorio
                                                      que cumple con la interfaz DocumentRepository.
        """
        if not isinstance(document_repository, DocumentRepository):
            logger.error("Invalid repository type provided to AddDocumentUseCase.")
            raise TypeError("document_repository must be an instance of DocumentRepository")
        self.document_repository = document_repository
        logger.info("AddDocumentUseCase initialized with repository.")

    def execute(self, document_id: str, content: str) -> Document:
        """
        Ejecuta el caso de uso para anadir un documento.

        Args:
            document_id (str): El identificador unico del documento.
            content (str): El contenido del documento.

        Returns:
            Document: La entidad del documento recien creado.

        Raises:
            ValueError: Si el document_id o el content estan vacios.
            DocumentAlreadyExists: Si ya existe un documento con el mismo document_id.
            RuntimeError: Si ocurre un error inesperado durante la interaccion con el repositorio.
        """
        logger.info(f"Executing AddDocumentUseCase for document_id: {document_id}")

        if not document_id or not document_id.strip():
            logger.warning("Validation failed: document_id cannot be empty.")
            raise ValueError("El ID del documento no puede estar vacío.")

        if not content:
            logger.warning("Validation failed: content cannot be empty.")
            raise ValueError("El contenido del documento no puede estar vacío.")

        try:
            existing_document = self.document_repository.get_by_id(document_id)
            if existing_document:
                logger.warning(f"Document with id '{document_id}' already exists.")
                raise DocumentAlreadyExists(f"El documento con ID '{document_id}' ya existe.")

            logger.debug(f"Document with id '{document_id}' does not exist. Proceeding to create.")

            new_document = Document(id=document_id, content=content)
            logger.debug(f"Created Document entity for id: {document_id}")

            self.document_repository.add(new_document)
            logger.info(f"Successfully added document with id: '{document_id}' to the repository.")

            return new_document

        except DocumentAlreadyExists:
            raise
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while adding document '{document_id}': {e}",
                exc_info=True
            )
            raise RuntimeError(f"Error inesperado en el repositorio al añadir el documento: {e}") from e

python