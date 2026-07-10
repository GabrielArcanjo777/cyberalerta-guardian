from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GuardianConsoleBotState(BaseModel):
    name: str
    active: bool
    provider: str
    mode: str
    last_event: Optional[str] = None


class GuardianConsoleActivationState(BaseModel):
    protected_bot: GuardianConsoleBotState
    responsible_bot: GuardianConsoleBotState
    channel_provider: str
    backend_state: str
    simulated: bool


class GuardianConsoleTimelineEvent(BaseModel):
    event_id: str
    event_type: str
    label: str
    description: str
    aggregate_type: str
    aggregate_id: str
    occurred_at: datetime
    status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GuardianConsoleDeliveryView(BaseModel):
    guardian_alert_status: Optional[str] = None
    guardian_notified: bool = False
    latest_provider_message_id: Optional[str] = None


class GuardianConsoleOutboundView(BaseModel):
    provider_message_id: Optional[str]
    kind: str
    to_label: str
    body: str
    status: Optional[str]
    simulated: bool


class GuardianConsolePatternView(BaseModel):
    score: int = Field(ge=0, le=100)
    level: str
    threat_type: str
    threat_type_label: str
    explanation: str
    reasons: List[str] = Field(default_factory=list)
    recommendation: str
    signals: List[str] = Field(default_factory=list)
    cluster_ids: List[str] = Field(default_factory=list)
    recurrence: Dict[str, int] = Field(default_factory=dict)
    similar_message_ids: List[str] = Field(default_factory=list)
    normalized_text_sha1: str
    text_fingerprint: str
    candidate_id: Optional[str] = None
    feedback_label: Optional[str] = None


class GuardianConsoleProtectedPersonView(BaseModel):
    protected_person_id: str
    alias: str
    status: str
    created_at: datetime
    updated_at: datetime


class GuardianConsoleResponsibleContactView(BaseModel):
    guardian_id: Optional[str]
    alias: Optional[str]
    status: Optional[str]
    notified: bool
    last_delivery_status: Optional[str] = None
    address_label: Optional[str] = None


class GuardianConsoleCaseStateView(BaseModel):
    case_id: str
    status: str
    source_message_id: str
    risk_assessment_id: str
    open: bool
    created_at: datetime
    updated_at: datetime


class GuardianConsoleMessageView(BaseModel):
    message_id: str
    provider_message_id: Optional[str]
    direction: str
    channel: str
    body: str
    summary: str
    status: str
    simulated: bool
    created_at: datetime


class GuardianConsoleRiskAssessmentView(BaseModel):
    risk_assessment_id: str
    score: int = Field(ge=0, le=100)
    risk_level: str
    signals: List[str] = Field(default_factory=list)
    explanation: List[str] = Field(default_factory=list)
    case_threshold_reached: bool
    threshold_label: str
    created_at: datetime


class GuardianConsoleChannelStatusView(BaseModel):
    provider: str
    mode: str
    simulated: bool
    backend_state: str
    protected_bot_active: bool
    responsible_bot_active: bool
    guardian_alert_status: Optional[str] = None
    guardian_notified: bool = False
    latest_provider_message_id: Optional[str] = None
    environment_label: str


class GuardianConsoleFeedbackView(BaseModel):
    available_actions: List[str] = Field(default_factory=list)
    latest_action: Optional[str] = None
    latest_actor: Optional[str] = None
    latest_note: Optional[str] = None
    latest_event_id: Optional[str] = None
    latest_event_at: Optional[datetime] = None
    guardian_confirmed: bool = False
    false_positive: bool = False
    resolved: bool = False


class GuardianConsoleAuditLogView(BaseModel):
    audit_log_id: str
    event_id: Optional[str] = None
    actor: Optional[str] = None
    action: str
    target_type: str
    target_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class GuardianConsoleAgentDecisionView(BaseModel):
    event_id: str
    agent: str
    summary: str
    recommended_action: str
    fallback_used: bool = False
    guardrails: List[str] = Field(default_factory=list)
    occurred_at: datetime


class GuardianConsoleConsentView(BaseModel):
    consent_id: str
    status: str
    bot_active: bool
    scopes: List[str] = Field(default_factory=list)
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    retention_message_body_days: int
    retention_event_audit_days: int
    delete_after_revocation_days: int
    latest_event: Optional[str] = None
    limitation_notice: str


class GuardianConsoleRealCaseSummary(BaseModel):
    case_id: str
    status: str
    protected_person_alias: str
    guardian_alias: Optional[str]
    source_channel: str
    risk_score: int
    risk_level: str
    risk_signals: List[str] = Field(default_factory=list)
    pattern_score: Optional[int] = None
    pattern_level: Optional[str] = None
    message_summary: str
    recommended_action: str
    alert_delivered: bool
    guardian_confirmed: bool
    false_positive: bool
    resolved: bool
    created_at: datetime
    updated_at: datetime


class GuardianConsoleRealCaseDetail(GuardianConsoleRealCaseSummary):
    source_message: str
    activation: GuardianConsoleActivationState
    delivery: GuardianConsoleDeliveryView
    guardian_alert: GuardianConsoleOutboundView
    protected_person: GuardianConsoleProtectedPersonView
    responsible_contact: GuardianConsoleResponsibleContactView
    case: GuardianConsoleCaseStateView
    message: GuardianConsoleMessageView
    risk_assessment: GuardianConsoleRiskAssessmentView
    channel_status: GuardianConsoleChannelStatusView
    feedback: GuardianConsoleFeedbackView
    audit_log: List[GuardianConsoleAuditLogView] = Field(default_factory=list)
    bot_events: List[GuardianConsoleTimelineEvent] = Field(default_factory=list)
    agent_decisions: List[GuardianConsoleAgentDecisionView] = Field(default_factory=list)
    consent: GuardianConsoleConsentView
    environment_label: str
    next_step: str
    pattern: Optional[GuardianConsolePatternView] = None
    timeline: List[GuardianConsoleTimelineEvent] = Field(default_factory=list)
    feedback_actions: List[str] = Field(default_factory=list)


class GuardianConsoleRealStatusResponse(BaseModel):
    service: str
    mode: str
    storage: str
    channel_provider: str
    case_count: int
    open_case_count: int
    protected_people_count: int
    guardians_count: int
    delivery_status_available: bool
    activation: GuardianConsoleActivationState
    consent: GuardianConsoleConsentView
    demo_note: str


class GuardianConsoleRealCaseListResponse(BaseModel):
    cases: List[GuardianConsoleRealCaseSummary]
    total: int
