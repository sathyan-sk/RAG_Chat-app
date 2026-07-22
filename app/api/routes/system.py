import httpx
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/config")
async def get_config():
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "app_env": settings.APP_ENV,
        "debug": settings.DEBUG,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "ollama_chat_model": settings.OLLAMA_CHAT_MODEL,
        "ollama_embed_model": settings.OLLAMA_EMBED_MODEL,
        "documents_base_path": settings.DOCUMENTS_BASE_PATH,
    }


@router.get("/ollama")
async def ollama_status():
    url = f"{settings.OLLAMA_BASE_URL}/api/tags"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        return {
            "status": "ok",
            "ollama_reachable": True,
            "models": data.get("models", []),
        }
    except Exception as exc:
        return {
            "status": "error",
            "ollama_reachable": False,
            "error": str(exc),
        }