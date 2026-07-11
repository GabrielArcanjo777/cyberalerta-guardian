from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.llm.models import LLMScamAnalysisRequest, LLMScamAnalysisResult


class LLMProviderError(Exception):
    """Provider-level failure (network, HTTP, malformed transport response).

    The message is intentionally generic — provider implementations must never
    put the API key, full prompt, or raw message content in the exception.
    """


class LLMProviderTimeout(LLMProviderError):
    """The provider did not answer within the configured timeout."""


@runtime_checkable
class LLMProvider(Protocol):
    """A scam classifier backed by some LLM endpoint.

    Implementations return a validated :class:`LLMScamAnalysisResult` or raise
    :class:`LLMProviderError` / :class:`LLMProviderTimeout`. They never send
    messages, never call the WhatsApp adapter, and never decide on delivery.
    """

    name: str
    model: str

    def analyze_scam(self, request: LLMScamAnalysisRequest) -> LLMScamAnalysisResult:
        ...
