"""Port: provider-agnostic LLM access.

Abstract interface only — no logic. This interface must stay strictly
provider-agnostic: no Ollama/Claude/OpenAI-specific parameters may leak into
any signature here. Concrete providers live under ``backend/adapters/``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMProvider(ABC):
    """Stream completions from some language model, provider unspecified."""

    @abstractmethod
    def stream_completion(self, prompt: str, context: str) -> AsyncIterator[str]:
        """Stream a completion token-by-token for ``prompt`` grounded in ``context``."""
        ...
