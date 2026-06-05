"""wiki ingest command — parse, extract, create/update pages, commit."""

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from wiki_cli.parsers import detect_parser
from wiki_cli.parsers.base import ParseResult
from wiki_cli.utils import slugify
from wiki_cli.wiki_manager import WikiManager


@dataclass
class IngestResult:
    success: bool = False
    title: str = ""
    pages_created: int = 0
    pages_updated: int = 0
    error: str = ""


class IngestPipeline:
    def __init__(self, wiki_mgr: WikiManager, provider, vault_path: Path):
        self.wiki_mgr = wiki_mgr
        self.provider = provider
        self.vault_path = vault_path

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def run(self, source: str) -> IngestResult:
        """Full pipeline: parse -> LLM extract -> create/update pages -> copy raw -> update index/log -> commit."""
        result = IngestResult()
        try:
            # 1. Parse the source
            parser = detect_parser(source)
            parsed = parser.parse(source)

            # 2. LLM extraction
            extraction = self._extract(parsed)

            result.title = extraction.get("title", parsed.title)

            # 3. Copy raw source
            self._copy_raw(parsed)

            # 4. Create/update entity pages
            for entity in extraction.get("entities", []):
                created = self._create_or_update_entity(entity, extraction)
                if created:
                    result.pages_created += 1
                else:
                    result.pages_updated += 1

            # 5. Create/update concept pages
            for concept in extraction.get("concepts", []):
                created = self._create_or_update_concept(concept, extraction)
                if created:
                    result.pages_created += 1
                else:
                    result.pages_updated += 1

            # 6. Create source summary page
            self._create_source_summary(parsed, extraction)
            result.pages_created += 1

            # 7. Update index and log
            for entity in extraction.get("entities", []):
                slug = slugify(entity["name"])
                self.wiki_mgr.update_index(f"entities/{slug}", entity["name"], "Entities")
            for concept in extraction.get("concepts", []):
                slug = slugify(concept["name"])
                self.wiki_mgr.update_index(f"concepts/{slug}", concept["name"], "Concepts")

            self.wiki_mgr.append_log("ingest", result.title)

            # 8. Commit
            self.wiki_mgr.commit(f"ingest: {result.title}")

            result.success = True
        except Exception as e:
            result.error = str(e)

        return result

    def run_reference(self, url: str, description: str) -> IngestResult:
        """Save a reference-only entry (no LLM processing)."""
        result = IngestResult()
        try:
            slug = slugify(description or url)
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            content = (
                f"---\ntitle: \"{description}\"\ntype: reference\n"
                f"url: \"{url}\"\ncreated_at: {now}\npublish: true\n---\n\n"
                f"# {description}\n\n- URL: {url}\n- Added: {now}\n"
            )
            ref_path = self.vault_path / "sources" / "references" / f"{slug}.md"
            ref_path.parent.mkdir(parents=True, exist_ok=True)
            ref_path.write_text(content, encoding="utf-8")

            self.wiki_mgr.append_log("reference", description)
            self.wiki_mgr.commit(f"reference: {description}")

            result.success = True
            result.title = description
        except Exception as e:
            result.error = str(e)

        return result

    def run_inbox(self) -> list[IngestResult]:
        """Process all files in the inbox directory."""
        inbox_dir = self.vault_path / "sources" / "inbox"
        results = []
        for md_file in sorted(inbox_dir.glob("*.md")):
            r = self.run(str(md_file))
            # Remove from inbox after processing (whether success or not)
            if md_file.exists():
                md_file.unlink()
            results.append(r)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract(self, parsed: ParseResult) -> dict:
        """Use LLM to extract structured data from parsed content."""
        system_prompt = (
            "You are a knowledge extraction assistant. Extract structured information "
            "from the provided content. Return valid JSON with these fields:\n"
            "- title: a concise title summarizing the content\n"
            "- summary: a 2-3 sentence summary\n"
            "- takeaways: list of key takeaway strings\n"
            "- entities: list of {name, category, description} for people/tools/projects\n"
            "- concepts: list of {name, description} for ideas/patterns/principles\n"
            "- tags: list of lowercase tag strings\n\n"
            "Return ONLY valid JSON, no markdown fencing."
        )
        raw = self.provider.complete(system_prompt, parsed.content)
        # Strip markdown fencing if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        return json.loads(raw)

    def _copy_raw(self, parsed: ParseResult) -> Path:
        """Copy the raw source into sources/raw/."""
        slug = slugify(parsed.title)
        raw_dir = self.vault_path / "sources" / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        dest = raw_dir / f"{slug}.md"
        dest.write_text(parsed.content, encoding="utf-8")
        return dest

    def _create_or_update_entity(self, entity: dict, extraction: dict) -> bool:
        """Create or update an entity page. Returns True if created, False if updated."""
        slug = slugify(entity["name"])
        page_path = f"entities/{slug}"
        existing = self.wiki_mgr.read_page(page_path)

        if existing:
            updated = self._update_page(existing, entity)
            self.wiki_mgr.write_page(page_path, updated)
            return False
        else:
            content = self._generate_page(entity, "entity")
            self.wiki_mgr.write_page(page_path, content)
            return True

    def _create_or_update_concept(self, concept: dict, extraction: dict) -> bool:
        """Create or update a concept page. Returns True if created, False if updated."""
        slug = slugify(concept["name"])
        page_path = f"concepts/{slug}"
        existing = self.wiki_mgr.read_page(page_path)

        if existing:
            updated = self._update_page(existing, concept)
            self.wiki_mgr.write_page(page_path, updated)
            return False
        else:
            content = self._generate_page(concept, "concept")
            self.wiki_mgr.write_page(page_path, content)
            return True

    def _generate_page(self, info: dict, page_type: str) -> str:
        """Use LLM to generate a new wiki page."""
        schema_path = self.vault_path / "schema" / "SCHEMA.md"
        schema = schema_path.read_text(encoding="utf-8") if schema_path.exists() else ""

        template_path = self.vault_path / "schema" / "templates" / f"{page_type}.md"
        template = template_path.read_text(encoding="utf-8") if template_path.exists() else ""

        system_prompt = (
            "You are a wiki page generator. Create a well-structured markdown page "
            "following the schema and template provided. Include YAML frontmatter."
        )
        context = [schema, template] if template else [schema]
        prompt = (
            f"Create a {page_type} page for: {info.get('name', info.get('title', ''))}\n"
            f"Description: {info.get('description', '')}\n"
            f"Category: {info.get('category', page_type)}"
        )
        return self.provider.complete_with_context(system_prompt, context, prompt)

    def _update_page(self, existing: str, new_info: dict) -> str:
        """Use LLM to merge new information into an existing page."""
        system_prompt = (
            "You are a wiki page updater. Merge the new information into the existing page. "
            "Preserve all existing content. Add new facts in appropriate sections. "
            "Do not duplicate existing information. Return the complete updated page."
        )
        prompt = (
            f"Existing page:\n{existing}\n\n"
            f"New information to merge:\n{json.dumps(new_info, indent=2)}"
        )
        return self.provider.complete_with_context(system_prompt, [existing], prompt)

    def _create_source_summary(self, parsed: ParseResult, extraction: dict) -> None:
        """Create a source summary page."""
        slug = slugify(extraction.get("title", parsed.title))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Build entity/concept links
        links = []
        for entity in extraction.get("entities", []):
            e_slug = slugify(entity["name"])
            links.append(f"- [[entities/{e_slug}|{entity['name']}]]")
        for concept in extraction.get("concepts", []):
            c_slug = slugify(concept["name"])
            links.append(f"- [[concepts/{c_slug}|{concept['name']}]]")

        takeaways = "\n".join(f"- {t}" for t in extraction.get("takeaways", []))
        tags_str = ", ".join(extraction.get("tags", []))

        content = (
            f"---\ntitle: \"{extraction.get('title', parsed.title)}\"\n"
            f"type: source-summary\nsource_type: \"{parsed.source_type}\"\n"
            f"ingested_at: {now}\ntags: [{tags_str}]\npublish: true\n---\n\n"
            f"# {extraction.get('title', parsed.title)}\n\n"
            f"## Key Takeaways\n\n{takeaways}\n\n"
            f"## Summary\n\n{extraction.get('summary', '')}\n\n"
            f"## Entities & Concepts Mentioned\n\n" + "\n".join(links) + "\n"
        )

        page_path = f"topics/{slug}"
        self.wiki_mgr.write_page(page_path, content)
