# Web Chat Interface

**Date:** 2026-06-05
**Status:** Approved

## Overview

A floating chat widget embedded in the Quartz site that calls a local FastAPI backend. The backend runs the exact same `QueryEngine` code as `wiki query`.

## Architecture

- **Frontend:** JavaScript chat widget injected into Quartz pages via custom head config
- **Backend:** FastAPI server with one endpoint, reusing `QueryEngine` from `wiki_cli`
- **New CLI command:** `wiki serve` starts the FastAPI server on `localhost:8000`

## Backend

**File:** `cli/src/wiki_cli/server.py`

Single endpoint: `POST /api/query`

Request:
```json
{"question": "What is Redis?", "save": false, "current_page": "entities/redis"}
```

Response:
```json
{"answer": "Redis is...", "saved": false}
```

- Loads config, creates provider and QueryEngine — same setup as CLI
- If `current_page` provided, reads that page and prepends to search results
- If `save: true`, calls `_save_exploration()` then auto-commits
- CORS enabled for all origins (local use)

**New CLI command in main.py:**
```
wiki serve [--port 8000]
```

**Dependencies:** Add `fastapi` and `uvicorn` to pyproject.toml.

## Frontend

**File:** `quartz/static/chat-widget.js`

Injected via Quartz custom head config or by adding a script tag to the layout.

- Floating button (bottom-right corner) → click to toggle slide-out chat panel
- Chat panel: message history + input box + send button
- Each bot response has a "Save" button that calls the endpoint with `save: true`
- Sends `current_page` slug extracted from the URL path
- If API unreachable, shows: "Start the wiki server with `wiki serve`"
- Styled to match Quartz theme (respects dark/light mode)
