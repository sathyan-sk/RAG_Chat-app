from app.core.config import settings
from app.core.prompts import PROMPT_VERSION, build_rag_system_prompt
from app.providers.text_generation_provider import TextGenerationProvider
from app.services.retrieval_service import RetrievalService


class RagChatService:
    def __init__(self) -> None:
        self.retrieval_service = RetrievalService()
        self.text_generation_provider = TextGenerationProvider()

    async def answer_question(self, question: str, top_k: int = 4) -> dict:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        retrieval_result = await self.retrieval_service.retrieve(question, top_k=top_k)
        sources = retrieval_result.get("results", [])

        context = "\n\n".join(
            [
                f"[Source {item['rank']}] "
                f"(file={item.get('source_file')}, chunk_id={item.get('chunk_id')})\n"
                f"{item.get('text', '')}"
                for item in sources
            ]
        ).strip()

        system_prompt = build_rag_system_prompt(context=context)
        answer = await self.text_generation_provider.generate_answer(
            system_prompt=system_prompt,
            user_message=question,
        )

        return {
            "question": question,
            "answer": answer,
            "top_k": top_k,
            "source_count": len(sources),
            "sources": sources,
            "status": "answered",
            "model_used": settings.OLLAMA_CHAT_MODEL,
            "embedding_model_used": settings.OLLAMA_EMBED_MODEL,
            "retrieval_backend": "faiss",
            "prompt_version": PROMPT_VERSION,
        }