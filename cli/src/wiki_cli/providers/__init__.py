from .base import LLMProvider


def get_provider(name: str, config: dict) -> LLMProvider:
    if name == "claude":
        from .claude import ClaudeProvider
        return ClaudeProvider(**config)
    elif name == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider(**config)
    elif name == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider(**config)
    else:
        raise ValueError(f"Unknown provider: {name}")
