import json
from pathlib import Path

from app.providers.embedding_provider import EmbeddingProvider
from app.services.document_registry_service import DocumentRegistryService


class EmbeddingService:
    def __init__(self) -> None:
        self.chunk_dir = Path("data_resources/documents/chunks")
        self.embedding_dir = Path("data_resources/documents/embeddings")
        self.embedding_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_provider = EmbeddingProvider()
        self.registry_service = DocumentRegistryService()

    async def embed_document(self, document_id: str) -> dict:
        record = self.registry_service.get_document(document_id)
        if not record:
            raise FileNotFoundError(f"Document not found: {document_id}")

        chunk_file = self.chunk_dir / f"{document_id}.json"
        if not chunk_file.exists():
            raise FileNotFoundError(f"Chunk file not found for document: {document_id}")

        data = json.loads(chunk_file.read_text(encoding="utf-8"))
        chunks = data.get("chunks", [])

        if not chunks:
            raise ValueError("No chunks found for embedding.")

        results = []
        for item in chunks:
            vector = await self.embedding_provider.embed_text(item["text"])
            results.append(
                {
                    "document_id": document_id,
                    "chunk_id": item["chunk_id"],
                    "text": item["text"],
                    "embedding": vector,
                    "metadata": item.get("metadata", {}),
                    "source_file": data.get("original_filename"),
                }
            )

        output = {
            "document_id": document_id,
            "original_filename": data.get("original_filename"),
            "embedding_model": "ollama",
            "vectors": results,
        }

        embedding_file = self.embedding_dir / f"{document_id}.json"
        embedding_file.write_text(
            json.dumps(output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "document_id": document_id,
            "embedding_file": str(embedding_file),
            "vector_count": len(results),
            "status": "embedded",
            "message": "Document embedded successfully.",
        }