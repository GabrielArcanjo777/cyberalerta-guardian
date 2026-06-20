from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Pattern

from pydantic import BaseModel, Field

from app.services.text_normalization import normalize_text


class RiskSignal(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)
    weight: int = Field(ge=0, le=100)
    evidence: str = Field(min_length=1, max_length=240)


def _compile(*patterns: str) -> tuple[Pattern[str], ...]:
    return tuple(re.compile(pattern) for pattern in patterns)


@dataclass(frozen=True)
class RiskSignalRule:
    code: str
    label: str
    category: str
    weight: int
    patterns: tuple[Pattern[str], ...]
    evidence_template: str

    def match(self, normalized_text: str) -> RiskSignal | None:
        for pattern in self.patterns:
            match = pattern.search(normalized_text)
            if not match:
                continue
            return RiskSignal(
                code=self.code,
                label=self.label,
                category=self.category,
                weight=self.weight,
                evidence=self.evidence_template.format(term=match.group(0)),
            )
        return None


RISK_SIGNAL_RULES = (
    RiskSignalRule(
        code="pix_or_payment",
        label="Pedido financeiro ou Pix",
        category="financial_request",
        weight=25,
        patterns=_compile(r"\bpix\b", r"\btransfer\w*\b", r"\bpag(?:ar|amento)\w*\b", r"\bboleto\b"),
        evidence_template="Termo financeiro detectado: {term}.",
    ),
    RiskSignalRule(
        code="urgency",
        label="Urgencia",
        category="urgency",
        weight=15,
        patterns=_compile(r"\burgent\w*\b", r"\bagora\b", r"\brapido\b", r"\bimediat\w*\b", r"\bhoje\b"),
        evidence_template="Pressao por acao rapida: {term}.",
    ),
    RiskSignalRule(
        code="new_number",
        label="Numero novo",
        category="identity_change",
        weight=20,
        patterns=_compile(r"\btroquei de numero\b", r"\bmudei de numero\b", r"\bnumero novo\b", r"\bnovo numero\b"),
        evidence_template="Mudanca de identidade ou contato: {term}.",
    ),
    RiskSignalRule(
        code="do_not_call",
        label="Pedido para nao ligar",
        category="secrecy",
        weight=15,
        patterns=_compile(r"\bnao lig\w*\b", r"\bnao telefon\w*\b", r"\bsem ligar\b"),
        evidence_template="Tentativa de evitar verificacao: {term}.",
    ),
    RiskSignalRule(
        code="secrecy_request",
        label="Pedido de segredo",
        category="secrecy",
        weight=15,
        patterns=_compile(r"\bsegredo\b", r"\bnao (?:conte|contar|fale|avise)\b", r"\bnao fala\b"),
        evidence_template="Tentativa de isolamento: {term}.",
    ),
    RiskSignalRule(
        code="false_relative",
        label="Possivel falso familiar",
        category="impersonation",
        weight=20,
        patterns=_compile(r"\bmae\b", r"\bpai\b", r"\bfilh\w*\b", r"\bnet\w*\b", r"\btia\b", r"\btio\b"),
        evidence_template="Referencia familiar usada como identidade: {term}.",
    ),
    RiskSignalRule(
        code="fake_bank",
        label="Possivel falsa central ou banco",
        category="impersonation",
        weight=18,
        patterns=_compile(r"\bbanco\b", r"\bcentral\b", r"\bsuporte\b", r"\batendente\b", r"\bseguranca\b"),
        evidence_template="Autoridade ou suporte citado: {term}.",
    ),
    RiskSignalRule(
        code="sms_token",
        label="Pedido de codigo, SMS ou token",
        category="credential_request",
        weight=30,
        patterns=_compile(r"\bcodigo\b", r"\bsms\b", r"\btoken\b", r"\botp\b", r"\bsenha\b"),
        evidence_template="Pedido de credencial ou codigo: {term}.",
    ),
    RiskSignalRule(
        code="suspicious_link",
        label="Link suspeito",
        category="suspicious_link",
        weight=15,
        patterns=_compile(r"https?://", r"\bwww\.", r"\blink\b", r"\b[a-z0-9-]+\.(?:com|net|org|xyz|top|info)\b"),
        evidence_template="Link ou dominio detectado: {term}.",
    ),
    RiskSignalRule(
        code="remote_access",
        label="Acesso remoto",
        category="remote_access",
        weight=30,
        patterns=_compile(r"\banydesk\b", r"\bteamviewer\b", r"\bacesso remoto\b", r"\binstal\w* app\b", r"\bbaix\w* app\b"),
        evidence_template="Indicio de acesso remoto: {term}.",
    ),
    RiskSignalRule(
        code="job_fee",
        label="Taxa de emprego ou oportunidade",
        category="job_fee",
        weight=20,
        patterns=_compile(r"\btaxa\b.*\bempreg\w*\b", r"\bempreg\w*\b.*\btaxa\b", r"\bvaga\b.*\bpagar\b"),
        evidence_template="Cobranca ligada a emprego/oportunidade: {term}.",
    ),
)


class RiskSignalDetector:
    def detect(
        self,
        text: str,
        *,
        action_type: str | None = None,
        channel: str | None = None,
        already_acted: bool = False,
    ) -> list[RiskSignal]:
        normalized_text = normalize_text(text)
        signals: list[RiskSignal] = []
        seen_codes: set[str] = set()

        for rule in RISK_SIGNAL_RULES:
            signal = rule.match(normalized_text)
            if signal is None:
                continue
            if signal.code == "false_relative" and not self._has_impersonation_context(normalized_text):
                continue
            self._append_unique(signals, seen_codes, signal)

        self._append_action_type_signals(signals, seen_codes, action_type)
        if already_acted:
            self._append_unique(
                signals,
                seen_codes,
                RiskSignal(
                    code="already_acted",
                    label="Acao ja realizada",
                    category="already_acted",
                    weight=10,
                    evidence="A pessoa informou que ja realizou uma acao sensivel.",
                ),
            )
        return signals

    def _append_action_type_signals(
        self,
        signals: list[RiskSignal],
        seen_codes: set[str],
        action_type: str | None,
    ) -> None:
        normalized_action = normalize_text(action_type)
        if normalized_action in {"pix", "pagamento", "transferencia"}:
            self._append_unique(
                signals,
                seen_codes,
                RiskSignal(
                    code="pix_or_payment",
                    label="Pedido financeiro ou Pix",
                    category="financial_request",
                    weight=25,
                    evidence=f"Tipo de acao informado: {normalized_action}.",
                ),
            )
        if normalized_action in {"codigo", "senha", "token", "sms"}:
            self._append_unique(
                signals,
                seen_codes,
                RiskSignal(
                    code="sms_token",
                    label="Pedido de codigo, SMS ou token",
                    category="credential_request",
                    weight=30,
                    evidence=f"Tipo de acao informado: {normalized_action}.",
                ),
            )
        if normalized_action in {"taxa", "emprego"}:
            self._append_unique(
                signals,
                seen_codes,
                RiskSignal(
                    code="job_fee",
                    label="Taxa de emprego ou oportunidade",
                    category="job_fee",
                    weight=20,
                    evidence=f"Tipo de acao informado: {normalized_action}.",
                ),
            )

    def _has_impersonation_context(self, normalized_text: str) -> bool:
        context_terms = ("troquei", "mudei", "numero", "pix", "urgente", "codigo", "nao liga")
        return any(term in normalized_text for term in context_terms)

    def _append_unique(self, signals: list[RiskSignal], seen_codes: set[str], signal: RiskSignal) -> None:
        if signal.code in seen_codes:
            return
        seen_codes.add(signal.code)
        signals.append(signal)
