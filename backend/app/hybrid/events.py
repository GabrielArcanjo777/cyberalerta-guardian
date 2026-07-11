from __future__ import annotations

from typing import Optional

from app.event_model.event_bus import LocalEventBus
from app.event_model.models import BotEventType
from app.hybrid.models import HybridAction
from app.hybrid.service import HybridAnalysisOutcome
from app.llm.models import LLMAnalysisStatus

# LLM statuses that mean "did not produce a usable result".
_LLM_FAILURE_STATUSES = {
    LLMAnalysisStatus.TIMEOUT,
    LLMAnalysisStatus.PROVIDER_ERROR,
    LLMAnalysisStatus.INVALID_OUTPUT,
}


def _audit_payload(outcome: HybridAnalysisOutcome, message_id: Optional[str]) -> dict:
    """Auditable metadata only — never the message body, prompt, or API key."""
    d = outcome.decision
    llm = outcome.llm_outcome
    return {
        "message_id": message_id,
        "content_hash": outcome.content_hash,
        "deterministic_score": outcome.deterministic.score,
        "rule_codes": [s.code for s in outcome.deterministic.signals],
        "llm_provider": llm.provider,
        "llm_model": llm.model,
        "llm_status": llm.status.value,
        "prompt_version": llm.prompt_version,
        "policy_version": d.policy_version,
        "classification": (llm.result.classification.value if llm.result else None),
        "confidence": d.confidence,
        "llm_score": d.llm_score,
        "final_score": d.final_score,
        "action": d.action.value,
        "reasons": d.reasons[:6],
        "scam_types": [t.value for t in d.scam_types],
        "conflict": d.conflict,
        "shadow_decision": d.shadow_decision,
        "requires_human_review": d.requires_human_review,
        "latency_ms": llm.latency_ms,
        "redactions": outcome.redactions,
        "truncated": outcome.truncated,
    }


def emit_hybrid_events(
    event_bus: LocalEventBus,
    outcome: HybridAnalysisOutcome,
    *,
    message_id: Optional[str],
    case_id: Optional[str] = None,
    protected_person_id: Optional[str] = None,
) -> None:
    """Emit the full audit trail for one hybrid analysis.

    Order: deterministic → llm req/result → injection → decision → action.
    Every payload is auditable metadata; raw content and secrets never appear.
    """
    payload = _audit_payload(outcome, message_id)

    def pub(event_type: BotEventType, extra: Optional[dict] = None) -> None:
        body = dict(payload)
        if extra:
            body.update(extra)
        event_bus.publish_type(
            event_type,
            aggregate_type="message",
            aggregate_id=message_id or "unknown",
            source="hybrid_pipeline",
            case_id=case_id,
            protected_person_id=protected_person_id,
            payload=body,
        )

    pub(BotEventType.DETERMINISTIC_ASSESSMENT_CREATED)

    llm = outcome.llm_outcome
    if llm.status != LLMAnalysisStatus.DISABLED:
        pub(BotEventType.LLM_ANALYSIS_REQUESTED)
        if llm.available:
            pub(BotEventType.LLM_ANALYSIS_COMPLETED)
        elif llm.status in _LLM_FAILURE_STATUSES:
            pub(BotEventType.LLM_ANALYSIS_FAILED, {"error_kind": llm.error_kind})
            pub(BotEventType.POLICY_FALLBACK_USED)

    if outcome.injection_suspected:
        pub(BotEventType.PROMPT_INJECTION_DETECTED)

    decision = outcome.decision
    if decision.shadow_decision:
        pub(BotEventType.HYBRID_SHADOW_DECISION_CREATED)
    else:
        pub(BotEventType.HYBRID_DECISION_CREATED)

    if decision.action == HybridAction.REVIEW:
        pub(BotEventType.REVIEW_QUEUED)
    elif decision.action == HybridAction.AUTO_ALERT:
        # In shadow (or whenever the decision is flagged shadow) the alert must
        # NOT fire — record it as blocked so the audit trail is honest.
        if decision.shadow_decision:
            pub(BotEventType.AUTO_ALERT_BLOCKED, {"blocked_reason": "shadow_mode"})
        else:
            pub(BotEventType.AUTO_ALERT_AUTHORIZED)
