"""
Modulo: InMemoryDocumentRepository
Capa: Infrastructure

Descripcion:
Implementacion concreta del repositorio de documentos que utiliza un
diccionario en memoria como mecanismo de persistencia.

Responsabilidades:
- Almacenar y recuperar entidades de tipo `Document`.
- Implementar la interfaz `DocumentRepository`.
- Gestionar el ciclo de vida de los documentos en memoria.

Version: 1.0.0
"""
import logging
from typing import Dict, List

from core.entities.document import Document
from core.exceptions import DocumentAlreadyExists, DocumentNotFound
from core.ports.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class InMemoryDocumentRepository(DocumentRepository):
    """
    Implementación en memoria de la interfaz DocumentRepository.

    Esta clase utiliza un diccionario para almacenar los documentos.
    Es útil para pruebas o entornos de desarrollo donde no se requiere
    persistencia real.
    """

    def __init__(self) -> None:
        """
        Inicializa el repositorio en memoria con un almacenamiento vacío.
        """
        self._storage: Dict[str, Document] = {}
        logger.info("InMemoryDocumentRepository inicializado.")

    def save(self, document: Document) -> None:
        """
        Guarda un nuevo documento en el almacenamiento en memoria.

        Args:
            document (Document): La entidad de documento a guardar.

        Raises:
            DocumentAlreadyExists: Si ya existe un documento con el mismo ID.
        """
        if document.id in self._storage:
            msg = f"El documento con ID '{document.id}' ya existe."
            logger.error(msg)
            raise DocumentAlreadyExists(msg)

        self._storage[document.id] = document
        logger.info(f"Documento con ID '{document.id}' guardado correctamente.")

    def find_by_id(self, document_id: str) -> Document:
        """
        Busca un documento por su ID.

        Args:
            document_id (str): El ID del documento a buscar.

        Returns:
            Document: La entidad de documento encontrada.

        Raises:
            DocumentNotFound: Si no se encuentra ningún documento con el ID proporcionado.
        """
        document = self._storage.get(document_id)
        if document is None:
            msg = f"No se encontró el documento con ID '{document_id}'."
            logger.warning(msg)
            raise DocumentNotFound(msg)

        logger.info(f"Documento con ID '{document_id}' encontrado.")
        return document

    def find_all(self) -> List[Document]:
        """
        Recupera todos los documentos almacenados.

        Returns:
            List[Document]: Una lista de todas las entidades de documento.
        """
        all_documents = list(self._storage.values())
        logger.info(f"Se recuperaron {len(all_documents)} documentos.")
        return all_documents

    def update(self, document: Document) -> None:
        """
        Actualiza un documento existente en el almacenamiento.

        Args:
            document (Document): La entidad de documento con los datos actualizados.

        Raises:
            DocumentNotFound: Si el documento a actualizar no existe.
        """
        if document.id not in self._storage:
            msg = f"No se puede actualizar. El documento con ID '{document.id}' no existe."
            logger.error(msg)
            raise DocumentNotFound(msg)

        self._storage[document.id] = document
        logger.info(f"Documento con ID '{document.id}' actualizado correctamente.")

    def delete(self, document_id: str) -> None:
        """
        Elimina un documento del almacenamiento por su ID.

        Args:
            document_id (str): El ID del documento a eliminar.

        Raises:
            DocumentNotFound: Si el documento a eliminar no existe.
        """
        if document_id not in self._storage:
            msg = f"No se puede eliminar. El documento con ID '{document_id}' no existe."
            logger.error(msg)
            raise DocumentNotFound(msg)

        del self._storage[document_id]
        logger.info(f"Documento con ID '{document_id}' eliminado correctamente.")