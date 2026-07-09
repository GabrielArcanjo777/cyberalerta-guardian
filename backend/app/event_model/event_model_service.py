from __future__ import annotations

from app.event_model.case_service import CaseService
from app.event_model.event_bus import LocalEventBus
from app.event_model.models import (
    BotEventType,
    Guardian,
    Message,
    MessageDirection,
    ProtectedPerson,
    SuspiciousMessageProcessingResult,
)
from app.event_model.repositories import EventModelRepositories, create_in_memory_repositories
from app.event_model.risk_assessment_service import RiskAssessmentService


class EventModelService:
    def __init__(self, repositories: EventModelRepositories) -> None:
        self.repositories = repositories
        self.event_bus = LocalEventBus(repositories.events, repositories.audit_logs)
        self.risk_assessments = RiskAssessmentService(repositories.risk_assessments, self.event_bus)
        self.cases = CaseService(repositories.cases, self.event_bus)

    @classmethod
    def in_memory(cls) -> "EventModelService":
        return cls(create_in_memory_repositories())

    @classmethod
    def from_config(cls) -> "EventModelService":
        """Select the persistence backend from app config.

        ``STORAGE_BACKEND=sqlite`` returns a SQLite-backed repository set (the
        core domain survives restarts); anything else falls back to in-memory.
        """
        from app.core.config import config

        if config.storage_backend == "sqlite":
            from app.event_model.sqlite_repositories import create_sqlite_repositories
            from app.storage.config import storage_config
            from app.storage.sqlite import SQLiteConnection

            connection = SQLiteConnection(storage_config.sqlite_path())
            return cls(create_sqlite_repositories(connection))
        return cls.in_memory()

    def process_suspicious_message(
        self,
        *,
        protected_person: ProtectedPerson,
        body: str,
        guardian: Guardian | None = None,
        channel: str = "simulated_whatsapp",
        provider_message_id: str | None = None,
        simulated: bool = True,
    ) -> SuspiciousMessageProcessingResult:
        before_events = len(self.repositories.events.list_all())
        saved_protected_person = self.repositories.protected_people.save(protected_person)
        saved_guardian = self.repositories.guardians.save(guardian) if guardian else None
        message = self.repositories.messages.save(
            Message(
                protected_person_id=saved_protected_person.protected_person_id,
                guardian_id=saved_guardian.guardian_id if saved_guardian else None,
                direction=MessageDirection.INBOUND,
                channel=channel,
                body=body,
                simulated=simulated,
                provider_message_id=provider_message_id,
            )
        )
        message_payload = {
            "protected_person_id": message.protected_person_id,
            "guardian_id": message.guardian_id,
            "channel": message.channel,
            "simulated": message.simulated,
            "provider_message_id": message.provider_message_id,
        }
        self.event_bus.publish_type(
            BotEventType.MESSAGE_RECEIVED,
            aggregate_type="message",
            aggregate_id=message.message_id,
            source="channel_adapter",
            protected_person_id=message.protected_person_id,
            payload=message_payload,
        )
        self.event_bus.publish_type(
            BotEventType.SUSPICIOUS_MESSAGE_RECEIVED,
            aggregate_type="message",
            aggregate_id=message.message_id,
            source="channel_adapter",
            protected_person_id=message.protected_person_id,
            payload=message_payload,
        )

        assessment = self.risk_assessments.assess(message)
        case = None
        if assessment.case_threshold_reached:
            case = self.cases.create_case(
                message=message,
                risk_assessment=assessment,
                protected_person_id=saved_protected_person.protected_person_id,
                guardian_id=saved_guardian.guardian_id if saved_guardian else None,
            )
            self.event_bus.publish_type(
                BotEventType.RESPONSIBLE_ALERT_QUEUED,
                aggregate_type="case",
                aggregate_id=case.case_id,
                source="event_model",
                case_id=case.case_id,
                protected_person_id=case.protected_person_id,
                payload={
                    "guardian_id": case.guardian_id,
                    "risk_score": case.risk_score,
                    "delivery_pending": True,
                    "simulated": simulated,
                },
            )

        emitted_events = self.repositories.events.list_all()[before_events:]
        return SuspiciousMessageProcessingResult(
            message=message,
            risk_assessment=assessment,
            case=case,
            emitted_event_ids=[event.event_id for event in emitted_events],
        )
