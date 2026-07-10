from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from app.channel_adapters import (
    ChannelAdapter,
    ChannelProvider,
    ChannelIngressService,
    DeliveryStatus,
    DeliveryStatusRecord,
    EvolutionDemoAdapter,
    InMemoryDeliveryStatusRegistry,
    InMemoryProviderMessageRegistry,
    MockWhatsAppAdapter,
    OutboundMessageKind,
    OutboundMessageRequest,
    WhatsAppChannelAdapter,
)
from app.controlled_agents import ControlledAgentOrchestrator
from app.core.config import config
from app.dual_bot.models import (
    DualBotCaseContextResponse,
    DualBotEventSummary,
    DualBotFlowResponse,
    DualBotInboundRequest,
    DualBotOutboundMessage,
    DualBotProviderStatusResponse,
    GuardianFeedbackAction,
    GuardianFeedbackRequest,
    GuardianFeedbackResponse,
)
from app.event_model import (
    BotEvent,
    BotEventType,
    Case,
    CaseStatus,
    EventModelService,
    RiskAssessment,
    RiskLevel,
)
from app.pattern_intelligence import PatternDetectionResult, PatternIntelligenceService


FEEDBACK_STATUS_MAP = {
    GuardianFeedbackAction.CONFIRM_SCAM: CaseStatus.CONFIRMED_SCAM,
    GuardianFeedbackAction.FALSE_ALARM: CaseStatus.FALSE_ALARM,
    GuardianFeedbackAction.NEEDS_REVIEW: CaseStatus.UNDER_REVIEW,
    GuardianFeedbackAction.MARK_RESOLVED: CaseStatus.RESOLVED,
}

DUAL_BOT_PROVIDER_ENV = "DUAL_BOT_CHANNEL_PROVIDER"

PROVIDER_ALIASES = {
    "mock": ChannelProvider.MOCK,
    "mock_whatsapp": ChannelProvider.MOCK,
    "whatsapp_mock": ChannelProvider.MOCK,
    "evolution": ChannelProvider.EVOLUTION_DEMO,
    "evolution_demo": ChannelProvider.EVOLUTION_DEMO,
}


def create_dual_bot_adapter(provider: str | ChannelProvider | None = None):
    requested = str(provider or os.getenv(DUAL_BOT_PROVIDER_ENV) or "mock").strip().lower()
    selected = PROVIDER_ALIASES.get(requested, ChannelProvider.MOCK)
    if selected == ChannelProvider.EVOLUTION_DEMO:
        return EvolutionDemoAdapter()
    return MockWhatsAppAdapter()


def _event_summaries(events: list[BotEvent]) -> list[DualBotEventSummary]:
    return [
        DualBotEventSummary(
            event_id=event.event_id,
            event_type=event.event_type.value,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            occurred_at=event.occurred_at,
        )
        for event in events
    ]


def _message_summary(body: str, *, limit: int = 180) -> str:
    normalized = " ".join(body.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3].rstrip()}..."


class OutboundAuditMixin:
    adapter: ChannelAdapter | WhatsAppChannelAdapter
    delivery_statuses: InMemoryDeliveryStatusRegistry
    event_model: EventModelService

    def _record_outbound(
        self,
        *,
        result,
        body: str,
        kind: OutboundMessageKind,
        related_case_id: str | None,
    ) -> tuple[DualBotOutboundMessage, DeliveryStatusRecord]:
        pending = self.delivery_statuses.record_outbound(result, updated_at=datetime.now(timezone.utc))
        delivery_record = pending
        if result.simulated:
            callback = self.adapter.parse_status_callback(
                {
                    "providerMessageId": result.provider_message_id,
                    "MessageSid": result.provider_message_id,
                    "status": DeliveryStatus.DELIVERED.value,
                    "MessageStatus": DeliveryStatus.DELIVERED.value,
                    "timestamp": datetime.now(timezone.utc),
                }
            )
            delivery_record = self.delivery_statuses.update_from_callback(callback)

        self.event_model.event_bus.publish_type(
            BotEventType.DELIVERY_STATUS_UPDATED,
            aggregate_type="outbound_message",
            aggregate_id=result.provider_message_id,
            payload={
                "provider": result.provider.value,
                "provider_message_id": result.provider_message_id,
                "status": delivery_record.status.value,
                "retryable": delivery_record.retryable,
                "kind": kind.value,
                "related_case_id": related_case_id,
                "simulated": result.simulated,
            },
        )
        return (
            DualBotOutboundMessage(
                provider_message_id=result.provider_message_id,
                to_address=result.to_address,
                body=body,
                kind=kind.value,
                status=delivery_record.status.value,
                simulated=result.simulated,
                retryable=delivery_record.retryable,
                related_case_id=related_case_id,
            ),
            delivery_record,
        )


class ResponsibleBotService(OutboundAuditMixin):
    def __init__(
        self,
        *,
        event_model: EventModelService,
        adapter: ChannelAdapter | WhatsAppChannelAdapter,
        delivery_statuses: InMemoryDeliveryStatusRegistry,
        pattern_intelligence: PatternIntelligenceService | None = None,
        agent_orchestrator: ControlledAgentOrchestrator | None = None,
    ) -> None:
        self.event_model = event_model
        self.adapter = adapter
        self.delivery_statuses = delivery_statuses
        self.pattern_intelligence = pattern_intelligence
        self.agent_orchestrator = agent_orchestrator

    def send_alert(
        self,
        *,
        guardian_address: str,
        protected_person_alias: str,
        assessment: RiskAssessment,
        case: Case,
        message_id: str | None,
        message_summary: str,
        recommended_action: str,
        language: str,
    ) -> DualBotOutboundMessage:
        if self.agent_orchestrator is not None:
            alert_decision = self.agent_orchestrator.responsible_alert_agent.generate(
                protected_person_alias=protected_person_alias,
                assessment=assessment,
                case_id=case.case_id,
                message_summary=message_summary,
                recommended_action=recommended_action,
            )
            self.agent_orchestrator.publish(BotEventType.RESPONSIBLE_ALERT_GENERATED, alert_decision)
            body = alert_decision.body
        else:
            body = (
                f"Alerta Guardian: {protected_person_alias} recebeu uma mensagem com sinais de risco. "
                f"Risco: {assessment.risk_level.value}. Sinais: {', '.join(assessment.signals) or 'sem sinais fortes'}. "
                f"Caso {case.case_id}. Acao recomendada: {recommended_action}"
            )
        result = self.adapter.send_guardian_alert(
            OutboundMessageRequest(
                provider=self.adapter.provider,
                to=guardian_address,
                body=body,
                kind=OutboundMessageKind.GUARDIAN_ALERT,
                relatedCaseId=case.case_id,
                relatedMessageId=message_id,
                metadata={
                    "risk_level": assessment.risk_level.value,
                    "risk_score": assessment.score,
                    "signals": assessment.signals,
                },
            )
        )
        outbound, delivery = self._record_outbound(
            result=result,
            body=body,
            kind=OutboundMessageKind.GUARDIAN_ALERT,
            related_case_id=case.case_id,
        )
        if delivery.status != DeliveryStatus.FAILED:
            self.event_model.event_bus.publish_type(
                BotEventType.RESPONSIBLE_NOTIFIED,
                aggregate_type="case",
                aggregate_id=case.case_id,
                source="channel_adapter",
                case_id=case.case_id,
                protected_person_id=case.protected_person_id,
                payload={
                    "provider": result.provider.value,
                    "provider_message_id": result.provider_message_id,
                    "risk_level": assessment.risk_level.value,
                    "risk_score": assessment.score,
                    "signals": assessment.signals,
                    "status": delivery.status.value,
                    "simulated": result.simulated,
                },
            )
        return outbound

    def get_case_context(self, case_id: str) -> DualBotCaseContextResponse:
        case = self.event_model.cases.get_case_by_id(case_id)
        message = self.event_model.repositories.messages.get(case.source_message_id)
        assessment = self.event_model.repositories.risk_assessments.get(case.risk_assessment_id)
        protected_person = self.event_model.repositories.protected_people.get(case.protected_person_id)
        guardian = self.event_model.repositories.guardians.get(case.guardian_id) if case.guardian_id else None
        if message is None or assessment is None or protected_person is None:
            raise ValueError(f"Case context is incomplete: {case_id}")

        aggregate_ids = {
            case.case_id,
            case.source_message_id,
            case.risk_assessment_id,
        }
        history = [
            event
            for event in self.event_model.repositories.events.list_all()
            if event.aggregate_id in aggregate_ids
            or event.payload.get("case_id") == case.case_id
            or event.payload.get("related_case_id") == case.case_id
        ]
        return DualBotCaseContextResponse(
            case_id=case.case_id,
            status=case.status.value,
            protected_person_alias=protected_person.alias,
            guardian_alias=guardian.alias if guardian else None,
            risk_score=case.risk_score,
            risk_level=case.risk_level.value,
            risk_signals=assessment.signals,
            message_summary=_message_summary(message.body),
            source_message=message.body,
            history=_event_summaries(history),
        )

    def record_feedback(self, case_id: str, request: GuardianFeedbackRequest) -> GuardianFeedbackResponse:
        current = self.event_model.cases.get_case_by_id(case_id)
        next_status = FEEDBACK_STATUS_MAP[request.action]
        updated = self.event_model.cases.update_case_status(case_id, next_status)
        pattern_feedback = None
        if self.pattern_intelligence is not None:
            pattern_feedback = self.pattern_intelligence.record_feedback(
                case_id=case_id,
                feedback_action=request.action.value,
                note=request.note,
            )
        event = self.event_model.event_bus.publish_type(
            BotEventType.GUARDIAN_FEEDBACK_RECEIVED,
            aggregate_type="case",
            aggregate_id=case_id,
            source="guardian_console",
            actor=request.guardian_alias,
            case_id=case_id,
            protected_person_id=updated.protected_person_id,
            payload={
                "action": request.action.value,
                "guardian_alias": request.guardian_alias,
                "note": request.note,
                "previous_status": current.status.value,
                "new_status": updated.status.value,
                "pattern_feedback_id": pattern_feedback.feedback_id if pattern_feedback else None,
                "pattern_candidate_ids": pattern_feedback.candidate_ids if pattern_feedback else [],
                "pattern_expected_label": pattern_feedback.expected_label if pattern_feedback else None,
                "simulated": True,
            },
        )
        if request.action == GuardianFeedbackAction.FALSE_ALARM:
            self.event_model.event_bus.publish_type(
                BotEventType.FALSE_POSITIVE_MARKED,
                aggregate_type="case",
                aggregate_id=case_id,
                source="guardian_console",
                actor=request.guardian_alias,
                case_id=case_id,
                protected_person_id=updated.protected_person_id,
                payload={
                    "previous_status": current.status.value,
                    "new_status": updated.status.value,
                    "note": request.note,
                },
            )
        if request.action == GuardianFeedbackAction.MARK_RESOLVED:
            self.event_model.event_bus.publish_type(
                BotEventType.CASE_RESOLVED,
                aggregate_type="case",
                aggregate_id=case_id,
                source="guardian_console",
                actor=request.guardian_alias,
                case_id=case_id,
                protected_person_id=updated.protected_person_id,
                payload={
                    "previous_status": current.status.value,
                    "new_status": updated.status.value,
                    "note": request.note,
                },
            )
        return GuardianFeedbackResponse(
            case_id=case_id,
            action=request.action,
            previous_status=current.status.value,
            new_status=updated.status.value,
            event_id=event.event_id,
            audit_event=event.event_type.value,
        )


class ProtectedBotService(OutboundAuditMixin):
    def __init__(
        self,
        *,
        event_model: EventModelService,
        adapter: ChannelAdapter | WhatsAppChannelAdapter,
        provider_messages: InMemoryProviderMessageRegistry,
        delivery_statuses: InMemoryDeliveryStatusRegistry,
        responsible_bot: ResponsibleBotService,
        pattern_intelligence: PatternIntelligenceService | None = None,
        agent_orchestrator: ControlledAgentOrchestrator | None = None,
    ) -> None:
        self.event_model = event_model
        self.adapter = adapter
        self.provider_messages = provider_messages
        self.delivery_statuses = delivery_statuses
        self.responsible_bot = responsible_bot
        self.pattern_intelligence = pattern_intelligence
        self.agent_orchestrator = agent_orchestrator
        self.ingress = ChannelIngressService(
            event_model=event_model,
            provider_message_registry=provider_messages,
        )

    def receive_message(
        self,
        *,
        payload: Mapping[str, Any],
        protected_person_alias: str | None,
        guardian_alias: str | None,
        guardian_address: str,
        language: str = "pt",
    ) -> DualBotFlowResponse:
        before_events = len(self.event_model.repositories.events.list_all())
        ingress_result = self.ingress.ingest_inbound(
            adapter=self.adapter,
            payload=payload,
            protected_person_alias=protected_person_alias,
            guardian_alias=guardian_alias,
        )
        guardian_alert = None
        assessment = None
        case = None
        pattern_detection: PatternDetectionResult | None = None
        stored_message = None
        triage_recommended_action = "Pausar e confirmar por canal confiavel antes de qualquer acao."

        if ingress_result.risk_assessment_id:
            assessment = self.event_model.repositories.risk_assessments.get(ingress_result.risk_assessment_id)
        if ingress_result.case_id:
            case = self.event_model.repositories.cases.get(ingress_result.case_id)

        if not ingress_result.duplicate and assessment is not None:
            resolved_protected_alias = (
                protected_person_alias
                or ingress_result.inbound.profile_name
                or ingress_result.inbound.from_address
            )
            stored_message = (
                self.event_model.repositories.messages.get(ingress_result.message_id)
                if ingress_result.message_id
                else None
            )
            if stored_message is not None and self.pattern_intelligence is not None:
                pattern_detection = self.pattern_intelligence.detect(
                    message=stored_message,
                    protected_person_id=stored_message.protected_person_id,
                    protected_person_alias=resolved_protected_alias,
                    sender_address=ingress_result.inbound.from_address,
                    case_id=ingress_result.case_id,
                )
            if stored_message is not None and self.agent_orchestrator is not None:
                triage_decision = self.agent_orchestrator.triage_agent.decide(
                    inbound=ingress_result.inbound,
                    message=stored_message,
                    assessment=assessment,
                    case=case,
                    pattern_detection=pattern_detection,
                )
                triage_recommended_action = triage_decision.recommended_action
                self.agent_orchestrator.publish(BotEventType.TRIAGE_DECISION_CREATED, triage_decision)
                if pattern_detection is not None:
                    pattern_review = self.agent_orchestrator.pattern_review_agent.review(
                        pattern_detection=pattern_detection
                    )
                    self.agent_orchestrator.publish(BotEventType.PATTERN_REVIEW_GENERATED, pattern_review)
            # The bot never replies to the person who sent the message. The only
            # outbound recipient is the single configured trusted contact
            # (guardian); the analysis itself lives in the backend/console.
            # Only alert for explicit scams (HIGH risk) — MEDIUM cases stay in
            # the console for review without sending a WhatsApp message.
            if case is not None and assessment.risk_level == RiskLevel.HIGH:
                guardian_alert = self.responsible_bot.send_alert(
                    guardian_address=guardian_address,
                    protected_person_alias=resolved_protected_alias,
                    assessment=assessment,
                    case=case,
                    message_id=ingress_result.message_id,
                    message_summary=_message_summary(stored_message.body) if stored_message else "",
                    recommended_action=triage_recommended_action,
                    language=language,
                )
                if stored_message is not None and self.agent_orchestrator is not None:
                    case_summary = self.agent_orchestrator.case_summary_agent.summarize(
                        case=case,
                        message=stored_message,
                        protected_person_alias=resolved_protected_alias,
                        assessment=assessment,
                        pattern_detection=pattern_detection,
                        safe_reply=None,
                        responsible_alert=guardian_alert.body if guardian_alert else None,
                    )
                    self.agent_orchestrator.publish(BotEventType.CASE_SUMMARY_GENERATED, case_summary)

        events = self.event_model.repositories.events.list_all()[before_events:]
        return DualBotFlowResponse(
            provider=ingress_result.inbound.provider.value,
            duplicate=ingress_result.duplicate,
            provider_message_id=ingress_result.inbound.provider_message_id,
            message_id=ingress_result.message_id,
            risk_assessment_id=ingress_result.risk_assessment_id,
            risk_score=assessment.score if assessment else None,
            risk_level=assessment.risk_level.value if assessment else None,
            risk_signals=assessment.signals if assessment else [],
            case_id=ingress_result.case_id,
            case_created=ingress_result.case_id is not None,
            guardian_alert=guardian_alert,
            pattern_detection=pattern_detection,
            events=[event.event_type.value for event in events],
        )

class DualBotFlowService:
    def __init__(
        self,
        *,
        adapter: ChannelAdapter | WhatsAppChannelAdapter | None = None,
        event_model: EventModelService | None = None,
        default_guardian_address: str | None = None,
        pattern_intelligence: PatternIntelligenceService | None = None,
    ) -> None:
        self.event_model = event_model or EventModelService.in_memory()
        self.adapter = adapter or create_dual_bot_adapter()
        # Single trusted contact resolved from config (TRUSTED_CONTACT + legacy
        # fallbacks). The placeholder is a last resort for the local mock demo.
        self.default_guardian_address = (
            default_guardian_address or config.trusted_contact or "+5511888880001"
        )
        self.pattern_intelligence = pattern_intelligence or PatternIntelligenceService(
            event_bus=self.event_model.event_bus
        )
        self.agent_orchestrator = ControlledAgentOrchestrator(self.event_model.event_bus)
        self.provider_messages = InMemoryProviderMessageRegistry()
        self.delivery_statuses = InMemoryDeliveryStatusRegistry()
        self.responsible_bot = ResponsibleBotService(
            event_model=self.event_model,
            adapter=self.adapter,
            delivery_statuses=self.delivery_statuses,
            pattern_intelligence=self.pattern_intelligence,
            agent_orchestrator=self.agent_orchestrator,
        )
        self.protected_bot = ProtectedBotService(
            event_model=self.event_model,
            adapter=self.adapter,
            provider_messages=self.provider_messages,
            delivery_statuses=self.delivery_statuses,
            responsible_bot=self.responsible_bot,
            pattern_intelligence=self.pattern_intelligence,
            agent_orchestrator=self.agent_orchestrator,
        )

    @classmethod
    def from_env(cls) -> "DualBotFlowService":
        return cls(
            adapter=create_dual_bot_adapter(),
            default_guardian_address=config.trusted_contact or None,
        )

    def status(self) -> DualBotProviderStatusResponse:
        return DualBotProviderStatusResponse(active_provider=self.adapter.provider.value)

    def receive_mock_message(self, request: DualBotInboundRequest) -> DualBotFlowResponse:
        payload = request.model_dump(by_alias=True, exclude_none=True)
        if request.provider_message_id is None:
            payload["providerMessageId"] = f"dual-bot-mock-in-{uuid4().hex}"
        mock_service = (
            self
            if isinstance(self.adapter, MockWhatsAppAdapter)
            else DualBotFlowService(
                adapter=MockWhatsAppAdapter(),
                event_model=self.event_model,
                default_guardian_address=self.default_guardian_address,
                pattern_intelligence=self.pattern_intelligence,
            )
        )
        return mock_service.protected_bot.receive_message(
            payload=payload,
            protected_person_alias=request.protected_person_alias,
            guardian_alias=request.guardian_alias,
            guardian_address=request.guardian_address,
            language=request.language,
        )

    def receive_provider_message(
        self,
        *,
        payload: Mapping[str, Any],
        protected_person_alias: str | None = None,
        guardian_alias: str | None = None,
        guardian_address: str | None = None,
        language: str = "pt",
    ) -> DualBotFlowResponse:
        return self.protected_bot.receive_message(
            payload=payload,
            protected_person_alias=protected_person_alias,
            guardian_alias=guardian_alias,
            guardian_address=guardian_address or self.default_guardian_address,
            language=language,
        )

    def get_case_context(self, case_id: str) -> DualBotCaseContextResponse:
        return self.responsible_bot.get_case_context(case_id)

    def record_guardian_feedback(
        self,
        case_id: str,
        request: GuardianFeedbackRequest,
    ) -> GuardianFeedbackResponse:
        return self.responsible_bot.record_feedback(case_id, request)
