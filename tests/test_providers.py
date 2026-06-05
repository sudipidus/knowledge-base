import pytest
from wiki_cli.providers.base import LLMProvider
from wiki_cli.providers import get_provider


def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_get_provider_claude():
    provider = get_provider("claude", {"api_key": "test", "model": "claude-sonnet-4-20250514"})
    assert isinstance(provider, LLMProvider)


def test_get_provider_openai():
    provider = get_provider("openai", {"api_key": "test", "model": "gpt-4o"})
    assert isinstance(provider, LLMProvider)


def test_get_provider_ollama():
    provider = get_provider("ollama", {"model": "llama3.1", "base_url": "http://localhost:11434"})
    assert isinstance(provider, LLMProvider)


def test_get_provider_unknown():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("unknown", {})
