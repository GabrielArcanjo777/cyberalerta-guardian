from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_pattern_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class PatternLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PatternSignal(BaseModel):
    signal: str
    label: str
    weight: int = Field(ge=0, le=100)
    matched_terms: List[str] = Field(default_factory=list)
    explanation: str


class NormalizedThreatText(BaseModel):
    original_length: int = Field(ge=0)
    normalized_text: str
    normalized_text_sha1: str
    text_fingerprint: str
    tokens: List[str] = Field(default_factory=list)
    language: str = "pt"
    created_at: datetime = Field(default_factory=utc_now)


class RiskExplanation(BaseModel):
    score: int = Field(ge=0, le=100)
    level: PatternLevel
    summary: str
    reasons: List[str] = Field(default_factory=list)
    recommendation: str
    thresholds: Dict[str, int] = Field(default_factory=dict)


class PatternDetectionResult(BaseModel):
    detection_id: str = Field(default_factory=lambda: new_pattern_id("pattern-detection"))
    message_id: Optional[str] = None
    case_id: Optional[str] = None
    candidate_id: Optional[str] = None
    threat_type: str
    threat_type_label: str
    score: int = Field(ge=0, le=100)
    level: PatternLevel
    signals: List[PatternSignal] = Field(default_factory=list)
    signal_names: List[str] = Field(default_factory=list)
    explanation: str
    normalized_text: str
    normalized_text_sha1: str
    normalized_threat_text: NormalizedThreatText
    risk_explanation: RiskExplanation
    recurrence: Dict[str, int] = Field(default_factory=dict)
    similar_message_ids: List[str] = Field(default_factory=list)
    cluster_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class PatternCluster(BaseModel):
    cluster_id: str
    cluster_type: str
    label: str
    signal_names: List[str] = Field(default_factory=list)
    message_ids: List[str] = Field(default_factory=list)
    case_ids: List[str] = Field(default_factory=list)
    protected_person_ids: List[str] = Field(default_factory=list)
    protected_person_aliases: List[str] = Field(default_factory=list)
    sender_addresses: List[str] = Field(default_factory=list)
    occurrence_count: int = 0
    average_score: float = 0
    explanation: str
    first_seen_at: datetime = Field(default_factory=utc_now)
    last_seen_at: datetime = Field(default_factory=utc_now)


class PatternCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: new_pattern_id("pattern-candidate"))
    message_id: str
    case_id: Optional[str] = None
    protected_person_id: str
    protected_person_alias: Optional[str] = None
    sender_address: Optional[str] = None
    normalized_text: str
    normalized_text_sha1: str
    text_fingerprint: str
    normalized_threat_text: Optional[NormalizedThreatText] = None
    threat_type: str = "unknown"
    threat_type_label: str = "Padrao nao classificado"
    score: int = Field(ge=0, le=100)
    level: PatternLevel
    signal_names: List[str] = Field(default_factory=list)
    risk_explanation: Optional[RiskExplanation] = None
    cluster_ids: List[str] = Field(default_factory=list)
    expected_label: Optional[str] = None
    feedback_action: Optional[str] = None
    feedback_note: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PatternFeedback(BaseModel):
    feedback_id: str = Field(default_factory=lambda: new_pattern_id("pattern-feedback"))
    case_id: str
    candidate_ids: List[str] = Field(default_factory=list)
    feedback_action: str
    expected_label: str
    confirmed_scam: bool = False
    false_positive: bool = False
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


PatternFeedbackRecord = PatternFeedback
