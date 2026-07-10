from __future__ import annotations

from dataclasses import dataclass

from app.storage.config import storage_config
from app.storage.memory import (
    AdminCaseMemoryStore,
    ConsentMemoryStore,
    ProofTrustMemoryStore,
    SettingsMemoryStore,
    TrustedCircleMemoryStore,
)
from app.storage.sqlite import SQLiteStorage


@dataclass(frozen=True)
class StorageRegistry:
    admin_case_store: AdminCaseMemoryStore | object
    consent_store: ConsentMemoryStore | object
    proof_trust_store: ProofTrustMemoryStore | object
    trusted_circle_store: TrustedCircleMemoryStore | object
    settings_store: SettingsMemoryStore | object


def _create_memory_registry() -> StorageRegistry:
    return StorageRegistry(
        admin_case_store=AdminCaseMemoryStore(),
        consent_store=ConsentMemoryStore(),
        proof_trust_store=ProofTrustMemoryStore(),
        trusted_circle_store=TrustedCircleMemoryStore(),
        settings_store=SettingsMemoryStore(),
    )


def _create_sqlite_registry() -> StorageRegistry:
    sqlite = SQLiteStorage()
    return StorageRegistry(
        admin_case_store=sqlite.admin_case_store,
        consent_store=sqlite.consent_store,
        proof_trust_store=sqlite.proof_trust_store,
        trusted_circle_store=sqlite.trusted_circle_store,
        settings_store=sqlite.settings_store,
    )


storage = _create_sqlite_registry() if storage_config.storage_backend == "sqlite" else _create_memory_registry()

admin_case_store = storage.admin_case_store
consent_store = storage.consent_store
proof_trust_store = storage.proof_trust_store
trusted_circle_store = storage.trusted_circle_store
settings_store = storage.settings_store
