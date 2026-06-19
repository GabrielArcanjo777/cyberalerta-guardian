from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Pattern, Tuple

from app.event_model.event_bus import LocalEventBus
from app.event_model.models import (
    BotEventType,
    Message,
    RiskAssessment,
    RiskLevel,
)
from app.event_model.repositories import RiskAssessmentRepository

CASE_CREATION_THRESHOLD = 40
HIGH_RISK_THRESHOLD = 70


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return without_accents.lower()


@dataclass(frozen=True)
class RiskRule:
    signal: str
    weight: int
    patterns: Tuple[Pattern[str], ...]

    def matches(self, normalized_text: str) -> bool:
        return any(pattern.search(normalized_text) for pattern in self.patterns)


def _patterns(*values: str) -> Tuple[Pattern[str], ...]:
    return tuple(re.compile(value) for value in values)


RISK_RULES = (
    RiskRule(
        signal="urgency",
        weight=20,
        patterns=_patterns(r"\burgent\w*\b", r"\bimediat\w*\b", r"\bagora\b"),
    ),
    RiskRule(
        signal="pix_or_payment",
        weight=25,
        patterns=_patterns(
            r"\bpix\b",
            r"\bpagamento\w*\b",
            r"\bpagar\b",
            r"\bpague\b",
            r"\bpago\b",
            r"\btransfer\w*\b",
            r"\bboleto\b",
        ),
    ),
    RiskRule(
        signal="new_number",
        weight=20,
        patterns=_patterns(
            r"\bnumero novo\b",
            r"\bnovo numero\b",
            r"\btroquei de numero\b",
            r"\bmudei de numero\b",
        ),
    ),
    RiskRule(
        signal="do_not_call",
        weight=25,
        patterns=_patterns(
            r"\bnao lig\w*\b",
            r"\bnao telefon\w*\b",
        ),
    ),
    RiskRule(
        signal="secrecy_request",
        weight=20,
        patterns=_patterns(
            r"\bnao (?:conte|contar|fale|avise)\b",
            r"\bsegredo\b",
        ),
    ),
    RiskRule(
        signal="emotional_pressure",
        weight=15,
        patterns=_patterns(
            r"\bpor favor\b",
            r"\bdesesperad\w*\b",
            r"\bemergencia\b",
            r"\bpreciso muito\b",
            r"\bconfia em mim\b",
        ),
    ),
    RiskRule(
        signal="unknown_link",
        weight=20,
        patterns=_patterns(r"https?://", r"\bwww\.", r"\blink\b"),
    ),
    RiskRule(
        signal="password_or_code",
        weight=35,
        patterns=_patterns(r"\bsenha\b", r"\bcodigo\b", r"\btoken\b", r"\botp\b"),
    ),
)


def risk_level_for_score(score: int) -> RiskLevel:
    if score >= HIGH_RISK_THRESHOLD:
        return RiskLevel.HIGH
    if score >= CASE_CREATION_THRESHOLD:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


class RiskAssessmentService:
    def __init__(
        self,
        repository: RiskAssessmentRepository,
        event_bus: LocalEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    def assess(self, message: Message) -> RiskAssessment:
        normalized_text = _normalize(message.body)
        matched_rules = [rule for rule in RISK_RULES if rule.matches(normalized_text)]
        raw_score = sum(rule.weight for rule in matched_rules)
        score = min(100, raw_score)
        assessment = RiskAssessment(
            message_id=message.message_id,
            score=score,
            risk_level=risk_level_for_score(score),
            signals=[rule.signal for rule in matched_rules],
            explanation=[
                *[f"{rule.signal}: +{rule.weight}" for rule in matched_rules],
                *(
                    [f"score capped at 100 from {raw_score}"]
                    if raw_score > score
                    else []
                ),
            ],
            case_threshold_reached=score >= CASE_CREATION_THRESHOLD,
        )
        saved = self._repository.save(assessment)
        self._event_bus.publish_type(
            BotEventType.RISK_ASSESSMENT_CREATED,
            aggregate_type="risk_assessment",
            aggregate_id=saved.risk_assessment_id,
            protected_person_id=message.protected_person_id,
            payload={
                "message_id": saved.message_id,
                "score": saved.score,
                "risk_level": saved.risk_level.value,
                "signals": saved.signals,
                "case_threshold_reached": saved.case_threshold_reached,
            },
        )
        return saved
