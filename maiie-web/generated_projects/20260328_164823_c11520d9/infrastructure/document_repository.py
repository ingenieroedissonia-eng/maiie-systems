"""
Module: Document Repository
Layer: Infrastructure

Description:
Implementation of the document repository using an in-memory storage.

Responsabilities:
- Provide a concrete implementation of the DocumentRepository protocol.
- Manage the persistence of Document entities in memory.
- Handle document creation, retrieval, and deletion operations.

Version: 1.0.0
"""

import logging
from typing import Dict, List

from core.document import Document
from core.exceptions import DocumentNotFound
from core.use_cases import DocumentRepository

logger = logging.getLogger(__name__)


class InMemoryDocumentRepository(DocumentRepository):
    """
    An in-memory repository for storing and retrieving documents.

    This class implements the DocumentRepository protocol and uses a simple
    dictionary as a data store. It is suitable for testing and development
    environments where data persistence across sessions is not required.
    """

    def __init__(self) -> None:
        """Initializes the in-memory repository with an empty storage."""
        self._storage: Dict[str, Document] = {}
        logger.info("InMemoryDocumentRepository initialized.")

    def save(self, document: Document) -> Document:
        """
        Saves a document to the in-memory storage.

        If a document with the same ID already exists, it will be overwritten.

        Args:
            document: The Document object to save.

        Returns:
            The saved Document object.
        
        Raises:
            TypeError: If the object to save is not a Document instance.
        """
        if not isinstance(document, Document):
            logger.error(f"Attempted to save an object of type {type(document).__name__}, expected Document.")
            raise TypeError("Expected a Document object to save.")

        logger.info(f"Saving document with id: {document.id}")
        self._storage[document.id] = document
        logger.debug(f"Current storage contains {len(self._storage)} documents.")
        return document

    def find_by_id(self, document_id: str) -> Document:
        """
        Finds a document by its unique identifier.

        Args:
            document_id: The ID of the document to find.

        Returns:
            The found Document object.

        Raises:
            DocumentNotFound: If no document with the given ID is found.
        """
        logger.info(f"Attempting to find document with id: {document_id}")
        document = self._storage.get(document_id)

        if document is None:
            logger.warning(f"Document with id '{document_id}' not found in storage.")
            raise DocumentNotFound(f"Document with id '{document_id}' not found.")

        logger.info(f"Document with id '{document_id}' found.")
        return document

    def get_all(self) -> List[Document]:
        """
        Retrieves all documents from the in-memory storage.

        Returns:
            A list of all Document objects.
        """
        logger.info("Retrieving all documents from storage.")
        all_documents = list(self._storage.values())
        logger.info(f"Found {len(all_documents)} documents.")
        return all_documents

    def delete_by_id(self, document_id: str) -> None:
        """
        Deletes a document by its unique identifier.

        Args:
            document_id: The ID of the document to delete.

        Raises:
            DocumentNotFound: If no document with the given ID is found.
        """
        logger.info(f"Attempting to delete document with id: {document_id}")
        if document_id not in self._storage:
            logger.warning(f"Attempted to delete non-existent document with id: {document_id}")
            raise DocumentNotFound(f"Cannot delete. Document with id '{document_id}' not found.")

        del self._storage[document_id]
        logger.info(f"Document with id '{document_id}' deleted successfully.")
        logger.debug(f"Current storage contains {len(self._storage)} documents.")