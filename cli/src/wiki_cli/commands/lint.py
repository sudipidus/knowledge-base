"""wiki lint command — structural health checks for the wiki."""

import re
from wiki_cli.wiki_manager import WikiManager


class WikiLinter:
    def __init__(self, wiki_mgr: WikiManager):
        self.wiki_mgr = wiki_mgr

    def check_broken_links(self) -> list[dict]:
        """Find wikilinks that point to non-existent pages."""
        issues = []
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            # Find all [[target]] or [[target|label]] links
            links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)
            for link in links:
                target = link.strip()
                # Try the target as-is and also with common prefixes
                if self.wiki_mgr.read_page(target) is None:
                    issues.append({
                        "check": "broken_link",
                        "page": page_path,
                        "detail": f"Broken link to [[{target}]]",
                    })
        return issues

    def check_orphan_pages(self) -> list[dict]:
        """Find pages that are not linked to from any other page."""
        all_pages = set(self.wiki_mgr.list_pages())
        linked_pages: set[str] = set()

        for page_path in all_pages:
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)
            for link in links:
                linked_pages.add(link.strip())

        # Also check the index for links
        index_content = (self.wiki_mgr.wiki_dir / "index.md").read_text(encoding="utf-8")
        index_links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", index_content)
        for link in index_links:
            linked_pages.add(link.strip())

        issues = []
        for page_path in all_pages:
            if page_path not in linked_pages:
                issues.append({
                    "check": "orphan_page",
                    "page": page_path,
                    "detail": f"Page '{page_path}' is not linked from any other page",
                })
        return issues

    def check_missing_frontmatter(self) -> list[dict]:
        """Find pages without YAML frontmatter."""
        issues = []
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            if not content.startswith("---"):
                issues.append({
                    "check": "missing_frontmatter",
                    "page": page_path,
                    "detail": f"Page '{page_path}' has no YAML frontmatter",
                })
        return issues

    def check_index_drift(self) -> list[dict]:
        """Find pages that exist but are not listed in the index."""
        issues = []
        index_path = self.wiki_mgr.wiki_dir / "index.md"
        if not index_path.exists():
            return issues
        index_content = index_path.read_text(encoding="utf-8")

        for page_path in self.wiki_mgr.list_pages():
            if page_path not in index_content:
                issues.append({
                    "check": "index_drift",
                    "page": page_path,
                    "detail": f"Page '{page_path}' is not listed in the index",
                })
        return issues

    def check_empty_sections(self) -> list[dict]:
        """Find pages with empty sections (heading followed by another heading or end of file)."""
        issues = []
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if re.match(r"^#{1,6}\s+", line):
                    # Check if the next non-blank line is another heading or end of content
                    remaining = lines[i + 1:]
                    non_blank = [l for l in remaining if l.strip()]
                    if non_blank and re.match(r"^#{1,6}\s+", non_blank[0]):
                        issues.append({
                            "check": "empty_section",
                            "page": page_path,
                            "detail": f"Empty section: {line.strip()}",
                        })
        return issues

    def run_all(self) -> dict:
        """Run all checks and return a summary report."""
        all_issues = []
        all_issues.extend(self.check_broken_links())
        all_issues.extend(self.check_orphan_pages())
        all_issues.extend(self.check_missing_frontmatter())
        all_issues.extend(self.check_index_drift())
        all_issues.extend(self.check_empty_sections())

        # Group by check type
        by_check: dict[str, list[dict]] = {}
        for issue in all_issues:
            check = issue["check"]
            by_check.setdefault(check, []).append(issue)

        return {
            "total_issues": len(all_issues),
            "by_check": by_check,
            "issues": all_issues,
        }
