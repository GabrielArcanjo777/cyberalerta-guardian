from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from app.channel_adapters import (
    ChannelIngressService,
    DeliveryStatus,
    InMemoryDeliveryStatusRegistry,
    InMemoryProviderMessageRegistry,
    OutboundMessage,
    OutboundMessageKind,
)
from app.channel_adapters.evolution_demo_adapter import (
    EvolutionDemoAdapter,
    EvolutionDemoConfig,
    EvolutionDemoIgnoredEvent,
    EvolutionDemoPayloadError,
)
from app.dual_bot.messages import protected_reply_for, responsible_alert_for
from app.event_model import BotEventType, EventModelService
from app.evolution_demo.models import (
    EvolutionDemoHealthResponse,
    EvolutionDemoOutboundRecord,
    EvolutionDemoWebhookResponse,
)


def mask_evolution_address(value: str | None) -> str:
    if not value:
        return ""
    stripped = value.removeprefix("whatsapp:")
    if "@" in stripped:
        stripped = stripped.split("@", 1)[0]
    if len(stripped) <= 4:
        return "*" * len(stripped)
    return f"{'*' * max(len(stripped) - 4, 0)}{stripped[-4:]}"


class EvolutionDemoService:
    def __init__(
        self,
        *,
        adapter: EvolutionDemoAdapter | None = None,
        event_model: EventModelService | None = None,
        guardian_address: str | None = None,
    ) -> None:
        self.event_model = event_model or EventModelService.in_memory()
        self.adapter = adapter or EvolutionDemoAdapter()
        self.config: EvolutionDemoConfig = self.adapter.config
        self.guardian_address = (
            guardian_address if guardian_address is not None else self.config.guardian_address
        )
        self.provider_messages = InMemoryProviderMessageRegistry()
        self.delivery_statuses = InMemoryDeliveryStatusRegistry()
        self.ingress = ChannelIngressService(
            event_model=self.event_model,
            provider_message_registry=self.provider_messages,
        )
        self._delivery_record_count = 0

    def health(self) -> EvolutionDemoHealthResponse:
        return EvolutionDemoHealthResponse(
            provider=self.adapter.provider.value,
            mode="demo",
            production=False,
            api_url_configured=bool(self.config.api_url),
            api_key_configured=bool(self.config.api_key),
            instance_name_configured=bool(self.config.instance_name),
            guardian_address_configured=bool(self.guardian_address),
            network_send_ready=self.config.can_send,
            delivery_records=self._delivery_record_count,
        )

    def handle_webhook(
        self,
        payload: Mapping[str, Any],
        *,
        guardian_alias: str | None = None,
        guardian_address: str | None = None,
    ) -> EvolutionDemoWebhookResponse:
        before_events = len(self.event_model.repositories.events.list_all())
        try:
            inbound = self.adapter.parseProviderPayload(payload)
        except EvolutionDemoIgnoredEvent as exc:
            return self._ignored_response(str(exc))
        except EvolutionDemoPayloadError:
            raise

        ingress_result = self.ingress.ingest_normalized(
            inbound=inbound,
            protected_person_alias=inbound.profile_name or inbound.from_address,
            guardian_alias=guardian_alias or "Evolution Demo Guardian",
        )

        outbound_messages: list[EvolutionDemoOutboundRecord] = []
        assessment = None
        case = None
        protected_person_alias = inbound.profile_name or inbound.from_address
        if ingress_result.risk_assessment_id:
            assessment = self.event_model.repositories.risk_assessments.get(
                ingress_result.risk_assessment_id
            )
        if ingress_result.case_id:
            case = self.event_model.repositories.cases.get(ingress_result.case_id)

        if not ingress_result.duplicate and assessment is not None:
            outbound_messages.append(
                self._send_protected_reply(
                    to_address=inbound.from_address,
                    body=protected_reply_for(
                        assessment,
                        case_created=ingress_result.case_id is not None,
                        language="pt",
                    ),
                    message_id=ingress_result.message_id,
                    case_id=ingress_result.case_id,
                    protected_person_id=case.protected_person_id if case else None,
                )
            )

        if not ingress_result.duplicate and case is not None and assessment is not None:
            destination = guardian_address or self.guardian_address
            alert_body = responsible_alert_for(
                protected_person_alias=protected_person_alias,
                risk_level=assessment.risk_level.value,
                signals=assessment.signals,
                case_id=case.case_id,
                language="pt",
            )
            if destination:
                outbound_messages.append(
                    self._send_guardian_alert(
                        to_address=destination,
                        body=alert_body,
                        message_id=ingress_result.message_id,
                        case_id=case.case_id,
                        protected_person_id=case.protected_person_id,
                    )
                )
            else:
                outbound_messages.append(
                    self._simulate_guardian_alert(
                        case_id=case.case_id,
                        protected_person_id=case.protected_person_id,
                    )
                )

        events = self.event_model.repositories.events.list_all()[before_events:]
        risk_score = assessment.score if assessment else None
        risk_level = assessment.risk_level.value if assessment else None
        return EvolutionDemoWebhookResponse(
            provider=self.adapter.provider.value,
            accepted=True,
            duplicate=ingress_result.duplicate,
            provider_message_id=inbound.external_message_id,
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

    def _ignored_response(self, message: str) -> EvolutionDemoWebhookResponse:
        return EvolutionDemoWebhookResponse(
            provider=self.adapter.provider.value,
            accepted=True,
            ignored=True,
            duplicate=False,
            case_created=False,
            protected_reply_sent=False,
            guardian_notified=False,
            events=[],
            demo_notice=f"{message} EvolutionDemoAdapter remains demo-only.",
        )

    def _send_protected_reply(
        self,
        *,
        to_address: str,
        body: str,
        message_id: str | None,
        case_id: str | None,
        protected_person_id: str | None,
    ) -> EvolutionDemoOutboundRecord:
        result = self.adapter.sendMessage(
            OutboundMessage(
                provider=self.adapter.provider,
                to=to_address,
                body=body,
                templateName="protected_reply",
                metadata={
                    "kind": OutboundMessageKind.PROTECTED_REPLY.value,
                    "related_message_id": message_id,
                    "demo": True,
                },
                caseId=case_id,
                protectedPersonId=protected_person_id,
            )
        )
        record = self._record_outbound(
            result,
            kind=OutboundMessageKind.PROTECTED_REPLY.value,
            case_id=case_id,
        )
        self.event_model.event_bus.publish_type(
            BotEventType.SAFE_REPLY_SENT,
            aggregate_type="message",
            aggregate_id=message_id or result.provider_message_id,
            source="channel_adapter",
            case_id=case_id,
            protected_person_id=protected_person_id,
            payload={
                "provider": result.provider.value,
                "provider_message_id": result.provider_message_id,
                "status": result.status.value,
                "related_case_id": case_id,
                "demo": True,
                "simulated": result.simulated,
            },
        )
        self.event_model.event_bus.publish_type(
            BotEventType.PROTECTED_PERSON_REPLIED,
            aggregate_type="message",
            aggregate_id=message_id or result.provider_message_id,
            source="channel_adapter",
            case_id=case_id,
            protected_person_id=protected_person_id,
            payload={
                "provider": result.provider.value,
                "provider_message_id": result.provider_message_id,
                "status": result.status.value,
                "related_case_id": case_id,
                "demo": True,
                "simulated": result.simulated,
            },
        )
        return record

    def _send_guardian_alert(
        self,
        *,
        to_address: str,
        body: str,
        message_id: str | None,
        case_id: str,
        protected_person_id: str,
    ) -> EvolutionDemoOutboundRecord:
        result = self.adapter.sendMessage(
            OutboundMessage(
                provider=self.adapter.provider,
                to=to_address,
                body=body,
                templateName="guardian_alert",
                metadata={
                    "kind": OutboundMessageKind.GUARDIAN_ALERT.value,
                    "related_message_id": message_id,
                    "demo": True,
                },
                caseId=case_id,
                protectedPersonId=protected_person_id,
            )
        )
        record = self._record_outbound(
            result,
            kind=OutboundMessageKind.GUARDIAN_ALERT.value,
            case_id=case_id,
        )
        if result.status != DeliveryStatus.FAILED:
            self._publish_responsible_notified(
                case_id=case_id,
                protected_person_id=protected_person_id,
                provider_message_id=result.provider_message_id,
                status=result.status.value,
                to_address=to_address,
                simulated=result.simulated,
            )
        return record

    def _simulate_guardian_alert(
        self,
        *,
        case_id: str,
        protected_person_id: str,
    ) -> EvolutionDemoOutboundRecord:
        provider_message_id = f"evolution-demo-simulated-guardian-{uuid4().hex}"
        self._publish_responsible_notified(
            case_id=case_id,
            protected_person_id=protected_person_id,
            provider_message_id=provider_message_id,
            status=DeliveryStatus.DELIVERED.value,
            to_address="simulated_guardian",
            simulated=True,
        )
        return EvolutionDemoOutboundRecord(
            provider_message_id=provider_message_id,
            to_address_masked="simulated_guardian",
            kind=OutboundMessageKind.GUARDIAN_ALERT.value,
            status=DeliveryStatus.DELIVERED.value,
            retryable=False,
            simulated=True,
            related_case_id=case_id,
        )

    def _record_outbound(
        self,
        result,
        *,
        kind: str,
        case_id: str | None,
    ) -> EvolutionDemoOutboundRecord:
        self.delivery_statuses.record_outbound(result, updated_at=datetime.now(timezone.utc))
        self._delivery_record_count += 1
        self.event_model.event_bus.publish_type(
            BotEventType.DELIVERY_STATUS_UPDATED,
            aggregate_type="outbound_message",
            aggregate_id=result.provider_message_id,
            source="channel_adapter",
            case_id=case_id,
            payload={
                "provider": result.provider.value,
                "provider_message_id": result.provider_message_id,
                "status": result.status.value,
                "retryable": result.retryable,
                "to_masked": mask_evolution_address(result.to_address),
                "kind": kind,
                "demo": True,
                "simulated": result.simulated,
            },
        )
        return EvolutionDemoOutboundRecord(
            provider_message_id=result.provider_message_id,
            to_address_masked=mask_evolution_address(result.to_address),
            kind=kind,
            status=result.status.value,
            retryable=result.retryable,
            simulated=result.simulated,
            related_case_id=case_id,
        )

    def _publish_responsible_notified(
        self,
        *,
        case_id: str,
        protected_person_id: str,
        provider_message_id: str,
        status: str,
        to_address: str,
        simulated: bool,
    ) -> None:
        self.event_model.event_bus.publish_type(
            BotEventType.RESPONSIBLE_NOTIFIED,
            aggregate_type="case",
            aggregate_id=case_id,
            source="channel_adapter",
            case_id=case_id,
            protected_person_id=protected_person_id,
            payload={
                "provider": self.adapter.provider.value,
                "provider_message_id": provider_message_id,
                "status": status,
                "to_masked": mask_evolution_address(to_address),
                "demo": True,
                "simulated": simulated,
            },
        )
