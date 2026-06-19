from __future__ import annotations

from typing import Any, Mapping, Optional

from app.channel_adapters.contract import (
    ChannelAdapter,
    WhatsAppChannelAdapter,
    normalize_provider_payload,
    receive_inbound_message,
)
from app.channel_adapters.idempotency import InMemoryProviderMessageRegistry
from app.channel_adapters.models import ChannelIngressResult, ChannelProvider, InboundMessage
from app.event_model import AuditLog, EventModelService, Guardian, ProtectedPerson


SIMULATED_PROVIDERS = {ChannelProvider.MOCK, ChannelProvider.MOCK_WHATSAPP}


class ChannelIngressService:
    def __init__(
        self,
        *,
        event_model: EventModelService,
        provider_message_registry: InMemoryProviderMessageRegistry | None = None,
    ) -> None:
        self._event_model = event_model
        self._provider_message_registry = provider_message_registry or InMemoryProviderMessageRegistry()

    def ingest_inbound(
        self,
        *,
        adapter: ChannelAdapter | WhatsAppChannelAdapter,
        payload: Mapping[str, Any],
        protected_person_alias: Optional[str] = None,
        guardian_alias: Optional[str] = None,
    ) -> ChannelIngressResult:
        inbound = normalize_provider_payload(adapter, payload)
        receive_inbound_message(adapter, inbound)
        return self.ingest_normalized(
            inbound=inbound,
            protected_person_alias=protected_person_alias,
            guardian_alias=guardian_alias,
        )

    def ingest_normalized(
        self,
        *,
        inbound: InboundMessage,
        protected_person_alias: Optional[str] = None,
        guardian_alias: Optional[str] = None,
    ) -> ChannelIngressResult:
        self._record_channel_audit("ChannelInboundReceived", inbound)
        first_seen = self._provider_message_registry.register_inbound(inbound)
        if not first_seen:
            self._record_channel_audit("ChannelInboundDuplicate", inbound)
            return ChannelIngressResult(inbound=inbound, duplicate=True)

        protected_person_alias_value = protected_person_alias or inbound.profile_name or inbound.from_address
        protected_person = (
            ProtectedPerson(
                protected_person_id=inbound.protected_person_id,
                alias=protected_person_alias_value,
            )
            if inbound.protected_person_id
            else ProtectedPerson(alias=protected_person_alias_value)
        )
        guardian = Guardian(alias=guardian_alias) if guardian_alias else None
        result = self._event_model.process_suspicious_message(
            protected_person=protected_person,
            guardian=guardian,
            body=inbound.body,
            channel=f"whatsapp:{inbound.provider.value}",
            provider_message_id=inbound.provider_message_id,
            simulated=inbound.provider in SIMULATED_PROVIDERS,
        )
        self._record_channel_audit(
            "ChannelInboundRouted",
            inbound,
            case_id=result.case.case_id if result.case else None,
            message_id=result.message.message_id,
        )
        return ChannelIngressResult(
            inbound=inbound,
            duplicate=False,
            message_id=result.message.message_id,
            risk_assessment_id=result.risk_assessment.risk_assessment_id,
            case_id=result.case.case_id if result.case else None,
            emitted_event_ids=result.emitted_event_ids,
        )

    def _record_channel_audit(
        self,
        action: str,
        inbound: InboundMessage,
        *,
        case_id: str | None = None,
        message_id: str | None = None,
    ) -> None:
        self._event_model.repositories.audit_logs.save(
            AuditLog(
                actor="channel_adapter",
                action=action,
                target_type="channel_message",
                target_id=inbound.external_message_id,
                payload={
                    "provider": inbound.provider.value,
                    "inbound_id": inbound.id,
                    "case_id": case_id or inbound.case_id,
                    "message_id": message_id,
                    "protected_person_id": inbound.protected_person_id,
                },
            )
        )
