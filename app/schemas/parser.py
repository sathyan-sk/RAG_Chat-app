from pydantic import BaseModel


class DocumentParseRequest(BaseModel):
    document_id: str


class DocumentParseResponse(BaseModel):
    document_id: str
    parsed_file: str
    status: str
    message: str