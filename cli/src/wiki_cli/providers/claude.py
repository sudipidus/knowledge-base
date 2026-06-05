from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(self, system: str, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model, max_tokens=4096, system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def complete_with_context(self, system: str, context: list[str], prompt: str) -> str:
        return self.complete(system, self._build_context_prompt(context, prompt))
