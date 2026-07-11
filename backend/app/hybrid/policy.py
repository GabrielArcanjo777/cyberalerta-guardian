from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.hybrid.models import (
    DeterministicAssessment,
    HybridAction,
    HybridDecision,
    HybridDecisionContext,
    ScoreComponents,
)
from app.llm.models import (
    LLMClassification,
    LLMScamAnalysisResult,
    ScamType,
)


@dataclass(frozen=True)
class PolicyThresholds:
    """Every constant the Policy Engine uses. Frozen + injectable so the whole
    decision matrix can be exercised in tests without patching globals."""

    discard_max_score: int = 30
    review_min_score: int = 40
    benign_confidence: float = 0.80
    auto_alert_min_deterministic: int = 65
    auto_alert_min_confidence: float = 0.85
    auto_alert_min_objective_signals: int = 2
    deterministic_weight: float = 0.60
    llm_weight: float = 0.40
    # Controlled, explicit bonuses (never hidden formulas).
    combo_bonus: int = 8
    # A strong conflict caps the outcome at REVIEW.
    conflict_score_gap: int = 40


# Scam types that mean "impersonating a bank / company / support / account".
_BANKISH_IMPERSONATION = {
    ScamType.BANK_IMPERSONATION,
    ScamType.TECH_SUPPORT_SCAM,
    ScamType.ACCOUNT_TAKEOVER,
}
_FAMILY_IMPERSONATION = {ScamType.FAMILY_IMPERSONATION}


@dataclass
class _Signals:
    """Combined (deterministic + LLM) boolean view used by the combinations."""

    money: bool
    credential: bool
    link: bool
    urgency: bool
    impersonation_any: bool
    impersonation_bankish: bool
    impersonation_family: bool
    new_number: bool


class HybridDecisionPolicy:
    """Pure, deterministic decision function. No network, no DB, no FastAPI.

    Only this class decides whether an alert *would* be sent (AUTO_ALERT). The
    caller still applies shadow mode and the safety gate before any real send.
    """

    def __init__(self, thresholds: Optional[PolicyThresholds] = None) -> None:
        self.t = thresholds or PolicyThresholds()

    # -- helpers ---------------------------------------------------------------

    def _combine_signals(
        self,
        deterministic: DeterministicAssessment,
        llm: Optional[LLMScamAnalysisResult],
    ) -> _Signals:
        llm_types = set(llm.scam_types) if llm else set()
        llm_impersonates = bool(llm and llm.impersonated_entities)
        bankish = bool(llm_types & _BANKISH_IMPERSONATION)
        family = bool(llm_types & _FAMILY_IMPERSONATION) or deterministic.has_new_number_signal
        return _Signals(
            money=deterministic.has_money_request or ScamType.PIX_FRAUD in llm_types,
            credential=deterministic.has_credential_request
            or ScamType.CREDENTIAL_THEFT in llm_types,
            link=deterministic.has_suspicious_link or ScamType.MALICIOUS_LINK in llm_types,
            urgency=deterministic.has_urgency,
            impersonation_any=deterministic.has_impersonation or llm_impersonates or bankish or family,
            impersonation_bankish=bankish,
            impersonation_family=family,
            new_number=deterministic.has_new_number_signal,
        )

    def _matched_combinations(self, s: _Signals) -> List[str]:
        matched: List[str] = []
        # A: money + impersonation + urgency
        if s.money and s.impersonation_any and s.urgency:
            matched.append("A_money_impersonation_urgency")
        # B: credential + bank/support impersonation
        if s.credential and s.impersonation_bankish:
            matched.append("B_credential_bank_impersonation")
        # C: link + (login/update/payment/install) + (urgency/threat)
        if s.link and (s.money or s.credential) and s.urgency:
            matched.append("C_link_action_urgency")
        # D: new number + family claim + money
        if s.new_number and s.impersonation_family and s.money:
            matched.append("D_newnumber_family_money")
        return matched

    def _blend_score(
        self,
        deterministic: DeterministicAssessment,
        llm: Optional[LLMScamAnalysisResult],
        combo_count: int,
    ) -> ScoreComponents:
        det = deterministic.score
        if llm is not None:
            blended = round(det * self.t.deterministic_weight + llm.risk_score * self.t.llm_weight)
            det_w, llm_w = self.t.deterministic_weight, self.t.llm_weight
            llm_score: Optional[int] = llm.risk_score
        else:
            blended = det
            det_w, llm_w = 1.0, 0.0
            llm_score = None
        bonus = self.t.combo_bonus if combo_count > 0 else 0
        final = max(0, min(100, blended + bonus))
        return ScoreComponents(
            deterministic_score=det,
            llm_score=llm_score,
            deterministic_weight=det_w,
            llm_weight=llm_w,
            blended=blended,
            policy_bonus=bonus,
            final_score=final,
        )

    # -- main ------------------------------------------------------------------

    def decide(
        self,
        deterministic: DeterministicAssessment,
        llm: Optional[LLMScamAnalysisResult],
        context: HybridDecisionContext,
        *,
        llm_available: bool = False,
        invalid_llm_output: bool = False,
        prompt_injection_suspected: bool = False,
    ) -> HybridDecision:
        reasons: List[str] = []
        s = self._combine_signals(deterministic, llm)
        combos = self._matched_combinations(s)
        components = self._blend_score(deterministic, llm, len(combos))
        final_score = components.final_score

        has_strong_signal = (
            s.money or s.credential or s.link or s.impersonation_any
        )

        # Conflict: rules and LLM strongly disagree.
        conflict = False
        if llm is not None:
            if deterministic.score >= self.t.auto_alert_min_deterministic and (
                llm.classification == LLMClassification.BENIGN
            ):
                conflict = True
                reasons.append("conflito: regras HIGH x LLM BENIGN")
            if deterministic.score < self.t.discard_max_score and (
                llm.classification == LLMClassification.SCAM
            ):
                conflict = True
                reasons.append("conflito: regras LOW x LLM SCAM")

        confidence = llm.confidence if llm is not None else 0.0

        # ---- try AUTO_ALERT (strongest gate) --------------------------------
        auto_alert_blocked_reason = self._auto_alert_block_reason(
            deterministic, llm, s, combos, context,
            llm_available=llm_available, conflict=conflict,
            invalid_llm_output=invalid_llm_output,
            prompt_injection=prompt_injection_suspected,
        )
        if auto_alert_blocked_reason is None:
            reasons.append("auto_alert: evidência objetiva + concordância + combinação")
            return self._build(
                HybridAction.AUTO_ALERT, final_score, confidence, reasons, deterministic,
                llm, s, context, components, conflict, combos,
            )
        else:
            reasons.append(f"auto_alert_bloqueado: {auto_alert_blocked_reason}")

        # ---- DISCARD --------------------------------------------------------
        if (
            deterministic.score < self.t.discard_max_score
            and not has_strong_signal
            and not conflict
            and not prompt_injection_suspected
            and not invalid_llm_output
        ):
            llm_says_benign = (
                llm is not None
                and llm.classification == LLMClassification.BENIGN
                and llm.confidence >= self.t.benign_confidence
            )
            if llm is None or llm_says_benign:
                reasons.append("discard: score baixo, sem sinais fortes, sem conflito")
                return self._build(
                    HybridAction.DISCARD, final_score, confidence, reasons, deterministic,
                    llm, s, context, components, conflict, combos,
                )

        # ---- default: REVIEW (safe) -----------------------------------------
        if invalid_llm_output or prompt_injection_suspected:
            reasons.append("review: saída LLM inválida ou possível injeção")
        elif not llm_available and deterministic.score >= self.t.review_min_score:
            reasons.append("review: LLM indisponível e score determinístico relevante")
        elif conflict:
            reasons.append("review: conflito entre regras e LLM")
        else:
            reasons.append("review: faixa intermediária ou evidência insuficiente")
        requires_human = True
        return self._build(
            HybridAction.REVIEW, final_score, confidence, reasons, deterministic,
            llm, s, context, components, conflict, combos, requires_human=requires_human,
        )

    def _auto_alert_block_reason(
        self,
        deterministic: DeterministicAssessment,
        llm: Optional[LLMScamAnalysisResult],
        s: _Signals,
        combos: List[str],
        context: HybridDecisionContext,
        *,
        llm_available: bool,
        conflict: bool,
        invalid_llm_output: bool,
        prompt_injection: bool,
    ) -> Optional[str]:
        """Return why AUTO_ALERT is NOT allowed, or None if all gates pass.

        Default posture blocks: any missing gate keeps the alert from firing.
        """
        if invalid_llm_output or prompt_injection:
            return "saida_invalida_ou_injecao"
        if context.require_llm_for_auto_alert and not llm_available:
            return "llm_obrigatoria_indisponivel"
        if llm is None or not llm_available:
            return "sem_llm"  # LLM alone never authorizes; and rules alone never do either
        if llm.classification != LLMClassification.SCAM:
            return "classificacao_nao_scam"
        if llm.confidence < self.t.auto_alert_min_confidence:
            return "confianca_baixa"
        if deterministic.score < self.t.auto_alert_min_deterministic:
            return "score_deterministico_baixo"
        if deterministic.objective_signal_count < self.t.auto_alert_min_objective_signals:
            return "poucos_sinais_objetivos"
        if conflict:
            return "conflito"
        if not combos:
            return "sem_combinacao_de_risco"
        return None

    def _build(
        self,
        action: HybridAction,
        final_score: int,
        confidence: float,
        reasons: List[str],
        deterministic: DeterministicAssessment,
        llm: Optional[LLMScamAnalysisResult],
        s: _Signals,
        context: HybridDecisionContext,
        components: ScoreComponents,
        conflict: bool,
        combos: List[str],
        *,
        requires_human: bool = False,
    ) -> HybridDecision:
        scam_types: List[ScamType] = list(deterministic.scam_types)
        if llm is not None:
            for t in llm.scam_types:
                if t not in scam_types:
                    scam_types.append(t)
        evidence = [f"{sig.code}:{sig.excerpt}" for sig in deterministic.signals if sig.excerpt]
        if llm is not None:
            evidence.extend(
                f"{ev.signal}:{ev.excerpt}" for ev in llm.objective_evidence if ev.excerpt
            )
        if combos:
            reasons = reasons + [f"combinacoes: {', '.join(combos)}"]
        return HybridDecision(
            action=action,
            final_score=final_score,
            confidence=confidence,
            reasons=reasons,
            policy_version=context.policy_version,
            llm_used=llm is not None,
            llm_available=llm is not None,
            deterministic_score=deterministic.score,
            llm_score=llm.risk_score if llm is not None else None,
            scam_types=scam_types,
            evidence=evidence[:12],
            requires_human_review=requires_human or (llm.requires_human_review if llm else False),
            shadow_decision=context.shadow_mode,
            conflict=conflict,
            score_components=components,
        )
