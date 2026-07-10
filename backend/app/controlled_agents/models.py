from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.event_model.models import utc_now


class ControlledAgentName(str, Enum):
    TRIAGE = "TriageAgent"
    RESPONSIBLE_ALERT = "ResponsibleAlertAgent"
    CASE_SUMMARY = "CaseSummaryAgent"
    PATTERN_REVIEW = "PatternReviewAgent"


class AgentGuardrailResult(BaseModel):
    passed: bool = True
    applied: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    fallback_used: bool = False


class ControlledAgentDecision(BaseModel):
    agent: ControlledAgentName
    decision_id: str
    case_id: Optional[str] = None
    message_id: Optional[str] = None
    summary: str
    recommended_action: str
    guardrails: AgentGuardrailResult
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class TriageDecision(ControlledAgentDecision):
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    signals: List[str] = Field(default_factory=list)
    pattern_signals: List[str] = Field(default_factory=list)
    should_create_case: bool
    should_notify_responsible: bool


class ResponsibleAlertDecision(ControlledAgentDecision):
    body: str
    protected_person_alias: str
    message_summary: str


class CaseSummaryDecision(ControlledAgentDecision):
    protected_person_alias: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    evidence: List[str] = Field(default_factory=list)
    report_summary: str


class PatternReviewDecision(ControlledAgentDecision):
    pattern_score: int = Field(ge=0, le=100)
    pattern_level: str
    threat_type: str
    threat_type_label: str
    recurrence: Dict[str, int] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
