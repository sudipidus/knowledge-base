import hashlib
from dataclasses import dataclass


@dataclass
class ParseResult:
    content: str
    title: str
    source_type: str
    source_path: str = ""

    @property
    def content_hash(self) -> str:
        h = hashlib.sha256(self.content.encode()).hexdigest()
        return f"sha256:{h}"
