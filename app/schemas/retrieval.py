from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrievedChunk(BaseModel):
    rank: int
    score: float
    source_file: str | None
    chunk_id: int
    text: str
    metadata: dict


class RetrievalResponse(BaseModel):
    query: str
    top_k: int
    match_count: int
    results: list[RetrievedChunk]
    status: str