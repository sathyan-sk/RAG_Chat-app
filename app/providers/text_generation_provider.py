import httpx

from app.core.config import settings


class TextGenerationProvider:
    async def generate_answer(self, system_prompt: str, user_message: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": settings.OLLAMA_CHAT_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code != 200:
            try:
                error_body = response.json()
            except Exception:
                error_body = {"raw_text": response.text}
            raise ValueError(
                f"Text generation failed: status={response.status_code}, body={error_body}"
            )

        data = response.json()
        return (
            data.get("message", {}).get("content", "").strip()
            or "I do not know based on the available documents."
        )