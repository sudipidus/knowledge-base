# Personal LLM-Powered Knowledge Base

**Date:** 2026-06-05
**Status:** Approved
**Location:** `~/projects/knowledge-base/`

## Overview

A three-layer personal wiki following Karpathy's LLM wiki pattern. Obsidian for local browsing/editing, Python CLI for LLM-powered operations (ingest, query, lint), Quartz for GitHub Pages publishing.

The human curates sources and asks good questions. The LLM handles summarizing, cross-referencing, and consistency maintenance.

## Architecture

### Three Layers

1. **Sources** (immutable) — raw articles, PDFs, and reference links curated by the user. LLM reads but never modifies.
2. **Wiki** (LLM-maintained) — structured markdown pages: summaries, entities, concepts, syntheses, explorations. Cross-referenced with Obsidian `[[wikilinks]]`. Gets richer with every ingest and query.
3. **Schema** (configuration) — `SCHEMA.md` + templates that instruct the LLM on wiki structure, conventions, and page types.

### Directory Structure

```
~/projects/knowledge-base/
├── schema/
│   ├── SCHEMA.md                # Wiki conventions, structure rules, LLM instructions
│   └── templates/               # Page type templates
│       ├── entity.md
│       ├── concept.md
│       ├── source-summary.md
│       └── comparison.md
├── sources/
│   ├── raw/                     # Stored raw sources (articles as markdown, PDFs)
│   ├── references/              # Reference-only entries (links to codebases, large files)
│   └── inbox/                   # Drop zone — files here await ingestion
├── wiki/
│   ├── index.md                 # Auto-maintained content catalog by category
│   ├── log.md                   # Append-only chronological activity log
│   ├── entities/                # People, tools, companies, projects
│   ├── concepts/                # Ideas, patterns, mental models
│   ├── topics/                  # Domain areas (health, finance, ML, distributed systems, etc.)
│   ├── syntheses/               # Cross-cutting comparisons, analyses
│   └── explorations/            # Query answers worth keeping
├── cli/
│   ├── pyproject.toml
│   └── src/
│       └── wiki_cli/
│           ├── __init__.py
│           ├── main.py           # CLI entry point (typer)
│           ├── commands/
│           │   ├── init.py       # Bootstrap new knowledge base
│           │   ├── ingest.py     # Ingest sources -> wiki pages
│           │   ├── reingest.py   # Re-fetch and diff-update changed sources
│           │   ├── query.py      # Ask questions against wiki
│           │   ├── lint.py       # Health checks, consistency
│           │   └── publish.py    # Trigger Quartz build
│           ├── providers/
│           │   ├── base.py       # LLM provider interface (ABC)
│           │   ├── claude.py     # Anthropic API provider
│           │   ├── openai.py     # OpenAI API provider
│           │   └── ollama.py     # Local models via Ollama
│           ├── parsers/
│           │   ├── web.py        # URL -> markdown (httpx + beautifulsoup4 + markdownify)
│           │   ├── pdf.py        # PDF -> markdown (pdfplumber)
│           │   └── text.py       # Plain text/markdown passthrough
│           └── config.py         # Load wiki.yaml configuration
├── .github/
│   └── workflows/
│       └── publish.yml           # GitHub Actions: build Quartz -> deploy to Pages
├── wiki.yaml                     # User config (provider, API keys, preferences)
├── .gitignore
└── .obsidian/                    # Obsidian vault config (auto-generated)
```

## CLI Commands

All commands are invoked via `wiki <command>`.

### `wiki init`

Bootstraps a new knowledge base:
1. Creates the directory structure (`schema/`, `sources/`, `wiki/`, etc.)
2. Initializes git repo
3. Creates default `wiki.yaml` with placeholder config
4. Creates default `SCHEMA.md` and page templates
5. Creates initial `wiki/index.md` and `wiki/log.md`
6. Creates `.gitignore` (excludes `.env`, `.obsidian/workspace.json`, `public/`)
7. Creates `.env.example` with required env var placeholders
8. Prints next steps (configure provider, open in Obsidian)

### `wiki ingest <source>`

**Input types:**

| Input | Example | Raw Storage |
|-------|---------|-------------|
| URL | `wiki ingest https://blog.com/post` | Converted to markdown -> `sources/raw/` |
| PDF | `wiki ingest paper.pdf` | Copied to `sources/raw/` |
| Local file | `wiki ingest notes.md` | Copied to `sources/raw/` |
| Inbox batch | `wiki ingest --inbox` | Processes all files in `sources/inbox/` |
| Codebase ref | `wiki ingest --ref https://github.com/org/repo` | Link saved to `sources/references/` only |

**Ingest pipeline:**

1. **Parse** — extract text from source (web scraper, PDF parser, or passthrough)
2. **Summarize** — LLM generates structured summary using `schema/templates/source-summary.md`
3. **Extract entities & concepts** — LLM identifies people, tools, ideas, patterns
4. **Create/update pages** — for each entity/concept: create new page from template, or update existing page (see reconciliation strategy below)
5. **Update cross-references** — add `[[backlinks]]` between related pages. Relatedness is determined by entities/concepts extracted in step 3, not by scanning the full wiki.
6. **Update `wiki/index.md`** — add entry under appropriate category
7. **Update `wiki/log.md`** — append: `## [2026-06-05] ingest | "Article Title"`
8. **Auto-commit** — message: `ingest: "Article Title" (+3 pages, ~2 updated)`

**Failure handling:**

Ingest is atomic — all file changes are staged in memory and only written to disk + committed if the entire pipeline succeeds. If any step fails:
- No files are written or modified
- Error is printed with the failing step and source identified
- The source remains in its original location (inbox or CLI argument) for retry
- For `--inbox` batch mode, each source is processed independently — one failure does not block others. Failed sources are logged and summarized at the end.

**Reconciliation strategy (step 4):**

When updating an existing wiki page with new information:
- The LLM receives the existing page content + new extracted information
- The prompt instructs: "Merge the new information into the existing page. Preserve existing content. Add new facts, update outdated claims, note contradictions with `> [!warning]` callouts. Do not duplicate."
- If an existing page exceeds 3000 tokens, the LLM works section-by-section rather than rewriting the whole page
- The result replaces the existing file (git diff shows exactly what changed)

**Source tracking frontmatter:**

```yaml
---
title: Understanding Distributed Consensus
source_url: https://blog.com/distributed-consensus
source_type: web
ingested_at: 2026-06-05T10:30:00
content_hash: sha256:abc123
tags: [distributed-systems, consensus, raft]
publish: true
---
```

### `wiki reingest <source>`

Re-fetches a previously ingested source and compares content hashes. Supports URLs (re-fetch from web) and local file paths (re-read from disk). If changed:
- Generates a diff-aware summary of what changed
- Updates the source summary and all affected entity/concept/topic pages
- Logs: `## [DATE] reingest | "Title" (content updated)`

If unchanged: `No changes detected. Skipping.`

Old raw source is overwritten (git history preserves previous versions).

### `wiki query "question" [--save] [-i]`

**Flow:**

1. **Search** — scan wiki pages for relevant content (keyword matching + frontmatter tags)
2. **Gather context** — collect top relevant wiki pages (not raw sources)
3. **Synthesize** — LLM answers with `[[wikilink]]` citations to wiki pages
4. **Display** — print answer to terminal
5. **Save** (optional, `--save`) — promote answer to `wiki/explorations/`, update index and cross-references

**Interactive mode (`-i`):**

```
$ wiki query -i
wiki> What's the relationship between Raft and Paxos?
[answer with citations]
wiki> /save
wiki> /quit
```

**Search scaling:**

| Wiki size | Method |
|-----------|--------|
| < 100 pages | Load all page frontmatter + headings, LLM picks relevant ones |
| 100-500 pages | BM25 keyword search |
| 500+ pages | Hybrid BM25 + vector embeddings (SQLite + local embedding model) |

### `wiki lint [--fix] [--deep]`

**Structural checks:**

| Check | Description |
|-------|-------------|
| Orphan pages | Pages with no incoming backlinks |
| Broken links | `[[wikilinks]]` pointing to nonexistent pages |
| Stale sources | Web sources older than threshold with changed content |
| Missing frontmatter | Pages lacking required fields |
| Duplicate entities | Multiple pages about the same thing |
| Index drift | Pages not listed in `index.md` |
| Empty sections | Placeholder headings with no content |

**`--fix`:** Auto-repairs orphans (suggest backlinks), broken links (create stubs), index drift (add missing entries). Prompts for re-ingest on stale sources.

**`--deep`:** LLM reads related pages and flags contradictions, missing citations, and synthesis opportunities. Expensive — run occasionally.

### `wiki publish [--preview]`

- `--preview`: starts local Quartz dev server at `localhost:8080`
- Without flag: builds static site to `/public`
- Filters out pages with `publish: false` frontmatter before building

## LLM Provider Configuration

**`wiki.yaml`:**

```yaml
provider: claude  # claude | openai | ollama
claude:
  api_key: ${ANTHROPIC_API_KEY}  # env var reference
  model: claude-sonnet-4-20250514
openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o
ollama:
  model: llama3.1
  base_url: http://localhost:11434

vault_path: .  # relative to wiki.yaml
stale_threshold_days: 30
auto_commit: true
```

**Provider interface (`providers/base.py`):**

```python
class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system: str, prompt: str) -> str: ...

    @abstractmethod
    async def complete_with_context(self, system: str, context: list[str], prompt: str) -> str: ...
```

All commands use this interface — swap providers by changing one config value.

## Publishing: Quartz + GitHub Pages

**Quartz configuration:**
- Source directory: `wiki/` only (raw sources and CLI code excluded)
- Enabled: graph view, backlinks, full-text search, tag pages, explorer sidebar

**GitHub Actions (`.github/workflows/publish.yml`):**

```yaml
on:
  push:
    branches: [main]
    paths: [wiki/**]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx quartz build
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: public
      - uses: actions/deploy-pages@v4
```

Quartz content directory is configured in `quartz.config.ts` (set to `wiki/`), not via CLI flag. Only triggers on wiki content changes.

**Privacy control:** Pages with `publish: false` in frontmatter are filtered out during the Quartz build. Full wiki is private locally; public site is curated. Default is `publish: true` — set `publish: false` on sensitive pages (personal, health, finance, etc.).

## Tech Stack

| Component | Technology |
|-----------|-----------|
| CLI framework | typer |
| Web scraping | httpx + beautifulsoup4 + markdownify |
| PDF parsing | pdfplumber |
| LLM clients | anthropic, openai, ollama (Python SDKs) |
| Config | PyYAML |
| Content hashing | hashlib (sha256) |
| Search (future) | SQLite + embeddings |
| Local browsing | Obsidian |
| Static site | Quartz v4 |
| CI/CD | GitHub Actions |
| Version control | git |

## Key Design Decisions

1. **Wiki is the compiled layer** — queries run against wiki pages, not raw sources. Knowledge is compiled once and kept current.
2. **Git as version control** — no custom versioning. Re-ingestion overwrites files; git history preserves all versions.
3. **Auto-commit on operations** — every ingest/reingest/lint-fix creates an atomic commit for traceable history.
4. **Obsidian wikilinks** — `[[page-name]]` syntax for cross-references. Works in both Obsidian and Quartz.
5. **Search scales lazily** — start with simple page scanning, add BM25/embeddings only when wiki grows large enough to need it.
6. **Raw sources are optional per type** — full storage for articles/PDFs, reference-only for large codebases.
7. **Public by default, opt-out for sensitive content** — pages default to `publish: true` and appear on the GitHub Pages site. Set `publish: false` in frontmatter for sensitive pages (personal journals, health, finance, etc.). The full wiki is always available locally in Obsidian regardless of publish flag.
8. **Atomic operations** — ingest writes no files and makes no commits unless the entire pipeline succeeds. Partial failures leave the wiki in its previous consistent state.
9. **Secrets via environment variables** — `wiki.yaml` references env vars (`${ANTHROPIC_API_KEY}`), never stores raw keys. A `.env` file (gitignored) and `.env.example` (committed) are used for local configuration.
10. **Single-user, serial operations** — the CLI assumes one user running one command at a time. No locking or concurrency control.
11. **Python 3.10+** — required for modern type syntax used in the codebase.
