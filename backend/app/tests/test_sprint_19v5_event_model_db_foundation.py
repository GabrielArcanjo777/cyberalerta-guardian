from app.event_model import (
    BotEventType,
    ChannelConnection,
    ChannelConnectionStatus,
    EntityStatus,
    EventModelService,
    Guardian,
    ProtectedPerson,
    RiskLevel,
    User,
)


def test_v5_defines_minimum_event_contract():
    required = {
        "SuspiciousMessageReceived",
        "RiskAssessmentCreated",
        "CaseCreated",
        "ResponsibleAlertQueued",
        "ResponsibleNotified",
        "PatternCandidateDetected",
        "GuardianFeedbackReceived",
    }

    assert required.issubset({event_type.value for event_type in BotEventType})


def test_v5_repositories_store_minimum_entities_for_db_foundation():
    service = EventModelService.in_memory()
    user = service.repositories.users.save(User(alias="Operador Guardian", email="ops@example.test"))
    protected = service.repositories.protected_people.save(
        ProtectedPerson(alias="Dona Lucia", user_id=user.user_id)
    )
    guardian = service.repositories.guardians.save(Guardian(alias="Gabriel", user_id=user.user_id))
    connection = service.repositories.channel_connections.save(
        ChannelConnection(
            provider="mock",
            channel="whatsapp",
            protected_person_id=protected.protected_person_id,
            guardian_id=guardian.guardian_id,
            external_contact_id="mock-contact-1",
            status=ChannelConnectionStatus.ACTIVE,
            simulated=True,
        )
    )

    assert service.repositories.users.get(user.user_id).status == EntityStatus.ACTIVE
    assert service.repositories.protected_people.get(protected.protected_person_id).user_id == user.user_id
    assert service.repositories.guardians.get(guardian.guardian_id).user_id == user.user_id
    assert service.repositories.channel_connections.get(
        connection.channel_connection_id
    ).provider == "mock"


def test_v5_processes_suspicious_message_with_capped_explainable_risk_and_audit_log():
    service = EventModelService.in_memory()

    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        guardian=Guardian(alias="Gabriel"),
        body=(
            "Urgente agora: troquei de numero. Preciso de Pix. "
            "Nao liga, nao conte para ninguem, e segredo. "
            "Por favor, estou desesperado. Abra https://regularizacao.invalid "
            "e informe o codigo token."
        ),
        channel="whatsapp:mock",
        provider_message_id="mock-provider-message-19v5",
    )

    assert result.case is not None
    assert result.risk_assessment.score == 100
    assert result.risk_assessment.risk_level == RiskLevel.HIGH
    assert {
        "urgency",
        "pix_or_payment",
        "new_number",
        "unknown_link",
        "do_not_call",
        "secrecy_request",
        "emotional_pressure",
        "password_or_code",
    }.issubset(set(result.risk_assessment.signals))
    assert result.risk_assessment.case_threshold_reached is True
    assert "score capped at 100" in " ".join(result.risk_assessment.explanation)

    events = service.repositories.events.list_all()
    assert [event.event_type for event in events] == [
        BotEventType.MESSAGE_RECEIVED,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED,
        BotEventType.RISK_ASSESSMENT_CREATED,
        BotEventType.CASE_CREATED,
        BotEventType.RESPONSIBLE_ALERT_QUEUED,
    ]
    assert events[0].source == "channel_adapter"
    assert events[0].protected_person_id == result.message.protected_person_id
    assert events[-1].case_id == result.case.case_id
    assert events[-1].payload["delivery_pending"] is True
    assert len(service.repositories.audit_logs.list_all()) == len(events)


def test_v5_core_stores_provider_neutral_message_metadata_only():
    service = EventModelService.in_memory()

    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        body="Pix urgente. Nao liga agora.",
        channel="whatsapp:future-adapter",
        provider_message_id="external-message-123",
        simulated=False,
    )

    assert result.case is not None
    assert result.message.channel == "whatsapp:future-adapter"
    assert result.message.provider_message_id == "external-message-123"
    assert result.message.simulated is False
    assert all("rawPayload" not in event.payload for event in service.repositories.events.list_all())
