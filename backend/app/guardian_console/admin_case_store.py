from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.guardian_console.admin_case_models import AdminCase, AdminCaseTraceStep

_CASES: Dict[str, AdminCase] = {}
_INITIALIZED = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _seed_cases() -> None:
    global _INITIALIZED
    if _INITIALIZED:
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
        _CASES[case.case_id] = case
    _INITIALIZED = True


def ensure_initialized() -> None:
    _seed_cases()


def list_cases() -> List[AdminCase]:
    ensure_initialized()
    return sorted(_CASES.values(), key=lambda item: item.updated_at, reverse=True)


def get_case(case_id: str) -> Optional[AdminCase]:
    ensure_initialized()
    return _CASES.get(case_id)


def save_case(case: AdminCase) -> AdminCase:
    ensure_initialized()
    _CASES[case.case_id] = case
    return case


def upsert_case(case: AdminCase) -> AdminCase:
    ensure_initialized()
    existing = _CASES.get(case.case_id)
    if existing:
        case.created_at = existing.created_at
    case.updated_at = _now_iso()
    _CASES[case.case_id] = case
    return case


def case_count() -> int:
    ensure_initialized()
    return len(_CASES)
