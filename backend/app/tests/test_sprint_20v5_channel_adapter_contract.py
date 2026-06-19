from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from app.channel_adapters import (
    ChannelAdapter,
    ChannelConnection,
    ChannelConnectionValidation,
    ChannelIngressService,
    ChannelProvider,
    ChannelReceiveResult,
    DeliveryStatus,
    DeliveryStatusEvent,
    InboundMessage,
    OutboundMessage,
    OutboundMessageResult,
    map_delivery_status,
    normalize_provider_payload,
    send_via_channel,
)
from app.event_model import EventModelService


class V5ContractTestAdapter:
    def getProviderName(self) -> ChannelProvider:
        return ChannelProvider.MOCK_WHATSAPP

    def validateConnection(
        self,
        connection: ChannelConnection | None = None,
    ) -> ChannelConnectionValidation:
        return ChannelConnectionValidation(
            provider=self.getProviderName(),
            valid=True,
            connectionId=connection.channel_connection_id if connection else None,
            message="Contract-only test adapter is available.",
        )

    def parseProviderPayload(self, payload: Mapping[str, Any]) -> InboundMessage:
        return InboundMessage(
            provider=self.getProviderName(),
            externalMessageId=payload["external_id"],
            **{
                "from": payload["from"],
                "to": payload["to"],
            },
            body=payload["body"],
            timestamp=payload["timestamp"],
            rawPayload=dict(payload),
            protectedPersonId=payload.get("protected_person_id"),
            caseId=payload.get("case_id"),
        )

    def receiveInboundMessage(self, message: InboundMessage) -> ChannelReceiveResult:
        return ChannelReceiveResult(inbound=message, accepted=True)

    def sendMessage(self, message: OutboundMessage) -> OutboundMessageResult:
        return OutboundMessageResult(
            provider=self.getProviderName(),
            providerMessageId=f"contract-out-{uuid4().hex}",
            to=message.to_address,
            status=DeliveryStatus.PENDING,
            simulated=True,
            retryable=False,
            raw=message.model_dump(by_alias=True),
        )

    def mapDeliveryStatus(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent:
        return DeliveryStatusEvent(
            provider=self.getProviderName(),
            externalMessageId=payload["external_id"],
            status=DeliveryStatus(payload["status"]),
            timestamp=payload["timestamp"],
            rawPayload=dict(payload),
        )


def _payload(message_id: str = "v5-contract-in-001") -> dict[str, Any]:
    return {
        "external_id": message_id,
        "from": "+5511999990001",
        "to": "+5511888880001",
        "body": "Troquei de numero. Preciso de Pix urgente. Nao liga agora.",
        "timestamp": datetime.now(timezone.utc),
    }


def test_v5_provider_enum_contains_future_adapter_targets():
    assert ChannelProvider.MOCK_WHATSAPP.value == "mock_whatsapp"
    assert ChannelProvider.EVOLUTION_DEMO.value == "evolution_demo"
    assert ChannelProvider.TWILIO_SANDBOX.value == "twilio_sandbox"
    assert ChannelProvider.META_CLOUD_API.value == "meta_cloud_api"


def test_v5_contract_adapter_satisfies_channel_adapter_protocol():
    adapter = V5ContractTestAdapter()
    connection = ChannelConnection(
        provider=ChannelProvider.MOCK_WHATSAPP.value,
        channel="whatsapp",
        status="active",
        simulated=True,
    )

    assert isinstance(adapter, ChannelAdapter)
    validation = adapter.validateConnection(connection)
    assert validation.valid is True
    assert validation.connection_id == connection.channel_connection_id


def test_v5_normalizes_provider_payload_to_inbound_message():
    inbound = normalize_provider_payload(V5ContractTestAdapter(), _payload())

    assert inbound.id.startswith("inbound-")
    assert inbound.provider == ChannelProvider.MOCK_WHATSAPP
    assert inbound.external_message_id == "v5-contract-in-001"
    assert inbound.provider_message_id == "v5-contract-in-001"
    assert inbound.from_address == "+5511999990001"
    assert inbound.to_address == "+5511888880001"
    assert inbound.raw_payload["external_id"] == "v5-contract-in-001"
    assert inbound.normalized_at.tzinfo is not None
    assert inbound.model_dump(by_alias=True)["externalMessageId"] == "v5-contract-in-001"


def test_v5_send_and_delivery_status_use_contract_only():
    adapter = V5ContractTestAdapter()
    outbound = OutboundMessage(
        provider=ChannelProvider.MOCK_WHATSAPP,
        to="+5511888880001",
        body="Alerta Guardian: revise o caso.",
        templateName="guardian_alert",
        metadata={"kind": "guardian_alert"},
        caseId="case-1",
        protectedPersonId="protected-1",
    )

    result = send_via_channel(adapter, outbound)
    delivered = map_delivery_status(
        adapter,
        {
            "external_id": result.provider_message_id,
            "status": "delivered",
            "timestamp": datetime.now(timezone.utc),
        },
    )

    assert result.provider == ChannelProvider.MOCK_WHATSAPP
    assert result.provider_message_id.startswith("contract-out-")
    assert result.raw["caseId"] == "case-1"
    assert delivered.external_message_id == result.provider_message_id
    assert delivered.status == DeliveryStatus.DELIVERED


def test_v5_channel_ingress_routes_only_normalized_message_to_core():
    event_model = EventModelService.in_memory()
    service = ChannelIngressService(event_model=event_model)
    inbound = normalize_provider_payload(V5ContractTestAdapter(), _payload("v5-contract-route-001"))

    result = service.ingest_normalized(inbound=inbound, guardian_alias="Gabriel")

    assert result.duplicate is False
    assert result.message_id is not None
    assert result.case_id is not None
    stored_message = event_model.repositories.messages.get(result.message_id)
    assert stored_message is not None
    assert stored_message.provider_message_id == "v5-contract-route-001"
    assert stored_message.channel == "whatsapp:mock_whatsapp"
    assert stored_message.simulated is True
    assert all("rawPayload" not in event.payload for event in event_model.repositories.events.list_all())
    channel_audits = [
        log.action
        for log in event_model.repositories.audit_logs.list_all()
        if log.actor == "channel_adapter"
    ]
    assert "ChannelInboundReceived" in channel_audits
    assert "ChannelInboundRouted" in channel_audits


def test_v5_channel_ingress_keeps_idempotency_by_external_message_id():
    event_model = EventModelService.in_memory()
    service = ChannelIngressService(event_model=event_model)
    adapter = V5ContractTestAdapter()

    first = service.ingest_inbound(adapter=adapter, payload=_payload("v5-idempotent-001"))
    duplicate = service.ingest_inbound(adapter=adapter, payload=_payload("v5-idempotent-001"))

    assert first.duplicate is False
    assert first.case_id is not None
    assert duplicate.duplicate is True
    assert duplicate.case_id is None
    assert len(event_model.repositories.messages.list_all()) == 1
    assert len(event_model.repositories.cases.list_all()) == 1
