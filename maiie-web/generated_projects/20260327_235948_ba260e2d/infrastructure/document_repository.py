"""
Modulo: Document Repository
Capa: Infrastructure

Descripcion:
Define la interfaz abstracta para la persistencia de documentos.
Este modulo establece el contrato que cualquier implementacion concreta
de un repositorio de documentos debe seguir.

Responsabilidades:
- Definir los metodos estandar para operaciones CRUD en documentos.
- Servir como puerto en la arquitectura hexagonal para la capa de dominio.

Version: 1.0.0
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

# Para evitar dependencias circulares y mantener la capa de infraestructura
# desacoplada de la implementacion concreta de las entidades del core,
# se utiliza TYPE_CHECKING para importar la entidad 'Document' solo
# durante la verificacion de tipos.
if TYPE_CHECKING:
    # Se asume que la entidad Document se definira en core/entities/document.py o similar.
    # Esta es una referencia a futuro para mantener el acoplamiento bajo.
    from core.document import Document

logger = logging.getLogger(__name__)
# Es una buena practica para las bibliotecas anadir un NullHandler para evitar
# advertencias de 'No handler found' si la aplicacion consumidora no
# configura el logging.
logger.addHandler(logging.NullHandler())

class DocumentRepository(ABC):
    """
    Clase base abstracta (ABC) para el repositorio de documentos.

    Esta clase define la interfaz para interactuar con el sistema de
    almacenamiento de documentos. Cualquier clase que herede de
    DocumentRepository debe implementar todos los metodos abstractos
    definidos aqui. Esto garantiza un contrato consistente para la
    persistencia de datos a traves de la aplicacion.
    """

    @abstractmethod
    def save(self, document: 'Document') -> 'Document':
        """
        Guarda o actualiza un documento en el sistema de persistencia.

        Si el documento tiene un ID, se intenta actualizar. Si no lo tiene,
        se crea un nuevo registro y se le asigna un ID.

        Args:
            document ('Document'): La entidad de documento a guardar.

        Returns:
            'Document': La entidad de documento guardada, posiblemente con
                        informacion actualizada (ej. ID asignado por la BD).
        
        Raises:
            RepositoryError: Si ocurre un error generico durante la operacion.
        """
        ...

    @abstractmethod
    def get_by_id(self, document_id: str) -> Optional['Document']:
        """
        Recupera un documento por su identificador unico.

        Args:
            document_id (str): El ID del documento a recuperar.

        Returns:
            Optional['Document']: La entidad del documento si se encuentra,
                                  de lo contrario None.
        
        Raises:
            RepositoryError: Si ocurre un error generico durante la operacion.
        """
        ...

    @abstractmethod
    def list_all(self) -> List['Document']:
        """
        Recupera una lista de todos los documentos disponibles.

        Este metodo puede incluir paginacion en implementaciones concretas,
        pero la interfaz base devuelve una lista completa.

        Returns:
            List['Document']: Una lista de entidades de documento. Puede ser
                            una lista vacia si no hay documentos.
        
        Raises:
            RepositoryError: Si ocurre un error generico durante la operacion.
        """
        ...

    @abstractmethod
    def delete(self, document_id: str) -> bool:
        """
        Elimina un documento por su identificador unico.

        Args:
            document_id (str): El ID del documento a eliminar.

        Returns:
            bool: True si el documento fue eliminado exitosamente,
                  False si el documento no se encontro para eliminar.
        
        Raises:
            RepositoryError: Si ocurre un error generico durante la operacion.
        """
        ...