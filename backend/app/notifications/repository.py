from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Optional, Protocol

from app.core.config import config
from app.notifications.models import Alert, utc_now
from app.storage.config import _resolve_sqlite_url


class AlertRepository(Protocol):
    def create_alert(self, alert: Alert) -> Alert: ...
    def update_alert(self, alert: Alert) -> Alert: ...
    def get_alert(self, alert_id: str) -> Optional[Alert]: ...
    def list_alerts_by_device(self, device_id: str) -> list[Alert]: ...


class InMemoryAlertRepository:
    def __init__(self) -> None:
        self._alerts: dict[str, Alert] = {}
        self._lock = threading.RLock()

    def create_alert(self, alert: Alert) -> Alert:
        stored = alert.model_copy(deep=True)
        with self._lock:
            self._alerts[stored.id] = stored
        return stored.model_copy(deep=True)

    def update_alert(self, alert: Alert) -> Alert:
        stored = alert.model_copy(update={"updated_at": utc_now()}, deep=True)
        with self._lock:
            if stored.id not in self._alerts:
                raise LookupError("Alert not found.")
            self._alerts[stored.id] = stored
        return stored.model_copy(deep=True)

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        with self._lock:
            alert = self._alerts.get(alert_id)
        return alert.model_copy(deep=True) if alert else None

    def list_alerts_by_device(self, device_id: str) -> list[Alert]:
        with self._lock:
            alerts = [a for a in self._alerts.values() if a.device_id == device_id]
        return [a.model_copy(deep=True) for a in sorted(alerts, key=lambda item: item.created_at)]


class SQLiteAlertRepository:
    def __init__(self, sqlite_url: str | None = None) -> None:
        self._path = _resolve_sqlite_url(sqlite_url or config.sqlite_database_url)
        if self._path != ":memory:":
            Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._ensure_schema()

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            return cursor

    def _ensure_schema(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                protected_person_alias TEXT,
                case_id TEXT,
                deep_link TEXT NOT NULL,
                state TEXT NOT NULL,
                retry_count INTEGER NOT NULL,
                failed_reason TEXT,
                sent_at TEXT,
                delivered_at TEXT,
                opened_at TEXT,
                actioned_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._execute("CREATE INDEX IF NOT EXISTS idx_alerts_device ON alerts(device_id)")

    def create_alert(self, alert: Alert) -> Alert:
        self._execute(
            """
            INSERT INTO alerts (
                id, organization_id, device_id, type, severity, protected_person_alias,
                case_id, deep_link, state, retry_count, failed_reason,
                sent_at, delivered_at, opened_at, actioned_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._params(alert),
        )
        return alert

    def update_alert(self, alert: Alert) -> Alert:
        stored = alert.model_copy(update={"updated_at": utc_now()}, deep=True)
        self._execute(
            """
            UPDATE alerts SET
                state = ?, retry_count = ?, failed_reason = ?,
                sent_at = ?, delivered_at = ?, opened_at = ?, actioned_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                stored.state.value,
                stored.retry_count,
                stored.failed_reason,
                stored.sent_at.isoformat() if stored.sent_at else None,
                stored.delivered_at.isoformat() if stored.delivered_at else None,
                stored.opened_at.isoformat() if stored.opened_at else None,
                stored.actioned_at.isoformat() if stored.actioned_at else None,
                stored.updated_at.isoformat(),
                stored.id,
            ),
        )
        return stored

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        row = self._execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        return self._row_to_alert(row) if row else None

    def list_alerts_by_device(self, device_id: str) -> list[Alert]:
        rows = self._execute(
            "SELECT * FROM alerts WHERE device_id = ? ORDER BY created_at ASC", (device_id,)
        ).fetchall()
        return [self._row_to_alert(row) for row in rows]

    def _params(self, alert: Alert) -> tuple:
        return (
            alert.id,
            alert.organization_id,
            alert.device_id,
            alert.type.value,
            alert.severity,
            alert.protected_person_alias,
            alert.case_id,
            alert.deep_link,
            alert.state.value,
            alert.retry_count,
            alert.failed_reason,
            alert.sent_at.isoformat() if alert.sent_at else None,
            alert.delivered_at.isoformat() if alert.delivered_at else None,
            alert.opened_at.isoformat() if alert.opened_at else None,
            alert.actioned_at.isoformat() if alert.actioned_at else None,
            alert.created_at.isoformat(),
            alert.updated_at.isoformat(),
        )

    def _row_to_alert(self, row: sqlite3.Row) -> Alert:
        data = dict(row)
        for key in ("sent_at", "delivered_at", "opened_at", "actioned_at", "created_at", "updated_at"):
            if data.get(key):
                data[key] = data[key].replace("Z", "+00:00")
        return Alert.model_validate(data)


_repository: AlertRepository | None = None


def create_notification_repository() -> AlertRepository:
    if config.storage_backend == "sqlite":
        return SQLiteAlertRepository()
    return InMemoryAlertRepository()


def get_notification_repository() -> AlertRepository:
    global _repository
    if _repository is None:
        _repository = create_notification_repository()
    return _repository


def reset_notification_repository_for_tests(repository: AlertRepository | None = None) -> AlertRepository:
    global _repository
    _repository = repository or InMemoryAlertRepository()
    return _repository
