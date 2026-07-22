from fastapi import APIRouter, HTTPException

from app.schemas.embedding import EmbeddingRequest, EmbeddingResponse
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/embedding", tags=["embedding"])

embedding_service = EmbeddingService()


@router.post("/run", response_model=EmbeddingResponse)
async def embed_document(request: EmbeddingRequest):
    try:
        return await embedding_service.embed_document(request.document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(exc)}")