from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Pattern

from app.event_model import BotEventType, LocalEventBus, Message
from app.pattern_intelligence.models import (
    NormalizedThreatText,
    PatternCandidate,
    PatternCluster,
    PatternDetectionResult,
    PatternFeedback,
    PatternFeedbackRecord,
    PatternLevel,
    PatternSignal,
    RiskExplanation,
    utc_now,
)


LOW_THRESHOLD = 1
MEDIUM_THRESHOLD = 25
HIGH_THRESHOLD = 55
CRITICAL_THRESHOLD = 80

PATTERN_THRESHOLDS = {
    "low": LOW_THRESHOLD,
    "medium": MEDIUM_THRESHOLD,
    "high": HIGH_THRESHOLD,
    "critical": CRITICAL_THRESHOLD,
}

THREAT_TYPE_LABELS = {
    "false_relative": "Possivel falso parente",
    "fake_support_center": "Possivel falsa central",
    "benefit_regularization": "Beneficio ou regularizacao",
    "code_token": "Codigo, senha ou token",
    "pix_or_payment": "Pedido financeiro ou Pix",
    "suspicious_link": "Link suspeito",
    "new_number": "Numero novo",
    "unknown": "Padrao nao classificado",
    "neutral": "Sem padrao forte",
}


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    lowered = without_accents.lower()
    return " ".join(lowered.split())


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def score_level(score: int) -> PatternLevel:
    if score >= CRITICAL_THRESHOLD:
        return PatternLevel.CRITICAL
    if score >= HIGH_THRESHOLD:
        return PatternLevel.HIGH
    if score >= MEDIUM_THRESHOLD:
        return PatternLevel.MEDIUM
    return PatternLevel.LOW


def _patterns(*values: str) -> tuple[Pattern[str], ...]:
    return tuple(re.compile(value) for value in values)


@dataclass(frozen=True)
class PatternRule:
    signal: str
    label: str
    weight: int
    explanation: str
    patterns: tuple[Pattern[str], ...]

    def match_terms(self, normalized_text: str) -> list[str]:
        terms: list[str] = []
        for pattern in self.patterns:
            match = pattern.search(normalized_text)
            if match:
                terms.append(match.group(0))
        return terms


PATTERN_RULES = (
    PatternRule(
        signal="urgency",
        label="Urgencia",
        weight=12,
        explanation="A mensagem pressiona por acao imediata.",
        patterns=_patterns(r"\burgent\w*\b", r"\burgenc\w*\b", r"\bagora\b", r"\brapido\b", r"\bimediat\w*\b"),
    ),
    PatternRule(
        signal="pix_or_payment",
        label="Pix ou pagamento",
        weight=14,
        explanation="Ha pedido de pagamento, transferencia, boleto ou Pix.",
        patterns=_patterns(r"\bpix\b", r"\bpagamento\w*\b", r"\btransfer\w*\b", r"\bboleto\b", r"\bpagar\b"),
    ),
    PatternRule(
        signal="new_number",
        label="Numero novo",
        weight=12,
        explanation="A mensagem usa troca de numero como justificativa.",
        patterns=_patterns(r"\btroquei de numero\b", r"\bmudei de numero\b", r"\bnumero novo\b", r"\bnovo numero\b"),
    ),
    PatternRule(
        signal="suspicious_link",
        label="Link suspeito",
        weight=12,
        explanation="A mensagem inclui link ou dominio externo para acao.",
        patterns=_patterns(r"https?://", r"\bwww\.", r"\bbit\.ly\b", r"\blink\b", r"\b[a-z0-9-]+\.(?:com|net|org|invalid)\b"),
    ),
    PatternRule(
        signal="do_not_call",
        label="Pedido para nao ligar",
        weight=12,
        explanation="A mensagem tenta evitar verificacao por ligacao.",
        patterns=_patterns(r"\bnao lig\w*\b", r"\bnao telefon\w*\b"),
    ),
    PatternRule(
        signal="secrecy_request",
        label="Pedido de segredo",
        weight=12,
        explanation="A mensagem tenta isolar a pessoa protegida de terceiros.",
        patterns=_patterns(r"\bsegredo\b", r"\bnao (?:conte|contar|fale|avise)\b", r"\bnao fala\b"),
    ),
    PatternRule(
        signal="emotional_pressure",
        label="Pressao emocional",
        weight=10,
        explanation="A mensagem usa emocao ou emergencia para reduzir verificacao.",
        patterns=_patterns(r"\bpor favor\b", r"\bconfia em mim\b", r"\bdesesperad\w*\b", r"\bemergencia\b", r"\bpreciso muito\b"),
    ),
    PatternRule(
        signal="false_relative",
        label="Falso parente",
        weight=16,
        explanation="A mensagem simula relacao familiar com pedido sensivel.",
        patterns=_patterns(r"\bmae\b", r"\bpai\b", r"\bfilh\w*\b", r"\bnet\w*\b", r"\btia\b", r"\btio\b"),
    ),
    PatternRule(
        signal="fake_support_center",
        label="Falsa central",
        weight=14,
        explanation="A mensagem simula atendimento, banco, suporte ou seguranca.",
        patterns=_patterns(r"\bcentral\b", r"\bsuporte\b", r"\bbanco\b", r"\batendente\b", r"\bseguranca\b"),
    ),
    PatternRule(
        signal="benefit_regularization",
        label="Beneficio ou regularizacao",
        weight=10,
        explanation="A mensagem usa regularizacao, beneficio, cadastro ou bloqueio como pretexto.",
        patterns=_patterns(r"\bregulariz\w*\b", r"\bbeneficio\b", r"\bcadastro\b", r"\bbloquei\w*\b", r"\bconta\b", r"\bauxilio\b"),
    ),
    PatternRule(
        signal="code_token",
        label="Codigo ou token",
        weight=18,
        explanation="A mensagem pede codigo, senha, token ou OTP.",
        patterns=_patterns(r"\bcodigo\b", r"\bsenha\b", r"\btoken\b", r"\botp\b"),
    ),
)


RECURRENCE_SIGNALS = {
    "repeated_similar_text": PatternSignal(
        signal="repeated_similar_text",
        label="Mensagem parecida repetida",
        weight=10,
        matched_terms=[],
        explanation="Ha mensagem anterior com texto parecido.",
    ),
    "recurring_sender": PatternSignal(
        signal="recurring_sender",
        label="Remetente recorrente",
        weight=8,
        matched_terms=[],
        explanation="O mesmo remetente apareceu em outra mensagem analisada.",
    ),
    "recurring_protected_person": PatternSignal(
        signal="recurring_protected_person",
        label="Pessoa protegida recorrente",
        weight=8,
        matched_terms=[],
        explanation="A mesma pessoa protegida aparece em mais de uma mensagem suspeita.",
    ),
    "recurring_threat_type": PatternSignal(
        signal="recurring_threat_type",
        label="Tipo de golpe recorrente",
        weight=8,
        matched_terms=[],
        explanation="O mesmo tipo de golpe ja apareceu em outra mensagem analisada.",
    ),
}


class PatternIntelligenceService:
    def __init__(self, event_bus: LocalEventBus | None = None) -> None:
        self._event_bus = event_bus
        self._candidates: dict[str, PatternCandidate] = {}
        self._case_index: dict[str, str] = {}
        self._message_index: dict[str, str] = {}
        self._clusters: dict[str, PatternCluster] = {}
        self._feedback: list[PatternFeedbackRecord] = []

    def detect(
        self,
        *,
        message: Message,
        protected_person_id: str,
        protected_person_alias: str | None = None,
        sender_address: str | None = None,
        case_id: str | None = None,
    ) -> PatternDetectionResult:
        normalized = normalize_text(message.body)
        normalized_threat_text = self._normalized_threat_text(message.body, normalized)
        base_signals = self._rule_signals(normalized)
        base_signal_names = [signal.signal for signal in base_signals]
        threat_type = self._threat_type_for_signal_names(base_signal_names)
        threat_type_label = self._threat_type_label(threat_type)
        recurrence = self._recurrence(
            normalized,
            protected_person_id,
            protected_person_alias,
            sender_address,
            threat_type,
        )
        signals = list(base_signals)
        for key in (
            "repeated_similar_text",
            "recurring_sender",
            "recurring_protected_person",
            "recurring_threat_type",
        ):
            if recurrence.get(key, 0) > 0:
                signals.append(RECURRENCE_SIGNALS[key])

        score = min(100, sum(signal.weight for signal in signals))
        level = score_level(score)
        risk_explanation = self._risk_explanation(signals, recurrence, score, level, threat_type_label)
        candidate = PatternCandidate(
            message_id=message.message_id,
            case_id=case_id,
            protected_person_id=protected_person_id,
            protected_person_alias=protected_person_alias,
            sender_address=sender_address,
            normalized_text=normalized,
            normalized_text_sha1=normalized_threat_text.normalized_text_sha1,
            text_fingerprint=normalized_threat_text.text_fingerprint,
            normalized_threat_text=normalized_threat_text,
            threat_type=threat_type,
            threat_type_label=threat_type_label,
            score=score,
            level=level,
            signal_names=[signal.signal for signal in signals],
            risk_explanation=risk_explanation,
        )
        cluster_ids = self._assign_clusters(candidate, signals, recurrence)
        candidate = candidate.model_copy(update={"cluster_ids": cluster_ids})
        self._store_candidate(candidate)

        result = PatternDetectionResult(
            message_id=message.message_id,
            case_id=case_id,
            candidate_id=candidate.candidate_id,
            threat_type=threat_type,
            threat_type_label=threat_type_label,
            score=score,
            level=level,
            signals=signals,
            signal_names=[signal.signal for signal in signals],
            explanation=risk_explanation.summary,
            normalized_text=normalized,
            normalized_text_sha1=candidate.normalized_text_sha1,
            normalized_threat_text=normalized_threat_text,
            risk_explanation=risk_explanation,
            recurrence={key: value for key, value in recurrence.items() if isinstance(value, int)},
            similar_message_ids=list(recurrence.get("similar_message_ids", [])),
            cluster_ids=cluster_ids,
        )
        self._publish_pattern_detected(result)
        return result

    def get_result_for_case(self, case_id: str) -> PatternDetectionResult | None:
        candidate_id = self._case_index.get(case_id)
        if not candidate_id:
            return None
        candidate = self._candidates.get(candidate_id)
        if not candidate:
            return None
        signals = [
            signal
            for signal in self._signals_from_names(candidate.signal_names)
        ]
        recurrence = self._recurrence_for_candidate(candidate)
        risk_explanation = candidate.risk_explanation or self._risk_explanation(
            signals,
            recurrence,
            candidate.score,
            candidate.level,
            candidate.threat_type_label,
        )
        normalized_threat_text = candidate.normalized_threat_text or self._normalized_threat_text(
            candidate.normalized_text,
            candidate.normalized_text,
        )
        return PatternDetectionResult(
            message_id=candidate.message_id,
            case_id=candidate.case_id,
            candidate_id=candidate.candidate_id,
            threat_type=candidate.threat_type,
            threat_type_label=candidate.threat_type_label,
            score=candidate.score,
            level=candidate.level,
            signals=signals,
            signal_names=candidate.signal_names,
            explanation=risk_explanation.summary,
            normalized_text=candidate.normalized_text,
            normalized_text_sha1=candidate.normalized_text_sha1,
            normalized_threat_text=normalized_threat_text,
            risk_explanation=risk_explanation,
            recurrence=recurrence,
            similar_message_ids=self._similar_message_ids(candidate),
            cluster_ids=candidate.cluster_ids,
        )

    def get_candidate_for_case(self, case_id: str) -> PatternCandidate | None:
        candidate_id = self._case_index.get(case_id)
        return self._candidates.get(candidate_id) if candidate_id else None

    def list_clusters(self) -> list[PatternCluster]:
        return list(self._clusters.values())

    def list_candidates(self) -> list[PatternCandidate]:
        return list(self._candidates.values())

    def list_feedback(self) -> list[PatternFeedbackRecord]:
        return list(self._feedback)

    def record_feedback(
        self,
        *,
        case_id: str,
        feedback_action: str,
        note: str | None = None,
    ) -> PatternFeedback:
        expected_label = self._label_for_feedback(feedback_action)
        candidate_ids = [
            candidate.candidate_id
            for candidate in self._candidates.values()
            if candidate.case_id == case_id
        ]
        for candidate_id in candidate_ids:
            candidate = self._candidates[candidate_id]
            self._candidates[candidate_id] = candidate.model_copy(
                update={
                    "expected_label": expected_label,
                    "feedback_action": feedback_action,
                    "feedback_note": note,
                    "updated_at": utc_now(),
                }
            )
        record = PatternFeedback(
            case_id=case_id,
            candidate_ids=candidate_ids,
            feedback_action=feedback_action,
            expected_label=expected_label,
            confirmed_scam=expected_label == "confirmed_scam",
            false_positive=expected_label == "false_alarm",
            note=note,
        )
        self._feedback.append(record)
        return record

    def _normalized_threat_text(self, original_text: str, normalized_text: str) -> NormalizedThreatText:
        tokens = sorted(set(re.findall(r"[a-z0-9]+", normalized_text)))
        return NormalizedThreatText(
            original_length=len(original_text),
            normalized_text=normalized_text,
            normalized_text_sha1=sha1_text(normalized_text),
            text_fingerprint=sha1_text(" ".join(tokens[:40]))[:16],
            tokens=tokens,
        )

    def _threat_type_for_signal_names(self, signal_names: list[str]) -> str:
        if not signal_names:
            return "neutral"
        priority = [
            "false_relative",
            "fake_support_center",
            "benefit_regularization",
            "code_token",
            "pix_or_payment",
            "suspicious_link",
            "new_number",
        ]
        for signal in priority:
            if signal in signal_names:
                return signal
        return signal_names[0]

    def _threat_type_label(self, threat_type: str) -> str:
        return THREAT_TYPE_LABELS.get(threat_type, threat_type.replace("_", " "))

    def _risk_explanation(
        self,
        signals: list[PatternSignal],
        recurrence: dict[str, int | list[str]],
        score: int,
        level: PatternLevel,
        threat_type_label: str,
    ) -> RiskExplanation:
        summary = self._explanation(signals, recurrence, score, level)
        reasons = [
            f"{signal.label}: {signal.explanation}"
            for signal in signals[:8]
        ]
        if not reasons:
            reasons = ["Nenhum sinal forte foi detectado pelas regras atuais."]
        recommendation = self._recommendation_for(level, threat_type_label)
        return RiskExplanation(
            score=score,
            level=level,
            summary=summary,
            reasons=reasons,
            recommendation=recommendation,
            thresholds=PATTERN_THRESHOLDS,
        )

    def _recommendation_for(self, level: PatternLevel, threat_type_label: str) -> str:
        if level == PatternLevel.CRITICAL:
            return f"Pausar qualquer acao e revisar imediatamente: {threat_type_label}."
        if level == PatternLevel.HIGH:
            return f"Pausar pagamento, link ou envio de codigo e confirmar por canal independente: {threat_type_label}."
        if level == PatternLevel.MEDIUM:
            return "Revisar com calma e confirmar identidade antes de agir."
        return "Monitorar. As regras atuais nao indicam padrao forte."

    def _rule_signals(self, normalized_text: str) -> list[PatternSignal]:
        signals: list[PatternSignal] = []
        matched_names: set[str] = set()
        for rule in PATTERN_RULES:
            terms = rule.match_terms(normalized_text)
            if not terms:
                continue
            if rule.signal == "false_relative" and not self._has_false_relative_context(normalized_text):
                continue
            if rule.signal == "benefit_regularization" and not self._has_benefit_context(normalized_text):
                continue
            matched_names.add(rule.signal)
            signals.append(
                PatternSignal(
                    signal=rule.signal,
                    label=rule.label,
                    weight=rule.weight,
                    matched_terms=terms,
                    explanation=rule.explanation,
                )
            )
        return signals

    def _has_false_relative_context(self, normalized_text: str) -> bool:
        context = ("troquei", "mudei", "numero", "pix", "urgente", "agora", "codigo")
        return any(term in normalized_text for term in context)

    def _has_benefit_context(self, normalized_text: str) -> bool:
        context = ("regulariz", "beneficio", "cadastro", "bloque", "auxilio")
        return any(term in normalized_text for term in context)

    def _recurrence(
        self,
        normalized_text: str,
        protected_person_id: str,
        protected_person_alias: str | None,
        sender_address: str | None,
        threat_type: str,
    ) -> dict[str, int | list[str]]:
        similar_message_ids: list[str] = []
        for candidate in self._candidates.values():
            if self._similarity(normalized_text, candidate.normalized_text) >= 0.72:
                similar_message_ids.append(candidate.message_id)

        sender_count = sum(
            1
            for candidate in self._candidates.values()
            if sender_address and candidate.sender_address == sender_address
        )
        protected_count = sum(
            1
            for candidate in self._candidates.values()
            if candidate.protected_person_id == protected_person_id
            or (
                protected_person_alias
                and candidate.protected_person_alias
                and normalize_text(candidate.protected_person_alias) == normalize_text(protected_person_alias)
            )
        )
        threat_type_count = sum(
            1
            for candidate in self._candidates.values()
            if threat_type != "neutral" and candidate.threat_type == threat_type
        )
        return {
            "repeated_similar_text": len(similar_message_ids),
            "recurring_sender": sender_count,
            "recurring_protected_person": protected_count,
            "recurring_threat_type": threat_type_count,
            "similar_message_ids": similar_message_ids,
        }

    def _assign_clusters(
        self,
        candidate: PatternCandidate,
        signals: list[PatternSignal],
        recurrence: dict[str, int | list[str]],
    ) -> list[str]:
        cluster_keys: list[tuple[str, str]] = []
        signal_names = [signal.signal for signal in signals]
        primary = self._primary_cluster_signal(signal_names)
        if primary:
            cluster_keys.append((f"pattern:{primary}", f"Padrao: {primary.replace('_', ' ')}"))
        if recurrence.get("repeated_similar_text", 0):
            cluster_keys.append((f"similar:{candidate.text_fingerprint}", "Texto parecido recorrente"))
        if recurrence.get("recurring_sender", 0) and candidate.sender_address:
            cluster_keys.append((f"sender:{candidate.sender_address}", "Remetente recorrente"))
        if recurrence.get("recurring_protected_person", 0):
            cluster_keys.append((f"protected:{candidate.protected_person_id}", "Pessoa protegida visada novamente"))
        if recurrence.get("recurring_threat_type", 0):
            cluster_keys.append((f"threat_type:{candidate.threat_type}", candidate.threat_type_label))

        cluster_ids: list[str] = []
        for key, label in cluster_keys:
            cluster_id = f"pattern-cluster-{sha1_text(key)[:12]}"
            cluster = self._clusters.get(cluster_id)
            now = utc_now()
            if cluster is None:
                cluster = PatternCluster(
                    cluster_id=cluster_id,
                    cluster_type=key.split(":", 1)[0],
                    label=label,
                    signal_names=signal_names,
                    explanation=f"{label} com sinais: {', '.join(signal_names) or 'sem sinais'}.",
                    first_seen_at=now,
                    last_seen_at=now,
                )
            message_ids = self._append_unique(cluster.message_ids, candidate.message_id)
            case_ids = self._append_unique(cluster.case_ids, candidate.case_id)
            protected_ids = self._append_unique(cluster.protected_person_ids, candidate.protected_person_id)
            protected_aliases = self._append_unique(cluster.protected_person_aliases, candidate.protected_person_alias)
            senders = self._append_unique(cluster.sender_addresses, candidate.sender_address)
            occurrence_count = len(message_ids)
            previous_total = cluster.average_score * max(cluster.occurrence_count, 0)
            average_score = round((previous_total + candidate.score) / max(occurrence_count, 1), 2)
            self._clusters[cluster_id] = cluster.model_copy(
                update={
                    "signal_names": sorted(set(cluster.signal_names + signal_names)),
                    "message_ids": message_ids,
                    "case_ids": case_ids,
                    "protected_person_ids": protected_ids,
                    "protected_person_aliases": protected_aliases,
                    "sender_addresses": senders,
                    "occurrence_count": occurrence_count,
                    "average_score": average_score,
                    "last_seen_at": now,
                }
            )
            cluster_ids.append(cluster_id)
        return cluster_ids

    def _store_candidate(self, candidate: PatternCandidate) -> None:
        self._candidates[candidate.candidate_id] = candidate
        self._message_index[candidate.message_id] = candidate.candidate_id
        if candidate.case_id:
            self._case_index[candidate.case_id] = candidate.candidate_id

    def _publish_pattern_detected(self, result: PatternDetectionResult) -> None:
        if self._event_bus is None:
            return
        if not result.signal_names:
            return
        self._event_bus.publish_type(
            BotEventType.PATTERN_CANDIDATE_DETECTED,
            aggregate_type="case" if result.case_id else "message",
            aggregate_id=result.case_id or result.message_id or result.detection_id,
            case_id=result.case_id,
            payload={
                "message_id": result.message_id,
                "case_id": result.case_id,
                "threat_type": result.threat_type,
                "threat_type_label": result.threat_type_label,
                "pattern_score": result.score,
                "pattern_level": result.level.value,
                "signals": result.signal_names,
                "explanation": result.explanation,
                "risk_reasons": result.risk_explanation.reasons,
                "recommendation": result.risk_explanation.recommendation,
                "cluster_ids": result.cluster_ids,
                "recurrence": result.recurrence,
                "similar_message_ids": result.similar_message_ids,
                "candidate_id": result.candidate_id,
                "normalized_text_sha1": result.normalized_text_sha1,
                "text_fingerprint": result.normalized_threat_text.text_fingerprint,
                "simulated": True,
            },
        )

    def _signals_from_names(self, names: list[str]) -> list[PatternSignal]:
        all_signals = {
            rule.signal: PatternSignal(
                signal=rule.signal,
                label=rule.label,
                weight=rule.weight,
                matched_terms=[],
                explanation=rule.explanation,
            )
            for rule in PATTERN_RULES
        }
        all_signals.update(RECURRENCE_SIGNALS)
        return [all_signals[name] for name in names if name in all_signals]

    def _explanation(
        self,
        signals: list[PatternSignal],
        recurrence: dict[str, int | list[str]],
        score: int,
        level: PatternLevel,
    ) -> str:
        if not signals:
            return "Nenhum padrao forte foi detectado pelas regras atuais."
        labels = ", ".join(signal.label for signal in signals[:5])
        recurrence_count = sum(
            int(value)
            for key, value in recurrence.items()
            if key != "similar_message_ids" and isinstance(value, int)
        )
        suffix = f" Recorrencia observada: {recurrence_count}." if recurrence_count else ""
        return f"Score {score}/100 ({level.value}) por sinais: {labels}.{suffix}"

    def _primary_cluster_signal(self, signal_names: list[str]) -> str | None:
        priority = [
            "false_relative",
            "fake_support_center",
            "code_token",
            "pix_or_payment",
            "benefit_regularization",
            "suspicious_link",
        ]
        for signal in priority:
            if signal in signal_names:
                return signal
        return signal_names[0] if signal_names else None

    def _recurrence_for_candidate(self, candidate: PatternCandidate) -> dict[str, int]:
        similar_count = len(self._similar_message_ids(candidate))
        sender_count = sum(
            1
            for item in self._candidates.values()
            if item.candidate_id != candidate.candidate_id
            and candidate.sender_address
            and item.sender_address == candidate.sender_address
        )
        protected_count = sum(
            1
            for item in self._candidates.values()
            if item.candidate_id != candidate.candidate_id
            and (
                item.protected_person_id == candidate.protected_person_id
                or (
                    item.protected_person_alias
                    and candidate.protected_person_alias
                    and normalize_text(item.protected_person_alias) == normalize_text(candidate.protected_person_alias)
                )
            )
        )
        threat_type_count = sum(
            1
            for item in self._candidates.values()
            if item.candidate_id != candidate.candidate_id
            and candidate.threat_type != "neutral"
            and item.threat_type == candidate.threat_type
        )
        return {
            "repeated_similar_text": similar_count,
            "recurring_sender": sender_count,
            "recurring_protected_person": protected_count,
            "recurring_threat_type": threat_type_count,
        }

    def _similar_message_ids(self, candidate: PatternCandidate) -> list[str]:
        return [
            item.message_id
            for item in self._candidates.values()
            if item.candidate_id != candidate.candidate_id
            and self._similarity(candidate.normalized_text, item.normalized_text) >= 0.72
        ]

    def _fingerprint(self, normalized_text: str) -> str:
        tokens = sorted(set(re.findall(r"[a-z0-9]+", normalized_text)))
        return sha1_text(" ".join(tokens[:40]))[:16]

    def _similarity(self, first: str, second: str) -> float:
        first_tokens = set(re.findall(r"[a-z0-9]+", first))
        second_tokens = set(re.findall(r"[a-z0-9]+", second))
        if not first_tokens or not second_tokens:
            return 0
        return len(first_tokens & second_tokens) / len(first_tokens | second_tokens)

    def _append_unique(self, values: list[str], value: str | None) -> list[str]:
        if not value or value in values:
            return list(values)
        return [*values, value]

    def _label_for_feedback(self, action: str) -> str:
        if action == "confirm_scam":
            return "confirmed_scam"
        if action == "false_alarm":
            return "false_alarm"
        if action == "needs_review":
            return "needs_review"
        if action == "mark_resolved":
            return "resolved"
        return action
