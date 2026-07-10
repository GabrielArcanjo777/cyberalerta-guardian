from typing import List, Literal, Optional

from pydantic import BaseModel, Field

CaseStatus = Literal[
    "open",
    "reviewing",
    "verified_safe",
    "confirmed_scam",
    "resolved",
    "recovery_needed",
]

VALID_CASE_STATUSES = {
    "open",
    "reviewing",
    "verified_safe",
    "confirmed_scam",
    "resolved",
    "recovery_needed",
}


class AdminCaseTraceStep(BaseModel):
    step: str
    detail: str


class AdminCase(BaseModel):
    case_id: str
    protected_person_alias: str
    guardian_alias: str
    source_channel: str
    received_content_summary: str
    risk_score: int
    risk_level: str
    scam_category: str
    detected_signals: List[str]
    agent_decision: str
    agent_decision_trace: List[AdminCaseTraceStep]
    trust_lock_status: str
    trusted_circle_status: str
    proof_of_trust_status: str
    recovery_status: str
    recommended_action: str
    protected_person_short_reply: Optional[str] = None
    status: CaseStatus
    created_at: str
    updated_at: str


class GuardianConsoleStatusResponse(BaseModel):
    service: str
    mode: str
    storage: str
    case_count: int
    auth_enabled: bool
    notifications_enabled: bool
    demo_note: str


class AdminCaseListResponse(BaseModel):
    cases: List[AdminCase]
    total: int


class AdminCaseStatusUpdateRequest(BaseModel):
    status: CaseStatus


class AdminCaseFromChannelRequest(BaseModel):
    channel_case_id: Optional[str] = None
    protected_person_alias: str
    guardian_alias: Optional[str] = "Gabriel"
    source_channel: str = "whatsapp_mock"
    received_content_summary: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    scam_category: str
    detected_signals: List[str] = Field(default_factory=list)
    agent_decision: str
    agent_decision_trace: List[AdminCaseTraceStep] = Field(default_factory=list)
    trust_lock_status: str = "not_needed"
    trusted_circle_status: str = "pending"
    proof_of_trust_status: str = "not_started"
    recovery_status: str = "not_needed"
    recommended_action: str
    protected_person_short_reply: Optional[str] = None
    status: CaseStatus = "open"
