"""
Modulo: core.test_entity
Capa: Core

Descripcion:
Define la entidad de dominio principal 'Test'.

Responsabilidades:
- Encapsular los datos y las reglas de negocio fundamentales relacionadas con un 'Test'.
- Garantizar la inmutabilidad y la validez de los datos de la entidad.

Version: 1.0.0
"""

import logging
import uuid
from dataclasses import dataclass, field

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Test:
    """
    Representa una entidad de prueba en el dominio.

    Esta clase es un objeto de valor inmutable. Una vez creada, sus atributos
    no pueden ser modificados. La validación básica se realiza en la
    post-inicialización.

    Attributes:
        name (str): El nombre del test, no puede ser vacío.
        value (str): El valor asociado al test.
        id (uuid.UUID): El identificador único para el test, generado
                        automáticamente si no se proporciona.
    """
    name: str
    value: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        """
        Realiza validaciones después de que la instancia ha sido inicializada.

        Raises:
            ValueError: Si el nombre del test está vacío o solo contiene espacios.
            TypeError: Si los atributos no son del tipo esperado.
        """
        logger.debug("Executing post-init validation for Test entity with id %s", self.id)

        if not isinstance(self.name, str):
            msg = f"Test name must be a string, but got {type(self.name).__name__}"
            logger.error(msg)
            raise TypeError(msg)

        if not isinstance(self.value, str):
            msg = f"Test value must be a string, but got {type(self.value).__name__}"
            logger.error(msg)
            raise TypeError(msg)

        if not self.name or not self.name.strip():
            msg = "Test name cannot be empty or contain only whitespace."
            logger.error(msg)
            raise ValueError(msg)

        logger.info("Successfully created and validated Test entity with id: %s", self.id)

python