from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Optional, Protocol

from app.auth.crypto import normalize_email
from app.auth.models import AuthAuditLog, AuthUser, OAuthAccount, utc_now
from app.core.config import config


class AuthRepository(Protocol):
    def create_user(self, user: AuthUser) -> AuthUser: ...
    def update_user(self, user: AuthUser) -> AuthUser: ...
    def get_user_by_email(self, email: str) -> Optional[AuthUser]: ...
    def get_user_by_id(self, user_id: str) -> Optional[AuthUser]: ...
    def list_users(self) -> list[AuthUser]: ...
    def save_oauth_account(self, account: OAuthAccount) -> OAuthAccount: ...
    def get_oauth_account(self, provider: str, provider_user_id: str) -> Optional[OAuthAccount]: ...
    def append_audit_log(self, log: AuthAuditLog) -> AuthAuditLog: ...
    def list_audit_logs(self, limit: int = 100) -> list[AuthAuditLog]: ...


class InMemoryAuthRepository:
    def __init__(self) -> None:
        self._users: dict[str, AuthUser] = {}
        self._users_by_email: dict[str, str] = {}
        self._oauth_accounts: dict[tuple[str, str], OAuthAccount] = {}
        self._audit_logs: list[AuthAuditLog] = []
        self._lock = threading.RLock()

    def create_user(self, user: AuthUser) -> AuthUser:
        stored = user.model_copy(update={"email": normalize_email(user.email), "updated_at": utc_now()}, deep=True)
        with self._lock:
            email = normalize_email(stored.email)
            if email in self._users_by_email:
                raise ValueError("User already exists.")
            self._users[stored.id] = stored
            self._users_by_email[email] = stored.id
        return stored.model_copy(deep=True)

    def update_user(self, user: AuthUser) -> AuthUser:
        stored = user.model_copy(update={"email": normalize_email(user.email), "updated_at": utc_now()}, deep=True)
        with self._lock:
            existing = self._users.get(stored.id)
            if not existing:
                raise LookupError("User not found.")
            old_email = normalize_email(existing.email)
            new_email = normalize_email(stored.email)
            if old_email != new_email and new_email in self._users_by_email:
                raise ValueError("User already exists.")
            self._users_by_email.pop(old_email, None)
            self._users[stored.id] = stored
            self._users_by_email[new_email] = stored.id
        return stored.model_copy(deep=True)

    def get_user_by_email(self, email: str) -> Optional[AuthUser]:
        with self._lock:
            user_id = self._users_by_email.get(normalize_email(email))
            user = self._users.get(user_id) if user_id else None
        return user.model_copy(deep=True) if user else None

    def get_user_by_id(self, user_id: str) -> Optional[AuthUser]:
        with self._lock:
            user = self._users.get(user_id)
        return user.model_copy(deep=True) if user else None

    def list_users(self) -> list[AuthUser]:
        with self._lock:
            users = list(self._users.values())
        return [user.model_copy(deep=True) for user in sorted(users, key=lambda item: item.created_at)]

    def save_oauth_account(self, account: OAuthAccount) -> OAuthAccount:
        stored = account.model_copy(update={"provider_email": normalize_email(account.provider_email), "updated_at": utc_now()}, deep=True)
        with self._lock:
            self._oauth_accounts[(stored.provider, stored.provider_user_id)] = stored
        return stored.model_copy(deep=True)

    def get_oauth_account(self, provider: str, provider_user_id: str) -> Optional[OAuthAccount]:
        with self._lock:
            account = self._oauth_accounts.get((provider, provider_user_id))
        return account.model_copy(deep=True) if account else None

    def append_audit_log(self, log: AuthAuditLog) -> AuthAuditLog:
        stored = log.model_copy(update={"email": normalize_email(log.email) if log.email else None}, deep=True)
        with self._lock:
            self._audit_logs.append(stored)
        return stored.model_copy(deep=True)

    def list_audit_logs(self, limit: int = 100) -> list[AuthAuditLog]:
        with self._lock:
            logs = list(self._audit_logs)
        return [log.model_copy(deep=True) for log in sorted(logs, key=lambda item: item.created_at, reverse=True)[:limit]]


class SQLiteAuthRepository:
    def __init__(self, sqlite_url: str | None = None) -> None:
        self._path = self._sqlite_path(sqlite_url or config.sqlite_database_url)
        if self._path != ":memory:":
            Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._ensure_schema()

    def _sqlite_path(self, sqlite_url: str) -> str:
        prefix = "sqlite:///"
        if sqlite_url == "sqlite:///:memory:":
            return ":memory:"
        if sqlite_url.startswith(prefix):
            path = sqlite_url[len(prefix) :]
        elif sqlite_url.startswith("sqlite:"):
            path = sqlite_url.split(":", 1)[1].lstrip("/")
        else:
            path = sqlite_url
        return path or "cyberalerta_guardian.db"

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            return cursor

    def _ensure_schema(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS users (
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
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS oauth_accounts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                provider_user_id TEXT NOT NULL,
                provider_email TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(provider, provider_user_id)
            )
            """
        )
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS auth_audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                email TEXT,
                event_type TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                success INTEGER NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

    def create_user(self, user: AuthUser) -> AuthUser:
        stored = user.model_copy(update={"email": normalize_email(user.email), "updated_at": utc_now()}, deep=True)
        self._execute(
            """
            INSERT INTO users (
                id, email, password_hash, full_name, role, is_active, is_admin,
                mfa_enabled, mfa_secret, created_at, updated_at, last_login_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            self._user_params(stored),
        )
        return stored

    def update_user(self, user: AuthUser) -> AuthUser:
        stored = user.model_copy(update={"email": normalize_email(user.email), "updated_at": utc_now()}, deep=True)
        self._execute(
            """
            UPDATE users SET
                email = ?, password_hash = ?, full_name = ?, role = ?, is_active = ?,
                is_admin = ?, mfa_enabled = ?, mfa_secret = ?, updated_at = ?, last_login_at = ?
            WHERE id = ?
            """,
            (
                stored.email,
                stored.password_hash,
                stored.full_name,
                stored.role.value,
                int(stored.is_active),
                int(stored.is_admin),
                int(stored.mfa_enabled),
                stored.mfa_secret,
                stored.updated_at.isoformat(),
                stored.last_login_at.isoformat() if stored.last_login_at else None,
                stored.id,
            ),
        )
        return stored

    def get_user_by_email(self, email: str) -> Optional[AuthUser]:
        row = self._execute("SELECT * FROM users WHERE email = ?", (normalize_email(email),)).fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[AuthUser]:
        row = self._execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._row_to_user(row) if row else None

    def list_users(self) -> list[AuthUser]:
        rows = self._execute("SELECT * FROM users ORDER BY created_at ASC").fetchall()
        return [self._row_to_user(row) for row in rows]

    def save_oauth_account(self, account: OAuthAccount) -> OAuthAccount:
        stored = account.model_copy(update={"provider_email": normalize_email(account.provider_email), "updated_at": utc_now()}, deep=True)
        self._execute(
            """
            INSERT INTO oauth_accounts (id, user_id, provider, provider_user_id, provider_email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider, provider_user_id) DO UPDATE SET
                user_id=excluded.user_id,
                provider_email=excluded.provider_email,
                updated_at=excluded.updated_at
            """,
            (
                stored.id,
                stored.user_id,
                stored.provider,
                stored.provider_user_id,
                stored.provider_email,
                stored.created_at.isoformat(),
                stored.updated_at.isoformat(),
            ),
        )
        return stored

    def get_oauth_account(self, provider: str, provider_user_id: str) -> Optional[OAuthAccount]:
        row = self._execute(
            "SELECT * FROM oauth_accounts WHERE provider = ? AND provider_user_id = ?",
            (provider, provider_user_id),
        ).fetchone()
        return OAuthAccount.model_validate(dict(row)) if row else None

    def append_audit_log(self, log: AuthAuditLog) -> AuthAuditLog:
        stored = log.model_copy(update={"email": normalize_email(log.email) if log.email else None}, deep=True)
        self._execute(
            """
            INSERT INTO auth_audit_logs (id, user_id, email, event_type, ip_address, user_agent, success, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stored.id,
                stored.user_id,
                stored.email,
                stored.event_type.value,
                stored.ip_address,
                stored.user_agent,
                int(stored.success),
                stored.reason,
                stored.created_at.isoformat(),
            ),
        )
        return stored

    def list_audit_logs(self, limit: int = 100) -> list[AuthAuditLog]:
        rows = self._execute(
            "SELECT * FROM auth_audit_logs ORDER BY created_at DESC LIMIT ?",
            (int(limit),),
        ).fetchall()
        return [AuthAuditLog.model_validate(dict(row)) for row in rows]

    def _user_params(self, user: AuthUser) -> tuple:
        return (
            user.id,
            user.email,
            user.password_hash,
            user.full_name,
            user.role.value,
            int(user.is_active),
            int(user.is_admin),
            int(user.mfa_enabled),
            user.mfa_secret,
            user.created_at.isoformat(),
            user.updated_at.isoformat(),
            user.last_login_at.isoformat() if user.last_login_at else None,
        )

    def _row_to_user(self, row: sqlite3.Row) -> AuthUser:
        data = dict(row)
        for key in ("is_active", "is_admin", "mfa_enabled"):
            data[key] = bool(data[key])
        for key in ("created_at", "updated_at", "last_login_at"):
            if data.get(key):
                data[key] = data[key].replace("Z", "+00:00")
        return AuthUser.model_validate(data)


_repository: AuthRepository | None = None


def create_auth_repository() -> AuthRepository:
    if config.storage_backend == "sqlite":
        return SQLiteAuthRepository()
    return InMemoryAuthRepository()


def get_auth_repository() -> AuthRepository:
    global _repository
    if _repository is None:
        _repository = create_auth_repository()
    return _repository


def reset_auth_repository_for_tests(repository: AuthRepository | None = None) -> AuthRepository:
    global _repository
    _repository = repository or InMemoryAuthRepository()
    return _repository
