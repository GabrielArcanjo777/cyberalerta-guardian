from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_state_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class CaseProcessingStatus(str, Enum):
    OPEN = "open"
    REVIEWING = "reviewing"
    CONFIRMED_SCAM = "confirmed_scam"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class InboundProcessingStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class StateCase(BaseModel):
    case_id: str = Field(default_factory=lambda: new_state_id("state-case"))
    user_name: str = Field(min_length=1, max_length=160)
    channel: str = Field(min_length=1, max_length=80)
    status: CaseProcessingStatus = CaseProcessingStatus.OPEN
    risk_score: Optional[int] = Field(default=None, ge=0, le=100)
    risk_level: Optional[str] = Field(default=None, max_length=40)
    n8n_action: Optional[str] = Field(default=None, max_length=120)
    ruleset_version: Optional[str] = Field(default=None, max_length=120)
    risk_engine_version: Optional[str] = Field(default=None, max_length=120)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class InboundMessageRecord(BaseModel):
    message_id: str = Field(min_length=1, max_length=180)
    case_id: Optional[str] = Field(default=None, max_length=180)
    channel: str = Field(min_length=1, max_length=80)
    from_number_hash: str = Field(min_length=1, max_length=128)
    message_hash: str = Field(min_length=1, max_length=128)
    message_preview: str = Field(default="", max_length=160)
    n8n_execution_id: Optional[str] = Field(default=None, max_length=180)
    processed_at: Optional[datetime] = None
    processing_status: InboundProcessingStatus = InboundProcessingStatus.RECEIVED
    last_response_json: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class AuditEventRecord(BaseModel):
    event_id: str = Field(default_factory=lambda: new_state_id("audit-event"))
    case_id: Optional[str] = Field(default=None, max_length=180)
    request_id: Optional[str] = Field(default=None, max_length=180)
    n8n_execution_id: Optional[str] = Field(default=None, max_length=180)
    event_type: str = Field(min_length=1, max_length=160)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class CaseStateRepository(Protocol):
    def save(self, case: StateCase) -> StateCase: ...
    def get(self, case_id: str) -> Optional[StateCase]: ...
    def list_all(self) -> List[StateCase]: ...


class InboundMessageStateRepository(Protocol):
    def reserve(self, record: InboundMessageRecord) -> tuple[InboundMessageRecord, bool]: ...
    def save(self, record: InboundMessageRecord) -> InboundMessageRecord: ...
    def get(self, message_id: str) -> Optional[InboundMessageRecord]: ...
    def mark_processed(
        self,
        message_id: str,
        *,
        case_id: str | None,
        response_json: Dict[str, Any],
    ) -> InboundMessageRecord: ...


class AuditEventStateRepository(Protocol):
    def append(self, event: AuditEventRecord) -> AuditEventRecord: ...
    def list_all(self) -> List[AuditEventRecord]: ...
    def list_by_case(self, case_id: str) -> List[AuditEventRecord]: ...


class OperationalStateRepository(Protocol):
    cases: CaseStateRepository
    inbound_messages: InboundMessageStateRepository
    audit_events: AuditEventStateRepository
