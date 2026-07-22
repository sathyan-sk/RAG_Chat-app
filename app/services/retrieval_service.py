from app.providers.embedding_provider import EmbeddingProvider
from app.providers.vector_store_provider import VectorStoreProvider


class RetrievalService:
    def __init__(self) -> None:
        self.embedding_provider = EmbeddingProvider()
        self.vector_store_provider = VectorStoreProvider()

    async def retrieve(self, query: str, top_k: int = 5) -> dict:
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        query_vector = await self.embedding_provider.embed_text(query)
        results = self.vector_store_provider.search(query_vector=query_vector, top_k=top_k)

        return {
            "query": query,
            "top_k": top_k,
            "match_count": len(results),
            "results": results,
            "status": "retrieved",
            "embedding_model_used": "ollama:" + self.embedding_provider.__class__.__name__,
            "retrieval_backend": "faiss",
        }