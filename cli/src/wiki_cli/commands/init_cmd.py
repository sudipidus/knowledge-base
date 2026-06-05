"""wiki init command — bootstraps a new knowledge base directory."""

from pathlib import Path

import typer

# ---------------------------------------------------------------------------
# Default file contents (embedded so init works regardless of install location)
# ---------------------------------------------------------------------------

DEFAULT_SCHEMA_MD = """\
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
"""

DEFAULT_ENTITY_TEMPLATE = """\
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
"""

DEFAULT_CONCEPT_TEMPLATE = """\
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
"""

DEFAULT_SOURCE_SUMMARY_TEMPLATE = """\
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
"""

DEFAULT_COMPARISON_TEMPLATE = """\
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
"""

DEFAULT_WIKI_YAML = """\
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
"""

DEFAULT_ENV_EXAMPLE = """\
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
"""

DEFAULT_GITIGNORE = """\
.env
public/
.obsidian/workspace.json
.obsidian/workspace-mobile.json
__pycache__/
*.pyc
.venv/
node_modules/
"""

DEFAULT_INDEX = """\
---
title: Index
publish: true
---

# Knowledge Base Index

Welcome to your personal knowledge base.

## Entities

## Concepts

## Topics

## Syntheses

## Explorations
"""

DEFAULT_LOG = """\
---
title: Log
publish: true
---

# Operations Log

This file records every ingest / update operation performed on the wiki.
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_if_not_exists(path: Path, content: str) -> None:
    """Write *content* to *path* only if the file does not already exist."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _ensure_dir_with_gitkeep(directory: Path) -> None:
    """Create *directory* (with parents) and drop a .gitkeep inside."""
    directory.mkdir(parents=True, exist_ok=True)
    gitkeep = directory / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("")


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def run_init(vault_path: Path) -> None:
    """Bootstrap a knowledge-base directory at *vault_path*."""
    vault_path.mkdir(parents=True, exist_ok=True)

    # --- Schema & templates ------------------------------------------------
    _write_if_not_exists(vault_path / "schema" / "SCHEMA.md", DEFAULT_SCHEMA_MD)
    _write_if_not_exists(vault_path / "schema" / "templates" / "entity.md", DEFAULT_ENTITY_TEMPLATE)
    _write_if_not_exists(vault_path / "schema" / "templates" / "concept.md", DEFAULT_CONCEPT_TEMPLATE)
    _write_if_not_exists(vault_path / "schema" / "templates" / "source-summary.md", DEFAULT_SOURCE_SUMMARY_TEMPLATE)
    _write_if_not_exists(vault_path / "schema" / "templates" / "comparison.md", DEFAULT_COMPARISON_TEMPLATE)

    # --- Sources directories -----------------------------------------------
    for sub in ("raw", "references", "inbox"):
        _ensure_dir_with_gitkeep(vault_path / "sources" / sub)

    # --- Wiki directories & seed files -------------------------------------
    _write_if_not_exists(vault_path / "wiki" / "index.md", DEFAULT_INDEX)
    _write_if_not_exists(vault_path / "wiki" / "log.md", DEFAULT_LOG)
    for sub in ("entities", "concepts", "topics", "syntheses", "explorations"):
        _ensure_dir_with_gitkeep(vault_path / "wiki" / sub)

    # --- Root config files -------------------------------------------------
    _write_if_not_exists(vault_path / "wiki.yaml", DEFAULT_WIKI_YAML)
    _write_if_not_exists(vault_path / ".env.example", DEFAULT_ENV_EXAMPLE)
    _write_if_not_exists(vault_path / ".gitignore", DEFAULT_GITIGNORE)

    # --- User feedback -----------------------------------------------------
    typer.echo(f"Knowledge base initialized at {vault_path.resolve()}")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo("  1. cd into the directory and review wiki.yaml")
    typer.echo("  2. Copy .env.example to .env and add your API keys")
    typer.echo("  3. Run: wiki ingest <url-or-file>")
