from typing import List

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.schemas.document_upload import DocumentUploadResponse
from app.schemas.document_registry import DocumentRecord
from app.services.document_service import DocumentService
from app.services.document_registry_service import DocumentRegistryService
from app.services.ingestion_pipeline_service import IngestionPipelineService

router = APIRouter(prefix="/documents", tags=["documents"])

document_service = DocumentService()
registry_service = DocumentRegistryService()
pipeline_service = IngestionPipelineService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        result = await document_service.upload_document(file)
        background_tasks.add_task(
            pipeline_service.process_document,
            result["document_id"],
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(exc)}")


@router.get("/", response_model=List[DocumentRecord])
async def list_documents():
    return registry_service.list_documents()


@router.get("/{document_id}", response_model=DocumentRecord)
async def get_document(document_id: str):
    document = registry_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document