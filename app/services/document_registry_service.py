import json
from pathlib import Path
from typing import Optional

from app.schemas.document_registry import DocumentRecord


class DocumentRegistryService:
    def __init__(self) -> None:
        self.registry_path = Path("data_resources/documents/document_registry.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            self.registry_path.write_text("[]", encoding="utf-8")

    def _load_registry(self) -> list[dict]:
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _save_registry(self, documents: list[dict]) -> None:
        self.registry_path.write_text(
            json.dumps(documents, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add_document(self, record: dict) -> None:
        documents = self._load_registry()
        documents.append(record)
        self._save_registry(documents)

    def list_documents(self) -> list[DocumentRecord]:
        return [DocumentRecord(**doc) for doc in self._load_registry()]

    def get_document(self, document_id: str) -> Optional[DocumentRecord]:
        documents = self._load_registry()
        for doc in documents:
            if doc["document_id"] == document_id:
                return DocumentRecord(**doc)
        return None

    def update_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        documents = self._load_registry()

        for doc in documents:
            if doc["document_id"] == document_id:
                doc["status"] = status
                doc["error_message"] = error_message
                self._save_registry(documents)
                return

        raise ValueError(f"Document not found: {document_id}")

    def deactivate_document(self, document_id: str) -> None:
        documents = self._load_registry()

        for doc in documents:
            if doc["document_id"] == document_id:
                doc["is_active"] = False
                self._save_registry(documents)
                return

        raise ValueError(f"Document not found: {document_id}")