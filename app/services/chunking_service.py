import json
from pathlib import Path

from app.services.document_registry_service import DocumentRegistryService


class ChunkingService:
    def __init__(self) -> None:
        self.parsed_dir = Path("data_resources/documents/parsed")
        self.chunk_dir = Path("data_resources/documents/chunks")
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        self.registry_service = DocumentRegistryService()

    def chunk_document(
        self,
        document_id: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 150
    ) -> dict:
        record = self.registry_service.get_document(document_id)
        if not record:
            raise FileNotFoundError(f"Document not found: {document_id}")

        parsed_file = self.parsed_dir / f"{document_id}.json"
        if not parsed_file.exists():
            raise FileNotFoundError(f"Parsed file not found for document: {document_id}")

        data = json.loads(parsed_file.read_text(encoding="utf-8"))
        pages = data.get("pages", [])

        full_text = "\n\n".join(
            page.get("text", "") for page in pages if page.get("text", "").strip()
        ).strip()

        if not full_text:
            raise ValueError("No text found to chunk.")

        chunks = []
        start = 0
        chunk_id = 1

        while start < len(full_text):
            end = start + chunk_size
            text = full_text[start:end].strip()

            if text:
                chunks.append(
                    {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "text": text,
                        "metadata": {
                            "source_file": data.get("original_filename"),
                        },
                    }
                )
                chunk_id += 1

            start += max(1, chunk_size - chunk_overlap)

        output = {
            "document_id": document_id,
            "original_filename": data.get("original_filename"),
            "chunks": chunks,
        }

        chunk_file = self.chunk_dir / f"{document_id}.json"
        chunk_file.write_text(
            json.dumps(output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "document_id": document_id,
            "chunk_file": str(chunk_file),
            "chunk_count": len(chunks),
            "status": "chunked",
            "message": "Document chunked successfully.",
        }