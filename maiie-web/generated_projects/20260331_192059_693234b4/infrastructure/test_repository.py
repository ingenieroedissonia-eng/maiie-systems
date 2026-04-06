"""
Modulo: Test Repository
Capa: Infrastructure

Descripcion:
Implementacion de un repositorio en memoria para la gestion de entidades TestEntity.

Responsabilidades:
- Almacenar y recuperar entidades TestEntity de un diccionario en memoria.
- Implementar las operaciones CRUD basicas (Crear, Leer, Actualizar, Eliminar).
- Lanzar excepciones especificas del dominio cuando las operaciones fallan (ej. TestNotFound).

Version: 1.0.0
"""
import logging
import uuid
from typing import Dict, List, Optional, Union

from core.test_entity import TestEntity
from core.test_exceptions import TestNotFound

logger = logging.getLogger(__name__)


class InMemoryTestRepository:
    """
    Repositorio en memoria para gestionar entidades TestEntity.

    Este repositorio utiliza un diccionario de Python para simular una base de datos,
    haciendolo ideal para pruebas, desarrollo local o escenarios donde la persistencia
    de datos entre reinicios no es necesaria.
    """

    def __init__(self) -> None:
        """Inicializa el repositorio en memoria."""
        self._storage: Dict[uuid.UUID, TestEntity] = {}
        logger.info("InMemoryTestRepository inicializado.")

    def create(self, test: TestEntity) -> TestEntity:
        """
        Agrega una nueva entidad TestEntity al almacenamiento.

        Args:
            test: La instancia de TestEntity a crear.

        Returns:
            La entidad TestEntity creada.

        Raises:
            ValueError: Si ya existe una entidad con el mismo ID.
        """
        logger.debug("Intentando crear entidad con ID: %s", test.id)
        if test.id in self._storage:
            error_msg = f"La entidad Test con ID '{test.id}' ya existe."
            logger.error(error_msg)
            raise ValueError(error_msg)

        self._storage[test.id] = test
        logger.info("Entidad Test con ID '%s' creada exitosamente.", test.id)
        return test

    def get_by_id(self, entity_id: Union[str, uuid.UUID]) -> TestEntity:
        """
        Recupera una entidad TestEntity por su ID.

        Args:
            entity_id: El ID (str o UUID) de la entidad a recuperar.

        Returns:
            La instancia de TestEntity encontrada.

        Raises:
            TestNotFound: Si no se encuentra ninguna entidad con el ID proporcionado.
            ValueError: Si el ID proporcionado no es un UUID valido.
        """
        try:
            test_uuid = uuid.UUID(str(entity_id))
        except ValueError as e:
            logger.error("ID proporcionado no es un UUID valido: %s", entity_id)
            raise ValueError(f"El ID '{entity_id}' no es un UUID valido.") from e

        logger.debug("Buscando entidad Test con ID: %s", test_uuid)
        test = self._storage.get(test_uuid)

        if test is None:
            logger.warning("Entidad Test con ID '%s' no encontrada.", test_uuid)
            raise TestNotFound(entity_id=test_uuid)

        logger.debug("Entidad Test con ID '%s' encontrada.", test_uuid)
        return test

    def update(self, test: TestEntity) -> TestEntity:
        """
        Actualiza una entidad TestEntity existente.

        Args:
            test: La instancia de TestEntity con los datos actualizados.

        Returns:
            La entidad TestEntity actualizada.

        Raises:
            TestNotFound: Si la entidad a actualizar no existe.
        """
        logger.debug("Intentando actualizar entidad con ID: %s", test.id)
        if test.id not in self._storage:
            logger.warning("Intento de actualizar entidad no existente con ID: %s", test.id)
            raise TestNotFound(entity_id=test.id)

        self._storage[test.id] = test
        logger.info("Entidad Test con ID '%s' actualizada exitosamente.", test.id)
        return test

    def delete(self, entity_id: Union[str, uuid.UUID]) -> None:
        """
        Elimina una entidad TestEntity por su ID.

        Args:
            entity_id: El ID (str o UUID) de la entidad a eliminar.

        Raises:
            TestNotFound: Si no se encuentra ninguna entidad con el ID proporcionado.
            ValueError: Si el ID proporcionado no es un UUID valido.
        """
        try:
            test_uuid = uuid.UUID(str(entity_id))
        except ValueError as e:
            logger.error("ID proporcionado para eliminar no es un UUID valido: %s", entity_id)
            raise ValueError(f"El ID '{entity_id}' no es un UUID valido.") from e

        logger.debug("Intentando eliminar entidad Test con ID: %s", test_uuid)
        if test_uuid not in self._storage:
            logger.warning("Intento de eliminar entidad no existente con ID: %s", test_uuid)
            raise TestNotFound(entity_id=test_uuid)

        del self._storage[test_uuid]
        logger.info("Entidad Test con ID '%s' eliminada exitosamente.", test_uuid)

    def list_all(self) -> List[TestEntity]:
        """
        Devuelve una lista de todas las entidades TestEntity en el almacenamiento.

        Returns:
            Una lista de instancias de TestEntity.
        """
        logger.debug("Recuperando todas las entidades Test.")
        return list(self._storage.values())