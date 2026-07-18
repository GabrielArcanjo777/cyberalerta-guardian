from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Optional, Protocol

from app.core.config import config
from app.devices.models import (
    Device,
    DevicePlatform,
    DeviceSession,
    DeviceState,
    PairingInvitation,
    PairingInvitationStatus,
    PushProvider,
    PushToken,
    utc_now,
)
from app.storage.config import _resolve_sqlite_url


class DeviceRepository(Protocol):
    # devices
    def create_device(self, device: Device) -> Device: ...
    def update_device(self, device: Device) -> Device: ...
    def get_device(self, device_id: str) -> Optional[Device]: ...
    def list_devices_by_user(self, user_id: str) -> list[Device]: ...
    def list_devices_by_organization(self, organization_id: str) -> list[Device]: ...

    # pairing invitations
    def create_invitation(self, invitation: PairingInvitation) -> PairingInvitation: ...
    def update_invitation(self, invitation: PairingInvitation) -> PairingInvitation: ...
    def get_invitation(self, invitation_id: str) -> Optional[PairingInvitation]: ...
    def get_invitation_by_token_hash(self, token_hash: str) -> Optional[PairingInvitation]: ...

    # device sessions
    def create_session(self, session: DeviceSession) -> DeviceSession: ...
    def update_session(self, session: DeviceSession) -> DeviceSession: ...
    def get_session(self, session_id: str) -> Optional[DeviceSession]: ...
    def list_sessions_by_device(self, device_id: str) -> list[DeviceSession]: ...

    # push tokens (one active token per device — a re-register overwrites it)
    def upsert_push_token(self, token: PushToken) -> PushToken: ...
    def get_push_token_by_device(self, device_id: str) -> Optional[PushToken]: ...
    def delete_push_token_by_device(self, device_id: str) -> None: ...


class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}
        self._invitations: dict[str, PairingInvitation] = {}
        self._invitations_by_token_hash: dict[str, str] = {}
        self._sessions: dict[str, DeviceSession] = {}
        self._push_tokens_by_device: dict[str, PushToken] = {}
        self._lock = threading.RLock()

    def create_device(self, device: Device) -> Device:
        stored = device.model_copy(deep=True)
        with self._lock:
            self._devices[stored.id] = stored
        return stored.model_copy(deep=True)

    def update_device(self, device: Device) -> Device:
        stored = device.model_copy(update={"updated_at": utc_now()}, deep=True)
        with self._lock:
            if stored.id not in self._devices:
                raise LookupError("Device not found.")
            self._devices[stored.id] = stored
        return stored.model_copy(deep=True)

    def get_device(self, device_id: str) -> Optional[Device]:
        with self._lock:
            device = self._devices.get(device_id)
        return device.model_copy(deep=True) if device else None

    def list_devices_by_user(self, user_id: str) -> list[Device]:
        with self._lock:
            devices = [d for d in self._devices.values() if d.user_id == user_id]
        return [d.model_copy(deep=True) for d in sorted(devices, key=lambda item: item.created_at)]

    def list_devices_by_organization(self, organization_id: str) -> list[Device]:
        with self._lock:
            devices = [d for d in self._devices.values() if d.organization_id == organization_id]
        return [d.model_copy(deep=True) for d in sorted(devices, key=lambda item: item.created_at)]

    def create_invitation(self, invitation: PairingInvitation) -> PairingInvitation:
        stored = invitation.model_copy(deep=True)
        with self._lock:
            self._invitations[stored.id] = stored
            self._invitations_by_token_hash[stored.token_hash] = stored.id
        return stored.model_copy(deep=True)

    def update_invitation(self, invitation: PairingInvitation) -> PairingInvitation:
        stored = invitation.model_copy(deep=True)
        with self._lock:
            if stored.id not in self._invitations:
                raise LookupError("Pairing invitation not found.")
            self._invitations[stored.id] = stored
            self._invitations_by_token_hash[stored.token_hash] = stored.id
        return stored.model_copy(deep=True)

    def get_invitation(self, invitation_id: str) -> Optional[PairingInvitation]:
        with self._lock:
            invitation = self._invitations.get(invitation_id)
        return invitation.model_copy(deep=True) if invitation else None

    def get_invitation_by_token_hash(self, token_hash: str) -> Optional[PairingInvitation]:
        with self._lock:
            invitation_id = self._invitations_by_token_hash.get(token_hash)
            invitation = self._invitations.get(invitation_id) if invitation_id else None
        return invitation.model_copy(deep=True) if invitation else None

    def create_session(self, session: DeviceSession) -> DeviceSession:
        stored = session.model_copy(deep=True)
        with self._lock:
            self._sessions[stored.id] = stored
        return stored.model_copy(deep=True)

    def update_session(self, session: DeviceSession) -> DeviceSession:
        stored = session.model_copy(deep=True)
        with self._lock:
            if stored.id not in self._sessions:
                raise LookupError("Device session not found.")
            self._sessions[stored.id] = stored
        return stored.model_copy(deep=True)

    def get_session(self, session_id: str) -> Optional[DeviceSession]:
        with self._lock:
            session = self._sessions.get(session_id)
        return session.model_copy(deep=True) if session else None

    def list_sessions_by_device(self, device_id: str) -> list[DeviceSession]:
        with self._lock:
            sessions = [s for s in self._sessions.values() if s.device_id == device_id]
        return [s.model_copy(deep=True) for s in sorted(sessions, key=lambda item: item.issued_at)]

    def upsert_push_token(self, token: PushToken) -> PushToken:
        stored = token.model_copy(update={"updated_at": utc_now()}, deep=True)
        with self._lock:
            self._push_tokens_by_device[stored.device_id] = stored
        return stored.model_copy(deep=True)

    def get_push_token_by_device(self, device_id: str) -> Optional[PushToken]:
        with self._lock:
            token = self._push_tokens_by_device.get(device_id)
        return token.model_copy(deep=True) if token else None

    def delete_push_token_by_device(self, device_id: str) -> None:
        with self._lock:
            self._push_tokens_by_device.pop(device_id, None)


class SQLiteDeviceRepository:
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
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                public_key TEXT NOT NULL,
                state TEXT NOT NULL,
                last_seen_at TEXT,
                revoked_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._execute("CREATE INDEX IF NOT EXISTS idx_devices_user ON devices(user_id)")
        self._execute("CREATE INDEX IF NOT EXISTS idx_devices_org ON devices(organization_id)")
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS pairing_invitations (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL,
                trusted_contact_user_id TEXT NOT NULL,
                created_by_user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                used_by_device_id TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS device_sessions (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                last_used_at TEXT
            )
            """
        )
        self._execute("CREATE INDEX IF NOT EXISTS idx_device_sessions_device ON device_sessions(device_id)")
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS push_tokens (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    # devices

    def create_device(self, device: Device) -> Device:
        self._execute(
            """
            INSERT INTO devices (
                id, organization_id, user_id, platform, public_key, state,
                last_seen_at, revoked_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._device_params(device),
        )
        return device

    def update_device(self, device: Device) -> Device:
        stored = device.model_copy(update={"updated_at": utc_now()}, deep=True)
        self._execute(
            """
            UPDATE devices SET
                organization_id = ?, user_id = ?, platform = ?, public_key = ?, state = ?,
                last_seen_at = ?, revoked_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                stored.organization_id,
                stored.user_id,
                stored.platform.value,
                stored.public_key,
                stored.state.value,
                stored.last_seen_at.isoformat() if stored.last_seen_at else None,
                stored.revoked_at.isoformat() if stored.revoked_at else None,
                stored.updated_at.isoformat(),
                stored.id,
            ),
        )
        return stored

    def get_device(self, device_id: str) -> Optional[Device]:
        row = self._execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        return self._row_to_device(row) if row else None

    def list_devices_by_user(self, user_id: str) -> list[Device]:
        rows = self._execute(
            "SELECT * FROM devices WHERE user_id = ? ORDER BY created_at ASC", (user_id,)
        ).fetchall()
        return [self._row_to_device(row) for row in rows]

    def list_devices_by_organization(self, organization_id: str) -> list[Device]:
        rows = self._execute(
            "SELECT * FROM devices WHERE organization_id = ? ORDER BY created_at ASC", (organization_id,)
        ).fetchall()
        return [self._row_to_device(row) for row in rows]

    def _device_params(self, device: Device) -> tuple:
        return (
            device.id,
            device.organization_id,
            device.user_id,
            device.platform.value,
            device.public_key,
            device.state.value,
            device.last_seen_at.isoformat() if device.last_seen_at else None,
            device.revoked_at.isoformat() if device.revoked_at else None,
            device.created_at.isoformat(),
            device.updated_at.isoformat(),
        )

    def _row_to_device(self, row: sqlite3.Row) -> Device:
        data = dict(row)
        for key in ("last_seen_at", "revoked_at", "created_at", "updated_at"):
            if data.get(key):
                data[key] = data[key].replace("Z", "+00:00")
        return Device.model_validate(data)

    # pairing invitations

    def create_invitation(self, invitation: PairingInvitation) -> PairingInvitation:
        self._execute(
            """
            INSERT INTO pairing_invitations (
                id, organization_id, trusted_contact_user_id, created_by_user_id, token_hash,
                status, expires_at, used_at, used_by_device_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._invitation_params(invitation),
        )
        return invitation

    def update_invitation(self, invitation: PairingInvitation) -> PairingInvitation:
        self._execute(
            """
            UPDATE pairing_invitations SET
                status = ?, used_at = ?, used_by_device_id = ?
            WHERE id = ?
            """,
            (
                invitation.status.value,
                invitation.used_at.isoformat() if invitation.used_at else None,
                invitation.used_by_device_id,
                invitation.id,
            ),
        )
        return invitation

    def get_invitation(self, invitation_id: str) -> Optional[PairingInvitation]:
        row = self._execute(
            "SELECT * FROM pairing_invitations WHERE id = ?", (invitation_id,)
        ).fetchone()
        return self._row_to_invitation(row) if row else None

    def get_invitation_by_token_hash(self, token_hash: str) -> Optional[PairingInvitation]:
        row = self._execute(
            "SELECT * FROM pairing_invitations WHERE token_hash = ?", (token_hash,)
        ).fetchone()
        return self._row_to_invitation(row) if row else None

    def _invitation_params(self, invitation: PairingInvitation) -> tuple:
        return (
            invitation.id,
            invitation.organization_id,
            invitation.trusted_contact_user_id,
            invitation.created_by_user_id,
            invitation.token_hash,
            invitation.status.value,
            invitation.expires_at.isoformat(),
            invitation.used_at.isoformat() if invitation.used_at else None,
            invitation.used_by_device_id,
            invitation.created_at.isoformat(),
        )

    def _row_to_invitation(self, row: sqlite3.Row) -> PairingInvitation:
        data = dict(row)
        for key in ("expires_at", "used_at", "created_at"):
            if data.get(key):
                data[key] = data[key].replace("Z", "+00:00")
        return PairingInvitation.model_validate(data)

    # device sessions

    def create_session(self, session: DeviceSession) -> DeviceSession:
        self._execute(
            """
            INSERT INTO device_sessions (
                id, device_id, issued_at, expires_at, revoked_at, last_used_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            self._session_params(session),
        )
        return session

    def update_session(self, session: DeviceSession) -> DeviceSession:
        self._execute(
            """
            UPDATE device_sessions SET
                expires_at = ?, revoked_at = ?, last_used_at = ?
            WHERE id = ?
            """,
            (
                session.expires_at.isoformat(),
                session.revoked_at.isoformat() if session.revoked_at else None,
                session.last_used_at.isoformat() if session.last_used_at else None,
                session.id,
            ),
        )
        return session

    def get_session(self, session_id: str) -> Optional[DeviceSession]:
        row = self._execute("SELECT * FROM device_sessions WHERE id = ?", (session_id,)).fetchone()
        return self._row_to_session(row) if row else None

    def list_sessions_by_device(self, device_id: str) -> list[DeviceSession]:
        rows = self._execute(
            "SELECT * FROM device_sessions WHERE device_id = ? ORDER BY issued_at ASC", (device_id,)
        ).fetchall()
        return [self._row_to_session(row) for row in rows]

    def _session_params(self, session: DeviceSession) -> tuple:
        return (
            session.id,
            session.device_id,
            session.issued_at.isoformat(),
            session.expires_at.isoformat(),
            session.revoked_at.isoformat() if session.revoked_at else None,
            session.last_used_at.isoformat() if session.last_used_at else None,
        )

    def _row_to_session(self, row: sqlite3.Row) -> DeviceSession:
        data = dict(row)
        for key in ("issued_at", "expires_at", "revoked_at", "last_used_at"):
            if data.get(key):
                data[key] = data[key].replace("Z", "+00:00")
        return DeviceSession.model_validate(data)

    # push tokens

    def upsert_push_token(self, token: PushToken) -> PushToken:
        stored = token.model_copy(update={"updated_at": utc_now()}, deep=True)
        self._execute(
            """
            INSERT INTO push_tokens (id, device_id, provider, token, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET
                token=excluded.token, provider=excluded.provider, updated_at=excluded.updated_at
            """,
            (
                stored.id,
                stored.device_id,
                stored.provider.value,
                stored.token,
                stored.created_at.isoformat(),
                stored.updated_at.isoformat(),
            ),
        )
        return stored

    def get_push_token_by_device(self, device_id: str) -> Optional[PushToken]:
        row = self._execute(
            "SELECT * FROM push_tokens WHERE device_id = ?", (device_id,)
        ).fetchone()
        return self._row_to_push_token(row) if row else None

    def delete_push_token_by_device(self, device_id: str) -> None:
        self._execute("DELETE FROM push_tokens WHERE device_id = ?", (device_id,))

    def _row_to_push_token(self, row: sqlite3.Row) -> PushToken:
        data = dict(row)
        for key in ("created_at", "updated_at"):
            if data.get(key):
                data[key] = data[key].replace("Z", "+00:00")
        return PushToken.model_validate(data)


_repository: DeviceRepository | None = None


def create_device_repository() -> DeviceRepository:
    if config.storage_backend == "sqlite":
        return SQLiteDeviceRepository()
    return InMemoryDeviceRepository()


def get_device_repository() -> DeviceRepository:
    global _repository
    if _repository is None:
        _repository = create_device_repository()
    return _repository


def reset_device_repository_for_tests(repository: DeviceRepository | None = None) -> DeviceRepository:
    global _repository
    _repository = repository or InMemoryDeviceRepository()
    return _repository
