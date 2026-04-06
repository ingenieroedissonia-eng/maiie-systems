"""
Modulo: Hello
Capa: Aplicacion Principal

Descripcion:
Este modulo contiene la implementacion principal del programa, cuya unica
responsabilidad es imprimir un mensaje de saludo en la consola.

Responsabilidades:
- Definir la funcion principal de ejecucion.
- Imprimir el mensaje 'Hola MAIIE'.
- Servir como punto de entrada para la aplicacion.

Version: 1.0.0
"""

import logging
import sys
from typing import NoReturn

# Configuracion basica del logging para la aplicacion
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Funcion principal que ejecuta la logica del programa.

    Realiza la impresion del mensaje 'Hola MAIIE' en la salida estandar,
    manejando posibles errores de E/S durante la operacion.
    """
    message = "Hola MAIIE"
    try:
        logger.info("Iniciando la ejecucion del programa de saludo.")
        print(message)
        logger.info("Mensaje impreso exitosamente en la consola.")
    except OSError as e:
        logger.error(f"Error de E/S al intentar imprimir el mensaje: {e}")
        sys.exit(1)


def _handle_unexpected_shutdown() -> NoReturn:
    """
    Maneja la salida inesperada del programa.
    
    Esta funcion se registra para ser llamada en caso de una salida no controlada,
    asegurando que se registre un mensaje de error.
    """
    logger.critical("El programa ha terminado de forma inesperada.")
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
        logger.info("El programa finalizo correctamente.")
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("Ejecucion interrumpida por el usuario.")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Se ha producido un error no controlado: {e}")
        _handle_unexpected_shutdown()