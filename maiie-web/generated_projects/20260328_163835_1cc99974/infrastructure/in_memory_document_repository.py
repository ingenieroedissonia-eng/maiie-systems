"""
Modulo: InMemoryDocumentRepository
Capa: Infrastructure

Descripcion:
Implementacion en memoria del repositorio de documentos.
Esta clase simula la persistencia de datos utilizando un diccionario de Python,
lo que la hace ideal para entornos de desarrollo, pruebas o prototipado rapido.

Responsabilidades:
- Implementar la interfaz `DocumentRepository`.
- Almacenar, recuperar, actualizar y eliminar entidades `Document` en un diccionario.
- Lanzar excepciones especificas del dominio cuando las operaciones fallan (e.g., documento no encontrado).

Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional

# Se asume que estas dependencias existen en la capa Core y seran implementadas en otras submisiones.
# No se implementan aqui.
from core.document import Document
from core.exceptions import DocumentNotFoundException, RepositoryException
from core.ports.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class InMemoryDocumentRepository(DocumentRepository):
    """
    Implementacion de un repositorio de documentos que utiliza un diccionario en memoria
    como mecanismo de almacenamiento.
    """

    def __init__(self) -> None:
        """
        Inicializa el repositorio en memoria con un almacen de datos vacio.
        """
        self._documents: Dict[str, Document] = {}
        logger.info("InMemoryDocumentRepository initialized.")

    def add(self, document: Document) -> None:
        """
        Agrega un nuevo documento al almacen en memoria.

        Si ya existe un documento con el mismo ID, sera reemplazado.

        Args:
            document: La instancia del documento a agregar.

        Raises:
            RepositoryException: Si ocurre un error inesperado durante la operacion.
        """
        try:
            if not isinstance(document, Document) or not hasattr(document, 'id'):
                raise TypeError("Provided object is not a valid Document instance.")

            logger.debug(f"Adding document with id: {document.id}")
            self._documents[document.id] = document
            logger.info(f"Document with id '{document.id}' added successfully.")
        except TypeError as e:
            logger.error(f"Error adding document: Invalid object type. Details: {e}")
            raise RepositoryException(f"Failed to add invalid document object: {e}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while adding document id {getattr(document, 'id', 'N/A')}: {e}")
            raise RepositoryException(f"Unexpected error adding document: {e}") from e

    def get_by_id(self, document_id: str) -> Document:
        """
        Recupera un documento por su ID.

        Args:
            document_id: El ID del documento a recuperar.

        Returns:
            La instancia del documento encontrada.

        Raises:
            DocumentNotFoundException: Si no se encuentra ningun documento con el ID especificado.
        """
        try:
            logger.debug(f"Attempting to retrieve document with id: {document_id}")
            document = self._documents[document_id]
            logger.info(f"Document with id '{document_id}' retrieved successfully.")
            return document
        except KeyError:
            logger.warning(f"Document with id '{document_id}' not found.")
            raise DocumentNotFoundException(f"Document with id '{document_id}' not found.")

    def list_all(self) -> List[Document]:
        """
        Devuelve una lista de todos los documentos almacenados.

        Returns:
            Una lista de todas las instancias de Document.

        Raises:
            RepositoryException: Si ocurre un error al construir la lista de documentos.
        """
        try:
            logger.debug("Retrieving all documents.")
            all_docs = list(self._documents.values())
            logger.info(f"Retrieved {len(all_docs)} documents.")
            return all_docs
        except Exception as e:
            logger.error(f"An unexpected error occurred while listing all documents: {e}")
            raise RepositoryException(f"Unexpected error listing documents: {e}") from e

    def update(self, document: Document) -> None:
        """
        Actualiza un documento existente en el almacen.

        Args:
            document: La instancia del documento con los datos actualizados.

        Raises:
            DocumentNotFoundException: Si el documento a actualizar no existe en el almacen.
            RepositoryException: Si ocurre un error inesperado durante la actualizacion.
        """
        try:
            if document.id not in self._documents:
                raise DocumentNotFoundException(f"Cannot update non-existent document with id '{document.id}'.")

            logger.debug(f"Updating document with id: {document.id}")
            self._documents[document.id] = document
            logger.info(f"Document with id '{document.id}' updated successfully.")
        except DocumentNotFoundException:
            logger.warning(f"Attempted to update a document that does not exist: id '{document.id}'")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while updating document id {document.id}: {e}")
            raise RepositoryException(f"Unexpected error updating document: {e}") from e

    def delete(self, document_id: str) -> None:
        """
        Elimina un documento del almacen por su ID.

        Args:
            document_id: El ID del documento a eliminar.

        Raises:
            DocumentNotFoundException: Si no se encuentra ningun documento con el ID especificado.
        """
        try:
            logger.debug(f"Attempting to delete document with id: {document_id}")
            del self._documents[document_id]
            logger.info(f"Document with id '{document_id}' deleted successfully.")
        except KeyError:
            logger.warning(f"Attempted to delete a document that does not exist: id '{document_id}'")
            raise DocumentNotFoundException(f"Document with id '{document_id}' not found for deletion.")