"""FastAPI server exposing the QueryEngine as an API."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Wiki Knowledge Base API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    save: bool = False
    current_page: str | None = None


class QueryResponse(BaseModel):
    answer: str
    saved: bool = False


def _build_engine():
    from wiki_cli.config import load_config
    from wiki_cli.providers import get_provider
    from wiki_cli.wiki_manager import WikiManager
    from wiki_cli.commands.query import QueryEngine

    config = load_config(Path("wiki.yaml"))
    provider = get_provider(config.provider, config.provider_config)
    wiki_mgr = WikiManager(config.vault_path)
    return QueryEngine(wiki_mgr, provider), wiki_mgr


_engine = None
_wiki_mgr = None


def get_engine():
    global _engine, _wiki_mgr
    if _engine is None:
        _engine, _wiki_mgr = _build_engine()
    return _engine, _wiki_mgr


@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest):
    engine, wiki_mgr = get_engine()

    # If current_page provided, inject it into context by prepending to question
    question = req.question
    if req.current_page:
        page_content = wiki_mgr.read_page(req.current_page)
        if page_content:
            question = f"[Context: currently viewing page '{req.current_page}']\n\n{req.question}"

    answer = engine.ask(question, save=req.save)

    saved = False
    if req.save:
        try:
            wiki_mgr.commit(f'explore: "{req.question[:50]}"')
        except Exception:
            pass
        saved = True

    return QueryResponse(answer=answer, saved=saved)


@app.get("/api/health")
def health():
    return {"status": "ok"}
