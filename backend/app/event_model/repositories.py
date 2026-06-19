from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Dict, Generic, List, Optional, Protocol, TypeVar

from pydantic import BaseModel

from app.event_model.models import (
    AuditLog,
    BotEvent,
    BotEventType,
    Case,
    ChannelConnection,
    Guardian,
    Message,
    ProtectedPerson,
    RiskAssessment,
    User,
)


class UserRepository(Protocol):
    def save(self, entity: User) -> User: ...
    def get(self, entity_id: str) -> Optional[User]: ...
    def list_all(self) -> List[User]: ...


class ProtectedPersonRepository(Protocol):
    def save(self, entity: ProtectedPerson) -> ProtectedPerson: ...
    def get(self, entity_id: str) -> Optional[ProtectedPerson]: ...
    def list_all(self) -> List[ProtectedPerson]: ...


class GuardianRepository(Protocol):
    def save(self, entity: Guardian) -> Guardian: ...
    def get(self, entity_id: str) -> Optional[Guardian]: ...
    def list_all(self) -> List[Guardian]: ...


class MessageRepository(Protocol):
    def save(self, entity: Message) -> Message: ...
    def get(self, entity_id: str) -> Optional[Message]: ...
    def list_all(self) -> List[Message]: ...


class RiskAssessmentRepository(Protocol):
    def save(self, entity: RiskAssessment) -> RiskAssessment: ...
    def get(self, entity_id: str) -> Optional[RiskAssessment]: ...
    def list_all(self) -> List[RiskAssessment]: ...


class CaseRepository(Protocol):
    def save(self, entity: Case) -> Case: ...
    def get(self, entity_id: str) -> Optional[Case]: ...
    def list_all(self) -> List[Case]: ...


class ChannelConnectionRepository(Protocol):
    def save(self, entity: ChannelConnection) -> ChannelConnection: ...
    def get(self, entity_id: str) -> Optional[ChannelConnection]: ...
    def list_all(self) -> List[ChannelConnection]: ...


class EventRepository(Protocol):
    def append(self, event: BotEvent) -> BotEvent: ...
    def list_all(self) -> List[BotEvent]: ...
    def list_by_aggregate(self, aggregate_id: str) -> List[BotEvent]: ...
    def list_by_type(self, event_type: BotEventType) -> List[BotEvent]: ...


class AuditLogRepository(Protocol):
    def save(self, entity: AuditLog) -> AuditLog: ...
    def get(self, entity_id: str) -> Optional[AuditLog]: ...
    def list_all(self) -> List[AuditLog]: ...


EntityT = TypeVar("EntityT", bound=BaseModel)


class _InMemoryEntityRepository(Generic[EntityT]):
    def __init__(self, id_attribute: str) -> None:
        self._id_attribute = id_attribute
        self._items: Dict[str, EntityT] = {}
        self._lock = RLock()

    def save(self, entity: EntityT) -> EntityT:
        entity_id = str(getattr(entity, self._id_attribute))
        stored = entity.model_copy(deep=True)
        with self._lock:
            self._items[entity_id] = stored
        return stored.model_copy(deep=True)

    def get(self, entity_id: str) -> Optional[EntityT]:
        with self._lock:
            entity = self._items.get(entity_id)
        return entity.model_copy(deep=True) if entity else None

    def list_all(self) -> List[EntityT]:
        with self._lock:
            entities = list(self._items.values())
        return [entity.model_copy(deep=True) for entity in entities]


class InMemoryProtectedPersonRepository(_InMemoryEntityRepository[ProtectedPerson]):
    def __init__(self) -> None:
        super().__init__("protected_person_id")


class InMemoryUserRepository(_InMemoryEntityRepository[User]):
    def __init__(self) -> None:
        super().__init__("user_id")


class InMemoryGuardianRepository(_InMemoryEntityRepository[Guardian]):
    def __init__(self) -> None:
        super().__init__("guardian_id")


class InMemoryMessageRepository(_InMemoryEntityRepository[Message]):
    def __init__(self) -> None:
        super().__init__("message_id")


class InMemoryRiskAssessmentRepository(_InMemoryEntityRepository[RiskAssessment]):
    def __init__(self) -> None:
        super().__init__("risk_assessment_id")


class InMemoryCaseRepository(_InMemoryEntityRepository[Case]):
    def __init__(self) -> None:
        super().__init__("case_id")


class InMemoryChannelConnectionRepository(_InMemoryEntityRepository[ChannelConnection]):
    def __init__(self) -> None:
        super().__init__("channel_connection_id")


class InMemoryEventRepository:
    def __init__(self) -> None:
        self._events: List[BotEvent] = []
        self._event_ids: set[str] = set()
        self._lock = RLock()

    def append(self, event: BotEvent) -> BotEvent:
        stored = event.model_copy(deep=True)
        with self._lock:
            if event.event_id in self._event_ids:
                raise ValueError(f"Event already recorded: {event.event_id}")
            self._events.append(stored)
            self._event_ids.add(event.event_id)
        return stored.model_copy(deep=True)

    def list_all(self) -> List[BotEvent]:
        with self._lock:
            events = list(self._events)
        return [event.model_copy(deep=True) for event in events]

    def list_by_aggregate(self, aggregate_id: str) -> List[BotEvent]:
        return [event for event in self.list_all() if event.aggregate_id == aggregate_id]

    def list_by_type(self, event_type: BotEventType) -> List[BotEvent]:
        return [event for event in self.list_all() if event.event_type == event_type]


class InMemoryAuditLogRepository(_InMemoryEntityRepository[AuditLog]):
    def __init__(self) -> None:
        super().__init__("audit_log_id")


@dataclass(frozen=True)
class EventModelRepositories:
    users: UserRepository
    protected_people: ProtectedPersonRepository
    guardians: GuardianRepository
    messages: MessageRepository
    risk_assessments: RiskAssessmentRepository
    cases: CaseRepository
    channel_connections: ChannelConnectionRepository
    events: EventRepository
    audit_logs: AuditLogRepository


def create_in_memory_repositories() -> EventModelRepositories:
    return EventModelRepositories(
        users=InMemoryUserRepository(),
        protected_people=InMemoryProtectedPersonRepository(),
        guardians=InMemoryGuardianRepository(),
        messages=InMemoryMessageRepository(),
        risk_assessments=InMemoryRiskAssessmentRepository(),
        cases=InMemoryCaseRepository(),
        channel_connections=InMemoryChannelConnectionRepository(),
        events=InMemoryEventRepository(),
        audit_logs=InMemoryAuditLogRepository(),
    )
