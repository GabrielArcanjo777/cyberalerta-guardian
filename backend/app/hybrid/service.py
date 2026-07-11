from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.event_model.models import RiskAssessment
from app.hybrid.deterministic import build_deterministic_assessment
from app.hybrid.models import (
    DeterministicAssessment,
    HybridDecision,
    HybridDecisionContext,
)
from app.hybrid.pii import content_hash, detect_prompt_injection, sanitize_for_llm
from app.hybrid.policy import HybridDecisionPolicy
from app.llm.models import (
    LLMAnalysisStatus,
    LLMScamAnalysisOutcome,
    LLMScamAnalysisRequest,
)
from app.llm.service import LLMAnalysisService


@dataclass
class HybridAnalysisOutcome:
    """Everything the flow needs to persist events and (maybe) alert.

    Carries the decision plus audit metadata — never the raw message (only its
    hash) and never secrets/prompts.
    """

    decision: HybridDecision
    deterministic: DeterministicAssessment
    llm_outcome: LLMScamAnalysisOutcome
    content_hash: str
    injection_suspected: bool
    truncated: bool
    redactions: List[str]


class HybridAnalysisService:
    """Runs deterministic normalization → sanitize → LLM → Policy Engine.

    No send capability. Returns a decision; the caller applies shadow mode and
    the existing safety gate before any real WhatsApp send.
    """

    def __init__(
        self,
        *,
        llm_service: LLMAnalysisService,
        policy: HybridDecisionPolicy,
        context: HybridDecisionContext,
        max_message_chars: int = 4000,
        redact_pii: bool = True,
    ) -> None:
        self._llm = llm_service
        self._policy = policy
        self._context = context
        self._max_chars = max_message_chars
        self._redact_pii = redact_pii

    @property
    def context(self) -> HybridDecisionContext:
        return self._context

    def analyze(
        self,
        *,
        assessment: RiskAssessment,
        message_text: str,
        sender_is_new_number: Optional[bool] = None,
        sender_is_unknown: Optional[bool] = None,
        recent_context: Optional[List[str]] = None,
        language: str = "pt",
    ) -> HybridAnalysisOutcome:
        deterministic = build_deterministic_assessment(assessment, message_text)
        chash = content_hash(message_text)
        injection = detect_prompt_injection(message_text)

        sanitized = sanitize_for_llm(
            message_text, max_chars=self._max_chars, redact_pii=self._redact_pii
        )

        llm_outcome = LLMScamAnalysisOutcome(status=LLMAnalysisStatus.DISABLED)
        if self._llm.enabled:
            request = LLMScamAnalysisRequest(
                normalized_text=sanitized.text,
                deterministic_score=deterministic.score,
                deterministic_signals=[s.code for s in deterministic.signals],
                recent_context=recent_context or [],
                sender_is_new_number=sender_is_new_number,
                sender_is_unknown=sender_is_unknown,
                language=language,
            )
            llm_outcome = self._llm.analyze(request)

        invalid_output = llm_outcome.status == LLMAnalysisStatus.INVALID_OUTPUT

        decision = self._policy.decide(
            deterministic,
            llm_outcome.result,
            self._context,
            llm_available=llm_outcome.available,
            invalid_llm_output=invalid_output,
            prompt_injection_suspected=injection,
        )

        return HybridAnalysisOutcome(
            decision=decision,
            deterministic=deterministic,
            llm_outcome=llm_outcome,
            content_hash=chash,
            injection_suspected=injection,
            truncated=sanitized.truncated,
            redactions=sanitized.redactions,
        )


def build_hybrid_service_from_config(config) -> HybridAnalysisService:
    """Wire the hybrid service from AppConfig. Provider is only constructed when
    enabled and fully configured; otherwise the LLM step is disabled and the
    pipeline runs deterministic-only (safe)."""
    from app.hybrid.policy import HybridDecisionPolicy
    from app.llm.contract import LLMProvider

    provider: Optional[LLMProvider] = None
    enabled = bool(config.hybrid_llm_enabled)
    if enabled and config.hybrid_llm_base_url and config.hybrid_llm_api_key and config.hybrid_llm_model:
        from app.llm.providers.openai_compatible import OpenAICompatibleProvider

        provider = OpenAICompatibleProvider(
            base_url=config.hybrid_llm_base_url,
            api_key=config.hybrid_llm_api_key,
            model=config.hybrid_llm_model,
            timeout_seconds=float(config.hybrid_llm_timeout_seconds),
            temperature=float(config.hybrid_llm_temperature),
        )
    else:
        # Missing config => never call out. LLM step stays disabled.
        enabled = False

    llm_service = LLMAnalysisService(
        provider=provider,
        enabled=enabled,
        max_retries=int(config.hybrid_llm_max_retries),
        prompt_version=config.hybrid_llm_prompt_version,
    )
    context = HybridDecisionContext(
        llm_enabled=bool(config.hybrid_llm_enabled),
        shadow_mode=bool(config.hybrid_llm_shadow_mode),
        require_llm_for_auto_alert=bool(config.hybrid_require_llm_for_auto_alert),
        policy_version=config.hybrid_policy_version,
    )
    return HybridAnalysisService(
        llm_service=llm_service,
        policy=HybridDecisionPolicy(),
        context=context,
        max_message_chars=int(config.hybrid_max_message_chars),
        redact_pii=bool(config.hybrid_redact_pii),
    )
