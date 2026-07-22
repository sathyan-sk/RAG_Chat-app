from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.indexing_service import IndexingService

router = APIRouter(prefix="/indexing", tags=["indexing"])

indexing_service = IndexingService()


class IndexingResponse(BaseModel):
    status: str
    document_count: int
    vector_count: int
    index_file: str
    metadata_file: str


@router.post("/rebuild", response_model=IndexingResponse)
async def rebuild_index():
    try:
        return indexing_service.rebuild_index()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(exc)}")