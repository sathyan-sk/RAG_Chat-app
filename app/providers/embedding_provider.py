import httpx

from app.core.config import settings


class EmbeddingProvider:
    async def embed_text(self, text: str) -> list[float]:
        url = f"{settings.OLLAMA_BASE_URL}/api/embed"
        payload = {
            "model": settings.OLLAMA_EMBED_MODEL,
            "input": text,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code != 200:
            try:
                error_body = response.json()
            except Exception:
                error_body = {"raw_text": response.text}
            raise ValueError(
                f"Embedding failed: status={response.status_code}, body={error_body}"
            )

        data = response.json()
        embeddings = data.get("embeddings", [])
        if not embeddings:
            raise ValueError("No embedding returned by embedding provider.")

        return embeddings[0]