from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
from urllib import request
from uuid import uuid4

from app.channel_adapters.models import (
    ChannelConnection,
    ChannelConnectionValidation,
    ChannelProvider,
    ChannelReceiveResult,
    DeliveryStatus,
    DeliveryStatusEvent,
    InboundMessage,
    NormalizedMedia,
    OutboundMessage,
    OutboundMessageRequest,
    OutboundMessageResult,
)


EVOLUTION_DEMO_PROVIDER = ChannelProvider.EVOLUTION_DEMO
EVOLUTION_DEMO_TIMEOUT_SECONDS = 10


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_csv(name: str) -> tuple[str, ...]:
    value = os.getenv(name) or ""
    return tuple(item.strip() for item in value.split(",") if item.strip())


class EvolutionDemoPayloadError(ValueError):
    pass


class EvolutionDemoIgnoredEvent(ValueError):
    pass


def _coalesce(payload: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None and value != "":
            return value
    return default


def _timestamp(value: Any | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        if value > 10_000_000_000:
            value = value / 1000
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str) and value:
        if value.isdigit():
            return _timestamp(int(value))
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def _event_name(value: Any) -> str:
    return str(value or "").strip().replace(".", "_").upper()


def _digits(value: str) -> str:
    return "".join(char for char in value if char.isdigit())


def _jid_to_address(value: str | None) -> str:
    if not value:
        return ""
    if "@" in value:
        value = value.split("@", 1)[0]
    return value.removeprefix("whatsapp:")


def _safe_raw(payload: Mapping[str, Any]) -> dict[str, Any]:
    hidden = {"apikey", "apiKey", "authorization", "Authorization", "EVOLUTION_API_KEY"}
    return {key: ("<hidden>" if key in hidden else value) for key, value in payload.items()}


def _message_body(message: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    direct = _coalesce(data, "text", "body", "messageText", "conversation")
    if direct:
        return str(direct).strip()
    if message.get("conversation"):
        return str(message["conversation"]).strip()
    extended = message.get("extendedTextMessage") or {}
    if isinstance(extended, Mapping) and extended.get("text"):
        return str(extended["text"]).strip()
    for key in ("imageMessage", "videoMessage", "documentMessage"):
        media_message = message.get(key) or {}
        if isinstance(media_message, Mapping) and media_message.get("caption"):
            return str(media_message["caption"]).strip()
    return ""


def _media_from_message(message: Mapping[str, Any]) -> list[NormalizedMedia]:
    media: list[NormalizedMedia] = []
    for key, media_type in (
        ("imageMessage", "image"),
        ("videoMessage", "video"),
        ("audioMessage", "audio"),
        ("documentMessage", "document"),
    ):
        value = message.get(key)
        if not isinstance(value, Mapping):
            continue
        media.append(
            NormalizedMedia(
                type=media_type,
                url=str(value.get("url")) if value.get("url") else None,
                providerMediaId=str(value.get("mediaKey") or value.get("fileSha256") or "")
                or None,
            )
        )
    return media


def _evolution_status(value: Any) -> DeliveryStatus:
    normalized = str(value or "").strip().lower()
    if normalized in {"server_ack", "sent", "2"}:
        return DeliveryStatus.SENT
    if normalized in {"delivery_ack", "read", "delivered", "3", "4"}:
        return DeliveryStatus.DELIVERED
    if normalized in {"failed", "error"}:
        return DeliveryStatus.FAILED
    return DeliveryStatus.PENDING


@dataclass(frozen=True)
class EvolutionDemoConfig:
    api_url: str | None = None
    api_key: str | None = None
    instance_name: str | None = None
    guardian_address: str | None = None
    # Safety gate for REAL WhatsApp sends. Defaults are fail-safe: unless real
    # sending is explicitly turned on AND the recipient is allow-listed, nothing
    # leaves the process. This mirrors the guard the n8n channel already applies.
    dry_run: bool = True
    real_send_enabled: bool = False
    require_allowed_recipient: bool = True
    allowed_recipients: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "EvolutionDemoConfig":
        return cls(
            api_url=os.getenv("EVOLUTION_API_URL") or None,
            api_key=os.getenv("EVOLUTION_API_KEY") or None,
            instance_name=os.getenv("EVOLUTION_INSTANCE_NAME") or None,
            # Single trusted contact (TRUSTED_CONTACT), with legacy vars as fallback.
            guardian_address=(
                os.getenv("TRUSTED_CONTACT")
                or os.getenv("EVOLUTION_GUARDIAN_TO")
                or os.getenv("DUAL_BOT_GUARDIAN_TO")
            )
            or None,
            dry_run=_env_flag("DRY_RUN", True),
            real_send_enabled=_env_flag("BETA_REAL_SEND_ENABLED", False),
            require_allowed_recipient=_env_flag("BETA_REQUIRE_ALLOWED_RECIPIENT", True),
            allowed_recipients=_env_csv("BETA_ALLOWED_RECIPIENTS"),
        )

    @property
    def can_send(self) -> bool:
        return bool(self.api_url and self.api_key and self.instance_name)

    def real_send_blocked_reason(self, to_address: str) -> str | None:
        """Why a real network send to ``to_address`` must be suppressed, or None.

        Any non-None reason means: do NOT hit the WhatsApp network — simulate.
        """
        if self.dry_run:
            return "dry_run"
        if not self.real_send_enabled:
            return "real_send_disabled"
        if self.require_allowed_recipient:
            allowed = {_digits(item) for item in self.allowed_recipients if _digits(item)}
            if _digits(to_address) not in allowed:
                return "recipient_not_allowed"
        return None

    @property
    def send_text_url(self) -> str | None:
        if not self.api_url or not self.instance_name:
            return None
        return f"{self.api_url.rstrip('/')}/message/sendText/{self.instance_name}"


class EvolutionMessageTransport(Protocol):
    def send_text(
        self,
        *,
        api_url: str,
        api_key: str,
        instance_name: str,
        to_address: str,
        body: str,
    ) -> Mapping[str, Any]: ...


class EvolutionHttpMessageTransport:
    def send_text(
        self,
        *,
        api_url: str,
        api_key: str,
        instance_name: str,
        to_address: str,
        body: str,
    ) -> Mapping[str, Any]:
        url = f"{api_url.rstrip('/')}/message/sendText/{instance_name}"
        payload = {
            "number": _digits(to_address),
            "text": body,
        }
        outbound_request = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "apikey": api_key,
            },
            method="POST",
        )
        with request.urlopen(outbound_request, timeout=EVOLUTION_DEMO_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))


class EvolutionDemoAdapter:
    provider = EVOLUTION_DEMO_PROVIDER

    def __init__(
        self,
        *,
        config: EvolutionDemoConfig | None = None,
        transport: EvolutionMessageTransport | None = None,
    ) -> None:
        self.config = config or EvolutionDemoConfig.from_env()
        self._transport = transport or EvolutionHttpMessageTransport()

    def getProviderName(self) -> ChannelProvider:
        return self.provider

    def validateConnection(
        self,
        connection: ChannelConnection | None = None,
    ) -> ChannelConnectionValidation:
        return ChannelConnectionValidation(
            provider=self.provider,
            valid=self.config.can_send,
            connectionId=connection.channel_connection_id if connection else None,
            message=(
                "Evolution demo env vars configured."
                if self.config.can_send
                else "Configure EVOLUTION_API_URL, EVOLUTION_API_KEY and EVOLUTION_INSTANCE_NAME."
            ),
        )

    def parseProviderPayload(self, payload: Mapping[str, Any]) -> InboundMessage:
        event = _event_name(_coalesce(payload, "event", "type"))
        if event and event != "MESSAGES_UPSERT":
            raise EvolutionDemoIgnoredEvent(f"Unsupported Evolution event: {event}")

        data = payload.get("data") or payload.get("message") or {}
        if isinstance(data, list):
            if not data:
                raise EvolutionDemoPayloadError("Evolution payload has empty data list.")
            data = data[0]
        if not isinstance(data, Mapping):
            raise EvolutionDemoPayloadError("Evolution payload data must be an object.")

        key = data.get("key") or {}
        if not isinstance(key, Mapping):
            key = {}
        if bool(key.get("fromMe")):
            raise EvolutionDemoIgnoredEvent("Ignoring outbound Evolution message.")

        message = data.get("message") or {}
        if not isinstance(message, Mapping):
            message = {}

        external_message_id = str(
            _coalesce(data, "messageId", "id", default=None)
            or _coalesce(key, "id", "messageId", default=None)
            or f"evolution-in-{uuid4().hex}"
        )
        remote_jid = str(_coalesce(key, "remoteJid", "participant", default="") or "")
        from_address = _jid_to_address(str(_coalesce(data, "from", default=remote_jid) or remote_jid))
        to_address = str(
            _coalesce(
                data,
                "to",
                default=self.config.instance_name or str(_coalesce(payload, "instance", default="evolution-demo")),
            )
        )
        body = _message_body(message, data)
        if not body:
            raise EvolutionDemoPayloadError("Evolution MESSAGES_UPSERT payload has no text body.")

        return InboundMessage(
            provider=self.provider,
            externalMessageId=external_message_id,
            **{
                "from": from_address,
                "to": to_address,
            },
            body=body,
            timestamp=_timestamp(_coalesce(data, "messageTimestamp", "timestamp", "createdAt")),
            profileName=_coalesce(data, "pushName", "profileName", "senderName"),
            media=_media_from_message(message),
            rawPayload=_safe_raw(payload),
        )

    def receiveInboundMessage(self, message: InboundMessage) -> ChannelReceiveResult:
        return ChannelReceiveResult(inbound=message, accepted=True)

    def sendMessage(self, message: OutboundMessage) -> OutboundMessageResult:
        if not self.config.can_send:
            return OutboundMessageResult(
                provider=self.provider,
                providerMessageId=f"evolution-demo-not-configured-{uuid4().hex}",
                to=message.to_address,
                status=DeliveryStatus.FAILED,
                simulated=True,
                retryable=True,
                raw={"reason": "evolution_demo_not_configured"},
            )
        # SAFETY GATE: never touch the WhatsApp network unless real sending is
        # explicitly enabled AND the recipient is allow-listed. Suppressed sends
        # are simulated (no retry) so no real message ever reaches a contact.
        blocked_reason = self.config.real_send_blocked_reason(message.to_address)
        if blocked_reason:
            return OutboundMessageResult(
                provider=self.provider,
                providerMessageId=f"evolution-demo-suppressed-{blocked_reason}-{uuid4().hex}",
                to=message.to_address,
                status=DeliveryStatus.SENT,
                simulated=True,
                retryable=False,
                raw={"reason": f"send_suppressed_{blocked_reason}"},
            )
        try:
            response = self._transport.send_text(
                api_url=str(self.config.api_url),
                api_key=str(self.config.api_key),
                instance_name=str(self.config.instance_name),
                to_address=message.to_address,
                body=message.body,
            )
        except Exception as exc:
            return OutboundMessageResult(
                provider=self.provider,
                providerMessageId=f"evolution-demo-send-error-{uuid4().hex}",
                to=message.to_address,
                status=DeliveryStatus.FAILED,
                simulated=False,
                retryable=True,
                raw={"error": exc.__class__.__name__},
            )

        provider_message_id = str(
            _coalesce(response, "messageId", "id", "key", default=f"evolution-out-{uuid4().hex}")
        )
        return OutboundMessageResult(
            provider=self.provider,
            providerMessageId=provider_message_id,
            to=message.to_address,
            status=DeliveryStatus.SENT,
            simulated=False,
            retryable=False,
            raw=_safe_raw(response),
        )

    def mapDeliveryStatus(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent:
        data = payload.get("data") or payload
        if not isinstance(data, Mapping):
            data = payload
        key = data.get("key") or {}
        if not isinstance(key, Mapping):
            key = {}
        return DeliveryStatusEvent(
            provider=self.provider,
            externalMessageId=str(
                _coalesce(data, "messageId", "id", default=None)
                or _coalesce(key, "id", "messageId", default=f"evolution-status-{uuid4().hex}")
            ),
            status=_evolution_status(_coalesce(data, "status", "ack", default=payload.get("status"))),
            timestamp=_timestamp(_coalesce(data, "timestamp", "updatedAt", "messageTimestamp")),
            rawPayload=_safe_raw(payload),
        )

    def normalize_inbound(self, payload: Mapping[str, Any]) -> InboundMessage:
        return self.parseProviderPayload(payload)

    def send_protected_reply(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self.sendMessage(payload)

    def send_guardian_alert(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self.sendMessage(payload)

    def parse_status_callback(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent:
        return self.mapDeliveryStatus(payload)
