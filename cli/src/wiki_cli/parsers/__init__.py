from pathlib import Path
from .base import ParseResult


def detect_parser(source: str):
    if source.startswith("http://") or source.startswith("https://"):
        from .web import WebParser
        return WebParser()
    path = Path(source)
    if path.suffix.lower() == ".pdf":
        from .pdf import PDFParser
        return PDFParser()
    from .text import TextParser
    return TextParser()
