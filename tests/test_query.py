import pytest
from unittest.mock import MagicMock
from wiki_cli.commands.query import QueryEngine
from wiki_cli.wiki_manager import WikiManager


@pytest.fixture
def populated_vault(tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text(
        '---\ntitle: Python\ntags: [programming, language]\npublish: true\n---\n# Python\n\nA versatile programming language.'
    )
    (tmp_vault / "wiki/concepts/testing.md").write_text(
        '---\ntitle: Testing\ntags: [software, quality]\npublish: true\n---\n# Testing\n\nVerifying software works correctly.'
    )
    return tmp_vault


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.complete_with_context.return_value = (
        "Python is a versatile programming language commonly used for "
        "[[entities/testing|testing]] and automation. See [[entities/python]] for more."
    )
    return provider


@pytest.fixture
def query_engine(populated_vault, mock_provider):
    wiki_mgr = WikiManager(populated_vault)
    return QueryEngine(wiki_mgr, mock_provider)


def test_query_returns_answer(query_engine):
    answer = query_engine.ask("What is Python?")
    assert "Python" in answer
    assert len(answer) > 10


def test_query_searches_relevant_pages(query_engine, mock_provider):
    query_engine.ask("What is Python?")
    call_args = mock_provider.complete_with_context.call_args
    context = call_args[0][1]
    assert any("Python" in c for c in context)


def test_query_save(query_engine, populated_vault):
    answer = query_engine.ask("What is Python?", save=True)
    explorations = list((populated_vault / "wiki/explorations").glob("*.md"))
    assert len(explorations) == 1
    content = explorations[0].read_text()
    assert "Python" in content
