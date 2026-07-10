from __future__ import annotations

from typing import Any, Mapping

from fastapi.testclient import TestClient

from app.channel_adapters import ChannelProvider, EvolutionDemoAdapter, EvolutionDemoConfig
from app.dual_bot import (
    DualBotFlowService,
    DualBotInboundRequest,
    GuardianFeedbackAction,
    GuardianFeedbackRequest,
)
from app.dual_bot.messages import responsible_alert_for
from app.dual_bot.services import create_dual_bot_adapter
from app.event_model import BotEventType, CaseStatus, EventModelService
from main import app


class FakeEvolutionTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def send_text(
        self,
        *,
        api_url: str,
        api_key: str,
        instance_name: str,
        to_address: str,
        body: str,
    ) -> Mapping[str, Any]:
        self.calls.append(
            {
                "api_url": api_url,
                "api_key": api_key,
                "instance_name": instance_name,
                "to_address": to_address,
                "body": body,
            }
        )
        return {"messageId": f"EVO-DUAL-OUT-{len(self.calls)}"}


def _suspicious_request(message_id: str = "dual-bot-v5-001") -> DualBotInboundRequest:
    return DualBotInboundRequest(
        providerMessageId=message_id,
        body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
        protected_person_alias="Maria",
        guardian_alias="Gabriel",
        guardian_address="+5511888880001",
    )


def _evolution_payload(message_id: str = "EVO-DUAL-IN-001") -> dict[str, Any]:
    return {
        "event": "MESSAGES_UPSERT",
        "instance": "guardian-demo",
        "data": {
            "key": {
                "id": message_id,
                "remoteJid": "5511999990001@s.whatsapp.net",
                "fromMe": False,
            },
            "pushName": "Maria",
            "messageTimestamp": 1780000000,
            "message": {
                "conversation": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora."
            },
        },
    }


def test_v5_mock_dual_bot_flow_generates_required_events_and_messages():
    service = DualBotFlowService(event_model=EventModelService.in_memory())

    response = service.receive_mock_message(_suspicious_request())

    assert response.case_created is True
    # The bot never replies to the sender; only the trusted contact is alerted.
    assert response.guardian_alert is not None
    assert "Alerta Guardian: Maria" in response.guardian_alert.body
    assert "Risco: alto" in response.guardian_alert.body
    assert "Pix ou pagamento" in response.guardian_alert.body
    for event_type in {
        BotEventType.MESSAGE_RECEIVED.value,
        BotEventType.RISK_ASSESSMENT_CREATED.value,
        BotEventType.CASE_CREATED.value,
        BotEventType.RESPONSIBLE_ALERT_QUEUED.value,
        BotEventType.RESPONSIBLE_NOTIFIED.value,
    }:
        assert event_type in response.events
    # No message is ever generated toward the protected person / sender.
    assert BotEventType.SAFE_REPLY_SENT.value not in response.events
    assert BotEventType.PROTECTED_PERSON_REPLIED.value not in response.events


def test_v5_responsible_feedback_records_false_positive_and_resolved_events():
    service = DualBotFlowService(event_model=EventModelService.in_memory())
    false_positive_flow = service.receive_mock_message(_suspicious_request("dual-bot-v5-fp"))
    assert false_positive_flow.case_id is not None

    false_positive = service.record_guardian_feedback(
        false_positive_flow.case_id,
        GuardianFeedbackRequest(
            action=GuardianFeedbackAction.FALSE_ALARM,
            guardian_alias="Gabriel",
            note="Confirmado por ligacao direta.",
        ),
    )

    assert false_positive.new_status == CaseStatus.FALSE_ALARM.value
    assert service.event_model.repositories.events.list_by_type(BotEventType.FALSE_POSITIVE_MARKED)

    resolved_flow = service.receive_mock_message(_suspicious_request("dual-bot-v5-resolved"))
    assert resolved_flow.case_id is not None
    resolved = service.record_guardian_feedback(
        resolved_flow.case_id,
        GuardianFeedbackRequest(action=GuardianFeedbackAction.MARK_RESOLVED),
    )

    assert resolved.new_status == CaseStatus.RESOLVED.value
    assert service.event_model.repositories.events.list_by_type(BotEventType.CASE_RESOLVED)


def test_v5_case_context_is_history_for_responsible_bot():
    service = DualBotFlowService(event_model=EventModelService.in_memory())
    response = service.receive_mock_message(_suspicious_request("dual-bot-v5-history"))
    assert response.case_id is not None

    context = service.get_case_context(response.case_id)

    assert context.protected_person_alias == "Maria"
    assert context.guardian_alias == "Gabriel"
    assert context.risk_level == "high"
    assert "Pix urgente" in context.message_summary
    assert BotEventType.CASE_CREATED.value in [event.event_type for event in context.history]


def test_v5_dual_bot_prepares_evolution_demo_provider_through_contract():
    transport = FakeEvolutionTransport()
    adapter = EvolutionDemoAdapter(
        config=EvolutionDemoConfig(
            api_url="http://evolution.local",
            api_key="local-demo-key",
            instance_name="guardian-demo",
            guardian_address="5511888880001",
            dry_run=False,
            real_send_enabled=True,
            require_allowed_recipient=False,
        ),
        transport=transport,
    )
    service = DualBotFlowService(
        adapter=adapter,
        event_model=EventModelService.in_memory(),
        default_guardian_address="5511888880001",
    )

    response = service.receive_provider_message(payload=_evolution_payload())

    assert response.provider == ChannelProvider.EVOLUTION_DEMO.value
    assert response.case_created is True
    assert response.guardian_alert is not None
    # Exactly ONE outbound send: the alert to the trusted contact, never the sender.
    assert len(transport.calls) == 1
    assert transport.calls[0]["to_address"] == "5511888880001"
    assert BotEventType.SAFE_REPLY_SENT.value not in response.events
    assert BotEventType.RESPONSIBLE_NOTIFIED.value in response.events


def test_v5_provider_factory_and_status_endpoint_are_adapter_first():
    assert create_dual_bot_adapter("mock_whatsapp").provider == ChannelProvider.MOCK
    assert create_dual_bot_adapter("evolution_demo").provider == ChannelProvider.EVOLUTION_DEMO

    client = TestClient(app)
    status = client.get("/dual-bot/status")

    assert status.status_code == 200
    assert status.json()["adapter_first"] is True
    assert status.json()["production"] is False


def test_v5_provider_endpoint_runs_active_mock_flow():
    client = TestClient(app)

    response = client.post(
        "/dual-bot/provider/protected-message",
        json={
            "providerMessageId": "dual-bot-v5-provider-api",
            "from": "+5511999990001",
            "to": "+5511999990000",
            "body": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            "profileName": "Maria",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["case_created"] is True
    assert "ResponsibleNotified" in body["events"]
    assert "SafeReplySent" not in body["events"]


def test_v5_responsible_alert_template_uses_readable_context():
    body = responsible_alert_for(
        protected_person_alias="Maria",
        risk_level="high",
        signals=["pix_or_payment", "new_number", "do_not_call"],
        case_id="case-123",
        language="pt",
    )

    assert body == (
        "Alerta Guardian: Maria recebeu uma mensagem com sinais de golpe. Risco: alto. "
        "Sinais: Pix ou pagamento, numero novo, pedido para nao ligar. "
        "Caso case-123. Acesse o caso para revisar."
    )
