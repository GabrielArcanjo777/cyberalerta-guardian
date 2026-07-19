from __future__ import annotations

from app.event_model import EventModelService
from app.event_model.models import Message, MessageDirection
from app.hybrid.deterministic import build_deterministic_assessment
from app.hybrid.models import DeterministicRiskLevel
from app.llm.models import ScamType


def _assess(body: str):
    event_model = EventModelService.in_memory()
    message = Message(
        protected_person_id="pp-1",
        direction=MessageDirection.INBOUND,
        channel="whatsapp:test",
        body=body,
    )
    return event_model.risk_assessments.assess(message), body


def test_family_pix_scam_maps_flags():
    assessment, body = _assess("Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.")
    det = build_deterministic_assessment(assessment, body)
    assert det.has_money_request is True
    assert det.has_new_number_signal is True
    assert det.has_impersonation is True  # new-number proxy
    assert det.has_urgency is True
    assert det.risk_level in {DeterministicRiskLevel.HIGH, DeterministicRiskLevel.CRITICAL}
    assert ScamType.PIX_FRAUD in det.scam_types
    assert ScamType.FAMILY_IMPERSONATION in det.scam_types


def test_credential_request_maps_flag():
    assessment, body = _assess("Me manda o codigo que chegou no seu celular agora.")
    det = build_deterministic_assessment(assessment, body)
    assert det.has_credential_request is True
    assert ScamType.CREDENTIAL_THEFT in det.scam_types


def test_suspicious_link_maps_flag():
    assessment, body = _assess("Urgente: clique neste link https://x.invalid para regularizar.")
    det = build_deterministic_assessment(assessment, body)
    assert det.has_suspicious_link is True
    assert ScamType.MALICIOUS_LINK in det.scam_types


def test_benign_message_has_no_strong_flags():
    assessment, body = _assess("Oi, tudo bem? Bom dia!")
    det = build_deterministic_assessment(assessment, body)
    assert det.has_money_request is False
    assert det.has_credential_request is False
    assert det.has_suspicious_link is False
    assert det.risk_level == DeterministicRiskLevel.LOW
    assert det.objective_signal_count == 0


def test_signals_carry_excerpt_and_weight():
    assessment, body = _assess("Preciso de um Pix urgente agora.")
    det = build_deterministic_assessment(assessment, body)
    assert det.signals, "expected at least one signal"
    money = [s for s in det.signals if s.code == "pix_or_payment"]
    assert money and money[0].weight > 0
    assert money[0].rule_version == "v1"


def test_government_benefit_scam_maps_flag():
    assessment, body = _assess("Seu beneficio do INSS foi bloqueado, ligue urgente para regularizar.")
    det = build_deterministic_assessment(assessment, body)
    assert det.has_impersonation is True
    assert det.has_urgency is True
    assert ScamType.GOVERNMENT_BENEFIT_SCAM in det.scam_types


def test_fake_legal_threat_maps_flag():
    assessment, body = _assess("Voce tem um mandado de prisao em aberto, pague agora para evitar a captura.")
    det = build_deterministic_assessment(assessment, body)
    assert det.has_impersonation is True
    assert ScamType.FAKE_LEGAL_THREAT in det.scam_types


def test_soft_signals_not_counted_as_objective():
    assessment, body = _assess("urgente, por favor")
    det = build_deterministic_assessment(assessment, body)
    # urgency + emotional_pressure are soft; objective count should be 0.
    assert det.objective_signal_count == 0
