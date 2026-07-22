import json
from pathlib import Path

import faiss
import numpy as np

from app.core.config import settings


class FaissIndexService:
    def __init__(self) -> None:
        self.base_path = Path(settings.DOCUMENTS_BASE_PATH)
        self.embeddings_path = self.base_path / "embeddings"

        self.vector_store_path = Path("data_resources/vector_store/faiss")
        self.vector_store_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.vector_store_path / "document_index.faiss"
        self.metadata_file = self.vector_store_path / "document_index_metadata.json"

    def index_embedding_file(self, embedding_file_name: str) -> dict:
        embedding_file_path = self.embeddings_path / embedding_file_name

        if not embedding_file_path.exists():
            raise FileNotFoundError(f"Embedding file not found: {embedding_file_name}")

        with open(embedding_file_path, "r", encoding="utf-8") as f:
            embedding_data = json.load(f)

        chunks = embedding_data.get("chunks", [])
        if not chunks:
            raise ValueError("Embedding file contains no chunks.")

        vectors = []
        metadata_records = []

        for chunk in chunks:
            embedding = chunk.get("embedding", [])
            if not embedding:
                continue

            vectors.append(embedding)
            metadata_records.append(
                {
                    "source_file": embedding_data.get("source_file"),
                    "embedding_file_name": embedding_file_name,
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "char_count": chunk["char_count"],
                    "metadata": chunk["metadata"],
                    "embedding_dimension": chunk["embedding_dimension"],
                }
            )

        if not vectors:
            raise ValueError("No valid embeddings found in embedding file.")

        vector_array = np.array(vectors, dtype="float32")
        faiss.normalize_L2(vector_array)

        dimension = vector_array.shape[1]

        if self.index_file.exists() and self.metadata_file.exists():
            index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                existing_metadata = json.load(f)
        else:
            index = faiss.IndexFlatIP(dimension)
            existing_metadata = []

        if index.d != dimension:
            raise ValueError(
                f"Embedding dimension mismatch. Existing index dimension={index.d}, new dimension={dimension}"
            )

        index.add(vector_array)
        existing_metadata.extend(metadata_records)

        faiss.write_index(index, str(self.index_file))

        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(existing_metadata, f, ensure_ascii=False, indent=2)

        return {
            "embedding_file_name": embedding_file_name,
            "indexed_count": len(metadata_records),
            "vector_dimension": dimension,
            "index_path": str(self.index_file).replace("\\", "/"),
            "metadata_path": str(self.metadata_file).replace("\\", "/"),
            "backend": settings.VECTOR_BACKEND,
            "status": "indexed",
        }