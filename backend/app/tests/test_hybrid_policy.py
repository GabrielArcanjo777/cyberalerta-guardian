from __future__ import annotations

from app.hybrid.models import (
    DeterministicAssessment,
    DeterministicRiskLevel,
    DeterministicSignal,
    HybridAction,
    HybridDecisionContext,
)
from app.hybrid.policy import HybridDecisionPolicy, PolicyThresholds
from app.llm.models import (
    EvidenceStrength,
    LLMClassification,
    LLMScamAnalysisResult,
    ObjectiveEvidence,
    ScamType,
)

# The Policy Engine must be testable with no DB, no network, no FastAPI.

policy = HybridDecisionPolicy()

REAL = HybridDecisionContext(llm_enabled=True, shadow_mode=False, require_llm_for_auto_alert=True)
SHADOW = HybridDecisionContext(llm_enabled=True, shadow_mode=True, require_llm_for_auto_alert=True)


def _det(
    score: int,
    *,
    objective_signals: int = 0,
    money: bool = False,
    credential: bool = False,
    link: bool = False,
    urgency: bool = False,
    impersonation: bool = False,
    new_number: bool = False,
    scam_types=None,
) -> DeterministicAssessment:
    level = (
        DeterministicRiskLevel.CRITICAL if score >= 90
        else DeterministicRiskLevel.HIGH if score >= 65
        else DeterministicRiskLevel.MEDIUM if score >= 40
        else DeterministicRiskLevel.LOW
    )
    signals = [
        DeterministicSignal(code=f"sig{i}", weight=25, excerpt="trecho", objective=True)
        for i in range(objective_signals)
    ]
    return DeterministicAssessment(
        score=score,
        risk_level=level,
        signals=signals,
        objective_signal_count=objective_signals,
        scam_types=scam_types or [],
        has_money_request=money,
        has_credential_request=credential,
        has_suspicious_link=link,
        has_urgency=urgency,
        has_impersonation=impersonation,
        has_new_number_signal=new_number,
    )


def _llm(
    classification: LLMClassification,
    *,
    confidence: float = 0.9,
    risk_score: int = 80,
    scam_types=None,
    impersonated=None,
) -> LLMScamAnalysisResult:
    return LLMScamAnalysisResult(
        classification=classification,
        confidence=confidence,
        risk_score=risk_score,
        scam_types=scam_types or [],
        impersonated_entities=impersonated or [],
        objective_evidence=[
            ObjectiveEvidence(signal="PIX", excerpt="pix agora", strength=EvidenceStrength.HIGH)
        ],
    )


def _family_pix_scam() -> LLMScamAnalysisResult:
    return _llm(
        LLMClassification.SCAM,
        confidence=0.92,
        risk_score=88,
        scam_types=[ScamType.FAMILY_IMPERSONATION, ScamType.PIX_FRAUD],
        impersonated=["filho"],
    )


# --- DISCARD ------------------------------------------------------------------

def test_common_pix_mention_without_money_request_is_not_alert():
    # "mãe recebeu um pix hoje" — mentions pix, low score, no money *request*.
    d = policy.decide(_det(10), _llm(LLMClassification.BENIGN, confidence=0.9, risk_score=5), REAL, llm_available=True)
    assert d.action == HybridAction.DISCARD


def test_real_relative_talking_about_a_pix_discarded():
    d = policy.decide(_det(20), _llm(LLMClassification.BENIGN, confidence=0.88, risk_score=8), REAL, llm_available=True)
    assert d.action == HybridAction.DISCARD


def test_legitimate_boleto_no_fraud_signals_not_alert():
    d = policy.decide(_det(15), _llm(LLMClassification.BENIGN, confidence=0.85, risk_score=12), REAL, llm_available=True)
    assert d.action == HybridAction.DISCARD


# --- AUTO_ALERT (only with full agreement + evidence) -------------------------

def test_new_number_child_urgent_pix_is_auto_alert():
    d = policy.decide(
        _det(90, objective_signals=3, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.AUTO_ALERT
    assert d.shadow_decision is False


def test_fake_bank_asking_token_is_auto_alert():
    llm = _llm(
        LLMClassification.SCAM,
        confidence=0.9,
        risk_score=86,
        scam_types=[ScamType.BANK_IMPERSONATION, ScamType.CREDENTIAL_THEFT],
        impersonated=["banco"],
    )
    d = policy.decide(
        _det(70, objective_signals=2, credential=True),
        llm,
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.AUTO_ALERT


def test_two_strong_agreeing_signals_auto_alert():
    d = policy.decide(
        _det(80, objective_signals=2, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.AUTO_ALERT


# --- The inviolable AUTO_ALERT guards ----------------------------------------

def test_llm_alone_never_authorizes_when_rules_low():
    # Strong LLM SCAM but weak deterministic -> conflict, never AUTO_ALERT.
    d = policy.decide(_det(20), _family_pix_scam(), REAL, llm_available=True)
    assert d.action != HybridAction.AUTO_ALERT


def test_rules_alone_never_authorize_without_llm():
    # High deterministic, but LLM unavailable and required -> max REVIEW.
    d = policy.decide(
        _det(95, objective_signals=3, money=True, urgency=True, impersonation=True, new_number=True),
        None,
        REAL,
        llm_available=False,
    )
    assert d.action == HybridAction.REVIEW


def test_low_confidence_llm_never_auto_alert():
    d = policy.decide(
        _det(80, objective_signals=2, money=True, urgency=True, impersonation=True, new_number=True),
        _llm(LLMClassification.SCAM, confidence=0.60, risk_score=80,
             scam_types=[ScamType.FAMILY_IMPERSONATION, ScamType.PIX_FRAUD], impersonated=["filho"]),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW


def test_single_objective_signal_never_auto_alert():
    d = policy.decide(
        _det(70, objective_signals=1, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW


def test_deterministic_below_threshold_never_auto_alert():
    d = policy.decide(
        _det(50, objective_signals=2, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW


def test_no_risk_combination_never_auto_alert():
    # High everything but no A/B/C/D combination present.
    llm = _llm(LLMClassification.SCAM, confidence=0.95, risk_score=90, scam_types=[ScamType.UNKNOWN])
    d = policy.decide(_det(80, objective_signals=2), llm, REAL, llm_available=True)
    assert d.action == HybridAction.REVIEW


# --- REVIEW paths -------------------------------------------------------------

def test_llm_unavailable_medium_score_is_review():
    d = policy.decide(_det(50, objective_signals=1, money=True), None, REAL, llm_available=False)
    assert d.action == HybridAction.REVIEW


def test_llm_suspicious_is_review():
    d = policy.decide(
        _det(55, objective_signals=1, money=True),
        _llm(LLMClassification.SUSPICIOUS, confidence=0.7, risk_score=55),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW


def test_conflict_rules_high_llm_benign_is_review():
    d = policy.decide(
        _det(80, objective_signals=2, money=True),
        _llm(LLMClassification.BENIGN, confidence=0.9, risk_score=10),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW
    assert d.conflict is True


def test_conflict_rules_low_llm_scam_is_review():
    d = policy.decide(
        _det(15),
        _llm(LLMClassification.SCAM, confidence=0.9, risk_score=80),
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW
    assert d.conflict is True


def test_invalid_llm_output_forces_review():
    d = policy.decide(
        _det(80, objective_signals=2, money=True, urgency=True, impersonation=True, new_number=True),
        None,
        REAL,
        llm_available=False,
        invalid_llm_output=True,
    )
    assert d.action == HybridAction.REVIEW


def test_prompt_injection_forces_review():
    d = policy.decide(
        _det(80, objective_signals=2, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        REAL,
        llm_available=True,
        prompt_injection_suspected=True,
    )
    assert d.action == HybridAction.REVIEW


# --- shadow vs real -----------------------------------------------------------

def test_shadow_mode_records_intent_but_marks_shadow():
    d = policy.decide(
        _det(90, objective_signals=3, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        SHADOW,
        llm_available=True,
    )
    # The engine still computes "what it would do", but flags it as shadow.
    assert d.action == HybridAction.AUTO_ALERT
    assert d.shadow_decision is True


def test_score_components_are_transparent():
    d = policy.decide(
        _det(80, objective_signals=2, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),
        REAL,
        llm_available=True,
    )
    assert d.score_components is not None
    assert d.score_components.deterministic_weight == 0.60
    assert d.score_components.llm_weight == 0.40
    assert d.score_components.final_score == d.final_score


def test_thresholds_are_configurable():
    strict = HybridDecisionPolicy(PolicyThresholds(auto_alert_min_confidence=0.99))
    d = strict.decide(
        _det(90, objective_signals=3, money=True, urgency=True, impersonation=True, new_number=True),
        _family_pix_scam(),  # confidence 0.92 < 0.99
        REAL,
        llm_available=True,
    )
    assert d.action == HybridAction.REVIEW
