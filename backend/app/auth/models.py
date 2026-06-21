from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class AuthEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    GOOGLE_LOGIN_STARTED = "google_login_started"
    GOOGLE_LOGIN_SUCCESS = "google_login_success"
    GOOGLE_LOGIN_FAILED = "google_login_failed"
    LOGOUT = "logout"
    MFA_SETUP_STARTED = "mfa_setup_started"
    MFA_ENABLED = "mfa_enabled"
    MFA_FAILED = "mfa_failed"
    PASSWORD_CHANGED = "password_changed"
    ADMIN_CREATED = "admin_created"
    ACCOUNT_LOCKED = "account_locked"


class AuthUser(BaseModel):
    id: str = Field(default_factory=lambda: new_id("user"))
    email: str = Field(min_length=3, max_length=254)
    password_hash: Optional[str] = None
    full_name: str = Field(min_length=1, max_length=160)
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    is_admin: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_login_at: Optional[datetime] = None

    @property
    def normalized_email(self) -> str:
        return self.email.lower().strip()


class OAuthAccount(BaseModel):
    id: str = Field(default_factory=lambda: new_id("oauth"))
    user_id: str
    provider: str = Field(min_length=1, max_length=80)
    provider_user_id: str = Field(min_length=1, max_length=180)
    provider_email: str = Field(min_length=3, max_length=254)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class AuthAuditLog(BaseModel):
    id: str = Field(default_factory=lambda: new_id("auth-audit"))
    user_id: Optional[str] = None
    email: Optional[str] = Field(default=None, max_length=254)
    event_type: AuthEventType
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    reason: Optional[str] = Field(default=None, max_length=240)
    created_at: datetime = Field(default_factory=utc_now)


class PublicUser(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_admin: bool
    mfa_enabled: bool

    @classmethod
    def from_user(cls, user: AuthUser) -> "PublicUser":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_admin=user.is_admin,
            mfa_enabled=user.mfa_enabled,
        )
