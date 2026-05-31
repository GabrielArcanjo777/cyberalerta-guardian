from __future__ import annotations

from typing import Literal, TypedDict

RiskTier = Literal["low", "medium", "high", "unknown"]


class EscalationRecommendation(TypedDict):
    tier: RiskTier
    recommended: bool
    action: str
    auto_escalate: bool
    status_if_requested: str
    demo_note: str


def normalize_risk_level(risk_level: str) -> str:
    return (risk_level or "").strip().lower()


def classify_risk_tier(risk_level: str) -> RiskTier:
    key = normalize_risk_level(risk_level)
    if key in {"critico", "crítico", "critical", "critica", "crítica"} or "crit" in key:
        return "high"
    if key in {"alto", "high", "elevado"}:
        return "high"
    if key in {"medio", "médio", "medium", "moderado"}:
        return "medium"
    if key in {"baixo", "low", "minimo", "mínimo"}:
        return "low"
    return "unknown"


def escalation_recommendation(risk_level: str) -> EscalationRecommendation:
    tier = classify_risk_tier(risk_level)

    if tier == "high":
        return EscalationRecommendation(
            tier=tier,
            recommended=True,
            action="trusted_circle",
            auto_escalate=False,
            status_if_requested="simulated_notified",
            demo_note="MVP: escalonamento simulado. Nenhuma notificação real será enviada.",
        )

    if tier == "medium":
        return EscalationRecommendation(
            tier=tier,
            recommended=False,
            action="guardian_review",
            auto_escalate=False,
            status_if_requested="review_suggested",
            demo_note="Risco médio: revisão do responsável sugerida antes de acionar o círculo.",
        )

    if tier == "low":
        return EscalationRecommendation(
            tier=tier,
            recommended=False,
            action="no_escalation",
            auto_escalate=False,
            status_if_requested="not_escalated",
            demo_note="Risco baixo: escalonamento automático não recomendado.",
        )

    return EscalationRecommendation(
        tier="unknown",
        recommended=False,
        action="guardian_review",
        auto_escalate=False,
        status_if_requested="review_suggested",
        demo_note="Nível de risco não reconhecido — tratar como revisão do responsável.",
    )


def allows_trusted_circle_escalation(risk_level: str) -> bool:
    return classify_risk_tier(risk_level) == "high"
