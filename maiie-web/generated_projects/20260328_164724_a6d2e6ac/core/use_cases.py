"""
Modulo: Casos de Uso
Capa: Core

Descripcion:
Contiene la logica de negocio y los casos de uso de la aplicacion
relacionados con la gestion de documentos.

Responsabilidades:
- Definir la interfaz del repositorio de documentos (puerto).
- Implementar el caso de uso para crear un documento.
- Implementar el caso de uso para obtener un documento.

Version: 1.0.0
"""

import logging
import uuid
from typing import Protocol, Optional

from .document import Document
from .exceptions import DocumentNotFound, ApplicationException

logger = logging.getLogger(__name__)


class DocumentRepository(Protocol):
    """
    Protocol