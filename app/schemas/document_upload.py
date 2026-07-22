from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    original_filename: str
    stored_filename: str
    status: str
    message: str