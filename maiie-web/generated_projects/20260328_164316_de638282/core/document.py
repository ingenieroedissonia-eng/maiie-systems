"""
Modulo: Document
Capa: Core

Descripcion:
Define la entidad de dominio `Document`, que representa la estructura de datos
fundamental para un documento en el sistema.

Responsabilidades:
- Definir los atributos de un documento (id, title, content).
- Asegurar la inmutabilidad de la entidad una vez creada.
- Proveer validaciones basicas sobre los datos del documento.

Version: 1.0.0
"""

import logging
import uuid
from dataclasses import dataclass, field

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Document:
    """
    Entidad que representa un documento.

    Es un objeto de valor inmutable. Una vez que se crea una instancia de Document,
    sus atributos no pueden ser modificados.

    Attributes:
        title (str): El título del documento. No puede estar vacío.
        content (str): El contenido principal del documento.
        id (str): El identificador único del documento, generado automáticamente
                  como un UUIDv4 si no se proporciona.
    """
    title: str
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """
        Realiza validaciones despues de la inicializacion del objeto.

        Este metodo es llamado automaticamente por el decorador @dataclass
        despues de que la instancia ha sido creada.

        Raises:
            ValueError: Si el título está vacío o solo contiene espacios en blanco.
        """
        logger.debug("Executing post-init validation for Document with id: %s", self.id)
        if not self.title or not self.title.strip():
            logger.error("Validation failed: Document title cannot be empty.")
            raise ValueError("El título del documento no puede estar vacío.")
        logger.debug("Document entity created successfully: id=%s, title='%s'", self.id, self.title)

    def to_dict(self) -> dict:
        """
        Convierte la instancia del documento a un diccionario.

        Returns:
            dict: Una representacion de diccionario del documento.
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """
        Crea una instancia de Document a partir de un diccionario.

        Args:
            data (dict): Un diccionario con las claves 'id', 'title', y 'content'.

        Returns:
            Document: Una nueva instancia de la clase Document.

        Raises:
            KeyError: Si alguna de las claves requeridas no está en el diccionario.
            ValueError: Si los datos de entrada no son válidos según las reglas de la entidad.
        """
        try:
            return cls(
                id=data["id"],
                title=data["title"],
                content=data["content"]
            )
        except KeyError as e:
            logger.error("Missing key in data for Document creation: %s", e)
            raise KeyError(f"Falta la clave requerida en los datos del documento: {e}") from e