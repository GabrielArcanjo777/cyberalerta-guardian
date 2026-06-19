from __future__ import annotations

from fastapi.testclient import TestClient

from app.consent import (
    ConsentAcceptRequest,
    ConsentBotActivationRequest,
    ConsentRevokeRequest,
    ConsentScope,
    ConsentService,
    OptInStatus,
)
from app.dual_bot import DualBotFlowService, DualBotInboundRequest
from app.event_model import BotEventType, EventModelService
from app.guardian_console import GuardianConsoleRealFlowService
from main import app


def test_v5_consent_service_records_accept_deactivate_and_revoke_events():
    event_model = EventModelService.in_memory()
    service = ConsentService(event_model.event_bus)

    accepted = service.accept(
        ConsentAcceptRequest(
            protected_person_id="protected-lgpd-001",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            scopes=[ConsentScope.PROTECTED_BOT, ConsentScope.RESPONSIBLE_ALERTS],
        )
    )
    disabled = service.deactivate_bot(
        ConsentBotActivationRequest(
            protected_person_id="protected-lgpd-001",
            reason="Pausa solicitada pelo responsavel.",
        )
    )
    revoked = service.revoke(
        ConsentRevokeRequest(
            protected_person_id="protected-lgpd-001",
            reason="Revogacao solicitada.",
        )
    )

    assert accepted.record.status == OptInStatus.ACTIVE
    assert accepted.record.bot_active is True
    assert disabled.record.status == OptInStatus.BOT_DISABLED
    assert disabled.record.bot_active is False
    assert revoked.record.status == OptInStatus.REVOKED
    assert revoked.record.bot_active is False

    emitted = [event.event_type for event in event_model.repositories.events.list_all()]
    assert BotEventType.CONSENT_ACCEPTED in emitted
    assert BotEventType.BOT_ACTIVATED in emitted
    assert BotEventType.BOT_DEACTIVATED in emitted
    assert BotEventType.CONSENT_REVOKED in emitted


def test_v5_console_reflects_consent_status_for_case_bot_activation():
    event_model = EventModelService.in_memory()
    dual_bot = DualBotFlowService(event_model=event_model)
    flow = dual_bot.receive_mock_message(
        DualBotInboundRequest(
            providerMessageId="lgpd-console-001",
            body="Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
            guardian_address="+5511888880001",
        )
    )
    case = event_model.repositories.cases.get(flow.case_id)
    consent = ConsentService(event_model.event_bus)
    consent.accept(
        ConsentAcceptRequest(
            protected_person_id=case.protected_person_id,
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
        )
    )
    console = GuardianConsoleRealFlowService(dual_bot, consent)

    detail = console.get_case_detail(flow.case_id)
    assert detail.consent.status == OptInStatus.ACTIVE.value
    assert detail.consent.bot_active is True
    assert detail.activation.protected_bot.active is True

    consent.deactivate_bot(
        ConsentBotActivationRequest(
            protected_person_id=case.protected_person_id,
            reason="Pausa operacional.",
        )
    )
    updated = console.get_case_detail(flow.case_id)
    assert updated.consent.status == OptInStatus.BOT_DISABLED.value
    assert updated.consent.bot_active is False
    assert updated.activation.protected_bot.active is False
    assert updated.channel_status.responsible_bot_active is False


def test_v5_consent_api_and_console_status_contract():
    client = TestClient(app)
    protected_person_id = "protected-lgpd-api-001"

    pending = client.get(f"/consent/status?protected_person_id={protected_person_id}")
    assert pending.status_code == 200
    assert pending.json()["record"]["status"] == OptInStatus.PENDING.value
    assert pending.json()["production_whatsapp_enabled"] is False

    accepted = client.post(
        "/consent/accept",
        json={
            "protected_person_id": protected_person_id,
            "protected_person_alias": "Dona Lucia",
            "guardian_alias": "Gabriel",
            "scopes": ["protected_bot", "responsible_alerts", "pattern_analysis"],
        },
    )
    assert accepted.status_code == 200
    assert accepted.json()["record"]["bot_active"] is True
    assert accepted.json()["latest_event"]["event_type"] == "bot_activated"

    deactivated = client.post(
        "/consent/bot/deactivate",
        json={"protected_person_id": protected_person_id, "reason": "Teste de pausa."},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["record"]["status"] == OptInStatus.BOT_DISABLED.value

    status = client.get("/guardian-console/real/status")
    assert status.status_code == 200
    body = status.json()
    assert "consent" in body
    assert body["consent"]["status"] in {
        OptInStatus.PENDING.value,
        OptInStatus.ACTIVE.value,
        OptInStatus.BOT_DISABLED.value,
        OptInStatus.REVOKED.value,
    }
