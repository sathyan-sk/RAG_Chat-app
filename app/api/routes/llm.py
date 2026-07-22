import httpx
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/models")
async def list_models():
    url = f"{settings.OLLAMA_BASE_URL}/api/tags"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        return {
            "fastapi_route_ok": True,
            "ollama_status_code": response.status_code,
            "ollama_response": response.json(),
        }


@router.post("/chat/test")
async def chat_test():
    url = f"{settings.OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": settings.OLLAMA_CHAT_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "Reply in one short sentence: confirm that local Ollama chat is working."
            }
        ]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)

    body = {}
    try:
        body = response.json()
    except Exception:
        body = {"raw_text": response.text}

    return {
        "fastapi_route_ok": True,
        "request_model": settings.OLLAMA_CHAT_MODEL,
        "ollama_status_code": response.status_code,
        "ollama_response": body,
    }


@router.post("/embeddings/test")
async def embeddings_test():
    url = f"{settings.OLLAMA_BASE_URL}/api/embed"
    payload = {
        "model": settings.OLLAMA_EMBED_MODEL,
        "input": "This is a test sentence for embedding generation."
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)

    body = response.json()
    embeddings = body.get("embeddings", [])
    vector_size = len(embeddings[0]) if embeddings else 0

    return {
        "fastapi_route_ok": True,
        "request_model": settings.OLLAMA_EMBED_MODEL,
        "ollama_status_code": response.status_code,
        "vector_count": len(embeddings),
        "vector_size": vector_size,
        "ollama_response": body,
    }