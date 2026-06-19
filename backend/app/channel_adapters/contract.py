from __future__ import annotations

from typing import Any, Mapping, Protocol, runtime_checkable

from app.channel_adapters.models import (
    ChannelConnection,
    ChannelConnectionValidation,
    ChannelProvider,
    ChannelReceiveResult,
    DeliveryStatusEvent,
    InboundMessage,
    NormalizedInboundMessage,
    OutboundMessage,
    OutboundMessageRequest,
    OutboundMessageResult,
)


@runtime_checkable
class ChannelAdapter(Protocol):
    def getProviderName(self) -> ChannelProvider | str: ...

    def validateConnection(
        self,
        connection: ChannelConnection | None = None,
    ) -> ChannelConnectionValidation: ...

    def parseProviderPayload(self, payload: Mapping[str, Any]) -> InboundMessage: ...

    def receiveInboundMessage(self, message: InboundMessage) -> ChannelReceiveResult: ...

    def sendMessage(self, message: OutboundMessage) -> OutboundMessageResult: ...

    def mapDeliveryStatus(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent: ...


@runtime_checkable
class WhatsAppChannelAdapter(Protocol):
    @property
    def provider(self) -> ChannelProvider: ...

    def normalize_inbound(self, payload: Mapping[str, Any]) -> NormalizedInboundMessage: ...

    def send_protected_reply(self, payload: OutboundMessageRequest) -> OutboundMessageResult: ...

    def send_guardian_alert(self, payload: OutboundMessageRequest) -> OutboundMessageResult: ...

    def parse_status_callback(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent: ...


@runtime_checkable
class SignatureVerifyingAdapter(Protocol):
    def verify_signature(self, request: Any) -> bool: ...


def get_provider_name(adapter: ChannelAdapter | WhatsAppChannelAdapter) -> ChannelProvider | str:
    provider_name = getattr(adapter, "getProviderName", None)
    if provider_name is not None:
        return provider_name()
    return getattr(adapter, "provider")


def validate_connection_if_supported(
    adapter: ChannelAdapter | WhatsAppChannelAdapter,
    connection: ChannelConnection | None = None,
) -> ChannelConnectionValidation:
    validator = getattr(adapter, "validateConnection", None)
    provider = ChannelProvider(get_provider_name(adapter))
    if validator is None:
        return ChannelConnectionValidation(
            provider=provider,
            valid=True,
            connectionId=connection.channel_connection_id if connection else None,
            message="No provider-specific validation configured.",
        )
    return validator(connection)


def normalize_provider_payload(
    adapter: ChannelAdapter | WhatsAppChannelAdapter,
    payload: Mapping[str, Any],
) -> InboundMessage:
    parser = getattr(adapter, "parseProviderPayload", None)
    if parser is not None:
        return parser(payload)
    return adapter.normalize_inbound(payload)


def receive_inbound_message(
    adapter: ChannelAdapter | WhatsAppChannelAdapter,
    message: InboundMessage,
) -> ChannelReceiveResult:
    receiver = getattr(adapter, "receiveInboundMessage", None)
    if receiver is not None:
        return receiver(message)
    return ChannelReceiveResult(inbound=message, accepted=True)


def send_via_channel(
    adapter: ChannelAdapter | WhatsAppChannelAdapter,
    message: OutboundMessage,
) -> OutboundMessageResult:
    sender = getattr(adapter, "sendMessage", None)
    if sender is not None:
        return sender(message)

    request = (
        message
        if isinstance(message, OutboundMessageRequest)
        else OutboundMessageRequest(
            provider=message.provider,
            to=message.to_address,
            body=message.body,
            kind=message.metadata.get("kind", "guardian_alert"),
            relatedCaseId=message.case_id,
            metadata=message.metadata,
        )
    )
    if request.kind.value == "protected_reply":
        return adapter.send_protected_reply(request)
    return adapter.send_guardian_alert(request)


def map_delivery_status(
    adapter: ChannelAdapter | WhatsAppChannelAdapter,
    payload: Mapping[str, Any],
) -> DeliveryStatusEvent:
    mapper = getattr(adapter, "mapDeliveryStatus", None)
    if mapper is not None:
        return mapper(payload)
    return adapter.parse_status_callback(payload)


def verify_signature_if_supported(adapter: ChannelAdapter | WhatsAppChannelAdapter, request: Any) -> bool:
    verifier = getattr(adapter, "verify_signature", None)
    if verifier is None:
        return True
    return bool(verifier(request))
