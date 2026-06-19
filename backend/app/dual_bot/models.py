from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.pattern_intelligence import PatternDetectionResult


class GuardianFeedbackAction(str, Enum):
    CONFIRM_SCAM = "confirm_scam"
    FALSE_ALARM = "false_alarm"
    NEEDS_REVIEW = "needs_review"
    MARK_RESOLVED = "mark_resolved"


class DualBotInboundRequest(BaseModel):
    provider_message_id: Optional[str] = Field(default=None, alias="providerMessageId", max_length=180)
    from_address: str = Field(default="+5511999990001", alias="from", min_length=1, max_length=180)
    to_address: str = Field(default="+5511999990000", alias="to", min_length=1, max_length=180)
    body: str = Field(min_length=1, max_length=8000)
    timestamp: Optional[datetime] = None
    protected_person_alias: str = Field(default="Dona Lucia", max_length=120)
    guardian_alias: str = Field(default="Gabriel", max_length=120)
    guardian_address: str = Field(default="+5511888880001", max_length=180)
    language: str = Field(default="pt", max_length=8)
    profile_name: Optional[str] = Field(default=None, alias="profileName", max_length=180)
    media: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class DualBotOutboundMessage(BaseModel):
    provider_message_id: str
    to_address: str
    body: str
    kind: str
    status: str
    simulated: bool
    retryable: bool
    related_case_id: Optional[str] = None


class DualBotFlowResponse(BaseModel):
    provider: str
    duplicate: bool
    provider_message_id: str
    message_id: Optional[str]
    risk_assessment_id: Optional[str]
    risk_score: Optional[int]
    risk_level: Optional[str]
    risk_signals: List[str] = Field(default_factory=list)
    case_id: Optional[str]
    case_created: bool
    protected_reply: Optional[DualBotOutboundMessage]
    guardian_alert: Optional[DualBotOutboundMessage]
    pattern_detection: Optional[PatternDetectionResult] = None
    events: List[str] = Field(default_factory=list)


class DualBotProviderStatusResponse(BaseModel):
    service: str = "dual-bot-flow"
    active_provider: str
    adapter_first: bool = True
    mock_supported: bool = True
    evolution_demo_supported: bool = True
    production: bool = False
    demo_notice: str = "Evolution API is demo/development only, not official WhatsApp production."


class DualBotEventSummary(BaseModel):
    event_id: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    occurred_at: datetime


class DualBotCaseContextResponse(BaseModel):
    case_id: str
    status: str
    protected_person_alias: str
    guardian_alias: Optional[str]
    risk_score: int
    risk_level: str
    risk_signals: List[str] = Field(default_factory=list)
    message_summary: str
    source_message: str
    history: List[DualBotEventSummary] = Field(default_factory=list)


class GuardianFeedbackRequest(BaseModel):
    action: GuardianFeedbackAction
    guardian_alias: str = Field(default="Gabriel", max_length=120)
    note: Optional[str] = Field(default=None, max_length=1000)


class GuardianFeedbackResponse(BaseModel):
    case_id: str
    action: GuardianFeedbackAction
    previous_status: str
    new_status: str
    event_id: str
    audit_event: str
