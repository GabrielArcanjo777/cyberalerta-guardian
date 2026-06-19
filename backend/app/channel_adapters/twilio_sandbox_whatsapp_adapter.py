from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
from urllib import parse, request
from uuid import uuid4

from app.channel_adapters.models import (
    ChannelProvider,
    DeliveryStatus,
    DeliveryStatusEvent,
    NormalizedInboundMessage,
    NormalizedMedia,
    OutboundMessageRequest,
    OutboundMessageResult,
)


TWILIO_SANDBOX_PROVIDER = ChannelProvider.TWILIO_SANDBOX
TWILIO_API_TIMEOUT_SECONDS = 10


def _coalesce(payload: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None and value != "":
            return value
    return default


def _timestamp(value: Any | None) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return datetime.now(timezone.utc)


def _bool_env(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _twilio_status(value: Any) -> DeliveryStatus:
    normalized = str(value or "").strip().lower()
    if normalized in {"sent"}:
        return DeliveryStatus.SENT
    if normalized in {"delivered", "read"}:
        return DeliveryStatus.DELIVERED
    if normalized in {"failed", "undelivered"}:
        return DeliveryStatus.FAILED
    return DeliveryStatus.PENDING


def _safe_raw(payload: Mapping[str, Any]) -> dict[str, Any]:
    hidden = {"AccountSid", "account_sid", "AuthToken", "auth_token"}
    return {key: ("<hidden>" if key in hidden else value) for key, value in payload.items()}


def _media_from_twilio(payload: Mapping[str, Any]) -> list[NormalizedMedia]:
    try:
        count = int(_coalesce(payload, "NumMedia", "num_media", default=0))
    except (TypeError, ValueError):
        count = 0

    media: list[NormalizedMedia] = []
    for index in range(max(count, 0)):
        content_type = _coalesce(payload, f"MediaContentType{index}", f"media_content_type_{index}")
        url = _coalesce(payload, f"MediaUrl{index}", f"media_url_{index}")
        provider_media_id = _coalesce(payload, f"MediaSid{index}", f"media_sid_{index}")
        if content_type or url or provider_media_id:
            media.append(
                NormalizedMedia(
                    type=str(content_type or "unknown"),
                    url=str(url) if url else None,
                    providerMediaId=str(provider_media_id) if provider_media_id else None,
                )
            )
    return media


@dataclass(frozen=True)
class TwilioSandboxConfig:
    account_sid: str | None = None
    auth_token: str | None = None
    whatsapp_from: str | None = None
    webhook_secret: str | None = None
    channel_provider: str = TWILIO_SANDBOX_PROVIDER.value
    status_callback_url: str | None = None
    guardian_address: str | None = None
    validate_signature: bool = False

    @classmethod
    def from_env(cls) -> "TwilioSandboxConfig":
        return cls(
            account_sid=os.getenv("TWILIO_ACCOUNT_SID") or None,
            auth_token=os.getenv("TWILIO_AUTH_TOKEN") or None,
            whatsapp_from=os.getenv("TWILIO_WHATSAPP_FROM") or None,
            webhook_secret=os.getenv("TWILIO_WEBHOOK_SECRET") or None,
            channel_provider=os.getenv("CHANNEL_PROVIDER") or TWILIO_SANDBOX_PROVIDER.value,
            status_callback_url=os.getenv("TWILIO_STATUS_CALLBACK_URL") or None,
            guardian_address=os.getenv("TWILIO_GUARDIAN_TO") or None,
            validate_signature=_bool_env(os.getenv("TWILIO_VALIDATE_SIGNATURE")),
        )

    @property
    def can_send(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.whatsapp_from)

    @property
    def signature_secret(self) -> str | None:
        return self.webhook_secret or self.auth_token


@dataclass(frozen=True)
class TwilioSignatureContext:
    url: str
    params: Mapping[str, Any]
    signature: str | None


class TwilioMessageTransport(Protocol):
    def send_message(
        self,
        *,
        account_sid: str,
        auth_token: str,
        from_address: str,
        to_address: str,
        body: str,
        status_callback_url: str | None = None,
    ) -> Mapping[str, Any]: ...


class TwilioHttpMessageTransport:
    def send_message(
        self,
        *,
        account_sid: str,
        auth_token: str,
        from_address: str,
        to_address: str,
        body: str,
        status_callback_url: str | None = None,
    ) -> Mapping[str, Any]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{parse.quote(account_sid)}/Messages.json"
        form: dict[str, str] = {
            "From": from_address,
            "To": to_address,
            "Body": body,
        }
        if status_callback_url:
            form["StatusCallback"] = status_callback_url

        data = parse.urlencode(form).encode("utf-8")
        credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("ascii")
        outbound_request = request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with request.urlopen(outbound_request, timeout=TWILIO_API_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))


class TwilioSandboxWhatsAppAdapter:
    provider = TWILIO_SANDBOX_PROVIDER

    def __init__(
        self,
        *,
        config: TwilioSandboxConfig | None = None,
        transport: TwilioMessageTransport | None = None,
    ) -> None:
        self.config = config or TwilioSandboxConfig.from_env()
        self._transport = transport or TwilioHttpMessageTransport()

    def normalize_inbound(self, payload: Mapping[str, Any]) -> NormalizedInboundMessage:
        return NormalizedInboundMessage(
            provider=self.provider,
            providerMessageId=str(_coalesce(payload, "MessageSid", "SmsMessageSid", "SmsSid")),
            **{
                "from": str(_coalesce(payload, "From", "from")),
                "to": str(_coalesce(payload, "To", "to")),
            },
            body=str(_coalesce(payload, "Body", "body", default="")).strip(),
            timestamp=_timestamp(_coalesce(payload, "Timestamp", "timestamp", "DateCreated")),
            profileName=_coalesce(payload, "ProfileName", "profile_name"),
            media=_media_from_twilio(payload),
            raw=_safe_raw(payload),
        )

    def send_protected_reply(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self._send(payload)

    def send_guardian_alert(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        return self._send(payload)

    def parse_status_callback(self, payload: Mapping[str, Any]) -> DeliveryStatusEvent:
        twilio_status = _coalesce(payload, "MessageStatus", "SmsStatus", "status", default="pending")
        delivery_status = _twilio_status(twilio_status)
        error_code = _coalesce(payload, "ErrorCode", "error_code")
        return DeliveryStatusEvent(
            provider=self.provider,
            providerMessageId=str(_coalesce(payload, "MessageSid", "SmsMessageSid", "SmsSid")),
            status=delivery_status,
            timestamp=_timestamp(_coalesce(payload, "Timestamp", "timestamp", "EventTimestamp")),
            errorCode=str(error_code) if error_code else None,
            errorMessage=_coalesce(payload, "ErrorMessage", "error_message"),
            retryable=self._is_retryable(delivery_status, error_code),
            raw=_safe_raw(payload),
        )

    def verify_signature(self, request_context: Any) -> bool:
        if not self.config.validate_signature:
            return True
        if not isinstance(request_context, TwilioSignatureContext):
            return False
        secret = self.config.signature_secret
        if not secret or not request_context.signature:
            return False
        expected = self._signature_for(
            url=request_context.url,
            params=request_context.params,
            secret=secret,
        )
        return hmac.compare_digest(expected, request_context.signature)

    def _send(self, payload: OutboundMessageRequest) -> OutboundMessageResult:
        if not self.config.can_send:
            return OutboundMessageResult(
                provider=self.provider,
                providerMessageId=f"twilio-sandbox-not-configured-{uuid4().hex}",
                to=payload.to_address,
                status=DeliveryStatus.FAILED,
                simulated=False,
                retryable=True,
                retryAfterSeconds=60,
                raw={"reason": "twilio_sandbox_not_configured", "kind": payload.kind.value},
            )

        try:
            response = self._transport.send_message(
                account_sid=str(self.config.account_sid),
                auth_token=str(self.config.auth_token),
                from_address=str(self.config.whatsapp_from),
                to_address=payload.to_address,
                body=payload.body,
                status_callback_url=self.config.status_callback_url,
            )
        except Exception as exc:
            return OutboundMessageResult(
                provider=self.provider,
                providerMessageId=f"twilio-sandbox-send-error-{uuid4().hex}",
                to=payload.to_address,
                status=DeliveryStatus.FAILED,
                simulated=False,
                retryable=True,
                retryAfterSeconds=60,
                raw={"reason": "twilio_send_failed", "error": str(exc), "kind": payload.kind.value},
            )

        provider_message_id = str(_coalesce(response, "sid", "MessageSid", default=f"twilio-sandbox-{uuid4().hex}"))
        status = _twilio_status(_coalesce(response, "status", "MessageStatus", default="queued"))
        return OutboundMessageResult(
            provider=self.provider,
            providerMessageId=provider_message_id,
            to=payload.to_address,
            status=status,
            simulated=False,
            retryable=status == DeliveryStatus.FAILED,
            raw=_safe_raw(dict(response)),
        )

    def _is_retryable(self, status: DeliveryStatus, error_code: Any) -> bool:
        if status != DeliveryStatus.FAILED:
            return False
        non_retryable = {"21211", "21610", "21614"}
        return str(error_code or "") not in non_retryable

    def _signature_for(self, *, url: str, params: Mapping[str, Any], secret: str) -> str:
        normalized = url + "".join(f"{key}{params[key]}" for key in sorted(params))
        digest = hmac.new(secret.encode("utf-8"), normalized.encode("utf-8"), hashlib.sha1).digest()
        return base64.b64encode(digest).decode("ascii")
