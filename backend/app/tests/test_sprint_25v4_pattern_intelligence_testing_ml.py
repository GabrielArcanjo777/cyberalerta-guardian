from __future__ import annotations

import pytest

from app.dual_bot import DualBotFlowService, DualBotInboundRequest, GuardianFeedbackRequest
from app.event_model import BotEventType, EventModelService, Message
from app.guardian_console import GuardianConsoleRealFlowService
from app.pattern_intelligence import PatternIntelligenceService, PatternLevel


def _message(body: str, protected_person_id: str = "protected-1") -> Message:
    return Message(protected_person_id=protected_person_id, body=body)


@pytest.mark.parametrize(
    ("body", "signal"),
    [
        ("Preciso disso urgente agora.", "urgency"),
        ("Faz um Pix para mim.", "pix_or_payment"),
        ("Mae, troquei de numero.", "new_number"),
        ("Clique no link https://regularizacao.invalid", "suspicious_link"),
        ("Nao liga agora.", "do_not_call"),
        ("Nao conte para ninguem, e segredo.", "secrecy_request"),
        ("Por favor, estou desesperado e preciso muito.", "emotional_pressure"),
        ("Mae, troquei de numero e preciso de Pix.", "false_relative"),
        ("Sou da central de seguranca do banco.", "fake_support_center"),
        ("Regularize seu beneficio para evitar bloqueio.", "benefit_regularization"),
        ("Me manda o codigo token que chegou.", "code_token"),
    ],
)
def test_pattern_rules_detect_main_signals(body: str, signal: str):
    service = PatternIntelligenceService()

    result = service.detect(
        message=_message(body),
        protected_person_id="protected-1",
        sender_address="+5511999990001",
    )

    assert signal in result.signal_names
    assert result.score > 0
    assert result.explanation
    assert result.normalized_text
    assert result.normalized_text_sha1


def test_pattern_score_is_capped_and_uses_clear_thresholds():
    service = PatternIntelligenceService()
    result = service.detect(
        message=_message(
            "Mae, troquei de numero. Preciso de Pix urgente agora. "
            "Nao liga, nao conte, e segredo. Me manda o codigo tambem. "
            "Por favor, estou desesperado."
        ),
        protected_person_id="protected-1",
        sender_address="+5511999990001",
    )

    assert result.score == 100
    assert result.level == PatternLevel.CRITICAL
    assert {
        "false_relative",
        "new_number",
        "pix_or_payment",
        "urgency",
        "do_not_call",
        "secrecy_request",
        "code_token",
    }.issubset(set(result.signal_names))


def test_pattern_recurrence_detects_similar_text_sender_and_protected_person():
    service = PatternIntelligenceService()
    first = service.detect(
        message=_message("Mae, troquei de numero. Preciso de um Pix urgente."),
        protected_person_id="protected-1",
        sender_address="+5511999990001",
    )
    second = service.detect(
        message=_message("Mae, troquei de numero. Preciso de Pix urgente agora."),
        protected_person_id="protected-1",
        sender_address="+5511999990001",
    )

    assert first.recurrence["repeated_similar_text"] == 0
    assert second.recurrence["repeated_similar_text"] == 1
    assert second.recurrence["recurring_sender"] == 1
    assert second.recurrence["recurring_protected_person"] == 1
    assert "repeated_similar_text" in second.signal_names
    assert "recurring_sender" in second.signal_names
    assert "recurring_protected_person" in second.signal_names
    assert service.list_clusters()


def test_dual_bot_publishes_pattern_detected_and_stores_candidate():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="pattern-dual-bot-001",
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )

    assert flow.pattern_detection is not None
    assert flow.pattern_detection.level in {PatternLevel.HIGH, PatternLevel.CRITICAL}
    assert BotEventType.PATTERN_CANDIDATE_DETECTED.value in flow.events
    assert dual_bot.pattern_intelligence.get_candidate_for_case(flow.case_id) is not None


def test_guardian_feedback_is_recorded_as_pattern_ground_truth():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="pattern-feedback-001",
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )
    assert flow.case_id is not None

    dual_bot.record_guardian_feedback(
        flow.case_id,
        GuardianFeedbackRequest(action="confirm_scam", guardian_alias="Gabriel"),
    )
    candidate = dual_bot.pattern_intelligence.get_candidate_for_case(flow.case_id)
    feedback = dual_bot.pattern_intelligence.list_feedback()[-1]

    assert candidate is not None
    assert candidate.expected_label == "confirmed_scam"
    assert candidate.feedback_action == "confirm_scam"
    assert feedback.expected_label == "confirmed_scam"
    assert candidate.candidate_id in feedback.candidate_ids


def test_guardian_console_exposes_pattern_summary_and_feedback_label():
    dual_bot = DualBotFlowService(event_model=EventModelService.in_memory())
    flow = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="pattern-console-001",
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )
    assert flow.case_id is not None
    dual_bot.record_guardian_feedback(
        flow.case_id,
        GuardianFeedbackRequest(action="false_alarm", guardian_alias="Gabriel"),
    )

    console = GuardianConsoleRealFlowService(dual_bot)
    detail = console.get_case_detail(flow.case_id)

    assert detail.pattern is not None
    assert detail.pattern.score > 0
    assert "false_relative" in detail.pattern.signals
    assert detail.pattern.feedback_label == "false_alarm"
    assert BotEventType.PATTERN_CANDIDATE_DETECTED.value in [
        event.event_type for event in detail.timeline
    ]
