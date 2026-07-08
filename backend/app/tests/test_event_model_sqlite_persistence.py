"""Fase 1 — persistence of the core Event Model in SQLite.

Verifies that domain data survives a fresh service instance pointing at the same
database file, that the SQLite event store keeps in-memory contract semantics
(insertion order + duplicate protection), and that a shared Event Model makes an
Evolution-created case visible to the Guardian Console.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.channel_adapters.evolution_demo_adapter import (
    EvolutionDemoAdapter,
    EvolutionDemoConfig,
)
from app.event_model import EventModelService
from app.event_model.sqlite_repositories import create_sqlite_repositories
from app.event_model.models import BotEvent, BotEventType, Guardian, Message, ProtectedPerson
from app.evolution_demo import EvolutionDemoService
from app.dual_bot import DualBotFlowService
from app.guardian_console import GuardianConsoleRealFlowService
from app.storage.sqlite import SQLiteConnection


def _repos(db_path: str):
    return create_sqlite_repositories(SQLiteConnection(db_path))


def _messages_upsert(message_id: str = "EVOIN001") -> dict[str, Any]:
    return {
        "event": "MESSAGES_UPSERT",
        "instance": "guardian-demo",
        "data": {
            "key": {"id": message_id, "remoteJid": "5511999990001@s.whatsapp.net", "fromMe": False},
            "pushName": "Dona Lucia",
            "messageTimestamp": 1780000000,
            "message": {"conversation": "Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora."},
        },
    }


def test_entities_persist_across_new_service_instance(tmp_path):
    db = str(tmp_path / "guardian.db")

    repos = _repos(db)
    person = repos.protected_people.save(ProtectedPerson(alias="Dona Lucia"))
    guardian = repos.guardians.save(Guardian(alias="Gabriel"))
    message = repos.messages.save(
        Message(protected_person_id=person.protected_person_id, body="mensagem de teste", channel="whatsapp")
    )

    # New repository set over the SAME file — data must still be there.
    reopened = _repos(db)
    assert reopened.protected_people.get(person.protected_person_id).alias == "Dona Lucia"
    assert reopened.guardians.get(guardian.guardian_id).alias == "Gabriel"
    assert reopened.messages.get(message.message_id).body == "mensagem de teste"
    assert len(reopened.protected_people.list_all()) == 1


def test_sqlite_event_store_keeps_order_and_rejects_duplicates(tmp_path):
    db = str(tmp_path / "events.db")
    repos = _repos(db)

    first = repos.events.append(
        BotEvent(event_type=BotEventType.MESSAGE_RECEIVED, aggregate_type="message", aggregate_id="m1")
    )
    repos.events.append(
        BotEvent(event_type=BotEventType.CASE_CREATED, aggregate_type="case", aggregate_id="c1")
    )

    ordered = repos.events.list_all()
    assert [event.event_type for event in ordered] == [
        BotEventType.MESSAGE_RECEIVED,
        BotEventType.CASE_CREATED,
    ]
    assert [e.aggregate_id for e in repos.events.list_by_aggregate("m1")] == ["m1"]
    assert repos.events.list_by_type(BotEventType.CASE_CREATED)[0].aggregate_id == "c1"

    with pytest.raises(ValueError):
        repos.events.append(first)  # same event_id -> duplicate


def test_process_suspicious_message_persists_case(tmp_path):
    db = str(tmp_path / "flow.db")

    service = EventModelService(_repos(db))
    result = service.process_suspicious_message(
        protected_person=ProtectedPerson(alias="Dona Lucia"),
        body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
        guardian=Guardian(alias="Gabriel"),
        channel="whatsapp",
    )
    assert result.case is not None
    case_id = result.case.case_id

    reopened = EventModelService(_repos(db))
    assert reopened.repositories.cases.get(case_id) is not None
    assert len(reopened.repositories.events.list_all()) >= 4


def test_shared_event_model_exposes_evolution_case_to_console(tmp_path):
    db = str(tmp_path / "shared.db")
    shared = EventModelService(_repos(db))

    evolution = EvolutionDemoService(
        adapter=EvolutionDemoAdapter(
            config=EvolutionDemoConfig(
                api_url="http://evolution.local",
                api_key="local-demo-key",
                instance_name="guardian-demo",
                guardian_address="5511888880001",
            )
        ),
        event_model=shared,
    )
    console = GuardianConsoleRealFlowService(DualBotFlowService(event_model=shared))

    evolution.handle_webhook(_messages_upsert("EVOSHARED001"))

    listing = console.list_cases()
    assert listing.total >= 1

    # And the case survives a brand-new console over the same database file.
    reopened_console = GuardianConsoleRealFlowService(DualBotFlowService(event_model=EventModelService(_repos(db))))
    assert reopened_console.list_cases().total >= 1
