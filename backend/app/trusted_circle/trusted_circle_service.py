from __future__ import annotations

from typing import List
from uuid import uuid4

from fastapi import HTTPException

from app.storage import admin_case_store, trusted_circle_store
from app.trusted_circle.escalation_rules import escalation_recommendation
from app.trusted_circle.trusted_circle_models import (
    TrustedCircleEscalateRequest,
    TrustedCircleEscalateResponse,
    TrustedCircleEscalationRecord,
    TrustedCircleStatusResponse,
)


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sanitize_aliases(contacts: List[str]) -> List[str]:
    cleaned: List[str] = []
    for name in contacts:
        alias = " ".join((name or "").split()).strip()
        if not alias:
            continue
        if any(char.isdigit() for char in alias) and len(alias) > 12:
            continue
        if "@" in alias:
            continue
        cleaned.append(alias[:64])
    return cleaned or ["Responsável"]


def build_guardian_message(protected_person_alias: str, reason: str) -> str:
    reason_clean = " ".join(reason.split())
    if len(reason_clean) > 120:
        reason_clean = reason_clean[:117] + "..."
    return (
        f"{protected_person_alias} recebeu uma mensagem com sinais de risco "
        f"({reason_clean}). Verifique antes de qualquer transferência."
    )


def _sync_admin_case(case_id: str, trusted_circle_status: str) -> None:
    admin_case_store.ensure_initialized()
    case = admin_case_store.get_case(case_id)
    if not case:
        return
    case.trusted_circle_status = trusted_circle_status
    if trusted_circle_status == "simulated_notified":
        if case.proof_of_trust_status == "not_started":
            case.proof_of_trust_status = "recommended"
    if trusted_circle_status == "review_suggested" and case.proof_of_trust_status == "not_started":
        case.proof_of_trust_status = "recommended"
    case.updated_at = _now_iso()
    admin_case_store.save_case(case)


class TrustedCircleService:
    def get_status(self) -> TrustedCircleStatusResponse:
        return TrustedCircleStatusResponse(
            service="trusted-circle-escalation",
            mode="in_memory_demo",
            real_notifications_enabled=False,
            escalation_count=trusted_circle_store.count(),
            demo_note=(
                "Escalonamento simulado no MVP. Contatos são aliases; "
                "nenhum WhatsApp, SMS ou e-mail real é enviado."
            ),
        )

    def escalate(self, payload: TrustedCircleEscalateRequest) -> TrustedCircleEscalateResponse:
        recommendation = escalation_recommendation(payload.risk_level)
        contacts = _sanitize_aliases(payload.trusted_contacts)
        message = build_guardian_message(payload.protected_person_alias, payload.reason)
        escalation_id = f"esc-{uuid4().hex[:10]}"

        admin_case_store.ensure_initialized()
        case = admin_case_store.get_case(payload.case_id)
        if case and not payload.trusted_contacts:
            contacts = _sanitize_aliases([case.guardian_alias])

        status = recommendation["status_if_requested"]
        proof_recommended = status in {"simulated_notified", "review_suggested"}

        if status == "not_escalated":
            response = TrustedCircleEscalateResponse(
                escalation_id=escalation_id,
                status="not_escalated",
                message_to_guardian=(
                    "Risco baixo: escalonamento do círculo de confiança não é recomendado. "
                    "Monitore o caso e oriente a pessoa protegida se necessário."
                ),
                trusted_contacts=contacts,
                proof_of_trust_recommended=False,
                sent_real_notification=False,
                demo_note=recommendation["demo_note"],
                case_id=payload.case_id,
                risk_level=payload.risk_level,
                escalation_recommended=False,
            )
            _sync_admin_case(payload.case_id, "not_required")
            return response

        if status == "review_suggested":
            record = TrustedCircleEscalationRecord(
                escalation_id=escalation_id,
                case_id=payload.case_id,
                risk_level=payload.risk_level,
                protected_person_alias=payload.protected_person_alias,
                trusted_contacts=contacts,
                reason=payload.reason,
                status="review_suggested",
                message_to_guardian=(
                    f"Revisão sugerida para o responsável: {message} "
                    "Acione o círculo de confiança apenas se a situação evoluir."
                ),
                proof_of_trust_recommended=True,
                sent_real_notification=False,
                created_at=_now_iso(),
            )
            trusted_circle_store.save(record)
            _sync_admin_case(payload.case_id, "review_suggested")
            return TrustedCircleEscalateResponse(
                escalation_id=escalation_id,
                status="review_suggested",
                message_to_guardian=record.message_to_guardian,
                trusted_contacts=contacts,
                proof_of_trust_recommended=True,
                sent_real_notification=False,
                demo_note=recommendation["demo_note"],
                case_id=payload.case_id,
                risk_level=payload.risk_level,
                escalation_recommended=False,
            )

        record = TrustedCircleEscalationRecord(
            escalation_id=escalation_id,
            case_id=payload.case_id,
            risk_level=payload.risk_level,
            protected_person_alias=payload.protected_person_alias,
            trusted_contacts=contacts,
            reason=payload.reason,
            status="simulated_notified",
            message_to_guardian=message,
            proof_of_trust_recommended=True,
            sent_real_notification=False,
            created_at=_now_iso(),
        )
        trusted_circle_store.save(record)
        _sync_admin_case(payload.case_id, "simulated_notified")

        return TrustedCircleEscalateResponse(
            escalation_id=escalation_id,
            status="simulated_notified",
            message_to_guardian=message,
            trusted_contacts=contacts,
            proof_of_trust_recommended=True,
            sent_real_notification=False,
            demo_note=recommendation["demo_note"],
            case_id=payload.case_id,
            risk_level=payload.risk_level,
            escalation_recommended=True,
        )

    def get_escalation(self, escalation_id: str) -> TrustedCircleEscalationRecord:
        record = trusted_circle_store.get(escalation_id)
        if not record:
            raise HTTPException(status_code=404, detail="Escalonamento não encontrado.")
        return record
