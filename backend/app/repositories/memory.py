from __future__ import annotations

from threading import RLock
from typing import Dict, List, Optional

from app.repositories.base import (
    AuditEventRecord,
    InboundMessageRecord,
    InboundProcessingStatus,
    StateCase,
    utc_now,
)


class InMemoryCaseStateRepository:
    def __init__(self) -> None:
        self._cases: Dict[str, StateCase] = {}
        self._lock = RLock()

    def save(self, case: StateCase) -> StateCase:
        stored = case.model_copy(update={"updated_at": utc_now()}, deep=True)
        with self._lock:
            existing = self._cases.get(stored.case_id)
            if existing:
                stored = stored.model_copy(update={"created_at": existing.created_at})
            self._cases[stored.case_id] = stored
        return stored.model_copy(deep=True)

    def get(self, case_id: str) -> Optional[StateCase]:
        with self._lock:
            case = self._cases.get(case_id)
        return case.model_copy(deep=True) if case else None

    def list_all(self) -> List[StateCase]:
        with self._lock:
            cases = list(self._cases.values())
        return [case.model_copy(deep=True) for case in sorted(cases, key=lambda item: item.updated_at, reverse=True)]


class InMemoryInboundMessageStateRepository:
    def __init__(self) -> None:
        self._messages: Dict[str, InboundMessageRecord] = {}
        self._lock = RLock()

    def reserve(self, record: InboundMessageRecord) -> tuple[InboundMessageRecord, bool]:
        stored = record.model_copy(
            update={
                "processing_status": InboundProcessingStatus.PROCESSING,
                "updated_at": utc_now(),
            },
            deep=True,
        )
        with self._lock:
            existing = self._messages.get(stored.message_id)
            if existing:
                return existing.model_copy(deep=True), False
            self._messages[stored.message_id] = stored
        return stored.model_copy(deep=True), True

    def save(self, record: InboundMessageRecord) -> InboundMessageRecord:
        stored = record.model_copy(update={"updated_at": utc_now()}, deep=True)
        with self._lock:
            existing = self._messages.get(stored.message_id)
            if existing:
                stored = stored.model_copy(update={"created_at": existing.created_at})
            self._messages[stored.message_id] = stored
        return stored.model_copy(deep=True)

    def get(self, message_id: str) -> Optional[InboundMessageRecord]:
        with self._lock:
            record = self._messages.get(message_id)
        return record.model_copy(deep=True) if record else None

    def mark_processed(
        self,
        message_id: str,
        *,
        case_id: str | None,
        response_json: dict,
    ) -> InboundMessageRecord:
        with self._lock:
            existing = self._messages.get(message_id)
            if not existing:
                raise LookupError(f"Inbound message not found: {message_id}")
            updated = existing.model_copy(
                update={
                    "case_id": case_id,
                    "processed_at": utc_now(),
                    "processing_status": InboundProcessingStatus.PROCESSED,
                    "last_response_json": response_json,
                    "updated_at": utc_now(),
                },
                deep=True,
            )
            self._messages[message_id] = updated
        return updated.model_copy(deep=True)


class InMemoryAuditEventStateRepository:
    def __init__(self) -> None:
        self._events: List[AuditEventRecord] = []
        self._event_ids: set[str] = set()
        self._lock = RLock()

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        stored = event.model_copy(deep=True)
        with self._lock:
            if stored.event_id in self._event_ids:
                raise ValueError(f"Audit event already exists: {stored.event_id}")
            self._events.append(stored)
            self._event_ids.add(stored.event_id)
        return stored.model_copy(deep=True)

    def list_all(self) -> List[AuditEventRecord]:
        with self._lock:
            events = list(self._events)
        return [event.model_copy(deep=True) for event in events]

    def list_by_case(self, case_id: str) -> List[AuditEventRecord]:
        return [event for event in self.list_all() if event.case_id == case_id]


class InMemoryOperationalStateRepository:
    def __init__(self) -> None:
        self.cases = InMemoryCaseStateRepository()
        self.inbound_messages = InMemoryInboundMessageStateRepository()
        self.audit_events = InMemoryAuditEventStateRepository()
