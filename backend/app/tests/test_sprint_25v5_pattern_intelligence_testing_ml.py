from __future__ import annotations

import pytest

from app.dual_bot import DualBotFlowService, DualBotInboundRequest, GuardianFeedbackRequest
from app.event_model import EventModelService, Message
from app.guardian_console import GuardianConsoleRealFlowService
from app.pattern_intelligence import (
    NormalizedThreatText,
    PatternFeedback,
    PatternIntelligenceService,
    PatternLevel,
    RiskExplanation,
)


def _message(body: str, protected_person_id: str = "protected-v5") -> Message:
    return Message(protected_person_id=protected_person_id, body=body)


@pytest.mark.parametrize(
    ("body", "expected_signals", "expected_threat_type", "minimum_score"),
    [
        (
            "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            {"false_relative", "new_number", "pix_or_payment", "urgency", "do_not_call"},
            "false_relative",
            55,
        ),
        (
            "Regularize seu beneficio agora pelo link https://beneficio.invalid para evitar bloqueio.",
            {"benefit_regularization", "suspicious_link", "urgency"},
            "benefit_regularization",
            25,
        ),
        (
            "Sou da central de seguranca do banco. Sua conta sera bloqueada agora.",
            {"fake_support_center", "benefit_regularization", "urgency"},
            "fake_support_center",
            25,
        ),
        (
            "Me envie o codigo token com urgencia para validar seu acesso.",
            {"code_token", "urgency"},
            "code_token",
            25,
        ),
        (
            "Oi, tudo bem? Vamos almocar no domingo.",
            set(),
            "neutral",
            0,
        ),
    ],
)
def test_v5_pattern_rules_cover_required_simulation_scenarios(
    body: str,
    expected_signals: set[str],
    expected_threat_type: str,
    minimum_score: int,
):
    service = PatternIntelligenceService()

    result = service.detect(
        message=_message(body),
        protected_person_id="protected-v5",
        protected_person_alias="Dona Lucia",
        sender_address="+5511999990001",
    )

    assert expected_signals.issubset(set(result.signal_names))
    assert result.threat_type == expected_threat_type
    assert result.score >= minimum_score
    assert result.score <= 100
    assert result.explanation
    assert isinstance(result.normalized_threat_text, NormalizedThreatText)
    assert isinstance(result.risk_explanation, RiskExplanation)
    assert result.normalized_threat_text.normalized_text_sha1 == result.normalized_text_sha1
    assert result.risk_explanation.thresholds["medium"] == 25
    assert result.risk_explanation.thresholds["high"] == 55
    assert result.risk_explanation.thresholds["critical"] == 80


def test_v5_neutral_message_has_low_score_without_magic_ai_claim():
    service = PatternIntelligenceService()

    result = service.detect(
        message=_message("Oi, tudo bem? Passei para desejar boa semana."),
        protected_person_id="protected-neutral",
        sender_address="+5511999992222",
    )

    assert result.score == 0
    assert result.level == PatternLevel.LOW
    assert result.signal_names == []
    assert result.threat_type == "neutral"
    assert "Nenhum padrao forte" in result.explanation
    assert result.risk_explanation.recommendation.startswith("Monitorar")


def test_v5_scores_use_clear_medium_high_and_critical_thresholds():
    service = PatternIntelligenceService()

    medium = service.detect(
        message=_message("Regularize seu beneficio agora pelo link https://beneficio.invalid."),
        protected_person_id="protected-score-1",
    )
    high = service.detect(
        message=_message("Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora."),
        protected_person_id="protected-score-2",
    )
    critical = service.detect(
        message=_message(
            "Mae, troquei de numero. Preciso de Pix urgente agora. "
            "Nao liga, nao conte, e segredo. Me manda o codigo token."
        ),
        protected_person_id="protected-score-3",
    )

    assert medium.level == PatternLevel.MEDIUM
    assert high.level == PatternLevel.HIGH
    assert critical.level == PatternLevel.CRITICAL
    assert critical.score == 100


def test_v5_recurrence_tracks_threat_type_without_same_sender_or_person():
    service = PatternIntelligenceService()
    service.detect(
        message=_message("Mae, troquei de numero. Preciso de Pix urgente.", "protected-a"),
        protected_person_id="protected-a",
        protected_person_alias="Dona Lucia",
        sender_address="+551100000001",
    )

    second = service.detect(
        message=_message("Pai, mudei de numero. Preciso pagar um boleto agora.", "protected-b"),
        protected_person_id="protected-b",
        protected_person_alias="Seu Joao",
        sender_address="+551100000002",
    )

    assert second.threat_type == "false_relative"
    assert second.recurrence["recurring_threat_type"] == 1
    assert second.recurrence["recurring_sender"] == 0
    assert second.recurrence["recurring_protected_person"] == 0
    assert "recurring_threat_type" in second.signal_names
    assert any(cluster.cluster_type == "threat_type" for cluster in service.list_clusters())


def test_v5_feedback_records_ground_truth_for_future_dataset():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="pattern-v5-feedback-001",
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )
    assert flow.case_id is not None

    dual_bot.record_guardian_feedback(
        flow.case_id,
        GuardianFeedbackRequest(
            action="false_alarm",
            guardian_alias="Gabriel",
            note="Responsavel reconheceu como mensagem legitima.",
        ),
    )

    candidate = dual_bot.pattern_intelligence.get_candidate_for_case(flow.case_id)
    feedback = dual_bot.pattern_intelligence.list_feedback()[-1]

    assert isinstance(feedback, PatternFeedback)
    assert candidate is not None
    assert candidate.normalized_threat_text is not None
    assert candidate.risk_explanation is not None
    assert candidate.expected_label == "false_alarm"
    assert candidate.feedback_action == "false_alarm"
    assert feedback.false_positive is True
    assert feedback.confirmed_scam is False
    assert candidate.candidate_id in feedback.candidate_ids


def test_v5_guardian_console_exposes_pattern_intelligence_without_static_panel():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    first = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="pattern-v5-console-001",
            body="Mae, troquei de numero. Preciso de Pix urgente.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )
    second = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="pattern-v5-console-002",
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )
    assert first.case_id is not None
    assert second.case_id is not None
    dual_bot.record_guardian_feedback(
        second.case_id,
        GuardianFeedbackRequest(action="confirm_scam", guardian_alias="Gabriel"),
    )

    console = GuardianConsoleRealFlowService(dual_bot)
    detail = console.get_case_detail(second.case_id)

    assert detail.pattern is not None
    assert detail.pattern.threat_type == "false_relative"
    assert detail.pattern.threat_type_label == "Possivel falso parente"
    assert detail.pattern.score >= 55
    assert "recurring_threat_type" in detail.pattern.recurrence
    assert detail.pattern.recurrence["recurring_threat_type"] >= 1
    assert detail.pattern.reasons
    assert detail.pattern.recommendation
    assert detail.pattern.normalized_text_sha1
    assert detail.pattern.text_fingerprint
    assert detail.pattern.feedback_label == "confirmed_scam"
