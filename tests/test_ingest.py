import pytest
import subprocess
import json
from pathlib import Path
from unittest.mock import MagicMock
from wiki_cli.commands.ingest import IngestPipeline
from wiki_cli.wiki_manager import WikiManager
from wiki_cli.parsers.base import ParseResult


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.complete.return_value = json.dumps({
        "title": "Test Article Summary",
        "summary": "This is a summary of the test article.",
        "takeaways": ["Key point 1", "Key point 2"],
        "entities": [
            {"name": "Python", "category": "tool", "description": "A programming language"},
        ],
        "concepts": [
            {"name": "Testing", "description": "Verifying software correctness"},
        ],
        "tags": ["python", "testing"],
    })
    provider.complete_with_context.return_value = "---\ntitle: Python\ntype: entity\ntags: [python]\ncreated_at: 2026-06-05\npublish: true\n---\n# Python\n\nA programming language."
    return provider


@pytest.fixture
def ingest_pipeline(tmp_vault, mock_provider):
    subprocess.run(["git", "init"], cwd=tmp_vault, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_vault, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_vault, capture_output=True)
    (tmp_vault / "schema" / "templates").mkdir(parents=True, exist_ok=True)
    (tmp_vault / "schema" / "templates" / "source-summary.md").write_text("template")
    (tmp_vault / "schema" / "SCHEMA.md").write_text("schema")
    wiki_mgr = WikiManager(tmp_vault)
    return IngestPipeline(wiki_mgr, mock_provider, tmp_vault)


def test_ingest_text_file(ingest_pipeline, tmp_vault):
    source_file = tmp_vault / "test-article.md"
    source_file.write_text("# Test Article\n\nThis is about Python and testing.")
    result = ingest_pipeline.run(str(source_file))
    assert result.success
    assert result.pages_created > 0
    raw_files = list((tmp_vault / "sources" / "raw").glob("*.md"))
    assert len(raw_files) >= 1
    index = (tmp_vault / "wiki" / "index.md").read_text()
    assert "Python" in index or "Test" in index


def test_ingest_reference(ingest_pipeline, tmp_vault):
    result = ingest_pipeline.run_reference("https://github.com/org/repo", "A cool repo")
    assert result.success
    ref_files = list((tmp_vault / "sources" / "references").glob("*.md"))
    assert len(ref_files) == 1


def test_ingest_inbox(ingest_pipeline, tmp_vault):
    (tmp_vault / "sources" / "inbox" / "note1.md").write_text("# Note 1\nContent.")
    (tmp_vault / "sources" / "inbox" / "note2.md").write_text("# Note 2\nMore content.")
    results = ingest_pipeline.run_inbox()
    assert len(results) == 2
    remaining = list((tmp_vault / "sources" / "inbox").glob("*.md"))
    assert len(remaining) == 0


def test_ingest_atomic_failure(ingest_pipeline, tmp_vault):
    ingest_pipeline.provider.complete.side_effect = Exception("LLM error")
    source_file = tmp_vault / "bad-article.md"
    source_file.write_text("# Bad Article\nContent.")
    result = ingest_pipeline.run(str(source_file))
    assert not result.success
    assert result.error == "LLM error"
