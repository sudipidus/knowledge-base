import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class WikiManager:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.wiki_dir = vault_path / "wiki"

    def read_page(self, page_path: str) -> str | None:
        full_path = self.wiki_dir / f"{page_path}.md"
        if not full_path.exists():
            return None
        return full_path.read_text(encoding="utf-8")

    def write_page(self, page_path: str, content: str) -> Path:
        full_path = self.wiki_dir / f"{page_path}.md"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return full_path

    def update_index(self, page_path: str, title: str, category: str) -> None:
        index_path = self.wiki_dir / "index.md"
        index = index_path.read_text(encoding="utf-8")
        entry = f"- [[{page_path}|{title}]]"
        if entry in index:
            return
        category_header = f"## {category.title()}"
        if category_header in index:
            index = index.replace(category_header, f"{category_header}\n{entry}")
        else:
            index += f"\n{category_header}\n{entry}\n"
        index_path.write_text(index, encoding="utf-8")

    def append_log(self, operation: str, title: str) -> None:
        log_path = self.wiki_dir / "log.md"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry = f'\n## [{now}] {operation} | "{title}"\n'
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def list_pages(self, subdirectory: str = "") -> list[str]:
        search_dir = self.wiki_dir / subdirectory if subdirectory else self.wiki_dir
        pages = []
        for md_file in search_dir.rglob("*.md"):
            rel = md_file.relative_to(self.wiki_dir)
            page_path = str(rel.with_suffix(""))
            if page_path not in ("index", "log"):
                pages.append(page_path)
        return sorted(pages)

    def find_pages_mentioning(self, term: str) -> list[str]:
        results = []
        for md_file in self.wiki_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            if f"[[{term}]]" in content or f"[[{term}|" in content:
                rel = md_file.relative_to(self.wiki_dir)
                results.append(str(rel.with_suffix("")))
        return sorted(results)

    def commit(self, message: str) -> None:
        subprocess.run(["git", "add", "-A"], cwd=self.vault_path, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", message], cwd=self.vault_path, capture_output=True, check=True)

    def get_all_page_summaries(self) -> list[dict]:
        summaries = []
        for page_path in self.list_pages():
            content = self.read_page(page_path)
            if not content:
                continue
            tags = []
            tag_match = re.search(r"tags:\s*\[([^\]]*)\]", content)
            if tag_match:
                tags = [t.strip() for t in tag_match.group(1).split(",")]
            heading_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            heading = heading_match.group(1) if heading_match else page_path
            summaries.append({"path": page_path, "title": heading, "tags": tags, "content": content})
        return summaries
