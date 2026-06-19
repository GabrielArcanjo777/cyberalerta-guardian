from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from app.channel_adapters import (
    ChannelIngressService,
    DeliveryStatus,
    InMemoryDeliveryStatusRegistry,
    InMemoryProviderMessageRegistry,
    OutboundMessageKind,
    OutboundMessageRequest,
)
from app.channel_adapters.twilio_sandbox_whatsapp_adapter import (
    TwilioSandboxConfig,
    TwilioSandboxWhatsAppAdapter,
)
from app.event_model import BotEventType, EventModelService
from app.twilio_sandbox.models import (
    TwilioSandboxHealthResponse,
    TwilioSandboxInboundWebhookResponse,
    TwilioSandboxOutboundRecord,
    TwilioSandboxStatusCallbackResponse,
)


def mask_channel_address(value: str | None) -> str:
    if not value:
        return ""
    prefix = "whatsapp:"
    stripped = value.removeprefix(prefix)
    if len(stripped) <= 4:
        masked = "*" * len(stripped)
    else:
        masked = f"{'*' * max(len(stripped) - 4, 0)}{stripped[-4:]}"
    return f"{prefix}{masked}" if value.startswith(prefix) else masked


class TwilioSandboxService:
    def __init__(
        self,
        *,
        adapter: TwilioSandboxWhatsAppAdapter | None = None,
        event_model: EventModelService | None = None,
        guardian_address: str | None = None,
    ) -> None:
        self.event_model = event_model or EventModelService.in_memory()
        self.adapter = adapter or TwilioSandboxWhatsAppAdapter()
        self.config = self.adapter.config
        self.guardian_address = guardian_address or self.config.guardian_address
        self.provider_messages = InMemoryProviderMessageRegistry()
        self.delivery_statuses = InMemoryDeliveryStatusRegistry()
        self.ingress = ChannelIngressService(
            event_model=self.event_model,
            provider_message_registry=self.provider_messages,
        )
        self._delivery_record_count = 0

    def handle_inbound(
        self,
        payload: Mapping[str, Any],
        *,
        protected_person_alias: str | None = None,
        guardian_alias: str | None = None,
        guardian_address: str | None = None,
    ) -> TwilioSandboxInboundWebhookResponse:
        before_events = len(self.event_model.repositories.events.list_all())
        inbound_alias = protected_person_alias or str(payload.get("ProfileName") or payload.get("From") or "")
        ingress_result = self.ingress.ingest_inbound(
            adapter=self.adapter,
            payload=payload,
            protected_person_alias=inbound_alias,
            guardian_alias=guardian_alias or "Twilio Sandbox Guardian",
        )

        outbound_messages: list[TwilioSandboxOutboundRecord] = []
        if not ingress_result.duplicate:
            outbound_messages.append(
                self._send_protected_reply(
                    to_address=ingress_result.inbound.from_address,
                    message_id=ingress_result.message_id,
                    case_id=ingress_result.case_id,
                )
            )

        if ingress_result.case_id and not ingress_result.duplicate:
            destination = guardian_address or self.guardian_address
            if destination:
                outbound_messages.append(
                    self._send_guardian_alert(
                        to_address=destination,
                        case_id=ingress_result.case_id,
                        message_id=ingress_result.message_id,
                        protected_person_alias=inbound_alias,
                    )
                )

        events = self.event_model.repositories.events.list_all()[before_events:]
        risk_score = None
        risk_level = None
        if ingress_result.risk_assessment_id:
            assessment = self.event_model.repositories.risk_assessments.get(ingress_result.risk_assessment_id)
            if assessment:
                risk_score = assessment.score
                risk_level = assessment.risk_level.value

        return TwilioSandboxInboundWebhookResponse(
            provider=self.adapter.provider.value,
            duplicate=ingress_result.duplicate,
            provider_message_id=ingress_result.inbound.provider_message_id,
            message_id=ingress_result.message_id,
            risk_assessment_id=ingress_result.risk_assessment_id,
            risk_score=risk_score,
            risk_level=risk_level,
            case_id=ingress_result.case_id,
            case_created=ingress_result.case_id is not None,
            protected_reply_sent=any(
                message.kind == OutboundMessageKind.PROTECTED_REPLY.value
                and message.status != DeliveryStatus.FAILED.value
                for message in outbound_messages
            ),
            guardian_notified=any(
                message.kind == OutboundMessageKind.GUARDIAN_ALERT.value
                and message.status != DeliveryStatus.FAILED.value
                for message in outbound_messages
            ),
            outbound_messages=outbound_messages,
            events=[event.event_type.value for event in events],
        )

    def handle_status_callback(self, payload: Mapping[str, Any]) -> TwilioSandboxStatusCallbackResponse:
        delivery_event = self.adapter.parse_status_callback(payload)
        self.delivery_statuses.update_from_callback(delivery_event)
        self._delivery_record_count += 1
        event = self.event_model.event_bus.publish_type(
            BotEventType.DELIVERY_STATUS_UPDATED,
            aggregate_type="outbound_message",
            aggregate_id=delivery_event.provider_message_id,
            payload={
                "provider": delivery_event.provider.value,
                "provider_message_id": delivery_event.provider_message_id,
                "status": delivery_event.status.value,
                "retryable": delivery_event.retryable,
                "error_code": delivery_event.error_code,
                "simulated": False,
            },
        )
        return TwilioSandboxStatusCallbackResponse(
            provider=delivery_event.provider.value,
            provider_message_id=delivery_event.provider_message_id,
            status=delivery_event.status.value,
            retryable=delivery_event.retryable,
            error_code=delivery_event.error_code,
            error_message=delivery_event.error_message,
            event_id=event.event_id,
        )

    def health(self) -> TwilioSandboxHealthResponse:
        config = self.config
        return TwilioSandboxHealthResponse(
            provider=self.adapter.provider.value,
            mode="sandbox",
            production=False,
            channel_provider=config.channel_provider,
            account_sid_configured=bool(config.account_sid),
            auth_token_configured=bool(config.auth_token),
            whatsapp_from_configured=bool(config.whatsapp_from),
            guardian_address_configured=bool(self.guardian_address),
            signature_validation_enabled=config.validate_signature,
            signature_secret_configured=bool(config.signature_secret),
            network_send_ready=config.can_send,
            delivery_records=self._delivery_record_count,
        )

    def _send_protected_reply(
        self,
        *,
        to_address: str,
        message_id: str | None,
        case_id: str | None,
    ) -> TwilioSandboxOutboundRecord:
        result = self.adapter.send_protected_reply(
            OutboundMessageRequest(
                provider=self.adapter.provider,
                to=to_address,
                body=(
                    "Guardian recebeu sua mensagem. Se houver pressa, pedido de Pix, codigo ou "
                    "sigilo, confirme por outro canal antes de responder."
                ),
                kind=OutboundMessageKind.PROTECTED_REPLY,
                relatedCaseId=case_id,
                relatedMessageId=message_id,
                metadata={"sandbox": True},
            )
        )
        return self._record_outbound(result, kind=OutboundMessageKind.PROTECTED_REPLY.value, case_id=case_id)

    def _send_guardian_alert(
        self,
        *,
        to_address: str,
        case_id: str,
        message_id: str | None,
        protected_person_alias: str,
    ) -> TwilioSandboxOutboundRecord:
        result = self.adapter.send_guardian_alert(
            OutboundMessageRequest(
                provider=self.adapter.provider,
                to=to_address,
                body=(
                    f"Alerta Guardian Sandbox: {protected_person_alias} recebeu uma mensagem suspeita. "
                    f"Caso {case_id} aguardando revisao."
                ),
                kind=OutboundMessageKind.GUARDIAN_ALERT,
                relatedCaseId=case_id,
                relatedMessageId=message_id,
                metadata={"sandbox": True},
            )
        )
        record = self._record_outbound(result, kind=OutboundMessageKind.GUARDIAN_ALERT.value, case_id=case_id)
        if result.status != DeliveryStatus.FAILED:
            self.event_model.event_bus.publish_type(
                BotEventType.GUARDIAN_NOTIFIED,
                aggregate_type="case",
                aggregate_id=case_id,
                payload={
                    "provider": result.provider.value,
                    "provider_message_id": result.provider_message_id,
                    "to_masked": mask_channel_address(result.to_address),
                    "status": result.status.value,
                    "simulated": False,
                },
            )
        return record

    def _record_outbound(
        self,
        result,
        *,
        kind: str,
        case_id: str | None,
    ) -> TwilioSandboxOutboundRecord:
        self.delivery_statuses.record_outbound(result, updated_at=datetime.now(timezone.utc))
        self._delivery_record_count += 1
        self.event_model.event_bus.publish_type(
            BotEventType.DELIVERY_STATUS_UPDATED,
            aggregate_type="outbound_message",
            aggregate_id=result.provider_message_id,
            payload={
                "provider": result.provider.value,
                "provider_message_id": result.provider_message_id,
                "status": result.status.value,
                "retryable": result.retryable,
                "to_masked": mask_channel_address(result.to_address),
                "simulated": False,
            },
        )
        return TwilioSandboxOutboundRecord(
            provider_message_id=result.provider_message_id,
            to_address_masked=mask_channel_address(result.to_address),
            kind=kind,
            status=result.status.value,
            retryable=result.retryable,
            simulated=result.simulated,
            related_case_id=case_id,
        )
