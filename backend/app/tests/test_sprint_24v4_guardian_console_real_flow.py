from __future__ import annotations

from fastapi.testclient import TestClient

from app.dual_bot import DualBotFlowService, DualBotInboundRequest, GuardianFeedbackRequest
from app.event_model import BotEventType, CaseStatus, EventModelService
from app.guardian_console import GuardianConsoleRealFlowService
from main import app


def _create_case(service: DualBotFlowService, message_id: str = "console-real-001"):
    return service.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId=message_id,
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )


def test_real_console_status_starts_empty_with_active_dual_bot_state():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    console = GuardianConsoleRealFlowService(dual_bot)

    status = console.get_status()
    cases = console.list_cases()

    assert status.service == "guardian-console-real-flow"
    assert status.case_count == 0
    assert status.activation.protected_bot.active is True
    assert status.activation.responsible_bot.active is True
    assert status.activation.channel_provider == "mock"
    assert status.activation.simulated is True
    assert cases.total == 0
    assert cases.cases == []


def test_real_console_lists_case_created_by_dual_bot_flow():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = _create_case(dual_bot)
    console = GuardianConsoleRealFlowService(dual_bot)

    listed = console.list_cases()
    detail = console.get_case_detail(flow.case_id)

    assert listed.total == 1
    assert listed.cases[0].case_id == flow.case_id
    assert listed.cases[0].protected_person_alias == "Dona Lucia"
    assert listed.cases[0].guardian_alias == "Gabriel"
    assert listed.cases[0].source_channel == "whatsapp:mock"
    assert listed.cases[0].risk_level == "high"
    assert listed.cases[0].alert_delivered is True
    assert detail.source_message.startswith("Mae, troquei de numero")
    assert detail.guardian_alert.status == "delivered"
    assert detail.delivery.guardian_notified is True
    assert detail.pattern is not None
    assert detail.pattern.score > 0
    assert "false_relative" in detail.pattern.signals
    assert detail.feedback_actions == ["confirm_scam", "false_alarm", "needs_review", "mark_resolved"]
    assert BotEventType.CASE_CREATED.value in [event.event_type for event in detail.timeline]
    assert BotEventType.RESPONSIBLE_NOTIFIED.value in [event.event_type for event in detail.timeline]


def test_real_console_feedback_updates_case_and_adds_timeline_event():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = _create_case(dual_bot, "console-real-feedback-001")
    console = GuardianConsoleRealFlowService(dual_bot)

    feedback = console.record_feedback(
        flow.case_id,
        GuardianFeedbackRequest(action="false_alarm", guardian_alias="Gabriel"),
    )
    detail = console.get_case_detail(flow.case_id)

    assert feedback.previous_status == CaseStatus.NEW.value
    assert feedback.new_status == CaseStatus.FALSE_ALARM.value
    assert detail.status == CaseStatus.FALSE_ALARM.value
    assert detail.false_positive is True
    assert detail.guardian_confirmed is False
    assert detail.resolved is False
    timeline_types = [event.event_type for event in detail.timeline]
    assert BotEventType.GUARDIAN_FEEDBACK_RECEIVED.value in timeline_types
    assert detail.timeline[-1].event_type == BotEventType.FALSE_POSITIVE_MARKED.value
    feedback_event = next(
        event
        for event in detail.timeline
        if event.event_type == BotEventType.GUARDIAN_FEEDBACK_RECEIVED.value
    )
    assert feedback_event.metadata["action"] == "false_alarm"


def test_real_console_api_flow_can_be_demonstrated_end_to_end():
    client = TestClient(app)

    inbound = client.post(
        "/dual-bot/mock/protected-message",
        json={
            "providerMessageId": "console-real-api-001",
            "body": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            "protected_person_alias": "Dona Lucia",
            "guardian_alias": "Gabriel",
            "guardian_address": "+5511888880001",
        },
    )
    assert inbound.status_code == 200
    case_id = inbound.json()["case_id"]

    status = client.get("/guardian-console/real/status")
    assert status.status_code == 200
    assert status.json()["case_count"] >= 1
    assert status.json()["consent"]["status"] in {"pending", "active", "bot_disabled", "revoked"}
    assert status.json()["activation"]["protected_bot"]["active"] == status.json()["consent"]["bot_active"]

    cases = client.get("/guardian-console/real/cases")
    assert cases.status_code == 200
    assert any(item["case_id"] == case_id for item in cases.json()["cases"])

    detail = client.get(f"/guardian-console/real/cases/{case_id}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["risk_signals"] == [
        "urgency",
        "pix_or_payment",
        "new_number",
        "do_not_call",
    ]
    assert detail_body["delivery"]["guardian_alert_status"] == "delivered"
    assert detail_body["pattern"]["score"] > 0
    assert "false_relative" in detail_body["pattern"]["signals"]
    assert len(detail_body["timeline"]) >= 8

    feedback = client.post(
        f"/guardian-console/real/cases/{case_id}/feedback",
        json={"action": "confirm_scam", "guardian_alias": "Gabriel"},
    )
    assert feedback.status_code == 200
    assert feedback.json()["new_status"] == CaseStatus.CONFIRMED_SCAM.value

    updated = client.get(f"/guardian-console/real/cases/{case_id}")
    assert updated.status_code == 200
    assert updated.json()["guardian_confirmed"] is True
