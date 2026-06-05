from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str) -> str:
        ...

    @abstractmethod
    def complete_with_context(self, system: str, context: list[str], prompt: str) -> str:
        ...

    def _build_context_prompt(self, context: list[str], prompt: str) -> str:
        context_block = "\n\n---\n\n".join(context)
        return f"## Context Documents\n\n{context_block}\n\n---\n\n## Question\n\n{prompt}"
