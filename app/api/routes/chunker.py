from fastapi import APIRouter, HTTPException

from app.schemas.chunker import ChunkRequest, ChunkResponse
from app.services.chunking_service import ChunkingService

router = APIRouter(prefix="/chunker", tags=["chunker"])

chunking_service = ChunkingService()


@router.post("/run", response_model=ChunkResponse)
async def chunk_document(request: ChunkRequest):
    try:
        return chunking_service.chunk_document(request.document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {str(exc)}")