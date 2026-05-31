from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import HTTPException

from app.guardian_console.admin_case_models import (
    AdminCase,
    AdminCaseFromChannelRequest,
    AdminCaseListResponse,
    AdminCaseStatusUpdateRequest,
    AdminCaseTraceStep,
    GuardianConsoleStatusResponse,
    VALID_CASE_STATUSES,
)
from app.guardian_console import admin_case_store


def build_trace_from_channel(
    *,
    signals: List[str],
    risk_level: str,
    trust_lock_status: str,
) -> List[AdminCaseTraceStep]:
    signal_text = ", ".join(signals) if signals else "nenhum sinal forte"
    return [
        AdminCaseTraceStep(
            step="Entrada recebida",
            detail="Caso recebido pelo canal simples com consentimento da pessoa protegida.",
        ),
        AdminCaseTraceStep(
            step="Sinais detectados",
            detail=f"Sinais: {signal_text}.",
        ),
        AdminCaseTraceStep(
            step="Decisão",
            detail=(
                "Pausa protetiva recomendada e responsável notificado."
                if trust_lock_status == "recommended" or risk_level in {"alto", "critico"}
                else "Monitorar e orientar verificação segura."
            ),
        ),
    ]


def summarize_content(content: str, max_len: int = 120) -> str:
    cleaned = " ".join(content.split())
    if len(cleaned) <= max_len:
        return cleaned
    return cleaned[: max_len - 3] + "..."


class AdminCaseService:
    def get_status(self) -> GuardianConsoleStatusResponse:
        admin_case_store.ensure_initialized()
        return GuardianConsoleStatusResponse(
            service="guardian-admin-case-console",
            mode="in_memory_demo",
            storage="mock_store",
            case_count=admin_case_store.case_count(),
            auth_enabled=False,
            notifications_enabled=False,
            demo_note=(
                "Console operacional simulado. Sem login, banco persistente ou envio real de mensagens."
            ),
        )

    def list_cases(self) -> AdminCaseListResponse:
        cases = admin_case_store.list_cases()
        return AdminCaseListResponse(cases=cases, total=len(cases))

    def get_case(self, case_id: str) -> AdminCase:
        case = admin_case_store.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Caso nao encontrado.")
        return case

    def update_status(self, case_id: str, payload: AdminCaseStatusUpdateRequest) -> AdminCase:
        if payload.status not in VALID_CASE_STATUSES:
            raise HTTPException(status_code=400, detail="Status de caso invalido.")

        case = self.get_case(case_id)
        case.status = payload.status
        case.updated_at = admin_case_store._now_iso()

        if payload.status == "recovery_needed":
            case.recovery_status = "needed"
        if payload.status == "verified_safe":
            case.trust_lock_status = "released"
            case.trusted_circle_status = "resolved"
        if payload.status == "confirmed_scam":
            case.trusted_circle_status = "notified"
        if payload.status == "reviewing":
            case.proof_of_trust_status = (
                "in_progress" if case.proof_of_trust_status == "not_started" else case.proof_of_trust_status
            )

        return admin_case_store.save_case(case)

    def create_from_channel(self, payload: AdminCaseFromChannelRequest) -> AdminCase:
        case_id = payload.channel_case_id or f"case-{uuid4().hex[:10]}"
        existing = admin_case_store.get_case(case_id)
        if existing:
            case_id = f"case-{uuid4().hex[:10]}"

        trace = payload.agent_decision_trace or build_trace_from_channel(
            signals=payload.detected_signals,
            risk_level=payload.risk_level,
            trust_lock_status=payload.trust_lock_status,
        )

        case = AdminCase(
            case_id=case_id,
            protected_person_alias=payload.protected_person_alias,
            guardian_alias=payload.guardian_alias or "Responsável",
            source_channel=payload.source_channel,
            received_content_summary=payload.received_content_summary,
            risk_score=payload.risk_score,
            risk_level=payload.risk_level,
            scam_category=payload.scam_category,
            detected_signals=payload.detected_signals,
            agent_decision=payload.agent_decision,
            agent_decision_trace=trace,
            trust_lock_status=payload.trust_lock_status,
            trusted_circle_status=payload.trusted_circle_status,
            proof_of_trust_status=payload.proof_of_trust_status,
            recovery_status=payload.recovery_status,
            recommended_action=payload.recommended_action,
            protected_person_short_reply=payload.protected_person_short_reply,
            status=payload.status,
            created_at=admin_case_store._now_iso(),
            updated_at=admin_case_store._now_iso(),
        )
        return admin_case_store.upsert_case(case)

    def create_from_simple_channel_record(self, record: Dict[str, Any]) -> Optional[AdminCase]:
        if not record.get("admin_case_created"):
            return None

        channel_case_id = record.get("channel_case_id")
        protected = record.get("protected_response") or {}
        short_reply = protected.get("short_reply")

        trust_lock = "recommended" if record.get("trust_lock_recommended") else "not_needed"
        signals = record.get("signals") or []
        risk_level = record.get("risk_level", "medio")
        category = record.get("category", "generico")

        agent_decision = (
            "Trust Lock recomendado antes de qualquer transferência."
            if trust_lock == "recommended"
            else "Monitorar e orientar verificação segura com o responsável."
        )

        recommended = (
            "Confirmar com contato salvo antes de qualquer Pix."
            if category == "golpe_pix"
            else "Não clicar em links e confirmar por canal oficial."
        )

        return self.create_from_channel(
            AdminCaseFromChannelRequest(
                channel_case_id=channel_case_id,
                protected_person_alias=record.get("protected_person_alias", "Pessoa protegida"),
                guardian_alias=record.get("trusted_contact_alias") or "Gabriel",
                source_channel=record.get("channel", "whatsapp_mock"),
                received_content_summary=summarize_content(record.get("content", "")),
                risk_score=int(record.get("risk_score", 0)),
                risk_level=risk_level,
                scam_category=category,
                detected_signals=signals,
                agent_decision=agent_decision,
                agent_decision_trace=build_trace_from_channel(
                    signals=signals,
                    risk_level=risk_level,
                    trust_lock_status=trust_lock,
                ),
                trust_lock_status=trust_lock,
                trusted_circle_status="pending" if trust_lock == "recommended" else "notified",
                proof_of_trust_status="not_started",
                recovery_status="not_needed",
                recommended_action=recommended,
                protected_person_short_reply=short_reply,
                status="open",
            )
        )
