import re
from pathlib import Path
from .base import ParseResult


class TextParser:
    def parse(self, source: str) -> ParseResult:
        path = Path(source)
        content = path.read_text(encoding="utf-8")
        title_match = re.match(r"^#\s+(.+)", content)
        title = title_match.group(1) if title_match else path.stem
        return ParseResult(content=content, title=title, source_type="text", source_path=str(path))
