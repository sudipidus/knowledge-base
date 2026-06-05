import pytest
from pathlib import Path
from wiki_cli.config import WikiConfig, load_config


def test_load_config_from_yaml(tmp_path):
    config_file = tmp_path / "wiki.yaml"
    config_file.write_text("""
provider: claude
claude:
  api_key: test-key
  model: claude-sonnet-4-20250514
vault_path: .
stale_threshold_days: 30
auto_commit: true
""")
    config = load_config(config_file)
    assert config.provider == "claude"
    assert config.vault_path == tmp_path
    assert config.stale_threshold_days == 30
    assert config.auto_commit is True


def test_load_config_resolves_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_API_KEY", "resolved-key")
    config_file = tmp_path / "wiki.yaml"
    config_file.write_text("""
provider: claude
claude:
  api_key: ${TEST_API_KEY}
  model: claude-sonnet-4-20250514
""")
    config = load_config(config_file)
    assert config.provider_config["api_key"] == "resolved-key"


def test_load_config_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nonexistent.yaml")


def test_config_provider_config_extraction(tmp_path):
    config_file = tmp_path / "wiki.yaml"
    config_file.write_text("""
provider: ollama
ollama:
  model: llama3.1
  base_url: http://localhost:11434
""")
    config = load_config(config_file)
    assert config.provider_config["model"] == "llama3.1"
    assert config.provider_config["base_url"] == "http://localhost:11434"
