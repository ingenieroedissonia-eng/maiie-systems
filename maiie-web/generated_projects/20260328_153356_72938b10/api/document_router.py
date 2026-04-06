"""
Modulo: Document Router
Capa: API

Descripcion:
Define los endpoints de la API REST para la gestion de documentos.

Responsabilidades:
- Exponer operaciones CRUD para documentos a traves de HTTP.
- Validar los datos de entrada de las solicitudes HTTP.
- Orquestar la interaccion entre las solicitudes HTTP y los casos de uso del core.
- Manejar errores especificos de la capa de API y traducirlos a codigos de estado HTTP.

Version: 1.0.0
"""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.document import Document
from core.exceptions import DocumentManagerException
from core.use_cases import CreateDocument
from infrastructure.document_repository import InMemoryDocumentRepository

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


class DocumentCreateRequest(BaseModel):
    """Schema para la solicitud de creación de un nuevo documento."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="El título del documento."
    )
    content: str = Field(
        ...,
        min_length=1,
        description="El contenido del documento."
    )


class DocumentResponse(BaseModel):
    """Schema para la respuesta de un documento."""
    id: str
    title: str
    content: str

    class Config:
        """Configuración de Pydantic para el mapeo de atributos."""
        from_attributes = True


# --- Dependency Injection Setup ---

# Esta implementación del repositorio es un singleton a nivel de módulo.
# En una aplicación más compleja, se gestionaría con un contenedor de dependencias más avanzado.
_document_repository_instance = InMemoryDocumentRepository()

def get_document_repository() -> InMemoryDocumentRepository:
    """
    Proveedor de dependencia para el repositorio de documentos.
    Devuelve una instancia singleton del repositorio en memoria.
    """
    return _document_repository_instance


def get_create_document_use_case(
    repository: InMemoryDocumentRepository = Depends(get_document_repository),
) -> CreateDocument:
    """
    Proveedor de dependencia para el caso de uso CreateDocument.
    Inyecta el repositorio de documentos en el caso de uso.
    """
    return CreateDocument(document_repository=repository)


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo documento",
    description="Crea un nuevo documento con un título y contenido, y devuelve el documento creado con su ID.",
)
def create_document(
    document_data: DocumentCreateRequest,
    create_use_case: CreateDocument = Depends(get_create_document_use_case),
) -> Document:
    """
    Endpoint para crear un nuevo documento.

    Args:
        document_data: Los datos para el nuevo documento, conteniendo título y contenido.
        create_use_case: El caso de uso responsable de la lógica de negocio de la creación de documentos.

    Returns:
        La entidad del documento recién creado.

    Raises:
        HTTPException: Si los datos del documento son inválidos (422), si ocurre un error de dominio (400)
                       o si ocurre un error inesperado en el servidor (500).
    """
    logger.info("Recibida solicitud para crear un nuevo documento con título: '%s'", document_data.title)
    try:
        created_document = create_use_case.execute(
            title=document_data.title,
            content=document_data.content
        )
        logger.info("Documento creado exitosamente con ID: %s", created_document.id)
        return created_document
    except ValueError as e:
        logger.warning("Error de validación al crear el documento: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except DocumentManagerException as e:
        logger.error("Error de dominio al crear un documento: %s", e, exc_info=False)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.critical("Error inesperado al crear un documento: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno en el servidor.",
        )