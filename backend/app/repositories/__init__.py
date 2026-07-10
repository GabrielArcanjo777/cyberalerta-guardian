from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class InboundProcessingStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class CaseProcessingStatus(str, Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class InboundMessageRecord:
    message_id: str
    channel: str
    from_number_hash: str = ""
    message_hash: str = ""
    message_preview: str = ""
    n8n_execution_id: str | None = None
    processing_status: InboundProcessingStatus = InboundProcessingStatus.RECEIVED
    case_id: str | None = None
    last_response_json: dict | None = None
    created_at: float = field(default_factory=time.monotonic)
    updated_at: float = field(default_factory=time.monotonic)


@dataclass
class StateCase:
    case_id: str
    user_name: str = "Pessoa protegida"
    channel: str = "whatsapp"
    status: CaseProcessingStatus = CaseProcessingStatus.OPEN
    risk_score: int = 0
    risk_level: str = "low"
    n8n_action: str = "allow_with_warning"
    ruleset_version: str = "ruleset-local-v1"
    risk_engine_version: str = "v1"
    created_at: float = field(default_factory=time.monotonic)
    updated_at: float = field(default_factory=time.monotonic)


@dataclass
class AuditEventRecord:
    case_id: str | None = None
    request_id: str | None = None
    n8n_execution_id: str | None = None
    event_type: str = ""
    metadata: dict = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.monotonic)


@dataclass
class InMemoryInboundStore:
    _records: dict = field(default_factory=dict)

    def reserve(self, record: InboundMessageRecord) -> tuple[InboundMessageRecord, bool]:
        existing = self._records.get(record.message_id)
        if existing is not None:
            return existing, False
        self._records[record.message_id] = record
        return record, True

    def mark_processed(self, message_id: str, *, case_id: str | None, response_json: dict | None) -> None:
        record = self._records.get(message_id)
        if record is None:
            return
        record.processing_status = InboundProcessingStatus.PROCESSED
        record.case_id = case_id
        record.last_response_json = response_json
        record.updated_at = time.monotonic()


@dataclass
class InMemoryCaseStore:
    _cases: dict = field(default_factory=dict)

    def save(self, case: StateCase) -> None:
        self._cases[case.case_id] = case

    def get(self, case_id: str) -> StateCase | None:
        return self._cases.get(case_id)


@dataclass
class InMemoryAuditStore:
    _events: list = field(default_factory=list)

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        self._events.append(event)
        return event


@dataclass
class OperationalStateRepository:
    inbound_messages: InMemoryInboundStore = field(default_factory=InMemoryInboundStore)
    cases: InMemoryCaseStore = field(default_factory=InMemoryCaseStore)
    audit_events: InMemoryAuditStore = field(default_factory=InMemoryAuditStore)


_repository: OperationalStateRepository | None = None


def get_operational_state_repository() -> OperationalStateRepository:
    global _repository
    if _repository is None:
        _repository = OperationalStateRepository()
    return _repository


def reset_operational_state_repository() -> OperationalStateRepository:
    global _repository
    _repository = OperationalStateRepository()
    return _repository


def stable_hash(value: str | None) -> str:
    if not value:
        return hashlib.sha256(b"empty").hexdigest()[:16]
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def message_preview(message: str, *, store_full_message: bool = False, max_length: int = 80) -> str:
    if store_full_message:
        return message[:200]
    if len(message) <= max_length:
        return message
    return message[:max_length] + "..."
