from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List

from app.event_model.models import AuditLog, BotEvent, BotEventType
from app.event_model.repositories import AuditLogRepository, EventRepository

EventHandler = Callable[[BotEvent], None]


class LocalEventBus:
    def __init__(
        self,
        event_repository: EventRepository,
        audit_log_repository: AuditLogRepository | None = None,
    ) -> None:
        self._event_repository = event_repository
        self._audit_log_repository = audit_log_repository
        self._handlers: DefaultDict[BotEventType, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: BotEventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: BotEvent) -> BotEvent:
        recorded = self._event_repository.append(event)
        self._record_audit_log(recorded)
        for handler in list(self._handlers[event.event_type]):
            handler(recorded.model_copy(deep=True))
        return recorded

    def publish_type(
        self,
        event_type: BotEventType,
        *,
        aggregate_type: str,
        aggregate_id: str,
        source: str = "event_model",
        actor: str | None = None,
        case_id: str | None = None,
        protected_person_id: str | None = None,
        payload: Dict[str, Any] | None = None,
    ) -> BotEvent:
        return self.publish(
            BotEvent(
                event_type=event_type,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                source=source,
                actor=actor,
                case_id=case_id,
                protected_person_id=protected_person_id,
                payload=payload or {},
            )
        )

    def _record_audit_log(self, event: BotEvent) -> None:
        if self._audit_log_repository is None:
            return
        self._audit_log_repository.save(
            AuditLog(
                event_id=event.event_id,
                actor=event.actor,
                action=event.event_type.value,
                target_type=event.aggregate_type,
                target_id=event.aggregate_id,
                payload={
                    "source": event.source,
                    "case_id": event.case_id,
                    "protected_person_id": event.protected_person_id,
                },
            )
        )
