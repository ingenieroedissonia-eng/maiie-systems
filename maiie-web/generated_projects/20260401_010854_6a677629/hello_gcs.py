"""
Modulo: hello_gcs
Capa: Application (Standalone Script)

Descripcion:
Este módulo contiene una función simple para imprimir un mensaje de saludo.
Está diseñado como un punto de entrada o prueba inicial para verificar la
ejecución de un script en un entorno, como podría ser una función de nube
o un contenedor.

Responsabilidades:
- Definir una función que imprime un saludo estático.
- Proporcionar un punto de entrada para la ejecución del script.
- Configurar un logging básico para el seguimiento de la ejecución.

Version: 1.0.0
"""

import logging
import sys

# Configuración básica del logger para la salida estándar
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


def hello_gcs() -> None:
    """
    Imprime un mensaje de saludo en la consola y registra la operación.

    Esta función es el núcleo del script y su propósito es demostrar
    una ejecución exitosa mediante la producción de una salida visible.
    """
    try:
        logger.info("Iniciando la ejecución de la función hello_gcs.")
        message = "Hola desde GCS"
        print(message)
        logger.info("Mensaje '%s' impreso correctamente.", message)
    except Exception as e:
        # Aunque es poco probable en esta función simple, se incluye para robustez
        logger.error("Ocurrió un error inesperado en hello_gcs: %s", e, exc_info=True)
        # En un escenario real, podríamos querer relanzar o manejar el error
        # de una forma más específica.
        raise


def main() -> None:
    """
    Función principal que orquesta la ejecución del script.
    """
    logger.info("Iniciando el script principal hello_gcs.py.")
    try:
        hello_gcs()
        logger.info("El script hello_gcs.py ha finalizado exitosamente.")
    except Exception as e:
        logger.critical("El script ha fallado debido a un error no recuperado: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()