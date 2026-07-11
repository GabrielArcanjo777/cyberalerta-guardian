from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.llm.models import ScamType


class DeterministicRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DeterministicSignal(BaseModel):
    """A single rule hit, normalized so the Policy Engine never touches the
    legacy rule objects directly."""

    model_config = ConfigDict(extra="forbid")

    code: str
    weight: int = Field(ge=0, le=100)
    excerpt: str = Field(default="", max_length=160)
    rule_origin: str = "risk_rules"
    rule_version: str = "v1"
    objective: bool = True


class DeterministicAssessment(BaseModel):
    """Provider-neutral view of the deterministic rules result.

    Built from the existing RiskAssessment so the Policy Engine depends only on
    this stable shape, not on the rule implementation."""

    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=100)
    risk_level: DeterministicRiskLevel
    scam_types: List[ScamType] = Field(default_factory=list)
    signals: List[DeterministicSignal] = Field(default_factory=list)
    objective_signal_count: int = 0
    has_money_request: bool = False
    has_credential_request: bool = False
    has_suspicious_link: bool = False
    has_urgency: bool = False
    has_impersonation: bool = False
    has_new_number_signal: bool = False


class HybridAction(str, Enum):
    DISCARD = "DISCARD"
    REVIEW = "REVIEW"
    AUTO_ALERT = "AUTO_ALERT"


class HybridDecisionContext(BaseModel):
    """Runtime flags that gate the decision. Defaults are the SAFE posture:
    shadow mode on, LLM disabled, LLM required for any auto-alert."""

    model_config = ConfigDict(extra="forbid")

    llm_enabled: bool = False
    shadow_mode: bool = True
    require_llm_for_auto_alert: bool = True
    policy_version: str = "v1"


class ScoreComponents(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deterministic_score: int
    llm_score: Optional[int] = None
    deterministic_weight: float
    llm_weight: float
    blended: int
    policy_bonus: int = 0
    final_score: int


class HybridDecision(BaseModel):
    """The decision the Policy Engine would take. In shadow mode it is recorded
    but never acts (``shadow_decision=True``)."""

    model_config = ConfigDict(extra="forbid")

    action: HybridAction
    final_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
    policy_version: str = "v1"
    llm_used: bool = False
    llm_available: bool = False
    deterministic_score: int = Field(ge=0, le=100)
    llm_score: Optional[int] = None
    scam_types: List[ScamType] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    requires_human_review: bool = False
    shadow_decision: bool = True
    conflict: bool = False
    score_components: Optional[ScoreComponents] = None
