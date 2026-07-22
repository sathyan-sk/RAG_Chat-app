from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    document_id: str


class EmbeddingResponse(BaseModel):
    document_id: str
    embedding_file: str
    vector_count: int
    status: str
    message: str