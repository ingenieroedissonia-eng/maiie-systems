"""
Modulo: hello_gcs
Capa: Application/Entrypoint

Descripcion:
Este script contiene una función simple para imprimir un mensaje de saludo,
simulando un punto de entrada para una aplicación que podría interactuar
con Google Cloud Storage (GCS).

Responsabilidades:
- Definir una función de saludo.
- Ejecutar la función de saludo desde un bloque principal.
- Configurar logging básico para el seguimiento de la ejecución.

Version: 1.0.0
"""

import logging
import sys
from typing import NoReturn

# --- Configuración del Logging ---
# Configura el logger para mostrar mensajes de nivel INFO y superiores.
# El formato incluye la marca de tiempo, el nombre del logger, el nivel del mensaje y el mensaje.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# --- Funciones Principales ---

def greet_gcs() -> None:
    """
    Imprime un mensaje de saludo a la salida estándar.

    Esta función encapsula la lógica de negocio principal de este script,
    que es simplemente mostrar un mensaje. Registra eventos antes y después
    de la operación de impresión para un seguimiento detallado.

    Raises:
        IOError: Si ocurre un error durante la operación de escritura en
                 la salida estándar (por ejemplo, si la tubería está rota).
    """
    message = "Hola desde GCS"
    logger.info("Preparando para imprimir el mensaje de saludo.")
    try:
        print(message)
        logger.info("El mensaje '%s' ha sido impreso correctamente.", message)
    except IOError as e:
        logger.error(
            "Fallo la operación de escritura en la salida estándar: %s",
            e,
            exc_info=True
        )
        # Re-lanzar la excepción para que el llamador pueda manejarla.
        raise


def main() -> int:
    """
    Punto de entrada principal del script.

    Coordina la ejecución del script, llamando a la función de saludo
    y manejando cualquier excepción que pueda surgir durante el proceso.

    Returns:
        int: Retorna 0 en caso de éxito y 1 en caso de error.
    """
    logger.info("Iniciando la ejecución del script hello_gcs.")
    try:
        greet_gcs()
        logger.info("El script hello_gcs se ha ejecutado exitosamente.")
        return 0
    except Exception as e:
        # Captura cualquier excepción no manejada específicamente en las capas inferiores.
        logger.critical(
            "Error crítico no recuperable durante la ejecución: %s",
            e,
            exc_info=True
        )
        return 1


if __name__ == "__main__":
    # Si el script se ejecuta directamente, llama a la función main
    # y sale con el código de estado que esta retorne.
    # Esto es una buena práctica para la integración con sistemas de CI/CD y orquestadores.
    exit_code = main()
    sys.exit(exit_code)