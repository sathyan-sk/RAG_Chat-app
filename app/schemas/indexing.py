from pydantic import BaseModel


class IndexingRequest(BaseModel):
    embedding_file_name: str


class IndexingResponse(BaseModel):
    embedding_file_name: str
    indexed_count: int
    vector_dimension: int
    index_path: str
    metadata_path: str
    backend: str
    status: str