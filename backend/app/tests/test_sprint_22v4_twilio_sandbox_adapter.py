from __future__ import annotations

from typing import Mapping

from fastapi.testclient import TestClient

from app.channel_adapters import (
    ChannelProvider,
    DeliveryStatus,
    TwilioSandboxConfig,
    TwilioSandboxWhatsAppAdapter,
    TwilioSignatureContext,
    WhatsAppChannelAdapter,
)
from app.event_model import BotEventType, EventModelService
from app.twilio_sandbox import TwilioSandboxService
from main import app


class FakeTwilioTransport:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def send_message(
        self,
        *,
        account_sid: str,
        auth_token: str,
        from_address: str,
        to_address: str,
        body: str,
        status_callback_url: str | None = None,
    ) -> Mapping[str, str]:
        self.calls.append(
            {
                "account_sid": account_sid,
                "auth_token": auth_token,
                "from": from_address,
                "to": to_address,
                "body": body,
                "status_callback_url": status_callback_url,
            }
        )
        return {"sid": f"SMOUT{len(self.calls):03d}", "status": "queued"}


def _twilio_config(*, validate_signature: bool = False) -> TwilioSandboxConfig:
    return TwilioSandboxConfig(
        account_sid="ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        auth_token="sandbox-auth-token",
        whatsapp_from="whatsapp:+14155238886",
        webhook_secret="sandbox-webhook-secret",
        status_callback_url="https://example.test/api/channels/twilio/whatsapp/status",
        guardian_address="whatsapp:+5511888880001",
        validate_signature=validate_signature,
    )


def _suspicious_twilio_payload(message_sid: str = "SMIN001") -> dict[str, str]:
    return {
        "MessageSid": message_sid,
        "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "From": "whatsapp:+5511999990001",
        "To": "whatsapp:+14155238886",
        "Body": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
        "ProfileName": "Dona Lucia",
        "NumMedia": "0",
    }


def test_twilio_sandbox_adapter_normalizes_inbound_payload():
    adapter = TwilioSandboxWhatsAppAdapter(config=_twilio_config())
    inbound = adapter.normalize_inbound(
        {
            **_suspicious_twilio_payload(),
            "NumMedia": "1",
            "MediaUrl0": "https://api.twilio.test/media/ME123",
            "MediaContentType0": "image/jpeg",
        }
    )

    assert isinstance(adapter, WhatsAppChannelAdapter)
    assert inbound.provider == ChannelProvider.TWILIO_SANDBOX
    assert inbound.provider_message_id == "SMIN001"
    assert inbound.from_address == "whatsapp:+5511999990001"
    assert inbound.to_address == "whatsapp:+14155238886"
    assert inbound.profile_name == "Dona Lucia"
    assert inbound.media[0].media_type == "image/jpeg"
    assert inbound.raw["AccountSid"] == "<hidden>"


def test_twilio_sandbox_adapter_parses_delivery_status_and_retry():
    adapter = TwilioSandboxWhatsAppAdapter(config=_twilio_config())

    delivered = adapter.parse_status_callback(
        {"MessageSid": "SMOUT001", "MessageStatus": "delivered"}
    )
    failed_retryable = adapter.parse_status_callback(
        {"MessageSid": "SMOUT002", "MessageStatus": "undelivered", "ErrorCode": "30003"}
    )
    failed_terminal = adapter.parse_status_callback(
        {"MessageSid": "SMOUT003", "MessageStatus": "failed", "ErrorCode": "21610"}
    )

    assert delivered.status == DeliveryStatus.DELIVERED
    assert delivered.retryable is False
    assert failed_retryable.status == DeliveryStatus.FAILED
    assert failed_retryable.retryable is True
    assert failed_terminal.retryable is False


def test_twilio_signature_validation_can_be_enabled():
    adapter = TwilioSandboxWhatsAppAdapter(config=_twilio_config(validate_signature=True))
    params = _suspicious_twilio_payload()
    url = "https://example.test/api/channels/twilio/whatsapp/inbound"
    signature = adapter._signature_for(url=url, params=params, secret="sandbox-webhook-secret")

    assert adapter.verify_signature(TwilioSignatureContext(url=url, params=params, signature=signature)) is True
    assert adapter.verify_signature(TwilioSignatureContext(url=url, params=params, signature="bad")) is False


def test_twilio_inbound_creates_case_and_uses_contract_for_outbound():
    fake_transport = FakeTwilioTransport()
    adapter = TwilioSandboxWhatsAppAdapter(config=_twilio_config(), transport=fake_transport)
    service = TwilioSandboxService(
        adapter=adapter,
        event_model=EventModelService.in_memory(),
    )

    response = service.handle_inbound(_suspicious_twilio_payload())

    assert response.case_created is True
    assert response.risk_level == "high"
    assert response.protected_reply_sent is True
    assert response.guardian_notified is True
    assert len(fake_transport.calls) == 2
    assert fake_transport.calls[0]["to"] == "whatsapp:+5511999990001"
    assert fake_transport.calls[1]["to"] == "whatsapp:+5511888880001"
    assert BotEventType.SUSPICIOUS_MESSAGE_RECEIVED.value in response.events
    assert BotEventType.CASE_CREATED.value in response.events
    assert BotEventType.GUARDIAN_NOTIFIED.value in response.events

    message = service.event_model.repositories.messages.list_all()[0]
    assert message.simulated is False
    alert_event = next(
        event
        for event in service.event_model.repositories.events.list_all()
        if event.event_type == BotEventType.RESPONSIBLE_ALERT_QUEUED
    )
    assert alert_event.payload["simulated"] is False


def test_twilio_message_sid_idempotency_blocks_duplicate_cases_and_outbound():
    fake_transport = FakeTwilioTransport()
    adapter = TwilioSandboxWhatsAppAdapter(config=_twilio_config(), transport=fake_transport)
    service = TwilioSandboxService(adapter=adapter, event_model=EventModelService.in_memory())
    payload = _suspicious_twilio_payload("SMIDEMPOTENT001")

    first = service.handle_inbound(payload)
    duplicate = service.handle_inbound(payload)

    assert first.case_created is True
    assert duplicate.duplicate is True
    assert duplicate.case_created is False
    assert duplicate.outbound_messages == []
    assert len(fake_transport.calls) == 2
    assert len(service.event_model.repositories.messages.list_all()) == 1
    assert len(service.event_model.repositories.cases.list_all()) == 1


def test_twilio_status_callback_records_delivery_event():
    service = TwilioSandboxService(
        adapter=TwilioSandboxWhatsAppAdapter(config=_twilio_config()),
        event_model=EventModelService.in_memory(),
    )
    response = service.handle_status_callback(
        {"MessageSid": "SMOUT999", "MessageStatus": "delivered"}
    )

    assert response.status == DeliveryStatus.DELIVERED.value
    assert response.retryable is False
    assert response.event_id.startswith("event-")
    assert service.health().delivery_records == 1


def test_twilio_api_exposes_health_inbound_and_status_webhooks():
    client = TestClient(app)

    health = client.get("/api/channels/twilio/whatsapp/health")
    assert health.status_code == 200
    assert health.json()["provider"] == ChannelProvider.TWILIO_SANDBOX.value
    assert health.json()["production"] is False

    inbound = client.post(
        "/api/channels/twilio/whatsapp/inbound",
        data=_suspicious_twilio_payload("SMAPI001"),
    )
    assert inbound.status_code == 200
    inbound_body = inbound.json()
    assert inbound_body["provider"] == ChannelProvider.TWILIO_SANDBOX.value
    assert inbound_body["case_created"] is True
    assert inbound_body["provider_message_id"] == "SMAPI001"

    status = client.post(
        "/api/channels/twilio/whatsapp/status",
        data={"MessageSid": "SMAPI-OUT-001", "MessageStatus": "delivered"},
    )
    assert status.status_code == 200
    assert status.json()["status"] == DeliveryStatus.DELIVERED.value
