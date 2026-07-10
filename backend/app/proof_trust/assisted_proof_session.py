from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal, Optional
from uuid import uuid4

from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.storage import admin_case_store, proof_trust_store
from app.proof_trust.assisted_verification_steps import (
    all_steps_completed,
    build_initial_steps,
    current_step_id,
    validate_step_id,
)

SessionStatus = Literal[
    "not_started",
    "in_progress",
    "verified_safe",
    "confirmed_scam",
    "inconclusive",
    "blocked",
]

FinalDecision = Literal["verified_safe", "confirmed_scam", "inconclusive", "blocked"]

StepStatus = Literal["pending", "completed", "skipped"]


class ProofTrustStepItem(BaseModel):
    id: str
    title: str
    status: StepStatus
    guidance: Optional[str] = None
    note: Optional[str] = None


class AssistedProofSessionCreateRequest(BaseModel):
    case_id: str
    protected_person_alias: str
    guardian_alias: str
    risk_level: str
    suspected_request: str
    trusted_contact_alias: str


class AssistedProofStepUpdateRequest(BaseModel):
    step_id: str
    status: StepStatus = "completed"
    note: Optional[str] = Field(default=None, max_length=500)
    final_decision: Optional[FinalDecision] = None


class AssistedProofSessionResponse(BaseModel):
    session_id: str
    case_id: str
    status: SessionStatus
    current_step: str
    steps: List[ProofTrustStepItem]
    final_decision: Optional[FinalDecision] = None
    guardian_note: Optional[str] = None
    protected_person_alias: Optional[str] = None
    guardian_alias: Optional[str] = None
    trusted_contact_alias: Optional[str] = None
    suspected_request: Optional[str] = None
    demo_note: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_session(session_id: str) -> dict:
    record = proof_trust_store.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Sessão de verificação não encontrada.")
    return record


def _normalize_risk(risk_level: str) -> str:
    return (risk_level or "").strip().lower()


def _high_risk(risk_level: str) -> bool:
    key = _normalize_risk(risk_level)
    return key in {"alto", "critico", "crítico", "critical"} or "crit" in key


def _to_response(record: dict) -> AssistedProofSessionResponse:
    return AssistedProofSessionResponse(
        session_id=record["session_id"],
        case_id=record["case_id"],
        status=record["status"],
        current_step=record["current_step"],
        steps=[ProofTrustStepItem(**step) for step in record["steps"]],
        final_decision=record.get("final_decision"),
        guardian_note=record.get("guardian_note"),
        protected_person_alias=record.get("protected_person_alias"),
        guardian_alias=record.get("guardian_alias"),
        trusted_contact_alias=record.get("trusted_contact_alias"),
        suspected_request=record.get("suspected_request"),
        demo_note=record["demo_note"],
    )


def _sync_admin_case(case_id: str, session_status: SessionStatus, final_decision: Optional[FinalDecision]) -> None:
    admin_case_store.ensure_initialized()
    case = admin_case_store.get_case(case_id)
    if not case:
        return

    case.proof_of_trust_status = "in_progress"
    case.updated_at = _now_iso()

    if session_status == "in_progress":
        case.proof_of_trust_status = "in_progress"
    elif final_decision == "verified_safe" or session_status == "verified_safe":
        case.proof_of_trust_status = "completed"
        case.trust_lock_status = "released"
        case.status = "verified_safe"
    elif final_decision == "confirmed_scam" or session_status == "confirmed_scam":
        case.proof_of_trust_status = "completed"
        case.trust_lock_status = "recommended"
        case.status = "confirmed_scam"
        case.recovery_status = "needed"
    elif final_decision in {"inconclusive", "blocked"} or session_status in {"inconclusive", "blocked"}:
        case.proof_of_trust_status = "in_progress"
        case.trust_lock_status = "recommended"

    admin_case_store.save_case(case)


def _resolve_session_status(final_decision: FinalDecision) -> SessionStatus:
    return final_decision  # type: ignore[return-value]


class AssistedProofTrustService:
    DEMO_NOTE = (
        "Verificação segura simulada no MVP. Canal independente apenas; "
        "sem consulta a banco, governo, CPF ou documentos reais."
    )

    def create_session(self, payload: AssistedProofSessionCreateRequest) -> AssistedProofSessionResponse:
        admin_case_store.ensure_initialized()
        if not admin_case_store.get_case(payload.case_id):
            raise HTTPException(status_code=404, detail="Caso não encontrado.")

        if not _high_risk(payload.risk_level):
            raise HTTPException(
                status_code=400,
                detail="Proof of Trust assistido recomendado apenas para risco alto ou crítico.",
            )

        session_id = f"proof-{uuid4().hex[:10]}"
        steps = build_initial_steps()
        record = {
            "session_id": session_id,
            "case_id": payload.case_id,
            "status": "in_progress",
            "current_step": current_step_id(steps),
            "steps": steps,
            "final_decision": None,
            "guardian_note": None,
            "protected_person_alias": payload.protected_person_alias,
            "guardian_alias": payload.guardian_alias,
            "trusted_contact_alias": payload.trusted_contact_alias,
            "suspected_request": payload.suspected_request,
            "demo_note": self.DEMO_NOTE,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        }
        record = proof_trust_store.save_session(record)
        _sync_admin_case(payload.case_id, "in_progress", None)

        case = admin_case_store.get_case(payload.case_id)
        if case:
            case.proof_of_trust_status = "in_progress"
            admin_case_store.save_case(case)

        return _to_response(record)

    def get_session(self, session_id: str) -> AssistedProofSessionResponse:
        record = _load_session(session_id)
        return _to_response(record)

    def update_step(
        self, session_id: str, payload: AssistedProofStepUpdateRequest
    ) -> AssistedProofSessionResponse:
        record = _load_session(session_id)

        if record["status"] not in {"in_progress", "not_started"}:
            raise HTTPException(status_code=400, detail="Sessão já finalizada.")

        if not validate_step_id(payload.step_id):
            raise HTTPException(status_code=400, detail="Passo de verificação inválido.")

        steps = record["steps"]
        target = next((step for step in steps if step["id"] == payload.step_id), None)
        if not target:
            raise HTTPException(status_code=400, detail="Passo não encontrado na sessão.")

        if target["status"] == "completed":
            raise HTTPException(status_code=400, detail="Passo já concluído.")

        if payload.step_id != record["current_step"]:
            raise HTTPException(
                status_code=400,
                detail=f"Conclua primeiro o passo atual: {record['current_step']}.",
            )

        target["status"] = payload.status
        if payload.note:
            target["note"] = payload.note.strip()[:500]
            if record.get("guardian_note"):
                record["guardian_note"] = f"{record['guardian_note']}\n{payload.note.strip()[:500]}"
            else:
                record["guardian_note"] = payload.note.strip()[:500]

        if payload.step_id == "record_decision":
            if not payload.final_decision:
                raise HTTPException(
                    status_code=400,
                    detail="Informe final_decision ao registrar a decisão (verified_safe, confirmed_scam, inconclusive, blocked).",
                )
            record["final_decision"] = payload.final_decision

        record["current_step"] = current_step_id(steps)
        record["updated_at"] = _now_iso()

        if payload.step_id == "release_or_block":
            decision = record.get("final_decision")
            if not decision:
                raise HTTPException(
                    status_code=400,
                    detail="Registre a decisão no passo 'record_decision' antes de liberar ou bloquear.",
                )
            record["status"] = _resolve_session_status(decision)
            _sync_admin_case(record["case_id"], record["status"], decision)
        elif all_steps_completed(steps) and record.get("final_decision"):
            record["status"] = _resolve_session_status(record["final_decision"])
            _sync_admin_case(record["case_id"], record["status"], record["final_decision"])
        else:
            _sync_admin_case(record["case_id"], "in_progress", record.get("final_decision"))

        record = proof_trust_store.save_session(record)
        return _to_response(record)
