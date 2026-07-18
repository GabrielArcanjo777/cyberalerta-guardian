"""Sprint 2 foundation (Plano Mestre v1.1) — Organization as the isolation
boundary that the devices/pairing IDOR test (Secao 6.5) will rely on.

Covers: in-memory + SQLite persistence of Organization, org-scoped
ProtectedPerson/Guardian/Case, and the new TRUSTED_CONTACT role + organization_id
on AuthUser (including backfill onto a users table created before the column
existed).
"""

from __future__ import annotations

import sqlite3

from app.auth.models import AuthUser, UserRole
from app.auth.repository import SQLiteAuthRepository
from app.event_model.models import Case, Guardian, Organization, ProtectedPerson
from app.event_model.repositories import create_in_memory_repositories
from app.event_model.sqlite_repositories import create_sqlite_repositories
from app.storage.sqlite import SQLiteConnection


def _sqlite_url(path: str) -> str:
    # _resolve_sqlite_url() parses this as a URL; on Windows a bare "D:\..." path
    # misparses "D" as the URL scheme, so route through sqlite:/// like the app does.
    return "sqlite:///" + path.replace("\\", "/")


def test_organization_defaults_are_backward_compatible_with_existing_entities():
    # Pre-existing single-tenant demo data (protected_person/guardian/case built
    # without an org) must keep constructing and persisting exactly as before.
    person = ProtectedPerson(alias="Dona Lucia")
    guardian = Guardian(alias="Gabriel")
    case = Case(
        protected_person_id=person.protected_person_id,
        source_message_id="msg-1",
        risk_assessment_id="risk-1",
        risk_score=80,
        risk_level="high",
    )
    assert person.organization_id is None
    assert guardian.organization_id is None
    assert case.organization_id is None


def test_in_memory_organization_repository_scopes_entities():
    repos = create_in_memory_repositories()
    org_a = repos.organizations.save(Organization(name="Familia A"))
    org_b = repos.organizations.save(Organization(name="Familia B"))

    person_a = repos.protected_people.save(
        ProtectedPerson(alias="Dona Lucia", organization_id=org_a.organization_id)
    )
    person_b = repos.protected_people.save(
        ProtectedPerson(alias="Seu Joao", organization_id=org_b.organization_id)
    )

    assert repos.protected_people.get(person_a.protected_person_id).organization_id == org_a.organization_id
    assert repos.protected_people.get(person_b.protected_person_id).organization_id == org_b.organization_id
    assert {org.organization_id for org in repos.organizations.list_all()} == {
        org_a.organization_id,
        org_b.organization_id,
    }


def test_sqlite_organization_and_scoped_entities_persist_across_reopen(tmp_path):
    db = str(tmp_path / "organizations.db")

    repos = create_sqlite_repositories(SQLiteConnection(db))
    org = repos.organizations.save(Organization(name="Familia Arcanjo"))
    person = repos.protected_people.save(
        ProtectedPerson(alias="Dona Lucia", organization_id=org.organization_id)
    )
    guardian = repos.guardians.save(
        Guardian(alias="Gabriel", organization_id=org.organization_id)
    )
    case = repos.cases.save(
        Case(
            organization_id=org.organization_id,
            protected_person_id=person.protected_person_id,
            guardian_id=guardian.guardian_id,
            source_message_id="msg-1",
            risk_assessment_id="risk-1",
            risk_score=80,
            risk_level="high",
        )
    )

    reopened = create_sqlite_repositories(SQLiteConnection(db))
    assert reopened.organizations.get(org.organization_id).name == "Familia Arcanjo"
    assert reopened.protected_people.get(person.protected_person_id).organization_id == org.organization_id
    assert reopened.guardians.get(guardian.guardian_id).organization_id == org.organization_id
    assert reopened.cases.get(case.case_id).organization_id == org.organization_id


def test_trusted_contact_role_and_organization_id_persist_in_sqlite(tmp_path):
    db = str(tmp_path / "auth.db")
    repo = SQLiteAuthRepository(sqlite_url=_sqlite_url(db))

    user = repo.create_user(
        AuthUser(
            email="contato@example.com",
            full_name="Gabriel",
            role=UserRole.TRUSTED_CONTACT,
            organization_id="org-arcanjo",
        )
    )
    assert user.role == UserRole.TRUSTED_CONTACT

    reopened = SQLiteAuthRepository(sqlite_url=_sqlite_url(db))
    fetched = reopened.get_user_by_id(user.id)
    assert fetched is not None
    assert fetched.role == UserRole.TRUSTED_CONTACT
    assert fetched.organization_id == "org-arcanjo"


def test_users_table_without_organization_id_column_is_backfilled(tmp_path):
    # Simulates a users table created by a pre-Sprint-2 build of the app, before
    # organization_id existed, to prove the ALTER TABLE backfill is safe.
    db = str(tmp_path / "legacy.db")
    conn = sqlite3.connect(db)
    conn.execute(
        """
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            is_admin INTEGER NOT NULL,
            mfa_enabled INTEGER NOT NULL,
            mfa_secret TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()

    repo = SQLiteAuthRepository(sqlite_url=_sqlite_url(db))
    user = repo.create_user(AuthUser(email="legacy@example.com", full_name="Legacy Admin", role=UserRole.ADMIN))
    assert user.organization_id is None
    assert repo.get_user_by_email("legacy@example.com").organization_id is None
