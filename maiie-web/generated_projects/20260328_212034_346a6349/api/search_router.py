"""
Modulo: Search Router
Capa: Presentation (API)

Descripcion:
Este módulo define el enrutador de FastAPI para la funcionalidad de búsqueda de documentos.
Expone un endpoint GET /search que permite a los clientes realizar búsquedas semánticas.

Responsabilidades:
- Definir la ruta /search.
- Recibir y validar los parámetros de la consulta de búsqueda.
- Invocar el caso de uso de búsqueda de documentos.
- Manejar errores específicos del dominio y de la aplicación, traduciéndolos a respuestas HTTP apropiadas.
- Serializar los resultados de la búsqueda en formato JSON para la respuesta.

Version: 1.0.0
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Se asume que las siguientes dependencias existen y están disponibles para importación.
# Estas clases y funciones son parte de otras capas de la arquitectura.
from core.search_use_case import SearchDocuments
from core.exceptions import QueryEmptyError, SearchError
from infrastructure.dependencies import get_search_use_case

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

# Creación de una instancia de APIRouter para agrupar los endpoints de búsqueda
router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)


class DocumentResponse(BaseModel):
    """
    Modelo Pydantic para la respuesta de un documento en el endpoint de búsqueda.
    Define la estructura de los datos que se enviarán al cliente.
    """
    id: str = Field(..., description="Identificador único del documento.")
    title: str = Field(..., description="Título del documento.")
    content: str = Field(..., description="Contenido parcial o completo del documento.")

    class Config:
        """Configuración del modelo Pydantic."""
        from_attributes = True


@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="Realizar una búsqueda semántica de documentos",
    description="Busca documentos que coincidan semánticamente con el texto de la consulta proporcionada.",
)
async def search_documents(
    query: str = Query(
        ...,
        min_length=1,
        max_length=300,
        title="Texto de búsqueda",
        description="El texto de la consulta para buscar documentos relevantes. No puede estar vacío.",
        alias="q",
    ),
    search_use_case: SearchDocuments = Depends(get_search_use_case),
) -> List[DocumentResponse]:
    """
    Endpoint para buscar documentos.

    Recibe una consulta de texto 'q' y utiliza el caso de uso 'SearchDocuments'
    para encontrar y devolver una lista de documentos coincidentes.

    Args:
        query: El texto a buscar, proporcionado como parámetro de consulta 'q'.
        search_use_case: Instancia del caso de uso inyectada como dependencia.

    Returns:
        Una lista de objetos DocumentResponse que representan los documentos encontrados.

    Raises:
        HTTPException:
            - 400 (Bad Request): Si la consulta está vacía o es inválida.
            - 500 (Internal Server Error): Si ocurre un error inesperado durante la búsqueda.
    """
    logger.info(f"Iniciando búsqueda para la consulta: '{query}'")
    try:
        documents = search_use_case.execute(query=query)
        logger.info(f"Búsqueda completada. Se encontraron {len(documents)} documentos para la consulta: '{query}'")
        return [DocumentResponse.model_validate(doc) for doc in documents]
    except QueryEmptyError as e:
        logger.warning(f"Intento de búsqueda con consulta vacía: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e
    except SearchError as e:
        logger.error(f"Error de dominio durante la búsqueda para la consulta '{query}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al procesar la búsqueda: {e}"
        ) from e
    except Exception as e:
        logger.exception(f"Error inesperado durante la búsqueda para la consulta '{query}': {e}")
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error interno inesperado en el servidor."
        ) from e