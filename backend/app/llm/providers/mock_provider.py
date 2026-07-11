from __future__ import annotations

from typing import Callable, Optional

from app.llm.contract import LLMProvider, LLMProviderError, LLMProviderTimeout
from app.llm.models import LLMScamAnalysisRequest, LLMScamAnalysisResult


class MockLLMProvider(LLMProvider):
    """Deterministic in-memory provider for tests and offline development.

    Never touches the network. Behavior is fully driven by the constructor:
    - ``result``: a fixed result to return;
    - ``result_fn``: compute a result from the request;
    - ``raise_error`` / ``raise_timeout``: simulate provider failure.

    Tests must use this (or a similar fake) — real endpoints are never called in
    the automated suite.
    """

    def __init__(
        self,
        *,
        result: Optional[LLMScamAnalysisResult] = None,
        result_fn: Optional[Callable[[LLMScamAnalysisRequest], LLMScamAnalysisResult]] = None,
        raise_error: bool = False,
        raise_timeout: bool = False,
        name: str = "mock",
        model: str = "mock-model",
    ) -> None:
        self._result = result
        self._result_fn = result_fn
        self._raise_error = raise_error
        self._raise_timeout = raise_timeout
        self.name = name
        self.model = model
        self.calls: list[LLMScamAnalysisRequest] = []

    def analyze_scam(self, request: LLMScamAnalysisRequest) -> LLMScamAnalysisResult:
        self.calls.append(request)
        if self._raise_timeout:
            raise LLMProviderTimeout("mock timeout")
        if self._raise_error:
            raise LLMProviderError("mock provider error")
        if self._result_fn is not None:
            return self._result_fn(request)
        if self._result is not None:
            return self._result
        raise LLMProviderError("MockLLMProvider has no configured result")
