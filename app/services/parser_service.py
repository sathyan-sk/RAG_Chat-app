import json
from pathlib import Path

from app.services.document_registry_service import DocumentRegistryService
from app.rag.loaders.pdf_loader import PDFLoader


class ParserService:
    def __init__(self) -> None:
        self.raw_dir = Path("data_resources/documents/raw")
        self.parsed_dir = Path("data_resources/documents/parsed")
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self.registry_service = DocumentRegistryService()

    def parse_document(self, document_id: str) -> dict:
        record = self.registry_service.get_document(document_id)
        if not record:
            raise FileNotFoundError(f"Document not found: {document_id}")

        pdf_path = self.raw_dir / record.stored_filename
        if not pdf_path.exists():
            raise FileNotFoundError(f"Raw PDF not found for document: {document_id}")

        loader = PDFLoader(str(pdf_path))
        pages = loader.load()

        parsed_output = {
            "document_id": document_id,
            "original_filename": record.original_filename,
            "pages": pages,
        }

        parsed_file = self.parsed_dir / f"{document_id}.json"
        parsed_file.write_text(
            json.dumps(parsed_output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "document_id": document_id,
            "parsed_file": str(parsed_file),
            "status": "parsed",
            "message": "Document parsed successfully.",
        }