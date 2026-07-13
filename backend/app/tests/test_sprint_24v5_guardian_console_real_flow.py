from __future__ import annotations

from fastapi.testclient import TestClient

from app.dual_bot import DualBotFlowService, DualBotInboundRequest, GuardianFeedbackRequest
from app.event_model import BotEventType, CaseStatus, EventModelService
from app.guardian_console import GuardianConsoleRealFlowService
from main import app


def _create_case(service: DualBotFlowService, message_id: str = "console-v5-001"):
    return service.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId=message_id,
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )


def test_v5_console_detail_exposes_operational_entities():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = _create_case(dual_bot)
    console = GuardianConsoleRealFlowService(dual_bot)

    detail = console.get_case_detail(flow.case_id)

    assert detail.protected_person.alias == "Dona Lucia"
    assert detail.responsible_contact.alias == "Gabriel"
    assert detail.responsible_contact.notified is True
    assert detail.case.case_id == flow.case_id
    assert detail.case.source_message_id == flow.message_id
    assert detail.case.risk_assessment_id == flow.risk_assessment_id
    assert detail.case.open is True
    assert detail.message.body == "[REDACTED]"
    assert detail.message.channel == "whatsapp:mock"
    assert detail.message.simulated is True
    assert detail.risk_assessment.score == detail.risk_score
    assert detail.risk_assessment.case_threshold_reached is True
    assert detail.channel_status.provider == "mock"
    assert detail.channel_status.simulated is True
    assert detail.channel_status.guardian_notified is True
    assert detail.channel_status.environment_label == "mock local / in-memory"
    assert detail.next_step == detail.recommended_action
    assert detail.environment_label == "mock local / in-memory"
    assert len(detail.bot_events) == len(detail.timeline)

    event_types = [event.event_type for event in detail.timeline]
    assert BotEventType.MESSAGE_RECEIVED.value in event_types
    assert BotEventType.RISK_ASSESSMENT_CREATED.value in event_types
    assert BotEventType.CASE_CREATED.value in event_types
    assert BotEventType.RESPONSIBLE_NOTIFIED.value in event_types
    assert BotEventType.SAFE_REPLY_SENT.value not in event_types

    audit_actions = [entry.action for entry in detail.audit_log]
    assert BotEventType.MESSAGE_RECEIVED.value in audit_actions
    assert BotEventType.CASE_CREATED.value in audit_actions
    assert BotEventType.RESPONSIBLE_NOTIFIED.value in audit_actions


def test_v5_console_feedback_and_resolution_are_auditable():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = _create_case(dual_bot, "console-v5-feedback-001")
    console = GuardianConsoleRealFlowService(dual_bot)

    feedback = console.record_feedback(
        flow.case_id,
        GuardianFeedbackRequest(
            action="mark_resolved",
            guardian_alias="Gabriel",
            note="Responsavel confirmou por canal independente e encerrou.",
        ),
    )
    detail = console.get_case_detail(flow.case_id)

    assert feedback.previous_status == CaseStatus.NEW.value
    assert feedback.new_status == CaseStatus.RESOLVED.value
    assert detail.status == CaseStatus.RESOLVED.value
    assert detail.case.status == CaseStatus.RESOLVED.value
    assert detail.case.open is False
    assert detail.feedback.latest_action == "mark_resolved"
    assert detail.feedback.latest_actor == "Gabriel"
    assert detail.feedback.latest_event_id == feedback.event_id
    assert detail.feedback.resolved is True
    assert detail.resolved is True

    event_types = [event.event_type for event in detail.timeline]
    assert BotEventType.GUARDIAN_FEEDBACK_RECEIVED.value in event_types
    assert BotEventType.CASE_RESOLVED.value in event_types
    assert feedback.event_id in [entry.event_id for entry in detail.audit_log]


def test_v5_console_api_flow_exposes_case_data_and_feedback_updates():
    client = TestClient(app)

    inbound = client.post(
        "/dual-bot/mock/protected-message",
        json={
            "providerMessageId": "console-v5-api-001",
            "body": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            "protected_person_alias": "Dona Lucia",
            "guardian_alias": "Gabriel",
            "guardian_address": "+5511888880001",
        },
    )
    assert inbound.status_code == 200
    case_id = inbound.json()["case_id"]

    cases = client.get("/guardian-console/real/cases")
    assert cases.status_code == 200
    assert any(item["case_id"] == case_id for item in cases.json()["cases"])

    detail = client.get(f"/guardian-console/real/cases/{case_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["protected_person"]["alias"] == "Dona Lucia"
    assert body["responsible_contact"]["alias"] == "Gabriel"
    assert body["case"]["case_id"] == case_id
    assert body["message"]["channel"] == "whatsapp:mock"
    assert body["risk_assessment"]["score"] == body["risk_score"]
    assert body["channel_status"]["guardian_notified"] is True
    assert body["feedback"]["latest_action"] is None
    assert len(body["timeline"]) >= 8
    assert len(body["audit_log"]) >= 8

    feedback = client.post(
        f"/guardian-console/real/cases/{case_id}/feedback",
        json={
            "action": "false_alarm",
            "guardian_alias": "Gabriel",
            "note": "Responsavel reconheceu mensagem legitima depois da verificacao.",
        },
    )
    assert feedback.status_code == 200
    assert feedback.json()["new_status"] == CaseStatus.FALSE_ALARM.value

    updated = client.get(f"/guardian-console/real/cases/{case_id}")
    assert updated.status_code == 200
    updated_body = updated.json()
    assert updated_body["feedback"]["latest_action"] == "false_alarm"
    assert updated_body["feedback"]["false_positive"] is True
    assert updated_body["false_positive"] is True
    assert BotEventType.FALSE_POSITIVE_MARKED.value in [
        item["event_type"] for item in updated_body["timeline"]
    ]
