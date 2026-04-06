"""
Modulo: Document Router
Capa: Presentation (API)

Descripcion:
Define los endpoints de la API para la gestión de documentos.
Este router maneja las solicitudes HTTP, las valida y las delega a los
casos de uso correspondientes.

Responsabilidades:
- Definir endpoints para crear y obtener documentos.
- Validar los datos de entrada de las solicitudes (a través de Pydantic).
- Serializar los datos de salida (respuestas JSON).
- Manejar las excepciones de la capa de aplicación y traducirlas a respuestas HTTP.
- Inyectar dependencias (casos de uso y repositorios).

Version: 1.0.0
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from core.document import Document
from core.exceptions import DocumentNotFound
from core.use_cases import CreateDocument, GetDocument, DocumentRepository
from infrastructure.document_repository import InMemoryDocumentRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# --- Pydantic Models ---

class DocumentCreateRequest(BaseModel):
    """Modelo de solicitud para la creación de un documento."""
    title: str = Field(..., min_length=1, description="The title of the document.")
    content: str = Field(..., min_length=1, description="The content of the document.")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My First Document",
                "content": "This is the content of my first document."
            }
        }

class DocumentResponse(BaseModel):
    """Modelo de respuesta para un documento."""
    id: str
    title: str
    content: str

# --- Dependencies ---

_document_repository_instance = InMemoryDocumentRepository()

def get_document_repository() -> DocumentRepository:
    """
    Proveedor de dependencia para el repositorio de documentos.
    Utiliza un patrón singleton para mantener una única instancia del repositorio en memoria.
    """
    return _document_repository_instance

def get_create_document_use_case(
    repo: DocumentRepository = Depends(get_document_repository)
) -> CreateDocument:
    """Proveedor de dependencia para el caso de uso CreateDocument."""
    return CreateDocument(document_repository=repo)

def get_get_document_use_case(
    repo: DocumentRepository = Depends(get_document_repository)
) -> GetDocument:
    """Proveedor de dependencia para el caso de uso GetDocument."""
    return GetDocument(document_repository=repo)

# --- Endpoints ---

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_endpoint(
    request: DocumentCreateRequest,
    use_case: CreateDocument = Depends(get_create_document_use_case),
):
    """
    Crea un nuevo documento a partir de un título y contenido.

    - **title**: El título del documento.
    - **content**: El contenido del documento.
    \f
    :param request: Datos de entrada para crear el documento.
    :param use_case: Instancia del caso de uso para crear documentos.
    :return: El documento recién creado.
    """
    try:
        logger.info(f"Received request to create document with title: {request.title}")
        new_document = use_case.execute(title=request.title, content=request.content)
        logger.info(f"Successfully created document with ID: {new_document.id}")
        return new_document
    except Exception as e:
        logger.error(f"Error creating document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the document."
        )

@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document_by_id_endpoint(
    document_id: str,
    use_case: GetDocument = Depends(get_get_document_use_case),
):
    """
    Recupera un documento específico por su ID.

    - **document_id**: El identificador único del documento a recuperar.
    \f
    :param document_id: El ID del documento a buscar.
    :param use_case: Instancia del caso de uso para obtener documentos.
    :return: El documento encontrado.
    :raises HTTPException: Si el documento no se encuentra (404) o si ocurre un error inesperado (500).
    """
    try:
        logger.info(f"Attempting to retrieve document with ID: {document_id}")
        document = use_case.execute(document_id=document_id)
        if document:
            logger.info(f"Successfully retrieved document with ID: {document_id}")
            return document
        
        raise DocumentNotFound(document_id=document_id)

    except DocumentNotFound as e:
        logger.warning(f"Document not found for ID {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred while retrieving document {document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )