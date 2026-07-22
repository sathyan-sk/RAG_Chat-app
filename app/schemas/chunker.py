from pydantic import BaseModel


class ChunkRequest(BaseModel):
    document_id: str


class ChunkResponse(BaseModel):
    document_id: str
    chunk_file: str
    chunk_count: int
    status: str
    message: str