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
        relevant = self._search(question)
        context = [f"# Source: {p['path']}\n\n{p['content']}" for p in relevant[:10]]
        answer = self.provider.complete_with_context(QUERY_SYSTEM_PROMPT, context, question)
        if save:
            self._save_exploration(question, answer)
        return answer

    def _search(self, question: str) -> list[dict]:
        all_pages = self.wiki_mgr.get_all_page_summaries()
        question_words = set(question.lower().split())
        scored = []
        for page in all_pages:
            page_text = f"{page['title']} {' '.join(page['tags'])} {page['content']}".lower()
            score = sum(1 for w in question_words if w in page_text)
            if score > 0:
                scored.append((score, page))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [page for _, page in scored]

    def _save_exploration(self, question: str, answer: str) -> None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        slug = slugify(question)
        page_path = f"explorations/{slug}"
        content = f'---\ntitle: "{question}"\ntype: exploration\ncreated_at: "{now}"\ntags: []\npublish: true\n---\n\n# {question}\n\n{answer}\n'
        self.wiki_mgr.write_page(page_path, content)
        self.wiki_mgr.update_index(page_path, question, "explorations")
        self.wiki_mgr.append_log("explore", question)
