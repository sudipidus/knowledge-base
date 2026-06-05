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

    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
        "they", "them", "what", "which", "who", "whom", "this", "that",
        "am", "not", "no", "nor", "and", "but", "or", "so", "if", "then",
        "than", "too", "very", "just", "about", "above", "after", "again",
        "all", "also", "any", "because", "before", "between", "both",
        "by", "for", "from", "how", "in", "into", "of", "on", "out",
        "over", "own", "same", "some", "such", "to", "up", "with",
        "know", "tell", "explain", "describe", "compare", "list",
    }

    def _search(self, question: str) -> list[dict]:
        all_pages = self.wiki_mgr.get_all_page_summaries()
        import re
        words = re.findall(r'[a-z0-9]+', question.lower())
        question_words = {w for w in words if w not in self.STOPWORDS and len(w) > 1}
        if not question_words:
            question_words = set(question.lower().split())

        scored = []
        for page in all_pages:
            title = page["title"].lower()
            tags = " ".join(page["tags"]).lower()
            content = page["content"].lower()
            # Title and tag matches are worth more
            score = 0
            for w in question_words:
                if w in title:
                    score += 5
                if w in tags:
                    score += 3
                if w in content:
                    score += 1
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
