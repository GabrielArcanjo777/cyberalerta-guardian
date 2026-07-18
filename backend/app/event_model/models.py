from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class BotEventType(str, Enum):
    MESSAGE_RECEIVED = "MessageReceived"
    SUSPICIOUS_MESSAGE_RECEIVED = "SuspiciousMessageReceived"
    RISK_ASSESSMENT_CREATED = "RiskAssessmentCreated"
    CASE_CREATED = "CaseCreated"
    SAFE_REPLY_SENT = "SafeReplySent"
    RESPONSIBLE_ALERT_QUEUED = "ResponsibleAlertQueued"
    RESPONSIBLE_NOTIFIED = "ResponsibleNotified"
    CASE_RESOLVED = "CaseResolved"
    FALSE_POSITIVE_MARKED = "FalsePositiveMarked"
    PATTERN_CANDIDATE_DETECTED = "PatternCandidateDetected"
    TRIAGE_DECISION_CREATED = "TriageDecisionCreated"
    SAFE_REPLY_GENERATED = "SafeReplyGenerated"
    RESPONSIBLE_ALERT_GENERATED = "ResponsibleAlertGenerated"
    CASE_SUMMARY_GENERATED = "CaseSummaryGenerated"
    PATTERN_REVIEW_GENERATED = "PatternReviewGenerated"
    AGENT_FALLBACK_USED = "AgentFallbackUsed"
    PROTECTED_PERSON_REPLIED = "ProtectedPersonReplied"
    GUARDIAN_ALERT_TRIGGERED = "GuardianAlertTriggered"
    GUARDIAN_NOTIFIED = "GuardianNotified"
    GUARDIAN_FEEDBACK_RECEIVED = "GuardianFeedbackReceived"
    PATTERN_DETECTED = "PatternDetected"
    CONSENT_UPDATED = "ConsentUpdated"
    CONSENT_ACCEPTED = "ConsentAccepted"
    CONSENT_REVOKED = "ConsentRevoked"
    BOT_ACTIVATED = "BotActivated"
    BOT_DEACTIVATED = "BotDeactivated"
    CONSENT_SCOPE_CHANGED = "ConsentScopeChanged"
    DELIVERY_STATUS_UPDATED = "DeliveryStatusUpdated"
    # --- Hybrid detection pipeline ---
    DETERMINISTIC_ASSESSMENT_CREATED = "DeterministicAssessmentCreated"
    LLM_ANALYSIS_REQUESTED = "LLMAnalysisRequested"
    LLM_ANALYSIS_COMPLETED = "LLMAnalysisCompleted"
    LLM_ANALYSIS_FAILED = "LLMAnalysisFailed"
    HYBRID_DECISION_CREATED = "HybridDecisionCreated"
    HYBRID_SHADOW_DECISION_CREATED = "HybridShadowDecisionCreated"
    REVIEW_QUEUED = "ReviewQueued"
    AUTO_ALERT_AUTHORIZED = "AutoAlertAuthorized"
    AUTO_ALERT_BLOCKED = "AutoAlertBlocked"
    PROMPT_INJECTION_DETECTED = "PromptInjectionDetected"
    POLICY_FALLBACK_USED = "PolicyFallbackUsed"


class CaseStatus(str, Enum):
    NEW = "new"
    UNDER_REVIEW = "under_review"
    PAUSED = "paused"
    CONFIRMED_SCAM = "confirmed_scam"
    FALSE_ALARM = "false_alarm"
    RESOLVED = "resolved"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class EntityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class MessageStatus(str, Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class ChannelConnectionStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"
    ERROR = "error"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Organization(BaseModel):
    """Isolation boundary for a family/tenant (Plano Mestre v1.1, Secao 5.3).

    Optional and unset (None) on ProtectedPerson/Guardian/Case for backward
    compatibility with the single-tenant demo data that predates this model;
    the devices/pairing module (Sprint 2) is what starts requiring it.
    """

    organization_id: str = Field(default_factory=lambda: new_id("org"))
    name: str = Field(min_length=1, max_length=160)
    status: EntityStatus = EntityStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: new_id("user"))
    alias: str = Field(min_length=1, max_length=120)
    email: Optional[str] = Field(default=None, max_length=240)
    status: EntityStatus = EntityStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ProtectedPerson(BaseModel):
    protected_person_id: str = Field(default_factory=lambda: new_id("protected"))
    organization_id: Optional[str] = None
    alias: str = Field(min_length=1, max_length=120)
    user_id: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Guardian(BaseModel):
    guardian_id: str = Field(default_factory=lambda: new_id("guardian"))
    organization_id: Optional[str] = None
    alias: str = Field(min_length=1, max_length=120)
    user_id: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: new_id("message"))
    protected_person_id: str
    guardian_id: Optional[str] = None
    direction: MessageDirection = MessageDirection.INBOUND
    channel: str = Field(default="simulated", min_length=1, max_length=80)
    body: str = Field(min_length=1, max_length=8000)
    simulated: bool = True
    provider_message_id: Optional[str] = None
    status: MessageStatus = MessageStatus.RECEIVED
    body_hash: Optional[str] = Field(default=None, max_length=64)
    body_preview: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class RiskAssessment(BaseModel):
    risk_assessment_id: str = Field(default_factory=lambda: new_id("risk"))
    message_id: str
    score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    signals: List[str] = Field(default_factory=list)
    explanation: List[str] = Field(default_factory=list)
    case_threshold_reached: bool
    created_at: datetime = Field(default_factory=utc_now)


class Case(BaseModel):
    case_id: str = Field(default_factory=lambda: new_id("case"))
    organization_id: Optional[str] = None
    protected_person_id: str
    guardian_id: Optional[str] = None
    channel_connection_id: Optional[str] = None
    source_message_id: str
    risk_assessment_id: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    status: CaseStatus = CaseStatus.NEW
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ChannelConnection(BaseModel):
    channel_connection_id: str = Field(default_factory=lambda: new_id("channel"))
    provider: str = Field(min_length=1, max_length=80)
    channel: str = Field(default="whatsapp", min_length=1, max_length=80)
    protected_person_id: Optional[str] = None
    guardian_id: Optional[str] = None
    external_contact_id: Optional[str] = Field(default=None, max_length=240)
    address_label: Optional[str] = Field(default=None, max_length=240)
    status: ChannelConnectionStatus = ChannelConnectionStatus.PENDING
    simulated: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BotEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: new_id("event"))
    event_type: BotEventType
    aggregate_type: str = Field(min_length=1, max_length=80)
    aggregate_id: str = Field(min_length=1, max_length=160)
    source: str = Field(default="event_model", min_length=1, max_length=120)
    actor: Optional[str] = Field(default=None, max_length=160)
    case_id: Optional[str] = None
    protected_person_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=utc_now)


class AuditLog(BaseModel):
    audit_log_id: str = Field(default_factory=lambda: new_id("audit"))
    event_id: Optional[str] = None
    actor: Optional[str] = Field(default=None, max_length=160)
    action: str = Field(min_length=1, max_length=160)
    target_type: str = Field(min_length=1, max_length=80)
    target_id: str = Field(min_length=1, max_length=160)
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: EntityStatus = EntityStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)


class SuspiciousMessageProcessingResult(BaseModel):
    message: Message
    risk_assessment: RiskAssessment
    case: Optional[Case] = None
    emitted_event_ids: List[str] = Field(default_factory=list)
