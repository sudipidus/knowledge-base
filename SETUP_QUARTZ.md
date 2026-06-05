# Quartz Setup for GitHub Pages Publishing

## Prerequisites

- Node.js v22+ (`node -v`)
- npm v10.9.2+

## Setup

Quartz needs to be initialized once before you can use `wiki publish`.

```bash
cd ~/projects/knowledge-base

# Initialize Quartz in the project root
npx quartz create

# When prompted:
# - Choose "Empty Quartz" (we have our own content in wiki/)
# - Choose your preferred link style (recommend "Shortest path")
```

After initialization, edit `quartz.config.ts` to point at your wiki directory:

```ts
// In quartz.config.ts, find the configuration object and set:
configuration: {
  // ... other settings
  contentFolder: "wiki",  // Point to our wiki/ directory instead of default content/
}
```

## Verify

```bash
# Build locally
npx quartz build

# Preview with live reload
npx quartz build --serve
# Open http://localhost:8080
```

## GitHub Pages Deployment

The project includes `.github/workflows/publish.yml` which automatically deploys when you push changes to `wiki/**` on the `main` branch.

To enable:
1. Push this repo to GitHub
2. Go to Settings > Pages > Source: GitHub Actions
3. Push a change to `wiki/` — the action will build and deploy automatically
