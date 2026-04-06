"""
Modulo: Document
Capa: Core

Descripcion:
Define la entidad de dominio 'Document', que representa la unidad fundamental
de información en el sistema.

Responsabilidades:
- Definir la estructura de datos de un documento.
- Asegurar la integridad de los datos a través de validaciones inmutables.
- Proporcionar un punto de creación controlado para la entidad.

Version: 1.0.0
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import UUID, uuid4

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Document:
    """
    Entidad inmutable que representa un documento en el sistema.

    Utiliza 'frozen=True' para garantizar que una vez que se crea una instancia
    de Document, su estado no puede ser modificado. Esto es una práctica
    común en la arquitectura limpia para las entidades de dominio.

    Atributos:
        id (UUID): Identificador único universal para el documento.
        title (str): Título del documento.
        content (str): Contenido principal del documento.
    """
    id: UUID = field(default_factory=uuid4, init=False)
    title: str
    content: str

    def __post_init__(self):
        """
        Realiza validaciones después de que el objeto ha sido inicializado.
        """
        logger.debug(f"Validando la entidad Document con título: '{self.title}'")
        self._validate_title()
        self._validate_content()
        logger.debug(f"Entidad Document creada exitosamente con ID: {self.id}")

    def _validate_title(self):
        """
        Valida que el título del documento no esté vacío.

        Raises:
            ValueError: Si el título está vacío o solo contiene espacios en blanco.
        """
        if not self.title or not self.title.strip():
            logger.error("Error de validación: El título no puede estar vacío.")
            raise ValueError("El título del documento no puede estar vacío.")
        if len(self.title) > 255:
            logger.error("Error de validación: El título excede la longitud máxima.")
            raise ValueError("El título no puede exceder los 255 caracteres.")

    def _validate_content(self):
        """
        Valida que el contenido del documento no esté vacío.

        Raises:
            ValueError: Si el contenido está vacío o solo contiene espacios en blanco.
        """
        if not self.content or not self.content.strip():
            logger.error("Error de validación: El contenido no puede estar vacío.")
            raise ValueError("El contenido del documento no puede estar vacío.")

    @classmethod
    def create(cls, title: str, content: str) -> 'Document':
        """
        Método de fábrica para crear una nueva instancia de Document.

        Este método encapsula la lógica de creación y validación, proporcionando
        una única forma controlada de instanciar la entidad.

        Args:
            title (str): El título para el nuevo documento.
            content (str): El contenido para el nuevo documento.

        Returns:
            Document: Una nueva instancia de la entidad Document.
        
        Raises:
            ValueError: Si los datos de entrada no superan las validaciones.
        """
        logger.info(f"Intentando crear un nuevo documento con título: '{title}'")
        try:
            document = cls(title=title, content=content)
            return document
        except ValueError as e:
            logger.warning(f"Fallo al crear el documento: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia de Document en un diccionario.

        Útil para la serialización de datos, por ejemplo, al preparar una respuesta
        para una API.

        Returns:
            Dict[str, Any]: Una representación de diccionario de la entidad.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
        }