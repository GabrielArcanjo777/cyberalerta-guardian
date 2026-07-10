from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.consent.models import ConsentEvent, ConsentRecord
    from app.guardian_console.admin_case_models import AdminCase
    from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class AdminCaseMemoryStore:
    def __init__(self) -> None:
        self._cases: Dict[str, AdminCase] = {}
        self._initialized = False

    def _seed_cases(self) -> None:
        from app.guardian_console.admin_case_models import AdminCase, AdminCaseTraceStep

        if self._initialized:
            return
        samples = [
            AdminCase(
                case_id="case-demo-001",
                protected_person_alias="Dona Lucia",
                guardian_alias="Gabriel",
                source_channel="whatsapp_mock",
                received_content_summary="Mensagem simulando falso filho pedindo Pix urgente.",
                risk_score=87,
                risk_level="alto",
                scam_category="golpe_pix",
                detected_signals=["urgencia", "numero_novo", "pedido_pix", "isolamento"],
                agent_decision="Trust Lock recomendado antes de qualquer transferência.",
                agent_decision_trace=[
                    AdminCaseTraceStep(step="Entrada recebida", detail="Conteúdo encaminhado por canal simples."),
                    AdminCaseTraceStep(step="Sinais detectados", detail="Urgência, pedido financeiro e identidade não verificada."),
                    AdminCaseTraceStep(step="Decisão", detail="Pausar ação e acionar responsável."),
                ],
                trust_lock_status="recommended",
                trusted_circle_status="pending",
                proof_of_trust_status="not_started",
                recovery_status="not_needed",
                recommended_action="Confirmar com contato salvo antes de qualquer Pix.",
                protected_person_short_reply="Não faça Pix agora. Essa mensagem tem sinais de golpe e estou avisando Gabriel.",
                status="open",
                created_at="2026-01-01T10:00:00Z",
                updated_at="2026-01-01T10:00:00Z",
            ),
            AdminCase(
                case_id="case-demo-002",
                protected_person_alias="Seu Joao",
                guardian_alias="Gabriel",
                source_channel="whatsapp_mock",
                received_content_summary="Link suspeito fingindo ser banco pedindo atualização de cadastro.",
                risk_score=62,
                risk_level="medio",
                scam_category="link_suspeito",
                detected_signals=["urgencia", "link_externo"],
                agent_decision="Orientar pausa antes de clicar e revisar com responsável.",
                agent_decision_trace=[
                    AdminCaseTraceStep(step="Entrada recebida", detail="Canal simples com texto suspeito."),
                    AdminCaseTraceStep(step="Sinais detectados", detail="Link externo e pressão de urgência."),
                    AdminCaseTraceStep(step="Decisão", detail="Manter monitoramento e aguardar confirmação."),
                ],
                trust_lock_status="not_needed",
                trusted_circle_status="notified",
                proof_of_trust_status="not_started",
                recovery_status="not_needed",
                recommended_action="Não clicar no link. Confirmar no app oficial do banco.",
                protected_person_short_reply="Não clique nesse link. Ele pode ser perigoso e o caso será verificado com Gabriel.",
                status="reviewing",
                created_at="2026-01-02T14:20:00Z",
                updated_at="2026-01-02T15:05:00Z",
            ),
            AdminCase(
                case_id="case-demo-003",
                protected_person_alias="Maria Helena",
                guardian_alias="Ana",
                source_channel="whatsapp_mock",
                received_content_summary="Pedido de código SMS para suposta verificação de conta.",
                risk_score=91,
                risk_level="critico",
                scam_category="codigo_senha",
                detected_signals=["pedido_codigo", "urgencia", "falsa_autoridade"],
                agent_decision="Bloquear compartilhamento de credenciais e acionar responsável.",
                agent_decision_trace=[
                    AdminCaseTraceStep(step="Entrada recebida", detail="Canal simples com pedido de código."),
                    AdminCaseTraceStep(step="Sinais detectados", detail="Pedido de credencial e urgência."),
                    AdminCaseTraceStep(step="Decisão", detail="Trust Lock e alerta ao responsável."),
                ],
                trust_lock_status="recommended",
                trusted_circle_status="pending",
                proof_of_trust_status="in_progress",
                recovery_status="not_needed",
                recommended_action="Não enviar código. Confirmar com Ana por telefone salvo.",
                protected_person_short_reply="Não envie código nem senha. Aguarde até Ana confirmar.",
                status="confirmed_scam",
                created_at="2026-01-03T09:15:00Z",
                updated_at="2026-01-03T11:40:00Z",
            ),
        ]
        for case in samples:
            self._cases[case.case_id] = case
        self._initialized = True

    def ensure_initialized(self) -> None:
        self._seed_cases()

    def list_cases(self) -> List[AdminCase]:
        self.ensure_initialized()
        return sorted(self._cases.values(), key=lambda item: item.updated_at, reverse=True)

    def get_case(self, case_id: str) -> Optional[AdminCase]:
        self.ensure_initialized()
        return self._cases.get(case_id)

    def save_case(self, case: AdminCase) -> AdminCase:
        self.ensure_initialized()
        self._cases[case.case_id] = case
        return case

    def upsert_case(self, case: AdminCase) -> AdminCase:
        self.ensure_initialized()
        existing = self._cases.get(case.case_id)
        if existing:
            case.created_at = existing.created_at
        case.updated_at = _now_iso()
        self._cases[case.case_id] = case
        return case

    def case_count(self) -> int:
        self.ensure_initialized()
        return len(self._cases)


class ConsentMemoryStore:
    def __init__(self) -> None:
        self._records: Dict[str, ConsentRecord] = {}
        self._events: Dict[str, List[ConsentEvent]] = {}

    def get_or_create_record(
        self,
        protected_person_id: str,
        protected_person_alias: str = "Pessoa protegida",
        guardian_id: str | None = None,
        guardian_alias: str | None = None,
        channel_provider: str = "mock",
    ) -> "ConsentRecord":
        from app.consent.models import ConsentRecord

        existing = self._records.get(protected_person_id)
        if existing:
            return existing
        record = ConsentRecord(
            protected_person_id=protected_person_id,
            protected_person_alias=protected_person_alias,
            guardian_id=guardian_id,
            guardian_alias=guardian_alias,
            channel_provider=channel_provider,
        )
        self._records[protected_person_id] = record
        self._events[record.consent_id] = []
        return record

    def save_record(self, record: "ConsentRecord") -> "ConsentRecord":
        self._records[record.protected_person_id] = record
        self._events.setdefault(record.consent_id, [])
        return record

    def append_event(self, event: "ConsentEvent") -> "ConsentEvent":
        self._events.setdefault(event.consent_id, []).append(event)
        return event

    def list_events(self, consent_id: str) -> List["ConsentEvent"]:
        return list(self._events.get(consent_id, []))


class ProofTrustMemoryStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, dict] = {}

    def save_session(self, record: dict) -> dict:
        self._sessions[record["session_id"]] = record.copy()
        return self._sessions[record["session_id"]]

    def get_session(self, session_id: str) -> Optional[dict]:
        session = self._sessions.get(session_id)
        return session.copy() if session else None


class TrustedCircleMemoryStore:
    def __init__(self) -> None:
        self._log: Dict[str, "TrustedCircleEscalationRecord"] = {}

    def save(self, record: "TrustedCircleEscalationRecord") -> "TrustedCircleEscalationRecord":
        self._log[record.escalation_id] = record
        return record

    def get(self, escalation_id: str) -> Optional["TrustedCircleEscalationRecord"]:
        return self._log.get(escalation_id)

    def list_all(self) -> List[TrustedCircleEscalationRecord]:
        return sorted(self._log.values(), key=lambda item: item.created_at, reverse=True)

    def count(self) -> int:
        return len(self._log)

    def latest_for_case(self, case_id: str) -> Optional[TrustedCircleEscalationRecord]:
        matches = [item for item in self._log.values() if item.case_id == case_id]
        if not matches:
            return None
        return max(matches, key=lambda item: item.created_at)


class SettingsMemoryStore:
    def __init__(self) -> None:
        self._data: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    def put(self, key: str, value: str) -> None:
        self._data[key] = value
