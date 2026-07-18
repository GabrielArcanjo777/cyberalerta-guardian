"""SQLite-backed repositories for the Event Model domain.

Mirrors :func:`app.event_model.repositories.create_in_memory_repositories` so the
core domain (users, protected people, guardians, messages, risk assessments,
cases, channel connections, events and audit logs) survives a backend restart
when ``STORAGE_BACKEND=sqlite``.

Entities are stored as JSON (``model_dump_json`` / ``model_validate_json``), the
same serialization pattern already used by :mod:`app.storage.sqlite`. Table names
are internal constants (never user input), so the small amount of table-name
string interpolation below has no injection surface.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel

from app.event_model.models import (
    AuditLog,
    BotEvent,
    BotEventType,
    Case,
    ChannelConnection,
    Guardian,
    Message,
    Organization,
    ProtectedPerson,
    RiskAssessment,
    User,
)
from app.event_model.repositories import EventModelRepositories
from app.storage.sqlite import SQLiteConnection

EntityT = TypeVar("EntityT", bound=BaseModel)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class _SqliteEntityRepository(Generic[EntityT]):
    """Generic key/value repository storing a Pydantic entity as JSON.

    Uses the implicit SQLite ``rowid`` for stable insertion-order listing; an
    upsert keeps the original ``rowid`` (and thus the original order) intact.
    """

    def __init__(
        self,
        connection: SQLiteConnection,
        *,
        table: str,
        id_attribute: str,
        model_cls: Type[EntityT],
    ) -> None:
        self._conn = connection
        self._table = table
        self._id_attribute = id_attribute
        self._model_cls = model_cls
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self._table} ("
            "id TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )

    def save(self, entity: EntityT) -> EntityT:
        entity_id = str(getattr(entity, self._id_attribute))
        payload = entity.model_dump_json()
        self._conn.execute(
            f"INSERT INTO {self._table}(id, data, updated_at) VALUES (?, ?, ?)"
            " ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
            (entity_id, payload, _now_iso()),
        )
        return entity.model_copy(deep=True)

    def get(self, entity_id: str) -> Optional[EntityT]:
        row = self._conn.execute(
            f"SELECT data FROM {self._table} WHERE id = ?", (entity_id,)
        ).fetchone()
        return self._model_cls.model_validate_json(row["data"]) if row else None

    def list_all(self) -> List[EntityT]:
        rows = self._conn.execute(
            f"SELECT data FROM {self._table} ORDER BY rowid ASC"
        ).fetchall()
        return [self._model_cls.model_validate_json(row["data"]) for row in rows]


class SqliteEventRepository:
    """Append-only event store. Preserves insertion order via ``rowid``."""

    _TABLE = "event_bot_events"

    def __init__(self, connection: SQLiteConnection) -> None:
        self._conn = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS {self._TABLE} ("
            "event_id TEXT PRIMARY KEY, aggregate_id TEXT, event_type TEXT, data TEXT NOT NULL)"
        )
        self._conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self._TABLE}_aggregate ON {self._TABLE}(aggregate_id)"
        )
        self._conn.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{self._TABLE}_type ON {self._TABLE}(event_type)"
        )

    def append(self, event: BotEvent) -> BotEvent:
        try:
            self._conn.execute(
                f"INSERT INTO {self._TABLE}(event_id, aggregate_id, event_type, data)"
                " VALUES (?, ?, ?, ?)",
                (event.event_id, event.aggregate_id, event.event_type.value, event.model_dump_json()),
            )
        except sqlite3.IntegrityError as exc:  # duplicate event_id — matches in-memory contract
            raise ValueError(f"Event already recorded: {event.event_id}") from exc
        return event.model_copy(deep=True)

    def list_all(self) -> List[BotEvent]:
        rows = self._conn.execute(
            f"SELECT data FROM {self._TABLE} ORDER BY rowid ASC"
        ).fetchall()
        return [BotEvent.model_validate_json(row["data"]) for row in rows]

    def list_by_aggregate(self, aggregate_id: str) -> List[BotEvent]:
        rows = self._conn.execute(
            f"SELECT data FROM {self._TABLE} WHERE aggregate_id = ? ORDER BY rowid ASC",
            (aggregate_id,),
        ).fetchall()
        return [BotEvent.model_validate_json(row["data"]) for row in rows]

    def list_by_type(self, event_type: BotEventType) -> List[BotEvent]:
        rows = self._conn.execute(
            f"SELECT data FROM {self._TABLE} WHERE event_type = ? ORDER BY rowid ASC",
            (event_type.value,),
        ).fetchall()
        return [BotEvent.model_validate_json(row["data"]) for row in rows]


def create_sqlite_repositories(connection: SQLiteConnection) -> EventModelRepositories:
    """Build the full repository set backed by a shared SQLite connection."""
    return EventModelRepositories(
        organizations=_SqliteEntityRepository(
            connection,
            table="event_organizations",
            id_attribute="organization_id",
            model_cls=Organization,
        ),
        users=_SqliteEntityRepository(
            connection, table="event_users", id_attribute="user_id", model_cls=User
        ),
        protected_people=_SqliteEntityRepository(
            connection,
            table="event_protected_people",
            id_attribute="protected_person_id",
            model_cls=ProtectedPerson,
        ),
        guardians=_SqliteEntityRepository(
            connection, table="event_guardians", id_attribute="guardian_id", model_cls=Guardian
        ),
        messages=_SqliteEntityRepository(
            connection, table="event_messages", id_attribute="message_id", model_cls=Message
        ),
        risk_assessments=_SqliteEntityRepository(
            connection,
            table="event_risk_assessments",
            id_attribute="risk_assessment_id",
            model_cls=RiskAssessment,
        ),
        cases=_SqliteEntityRepository(
            connection, table="event_cases", id_attribute="case_id", model_cls=Case
        ),
        channel_connections=_SqliteEntityRepository(
            connection,
            table="event_channel_connections",
            id_attribute="channel_connection_id",
            model_cls=ChannelConnection,
        ),
        events=SqliteEventRepository(connection),
        audit_logs=_SqliteEntityRepository(
            connection, table="event_audit_logs", id_attribute="audit_log_id", model_cls=AuditLog
        ),
    )
