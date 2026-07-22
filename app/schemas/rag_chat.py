from pydantic import BaseModel


class RagChatRequest(BaseModel):
    question: str
    top_k: int = 4


class RagChatSource(BaseModel):
    rank: int
    score: float
    source_file: str | None
    chunk_id: int
    text: str
    metadata: dict


class RagChatResponse(BaseModel):
    question: str
    answer: str
    top_k: int
    source_count: int
    sources: list[RagChatSource]
    status: str
    model_used: str
    embedding_model_used: str
    retrieval_backend: str
    prompt_version: str