"""wiki reingest command — re-fetch and update a previously ingested source."""

import re
from pathlib import Path

from wiki_cli.commands.ingest import IngestPipeline, IngestResult
from wiki_cli.parsers import detect_parser
from wiki_cli.providers.base import LLMProvider
from wiki_cli.wiki_manager import WikiManager


class ReingestPipeline:
    def __init__(self, wiki_mgr: WikiManager, provider: LLMProvider, vault_path: Path):
        self.wiki_mgr = wiki_mgr
        self.provider = provider
        self.vault_path = vault_path
        self.ingest = IngestPipeline(wiki_mgr, provider, vault_path)

    def run(self, source: str) -> IngestResult:
        try:
            parser = detect_parser(source)
            parsed = parser.parse(source)
            new_hash = parsed.content_hash

            old_hash = self._find_existing_hash(source)
            if old_hash and old_hash == new_hash:
                return IngestResult(success=True, title="(unchanged)")

            return self.ingest.run(source)
        except Exception as e:
            return IngestResult(success=False, error=str(e))

    def _find_existing_hash(self, source: str) -> str | None:
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            if source in content:
                hash_match = re.search(
                    r'content_hash:\s*"?(sha256:[a-f0-9]+)"?', content
                )
                if hash_match:
                    return hash_match.group(1)
        return None
