from typing import List, Literal, Optional

from pydantic import BaseModel, Field

EscalationStatus = Literal[
    "simulated_notified",
    "review_suggested",
    "not_escalated",
]


class TrustedCircleStatusResponse(BaseModel):
    service: str
    mode: str
    real_notifications_enabled: bool
    escalation_count: int
    demo_note: str


class TrustedCircleEscalateRequest(BaseModel):
    case_id: str
    risk_level: str
    protected_person_alias: str
    trusted_contacts: List[str] = Field(default_factory=list)
    reason: str = Field(min_length=3, max_length=500)


class TrustedCircleEscalateResponse(BaseModel):
    escalation_id: str
    status: EscalationStatus
    message_to_guardian: str
    trusted_contacts: List[str]
    proof_of_trust_recommended: bool
    sent_real_notification: bool
    demo_note: str
    case_id: Optional[str] = None
    risk_level: Optional[str] = None
    escalation_recommended: bool = False


class TrustedCircleEscalationRecord(BaseModel):
    escalation_id: str
    case_id: str
    risk_level: str
    protected_person_alias: str
    trusted_contacts: List[str]
    reason: str
    status: EscalationStatus
    message_to_guardian: str
    proof_of_trust_recommended: bool
    sent_real_notification: bool
    created_at: str
