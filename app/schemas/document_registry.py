from typing import Optional
from pydantic import BaseModel


class DocumentRecord(BaseModel):
    document_id: str
    original_filename: str
    stored_filename: str
    content_type: str
    status: str
    is_active: bool = True
    error_message: Optional[str] = None