"""
Modulo: test_entity
Capa: Core

Descripcion:
Define la entidad de dominio `TestEntity`, que representa el objeto central
del negocio.

Responsabilidades:
- Definir la estructura de datos de una entidad de prueba.
- Contener la logica de validacion inherente a la entidad.
- Ser inmutable por diseño para garantizar la consistencia del estado.

Version: 1.0.0
"""

import logging
import uuid
from dataclasses import dataclass, field

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class TestEntity:
    """
    Representa una entidad de prueba en el dominio.

    Esta clase utiliza `dataclasses` con `frozen=True` para asegurar la inmutabilidad
    de las instancias una vez creadas. La validación de los datos se realiza
    en el método `__post_init__`.

    Attributes:
        id (uuid.UUID): El identificador único de la entidad.
        name (str): El nombre descriptivo de la entidad. No puede estar vacío.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = field(default="")

    def __post_init__(self):
        """
        Realiza validaciones de la entidad después de su inicialización.

        Este método es llamado automáticamente por el decorador `@dataclass`
        después de que se inicializa una instancia.

        Raises:
            ValueError: Si el nombre está vacío o solo contiene espacios en blanco.
        """
        logger.debug(f"Iniciando post-inicialización para TestEntity con id: {self.id}")

        if not isinstance(self.name, str) or not self.name.strip():
            log_msg = "El nombre de TestEntity no puede ser nulo, vacío o contener solo espacios."
            logger.error(log_msg)
            raise ValueError(log_msg)

        if not isinstance(self.id, uuid.UUID):
            log_msg = f"El ID de TestEntity debe ser un UUID, pero se recibió {type(self.id)}."
            logger.error(log_msg)
            raise TypeError(log_msg)

        logger.info(f"TestEntity creada o validada exitosamente: id={self.id}, name='{self.name}'")

    def to_dict(self) -> dict:
        """
        Convierte la entidad a un diccionario.

        Returns:
            dict: Una representación en diccionario de la entidad.
        """
        return {
            "id": str(self.id),
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TestEntity':
        """
        Crea una instancia de TestEntity desde un diccionario.

        Args:
            data (dict): El diccionario con los datos de la entidad.

        Returns:
            TestEntity: Una nueva instancia de la entidad.
        
        Raises:
            KeyError: Si faltan claves 'id' o 'name' en el diccionario.
            ValueError: Si el valor de 'id' no es un UUID válido.
        """
        try:
            entity_id = uuid.UUID(data['id']) if 'id' in data else uuid.uuid4()
            entity_name = data['name']
            return cls(id=entity_id, name=entity_name)
        except KeyError as e:
            logger.error(f"Falta la clave requerida '{e.args[0]}' en los datos para crear TestEntity.")
            raise KeyError(f"Datos de entrada incompletos para TestEntity: falta '{e.args[0]}'.") from e
        except ValueError as e:
            logger.error(f"Error al convertir el ID a UUID desde los datos: {data.get('id')}")
            raise ValueError("El ID proporcionado no es un UUID válido.") from e