from __future__ import annotations

import logging
import time
from typing import Optional

from app.llm.contract import LLMProvider, LLMProviderError, LLMProviderTimeout
from app.llm.models import (
    LLMAnalysisStatus,
    LLMScamAnalysisOutcome,
    LLMScamAnalysisRequest,
)

logger = logging.getLogger("cyberalerta.llm")


class LLMAnalysisService:
    """Runs the LLM step defensively and always returns an outcome — never raises.

    Responsibilities:
    - honor the ``enabled`` flag (disabled => no call, status DISABLED);
    - retry at most ``max_retries`` extra times on provider error;
    - normalize timeout/error/invalid-output into a status the Policy Engine can
      treat as "LLM unavailable" and fall back safely;
    - measure latency for auditing.

    It has no send capability and no knowledge of the WhatsApp adapter.
    """

    def __init__(
        self,
        *,
        provider: Optional[LLMProvider],
        enabled: bool,
        max_retries: int = 1,
        prompt_version: str = "v1",
    ) -> None:
        self._provider = provider
        self._enabled = enabled
        self._max_retries = max(0, max_retries)
        self._prompt_version = prompt_version

    @property
    def enabled(self) -> bool:
        return self._enabled and self._provider is not None

    def analyze(self, request: LLMScamAnalysisRequest) -> LLMScamAnalysisOutcome:
        if not self.enabled or self._provider is None:
            return LLMScamAnalysisOutcome(status=LLMAnalysisStatus.DISABLED)

        attempts = self._max_retries + 1
        started = time.monotonic()
        last_status = LLMAnalysisStatus.PROVIDER_ERROR
        last_error_kind: Optional[str] = None

        for attempt in range(attempts):
            try:
                result = self._provider.analyze_scam(request)
            except LLMProviderTimeout:
                last_status = LLMAnalysisStatus.TIMEOUT
                last_error_kind = "timeout"
            except LLMProviderError as exc:
                # exc text is provider-controlled but never contains secrets
                # (providers guarantee that). Record only the class name.
                last_status = LLMAnalysisStatus.PROVIDER_ERROR
                last_error_kind = type(exc).__name__
            except Exception as exc:  # unexpected: still never leak, still fall back
                logger.warning("Unexpected LLM error: %s", type(exc).__name__)
                last_status = LLMAnalysisStatus.PROVIDER_ERROR
                last_error_kind = "unexpected"
            else:
                latency_ms = int((time.monotonic() - started) * 1000)
                return LLMScamAnalysisOutcome(
                    status=LLMAnalysisStatus.COMPLETED,
                    result=result,
                    provider=getattr(self._provider, "name", None),
                    model=getattr(self._provider, "model", None),
                    prompt_version=self._prompt_version,
                    latency_ms=latency_ms,
                )
            # timeout is not worth retrying within a short webhook budget
            if last_status == LLMAnalysisStatus.TIMEOUT:
                break

        latency_ms = int((time.monotonic() - started) * 1000)
        return LLMScamAnalysisOutcome(
            status=last_status,
            provider=getattr(self._provider, "name", None),
            model=getattr(self._provider, "model", None),
            prompt_version=self._prompt_version,
            latency_ms=latency_ms,
            error_kind=last_error_kind,
        )
