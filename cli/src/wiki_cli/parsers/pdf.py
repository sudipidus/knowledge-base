from pathlib import Path
import pdfplumber
from .base import ParseResult


class PDFParser:
    def parse(self, source: str) -> ParseResult:
        path = Path(source)
        pages = []
        title = path.stem
        with pdfplumber.open(path) as pdf:
            if pdf.metadata and pdf.metadata.get("Title"):
                title = pdf.metadata["Title"]
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        content = "\n\n---\n\n".join(pages)
        return ParseResult(content=content, title=title, source_type="pdf", source_path=str(path))
