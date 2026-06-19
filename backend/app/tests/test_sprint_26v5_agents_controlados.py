from __future__ import annotations

from app.controlled_agents import SafeReplyAgent
from app.dual_bot import DualBotFlowService, DualBotInboundRequest
from app.event_model import BotEventType, EventModelService, RiskAssessment, RiskLevel
from app.guardian_console import GuardianConsoleRealFlowService


def _suspicious_request(message_id: str = "agents-v5-001") -> DualBotInboundRequest:
    return DualBotInboundRequest(
        providerMessageId=message_id,
        body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
        protected_person_alias="Dona Lucia",
        guardian_alias="Gabriel",
        guardian_address="+5511888880001",
    )


def test_v5_safe_reply_agent_applies_guardrail_fallback():
    assessment = RiskAssessment(
        message_id="message-agents-guardrail",
        score=90,
        risk_level=RiskLevel.HIGH,
        signals=["pix_or_payment", "urgency"],
        explanation=["Mensagem com sinais de risco."],
        case_threshold_reached=True,
    )

    decision = SafeReplyAgent().generate(
        assessment=assessment,
        case_id="case-agents-guardrail",
        candidate_body="Envie sua senha e pague agora para resolver.",
    )

    assert decision.guardrails.fallback_used is True
    assert "senha" not in decision.body.lower()
    assert "pague agora" not in decision.body.lower()
    assert "sinais de risco" in decision.body
    assert "canal confiavel" in decision.recommended_action


def test_v5_dual_bot_flow_uses_controlled_agents_and_records_events():
    service = DualBotFlowService(event_model=EventModelService.in_memory())

    response = service.receive_mock_message(_suspicious_request())

    assert response.case_id is not None
    assert response.protected_reply is not None
    assert "sinais de risco" in response.protected_reply.body
    assert "com certeza" not in response.protected_reply.body.lower()
    assert response.guardian_alert is not None
    assert "Alerta Guardian: Dona Lucia" in response.guardian_alert.body
    assert "Acao recomendada" in response.guardian_alert.body

    for event_type in {
        BotEventType.TRIAGE_DECISION_CREATED.value,
        BotEventType.SAFE_REPLY_GENERATED.value,
        BotEventType.RESPONSIBLE_ALERT_GENERATED.value,
        BotEventType.CASE_SUMMARY_GENERATED.value,
        BotEventType.PATTERN_REVIEW_GENERATED.value,
    }:
        assert event_type in response.events


def test_v5_guardian_console_exposes_agent_decisions():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = dual_bot.receive_mock_message(_suspicious_request("agents-v5-console-001"))
    assert flow.case_id is not None

    console = GuardianConsoleRealFlowService(dual_bot)
    detail = console.get_case_detail(flow.case_id)

    agents = {decision.agent for decision in detail.agent_decisions}

    assert "TriageAgent" in agents
    assert "SafeReplyAgent" in agents
    assert "ResponsibleAlertAgent" in agents
    assert "CaseSummaryAgent" in agents
    assert "PatternReviewAgent" in agents
    assert all(decision.guardrails for decision in detail.agent_decisions)
    assert detail.protected_reply.body == flow.protected_reply.body
    assert detail.guardian_alert.body == flow.guardian_alert.body
