from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from app.channel_adapters.models import (
    ChannelProvider,
    DeliveryStatus,
    DeliveryStatusEvent,
    NormalizedInboundMessage,
    OutboundMessageRequest,
    OutboundMessageResult,
)


def _is_present(value: Any) -> bool:
    return value is not None and value != ""


def _coalesce(payload: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload and _is_present(payload[key]):
            return payload[key]
    return default


def _timestamp(value: Any | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    return datetime.now(timezone.utc)


class MockWhatsAppAdapter:
    provider = ChannelProvider.MOCK

    def normalize_inbound(self, payload: Mapping[str, Any]) -> NormalizedInboundMessage:
        provider_message_id = _coalesce(
            payload,
            "providerMessageId",
            "provider_message_id",
            "message_id",
            default=f"mock-in-{uuid4().hex}",
        )
        return NormalizedInboundMessage(
            provider=self.provider,
            providerMessageId=provider_message_id,
            **{
                "from": _coalesce(payload, "from", "from_address"),
                "to": _coalesce(payload, "to", "to_address"),
            },
            body=str(_coalesce(payload, "body", "message", default="")).strip(),
            timestamp=_timestamp(_coalesce(payload, "timestamp", "created_at")),
            profileName=_coalesce(payload, "profileName", "profile_name", "protected_person_alias"),
            media=list(_coalesce(payload, "media", default=[])),
            raw=dict(payload),
        )

    def send_protected_reply(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self._send(payload, prefix="mock-protected")

    def send_guardian_alert(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self._send(payload, prefix="mock-guardian")

    def parse_status_callback(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent:
        return DeliveryStatusEvent(
            provider=self.provider,
            providerMessageId=_coalesce(
                payload,
                "providerMessageId",
                "provider_message_id",
                "message_id",
            ),
            status=DeliveryStatus(_coalesce(payload, "status", default=DeliveryStatus.DELIVERED.value)),
            timestamp=_timestamp(_coalesce(payload, "timestamp", "updated_at")),
            errorCode=_coalesce(payload, "errorCode", "error_code"),
            errorMessage=_coalesce(payload, "errorMessage", "error_message"),
            retryable=bool(_coalesce(payload, "retryable", default=False)),
            raw=dict(payload),
        )

    def _send(self, payload: OutboundMessageRequest, *, prefix: str) -> OutboundMessageResult:
        return OutboundMessageResult(
            provider=self.provider,
            providerMessageId=f"{prefix}-{uuid4().hex}",
            to=payload.to_address,
            status=DeliveryStatus.PENDING,
            simulated=True,
            retryable=True,
            raw=payload.model_dump(by_alias=True),
        )
