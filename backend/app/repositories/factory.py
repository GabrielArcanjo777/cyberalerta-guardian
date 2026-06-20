from __future__ import annotations

from app.core.config import config
from app.repositories.base import OperationalStateRepository
from app.repositories.memory import InMemoryOperationalStateRepository


_memory_repository = InMemoryOperationalStateRepository()


def get_operational_state_repository() -> OperationalStateRepository:
    if config.storage_backend != "memory":
        # Phase 1 intentionally keeps the operational repository in memory.
        # SQLite wiring is reserved for the next approved phase.
        return _memory_repository
    return _memory_repository


def reset_memory_operational_state_repository() -> None:
    global _memory_repository
    _memory_repository = InMemoryOperationalStateRepository()
