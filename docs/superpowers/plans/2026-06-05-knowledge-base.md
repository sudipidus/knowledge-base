# Knowledge Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a personal LLM-powered knowledge base with Python CLI, Obsidian vault, and Quartz publishing following Karpathy's wiki pattern.

**Architecture:** Three-layer system — immutable sources, LLM-maintained wiki pages, and a schema layer with templates. Python CLI (`wiki`) drives all operations (init, ingest, query, lint, publish). LLM provider is configurable (Claude/OpenAI/Ollama).

**Tech Stack:** Python 3.10+, typer, httpx, beautifulsoup4, markdownify, pdfplumber, anthropic/openai/ollama SDKs, PyYAML, Quartz v4, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-06-05-knowledge-base-design.md`

---

## File Structure

```
cli/
├── pyproject.toml                    # Package config, dependencies, [project.scripts] wiki entry
└── src/
    └── wiki_cli/
        ├── __init__.py
        ├── main.py                   # Typer app, register subcommands
        ├── config.py                 # Load wiki.yaml, resolve env vars, WikiConfig dataclass
        ├── wiki_manager.py           # Core wiki operations: read/write pages, update index/log, git commit
        ├── commands/
        │   ├── __init__.py
        │   ├── init_cmd.py           # wiki init — scaffold directory structure + defaults
        │   ├── ingest.py             # wiki ingest — parse, summarize, extract, create/update pages
        │   ├── reingest.py           # wiki reingest — re-fetch, compare hash, diff-update
        │   ├── query.py              # wiki query — search wiki, synthesize answer, optional save
        │   ├── lint.py               # wiki lint — structural checks, --fix, --deep
        │   └── publish.py            # wiki publish — Quartz build/preview wrapper
        ├── providers/
        │   ├── __init__.py           # get_provider() factory
        │   ├── base.py               # LLMProvider ABC
        │   ├── claude.py             # Anthropic SDK provider
        │   ├── openai_provider.py    # OpenAI SDK provider
        │   └── ollama.py             # Ollama HTTP provider
        └── parsers/
            ├── __init__.py           # detect_parser() factory
            ├── base.py               # Parser ABC
            ├── web.py                # URL -> markdown
            ├── pdf.py                # PDF -> markdown
            └── text.py               # Markdown/text passthrough

schema/
├── SCHEMA.md                        # Wiki conventions for LLM
└── templates/
    ├── entity.md                    # Template for entity pages
    ├── concept.md                   # Template for concept pages
    ├── source-summary.md            # Template for source summaries
    └── comparison.md                # Template for comparison/synthesis pages

wiki/
├── index.md                         # Content catalog
├── log.md                           # Activity log
├── entities/.gitkeep
├── concepts/.gitkeep
├── topics/.gitkeep
├── syntheses/.gitkeep
└── explorations/.gitkeep

sources/
├── raw/.gitkeep
├── references/.gitkeep
└── inbox/.gitkeep

tests/
├── conftest.py                      # Shared fixtures (tmp vault, mock provider)
├── test_config.py
├── test_wiki_manager.py
├── test_parsers.py
├── test_providers.py
├── test_init_cmd.py
├── test_ingest.py
├── test_query.py
└── test_lint.py

wiki.yaml                            # Default config
.env.example                         # Env var placeholders
.gitignore
.github/workflows/publish.yml
cli/
├── pyproject.toml
└── src/
    └── wiki_cli/
        ...
        ├── utils.py                  # Shared utilities (slugify)
        ...
```

---

### Task 1: Project Scaffolding & CLI Skeleton

**Files:**
- Create: `cli/pyproject.toml`
- Create: `cli/src/wiki_cli/__init__.py`
- Create: `cli/src/wiki_cli/main.py`
- Create: `cli/src/wiki_cli/utils.py`
- Create: `tests/conftest.py`

- [ ] **Step 0: Initialize git repo and root config files**

```bash
cd ~/projects/knowledge-base
git init
```

Create `.gitignore`:
```
.env
public/
.obsidian/workspace.json
.obsidian/workspace-mobile.json
__pycache__/
*.pyc
.venv/
node_modules/
```

Create `.env.example`:
```
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

Create `wiki.yaml`:
```yaml
provider: ollama

claude:
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-sonnet-4-20250514

openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o

ollama:
  model: llama3.1
  base_url: http://localhost:11434

vault_path: .
stale_threshold_days: 30
auto_commit: true
```

```bash
git add .gitignore .env.example wiki.yaml
git commit -m "chore: initial repo setup with config files"
```

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "wiki-cli"
version = "0.1.0"
description = "Personal LLM-powered knowledge base CLI"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.12",
    "httpx>=0.27",
    "beautifulsoup4>=4.12",
    "markdownify>=0.13",
    "pdfplumber>=0.11",
    "pyyaml>=6.0",
    "rich>=13.0",
]

[project.optional-dependencies]
claude = ["anthropic>=0.40"]
openai = ["openai>=1.50"]
ollama = ["ollama>=0.4"]
all = ["wiki-cli[claude,openai,ollama]"]
dev = [
    "pytest>=8.0",
]

[project.scripts]
wiki = "wiki_cli.main:app"
```

- [ ] **Step 2: Create main.py with typer app**

```python
import typer

app = typer.Typer(
    name="wiki",
    help="Personal LLM-powered knowledge base CLI",
    no_args_is_help=True,
)


@app.command()
def init():
    """Initialize a new knowledge base."""
    typer.echo("wiki init - not yet implemented")


@app.command()
def ingest(source: str = typer.Argument(None), inbox: bool = False, ref: bool = False):
    """Ingest a source into the knowledge base."""
    typer.echo("wiki ingest - not yet implemented")


@app.command()
def reingest(source: str = typer.Argument(...)):
    """Re-fetch and update a previously ingested source."""
    typer.echo("wiki reingest - not yet implemented")


@app.command()
def query(question: str = typer.Argument(None), save: bool = False, interactive: bool = typer.Option(False, "-i")):
    """Query the knowledge base."""
    typer.echo("wiki query - not yet implemented")


@app.command()
def lint(fix: bool = False, deep: bool = False):
    """Run health checks on the wiki."""
    typer.echo("wiki lint - not yet implemented")


@app.command()
def publish(preview: bool = False):
    """Build and publish the wiki with Quartz."""
    typer.echo("wiki publish - not yet implemented")


if __name__ == "__main__":
    app()
```

- [ ] **Step 3: Create `__init__.py`**

```python
# wiki_cli
```

- [ ] **Step 3b: Create shared `utils.py`**

```python
# cli/src/wiki_cli/utils.py
import re


def slugify(text: str) -> str:
    """Convert text to a kebab-case slug safe for filenames.

    Examples: "Node.js" -> "nodejs", "C++" -> "cpp", "Hello World!" -> "hello-world"
    """
    text = text.lower().strip()
    text = text.replace("+", "p").replace(".", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]
```

- [ ] **Step 4: Create conftest.py with shared fixtures**

```python
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault directory structure."""
    dirs = [
        "schema/templates",
        "sources/raw",
        "sources/references",
        "sources/inbox",
        "wiki/entities",
        "wiki/concepts",
        "wiki/topics",
        "wiki/syntheses",
        "wiki/explorations",
    ]
    for d in dirs:
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "wiki/index.md").write_text("# Index\n")
    (tmp_path / "wiki/log.md").write_text("# Activity Log\n")
    return tmp_path
```

- [ ] **Step 5: Install package in dev mode and verify CLI runs**

Run: `cd ~/projects/knowledge-base && pip install -e "cli[all,dev]"`
Run: `wiki --help`
Expected: Help text showing init, ingest, reingest, query, lint, publish commands

- [ ] **Step 6: Commit**

```bash
git add cli/ tests/conftest.py
git commit -m "feat: project scaffolding with CLI skeleton and test fixtures"
```

---

### Task 2: Configuration System

**Files:**
- Create: `cli/src/wiki_cli/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write failing tests for config loading**

```python
# tests/test_config.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/projects/knowledge-base && pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'wiki_cli.config'`

- [ ] **Step 3: Implement config.py**

```python
# cli/src/wiki_cli/config.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add cli/src/wiki_cli/config.py tests/test_config.py
git commit -m "feat: configuration system with env var resolution"
```

---

### Task 3: LLM Provider Interface & Implementations

**Files:**
- Create: `cli/src/wiki_cli/providers/__init__.py`
- Create: `cli/src/wiki_cli/providers/base.py`
- Create: `cli/src/wiki_cli/providers/claude.py`
- Create: `cli/src/wiki_cli/providers/openai_provider.py`
- Create: `cli/src/wiki_cli/providers/ollama.py`
- Create: `tests/test_providers.py`

- [ ] **Step 1: Write failing tests for provider interface**

```python
# tests/test_providers.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_providers.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement base.py**

Note: All providers are **synchronous** since the CLI is single-user and serial by design (spec decision #10). No need for async overhead.

```python
# cli/src/wiki_cli/providers/base.py
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str) -> str:
        """Send a prompt with system instructions and return the response."""
        ...

    @abstractmethod
    def complete_with_context(
        self, system: str, context: list[str], prompt: str
    ) -> str:
        """Send a prompt with system instructions and context documents."""
        ...

    def _build_context_prompt(self, context: list[str], prompt: str) -> str:
        context_block = "\n\n---\n\n".join(context)
        return f"## Context Documents\n\n{context_block}\n\n---\n\n## Question\n\n{prompt}"
```

- [ ] **Step 4: Implement claude.py**

```python
# cli/src/wiki_cli/providers/claude.py
from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(self, system: str, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def complete_with_context(
        self, system: str, context: list[str], prompt: str
    ) -> str:
        return self.complete(system, self._build_context_prompt(context, prompt))
```

- [ ] **Step 5: Implement openai_provider.py**

```python
# cli/src/wiki_cli/providers/openai_provider.py
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def complete(self, system: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def complete_with_context(
        self, system: str, context: list[str], prompt: str
    ) -> str:
        return self.complete(system, self._build_context_prompt(context, prompt))
```

- [ ] **Step 6: Implement ollama.py**

```python
# cli/src/wiki_cli/providers/ollama.py
import httpx
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, system: str, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "system": system,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["response"]

    def complete_with_context(
        self, system: str, context: list[str], prompt: str
    ) -> str:
        return self.complete(system, self._build_context_prompt(context, prompt))
```

- [ ] **Step 7: Implement providers/__init__.py with factory**

```python
# cli/src/wiki_cli/providers/__init__.py
from .base import LLMProvider


def get_provider(name: str, config: dict) -> LLMProvider:
    """Factory to create an LLM provider by name."""
    if name == "claude":
        from .claude import ClaudeProvider
        return ClaudeProvider(**config)
    elif name == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(**config)
    elif name == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider(**config)
    else:
        raise ValueError(f"Unknown provider: {name}")
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `pytest tests/test_providers.py -v`
Expected: All 5 tests PASS

- [ ] **Step 9: Commit**

```bash
git add cli/src/wiki_cli/providers/ tests/test_providers.py
git commit -m "feat: LLM provider interface with Claude, OpenAI, and Ollama implementations"
```

---

### Task 4: Parsers (Web, PDF, Text)

**Files:**
- Create: `cli/src/wiki_cli/parsers/__init__.py`
- Create: `cli/src/wiki_cli/parsers/base.py`
- Create: `cli/src/wiki_cli/parsers/web.py`
- Create: `cli/src/wiki_cli/parsers/pdf.py`
- Create: `cli/src/wiki_cli/parsers/text.py`
- Create: `tests/test_parsers.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_parsers.py
import pytest
from pathlib import Path
from wiki_cli.parsers import detect_parser
from wiki_cli.parsers.text import TextParser
from wiki_cli.parsers.base import ParseResult


def test_text_parser_reads_markdown(tmp_path):
    md_file = tmp_path / "notes.md"
    md_file.write_text("# My Notes\n\nSome content here.")
    parser = TextParser()
    result = parser.parse(str(md_file))
    assert result.content == "# My Notes\n\nSome content here."
    assert result.title == "My Notes"
    assert result.source_type == "text"


def test_text_parser_plain_text(tmp_path):
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("Just plain text.")
    parser = TextParser()
    result = parser.parse(str(txt_file))
    assert result.content == "Just plain text."
    assert result.source_type == "text"


def test_detect_parser_url():
    parser = detect_parser("https://example.com/article")
    assert parser.__class__.__name__ == "WebParser"


def test_detect_parser_pdf(tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    parser = detect_parser(str(pdf))
    assert parser.__class__.__name__ == "PDFParser"


def test_detect_parser_markdown(tmp_path):
    md = tmp_path / "notes.md"
    md.write_text("# test")
    parser = detect_parser(str(md))
    assert parser.__class__.__name__ == "TextParser"


def test_parse_result_content_hash():
    result = ParseResult(content="hello", title="test", source_type="text")
    assert result.content_hash.startswith("sha256:")
    assert len(result.content_hash) > 10
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_parsers.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement base.py**

```python
# cli/src/wiki_cli/parsers/base.py
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParseResult:
    content: str
    title: str
    source_type: str
    source_path: str = ""

    @property
    def content_hash(self) -> str:
        h = hashlib.sha256(self.content.encode()).hexdigest()
        return f"sha256:{h}"
```

- [ ] **Step 4: Implement text.py**

```python
# cli/src/wiki_cli/parsers/text.py
import re
from pathlib import Path
from .base import ParseResult


class TextParser:
    def parse(self, source: str) -> ParseResult:
        path = Path(source)
        content = path.read_text(encoding="utf-8")
        # Extract title from first markdown heading if present
        title_match = re.match(r"^#\s+(.+)", content)
        title = title_match.group(1) if title_match else path.stem
        return ParseResult(
            content=content,
            title=title,
            source_type="text",
            source_path=str(path),
        )
```

- [ ] **Step 5: Implement web.py**

```python
# cli/src/wiki_cli/parsers/web.py
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify
from .base import ParseResult


class WebParser:
    def parse(self, url: str) -> ParseResult:
        response = httpx.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Remove nav, header, footer, script, style
        for tag in soup.find_all(["nav", "header", "footer", "script", "style", "aside"]):
            tag.decompose()

        # Find main content area
        main = soup.find("main") or soup.find("article") or soup.find("body")
        content = markdownify(str(main), heading_style="ATX", strip=["img"])

        return ParseResult(
            content=content.strip(),
            title=title,
            source_type="web",
            source_path=url,
        )
```

- [ ] **Step 6: Implement pdf.py**

```python
# cli/src/wiki_cli/parsers/pdf.py
from pathlib import Path
import pdfplumber
from .base import ParseResult


class PDFParser:
    def parse(self, source: str) -> ParseResult:
        path = Path(source)
        pages = []
        title = path.stem

        with pdfplumber.open(path) as pdf:
            # Try to get title from metadata
            if pdf.metadata and pdf.metadata.get("Title"):
                title = pdf.metadata["Title"]

            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)

        content = "\n\n---\n\n".join(pages)
        return ParseResult(
            content=content,
            title=title,
            source_type="pdf",
            source_path=str(path),
        )
```

- [ ] **Step 7: Implement parsers/__init__.py**

```python
# cli/src/wiki_cli/parsers/__init__.py
from pathlib import Path
from .base import ParseResult


def detect_parser(source: str):
    """Detect and return the appropriate parser for a source."""
    if source.startswith("http://") or source.startswith("https://"):
        from .web import WebParser
        return WebParser()

    path = Path(source)
    if path.suffix.lower() == ".pdf":
        from .pdf import PDFParser
        return PDFParser()

    from .text import TextParser
    return TextParser()
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `pytest tests/test_parsers.py -v`
Expected: All 6 tests PASS

- [ ] **Step 9: Commit**

```bash
git add cli/src/wiki_cli/parsers/ tests/test_parsers.py
git commit -m "feat: source parsers for web, PDF, and text/markdown"
```

---

### Task 5: Wiki Manager (Core Wiki Operations)

**Files:**
- Create: `cli/src/wiki_cli/wiki_manager.py`
- Create: `tests/test_wiki_manager.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_wiki_manager.py
import pytest
import subprocess
from pathlib import Path
from wiki_cli.wiki_manager import WikiManager


@pytest.fixture
def wiki_mgr(tmp_vault):
    # Init git in tmp_vault for commit tests
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_wiki_manager.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement wiki_manager.py**

```python
# cli/src/wiki_cli/wiki_manager.py
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class WikiManager:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.wiki_dir = vault_path / "wiki"

    def read_page(self, page_path: str) -> str | None:
        """Read a wiki page. page_path is relative to wiki/, without .md extension."""
        full_path = self.wiki_dir / f"{page_path}.md"
        if not full_path.exists():
            return None
        return full_path.read_text(encoding="utf-8")

    def write_page(self, page_path: str, content: str) -> Path:
        """Write content to a wiki page. Creates parent directories if needed."""
        full_path = self.wiki_dir / f"{page_path}.md"
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return full_path

    def update_index(self, page_path: str, title: str, category: str) -> None:
        """Add an entry to index.md under the given category."""
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
        """Append an entry to log.md."""
        log_path = self.wiki_dir / "log.md"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry = f'\n## [{now}] {operation} | "{title}"\n'
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def list_pages(self, subdirectory: str = "") -> list[str]:
        """List all wiki pages, optionally filtered by subdirectory. Returns paths relative to wiki/."""
        search_dir = self.wiki_dir / subdirectory if subdirectory else self.wiki_dir
        pages = []
        for md_file in search_dir.rglob("*.md"):
            rel = md_file.relative_to(self.wiki_dir)
            page_path = str(rel.with_suffix(""))
            if page_path not in ("index", "log"):
                pages.append(page_path)
        return sorted(pages)

    def find_pages_mentioning(self, term: str) -> list[str]:
        """Find all wiki pages that contain a [[wikilink]] or plain mention of the term."""
        results = []
        for md_file in self.wiki_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            if f"[[{term}]]" in content or f"[[{term}|" in content:
                rel = md_file.relative_to(self.wiki_dir)
                results.append(str(rel.with_suffix("")))
        return sorted(results)

    def commit(self, message: str) -> None:
        """Stage all changes in the vault and commit."""
        subprocess.run(["git", "add", "-A"], cwd=self.vault_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.vault_path,
            capture_output=True,
            check=True,
        )

    def get_all_page_summaries(self) -> list[dict]:
        """Get frontmatter + first heading of all wiki pages for search."""
        summaries = []
        for page_path in self.list_pages():
            content = self.read_page(page_path)
            if not content:
                continue
            # Extract frontmatter tags
            tags = []
            tag_match = re.search(r"tags:\s*\[([^\]]*)\]", content)
            if tag_match:
                tags = [t.strip() for t in tag_match.group(1).split(",")]
            # Extract first heading
            heading_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
            heading = heading_match.group(1) if heading_match else page_path
            summaries.append({
                "path": page_path,
                "title": heading,
                "tags": tags,
                "content": content,
            })
        return summaries
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_wiki_manager.py -v`
Expected: All 8 tests PASS

- [ ] **Step 5: Commit**

```bash
git add cli/src/wiki_cli/wiki_manager.py tests/test_wiki_manager.py
git commit -m "feat: wiki manager with page CRUD, index/log updates, and git commits"
```

---

### Task 6: Schema & Templates

**Files:**
- Create: `schema/SCHEMA.md`
- Create: `schema/templates/entity.md`
- Create: `schema/templates/concept.md`
- Create: `schema/templates/source-summary.md`
- Create: `schema/templates/comparison.md`

- [ ] **Step 1: Create SCHEMA.md**

```markdown
# Wiki Schema

## Purpose

This file instructs the LLM on how to maintain this knowledge base. Read this before performing any wiki operation.

## Conventions

- All wiki pages use Obsidian-compatible markdown with YAML frontmatter
- Cross-references use `[[wikilinks]]` syntax: `[[page-name]]` or `[[path/page-name|Display Text]]`
- Every page has frontmatter with at minimum: `title`, `tags`, `created_at`, `publish`
- File names use lowercase kebab-case: `distributed-consensus.md`, `andrej-karpathy.md`
- Tags use lowercase with hyphens: `machine-learning`, `distributed-systems`

## Page Types

### Entity (`wiki/entities/`)
People, tools, companies, projects, frameworks. One page per distinct entity.
Template: `schema/templates/entity.md`

### Concept (`wiki/concepts/`)
Ideas, patterns, mental models, principles. Abstract knowledge.
Template: `schema/templates/concept.md`

### Topic (`wiki/topics/`)
Broad domain areas that group entities and concepts. E.g., `machine-learning`, `personal-finance`.
Created as needed when multiple entities/concepts cluster around a domain.

### Source Summary (`wiki/topics/` or contextually appropriate directory)
Summary of an ingested source with key takeaways. Links to entities and concepts mentioned.
Template: `schema/templates/source-summary.md`

### Synthesis (`wiki/syntheses/`)
Comparisons, analyses, and cross-cutting insights that connect multiple entities or concepts.
Template: `schema/templates/comparison.md`

### Exploration (`wiki/explorations/`)
Saved query answers — synthesized responses to questions asked of the wiki.

## Ingest Instructions

When ingesting a new source:
1. Identify all entities (people, tools, projects) and concepts (ideas, patterns) mentioned
2. For each entity/concept, create a new page or update the existing one
3. Add `[[wikilinks]]` between related pages
4. Create a source summary page with key takeaways
5. Update `wiki/index.md` with new entries
6. Update `wiki/log.md` with the operation record

## Update Instructions

When updating an existing page with new information:
- Preserve all existing content
- Add new facts in the appropriate section
- If new information contradicts existing content, add a warning callout:
  `> [!warning] Contradiction: [description]`
- Do not duplicate existing information
- Update the `updated_at` field in frontmatter
```

- [ ] **Step 2: Create entity template**

```markdown
---
title: "{{title}}"
type: entity
category: "{{category}}"
tags: []
created_at: "{{date}}"
updated_at: "{{date}}"
publish: true
---

# {{title}}

## Overview

{{overview}}

## Key Details

{{details}}

## Related

{{related_links}}
```

- [ ] **Step 3: Create concept template**

```markdown
---
title: "{{title}}"
type: concept
tags: []
created_at: "{{date}}"
updated_at: "{{date}}"
publish: true
---

# {{title}}

## Definition

{{definition}}

## Key Principles

{{principles}}

## Examples

{{examples}}

## Related

{{related_links}}
```

- [ ] **Step 4: Create source-summary template**

```markdown
---
title: "{{title}}"
type: source-summary
source_url: "{{source_url}}"
source_type: "{{source_type}}"
ingested_at: "{{date}}"
content_hash: "{{content_hash}}"
tags: []
publish: true
---

# {{title}}

## Key Takeaways

{{takeaways}}

## Summary

{{summary}}

## Entities & Concepts Mentioned

{{entities_and_concepts}}

## Source

- URL: {{source_url}}
- Type: {{source_type}}
- Ingested: {{date}}
```

- [ ] **Step 5: Create comparison template**

```markdown
---
title: "{{title}}"
type: comparison
tags: []
created_at: "{{date}}"
updated_at: "{{date}}"
publish: true
---

# {{title}}

## Overview

{{overview}}

## Comparison

{{comparison_table_or_analysis}}

## Key Differences

{{differences}}

## When to Use Which

{{recommendations}}

## Related

{{related_links}}
```

- [ ] **Step 6: Commit**

```bash
git add schema/
git commit -m "feat: wiki schema and page templates"
```

---

### Task 7: Init Command

**Files:**
- Create: `cli/src/wiki_cli/commands/__init__.py`
- Create: `cli/src/wiki_cli/commands/init_cmd.py`
- Create: `tests/test_init_cmd.py`
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_init_cmd.py
import pytest
from pathlib import Path
from wiki_cli.commands.init_cmd import run_init


def test_init_creates_directory_structure(tmp_path):
    run_init(tmp_path)
    assert (tmp_path / "schema/SCHEMA.md").exists()
    assert (tmp_path / "schema/templates/entity.md").exists()
    assert (tmp_path / "schema/templates/concept.md").exists()
    assert (tmp_path / "schema/templates/source-summary.md").exists()
    assert (tmp_path / "schema/templates/comparison.md").exists()
    assert (tmp_path / "sources/raw").is_dir()
    assert (tmp_path / "sources/references").is_dir()
    assert (tmp_path / "sources/inbox").is_dir()
    assert (tmp_path / "wiki/index.md").exists()
    assert (tmp_path / "wiki/log.md").exists()
    assert (tmp_path / "wiki/entities").is_dir()
    assert (tmp_path / "wiki/concepts").is_dir()
    assert (tmp_path / "wiki/topics").is_dir()
    assert (tmp_path / "wiki/syntheses").is_dir()
    assert (tmp_path / "wiki/explorations").is_dir()


def test_init_creates_config_files(tmp_path):
    run_init(tmp_path)
    assert (tmp_path / "wiki.yaml").exists()
    assert (tmp_path / ".env.example").exists()
    assert (tmp_path / ".gitignore").exists()


def test_init_gitignore_contents(tmp_path):
    run_init(tmp_path)
    gitignore = (tmp_path / ".gitignore").read_text()
    assert ".env" in gitignore
    assert "public/" in gitignore
    assert ".obsidian/workspace.json" in gitignore


def test_init_does_not_overwrite_existing(tmp_path):
    (tmp_path / "wiki.yaml").write_text("existing: true")
    run_init(tmp_path)
    assert "existing: true" in (tmp_path / "wiki.yaml").read_text()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_init_cmd.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement init_cmd.py**

```python
# cli/src/wiki_cli/commands/init_cmd.py
import shutil
from pathlib import Path

import typer

# Default content for generated files
DEFAULT_WIKI_YAML = """\
provider: ollama  # claude | openai | ollama

claude:
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-sonnet-4-20250514

openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o

ollama:
  model: llama3.1
  base_url: http://localhost:11434

vault_path: .
stale_threshold_days: 30
auto_commit: true
"""

DEFAULT_ENV_EXAMPLE = """\
# LLM Provider API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
"""

DEFAULT_GITIGNORE = """\
.env
public/
.obsidian/workspace.json
.obsidian/workspace-mobile.json
__pycache__/
*.pyc
.venv/
"""

DEFAULT_INDEX = """\
# Knowledge Base Index

A catalog of all wiki content, organized by category.
"""

DEFAULT_LOG = """\
# Activity Log

Chronological record of all wiki operations.
"""


def _write_if_not_exists(path: Path, content: str) -> bool:
    """Write content to path only if it doesn't already exist. Returns True if written."""
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def run_init(vault_path: Path) -> None:
    """Initialize a new knowledge base at the given path."""
    vault_path = vault_path.resolve()

    # Create directory structure
    dirs = [
        "schema/templates",
        "sources/raw",
        "sources/references",
        "sources/inbox",
        "wiki/entities",
        "wiki/concepts",
        "wiki/topics",
        "wiki/syntheses",
        "wiki/explorations",
    ]
    for d in dirs:
        (vault_path / d).mkdir(parents=True, exist_ok=True)

    # Copy schema templates from package
    templates_src = Path(__file__).parent.parent.parent.parent.parent / "schema" / "templates"
    schema_src = Path(__file__).parent.parent.parent.parent.parent / "schema" / "SCHEMA.md"

    if schema_src.exists():
        _write_if_not_exists(vault_path / "schema" / "SCHEMA.md", schema_src.read_text())
    if templates_src.exists():
        for tmpl in templates_src.glob("*.md"):
            _write_if_not_exists(vault_path / "schema" / "templates" / tmpl.name, tmpl.read_text())

    # Create config files
    _write_if_not_exists(vault_path / "wiki.yaml", DEFAULT_WIKI_YAML)
    _write_if_not_exists(vault_path / ".env.example", DEFAULT_ENV_EXAMPLE)
    _write_if_not_exists(vault_path / ".gitignore", DEFAULT_GITIGNORE)

    # Create wiki index and log
    _write_if_not_exists(vault_path / "wiki" / "index.md", DEFAULT_INDEX)
    _write_if_not_exists(vault_path / "wiki" / "log.md", DEFAULT_LOG)

    # Add .gitkeep to empty directories
    for d in ["sources/raw", "sources/references", "sources/inbox",
              "wiki/entities", "wiki/concepts", "wiki/topics",
              "wiki/syntheses", "wiki/explorations"]:
        gitkeep = vault_path / d / ".gitkeep"
        if not any((vault_path / d).iterdir()):
            gitkeep.touch()

    typer.echo(f"Knowledge base initialized at {vault_path}")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo("  1. Copy .env.example to .env and add your API keys")
    typer.echo("  2. Edit wiki.yaml to set your preferred provider")
    typer.echo("  3. Open this directory in Obsidian as a vault")
    typer.echo("  4. Run 'wiki ingest <url>' to add your first source")
```

- [ ] **Step 4: Create commands/__init__.py**

```python
# cli/src/wiki_cli/commands/__init__.py
```

- [ ] **Step 5: Wire init command into main.py**

Update `main.py` to replace the placeholder `init` command:

```python
# Replace the init function in main.py
@app.command()
def init(
    path: str = typer.Argument(".", help="Path to initialize the knowledge base"),
):
    """Initialize a new knowledge base."""
    from wiki_cli.commands.init_cmd import run_init
    run_init(Path(path))
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_init_cmd.py -v`
Expected: All 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add cli/src/wiki_cli/commands/ cli/src/wiki_cli/main.py tests/test_init_cmd.py
git commit -m "feat: wiki init command to bootstrap knowledge base"
```

---

### Task 8: Ingest Command

**Files:**
- Create: `cli/src/wiki_cli/commands/ingest.py`
- Create: `tests/test_ingest.py`
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_ingest.py
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
    # Mock the summarize + extract response as JSON
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
    # Mock the page generation response
    provider.complete_with_context.return_value = "---\ntitle: Python\ntype: entity\ntags: [python]\ncreated_at: 2026-06-05\npublish: true\n---\n# Python\n\nA programming language."
    return provider


@pytest.fixture
def ingest_pipeline(tmp_vault, mock_provider):
    subprocess.run(["git", "init"], cwd=tmp_vault, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_vault, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_vault, capture_output=True)
    # Create schema templates dir
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
    # Source should be copied to raw/
    raw_files = list((tmp_vault / "sources" / "raw").glob("*.md"))
    assert len(raw_files) >= 1
    # Index should be updated
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
    # Inbox should be empty after processing
    remaining = list((tmp_vault / "sources" / "inbox").glob("*.md"))
    assert len(remaining) == 0


def test_ingest_atomic_failure(ingest_pipeline, tmp_vault):
    """If pipeline fails, no files should be written."""
    ingest_pipeline.provider.complete.side_effect = Exception("LLM error")
    source_file = tmp_vault / "bad-article.md"
    source_file.write_text("# Bad Article\nContent.")

    result = ingest_pipeline.run(str(source_file))

    assert not result.success
    assert result.error == "LLM error"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ingest.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement ingest.py**

```python
# cli/src/wiki_cli/commands/ingest.py
import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import typer

from wiki_cli.parsers import detect_parser
from wiki_cli.parsers.base import ParseResult
from wiki_cli.providers.base import LLMProvider
from wiki_cli.utils import slugify
from wiki_cli.wiki_manager import WikiManager


@dataclass
class IngestResult:
    success: bool
    title: str = ""
    pages_created: int = 0
    pages_updated: int = 0
    error: str = ""


INGEST_SYSTEM_PROMPT = """You are a knowledge base assistant. Given a source document, extract structured information.

Return a JSON object with:
- "title": concise title for this source
- "summary": 2-3 paragraph summary of the content
- "takeaways": list of 3-5 key takeaways
- "entities": list of objects {"name": str, "category": str, "description": str} for people, tools, companies, projects mentioned
- "concepts": list of objects {"name": str, "description": str} for ideas, patterns, mental models discussed
- "tags": list of lowercase hyphenated tags

Return ONLY valid JSON, no markdown fencing."""

PAGE_UPDATE_SYSTEM_PROMPT = """You are a knowledge base assistant. You will receive an existing wiki page and new information about the same topic.

Merge the new information into the existing page:
- Preserve all existing content
- Add new facts in the appropriate sections
- If new info contradicts existing content, add: > [!warning] Contradiction: [description]
- Do not duplicate existing information
- Maintain the existing page structure and frontmatter format
- Update the updated_at field to today's date

Return the complete updated page content."""


class IngestPipeline:
    def __init__(self, wiki_mgr: WikiManager, provider: LLMProvider, vault_path: Path):
        self.wiki_mgr = wiki_mgr
        self.provider = provider
        self.vault_path = vault_path

    def run(self, source: str) -> IngestResult:
        """Run the full ingest pipeline for a single source."""
        try:
            # Step 1: Parse
            parser = detect_parser(source)
            parsed = parser.parse(source)

            # Step 2-3: Summarize + extract entities/concepts via LLM
            extraction = self._extract(parsed)

            # Collect all file operations in memory before writing
            file_ops: list[tuple[Path, str]] = []
            pages_created = 0
            pages_updated = 0

            # Step 4: Create/update entity and concept pages
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

            for entity in extraction.get("entities", []):
                slug = slugify(entity["name"])
                page_path = f"entities/{slug}"
                existing = self.wiki_mgr.read_page(page_path)
                if existing:
                    updated = self._update_page(existing, entity["description"])
                    file_ops.append((self.wiki_mgr.wiki_dir / f"{page_path}.md", updated))
                    pages_updated += 1
                else:
                    content = f'---\ntitle: "{entity["name"]}"\ntype: entity\ncategory: "{entity.get("category", "")}"\ntags: {json.dumps(extraction.get("tags", []))}\ncreated_at: "{now}"\nupdated_at: "{now}"\npublish: true\n---\n\n# {entity["name"]}\n\n## Overview\n\n{entity["description"]}\n\n## Related\n\n'
                    file_ops.append((self.wiki_mgr.wiki_dir / f"{page_path}.md", content))
                    pages_created += 1

            for concept in extraction.get("concepts", []):
                slug = slugify(concept["name"])
                page_path = f"concepts/{slug}"
                existing = self.wiki_mgr.read_page(page_path)
                if existing:
                    updated = self._update_page(existing, concept["description"])
                    file_ops.append((self.wiki_mgr.wiki_dir / f"{page_path}.md", updated))
                    pages_updated += 1
                else:
                    content = f'---\ntitle: "{concept["name"]}"\ntype: concept\ntags: {json.dumps(extraction.get("tags", []))}\ncreated_at: "{now}"\nupdated_at: "{now}"\npublish: true\n---\n\n# {concept["name"]}\n\n## Definition\n\n{concept["description"]}\n\n## Related\n\n'
                    file_ops.append((self.wiki_mgr.wiki_dir / f"{page_path}.md", content))
                    pages_created += 1

            # Source summary page
            summary_slug = slugify(extraction.get("title", parsed.title))
            summary_path = f"topics/{summary_slug}"
            summary_content = f'---\ntitle: "{extraction.get("title", parsed.title)}"\ntype: source-summary\nsource_url: "{parsed.source_path}"\nsource_type: "{parsed.source_type}"\ningested_at: "{now}"\ncontent_hash: "{parsed.content_hash}"\ntags: {json.dumps(extraction.get("tags", []))}\npublish: true\n---\n\n# {extraction.get("title", parsed.title)}\n\n## Key Takeaways\n\n'
            for t in extraction.get("takeaways", []):
                summary_content += f"- {t}\n"
            summary_content += f'\n## Summary\n\n{extraction.get("summary", "")}\n\n## Entities & Concepts Mentioned\n\n'
            all_mentions = [e["name"] for e in extraction.get("entities", [])] + [c["name"] for c in extraction.get("concepts", [])]
            for m in all_mentions:
                summary_content += f"- [[{slugify(m)}|{m}]]\n"
            file_ops.append((self.wiki_mgr.wiki_dir / f"{summary_path}.md", summary_content))
            pages_created += 1

            # Step 5: Write all files atomically
            for path, content in file_ops:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            # Copy raw source
            raw_dest = self.vault_path / "sources" / "raw" / f"{summary_slug}{Path(source).suffix or '.md'}"
            raw_dest.parent.mkdir(parents=True, exist_ok=True)
            if parsed.source_type == "web":
                raw_dest.write_text(parsed.content, encoding="utf-8")
            elif Path(source).exists():
                shutil.copy2(source, raw_dest)

            # Step 6-7: Update index and log
            title = extraction.get("title", parsed.title)
            for entity in extraction.get("entities", []):
                self.wiki_mgr.update_index(f"entities/{slugify(entity['name'])}", entity["name"], "entities")
            for concept in extraction.get("concepts", []):
                self.wiki_mgr.update_index(f"concepts/{slugify(concept['name'])}", concept["name"], "concepts")
            self.wiki_mgr.update_index(summary_path, title, "topics")
            self.wiki_mgr.append_log("ingest", title)

            # Step 8: Commit
            self.wiki_mgr.commit(f'ingest: "{title}" (+{pages_created} pages, ~{pages_updated} updated)')

            return IngestResult(
                success=True,
                title=title,
                pages_created=pages_created,
                pages_updated=pages_updated,
            )

        except Exception as e:
            return IngestResult(success=False, error=str(e))

    def run_reference(self, url: str, description: str = "") -> IngestResult:
        """Save a reference-only entry (no raw source stored)."""
        try:
            slug = slugify(url.rstrip("/").split("/")[-1])
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            content = f'---\ntitle: "{slug}"\nsource_url: "{url}"\nsource_type: reference\ningested_at: "{now}"\npublish: true\n---\n\n# {slug}\n\n{description or url}\n'
            ref_path = self.vault_path / "sources" / "references" / f"{slug}.md"
            ref_path.parent.mkdir(parents=True, exist_ok=True)
            ref_path.write_text(content, encoding="utf-8")
            self.wiki_mgr.append_log("reference", slug)
            self.wiki_mgr.commit(f'reference: "{slug}"')
            return IngestResult(success=True, title=slug, pages_created=1)
        except Exception as e:
            return IngestResult(success=False, error=str(e))

    def run_inbox(self) -> list[IngestResult]:
        """Process all files in the inbox."""
        inbox = self.vault_path / "sources" / "inbox"
        results = []
        for item in sorted(inbox.iterdir()):
            if item.name.startswith("."):
                continue
            result = self.run(str(item))
            results.append(result)
            if result.success:
                item.unlink()
        return results

    def _extract(self, parsed: ParseResult) -> dict:
        """Use LLM to extract structured information from parsed content."""
        response = self.provider.complete(INGEST_SYSTEM_PROMPT, parsed.content)
        return json.loads(response)

    def _update_page(self, existing_content: str, new_info: str) -> str:
        """Use LLM to merge new information into an existing page."""
        prompt = f"## Existing Page\n\n{existing_content}\n\n## New Information\n\n{new_info}"
        return self.provider.complete_with_context(
            PAGE_UPDATE_SYSTEM_PROMPT, [], prompt
        )
```

- [ ] **Step 4: Wire ingest command into main.py**

Update the `ingest` function in `main.py`:

```python


@app.command()
def ingest(
    source: str = typer.Argument(None, help="URL, file path, or --inbox to process inbox"),
    inbox: bool = typer.Option(False, "--inbox", help="Process all files in sources/inbox/"),
    ref: bool = typer.Option(False, "--ref", help="Save as reference only (no raw source)"),
):
    """Ingest a source into the knowledge base."""
    from wiki_cli.commands.ingest import IngestPipeline
    from wiki_cli.config import load_config
    from wiki_cli.providers import get_provider

    config = load_config(Path("wiki.yaml"))
    provider = get_provider(config.provider, config.provider_config)
    wiki_mgr = WikiManager(config.vault_path)
    pipeline = IngestPipeline(wiki_mgr, provider, config.vault_path)

    if inbox:
        results = pipeline.run_inbox()
        succeeded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        typer.echo(f"Inbox processed: {succeeded} succeeded, {failed} failed")
        for r in results:
            if not r.success:
                typer.echo(f"  FAILED: {r.error}", err=True)
    elif ref:
        if not source:
            typer.echo("Error: source URL required with --ref", err=True)
            raise typer.Exit(1)
        result = pipeline.run_reference(source)
        if result.success:
            typer.echo(f"Reference saved: {result.title}")
        else:
            typer.echo(f"Error: {result.error}", err=True)
    else:
        if not source:
            typer.echo("Error: source required (URL, file path, or use --inbox)", err=True)
            raise typer.Exit(1)
        result = pipeline.run(source)
        if result.success:
            typer.echo(f'Ingested: "{result.title}" (+{result.pages_created} pages, ~{result.pages_updated} updated)')
        else:
            typer.echo(f"Error: {result.error}", err=True)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_ingest.py -v`
Expected: All 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add cli/src/wiki_cli/commands/ingest.py cli/src/wiki_cli/main.py tests/test_ingest.py
git commit -m "feat: ingest command with parse, extract, page creation, and atomic commits"
```

---

### Task 9: Query Command

**Files:**
- Create: `cli/src/wiki_cli/commands/query.py`
- Create: `tests/test_query.py`
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_query.py
import pytest
from unittest.mock import AsyncMock
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
    provider = AsyncMock()
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
    # Provider should have been called with context containing Python page
    call_args = mock_provider.complete_with_context.call_args
    context = call_args[0][1]  # second positional arg
    assert any("Python" in c for c in context)



def test_query_save(query_engine, populated_vault):
    answer = query_engine.ask("What is Python?", save=True)
    explorations = list((populated_vault / "wiki/explorations").glob("*.md"))
    assert len(explorations) == 1
    content = explorations[0].read_text()
    assert "Python" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_query.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement query.py**

```python
# cli/src/wiki_cli/commands/query.py
from datetime import datetime, timezone

from wiki_cli.providers.base import LLMProvider
from wiki_cli.utils import slugify
from wiki_cli.wiki_manager import WikiManager

QUERY_SYSTEM_PROMPT = """You are a knowledgeable assistant answering questions from a personal knowledge base.

You will receive relevant wiki pages as context. Answer the question using ONLY the information in the provided context.
- Cite sources using [[wikilinks]] syntax: [[page-path|display name]]
- If the context doesn't contain enough information, say so clearly
- Be concise and direct"""


class QueryEngine:
    def __init__(self, wiki_mgr: WikiManager, provider: LLMProvider):
        self.wiki_mgr = wiki_mgr
        self.provider = provider

    def ask(self, question: str, save: bool = False) -> str:
        """Search the wiki and synthesize an answer."""
        # Step 1: Search for relevant pages
        relevant = self._search(question)

        # Step 2: Gather context
        context = []
        for page_info in relevant[:10]:
            content = page_info["content"]
            context.append(f"# Source: {page_info['path']}\n\n{content}")

        # Step 3: Synthesize
        answer = self.provider.complete_with_context(
            QUERY_SYSTEM_PROMPT, context, question
        )

        # Step 4: Optionally save
        if save:
            self._save_exploration(question, answer)

        return answer

    def _search(self, question: str) -> list[dict]:
        """Simple keyword search over wiki pages. Returns relevant page summaries sorted by relevance."""
        all_pages = self.wiki_mgr.get_all_page_summaries()
        question_words = set(question.lower().split())

        scored = []
        for page in all_pages:
            # Score based on keyword overlap with title, tags, and content
            page_text = f"{page['title']} {' '.join(page['tags'])} {page['content']}".lower()
            score = sum(1 for w in question_words if w in page_text)
            if score > 0:
                scored.append((score, page))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [page for _, page in scored]

    def _save_exploration(self, question: str, answer: str) -> None:
        """Save a query answer as an exploration page."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        slug = slugify(question)
        page_path = f"explorations/{slug}"

        content = f'---\ntitle: "{question}"\ntype: exploration\ncreated_at: "{now}"\ntags: []\npublish: true\n---\n\n# {question}\n\n{answer}\n'
        self.wiki_mgr.write_page(page_path, content)
        self.wiki_mgr.update_index(page_path, question, "explorations")
        self.wiki_mgr.append_log("explore", question)
```

- [ ] **Step 4: Wire query command into main.py**

Update the `query` function in `main.py`:

```python
@app.command()
def query(
    question: str = typer.Argument(None, help="Question to ask the knowledge base"),
    save: bool = typer.Option(False, "--save", help="Save the answer as an exploration"),
    interactive: bool = typer.Option(False, "-i", help="Interactive query mode"),
):
    """Query the knowledge base."""
    from wiki_cli.commands.query import QueryEngine
    from wiki_cli.config import load_config
    from wiki_cli.providers import get_provider

    config = load_config(Path("wiki.yaml"))
    provider = get_provider(config.provider, config.provider_config)
    wiki_mgr = WikiManager(config.vault_path)
    engine = QueryEngine(wiki_mgr, provider)

    if interactive:
        typer.echo("Interactive mode. Type /save to save last answer, /quit to exit.")
        last_answer = ""
        while True:
            q = typer.prompt("wiki")
            if q == "/quit":
                break
            if q == "/save" and last_answer:
                engine._save_exploration("interactive-query", last_answer)
                typer.echo("Saved to explorations.")
                continue
            last_answer = engine.ask(q)
            typer.echo(f"\n{last_answer}\n")
    else:
        if not question:
            typer.echo("Error: question required (or use -i for interactive mode)", err=True)
            raise typer.Exit(1)
        answer = engine.ask(question, save=save)
        typer.echo(answer)
        if save:
            typer.echo("\n(Answer saved to explorations)")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_query.py -v`
Expected: All 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add cli/src/wiki_cli/commands/query.py cli/src/wiki_cli/main.py tests/test_query.py
git commit -m "feat: query command with keyword search, LLM synthesis, and save-to-explorations"
```

---

### Task 10: Lint Command

**Files:**
- Create: `cli/src/wiki_cli/commands/lint.py`
- Create: `tests/test_lint.py`
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_lint.py
import pytest
from wiki_cli.commands.lint import WikiLinter
from wiki_cli.wiki_manager import WikiManager


@pytest.fixture
def wiki_linter(tmp_vault):
    wiki_mgr = WikiManager(tmp_vault)
    return WikiLinter(wiki_mgr)


def test_find_broken_links(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text(
        "# Python\nSee [[nonexistent-page]] and [[entities/also-missing]]"
    )
    issues = wiki_linter.check_broken_links()
    assert len(issues) >= 1
    assert any("nonexistent-page" in i["detail"] for i in issues)


def test_find_orphan_pages(wiki_linter, tmp_vault):
    (tmp_vault / "wiki/entities/python.md").write_text("# Python\nNo links to this.")
    (tmp_vault / "wiki/entities/rust.md").write_text("# Rust\nSee [[entities/python]]")
    issues = wiki_linter.check_orphan_pages()
    # Rust should be orphan (nothing links to it), Python is linked from Rust
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_lint.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement lint.py**

```python
# cli/src/wiki_cli/commands/lint.py
import re
from pathlib import Path

from wiki_cli.wiki_manager import WikiManager


class WikiLinter:
    def __init__(self, wiki_mgr: WikiManager):
        self.wiki_mgr = wiki_mgr

    def check_broken_links(self) -> list[dict]:
        """Find [[wikilinks]] that point to nonexistent pages."""
        issues = []
        all_pages = set(self.wiki_mgr.list_pages())

        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            # Find all [[wikilinks]]
            links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)
            for link in links:
                # Normalize: try link as-is and with common prefixes
                if link not in all_pages and not any(
                    f"{prefix}/{link}" in all_pages
                    for prefix in ["entities", "concepts", "topics", "syntheses", "explorations"]
                ):
                    issues.append({
                        "check": "broken_link",
                        "page": page_path,
                        "detail": f"Broken link: [[{link}]]",
                    })
        return issues

    def check_orphan_pages(self) -> list[dict]:
        """Find pages with no incoming backlinks."""
        all_pages = self.wiki_mgr.list_pages()
        linked_to = set()

        for page_path in all_pages:
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)
            for link in links:
                linked_to.add(link)
                # Also check with prefixes stripped/added
                for prefix in ["entities", "concepts", "topics", "syntheses", "explorations"]:
                    if link.startswith(f"{prefix}/"):
                        linked_to.add(link)
                    else:
                        linked_to.add(f"{prefix}/{link}")

        issues = []
        for page_path in all_pages:
            if page_path not in linked_to:
                issues.append({
                    "check": "orphan_page",
                    "page": page_path,
                    "detail": f"Orphan page: no incoming links",
                })
        return issues

    def check_missing_frontmatter(self) -> list[dict]:
        """Find pages without YAML frontmatter."""
        issues = []
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content or not content.startswith("---"):
                issues.append({
                    "check": "missing_frontmatter",
                    "page": page_path,
                    "detail": "Missing YAML frontmatter",
                })
        return issues

    def check_index_drift(self) -> list[dict]:
        """Find pages that exist but aren't listed in index.md."""
        issues = []
        index_content = self.wiki_mgr.read_page("index") or ""
        for page_path in self.wiki_mgr.list_pages():
            if page_path not in index_content:
                issues.append({
                    "check": "index_drift",
                    "page": page_path,
                    "detail": "Page not listed in index.md",
                })
        return issues

    def check_empty_sections(self) -> list[dict]:
        """Find pages with heading-only sections (no content under heading)."""
        issues = []
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("## "):
                    # Check if next non-empty line is another heading or end of file
                    remaining = [l.strip() for l in lines[i + 1:] if l.strip()]
                    if not remaining or (remaining and remaining[0].startswith("#")):
                        issues.append({
                            "check": "empty_section",
                            "page": page_path,
                            "detail": f"Empty section: {line.strip()}",
                        })
        return issues

    def run_all(self) -> dict:
        """Run all structural lint checks and return a report."""
        all_issues = []
        all_issues.extend(self.check_broken_links())
        all_issues.extend(self.check_orphan_pages())
        all_issues.extend(self.check_missing_frontmatter())
        all_issues.extend(self.check_index_drift())
        all_issues.extend(self.check_empty_sections())

        return {
            "total_issues": len(all_issues),
            "issues": all_issues,
            "by_check": {
                check: [i for i in all_issues if i["check"] == check]
                for check in set(i["check"] for i in all_issues)
            },
        }
```

- [ ] **Step 4: Wire lint command into main.py**

Update the `lint` function in `main.py`:

```python
@app.command()
def lint(
    fix: bool = typer.Option(False, "--fix", help="Auto-fix repairable issues"),
    deep: bool = typer.Option(False, "--deep", help="LLM-powered deep analysis"),
):
    """Run health checks on the wiki."""
    from wiki_cli.commands.lint import WikiLinter
    from wiki_cli.config import load_config

    config = load_config(Path("wiki.yaml"))
    wiki_mgr = WikiManager(config.vault_path)
    linter = WikiLinter(wiki_mgr)

    report = linter.run_all()
    total = report["total_issues"]
    pages = len(wiki_mgr.list_pages())

    typer.echo(f"Wiki Health Report")
    typer.echo(f"==================")
    typer.echo(f"{pages} pages scanned\n")

    if total == 0:
        typer.echo("All checks passed!")
    else:
        for check_name, issues in report["by_check"].items():
            symbol = "x" if issues else "v"
            typer.echo(f"  [{symbol}] {check_name}: {len(issues)} issues")
            for issue in issues[:5]:
                typer.echo(f"      - {issue['page']}: {issue['detail']}")
            if len(issues) > 5:
                typer.echo(f"      ... and {len(issues) - 5} more")

    typer.echo(f"\nTotal: {total} issues found")

    if deep:
        typer.echo("\n--deep mode not yet implemented (requires LLM)")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_lint.py -v`
Expected: All 5 tests PASS

- [ ] **Step 6: Commit**

```bash
git add cli/src/wiki_cli/commands/lint.py cli/src/wiki_cli/main.py tests/test_lint.py
git commit -m "feat: lint command with structural checks for broken links, orphans, frontmatter, index drift"
```

---

### Task 11: Reingest Command

**Files:**
- Create: `cli/src/wiki_cli/commands/reingest.py`
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Implement reingest.py**

```python
# cli/src/wiki_cli/commands/reingest.py
import re
from pathlib import Path

from wiki_cli.commands.ingest import IngestPipeline, IngestResult
from wiki_cli.parsers import detect_parser
from wiki_cli.providers.base import LLMProvider
from wiki_cli.wiki_manager import WikiManager


class ReingestPipeline:
    def __init__(self, wiki_mgr: WikiManager, provider: LLMProvider, vault_path: Path):
        self.wiki_mgr = wiki_mgr
        self.provider = provider
        self.vault_path = vault_path
        self.ingest = IngestPipeline(wiki_mgr, provider, vault_path)

    def run(self, source: str) -> IngestResult:
        """Re-fetch a source and update wiki if content has changed."""
        try:
            # Parse the source fresh
            parser = detect_parser(source)
            parsed = parser.parse(source)
            new_hash = parsed.content_hash

            # Find existing source summary page by source_url
            old_hash = self._find_existing_hash(source)

            if old_hash and old_hash == new_hash:
                return IngestResult(success=True, title="(unchanged)")

            # Content changed or new — run full ingest
            return self.ingest.run(source)

        except Exception as e:
            return IngestResult(success=False, error=str(e))

    def _find_existing_hash(self, source: str) -> str | None:
        """Find the content_hash of a previously ingested source."""
        for page_path in self.wiki_mgr.list_pages():
            content = self.wiki_mgr.read_page(page_path)
            if not content:
                continue
            if source in content:
                hash_match = re.search(r'content_hash:\s*"?(sha256:[a-f0-9]+)"?', content)
                if hash_match:
                    return hash_match.group(1)
        return None
```

- [ ] **Step 2: Wire reingest command into main.py**

```python
@app.command()
def reingest(
    source: str = typer.Argument(..., help="URL or file path to re-ingest"),
):
    """Re-fetch and update a previously ingested source."""
    from wiki_cli.commands.reingest import ReingestPipeline
    from wiki_cli.config import load_config
    from wiki_cli.providers import get_provider

    config = load_config(Path("wiki.yaml"))
    provider = get_provider(config.provider, config.provider_config)
    wiki_mgr = WikiManager(config.vault_path)
    pipeline = ReingestPipeline(wiki_mgr, provider, config.vault_path)

    result = pipeline.run(source)
    if result.success:
        if result.title == "(unchanged)":
            typer.echo("No changes detected. Skipping.")
        else:
            typer.echo(f'Re-ingested: "{result.title}" (+{result.pages_created}, ~{result.pages_updated} updated)')
    else:
        typer.echo(f"Error: {result.error}", err=True)
```

- [ ] **Step 3: Commit**

```bash
git add cli/src/wiki_cli/commands/reingest.py cli/src/wiki_cli/main.py
git commit -m "feat: reingest command with content hash comparison"
```

---

### Task 12: Publish Command & GitHub Actions

**Files:**
- Create: `cli/src/wiki_cli/commands/publish.py`
- Create: `.github/workflows/publish.yml`
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Implement publish.py**

```python
# cli/src/wiki_cli/commands/publish.py
import subprocess
import sys

import typer


def run_publish(preview: bool = False) -> None:
    """Build or preview the Quartz static site."""
    # Check if npx/quartz is available
    try:
        subprocess.run(["npx", "quartz", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("Error: Quartz is not installed. Run 'npm install' first.", err=True)
        raise typer.Exit(1)

    if preview:
        typer.echo("Starting Quartz dev server at http://localhost:8080...")
        try:
            subprocess.run(["npx", "quartz", "build", "--serve"], check=True)
        except KeyboardInterrupt:
            typer.echo("\nServer stopped.")
    else:
        typer.echo("Building static site...")
        result = subprocess.run(["npx", "quartz", "build"], capture_output=True, text=True)
        if result.returncode == 0:
            typer.echo("Build complete. Output in public/")
        else:
            typer.echo(f"Build failed:\n{result.stderr}", err=True)
            raise typer.Exit(1)
```

- [ ] **Step 2: Create GitHub Actions workflow**

```yaml
# .github/workflows/publish.yml
name: Publish Wiki

on:
  push:
    branches: [main]
    paths: [wiki/**]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      - name: Filter unpublished pages
        run: |
          find wiki -name '*.md' | while read f; do
            if head -20 "$f" | grep -q 'publish: false'; then
              rm "$f"
            fi
          done

      - run: npx quartz build

      - uses: actions/configure-pages@v4

      - uses: actions/upload-pages-artifact@v3
        with:
          path: public

      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 3: Wire publish command into main.py**

```python
@app.command()
def publish(
    preview: bool = typer.Option(False, "--preview", help="Start local dev server"),
):
    """Build and publish the wiki with Quartz."""
    from wiki_cli.commands.publish import run_publish
    run_publish(preview=preview)
```

- [ ] **Step 4: Commit**

```bash
git add cli/src/wiki_cli/commands/publish.py .github/workflows/publish.yml cli/src/wiki_cli/main.py
git commit -m "feat: publish command and GitHub Actions workflow for Quartz deployment"
```

---

### Task 13: Final main.py Cleanup & Integration

**Files:**
- Modify: `cli/src/wiki_cli/main.py`

- [ ] **Step 1: Write the final clean main.py**

Consolidate all command wiring into a clean final `main.py`:

```python
# cli/src/wiki_cli/main.py

from pathlib import Path

import typer

from wiki_cli.wiki_manager import WikiManager

app = typer.Typer(
    name="wiki",
    help="Personal LLM-powered knowledge base CLI",
    no_args_is_help=True,
)


def _load_deps():
    """Load config, provider, and wiki manager."""
    from wiki_cli.config import load_config
    from wiki_cli.providers import get_provider

    config = load_config(Path("wiki.yaml"))
    provider = get_provider(config.provider, config.provider_config)
    wiki_mgr = WikiManager(config.vault_path)
    return config, provider, wiki_mgr


@app.command()
def init(
    path: str = typer.Argument(".", help="Path to initialize the knowledge base"),
):
    """Initialize a new knowledge base."""
    from wiki_cli.commands.init_cmd import run_init
    run_init(Path(path))


@app.command()
def ingest(
    source: str = typer.Argument(None, help="URL, file path, or use --inbox"),
    inbox: bool = typer.Option(False, "--inbox", help="Process all files in sources/inbox/"),
    ref: bool = typer.Option(False, "--ref", help="Save as reference only"),
):
    """Ingest a source into the knowledge base."""
    from wiki_cli.commands.ingest import IngestPipeline

    config, provider, wiki_mgr = _load_deps()
    pipeline = IngestPipeline(wiki_mgr, provider, config.vault_path)

    if inbox:
        results = pipeline.run_inbox()
        succeeded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        typer.echo(f"Inbox: {succeeded} succeeded, {failed} failed")
        for r in results:
            if not r.success:
                typer.echo(f"  FAILED: {r.error}", err=True)
    elif ref:
        if not source:
            typer.echo("Error: source URL required with --ref", err=True)
            raise typer.Exit(1)
        result = pipeline.run_reference(source)
        typer.echo(f"Reference saved: {result.title}" if result.success else f"Error: {result.error}")
    else:
        if not source:
            typer.echo("Error: provide a source or use --inbox", err=True)
            raise typer.Exit(1)
        result = pipeline.run(source)
        if result.success:
            typer.echo(f'Ingested: "{result.title}" (+{result.pages_created}, ~{result.pages_updated} updated)')
        else:
            typer.echo(f"Error: {result.error}", err=True)


@app.command()
def reingest(
    source: str = typer.Argument(..., help="URL or file path to re-ingest"),
):
    """Re-fetch and update a previously ingested source."""
    from wiki_cli.commands.reingest import ReingestPipeline

    config, provider, wiki_mgr = _load_deps()
    pipeline = ReingestPipeline(wiki_mgr, provider, config.vault_path)
    result = pipeline.run(source)

    if result.success:
        if result.title == "(unchanged)":
            typer.echo("No changes detected. Skipping.")
        else:
            typer.echo(f'Re-ingested: "{result.title}" (+{result.pages_created}, ~{result.pages_updated} updated)')
    else:
        typer.echo(f"Error: {result.error}", err=True)


@app.command()
def query(
    question: str = typer.Argument(None, help="Question to ask"),
    save: bool = typer.Option(False, "--save", help="Save answer as exploration"),
    interactive: bool = typer.Option(False, "-i", help="Interactive mode"),
):
    """Query the knowledge base."""
    from wiki_cli.commands.query import QueryEngine

    _, provider, wiki_mgr = _load_deps()
    engine = QueryEngine(wiki_mgr, provider)

    if interactive:
        typer.echo("Interactive mode. /save to save last answer, /quit to exit.")
        last_answer = ""
        while True:
            q = typer.prompt("wiki")
            if q == "/quit":
                break
            if q == "/save" and last_answer:
                engine._save_exploration("interactive-query", last_answer)
                typer.echo("Saved.")
                continue
            last_answer = engine.ask(q)
            typer.echo(f"\n{last_answer}\n")
    else:
        if not question:
            typer.echo("Error: provide a question or use -i", err=True)
            raise typer.Exit(1)
        answer = engine.ask(question, save=save)
        typer.echo(answer)
        if save:
            typer.echo("\n(Saved to explorations)")


@app.command()
def lint(
    fix: bool = typer.Option(False, "--fix", help="Auto-fix repairable issues"),
    deep: bool = typer.Option(False, "--deep", help="LLM-powered deep analysis"),
):
    """Run health checks on the wiki."""
    from wiki_cli.commands.lint import WikiLinter
    from wiki_cli.config import load_config

    config = load_config(Path("wiki.yaml"))
    wiki_mgr = WikiManager(config.vault_path)
    linter = WikiLinter(wiki_mgr)
    report = linter.run_all()

    total = report["total_issues"]
    pages = len(wiki_mgr.list_pages())
    typer.echo(f"Wiki Health Report\n==================\n{pages} pages scanned\n")

    if total == 0:
        typer.echo("All checks passed!")
    else:
        for check_name, issues in report["by_check"].items():
            sym = "x" if issues else "v"
            typer.echo(f"  [{sym}] {check_name}: {len(issues)}")
            for issue in issues[:5]:
                typer.echo(f"      - {issue['page']}: {issue['detail']}")
            if len(issues) > 5:
                typer.echo(f"      ... and {len(issues) - 5} more")

    typer.echo(f"\nTotal: {total} issues")


@app.command()
def publish(
    preview: bool = typer.Option(False, "--preview", help="Start local dev server"),
):
    """Build and publish the wiki with Quartz."""
    from wiki_cli.commands.publish import run_publish
    run_publish(preview=preview)


if __name__ == "__main__":
    app()
```

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add cli/src/wiki_cli/main.py
git commit -m "refactor: clean up main.py with consolidated command wiring"
```

---

### Task 14: Quartz Setup & End-to-End Verification

**Files:**
- Create: `package.json`
- Create: `quartz.config.ts`

Note: git init and root config files (wiki.yaml, .env.example, .gitignore) were created in Task 1 Step 0.

- [ ] **Step 1: Initialize Quartz**

```bash
cd ~/projects/knowledge-base
npx quartz create --directory wiki --strategy new
```

This creates `quartz.config.ts`, `package.json`, and `quartz.layout.ts`. If the interactive prompts aren't suitable, create manually:

- [ ] **Step 2: Configure quartz.config.ts**

Ensure `quartz.config.ts` has the content directory set to `wiki/`:

```ts
// In quartz.config.ts, set:
configuration: {
  contentFolder: "wiki",
  // ... other config
}
```

- [ ] **Step 3: Run full test suite**

Run: `cd ~/projects/knowledge-base && pip install -e "cli[all,dev]" && pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Test wiki init end-to-end**

```bash
cd /tmp && mkdir test-kb && cd test-kb
wiki init .
ls -la schema/ sources/ wiki/
```
Expected: Full directory structure created with templates and config files

- [ ] **Step 5: Test Quartz build locally**

```bash
cd ~/projects/knowledge-base
npx quartz build
ls public/
```
Expected: Static site files generated in `public/`

- [ ] **Step 6: Commit**

```bash
cd ~/projects/knowledge-base
git add package.json quartz.config.ts quartz.layout.ts
git commit -m "feat: Quartz setup for GitHub Pages publishing"
```

---

## Summary

| Task | Description | Key files |
|------|-------------|-----------|
| 1 | Project scaffolding, git init, root configs | `pyproject.toml`, `main.py`, `wiki.yaml`, `.gitignore` |
| 2 | Configuration system | `config.py` |
| 3 | LLM provider interface | `providers/` |
| 4 | Source parsers | `parsers/` |
| 5 | Wiki manager (core ops) | `wiki_manager.py` |
| 6 | Schema & templates | `schema/` |
| 7 | Init command | `commands/init_cmd.py` |
| 8 | Ingest command | `commands/ingest.py` |
| 9 | Query command | `commands/query.py` |
| 10 | Lint command | `commands/lint.py` |
| 11 | Reingest command | `commands/reingest.py` |
| 12 | Publish command & CI | `commands/publish.py`, `.github/workflows/` |
| 13 | Main.py cleanup | `main.py` |
| 14 | Quartz setup & E2E verification | `package.json`, `quartz.config.ts` |

Tasks 1-5 build the foundation. Tasks 6-12 implement each feature. Tasks 13-14 finalize.
