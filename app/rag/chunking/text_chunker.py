from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class TextChunker:
    def __init__(self) -> None:
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )

    def split_text(self, text: str) -> list[str]:
        return self.splitter.split_text(text)