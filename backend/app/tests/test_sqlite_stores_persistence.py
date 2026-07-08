"""Regression coverage for the SQLite storage backend.

Before this suite, the admin/consent/trusted SQLite stores imported their model
classes only under TYPE_CHECKING, so any read raised NameError at runtime — and
no test exercised STORAGE_BACKEND=sqlite end-to-end, so it went unnoticed. These
tests construct a real SQLite store, then reopen it on the SAME file to force the
deserialization path (which is where the bug lived) and prove data persists.
"""

from __future__ import annotations

from app.consent.models import ConsentRecord
from app.storage.sqlite import SQLiteStorage
from app.trusted_circle.trusted_circle_models import TrustedCircleEscalationRecord


def _escalation(escalation_id: str = "esc-1", case_id: str = "case-1") -> TrustedCircleEscalationRecord:
    return TrustedCircleEscalationRecord(
        escalation_id=escalation_id,
        case_id=case_id,
        risk_level="high",
        protected_person_alias="Dona Lucia",
        trusted_contacts=["+5511999990000"],
        reason="Pix urgente suspeito",
        status="simulated_notified",
        message_to_guardian="Alerta: possível golpe em andamento.",
        proof_of_trust_recommended=True,
        sent_real_notification=False,
        created_at="2026-07-08T10:00:00Z",
    )


def test_admin_case_store_persists_across_reopen(tmp_path):
    db = str(tmp_path / "admin.db")

    store = SQLiteStorage(db)
    store.admin_case_store.ensure_initialized()  # seeds valid AdminCase samples
    seeded = store.admin_case_store.list_cases()
    assert len(seeded) >= 1
    first_id = seeded[0].case_id
    store.close()

    reopened = SQLiteStorage(db)
    cases = reopened.admin_case_store.list_cases()  # deserializes AdminCase from JSON
    assert len(cases) == len(seeded)
    assert reopened.admin_case_store.get_case(first_id) is not None
    reopened.close()


def test_consent_store_persists_across_reopen(tmp_path):
    db = str(tmp_path / "consent.db")

    store = SQLiteStorage(db)
    record: ConsentRecord = store.consent_store.get_or_create_record("pp-1", "Dona Lucia")
    assert record.protected_person_id == "pp-1"
    # exercises the ConsentEvent deserialization path (empty is fine)
    assert store.consent_store.list_events(record.consent_id) == []
    store.close()

    reopened = SQLiteStorage(db)
    persisted = reopened.consent_store.get_record("pp-1")  # deserializes ConsentRecord
    assert persisted is not None
    assert persisted.consent_id == record.consent_id
    reopened.close()


def test_trusted_circle_store_persists_across_reopen(tmp_path):
    db = str(tmp_path / "trusted.db")

    store = SQLiteStorage(db)
    store.trusted_circle_store.save(_escalation("esc-1", "case-1"))
    store.close()

    reopened = SQLiteStorage(db)
    got = reopened.trusted_circle_store.get("esc-1")  # deserializes the record
    assert got is not None
    assert got.case_id == "case-1"
    assert reopened.trusted_circle_store.latest_for_case("case-1") is not None
    assert len(reopened.trusted_circle_store.list_all()) == 1
    reopened.close()
