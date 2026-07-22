import json
from pathlib import Path

import faiss
import numpy as np


class VectorStoreProvider:
    def __init__(self) -> None:
        self.index_path = Path("data_resources/vector_store/faiss/document_index.faiss")
        self.metadata_path = Path("data_resources/vector_store/faiss/document_index_metadata.json")

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        if not self.index_path.exists() or not self.metadata_path.exists():
            raise FileNotFoundError("FAISS index or metadata file not found.")

        index = faiss.read_index(str(self.index_path))

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        query_array = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(query_array)

        distances, indices = index.search(query_array, top_k)

        results = []
        for rank, (score, idx) in enumerate(zip(distances[0], indices[0]), start=1):
            if idx == -1 or idx >= len(metadata):
                continue

            item = metadata[idx]
            results.append(
                {
                    "rank": rank,
                    "score": float(score),
                    "source_file": item.get("source_file"),
                    "chunk_id": item["chunk_id"],
                    "text": item["text"],
                    "metadata": item.get("metadata", {}),
                }
            )

        return results