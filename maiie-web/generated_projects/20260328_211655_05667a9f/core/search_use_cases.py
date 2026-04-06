"""
Modulo: Search Use Cases
Capa: Core

Descripcion:
Contiene los casos de uso relacionados con la búsqueda de documentos y las
interfaces de repositorio necesarias para su funcionamiento.

Responsabilidades:
- Definir la interfaz del repositorio de documentos.
- Implementar el caso de uso para buscar documentos.
- Orquestar la lógica de negocio para la búsqueda, incluyendo validaciones.

Version: 1.0.0
"""

import logging
from abc import ABCMeta, abstractmethod
from typing import List

from core.document import Document
from core.exceptions import DocumentNotFoundError, InvalidQueryError

logger = logging.getLogger(__name__)


class DocumentRepository(metaclass=ABCMeta):
    """
    Interfaz abstracta que define las operaciones de persistencia para las
    entidades Document.

    Esta interfaz desacopla el núcleo de la aplicación de los detalles de
    implementación de la base de datos.
    """

    @abstractmethod
    def find_by_query(self, query: str) -> List[Document]:
        """
        Busca y devuelve una lista de documentos que coinciden con un término de búsqueda.

        Args:
            query (str): El término a buscar en el título o contenido de los documentos.

        Returns:
            List[Document]: Una lista de objetos Document que coinciden con la consulta.
                            Puede ser una lista vacía si no se encuentran coincidencias.

        Raises:
            NotImplementedError: Si el método no está implementado por una subclase.
        """
        raise NotImplementedError


class SearchDocuments:
    """
    Caso de uso para buscar documentos que contengan un término específico.

    Este caso de uso encapsula la lógica de negocio para realizar una búsqueda,
    validar la consulta y manejar los resultados.
    """

    def __init__(self, document_repository: DocumentRepository):
        """
        Inicializa el caso de uso SearchDocuments.

        Args:
            document_repository (DocumentRepository): Una instancia de una implementación
                                                    de DocumentRepository para acceder a los datos.
        """
        if not isinstance(document_repository, DocumentRepository):
            raise TypeError("document_repository must be an instance of DocumentRepository")
        self.document_repository = document_repository
        logger.info("SearchDocuments use case initialized.")

    def execute(self, query: str) -> List[Document]:
        """
        Ejecuta la lógica de búsqueda de documentos.

        Args:
            query (str): El término de búsqueda para encontrar en los documentos.

        Returns:
            List[Document]: Una lista de documentos que coinciden con la consulta.

        Raises:
            InvalidQueryError: Si el término de búsqueda es nulo, vacío o solo espacios en blanco.
            DocumentNotFoundError: Si no se encuentra ningún documento que coincida con la consulta.
        """
        logger.info(f"Executing search for documents with query: '{query}'")

        if not query or not query.strip():
            logger.warning("Search failed: query is empty or contains only whitespace.")
            raise InvalidQueryError("Search query cannot be empty.")

        try:
            found_documents = self.document_repository.find_by_query(query)
        except Exception as e:
            logger.error(f"An unexpected error occurred in the repository during search: {e}", exc_info=True)
            # Re-lanzar como una excepción de dominio podría ser una opción,
            # pero por ahora se propaga para ser manejada en una capa superior.
            raise

        if not found_documents:
            logger.warning(f"No documents found for query: '{query}'")
            raise DocumentNotFoundError(f"No documents found matching the query: '{query}'")

        logger.info(f"Successfully found {len(found_documents)} document(s) for query: '{query}'")
        return found_documents