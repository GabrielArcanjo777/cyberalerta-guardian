from __future__ import annotations

from typing import Any, Mapping

from app.channel_adapters.evolution_demo_adapter import (
    EvolutionDemoAdapter,
    EvolutionDemoConfig,
)
from app.event_model import BotEventType, EventModelService
from app.evolution_demo import EvolutionDemoService
from app.hybrid.models import HybridDecisionContext
from app.hybrid.policy import HybridDecisionPolicy
from app.hybrid.service import HybridAnalysisService
from app.llm.models import (
    EvidenceStrength,
    LLMClassification,
    LLMScamAnalysisResult,
    ObjectiveEvidence,
    ScamType,
)
from app.llm.providers.mock_provider import MockLLMProvider
from app.llm.service import LLMAnalysisService

SENDER = "5511999990001"
TRUSTED = "5511888880001"


class FakeEvolutionTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def send_text(self, *, api_url, api_key, instance_name, to_address, body) -> Mapping[str, Any]:
        self.calls.append({"to_address": to_address, "body": body})
        return {"status": "ok"}


def _config() -> EvolutionDemoConfig:
    return EvolutionDemoConfig(
        api_url="http://evolution.local",
        api_key="local-demo-key",
        instance_name="guardian-demo",
        guardian_address=TRUSTED,
        dry_run=False,
        real_send_enabled=True,
        require_allowed_recipient=False,
    )


def _scam_llm() -> LLMScamAnalysisResult:
    return LLMScamAnalysisResult(
        classification=LLMClassification.SCAM,
        confidence=0.92,
        risk_score=88,
        scam_types=[ScamType.FAMILY_IMPERSONATION, ScamType.PIX_FRAUD],
        impersonated_entities=["filho"],
        objective_evidence=[
            ObjectiveEvidence(signal="PIX", excerpt="pix", strength=EvidenceStrength.HIGH)
        ],
    )


def _hybrid(*, llm_result=None, enabled=True, shadow=False):
    provider = MockLLMProvider(result=llm_result) if llm_result is not None else None
    llm_service = LLMAnalysisService(provider=provider, enabled=enabled)
    ctx = HybridDecisionContext(
        llm_enabled=enabled, shadow_mode=shadow, require_llm_for_auto_alert=True
    )
    return HybridAnalysisService(
        llm_service=llm_service, policy=HybridDecisionPolicy(), context=ctx
    )


def _service(hybrid, transport):
    return EvolutionDemoService(
        adapter=EvolutionDemoAdapter(config=_config(), transport=transport),
        event_model=EventModelService.in_memory(),
        hybrid_service=hybrid,
    )


def _upsert(message_id: str = "EVOIN001", body: str | None = None) -> dict[str, Any]:
    return {
        "event": "MESSAGES_UPSERT",
        "instance": "guardian-demo",
        "data": {
            "key": {"id": message_id, "remoteJid": f"{SENDER}@s.whatsapp.net", "fromMe": False},
            "pushName": "Dona Lucia",
            "messageTimestamp": 1780000000,
            "message": {
                "conversation": body
                or "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora."
            },
        },
    }


def test_full_hybrid_flow_auto_alert_reaches_only_trusted_contact():
    transport = FakeEvolutionTransport()
    service = _service(_hybrid(llm_result=_scam_llm(), enabled=True, shadow=False), transport)

    response = service.handle_webhook(_upsert("EVOIN010"))

    assert response.case_created is True
    assert response.guardian_notified is True
    # Exactly one outbound, and it goes to the trusted contact — never the sender.
    assert len(transport.calls) == 1
    assert transport.calls[0]["to_address"] == TRUSTED
    assert transport.calls[0]["to_address"] != SENDER
    # Hybrid audit trail persisted, with a real (non-shadow) authorization.
    assert BotEventType.DETERMINISTIC_ASSESSMENT_CREATED.value in response.events
    assert BotEventType.LLM_ANALYSIS_COMPLETED.value in response.events
    assert BotEventType.HYBRID_DECISION_CREATED.value in response.events
    assert BotEventType.AUTO_ALERT_AUTHORIZED.value in response.events


def test_hybrid_review_does_not_alert_when_llm_unavailable():
    transport = FakeEvolutionTransport()
    # LLM enabled but no provider => unavailable; require_llm caps at REVIEW.
    service = _service(_hybrid(llm_result=None, enabled=True, shadow=False), transport)

    response = service.handle_webhook(_upsert("EVOIN011"))

    # High deterministic score still creates a case, but no auto-alert fires.
    assert response.case_created is True
    assert transport.calls == []
    assert response.guardian_notified is False
    assert BotEventType.REVIEW_QUEUED.value in response.events
    assert BotEventType.AUTO_ALERT_AUTHORIZED.value not in response.events


def test_hybrid_never_sends_to_sender_even_on_scam():
    transport = FakeEvolutionTransport()
    service = _service(_hybrid(llm_result=_scam_llm(), enabled=True, shadow=False), transport)
    service.handle_webhook(_upsert("EVOIN012"))
    for call in transport.calls:
        assert call["to_address"] != SENDER


def test_safety_gate_blocks_real_send_in_dry_run(monkeypatch):
    # Same scam, but a DRY_RUN adapter must simulate (no network transport call).
    transport = FakeEvolutionTransport()
    dry_config = EvolutionDemoConfig(
        api_url="http://evolution.local",
        api_key="local-demo-key",
        instance_name="guardian-demo",
        guardian_address=TRUSTED,
        dry_run=True,
        real_send_enabled=False,
        require_allowed_recipient=True,
    )
    service = EvolutionDemoService(
        adapter=EvolutionDemoAdapter(config=dry_config, transport=transport),
        event_model=EventModelService.in_memory(),
        hybrid_service=_hybrid(llm_result=_scam_llm(), enabled=True, shadow=False),
    )
    response = service.handle_webhook(_upsert("EVOIN013"))
    # Decision may authorize, but the safety gate prevents any real network send.
    assert transport.calls == []
    assert BotEventType.AUTO_ALERT_AUTHORIZED.value in response.events


def test_hybrid_decision_is_queryable_for_case():
    from app.hybrid.query import get_hybrid_decision_for_case

    transport = FakeEvolutionTransport()
    service = _service(_hybrid(llm_result=_scam_llm(), enabled=True, shadow=False), transport)
    response = service.handle_webhook(_upsert("EVOIN020"))

    decision = get_hybrid_decision_for_case(service.event_model, response.case_id)
    assert decision is not None
    assert decision["action"] == "AUTO_ALERT"
    assert decision["policy_version"] == "v1"
    assert "content_hash" in decision
    # never leaks raw content or secrets
    assert "api_key" not in decision and "prompt" not in decision


def test_shadow_mode_keeps_legacy_behavior():
    # Shadow + enabled: records the decision but alerting stays on the legacy
    # deterministic HIGH rule (still notifies for this HIGH message).
    transport = FakeEvolutionTransport()
    service = _service(_hybrid(llm_result=_scam_llm(), enabled=True, shadow=True), transport)
    response = service.handle_webhook(_upsert("EVOIN014"))
    assert response.guardian_notified is True
    assert transport.calls[0]["to_address"] == TRUSTED
    assert BotEventType.HYBRID_SHADOW_DECISION_CREATED.value in response.events
    # In shadow, an AUTO_ALERT intent is recorded as blocked, not authorized.
    assert BotEventType.AUTO_ALERT_BLOCKED.value in response.events
    assert BotEventType.AUTO_ALERT_AUTHORIZED.value not in response.events
