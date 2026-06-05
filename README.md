# Knowledge Base

A personal LLM-powered knowledge base following [Karpathy's wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). Ingest sources, query your knowledge, and publish as a static site.

## Quick Start

```bash
# Install the CLI
pip install -e "cli[all,dev]"

# Configure your LLM provider (edit wiki.yaml)
# Default is Ollama — make sure it's running with a model pulled

# Ingest a source
wiki ingest article.md
wiki ingest https://some-blog.com/post

# Query your wiki
wiki query "What do I know about distributed systems?"

# Check wiki health
wiki lint
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `wiki init [path]` | Scaffold a new knowledge base |
| `wiki ingest <source>` | Ingest a URL, file, or `--inbox` to batch process |
| `wiki ingest --ref <url>` | Save a reference link (no LLM processing) |
| `wiki reingest <source>` | Re-ingest a source if content changed |
| `wiki query "question"` | Search wiki and get an LLM-synthesized answer |
| `wiki query -i` | Interactive query mode |
| `wiki query "question" --save` | Save the answer as an exploration page |
| `wiki lint` | Run structural health checks |
| `wiki serve [--port 8000]` | Start the API server for the web chat widget |
| `wiki publish --preview` | Preview site locally via Quartz |

## LLM Provider Setup

Edit `wiki.yaml` to set your provider:

```yaml
provider: ollama  # or: claude, openai

claude:
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-sonnet-4-20250514

openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4o

ollama:
  model: llama3
  base_url: http://localhost:11434
```

For Claude/OpenAI, copy `.env.example` to `.env` and add your API key.

## Quartz (Static Site)

Quartz v5 powers the static site for browsing your wiki with graph view, backlinks, and search.

### Setup (one-time)

```bash
# Clone Quartz framework files
git clone https://github.com/jackyzha0/quartz.git quartz-tmp
cp -r quartz-tmp/quartz quartz-tmp/package.json quartz-tmp/package-lock.json \
      quartz-tmp/quartz.config.default.yaml quartz-tmp/quartz.lock.json \
      quartz-tmp/globals.d.ts quartz-tmp/index.d.ts .
rm -rf quartz-tmp

# Create the config entry point
cat > quartz.ts << 'EOF'
import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
EOF

# Copy and customize the config
cp quartz.config.default.yaml quartz.config.yaml
# Edit quartz.config.yaml: set pageTitle, baseUrl, etc.

# Install dependencies and plugins
npm install
npm run quartz -- plugin install --from-config
```

### Preview locally with chat

Run both in separate terminals:

```bash
# Terminal 1: Start the wiki API server (powers the chat widget)
wiki serve

# Terminal 2: Start Quartz dev server
npm run quartz -- build -d wiki --serve
# Open http://localhost:8080
```

A chat bubble appears in the bottom-right corner of every page. Click it to query your knowledge base — same as `wiki query` but from the browser. Each response has a "Save to wiki" button (same as `--save`).

### Build static site

```bash
npm run quartz -- build -d wiki
# Output in public/
```

### Deploy to GitHub Pages

The project includes `.github/workflows/publish.yml` that auto-deploys on pushes to `wiki/**` on `main`.

1. Push repo to GitHub
2. Go to Settings > Pages > Source: GitHub Actions
3. Push a change to `wiki/` — deploys automatically

Pages with `publish: false` in frontmatter are excluded from the public site.

## Project Structure

```
knowledge-base/
├── wiki/                  # LLM-maintained wiki pages (Obsidian vault)
│   ├── entities/          # People, tools, companies
│   ├── concepts/          # Ideas, patterns, mental models
│   ├── topics/            # Source summaries
│   ├── syntheses/         # Cross-cutting comparisons
│   ├── explorations/      # Saved query answers
│   ├── index.md           # Auto-maintained catalog
│   └── log.md             # Activity log
├── sources/
│   ├── raw/               # Stored raw sources
│   ├── references/        # Reference-only links
│   └── inbox/             # Drop zone for batch ingestion
├── schema/                # Wiki conventions + page templates
├── cli/                   # Python CLI package
└── wiki.yaml              # Configuration
```

## Development

```bash
# Run tests
.venv/bin/pytest tests/ -v

# Install in dev mode
pip install -e "cli[all,dev]"
```
