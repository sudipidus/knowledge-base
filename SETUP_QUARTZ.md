# Quartz Setup for GitHub Pages Publishing

## Prerequisites

- Node.js v22+ (`node -v`)
- npm v10.9.2+

## Setup

Quartz v5 is a framework you clone and configure. Run this once:

```bash
cd ~/projects/knowledge-base

# Clone Quartz into the project root (it adds quartz/, package.json, etc.)
git clone https://github.com/jackyzha0/quartz.git quartz-tmp
cp -r quartz-tmp/quartz quartz-tmp/package.json quartz-tmp/tsconfig.json quartz-tmp/quartz.config.default.yaml .
rm -rf quartz-tmp

# Install dependencies
npm install
```

Then configure Quartz to read from your `wiki/` directory. Edit `quartz.config.default.yaml` and set the content directory:

```yaml
# In quartz.config.default.yaml, find and change:
contentDirectory: wiki
```

Or if using the `create` command after `npm install`:

```bash
npm run quartz -- create --directory wiki --strategy new --template obsidian --links shortest
```

## Verify

```bash
# Build locally
npm run quartz -- build --directory wiki

# Preview with live reload
npm run quartz -- build --serve --directory wiki
# Open http://localhost:8080
```

## GitHub Pages Deployment

The project includes `.github/workflows/publish.yml` which automatically deploys when you push changes to `wiki/**` on the `main` branch.

To enable:
1. Push this repo to GitHub
2. Go to Settings > Pages > Source: GitHub Actions
3. Push a change to `wiki/` — the action will build and deploy automatically

## Privacy

Pages with `publish: false` in frontmatter are filtered out during the CI build (see the workflow file). They remain visible locally in Obsidian but won't appear on the public site.
