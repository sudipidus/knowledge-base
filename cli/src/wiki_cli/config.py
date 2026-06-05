import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class WikiConfig:
    provider: str
    provider_config: dict = field(default_factory=dict)
    vault_path: Path = Path(".")
    stale_threshold_days: int = 30
    auto_commit: bool = True

    @property
    def schema_dir(self) -> Path:
        return self.vault_path / "schema"

    @property
    def sources_dir(self) -> Path:
        return self.vault_path / "sources"

    @property
    def wiki_dir(self) -> Path:
        return self.vault_path / "wiki"

    @property
    def raw_dir(self) -> Path:
        return self.sources_dir / "raw"

    @property
    def references_dir(self) -> Path:
        return self.sources_dir / "references"

    @property
    def inbox_dir(self) -> Path:
        return self.sources_dir / "inbox"


def _resolve_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} with environment variable values."""
    def replacer(match):
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    return re.sub(r"\$\{(\w+)\}", replacer, value)


def _resolve_env_vars_in_dict(d: dict) -> dict:
    """Recursively resolve env vars in a dictionary."""
    resolved = {}
    for k, v in d.items():
        if isinstance(v, str):
            resolved[k] = _resolve_env_vars(v)
        elif isinstance(v, dict):
            resolved[k] = _resolve_env_vars_in_dict(v)
        else:
            resolved[k] = v
    return resolved


def load_config(config_path: Path) -> WikiConfig:
    """Load and parse wiki.yaml configuration."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    provider = raw.get("provider", "ollama")
    provider_config = raw.get(provider, {})
    provider_config = _resolve_env_vars_in_dict(provider_config)

    vault_path = config_path.parent / raw.get("vault_path", ".")
    vault_path = vault_path.resolve()

    return WikiConfig(
        provider=provider,
        provider_config=provider_config,
        vault_path=vault_path,
        stale_threshold_days=raw.get("stale_threshold_days", 30),
        auto_commit=raw.get("auto_commit", True),
    )
