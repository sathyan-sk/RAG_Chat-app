import json
from pathlib import Path

import faiss
import numpy as np

from app.services.document_registry_service import DocumentRegistryService


class IndexingService:
    def __init__(self) -> None:
        self.embedding_dir = Path("data_resources/documents/embeddings")
        self.index_dir = Path("data_resources/vector_store/faiss")
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.index_path = self.index_dir / "document_index.faiss"
        self.metadata_path = self.index_dir / "document_index_metadata.json"

        self.registry_service = DocumentRegistryService()

    def rebuild_index(self) -> dict:
        documents = self.registry_service.list_documents()
        active_docs = [doc for doc in documents if doc.is_active]

        all_vectors = []
        all_metadata = []
        indexed_document_ids = []

        for doc in active_docs:
            embedding_file = self.embedding_dir / f"{doc.document_id}.json"
            if not embedding_file.exists():
                continue

            data = json.loads(embedding_file.read_text(encoding="utf-8"))
            vectors = data.get("vectors", [])

            for item in vectors:
                all_vectors.append(item["embedding"])
                all_metadata.append(
                    {
                        "document_id": item["document_id"],
                        "source_file": item.get("source_file"),
                        "chunk_id": item["chunk_id"],
                        "text": item["text"],
                        "metadata": item.get("metadata", {}),
                    }
                )

            indexed_document_ids.append(doc.document_id)

        if not all_vectors:
            raise ValueError("No active embedded documents found for indexing.")

        vector_array = np.array(all_vectors, dtype="float32")
        faiss.normalize_L2(vector_array)

        dim = vector_array.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vector_array)

        faiss.write_index(index, str(self.index_path))
        self.metadata_path.write_text(
            json.dumps(all_metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return {
            "status": "indexed",
            "document_count": len(indexed_document_ids),
            "vector_count": len(all_vectors),
            "index_file": str(self.index_path),
            "metadata_file": str(self.metadata_path),
        }