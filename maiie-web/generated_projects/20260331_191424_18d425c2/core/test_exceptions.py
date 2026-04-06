"""
Modulo: test_exceptions
Capa: Core

Descripcion:
Define las excepciones personalizadas para el dominio de 'Test'.
Estas excepciones permiten un manejo de errores mas granular y especifico
del contexto de negocio, en lugar de depender de excepciones genericas de Python.

Responsabilidades:
- Definir la excepcion 'TestNotFound' para casos donde una entidad no es encontrada.
- Proporcionar un mecanismo estandarizado para reportar errores de dominio.

Version: 1.0.0
"""

import logging
import uuid
from typing import Optional, Union

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

class TestNotFound(Exception):
    """
    Excepción lanzada cuando una entidad TestEntity específica no se encuentra.

    Esta excepción es fundamental para los casos de uso que intentan recuperar,
    actualizar o eliminar una entidad de prueba que no existe en la capa de
    persistencia. Proporciona contexto sobre el identificador de la entidad
    que falta, lo cual es útil para la depuración y para devolver mensajes de
    error claros a los clientes de la API.
    """

    def __init__(self, entity_id: Union[str, uuid.UUID], message: Optional[str] = None):
        """
        Inicializa la excepción TestNotFound.

        Args:
            entity_id: El ID (como string o UUID) de la entidad que no se encontró.
            message: Un mensaje de error personalizado opcional. Si no se proporciona,
                     se generará un mensaje predeterminado.
        """
        self.entity_id = entity_id
        self.message = message or f"La entidad de prueba con ID '{entity_id}' no fue encontrada."
        
        # Se llama al constructor de la clase base (Exception) para asegurar
        # un comportamiento estándar de las excepciones.
        super().__init__(self.message)
        
        logger.warning(
            "Excepción TestNotFound creada para la entidad con ID: %s",
            self.entity_id
        )

    def __str__(self) -> str:
        """
        Devuelve el mensaje de error legible para el usuario.
        """
        return self.message

    def __repr__(self) -> str:
        """
        Proporciona una representación de la excepción útil para desarrolladores.
        
        Esta representación puede ser utilizada para recrear el objeto de excepción
        si es necesario durante la depuración.
        """
        class_name = self.__class__.__name__
        return f"{class_name}(entity_id='{self.entity_id}', message='{self.message}')"