from __future__ import annotations

from app.llm.models import (
    LLMAnalysisStatus,
    LLMClassification,
    LLMScamAnalysisRequest,
    LLMScamAnalysisResult,
)
from app.llm.providers.mock_provider import MockLLMProvider
from app.llm.service import LLMAnalysisService


def _req() -> LLMScamAnalysisRequest:
    return LLMScamAnalysisRequest(normalized_text="oi", deterministic_score=50)


def _result() -> LLMScamAnalysisResult:
    return LLMScamAnalysisResult(
        classification=LLMClassification.SCAM, confidence=0.9, risk_score=80, summary="x"
    )


def test_disabled_service_does_not_call_provider():
    provider = MockLLMProvider(result=_result())
    svc = LLMAnalysisService(provider=provider, enabled=False)
    out = svc.analyze(_req())
    assert out.status == LLMAnalysisStatus.DISABLED
    assert out.available is False
    assert provider.calls == []


def test_completed_returns_result_and_metadata():
    svc = LLMAnalysisService(provider=MockLLMProvider(result=_result()), enabled=True)
    out = svc.analyze(_req())
    assert out.status == LLMAnalysisStatus.COMPLETED
    assert out.available is True
    assert out.result is not None
    assert out.model == "mock-model"
    assert out.latency_ms is not None


def test_timeout_is_normalized_and_never_raises():
    svc = LLMAnalysisService(provider=MockLLMProvider(raise_timeout=True), enabled=True)
    out = svc.analyze(_req())
    assert out.status == LLMAnalysisStatus.TIMEOUT
    assert out.available is False


def test_provider_error_is_normalized():
    svc = LLMAnalysisService(provider=MockLLMProvider(raise_error=True), enabled=True, max_retries=1)
    out = svc.analyze(_req())
    assert out.status == LLMAnalysisStatus.PROVIDER_ERROR
    assert out.available is False


def test_retry_happens_at_most_once_then_succeeds():
    calls = {"n": 0}

    def flaky(_req):
        calls["n"] += 1
        if calls["n"] == 1:
            from app.llm.contract import LLMProviderError
            raise LLMProviderError("first fails")
        return _result()

    svc = LLMAnalysisService(
        provider=MockLLMProvider(result_fn=flaky), enabled=True, max_retries=1
    )
    out = svc.analyze(_req())
    assert out.status == LLMAnalysisStatus.COMPLETED
    assert calls["n"] == 2


def test_no_provider_is_disabled():
    svc = LLMAnalysisService(provider=None, enabled=True)
    assert svc.enabled is False
    assert svc.analyze(_req()).status == LLMAnalysisStatus.DISABLED
