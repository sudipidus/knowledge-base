import pytest
import subprocess
from pathlib import Path
from wiki_cli.wiki_manager import WikiManager


@pytest.fixture
def wiki_mgr(tmp_vault):
    subprocess.run(["git", "init"], cwd=tmp_vault, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_vault, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_vault, capture_output=True)
    return WikiManager(tmp_vault)


def test_read_page(wiki_mgr, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("---\ntitle: Python\n---\n# Python\nA language.")
    content = wiki_mgr.read_page("entities/python")
    assert "Python" in content
    assert "A language." in content


def test_read_page_not_found(wiki_mgr):
    assert wiki_mgr.read_page("entities/nonexistent") is None


def test_write_page(wiki_mgr, tmp_vault):
    wiki_mgr.write_page("entities/rust", "---\ntitle: Rust\n---\n# Rust\nA systems language.")
    assert (tmp_vault / "wiki/entities/rust.md").exists()
    assert "systems language" in (tmp_vault / "wiki/entities/rust.md").read_text()


def test_update_index(wiki_mgr, tmp_vault):
    wiki_mgr.update_index("entities/rust", "Rust", "entities")
    index = (tmp_vault / "wiki/index.md").read_text()
    assert "[[entities/rust|Rust]]" in index


def test_append_log(wiki_mgr, tmp_vault):
    wiki_mgr.append_log("ingest", "Test Article")
    log = (tmp_vault / "wiki/log.md").read_text()
    assert "ingest | \"Test Article\"" in log


def test_list_pages(wiki_mgr, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python")
    (tmp_vault / "wiki/entities/rust.md").write_text("# Rust")
    pages = wiki_mgr.list_pages("entities")
    assert len(pages) == 2


def test_commit(wiki_mgr, tmp_vault):
    (tmp_vault / "wiki/entities/test.md").write_text("# Test")
    wiki_mgr.commit("test: add test page")
    result = subprocess.run(["git", "log", "--oneline", "-1"], cwd=tmp_vault, capture_output=True, text=True)
    assert "test: add test page" in result.stdout


def test_find_pages_mentioning(wiki_mgr, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python\nUsed in [[machine-learning]]")
    (tmp_vault / "wiki/concepts/testing.md").write_text("# Testing\nNo mentions here.")
    pages = wiki_mgr.find_pages_mentioning("machine-learning")
    assert "entities/python" in pages
    assert "concepts/testing" not in pages
