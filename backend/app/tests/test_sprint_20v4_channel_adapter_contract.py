from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from app.channel_adapters import (
    ChannelIngressService,
    ChannelProvider,
    DeliveryStatus,
    DeliveryStatusEvent,
    InMemoryDeliveryStatusRegistry,
    NormalizedInboundMessage,
    OutboundMessageKind,
    OutboundMessageRequest,
    OutboundMessageResult,
    WhatsAppChannelAdapter,
)
from app.event_model import EventModelService


class ContractTestAdapter:
    provider = ChannelProvider.MOCK

    def normalize_inbound(self, payload: Mapping[str, Any]) -> NormalizedInboundMessage:
        return NormalizedInboundMessage(
            provider=self.provider,
            providerMessageId=payload["message_id"],
            **{
                "from": payload["from"],
                "to": payload["to"],
            },
            body=payload["body"],
            timestamp=payload["timestamp"],
            profileName=payload.get("profile_name"),
            media=payload.get("media", []),
            raw=dict(payload),
        )

    def send_guardian_alert(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self._send(payload)

    def parse_status_callback(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent:
        return DeliveryStatusEvent(
            provider=self.provider,
            providerMessageId=payload["message_id"],
            status=DeliveryStatus(payload["status"]),
            timestamp=payload["timestamp"],
            errorCode=payload.get("error_code"),
            errorMessage=payload.get("error_message"),
            retryable=payload.get("retryable", False),
            raw=dict(payload),
        )

    def _send(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return OutboundMessageResult(
            provider=self.provider,
            providerMessageId=f"out-{uuid4().hex}",
            to=payload.to_address,
            status=DeliveryStatus.PENDING,
            simulated=True,
            retryable=True,
            raw=payload.model_dump(by_alias=True),
        )


def sample_payload(message_id: str = "provider-msg-001") -> dict[str, Any]:
    return {
        "message_id": message_id,
        "from": "+5511999990001",
        "to": "+14155238886",
        "body": "Troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
        "timestamp": "2026-06-05T22:00:00Z",
        "profile_name": "Dona Lucia",
        "media": [{"type": "image", "providerMediaId": "media-1"}],
    }


def test_contract_test_adapter_satisfies_whatsapp_channel_adapter_protocol():
    assert isinstance(ContractTestAdapter(), WhatsAppChannelAdapter)


def test_inbound_payload_is_normalized_to_provider_neutral_message():
    adapter = ContractTestAdapter()
    inbound = adapter.normalize_inbound(sample_payload())

    assert inbound.provider == ChannelProvider.MOCK
    assert inbound.provider_message_id == "provider-msg-001"
    assert inbound.from_address == "+5511999990001"
    assert inbound.to_address == "+14155238886"
    assert inbound.profile_name == "Dona Lucia"
    assert inbound.media[0].media_type == "image"
    assert inbound.media[0].provider_media_id == "media-1"
    assert inbound.model_dump(by_alias=True)["from"] == "+5511999990001"


def test_outbound_contract_returns_provider_neutral_result():
    adapter = ContractTestAdapter()
    result = adapter.send_guardian_alert(
        OutboundMessageRequest(
            provider=ChannelProvider.MOCK,
            to="+5511999990001",
            body="Alerta Guardian: revise o caso.",
            kind=OutboundMessageKind.GUARDIAN_ALERT,
            relatedCaseId="case-1",
        )
    )

    assert result.provider == ChannelProvider.MOCK
    assert result.provider_message_id.startswith("out-")
    assert result.status == DeliveryStatus.PENDING
    assert result.simulated is True
    assert result.retryable is True


def test_delivery_status_registry_tracks_pending_and_callback_updates():
    adapter = ContractTestAdapter()
    registry = InMemoryDeliveryStatusRegistry()
    result = adapter.send_guardian_alert(
        OutboundMessageRequest(
            provider=ChannelProvider.MOCK,
            to="+5511999990002",
            body="Alerta simulado.",
            kind=OutboundMessageKind.GUARDIAN_ALERT,
        )
    )
    pending = registry.record_outbound(result, updated_at=datetime.now(timezone.utc))
    assert pending.status == DeliveryStatus.PENDING

    callback = adapter.parse_status_callback(
        {
            "message_id": result.provider_message_id,
            "status": "delivered",
            "timestamp": "2026-06-05T22:01:00Z",
        }
    )
    delivered = registry.update_from_callback(callback)

    assert delivered.status == DeliveryStatus.DELIVERED
    assert registry.get(ChannelProvider.MOCK, result.provider_message_id) == delivered


def test_channel_ingress_integrates_normalized_inbound_with_event_model():
    event_model = EventModelService.in_memory()
    service = ChannelIngressService(event_model=event_model)
    result = service.ingest_inbound(
        adapter=ContractTestAdapter(),
        payload=sample_payload(),
        guardian_alias="Gabriel",
    )

    assert result.duplicate is False
    assert result.message_id is not None
    assert result.case_id is not None
    stored_message = event_model.repositories.messages.get(result.message_id)
    assert stored_message is not None
    assert stored_message.provider_message_id == "provider-msg-001"
    assert stored_message.channel == "whatsapp:mock"
    assert stored_message.simulated is True


def test_provider_message_id_prevents_duplicate_case_creation():
    event_model = EventModelService.in_memory()
    service = ChannelIngressService(event_model=event_model)
    adapter = ContractTestAdapter()

    first = service.ingest_inbound(adapter=adapter, payload=sample_payload())
    duplicate = service.ingest_inbound(adapter=adapter, payload=sample_payload())

    assert first.duplicate is False
    assert first.case_id is not None
    assert duplicate.duplicate is True
    assert duplicate.case_id is None
    assert len(event_model.repositories.messages.list_all()) == 1
    assert len(event_model.repositories.cases.list_all()) == 1
    assert len(event_model.repositories.events.list_all()) == 5
