import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.services.document_registry_service import DocumentRegistryService


class DocumentService:
    def __init__(self) -> None:
        self.raw_dir = Path("data_resources/documents/raw")
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.registry_service = DocumentRegistryService()

    async def upload_document(self, file: UploadFile) -> dict:
        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are supported.")

        document_id = str(uuid.uuid4())
        stored_filename = f"{document_id}.pdf"
        file_path = self.raw_dir / stored_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        record = {
            "document_id": document_id,
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "content_type": file.content_type,
            "status": "uploaded",
            "is_active": True,
            "error_message": None,
        }

        self.registry_service.add_document(record)

        return {
            "document_id": document_id,
            "original_filename": file.filename,
            "stored_filename": stored_filename,
            "status": "uploaded",
            "message": "Document uploaded successfully. Processing started.",
        }