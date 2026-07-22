from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RAG Backend"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "dev"
    DEBUG: bool = True

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "qwen2.5:3b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    DOCUMENTS_BASE_PATH: str = "data_resources/documents"

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    EMBEDDING_BATCH_SIZE: int = 20

    VECTOR_BACKEND: str = "faiss"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()