from fastapi import APIRouter, HTTPException

from app.schemas.retrieval import RetrievalRequest, RetrievalResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/retrieval", tags=["retrieval"])

retrieval_service = RetrievalService()


@router.post("/search", response_model=RetrievalResponse)
async def search(request: RetrievalRequest):
    try:
        result = await retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
        )
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(exc)}")