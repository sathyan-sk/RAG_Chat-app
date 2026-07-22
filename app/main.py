from fastapi import FastAPI

from app.api.routes.chunker import router as chunker_router
from app.api.routes.documents import router as documents_router
from app.api.routes.embedding import router as embedding_router
from app.api.routes.health import router as health_router
from app.api.routes.indexing import router as indexing_router
from app.api.routes.llm import router as llm_router
from app.api.routes.parser import router as parser_router
from app.api.routes.rag_chat import router as rag_chat_router
from app.api.routes.retrieval import router as retrieval_router
from app.api.routes.system import router as system_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(health_router)
app.include_router(system_router)
app.include_router(llm_router)
app.include_router(documents_router)
app.include_router(parser_router)
app.include_router(chunker_router)
app.include_router(embedding_router)
app.include_router(indexing_router)
app.include_router(retrieval_router)
app.include_router(rag_chat_router)


@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }