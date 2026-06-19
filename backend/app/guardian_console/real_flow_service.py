from __future__ import annotations

from typing import Optional

from app.consent import ConsentService
from app.dual_bot import (
    DualBotFlowService,
    GuardianFeedbackRequest,
    protected_reply_for,
    responsible_alert_for,
)
from app.event_model import BotEvent, BotEventType, Case, CaseStatus, Message, RiskAssessment
from app.guardian_console.real_flow_models import (
    GuardianConsoleActivationState,
    GuardianConsoleAgentDecisionView,
    GuardianConsoleAuditLogView,
    GuardianConsoleBotState,
    GuardianConsoleCaseStateView,
    GuardianConsoleChannelStatusView,
    GuardianConsoleConsentView,
    GuardianConsoleDeliveryView,
    GuardianConsoleFeedbackView,
    GuardianConsoleMessageView,
    GuardianConsoleOutboundView,
    GuardianConsolePatternView,
    GuardianConsoleProtectedPersonView,
    GuardianConsoleRealCaseDetail,
    GuardianConsoleRealCaseListResponse,
    GuardianConsoleRealCaseSummary,
    GuardianConsoleRealStatusResponse,
    GuardianConsoleResponsibleContactView,
    GuardianConsoleRiskAssessmentView,
    GuardianConsoleTimelineEvent,
)


OPEN_CASE_STATUSES = {CaseStatus.NEW, CaseStatus.UNDER_REVIEW, CaseStatus.PAUSED}
FEEDBACK_ACTIONS = ["confirm_scam", "false_alarm", "needs_review", "mark_resolved"]


EVENT_LABELS = {
    BotEventType.MESSAGE_RECEIVED: "Mensagem recebida",
    BotEventType.SUSPICIOUS_MESSAGE_RECEIVED: "Mensagem recebida",
    BotEventType.RISK_ASSESSMENT_CREATED: "Risco avaliado",
    BotEventType.CASE_CREATED: "Caso criado",
    BotEventType.SAFE_REPLY_SENT: "Resposta segura enviada",
    BotEventType.RESPONSIBLE_ALERT_QUEUED: "Alerta ao responsavel enfileirado",
    BotEventType.RESPONSIBLE_NOTIFIED: "Responsavel notificado",
    BotEventType.CASE_RESOLVED: "Caso resolvido",
    BotEventType.FALSE_POSITIVE_MARKED: "Falso positivo marcado",
    BotEventType.PATTERN_CANDIDATE_DETECTED: "Padrao candidato detectado",
    BotEventType.TRIAGE_DECISION_CREATED: "Triagem controlada",
    BotEventType.SAFE_REPLY_GENERATED: "Resposta segura gerada",
    BotEventType.RESPONSIBLE_ALERT_GENERATED: "Alerta ao responsavel gerado",
    BotEventType.CASE_SUMMARY_GENERATED: "Resumo do caso gerado",
    BotEventType.PATTERN_REVIEW_GENERATED: "Revisao de padrao gerada",
    BotEventType.AGENT_FALLBACK_USED: "Fallback de agente aplicado",
    BotEventType.GUARDIAN_ALERT_TRIGGERED: "Alerta preparado",
    BotEventType.PROTECTED_PERSON_REPLIED: "Bot Protegido respondeu",
    BotEventType.GUARDIAN_NOTIFIED: "Responsavel notificado",
    BotEventType.GUARDIAN_FEEDBACK_RECEIVED: "Feedback registrado",
    BotEventType.DELIVERY_STATUS_UPDATED: "Status de entrega atualizado",
    BotEventType.PATTERN_DETECTED: "Padrao detectado",
}


def _summary(text: str, *, limit: int = 150) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 3].rstrip()}..."


def _recommended_action(case: Case, assessment: RiskAssessment) -> str:
    if case.status == CaseStatus.CONFIRMED_SCAM:
        return "Golpe confirmado. Preserve evidencias e mantenha a pessoa protegida orientada."
    if case.status == CaseStatus.FALSE_ALARM:
        return "Falso positivo registrado. Use o feedback para ajustar a operacao futura."
    if case.status == CaseStatus.RESOLVED:
        return "Caso resolvido. Historico mantido para auditoria."
    if assessment.risk_level.value == "high":
        return "Pausar pagamento ou resposta e confirmar por canal independente."
    if assessment.risk_level.value == "medium":
        return "Revisar a mensagem e confirmar identidade por outro canal."
    return "Monitorar e orientar verificacao se houver dinheiro, codigo ou pressa."


def _event_description(event: BotEvent) -> str:
    payload = event.payload
    if event.event_type in {BotEventType.MESSAGE_RECEIVED, BotEventType.SUSPICIOUS_MESSAGE_RECEIVED}:
        return f"Mensagem registrada no canal {payload.get('channel', 'desconhecido')}."
    if event.event_type == BotEventType.RISK_ASSESSMENT_CREATED:
        signals = payload.get("signals") or []
        signal_text = ", ".join(signals) if signals else "sem sinais fortes"
        return f"Score {payload.get('score')} com risco {payload.get('risk_level')}. Sinais: {signal_text}."
    if event.event_type == BotEventType.CASE_CREATED:
        return f"Caso aberto com score {payload.get('risk_score')} e status {payload.get('status')}."
    if event.event_type in {
        BotEventType.RESPONSIBLE_ALERT_QUEUED,
        BotEventType.GUARDIAN_ALERT_TRIGGERED,
    }:
        return "Alerta ao responsavel foi enfileirado pelo Bot Responsavel."
    if event.event_type in {BotEventType.SAFE_REPLY_SENT, BotEventType.PROTECTED_PERSON_REPLIED}:
        return f"Resposta curta enviada pelo Bot Protegido. Status: {payload.get('status')}."
    if event.event_type in {BotEventType.RESPONSIBLE_NOTIFIED, BotEventType.GUARDIAN_NOTIFIED}:
        return f"Responsavel notificado. Status: {payload.get('status')}."
    if event.event_type == BotEventType.GUARDIAN_FEEDBACK_RECEIVED:
        return f"Acao {payload.get('action')} alterou status de {payload.get('previous_status')} para {payload.get('new_status')}."
    if event.event_type == BotEventType.FALSE_POSITIVE_MARKED:
        return "Responsavel marcou o caso como falso positivo."
    if event.event_type == BotEventType.CASE_RESOLVED:
        return "Responsavel marcou o caso como resolvido."
    if event.event_type == BotEventType.DELIVERY_STATUS_UPDATED:
        return f"{payload.get('kind', 'mensagem')} ficou com status {payload.get('status')}."
    if event.event_type in {
        BotEventType.PATTERN_CANDIDATE_DETECTED,
        BotEventType.PATTERN_DETECTED,
    }:
        return str(payload.get("explanation") or "Pattern Intelligence registrou sinais explicaveis.")
    if event.event_type in {
        BotEventType.TRIAGE_DECISION_CREATED,
        BotEventType.SAFE_REPLY_GENERATED,
        BotEventType.RESPONSIBLE_ALERT_GENERATED,
        BotEventType.CASE_SUMMARY_GENERATED,
        BotEventType.PATTERN_REVIEW_GENERATED,
    }:
        return str(payload.get("summary") or "Agente controlado registrou uma decisao auditavel.")
    if event.event_type == BotEventType.AGENT_FALLBACK_USED:
        return "Guardrail acionou fallback seguro para a saida do agente."
    return event.event_type.value


class GuardianConsoleRealFlowService:
    def __init__(
        self,
        dual_bot_service: DualBotFlowService,
        consent_service: ConsentService | None = None,
    ) -> None:
        self._dual_bot_service = dual_bot_service
        self._consent_service = consent_service

    def get_status(self) -> GuardianConsoleRealStatusResponse:
        event_model = self._dual_bot_service.event_model
        cases = event_model.repositories.cases.list_all()
        activation = self._activation_state()
        consent = self._consent_view()
        return GuardianConsoleRealStatusResponse(
            service="guardian-console-real-flow",
            mode="dual_bot_local",
            storage="in_memory_event_model",
            channel_provider=self._dual_bot_service.adapter.provider.value,
            case_count=len(cases),
            open_case_count=sum(1 for case in cases if case.status in OPEN_CASE_STATUSES),
            protected_people_count=len(event_model.repositories.protected_people.list_all()),
            guardians_count=len(event_model.repositories.guardians.list_all()),
            delivery_status_available=True,
            activation=activation,
            consent=consent,
            demo_note=(
                "Console operacional usando Event Model local/in-memory. Dados podem ser mock local "
                "ou provider demo/sandbox controlado, conforme o adapter ativo."
            ),
        )

    def list_cases(self) -> GuardianConsoleRealCaseListResponse:
        cases = [
            self._case_summary(case)
            for case in sorted(
                self._dual_bot_service.event_model.repositories.cases.list_all(),
                key=lambda item: item.updated_at,
                reverse=True,
            )
        ]
        return GuardianConsoleRealCaseListResponse(cases=cases, total=len(cases))

    def get_case_detail(self, case_id: str) -> GuardianConsoleRealCaseDetail:
        case = self._dual_bot_service.event_model.cases.get_case_by_id(case_id)
        context = self._dual_bot_service.get_case_context(case_id)
        message = self._message_for(case)
        assessment = self._assessment_for(case)
        delivery = self._delivery_for(case.case_id)
        pattern = self._pattern_for(case.case_id)
        protected_reply = self._protected_reply_view(case, message, assessment, delivery)
        guardian_alert = self._guardian_alert_view(case, assessment, context.protected_person_alias, delivery)
        timeline = self._timeline_for(case)
        summary = self._case_summary(case)
        consent = self._consent_view(case.protected_person_id)
        return GuardianConsoleRealCaseDetail(
            **summary.model_dump(),
            source_message=message.body,
            activation=self._activation_state(case.protected_person_id),
            delivery=delivery,
            protected_reply=protected_reply,
            guardian_alert=guardian_alert,
            protected_person=self._protected_person_view(case),
            responsible_contact=self._responsible_contact_view(case, delivery),
            case=self._case_state_view(case),
            message=self._message_view(message),
            risk_assessment=self._risk_assessment_view(assessment),
            channel_status=self._channel_status_view(delivery, case.protected_person_id),
            feedback=self._feedback_view(case),
            audit_log=self._audit_log_for(case),
            bot_events=timeline,
            agent_decisions=self._agent_decisions_for(case),
            consent=consent,
            environment_label=self._environment_label(),
            next_step=_recommended_action(case, assessment),
            pattern=pattern,
            timeline=timeline,
            feedback_actions=list(FEEDBACK_ACTIONS),
        )

    def record_feedback(self, case_id: str, request: GuardianFeedbackRequest):
        return self._dual_bot_service.record_guardian_feedback(case_id, request)

    def _activation_state(self, protected_person_id: str | None = None) -> GuardianConsoleActivationState:
        provider = self._dual_bot_service.adapter.provider.value
        last_event = self._latest_event_type()
        simulated = provider == "mock"
        mode = "mock_local" if simulated else "demo_controlled"
        consent = self._consent_view(protected_person_id)
        bot_active = consent.bot_active
        return GuardianConsoleActivationState(
            protected_bot=GuardianConsoleBotState(
                name="Bot Protegido",
                active=bot_active,
                provider=provider,
                mode=mode,
                last_event=last_event,
            ),
            responsible_bot=GuardianConsoleBotState(
                name="Bot Responsavel",
                active=bot_active,
                provider=provider,
                mode=mode,
                last_event=last_event,
            ),
            channel_provider=provider,
            backend_state="local_in_memory",
            simulated=simulated,
        )

    def _case_summary(self, case: Case) -> GuardianConsoleRealCaseSummary:
        context = self._dual_bot_service.get_case_context(case.case_id)
        message = self._message_for(case)
        assessment = self._assessment_for(case)
        delivery = self._delivery_for(case.case_id)
        pattern = self._pattern_for(case.case_id)
        return GuardianConsoleRealCaseSummary(
            case_id=case.case_id,
            status=case.status.value,
            protected_person_alias=context.protected_person_alias,
            guardian_alias=context.guardian_alias,
            source_channel=message.channel,
            risk_score=case.risk_score,
            risk_level=case.risk_level.value,
            risk_signals=assessment.signals,
            pattern_score=pattern.score if pattern else None,
            pattern_level=pattern.level if pattern else None,
            message_summary=context.message_summary,
            recommended_action=_recommended_action(case, assessment),
            alert_delivered=delivery.guardian_alert_status == "delivered",
            guardian_confirmed=case.status == CaseStatus.CONFIRMED_SCAM,
            false_positive=case.status == CaseStatus.FALSE_ALARM,
            resolved=case.status == CaseStatus.RESOLVED,
            created_at=case.created_at,
            updated_at=case.updated_at,
        )

    def _protected_person_view(self, case: Case) -> GuardianConsoleProtectedPersonView:
        protected_person = self._dual_bot_service.event_model.repositories.protected_people.get(
            case.protected_person_id
        )
        if protected_person is None:
            raise ValueError(f"Protected person not found for case: {case.case_id}")
        return GuardianConsoleProtectedPersonView(
            protected_person_id=protected_person.protected_person_id,
            alias=protected_person.alias,
            status=protected_person.status.value,
            created_at=protected_person.created_at,
            updated_at=protected_person.updated_at,
        )

    def _responsible_contact_view(
        self,
        case: Case,
        delivery: GuardianConsoleDeliveryView,
    ) -> GuardianConsoleResponsibleContactView:
        guardian = (
            self._dual_bot_service.event_model.repositories.guardians.get(case.guardian_id)
            if case.guardian_id
            else None
        )
        connection = self._channel_connection_for(case)
        return GuardianConsoleResponsibleContactView(
            guardian_id=guardian.guardian_id if guardian else None,
            alias=guardian.alias if guardian else None,
            status=guardian.status.value if guardian else None,
            notified=delivery.guardian_notified,
            last_delivery_status=delivery.guardian_alert_status,
            address_label=connection.address_label if connection else None,
        )

    def _case_state_view(self, case: Case) -> GuardianConsoleCaseStateView:
        return GuardianConsoleCaseStateView(
            case_id=case.case_id,
            status=case.status.value,
            source_message_id=case.source_message_id,
            risk_assessment_id=case.risk_assessment_id,
            open=case.status in OPEN_CASE_STATUSES,
            created_at=case.created_at,
            updated_at=case.updated_at,
        )

    def _message_view(self, message: Message) -> GuardianConsoleMessageView:
        return GuardianConsoleMessageView(
            message_id=message.message_id,
            provider_message_id=message.provider_message_id,
            direction=message.direction.value,
            channel=message.channel,
            body=message.body,
            summary=_summary(message.body),
            status=message.status.value,
            simulated=message.simulated,
            created_at=message.created_at,
        )

    def _risk_assessment_view(self, assessment: RiskAssessment) -> GuardianConsoleRiskAssessmentView:
        return GuardianConsoleRiskAssessmentView(
            risk_assessment_id=assessment.risk_assessment_id,
            score=assessment.score,
            risk_level=assessment.risk_level.value,
            signals=assessment.signals,
            explanation=assessment.explanation,
            case_threshold_reached=assessment.case_threshold_reached,
            threshold_label="case_created" if assessment.case_threshold_reached else "monitor_only",
            created_at=assessment.created_at,
        )

    def _channel_status_view(
        self,
        delivery: GuardianConsoleDeliveryView,
        protected_person_id: str | None = None,
    ) -> GuardianConsoleChannelStatusView:
        activation = self._activation_state(protected_person_id)
        return GuardianConsoleChannelStatusView(
            provider=activation.channel_provider,
            mode=activation.protected_bot.mode,
            simulated=activation.simulated,
            backend_state=activation.backend_state,
            protected_bot_active=activation.protected_bot.active,
            responsible_bot_active=activation.responsible_bot.active,
            protected_reply_status=delivery.protected_reply_status,
            guardian_alert_status=delivery.guardian_alert_status,
            guardian_notified=delivery.guardian_notified,
            latest_provider_message_id=delivery.latest_provider_message_id,
            environment_label=self._environment_label(),
        )

    def _consent_view(self, protected_person_id: str | None = None) -> GuardianConsoleConsentView:
        if self._consent_service is None:
            return GuardianConsoleConsentView(
                consent_id="consent-not-configured",
                status="not_configured",
                bot_active=True,
                scopes=[],
                retention_message_body_days=0,
                retention_event_audit_days=0,
                delete_after_revocation_days=0,
                latest_event=None,
                limitation_notice="Servico de consentimento nao conectado neste contexto local.",
            )
        status = self._consent_service.get_status(protected_person_id or "demo-protected-person")
        record = status.record
        latest_event = status.latest_event.event_type.value if status.latest_event else None
        return GuardianConsoleConsentView(
            consent_id=record.consent_id,
            status=record.status.value,
            bot_active=record.bot_active,
            scopes=[scope.value for scope in record.scopes],
            accepted_at=record.accepted_at,
            revoked_at=record.revoked_at,
            retention_message_body_days=record.retention_policy.message_body_days,
            retention_event_audit_days=record.retention_policy.event_audit_days,
            delete_after_revocation_days=record.retention_policy.delete_after_revocation_days,
            latest_event=latest_event,
            limitation_notice=record.limitation_notice,
        )

    def _feedback_view(self, case: Case) -> GuardianConsoleFeedbackView:
        feedback_event = self._latest_event_for(case.case_id, BotEventType.GUARDIAN_FEEDBACK_RECEIVED)
        payload = feedback_event.payload if feedback_event else {}
        return GuardianConsoleFeedbackView(
            available_actions=list(FEEDBACK_ACTIONS),
            latest_action=payload.get("action"),
            latest_actor=(feedback_event.actor or payload.get("guardian_alias")) if feedback_event else None,
            latest_note=payload.get("note"),
            latest_event_id=feedback_event.event_id if feedback_event else None,
            latest_event_at=feedback_event.occurred_at if feedback_event else None,
            guardian_confirmed=case.status == CaseStatus.CONFIRMED_SCAM,
            false_positive=case.status == CaseStatus.FALSE_ALARM,
            resolved=case.status == CaseStatus.RESOLVED,
        )

    def _audit_log_for(self, case: Case) -> list[GuardianConsoleAuditLogView]:
        case_events = self._events_for_case(case)
        event_ids = {event.event_id for event in case_events}
        target_ids = {
            case.case_id,
            case.source_message_id,
            case.risk_assessment_id,
            case.protected_person_id,
        }
        audit_logs = [
            audit_log
            for audit_log in self._dual_bot_service.event_model.repositories.audit_logs.list_all()
            if audit_log.event_id in event_ids
            or audit_log.target_id in target_ids
            or audit_log.payload.get("case_id") == case.case_id
            or audit_log.payload.get("protected_person_id") == case.protected_person_id
        ]
        return [
            GuardianConsoleAuditLogView(
                audit_log_id=audit_log.audit_log_id,
                event_id=audit_log.event_id,
                actor=audit_log.actor,
                action=audit_log.action,
                target_type=audit_log.target_type,
                target_id=audit_log.target_id,
                payload=audit_log.payload,
                created_at=audit_log.created_at,
            )
            for audit_log in sorted(audit_logs, key=lambda item: item.created_at)
        ]

    def _agent_decisions_for(self, case: Case) -> list[GuardianConsoleAgentDecisionView]:
        agent_event_types = {
            BotEventType.TRIAGE_DECISION_CREATED,
            BotEventType.SAFE_REPLY_GENERATED,
            BotEventType.RESPONSIBLE_ALERT_GENERATED,
            BotEventType.CASE_SUMMARY_GENERATED,
            BotEventType.PATTERN_REVIEW_GENERATED,
            BotEventType.AGENT_FALLBACK_USED,
        }
        decisions: list[GuardianConsoleAgentDecisionView] = []
        for event in self._events_for_case(case):
            if event.event_type not in agent_event_types:
                continue
            payload = event.payload
            guardrails = payload.get("guardrails") or {}
            decisions.append(
                GuardianConsoleAgentDecisionView(
                    event_id=event.event_id,
                    agent=str(payload.get("agent") or event.actor or event.event_type.value),
                    summary=str(payload.get("summary") or _event_description(event)),
                    recommended_action=str(payload.get("recommended_action") or ""),
                    fallback_used=bool(guardrails.get("fallback_used") or payload.get("fallback_used")),
                    guardrails=list(guardrails.get("applied") or []),
                    occurred_at=event.occurred_at,
                )
            )
        return sorted(decisions, key=lambda item: item.occurred_at)

    def _channel_connection_for(self, case: Case):
        connections = self._dual_bot_service.event_model.repositories.channel_connections.list_all()
        if case.channel_connection_id:
            for connection in connections:
                if connection.channel_connection_id == case.channel_connection_id:
                    return connection
        for connection in reversed(connections):
            if (
                connection.protected_person_id == case.protected_person_id
                or (case.guardian_id and connection.guardian_id == case.guardian_id)
            ):
                return connection
        return None

    def _environment_label(self) -> str:
        provider = self._dual_bot_service.adapter.provider.value
        if provider == "mock":
            return "mock local / in-memory"
        return f"{provider} demo controlado / in-memory"

    def _message_for(self, case: Case) -> Message:
        message = self._dual_bot_service.event_model.repositories.messages.get(case.source_message_id)
        if message is None:
            raise ValueError(f"Source message not found for case: {case.case_id}")
        return message

    def _assessment_for(self, case: Case) -> RiskAssessment:
        assessment = self._dual_bot_service.event_model.repositories.risk_assessments.get(
            case.risk_assessment_id
        )
        if assessment is None:
            raise ValueError(f"Risk assessment not found for case: {case.case_id}")
        return assessment

    def _events_for_case(self, case: Case) -> list[BotEvent]:
        aggregate_ids = {
            case.case_id,
            case.source_message_id,
            case.risk_assessment_id,
        }
        return [
            event
            for event in self._dual_bot_service.event_model.repositories.events.list_all()
            if event.aggregate_id in aggregate_ids
            or event.payload.get("case_id") == case.case_id
            or event.payload.get("related_case_id") == case.case_id
        ]

    def _timeline_for(self, case: Case) -> list[GuardianConsoleTimelineEvent]:
        return [
            GuardianConsoleTimelineEvent(
                event_id=event.event_id,
                event_type=event.event_type.value,
                label=EVENT_LABELS.get(event.event_type, event.event_type.value),
                description=_event_description(event),
                aggregate_type=event.aggregate_type,
                aggregate_id=event.aggregate_id,
                occurred_at=event.occurred_at,
                status=event.payload.get("status") or event.payload.get("new_status"),
                metadata=event.payload,
            )
            for event in sorted(self._events_for_case(case), key=lambda item: item.occurred_at)
        ]

    def _pattern_for(self, case_id: str) -> GuardianConsolePatternView | None:
        result = self._dual_bot_service.pattern_intelligence.get_result_for_case(case_id)
        if result is None:
            return None
        candidate = self._dual_bot_service.pattern_intelligence.get_candidate_for_case(case_id)
        return GuardianConsolePatternView(
            score=result.score,
            level=result.level.value,
            threat_type=result.threat_type,
            threat_type_label=result.threat_type_label,
            explanation=result.explanation,
            reasons=result.risk_explanation.reasons,
            recommendation=result.risk_explanation.recommendation,
            signals=result.signal_names,
            cluster_ids=result.cluster_ids,
            recurrence={
                key: int(value)
                for key, value in result.recurrence.items()
                if isinstance(value, int)
            },
            similar_message_ids=result.similar_message_ids,
            normalized_text_sha1=result.normalized_text_sha1,
            text_fingerprint=result.normalized_threat_text.text_fingerprint,
            candidate_id=result.candidate_id,
            feedback_label=candidate.expected_label if candidate else None,
        )

    def _delivery_for(self, case_id: str) -> GuardianConsoleDeliveryView:
        protected_status: Optional[str] = None
        guardian_status: Optional[str] = None
        latest_provider_message_id: Optional[str] = None
        guardian_notified = False
        for event in self._dual_bot_service.event_model.repositories.events.list_all():
            payload = event.payload
            if payload.get("related_case_id") != case_id and event.aggregate_id != case_id:
                continue
            provider_message_id = payload.get("provider_message_id")
            if provider_message_id:
                latest_provider_message_id = provider_message_id
            if event.event_type == BotEventType.DELIVERY_STATUS_UPDATED:
                if payload.get("kind") == "protected_reply":
                    protected_status = payload.get("status")
                if payload.get("kind") == "guardian_alert":
                    guardian_status = payload.get("status")
            if event.event_type in {BotEventType.RESPONSIBLE_NOTIFIED, BotEventType.GUARDIAN_NOTIFIED}:
                guardian_notified = True
                guardian_status = payload.get("status") or guardian_status
        return GuardianConsoleDeliveryView(
            protected_reply_status=protected_status,
            guardian_alert_status=guardian_status,
            guardian_notified=guardian_notified,
            latest_provider_message_id=latest_provider_message_id,
        )

    def _protected_reply_view(
        self,
        case: Case,
        message: Message,
        assessment: RiskAssessment,
        delivery: GuardianConsoleDeliveryView,
    ) -> GuardianConsoleOutboundView:
        event = self._latest_event_for(case.case_id, BotEventType.PROTECTED_PERSON_REPLIED)
        generated_body = self._latest_agent_body(case.case_id, BotEventType.SAFE_REPLY_GENERATED)
        return GuardianConsoleOutboundView(
            provider_message_id=event.payload.get("provider_message_id") if event else None,
            kind="protected_reply",
            to_label="Pessoa protegida",
            body=generated_body or protected_reply_for(assessment, case_created=True, language="pt"),
            status=delivery.protected_reply_status,
            simulated=message.simulated,
        )

    def _guardian_alert_view(
        self,
        case: Case,
        assessment: RiskAssessment,
        protected_person_alias: str,
        delivery: GuardianConsoleDeliveryView,
    ) -> GuardianConsoleOutboundView:
        event = self._latest_event_for(case.case_id, BotEventType.RESPONSIBLE_NOTIFIED)
        if event is None:
            event = self._latest_event_for(case.case_id, BotEventType.GUARDIAN_NOTIFIED)
        generated_body = self._latest_agent_body(case.case_id, BotEventType.RESPONSIBLE_ALERT_GENERATED)
        return GuardianConsoleOutboundView(
            provider_message_id=event.payload.get("provider_message_id") if event else None,
            kind="guardian_alert",
            to_label="Responsavel vinculado",
            body=generated_body or responsible_alert_for(
                protected_person_alias=protected_person_alias,
                risk_level=assessment.risk_level.value,
                signals=assessment.signals,
                case_id=case.case_id,
                language="pt",
            ),
            status=delivery.guardian_alert_status,
            simulated=self._dual_bot_service.adapter.provider.value == "mock",
        )

    def _latest_event_for(self, case_id: str, event_type: BotEventType) -> Optional[BotEvent]:
        events = [
            event
            for event in self._dual_bot_service.event_model.repositories.events.list_all()
            if event.event_type == event_type
            and (event.aggregate_id == case_id or event.payload.get("related_case_id") == case_id)
        ]
        return events[-1] if events else None

    def _latest_agent_body(self, case_id: str, event_type: BotEventType) -> Optional[str]:
        events = [
            event
            for event in self._dual_bot_service.event_model.repositories.events.list_all()
            if event.event_type == event_type
            and (event.case_id == case_id or event.aggregate_id == case_id or event.payload.get("case_id") == case_id)
        ]
        if not events:
            return None
        body = events[-1].payload.get("body")
        return str(body) if body else None

    def _latest_event_type(self) -> Optional[str]:
        events = self._dual_bot_service.event_model.repositories.events.list_all()
        return events[-1].event_type.value if events else None
