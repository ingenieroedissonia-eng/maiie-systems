"""
Modulo: create_test
Capa: Core (Casos de Uso)

Descripcion:
Este módulo contiene el caso de uso para crear una nueva entidad de prueba.
Se encarga de la lógica de negocio relacionada con la creación, incluyendo
la validación de datos de entrada y la interacción con la capa de persistencia
a través de una interfaz de repositorio.

Responsabilidades:
- Orquestar la creación de una nueva `TestEntity`.
- Validar los datos necesarios para la creación.
- Interactuar con la interfaz del repositorio para persistir la nueva entidad.
- Devolver la entidad creada.

Version: 1.0.0
"""

import logging
import uuid
from typing import TYPE_CHECKING

from core.test_entity import TestEntity

if TYPE_CHECKING:
    from core.interfaces import TestRepository

logger = logging.getLogger(__name__)


class CreateTest:
    """
    Caso de uso para crear una nueva entidad de prueba.
    """

    def __init__(self, test_repository: 'TestRepository'):
        """
        Inicializa el caso de uso con una implementación del repositorio de pruebas.

        Args:
            test_repository (TestRepository): Una instancia que implementa la interfaz
                                              TestRepository para la persistencia de datos.
        """
        if not hasattr(test_repository, 'create'):
            raise TypeError("test_repository must implement the 'create' method.")
        self.test_repository = test_repository

    def execute(self, name: str) -> TestEntity:
        """
        Ejecuta la lógica para crear una nueva entidad de prueba.

        Args:
            name (str): El nombre para la nueva entidad de prueba.

        Returns:
            TestEntity: La entidad de prueba recién creada y persistida.

        Raises:
            ValueError: Si el nombre proporcionado es inválido (vacío o nulo).
            Exception: Propaga excepciones que puedan ocurrir durante la operación
                       de persistencia en el repositorio.
        """
        logger.info(f"Executing CreateTest use case with name: '{name}'")

        if not name or not isinstance(name, str) or not name.strip():
            logger.error("Validation failed: Test name cannot be empty.")
            raise ValueError("Test name cannot be empty.")

        try:
            # La entidad es responsable de su propia consistencia inicial
            # y de la generación de su ID.
            new_test = TestEntity(id=uuid.uuid4(), name=name.strip())
            logger.debug(f"Created new TestEntity instance with ID: {new_test.id}")

            # Delega la persistencia al repositorio
            created_test = self.test_repository.create(new_test)
            logger.info(f"Successfully created and persisted test with ID: {created_test.id}")

            return created_test
        except Exception as e:
            # Captura cualquier error de la capa de infraestructura (repositorio)
            # y lo registra antes de propagarlo.
            logger.error(
                f"An unexpected error occurred while creating the test: {e}",
                exc_info=True
            )
            # Re-lanza la excepción para que sea manejada por una capa superior
            # (e.g., la capa de presentación/API).
            raise