"""End-to-end validation for STORE_FULL_MESSAGE=false in the event model.

Proves that:
- message body is redacted on disk
- body_hash + body_preview are populated
- risk assessment still works on the full text (same message_id)
- case creation still links correctly to the message
- dual-bot context uses the redacted view
- /analyze still returns the same risk result
"""
from __future__ import annotations

import pytest

from app.core.config import config
from app.event_model import EventModelService, Guardian, ProtectedPerson
from app.schemas.analysis import AnalysisRequest


@pytest.fixture(autouse=True)
def _force_redaction(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "store_full_message", False, raising=False)


def test_event_model_redacts_body_but_keeps_analysis_flow() -> None:
    service = EventModelService.in_memory()
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        guardian=Guardian(alias="Gabriel"),
        body=(
            "Urgente: troquei de numero. Faca um Pix agora, nao liga. "
            "Abra https://exemplo.invalid e informe o codigo."
        ),
    )

    stored = service.repositories.messages.get(result.message.message_id)
    assert stored is not None
    assert stored.body == "[REDACTED]"
    assert stored.body_hash
    assert stored.body_preview
    assert result.message.message_id == stored.message_id

    assert result.risk_assessment.score == 100
    assert result.risk_assessment.case_threshold_reached is True
    assert result.case is not None
    assert result.case.risk_assessment_id == result.risk_assessment.risk_assessment_id

    events = service.repositories.events.list_all()
    assert [event.event_type for event in events] == [
        "MessageReceived",
        "SuspiciousMessageReceived",
        "RiskAssessmentCreated",
        "CaseCreated",
        "ResponsibleAlertQueued",
    ]


def test_dual_bot_context_uses_redacted_summary() -> None:
    from app.dual_bot import DualBotFlowService
    from app.dual_bot.models import DualBotInboundRequest

    service = DualBotFlowService(event_model=EventModelService.in_memory())
    request = DualBotInboundRequest(
        provider_message_id="redaction-context-001",
        from_address="+5511999990001",
        body="Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
        profile_name="Dona Lucia",
        channel="whatsapp",
    )
    flow = service.receive_mock_message(request)
    assert flow.case_id is not None

    context = service.get_case_context(flow.case_id)
    assert context.source_message == "[REDACTED]"
    assert context.message_summary == "[REDACTED]"
    assert "Pix urgente" not in context.message_summary
    assert context.risk_score >= 40


def test_analyze_endpoint_still_works_under_redaction() -> None:
    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.post(
        "/analyze",
        json={
            "user_name": "Dona Lucia",
            "age_group": "elderly",
            "trusted_contact_name": "Gabriel",
            "trusted_contact_relation": "filho",
            "action_type": "pix",
            "channel": "whatsapp",
            "message": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
            "already_acted": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["risk_score"] >= 40
    assert body["risk_level"] in {"medium", "high", "critical"}
