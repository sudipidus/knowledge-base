import httpx
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, system: str, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "system": system, "prompt": prompt, "stream": False},
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()["response"]

    def complete_with_context(self, system: str, context: list[str], prompt: str) -> str:
        return self.complete(system, self._build_context_prompt(context, prompt))
