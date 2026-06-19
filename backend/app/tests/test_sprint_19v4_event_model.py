import pytest

from app.event_model import (
    BotEvent,
    BotEventType,
    CaseStatus,
    EventModelService,
    Guardian,
    InMemoryEventRepository,
    LocalEventBus,
    ProtectedPerson,
    RiskLevel,
)


def test_defines_all_required_sprint_events():
    required_events = {
        "MessageReceived",
        "SuspiciousMessageReceived",
        "RiskAssessmentCreated",
        "CaseCreated",
        "SafeReplySent",
        "ResponsibleAlertQueued",
        "ResponsibleNotified",
        "CaseResolved",
        "FalsePositiveMarked",
        "PatternCandidateDetected",
        "ProtectedPersonReplied",
        "GuardianAlertTriggered",
        "GuardianNotified",
        "GuardianFeedbackReceived",
        "PatternDetected",
        "ConsentUpdated",
        "DeliveryStatusUpdated",
    }
    assert required_events.issubset({event_type.value for event_type in BotEventType})


def test_rule_based_assessment_uses_sprint_weights():
    service = EventModelService.in_memory()
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        guardian=Guardian(alias="Gabriel"),
        body=(
            "Urgente: troquei de numero. Faca um Pix agora, nao liga. "
            "Abra https://exemplo.invalid e informe o codigo."
        ),
    )

    assessment = result.risk_assessment
    assert assessment.score == 100
    assert assessment.risk_level == RiskLevel.HIGH
    assert set(assessment.signals) == {
        "urgency",
        "pix_or_payment",
        "new_number",
        "do_not_call",
        "unknown_link",
        "password_or_code",
    }
    assert any(item.startswith("score capped at 100 from ") for item in assessment.explanation)


def test_simulated_suspicious_message_persists_case_and_auditable_events():
    service = EventModelService.in_memory()
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        guardian=Guardian(alias="Gabriel"),
        body="Troquei de numero. Preciso de um Pix.",
    )

    assert result.risk_assessment.score == 45
    assert result.risk_assessment.case_threshold_reached is True
    assert result.case is not None
    assert result.case.status == CaseStatus.NEW
    assert service.repositories.messages.get(result.message.message_id) == result.message
    assert service.repositories.risk_assessments.get(
        result.risk_assessment.risk_assessment_id
    ) == result.risk_assessment
    assert service.repositories.cases.get(result.case.case_id) == result.case

    events = service.repositories.events.list_all()
    assert [event.event_type for event in events] == [
        BotEventType.MESSAGE_RECEIVED,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED,
        BotEventType.RISK_ASSESSMENT_CREATED,
        BotEventType.CASE_CREATED,
        BotEventType.RESPONSIBLE_ALERT_QUEUED,
    ]
    assert all(event.event_id in result.emitted_event_ids for event in events)


def test_score_below_threshold_does_not_create_case_or_alert():
    service = EventModelService.in_memory()
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        body="Recebi uma pagina e gostaria de confirmar se esta tudo bem.",
    )

    assert result.risk_assessment.score == 0
    assert result.risk_assessment.risk_level == RiskLevel.LOW
    assert result.case is None
    assert service.repositories.cases.list_all() == []
    assert [event.event_type for event in service.repositories.events.list_all()] == [
        BotEventType.MESSAGE_RECEIVED,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED,
        BotEventType.RISK_ASSESSMENT_CREATED,
    ]


def test_case_service_lists_gets_and_updates_case_status():
    service = EventModelService.in_memory()
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        guardian=Guardian(alias="Gabriel"),
        body="Pagamento urgente. Nao liga agora.",
    )
    assert result.case is not None

    updated = service.cases.update_case_status(result.case.case_id, CaseStatus.UNDER_REVIEW)

    assert updated.status == CaseStatus.UNDER_REVIEW
    assert service.cases.get_case_by_id(result.case.case_id).status == CaseStatus.UNDER_REVIEW
    assert [case.case_id for case in service.cases.list_cases()] == [result.case.case_id]


def test_local_event_bus_records_before_notifying_subscribers():
    repository = InMemoryEventRepository()
    bus = LocalEventBus(repository)
    observed_event_counts = []
    bus.subscribe(
        BotEventType.CONSENT_UPDATED,
        lambda event: observed_event_counts.append(len(repository.list_all())),
    )

    recorded = bus.publish(
        BotEvent(
            event_type=BotEventType.CONSENT_UPDATED,
            aggregate_type="protected_person",
            aggregate_id="protected-1",
            payload={"consent": True, "simulated": True},
        )
    )

    assert observed_event_counts == [1]
    assert repository.list_by_type(BotEventType.CONSENT_UPDATED) == [recorded]


def test_invalid_case_status_is_rejected():
    service = EventModelService.in_memory()
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        body="Pix urgente.",
    )
    assert result.case is not None

    with pytest.raises(ValueError):
        service.cases.update_case_status(result.case.case_id, "invalid")
