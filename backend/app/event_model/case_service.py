from __future__ import annotations

from app.event_model.event_bus import LocalEventBus
from app.event_model.models import (
    BotEventType,
    Case,
    CaseStatus,
    Message,
    RiskAssessment,
    utc_now,
)
from app.event_model.repositories import CaseRepository


class CaseNotFoundError(LookupError):
    pass


class CaseService:
    def __init__(self, repository: CaseRepository, event_bus: LocalEventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    def create_case(
        self,
        *,
        message: Message,
        risk_assessment: RiskAssessment,
        protected_person_id: str,
        guardian_id: str | None = None,
    ) -> Case:
        if risk_assessment.message_id != message.message_id:
            raise ValueError("Risk assessment does not belong to the source message.")
        if not risk_assessment.case_threshold_reached:
            raise ValueError("Risk assessment did not reach the case creation threshold.")

        case = Case(
            protected_person_id=protected_person_id,
            guardian_id=guardian_id,
            source_message_id=message.message_id,
            risk_assessment_id=risk_assessment.risk_assessment_id,
            risk_score=risk_assessment.score,
            risk_level=risk_assessment.risk_level,
        )
        saved = self._repository.save(case)
        self._event_bus.publish_type(
            BotEventType.CASE_CREATED,
            aggregate_type="case",
            aggregate_id=saved.case_id,
            case_id=saved.case_id,
            protected_person_id=saved.protected_person_id,
            payload={
                "source_message_id": saved.source_message_id,
                "risk_assessment_id": saved.risk_assessment_id,
                "risk_score": saved.risk_score,
                "risk_level": saved.risk_level.value,
                "status": saved.status.value,
            },
        )
        return saved

    def list_cases(self) -> list[Case]:
        return sorted(self._repository.list_all(), key=lambda item: item.created_at, reverse=True)

    def get_case_by_id(self, case_id: str) -> Case:
        case = self._repository.get(case_id)
        if not case:
            raise CaseNotFoundError(f"Case not found: {case_id}")
        return case

    def update_case_status(self, case_id: str, status: CaseStatus | str) -> Case:
        case = self.get_case_by_id(case_id)
        next_status = status if isinstance(status, CaseStatus) else CaseStatus(status)
        updated = case.model_copy(update={"status": next_status, "updated_at": utc_now()})
        return self._repository.save(updated)
