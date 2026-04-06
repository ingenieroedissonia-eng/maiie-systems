"""
Modulo: Search Use Case
Capa: Core

Descripcion:
Contiene la logica de negocio para realizar busquedas semanticas de documentos.

Responsabilidades:
- Orquestar el proceso de busqueda semantica.
- Validar las consultas de busqueda.
- Interactuar con las interfaces de servicios y repositorios para obtener los resultados.

Version: 1.0.0
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

# Configuracion del logger para este modulo
logger = logging.getLogger(__name__)

# -------------------
# Entidades del Dominio
# -------------------
# En una aplicacion real, esta entidad estaria en su propio archivo (e.g., core/entities.py)
@dataclass
class Document:
    """
    Representa un documento en el sistema.
    """
    id: str
    title: str
    content: str
    score: Optional[float] = None

# -------------------
# Excepciones del Dominio
# -------------------
# En una aplicacion real, estas excepciones estarian en su propio archivo (e.g., core/exceptions.py)
class SearchError(Exception):
    """Clase base para errores relacionados con la busqueda."""
    pass

class EmptyQueryError(SearchError):
    """Lanzada cuando la consulta de busqueda esta vacia."""
    pass

class SearchServiceError(SearchError):
    """Lanzada cuando ocurre un error en el servicio de busqueda subyacente."""
    pass

# -------------------
# Interfaces (Puertos)
# -------------------
# En una aplicacion real, estas interfaces estarian en su propio archivo (e.g., core/interfaces.py)

class DocumentRepository(ABC):
    """
    Interfaz para un repositorio de documentos. Define los metodos para
    interactuar con la capa de persistencia de documentos.
    """
    @abstractmethod
    def get_by_ids(self, doc_ids: List[str]) -> List[Document]:
        """
        Recupera una lista de documentos a partir de sus IDs.

        Args:
            doc_ids: Una lista de identificadores de documentos.

        Returns:
            Una lista de objetos Document.
        """
        raise NotImplementedError

class SemanticSearchService(ABC):
    """
    Interfaz para un servicio de busqueda semantica. Abstrae la logica
    de vectorizacion y busqueda en una base de datos de vectores.
    """
    @abstractmethod
    def find_similar(self, query: str, top_k: int = 5) -> List[tuple[str, float]]:
        """
        Encuentra los documentos mas similares a una consulta dada.

        Args:
            query: El texto de la consulta.
            top_k: El numero maximo de resultados a devolver.

        Returns:
            Una lista de tuplas, donde cada tupla contiene (document_id, score).
        """
        raise NotImplementedError

# -------------------
# Caso de Uso
# -------------------

class SearchDocuments:
    """
    Caso de uso para buscar documentos semanticamente.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        search_service: SemanticSearchService
    ):
        """
        Inicializa el caso de uso con las dependencias necesarias.

        Args:
            document_repository: Una implementacion de la interfaz DocumentRepository.
            search_service: Una implementacion de la interfaz SemanticSearchService.
        """
        if not isinstance(document_repository, DocumentRepository):
            raise TypeError("document_repository must be an instance of DocumentRepository")
        if not isinstance(search_service, SemanticSearchService):
            raise TypeError("search_service must be an instance of SemanticSearchService")

        self.document_repository = document_repository
        self.search_service = search_service
        logger.info("SearchDocuments use case initialized.")

    def execute(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Ejecuta el caso de uso de busqueda.

        Args:
            query: La consulta de busqueda del usuario.
            top_k: El numero de resultados a devolver.

        Returns:
            Una lista de documentos que coinciden semanticamente con la consulta.

        Raises:
            EmptyQueryError: Si la consulta esta vacia o solo contiene espacios.
            SearchServiceError: Si ocurre un error durante la interaccion con los
                                servicios de busqueda o el repositorio.
        """
        if not query or not query.strip():
            logger.warning("Search attempt with an empty query.")
            raise EmptyQueryError("Search query cannot be empty.")

        logger.info(f"Executing search for query: '{query}' with top_k={top_k}")

        try:
            similar_docs_tuples = self.search_service.find_similar(query, top_k)

            if not similar_docs_tuples:
                logger.info(f"No similar documents found for query: '{query}'")
                return []

            doc_ids = [doc_id for doc_id, score in similar_docs_tuples]
            scores_map = {doc_id: score for doc_id, score in similar_docs_tuples}

            logger.debug(f"Found similar document IDs: {doc_ids}")

            documents = self.document_repository.get_by_ids(doc_ids)

            for doc in documents:
                doc.score = scores_map.get(doc.id)

            documents.sort(key=lambda d: d.score if d.score is not None else 0.0, reverse=True)

            logger.info(f"Successfully found {len(documents)} documents for query: '{query}'")
            return documents

        except (IOError, ConnectionError, ValueError) as e:
            logger.error(
                f"An infrastructure error occurred during search for query '{query}': {e}",
                exc_info=True
            )
            raise SearchServiceError(f"Failed to perform search due to a service error: {e}") from e
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred during search for query '{query}': {e}",
                exc_info=True
            )
            raise SearchServiceError(f"An unexpected error occurred: {e}") from e