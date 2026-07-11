from __future__ import annotations

from typing import List

from app.event_model.models import RiskAssessment
from app.event_model.risk_assessment_service import (
    HIGH_RISK_THRESHOLD,
    RISK_RULES,
    _normalize,
)
from app.hybrid.models import (
    DeterministicAssessment,
    DeterministicRiskLevel,
    DeterministicSignal,
)
from app.llm.models import ScamType

# Signals that are "soft" on their own (context/tone) rather than objective acts.
_SOFT_SIGNALS = {"urgency", "emotional_pressure"}

# Map each rule signal to the normalized boolean flags the Policy Engine reads.
_MONEY_SIGNALS = {"pix_or_payment"}
_CREDENTIAL_SIGNALS = {"password_or_code"}
_LINK_SIGNALS = {"unknown_link"}
_URGENCY_SIGNALS = {"urgency", "emotional_pressure"}
# The current rules have no bank/company impersonation detector; "new number"
# ("troquei de número") is the classic family-impersonation vector, so we use it
# as a weak deterministic proxy. Bank/company impersonation is left to the LLM.
_NEW_NUMBER_SIGNALS = {"new_number"}

# Weak scam-type hints derived from deterministic signals. The LLM refines these.
_SIGNAL_SCAM_TYPES = {
    "pix_or_payment": ScamType.PIX_FRAUD,
    "password_or_code": ScamType.CREDENTIAL_THEFT,
    "unknown_link": ScamType.MALICIOUS_LINK,
    "new_number": ScamType.FAMILY_IMPERSONATION,
}

CRITICAL_THRESHOLD = 90

_RULE_BY_SIGNAL = {rule.signal: rule for rule in RISK_RULES}


def _deterministic_level(score: int) -> DeterministicRiskLevel:
    if score >= CRITICAL_THRESHOLD:
        return DeterministicRiskLevel.CRITICAL
    if score >= HIGH_RISK_THRESHOLD:
        return DeterministicRiskLevel.HIGH
    if score >= 40:
        return DeterministicRiskLevel.MEDIUM
    return DeterministicRiskLevel.LOW


def _excerpt_for(signal: str, normalized_text: str) -> str:
    rule = _RULE_BY_SIGNAL.get(signal)
    if rule is None:
        return ""
    for pattern in rule.patterns:
        match = pattern.search(normalized_text)
        if match:
            start = max(0, match.start() - 20)
            end = min(len(normalized_text), match.end() + 20)
            snippet = normalized_text[start:end].strip()
            return snippet[:160]
    return ""


def build_deterministic_assessment(
    assessment: RiskAssessment,
    message_text: str,
) -> DeterministicAssessment:
    """Normalize an existing RiskAssessment into the provider-neutral shape.

    Reuses the rule weights/patterns; does not re-run or duplicate the rules.
    """
    normalized = _normalize(message_text or "")
    signal_names = list(assessment.signals)

    signals: List[DeterministicSignal] = []
    scam_types: List[ScamType] = []
    for name in signal_names:
        rule = _RULE_BY_SIGNAL.get(name)
        weight = rule.weight if rule else 0
        objective = name not in _SOFT_SIGNALS
        signals.append(
            DeterministicSignal(
                code=name,
                weight=weight,
                excerpt=_excerpt_for(name, normalized),
                rule_origin="risk_rules",
                rule_version="v1",
                objective=objective,
            )
        )
        hint = _SIGNAL_SCAM_TYPES.get(name)
        if hint and hint not in scam_types:
            scam_types.append(hint)

    signal_set = set(signal_names)
    has_new_number = bool(signal_set & _NEW_NUMBER_SIGNALS)
    objective_count = sum(1 for s in signals if s.objective)

    return DeterministicAssessment(
        score=assessment.score,
        risk_level=_deterministic_level(assessment.score),
        scam_types=scam_types,
        signals=signals,
        objective_signal_count=objective_count,
        has_money_request=bool(signal_set & _MONEY_SIGNALS),
        has_credential_request=bool(signal_set & _CREDENTIAL_SIGNALS),
        has_suspicious_link=bool(signal_set & _LINK_SIGNALS),
        has_urgency=bool(signal_set & _URGENCY_SIGNALS),
        has_impersonation=has_new_number,
        has_new_number_signal=has_new_number,
    )
