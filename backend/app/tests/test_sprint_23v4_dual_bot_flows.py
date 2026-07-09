from __future__ import annotations

from fastapi.testclient import TestClient

from app.dual_bot import (
    DualBotFlowService,
    DualBotInboundRequest,
    GuardianFeedbackAction,
    GuardianFeedbackRequest,
)
from app.event_model import BotEventType, CaseStatus, EventModelService
from main import app


def _suspicious_request(message_id: str = "dual-bot-mock-001") -> DualBotInboundRequest:
    return DualBotInboundRequest(
        providerMessageId=message_id,
        body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
        protected_person_alias="Dona Lucia",
        guardian_alias="Gabriel",
        guardian_address="+5511888880001",
    )


def test_protected_bot_suspicious_message_creates_case_and_alerts_trusted_contact():
    service = DualBotFlowService(event_model=EventModelService.in_memory())

    response = service.receive_mock_message(_suspicious_request())

    assert response.duplicate is False
    assert response.case_created is True
    assert response.risk_score == 90
    assert response.risk_level == "high"
    assert response.risk_signals == [
        "urgency",
        "pix_or_payment",
        "new_number",
        "do_not_call",
    ]
    # Only the trusted contact is messaged; nothing goes back to the sender.
    assert response.guardian_alert is not None
    assert response.guardian_alert.kind == "guardian_alert"
    assert "Risco: alto" in response.guardian_alert.body
    assert "Dona Lucia" in response.guardian_alert.body
    expected_events = [
        BotEventType.MESSAGE_RECEIVED.value,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED.value,
        BotEventType.RISK_ASSESSMENT_CREATED.value,
        BotEventType.CASE_CREATED.value,
        BotEventType.RESPONSIBLE_ALERT_QUEUED.value,
        BotEventType.PATTERN_CANDIDATE_DETECTED.value,
        BotEventType.DELIVERY_STATUS_UPDATED.value,
        BotEventType.RESPONSIBLE_NOTIFIED.value,
    ]
    for event_type in expected_events:
        assert event_type in response.events
    assert BotEventType.SAFE_REPLY_SENT.value not in response.events
    assert BotEventType.PROTECTED_PERSON_REPLIED.value not in response.events


def test_low_risk_message_produces_no_outbound_and_no_case():
    service = DualBotFlowService(event_model=EventModelService.in_memory())
    response = service.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="dual-bot-low-001",
            body="Oi, tudo bem?",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )

    assert response.case_created is False
    assert response.case_id is None
    assert response.risk_score == 0
    # Low risk: analyzed and stored only. Nobody is messaged.
    assert response.guardian_alert is None
    assert BotEventType.SAFE_REPLY_SENT.value not in response.events
    assert BotEventType.RESPONSIBLE_NOTIFIED.value not in response.events
    assert BotEventType.MESSAGE_RECEIVED.value in response.events
    assert BotEventType.RISK_ASSESSMENT_CREATED.value in response.events


def test_duplicate_provider_message_does_not_send_second_alert():
    service = DualBotFlowService(event_model=EventModelService.in_memory())
    request = _suspicious_request("dual-bot-duplicate-001")

    first = service.receive_mock_message(request)
    duplicate = service.receive_mock_message(request)

    assert first.case_created is True
    assert duplicate.duplicate is True
    assert duplicate.case_created is False
    assert duplicate.guardian_alert is None
    assert len(service.event_model.repositories.messages.list_all()) == 1
    assert len(service.event_model.repositories.cases.list_all()) == 1


def test_responsible_bot_context_contains_risk_signals_message_and_history():
    service = DualBotFlowService(event_model=EventModelService.in_memory())
    response = service.receive_mock_message(_suspicious_request("dual-bot-context-001"))
    assert response.case_id is not None

    context = service.get_case_context(response.case_id)

    assert context.case_id == response.case_id
    assert context.status == CaseStatus.NEW.value
    assert context.protected_person_alias == "Dona Lucia"
    assert context.guardian_alias == "Gabriel"
    assert context.risk_score == 90
    assert "Pix urgente" in context.message_summary
    assert "do_not_call" in context.risk_signals
    assert BotEventType.CASE_CREATED.value in [event.event_type for event in context.history]


def test_responsible_feedback_updates_case_status_and_records_audit_event():
    service = DualBotFlowService(event_model=EventModelService.in_memory())
    response = service.receive_mock_message(_suspicious_request("dual-bot-feedback-001"))
    assert response.case_id is not None

    feedback = service.record_guardian_feedback(
        response.case_id,
        GuardianFeedbackRequest(
            action=GuardianFeedbackAction.CONFIRM_SCAM,
            guardian_alias="Gabriel",
            note="Confirmado por ligacao direta.",
        ),
    )
    updated_case = service.event_model.cases.get_case_by_id(response.case_id)
    events = service.event_model.repositories.events.list_by_type(
        BotEventType.GUARDIAN_FEEDBACK_RECEIVED
    )

    assert feedback.previous_status == CaseStatus.NEW.value
    assert feedback.new_status == CaseStatus.CONFIRMED_SCAM.value
    assert feedback.audit_event == BotEventType.GUARDIAN_FEEDBACK_RECEIVED.value
    assert updated_case.status == CaseStatus.CONFIRMED_SCAM
    assert events[-1].payload["action"] == GuardianFeedbackAction.CONFIRM_SCAM.value
    assert events[-1].payload["note"] == "Confirmado por ligacao direta."


def test_feedback_actions_map_to_expected_case_statuses():
    expected = {
        GuardianFeedbackAction.FALSE_ALARM: CaseStatus.FALSE_ALARM,
        GuardianFeedbackAction.NEEDS_REVIEW: CaseStatus.UNDER_REVIEW,
        GuardianFeedbackAction.MARK_RESOLVED: CaseStatus.RESOLVED,
    }
    for index, (action, status) in enumerate(expected.items()):
        service = DualBotFlowService(event_model=EventModelService.in_memory())
        response = service.receive_mock_message(_suspicious_request(f"dual-bot-action-{index}"))
        assert response.case_id is not None

        service.record_guardian_feedback(
            response.case_id,
            GuardianFeedbackRequest(action=action),
        )

        assert service.event_model.cases.get_case_by_id(response.case_id).status == status


def test_dual_bot_api_runs_flow_context_and_feedback():
    client = TestClient(app)

    inbound = client.post(
        "/dual-bot/mock/protected-message",
        json={
            "providerMessageId": "dual-bot-api-001",
            "body": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            "protected_person_alias": "Dona Lucia",
            "guardian_alias": "Gabriel",
            "guardian_address": "+5511888880001",
        },
    )
    assert inbound.status_code == 200
    inbound_body = inbound.json()
    assert inbound_body["case_created"] is True
    assert inbound_body["guardian_alert"]["kind"] == "guardian_alert"

    context = client.get(f"/dual-bot/cases/{inbound_body['case_id']}/context")
    assert context.status_code == 200
    assert context.json()["risk_level"] == "high"

    feedback = client.post(
        f"/dual-bot/cases/{inbound_body['case_id']}/feedback",
        json={"action": "false_alarm", "guardian_alias": "Gabriel"},
    )
    assert feedback.status_code == 200
    assert feedback.json()["new_status"] == CaseStatus.FALSE_ALARM.value
