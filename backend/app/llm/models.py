from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# --- Limits (kept small; the LLM output is untrusted data) ---------------------
MAX_SUMMARY_CHARS = 400
MAX_EXCERPT_CHARS = 160
MAX_EVIDENCE_ITEMS = 8
MAX_LIST_ITEMS = 12


class LLMClassification(str, Enum):
    BENIGN = "BENIGN"
    SUSPICIOUS = "SUSPICIOUS"
    SCAM = "SCAM"


class EvidenceStrength(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ScamType(str, Enum):
    FAMILY_IMPERSONATION = "FAMILY_IMPERSONATION"
    BANK_IMPERSONATION = "BANK_IMPERSONATION"
    ACCOUNT_TAKEOVER = "ACCOUNT_TAKEOVER"
    PIX_FRAUD = "PIX_FRAUD"
    CREDENTIAL_THEFT = "CREDENTIAL_THEFT"
    MALICIOUS_LINK = "MALICIOUS_LINK"
    FAKE_INVOICE_OR_BOLETO = "FAKE_INVOICE_OR_BOLETO"
    DELIVERY_SCAM = "DELIVERY_SCAM"
    PRIZE_OR_LOTTERY = "PRIZE_OR_LOTTERY"
    FAKE_JOB = "FAKE_JOB"
    INVESTMENT_SCAM = "INVESTMENT_SCAM"
    ROMANCE_OR_EMOTIONAL_MANIPULATION = "ROMANCE_OR_EMOTIONAL_MANIPULATION"
    TECH_SUPPORT_SCAM = "TECH_SUPPORT_SCAM"
    EXTORTION = "EXTORTION"
    UNKNOWN = "UNKNOWN"


class ObjectiveEvidence(BaseModel):
    """One observable signal the model found in the message.

    ``extra="forbid"`` so a hostile/hallucinated payload with extra keys is
    rejected during validation instead of silently accepted.
    """

    model_config = ConfigDict(extra="forbid")

    signal: str = Field(max_length=64)
    excerpt: str = Field(default="", max_length=MAX_EXCERPT_CHARS)
    strength: EvidenceStrength = EvidenceStrength.LOW


class LLMScamAnalysisResult(BaseModel):
    """Structured, validated output of the scam classifier.

    This is untrusted model output: it never carries send instructions, and any
    field the model might try to smuggle in (tools, actions, system overrides) is
    rejected by ``extra="forbid"``.
    """

    model_config = ConfigDict(extra="forbid")

    classification: LLMClassification
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: int = Field(ge=0, le=100)
    scam_types: List[ScamType] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    requested_actions: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    impersonated_entities: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    emotional_signals: List[str] = Field(default_factory=list, max_length=MAX_LIST_ITEMS)
    objective_evidence: List[ObjectiveEvidence] = Field(
        default_factory=list, max_length=MAX_EVIDENCE_ITEMS
    )
    requires_context: bool = False
    requires_human_review: bool = False
    summary: str = Field(default="", max_length=MAX_SUMMARY_CHARS)


class LLMScamAnalysisRequest(BaseModel):
    """Minimal, sanitized input handed to the provider.

    Only what the classifier needs — never secrets, never full PII. The message
    text is treated as untrusted data and delimited by the prompt layer.
    """

    model_config = ConfigDict(extra="forbid")

    normalized_text: str
    deterministic_score: int = Field(ge=0, le=100)
    deterministic_signals: List[str] = Field(default_factory=list)
    recent_context: List[str] = Field(default_factory=list)
    sender_is_new_number: Optional[bool] = None
    sender_is_unknown: Optional[bool] = None
    language: str = "pt"


class LLMAnalysisStatus(str, Enum):
    """Why the LLM step produced (or failed to produce) a result."""

    COMPLETED = "completed"
    DISABLED = "disabled"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    INVALID_OUTPUT = "invalid_output"


class LLMScamAnalysisOutcome(BaseModel):
    """Wraps the result with availability + audit metadata.

    ``result`` is None whenever ``status`` is not COMPLETED — callers must treat
    that as "LLM unavailable" and fall back to the safe path.
    """

    model_config = ConfigDict(extra="forbid")

    status: LLMAnalysisStatus
    result: Optional[LLMScamAnalysisResult] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    latency_ms: Optional[int] = None
    error_kind: Optional[str] = None

    @property
    def available(self) -> bool:
        return self.status == LLMAnalysisStatus.COMPLETED and self.result is not None
