import pytest
from wiki_cli.commands.lint import WikiLinter
from wiki_cli.wiki_manager import WikiManager

@pytest.fixture
def wiki_linter(tmp_vault):
    wiki_mgr = WikiManager(tmp_vault)
    return WikiLinter(wiki_mgr)

def test_find_broken_links(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python\nSee [[nonexistent-page]] and [[entities/also-missing]]")
    issues = wiki_linter.check_broken_links()
    assert len(issues) >= 1
    assert any("nonexistent-page" in i["detail"] for i in issues)

def test_find_orphan_pages(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python\nNo links to this.")
    (tmp_vault / "wiki/entities/rust.md").write_text("# Rust\nSee [[entities/python]]")
    issues = wiki_linter.check_orphan_pages()
    orphans = [i["page"] for i in issues]
    assert "entities/rust" in orphans
    assert "entities/python" not in orphans

def test_find_missing_frontmatter(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python\nNo frontmatter here.")
    issues = wiki_linter.check_missing_frontmatter()
    assert len(issues) == 1

def test_find_index_drift(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("---\ntitle: Python\n---\n# Python")
    issues = wiki_linter.check_index_drift()
    assert len(issues) == 1
    assert "python" in issues[0]["page"]

def test_run_all_checks(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python\n[[missing-link]]")
    report = wiki_linter.run_all()
    assert "total_issues" in report
    assert report["total_issues"] > 0
