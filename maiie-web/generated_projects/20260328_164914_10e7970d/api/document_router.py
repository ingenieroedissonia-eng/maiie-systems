"""
Modulo: Document Router
Capa: API (Presentation)

Descripcion:
Este módulo define los endpoints de la API para la gestión de documentos.
Utiliza FastAPI para exponer la funcionalidad del core a través de una API REST.

Responsabilidades:
- Definir el router de FastAPI para la ruta /documents.
- Implementar el endpoint POST / para la creación de documentos.
- Orquestar la llamada al caso de uso de creación de documentos.
- Manejar las respuestas HTTP y los errores específicos de la capa de API.

Version: 1.0.0
"""

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from core.document import Document
from core.use_cases import CreateDocument, DocumentRepository
from core.exceptions import ApplicationException
from infrastructure.document_repository import InMemoryDocumentRepository

logger = logging.getLogger(__name__)

# Pydantic models for request and response
class DocumentCreateRequest(BaseModel):
    """Modelo de Pydantic para la carga útil de creación de un documento."""
    title: str = Field(..., min_length=1, description="El título del documento.")
    content: str = Field(..., min_length=1, description="El contenido del documento.")

class DocumentResponse(BaseModel):
    """Modelo de Pydantic para la respuesta de un documento."""
    id: str
    title: str
    content: str

# API Router instance
router = APIRouter(prefix="/documents", tags=["Documents"])

# Dependency Injection setup
# En una aplicación real, esta instancia sería gestionada por el contenedor de la aplicación.
document_repository_instance = InMemoryDocumentRepository()

def get_document_repository() -> DocumentRepository:
    """
    Proveedor de dependencia para el repositorio de documentos.
    Retorna una instancia singleton del repositorio en memoria.
    """
    return document_repository_instance

def get_create_document_use_case(
    repo: Annotated[DocumentRepository, Depends(get_document_repository)]
) -> CreateDocument:
    """
    Proveedor de dependencia para el caso de uso CreateDocument.
    Inyecta el repositorio en el caso de uso.
    """
    return CreateDocument(document_repository=repo)

@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo documento",
    description="Crea un nuevo documento con un título y contenido proporcionados.",
)
async def create_document_endpoint(
    document_data: DocumentCreateRequest,
    use_case: Annotated[CreateDocument, Depends(get_create_document_use_case)],
):
    """
    Endpoint para crear un nuevo documento.

    Recibe un título y contenido y utiliza el caso de uso `CreateDocument`
    para persistir y devolver el nuevo documento.

    Args:
        document_data: Datos de entrada para el nuevo documento.
        use_case: Instancia del caso de uso `