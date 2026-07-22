from pathlib import Path

import fitz


class PDFLoader:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def load(self) -> list[dict]:
        result = self.extract_text(self._file_path)
        return result.get("pages", [])

    def extract_text(self, file_path: str) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        pages = []

        with fitz.open(str(path)) as doc:
            for page_number in range(doc.page_count):
                page = doc.load_page(page_number)
                raw_text = page.get_text("text", sort=True)
                text = raw_text.strip() if isinstance(raw_text, str) else ""

                if not text:
                    words = page.get_text("words", sort=True) or []
                    if words:
                        text = " ".join(word[4] for word in words if len(word) > 4).strip()

                pages.append(
                    {
                        "page_number": page_number + 1,
                        "text": text,
                        "char_count": len(text),
                    }
                )

        full_text = "\n\n".join(
            f"[Page {page['page_number']}]\n{page['text']}"
            for page in pages
            if page["text"]
        ).strip()

        return {
            "file_name": path.name,
            "page_count": len(pages),
            "pages": pages,
            "full_text": full_text,
            "char_count": len(full_text),
        }