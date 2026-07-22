from fastapi import APIRouter, HTTPException

from app.schemas.rag_chat import RagChatRequest, RagChatResponse
from app.services.rag_chat_service import RagChatService

router = APIRouter(prefix="/rag", tags=["rag"])

rag_chat_service = RagChatService()


@router.post("/chat", response_model=RagChatResponse)
async def rag_chat(request: RagChatRequest):
    try:
        return await rag_chat_service.answer_question(
            question=request.question,
            top_k=request.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected RAG chat failure: {str(exc)}",
        )