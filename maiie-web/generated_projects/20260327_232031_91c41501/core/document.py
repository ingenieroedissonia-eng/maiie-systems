"""
Módulo: Document
Capa: Core

Descripción:
Define la entidad de dominio 'Document', que representa un fragmento de texto
con metadatos asociados y su correspondiente representación vectorial (embedding).

Responsabilidades:
- Estructurar los datos de un documento o fragmento de documento.
- Proporcionar validación básica de sus atributos.
- Servir como el objeto de datos principal para la lógica de negocio.

Versión: 1.0.0
"""

import logging
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Document:
    """
    Entidad que representa un fragmento de un documento.

    Esta clase es inmutable (`frozen=True`) para garantizar la consistencia de los
    datos una vez que un objeto ha sido creado.

    Attributes:
        id (str): Identificador único para el fragmento del documento.
                  Se genera automáticamente un UUID v4 si no se proporciona.
        filename (str): Nombre del archivo original del cual se extrajo el fragmento.
        content (str): El contenido textual del fragmento del documento.
        chunk_index (int): El índice secuencial del fragmento dentro del documento original.
        embedding (Optional[List[float]]): La representación vectorial (embedding) del
                                           contenido. Puede ser None si aún no se ha calculado.
    """
    filename: str
    content: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()), kw_only=True)

    def __post_init__(self):
        """
        Realiza validaciones después de la inicialización del objeto.
        """
        if not self.filename:
            msg = "El nombre de archivo ('filename') no puede estar vacío."
            logger.error(msg)
            raise ValueError(msg)

        if not self.content:
            msg = "El contenido ('content') no puede estar vacío."
            logger.error(msg)
            raise ValueError(msg)

        if self.chunk_index < 0:
            msg = "El índice del fragmento ('chunk_index') no puede ser negativo."
            logger.error(msg)
            raise ValueError(msg)

        logger.debug(f"Documento creado con éxito: id={self.id}, file={self.filename}")

    def __repr__(self) -> str:
        """
        Representación de cadena para el objeto Documento, útil para logging.
        """
        embedding_status = "Presente" if self.embedding is not None else "Ausente"
        return (
            f"Document(id={self.id}, filename='{self.filename}', "
            f"chunk_index={self.chunk_index}, embedding={embedding_status})"
        )

    def get_content_summary(self, length: int = 50) -> str:
        """
        Devuelve un resumen del contenido del documento.

        Args:
            length (int): La longitud máxima del resumen.

        Returns:
            str: Una cadena con el contenido truncado.
        """
        if len(self.content) > length:
            return self.content[:length] + "..."
        return self.content