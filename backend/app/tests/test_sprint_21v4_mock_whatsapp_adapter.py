from fastapi.testclient import TestClient

from app.channel_adapters import (
    ChannelProvider,
    DeliveryStatus,
    MockWhatsAppAdapter,
    OutboundMessageKind,
    OutboundMessageRequest,
    WhatsAppChannelAdapter,
)
from app.event_model import BotEventType, EventModelService
from app.mock_whatsapp import MockWhatsAppInboundRequest, MockWhatsAppSimulatorService
from main import app


def test_mock_whatsapp_adapter_implements_contract_and_normalizes_payload():
    adapter = MockWhatsAppAdapter()
    inbound = adapter.normalize_inbound(
        {
            "providerMessageId": "mock-in-1",
            "from": "+5511999990001",
            "to": "+5511999990000",
            "body": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            "timestamp": "2026-06-05T22:00:00Z",
            "profileName": "Dona Lucia",
        }
    )

    assert isinstance(adapter, WhatsAppChannelAdapter)
    assert inbound.provider == ChannelProvider.MOCK
    assert inbound.provider_message_id == "mock-in-1"
    assert inbound.from_address == "+5511999990001"
    assert inbound.profile_name == "Dona Lucia"


def test_mock_whatsapp_adapter_registers_outbound_and_delivery_status():
    adapter = MockWhatsAppAdapter()
    outbound = adapter.send_guardian_alert(
        OutboundMessageRequest(
            provider=ChannelProvider.MOCK,
            to="+5511888880001",
            body="Alerta simulado.",
            kind=OutboundMessageKind.GUARDIAN_ALERT,
        )
    )
    delivered = adapter.parse_status_callback(
        {
            "providerMessageId": outbound.provider_message_id,
            "status": "delivered",
            "timestamp": "2026-06-05T22:01:00Z",
        }
    )

    assert outbound.provider_message_id.startswith("mock-guardian-")
    assert outbound.status == DeliveryStatus.PENDING
    assert outbound.simulated is True
    assert delivered.status == DeliveryStatus.DELIVERED


def test_false_relative_fixture_creates_case_and_notifies_guardian():
    service = MockWhatsAppSimulatorService(event_model=EventModelService.in_memory())
    response = service.simulate_fixture("false_relative_pix")

    assert response.case_created is True
    assert response.guardian_notified is True
    assert response.risk_level == "high"
    assert response.risk_score is not None and response.risk_score >= 70
    assert response.outbound_messages[0].status == "delivered"
    assert response.events == [
        BotEventType.MESSAGE_RECEIVED.value,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED.value,
        BotEventType.RISK_ASSESSMENT_CREATED.value,
        BotEventType.CASE_CREATED.value,
        BotEventType.RESPONSIBLE_ALERT_QUEUED.value,
        BotEventType.RESPONSIBLE_NOTIFIED.value,
        BotEventType.DELIVERY_STATUS_UPDATED.value,
    ]


def test_normal_message_does_not_create_case_or_notify_guardian():
    service = MockWhatsAppSimulatorService(event_model=EventModelService.in_memory())
    response = service.simulate_fixture("normal_message")

    assert response.case_created is False
    assert response.guardian_notified is False
    assert response.risk_score == 0
    assert response.outbound_messages == []
    assert response.events == [
        BotEventType.MESSAGE_RECEIVED.value,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED.value,
        BotEventType.RISK_ASSESSMENT_CREATED.value,
    ]


def test_duplicate_provider_message_id_does_not_create_second_case_or_alert():
    service = MockWhatsAppSimulatorService(event_model=EventModelService.in_memory())
    request = MockWhatsAppInboundRequest(
        providerMessageId="mock-duplicate-001",
        body="Troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
    )

    first = service.simulate_inbound(request)
    duplicate = service.simulate_inbound(request)

    assert first.case_created is True
    assert first.guardian_notified is True
    assert duplicate.duplicate is True
    assert duplicate.case_created is False
    assert duplicate.guardian_notified is False
    assert len(service.event_model.repositories.messages.list_all()) == 1
    assert len(service.event_model.repositories.cases.list_all()) == 1


def test_link_and_code_fixtures_create_cases_with_mock_alerts():
    service = MockWhatsAppSimulatorService(event_model=EventModelService.in_memory())
    link = service.simulate_fixture("suspicious_link_urgency")
    code = service.simulate_fixture("code_password_pressure")

    assert link.case_created is True
    assert link.risk_level == "medium"
    assert link.guardian_notified is True
    assert code.case_created is True
    assert code.risk_level == "high"
    assert code.guardian_notified is True


def test_mock_whatsapp_api_exposes_fixtures_simulation_and_state():
    client = TestClient(app)

    fixtures = client.get("/mock-whatsapp/fixtures")
    assert fixtures.status_code == 200
    assert len(fixtures.json()["fixtures"]) >= 4

    simulation = client.post(
        "/mock-whatsapp/simulate-inbound",
        json={
            "providerMessageId": "api-mock-false-relative-001",
            "from": "+5511999990001",
            "to": "+5511999990000",
            "body": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            "protected_person_alias": "Dona Lucia",
            "guardian_alias": "Gabriel",
            "guardian_address": "+5511888880001",
        },
    )
    assert simulation.status_code == 200
    body = simulation.json()
    assert body["case_created"] is True
    assert body["guardian_notified"] is True
    assert "ResponsibleNotified" in body["events"]

    state = client.get("/mock-whatsapp/simulations")
    assert state.status_code == 200
    assert state.json()["total"] >= 1
