from app.services.document_registry_service import DocumentRegistryService
from app.services.parser_service import ParserService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService


class IngestionPipelineService:
    def __init__(self) -> None:
        self.registry_service = DocumentRegistryService()
        self.parser_service = ParserService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.indexing_service = IndexingService()

    async def process_document(self, document_id: str) -> None:
        try:
            self.registry_service.update_status(document_id, "parsing")
            self.parser_service.parse_document(document_id)

            self.registry_service.update_status(document_id, "chunking")
            self.chunking_service.chunk_document(document_id)

            self.registry_service.update_status(document_id, "embedding")
            await self.embedding_service.embed_document(document_id)

            self.registry_service.update_status(document_id, "indexing")
            self.indexing_service.rebuild_index()

            self.registry_service.update_status(document_id, "indexed")

        except Exception as exc:
            self.registry_service.update_status(
                document_id=document_id,
                status="failed",
                error_message=str(exc),
            )