from __future__ import annotations

import re
import unicodedata
from uuid import uuid4

from app.channel_adapters import InboundMessage
from app.event_model import BotEventType, Case, LocalEventBus, Message, RiskAssessment
from app.pattern_intelligence import PatternDetectionResult
from app.controlled_agents.models import (
    AgentGuardrailResult,
    CaseSummaryDecision,
    ControlledAgentDecision,
    ControlledAgentName,
    PatternReviewDecision,
    ResponsibleAlertDecision,
    SafeReplyDecision,
    TriageDecision,
)


GUARDRAILS = [
    "usar sinais de risco, sem certeza absoluta",
    "orientar pausa e verificacao por canal confiavel",
    "nao pedir senha, codigo ou dados bancarios",
    "nao orientar pagamento ou clique",
    "manter revisao humana",
]

FORBIDDEN_PHRASES = (
    "e golpe com certeza",
    "golpe com certeza",
    "tenho certeza",
    "pague agora",
    "faca o pagamento",
    "clique no link",
    "envie sua senha",
    "mande sua senha",
    "informe sua senha",
    "envie o codigo",
    "mande o codigo",
    "informe o codigo",
    "dados bancarios",
)

SAFE_REPLY_FALLBACK = (
    "Recebi sua mensagem. Ela tem sinais de risco. Nao faca pagamento nem clique em links "
    "por enquanto. Confirme por um canal confiavel."
)

RESPONSIBLE_ALERT_FALLBACK = (
    "Alerta Guardian: mensagem com sinais de risco. Revise o caso e confirme por canal confiavel "
    "antes de qualquer acao."
)


def _decision_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_accents.lower().split())


def _summary(text: str, *, limit: int = 180) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3].rstrip()}..."


def _risk_label(risk_level: str) -> str:
    return {"low": "baixo", "medium": "medio", "high": "alto"}.get(risk_level, risk_level)


def _safe_signal_text(signals: list[str]) -> str:
    labels = {
        "urgency": "urgencia",
        "pix_or_payment": "Pix ou pagamento",
        "new_number": "numero novo",
        "unknown_link": "link suspeito",
        "suspicious_link": "link suspeito",
        "do_not_call": "pedido para nao ligar",
        "secrecy_request": "pedido de segredo",
        "emotional_pressure": "pressao emocional",
        "password_or_code": "codigo ou token",
        "code_token": "codigo ou token",
    }
    return ", ".join(labels.get(signal, signal.replace("_", " ")) for signal in signals) if signals else "sem sinais fortes"


class AgentGuardrails:
    def enforce(
        self,
        *,
        candidate_text: str,
        fallback_text: str,
    ) -> tuple[str, AgentGuardrailResult]:
        normalized = _normalize(candidate_text)
        violations = [phrase for phrase in FORBIDDEN_PHRASES if phrase in normalized]
        fallback_used = bool(violations)
        return (
            fallback_text if fallback_used else candidate_text,
            AgentGuardrailResult(
                passed=not fallback_used,
                applied=list(GUARDRAILS),
                violations=violations,
                fallback_used=fallback_used,
            ),
        )


class TriageAgent:
    name = ControlledAgentName.TRIAGE

    def decide(
        self,
        *,
        inbound: InboundMessage,
        message: Message,
        assessment: RiskAssessment,
        case: Case | None,
        pattern_detection: PatternDetectionResult | None,
    ) -> TriageDecision:
        pattern_signals = pattern_detection.signal_names if pattern_detection else []
        should_create_case = assessment.case_threshold_reached
        should_notify = case is not None and assessment.risk_level.value in {"medium", "high"}
        recommended = self._recommended_action(assessment, pattern_detection)
        signals = sorted(set(assessment.signals + pattern_signals))
        return TriageDecision(
            agent=self.name,
            decision_id=_decision_id("triage-decision"),
            case_id=case.case_id if case else None,
            message_id=message.message_id,
            summary=(
                f"Mensagem normalizada de {inbound.from_address} avaliada com risco "
                f"{assessment.risk_level.value} e score {assessment.score}."
            ),
            recommended_action=recommended,
            guardrails=AgentGuardrailResult(applied=list(GUARDRAILS)),
            metadata={
                "provider": inbound.provider.value,
                "external_message_id": inbound.external_message_id,
                "pattern_level": pattern_detection.level.value if pattern_detection else None,
                "threat_type": pattern_detection.threat_type if pattern_detection else None,
            },
            risk_score=assessment.score,
            risk_level=assessment.risk_level.value,
            signals=signals,
            pattern_signals=pattern_signals,
            should_create_case=should_create_case,
            should_notify_responsible=should_notify,
        )

    def _recommended_action(
        self,
        assessment: RiskAssessment,
        pattern_detection: PatternDetectionResult | None,
    ) -> str:
        if pattern_detection and pattern_detection.risk_explanation.recommendation:
            return pattern_detection.risk_explanation.recommendation
        if assessment.risk_level.value == "high":
            return "Pausar e confirmar por canal confiavel antes de qualquer acao."
        if assessment.risk_level.value == "medium":
            return "Revisar com o responsavel e confirmar identidade."
        return "Monitorar e orientar verificacao se houver dinheiro, codigo ou pressa."


class SafeReplyAgent:
    name = ControlledAgentName.SAFE_REPLY

    def __init__(self, guardrails: AgentGuardrails | None = None) -> None:
        self.guardrails = guardrails or AgentGuardrails()

    def generate(
        self,
        *,
        assessment: RiskAssessment,
        case_id: str | None,
        language: str | None = "pt",
        candidate_body: str | None = None,
    ) -> SafeReplyDecision:
        body = candidate_body or self._body_for(assessment)
        body, guardrail_result = self.guardrails.enforce(
            candidate_text=body,
            fallback_text=SAFE_REPLY_FALLBACK,
        )
        return SafeReplyDecision(
            agent=self.name,
            decision_id=_decision_id("safe-reply"),
            case_id=case_id,
            message_id=assessment.message_id,
            summary="Resposta segura curta gerada para a pessoa protegida.",
            recommended_action="Pausar, nao pagar, nao clicar e confirmar por canal confiavel.",
            guardrails=guardrail_result,
            metadata={"language": language or "pt", "risk_level": assessment.risk_level.value},
            body=body,
        )

    def _body_for(self, assessment: RiskAssessment) -> str:
        if assessment.case_threshold_reached:
            return (
                "Recebi sua mensagem. Ela tem sinais de risco. Nao faca pagamento nem clique em links "
                "por enquanto. Vou avisar seu contato de confianca."
            )
        return (
            "Recebi sua mensagem. Se houver pedido de dinheiro, codigo ou pressa, confirme por outro "
            "canal antes de agir."
        )


class ResponsibleAlertAgent:
    name = ControlledAgentName.RESPONSIBLE_ALERT

    def __init__(self, guardrails: AgentGuardrails | None = None) -> None:
        self.guardrails = guardrails or AgentGuardrails()

    def generate(
        self,
        *,
        protected_person_alias: str,
        assessment: RiskAssessment,
        case_id: str,
        message_summary: str,
        recommended_action: str,
        candidate_body: str | None = None,
    ) -> ResponsibleAlertDecision:
        body = candidate_body or (
            f"Alerta Guardian: {protected_person_alias} recebeu uma mensagem com sinais de risco. "
            f"Risco: {_risk_label(assessment.risk_level.value)}. "
            f"Sinais: {_safe_signal_text(assessment.signals)}. "
            f"Caso {case_id}. Acao recomendada: {recommended_action}"
        )
        body, guardrail_result = self.guardrails.enforce(
            candidate_text=body,
            fallback_text=RESPONSIBLE_ALERT_FALLBACK,
        )
        return ResponsibleAlertDecision(
            agent=self.name,
            decision_id=_decision_id("responsible-alert"),
            case_id=case_id,
            message_id=assessment.message_id,
            summary="Alerta claro gerado para o responsavel vinculado.",
            recommended_action=recommended_action,
            guardrails=guardrail_result,
            metadata={"risk_level": assessment.risk_level.value, "risk_score": assessment.score},
            body=body,
            protected_person_alias=protected_person_alias,
            message_summary=message_summary,
        )


class CaseSummaryAgent:
    name = ControlledAgentName.CASE_SUMMARY

    def summarize(
        self,
        *,
        case: Case,
        message: Message,
        protected_person_alias: str,
        assessment: RiskAssessment,
        pattern_detection: PatternDetectionResult | None,
        safe_reply: str | None,
        responsible_alert: str | None,
    ) -> CaseSummaryDecision:
        evidence = [
            f"Mensagem: {_summary(message.body)}",
            f"Risco: {assessment.score}/{assessment.risk_level.value}",
            f"Sinais: {_safe_signal_text(assessment.signals)}",
        ]
        if pattern_detection:
            evidence.append(f"Padrao: {pattern_detection.threat_type_label} ({pattern_detection.score}/100)")
        report_summary = (
            f"{protected_person_alias} recebeu mensagem com sinais de risco "
            f"{assessment.risk_level.value}. Caso {case.case_id} permanece revisavel."
        )
        return CaseSummaryDecision(
            agent=self.name,
            decision_id=_decision_id("case-summary"),
            case_id=case.case_id,
            message_id=message.message_id,
            summary=report_summary,
            recommended_action="Manter revisao humana e confirmar por canal confiavel.",
            guardrails=AgentGuardrailResult(applied=list(GUARDRAILS)),
            metadata={
                "safe_reply_generated": bool(safe_reply),
                "responsible_alert_generated": bool(responsible_alert),
            },
            protected_person_alias=protected_person_alias,
            risk_score=assessment.score,
            risk_level=assessment.risk_level.value,
            evidence=evidence,
            report_summary=report_summary,
        )


class PatternReviewAgent:
    name = ControlledAgentName.PATTERN_REVIEW

    def review(self, *, pattern_detection: PatternDetectionResult) -> PatternReviewDecision:
        evidence = [
            *pattern_detection.risk_explanation.reasons[:5],
            f"Recorrencia: {pattern_detection.recurrence}",
        ]
        return PatternReviewDecision(
            agent=self.name,
            decision_id=_decision_id("pattern-review"),
            case_id=pattern_detection.case_id,
            message_id=pattern_detection.message_id,
            summary=pattern_detection.explanation,
            recommended_action=pattern_detection.risk_explanation.recommendation,
            guardrails=AgentGuardrailResult(applied=list(GUARDRAILS)),
            metadata={
                "cluster_ids": pattern_detection.cluster_ids,
                "similar_message_ids": pattern_detection.similar_message_ids,
            },
            pattern_score=pattern_detection.score,
            pattern_level=pattern_detection.level.value,
            threat_type=pattern_detection.threat_type,
            threat_type_label=pattern_detection.threat_type_label,
            recurrence=pattern_detection.recurrence,
            evidence=evidence,
        )


class ControlledAgentOrchestrator:
    def __init__(self, event_bus: LocalEventBus) -> None:
        self.event_bus = event_bus
        guardrails = AgentGuardrails()
        self.triage_agent = TriageAgent()
        self.safe_reply_agent = SafeReplyAgent(guardrails)
        self.responsible_alert_agent = ResponsibleAlertAgent(guardrails)
        self.case_summary_agent = CaseSummaryAgent()
        self.pattern_review_agent = PatternReviewAgent()

    def publish(self, event_type: BotEventType, decision: ControlledAgentDecision) -> None:
        aggregate_id = decision.case_id or decision.message_id or decision.decision_id
        self.event_bus.publish_type(
            event_type,
            aggregate_type="agent_decision",
            aggregate_id=aggregate_id,
            source="controlled_agent",
            actor=decision.agent.value,
            case_id=decision.case_id,
            payload=decision.model_dump(mode="json"),
        )
        if decision.guardrails.fallback_used:
            self.event_bus.publish_type(
                BotEventType.AGENT_FALLBACK_USED,
                aggregate_type="agent_decision",
                aggregate_id=decision.decision_id,
                source="controlled_agent",
                actor=decision.agent.value,
                case_id=decision.case_id,
                payload={
                    "agent": decision.agent.value,
                    "decision_id": decision.decision_id,
                    "violations": decision.guardrails.violations,
                    "fallback_used": True,
                },
            )
