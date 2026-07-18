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


class DevicePlatform(str, Enum):
    ANDROID = "android"
    WINDOWS = "windows"
    WEB = "web"


class DeviceState(str, Enum):
    """Plano Mestre v1.1, Secao 4.5 — estados recomendados de Dispositivo."""

    PENDING_PAIRING = "pending_pairing"
    ACTIVE = "active"
    REVOKED = "revoked"
    LOST = "lost"
    EXPIRED = "expired"


class PairingInvitationStatus(str, Enum):
    PENDING = "pending"
    USED = "used"
    EXPIRED = "expired"
    REVOKED = "revoked"


class PushProvider(str, Enum):
    FCM = "fcm"


class Device(BaseModel):
    """A paired client (Secao 6.2). ``user_id`` points at the AuthUser (role
    TRUSTED_CONTACT) that owns this device; ``public_key`` is the proof-of-
    possession key generated on-device during pairing, never a server secret."""

    id: str = Field(default_factory=lambda: new_id("device"))
    organization_id: str
    user_id: str
    platform: DevicePlatform
    public_key: str = Field(min_length=1, max_length=2000)
    state: DeviceState = DeviceState.PENDING_PAIRING
    last_seen_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PairingInvitation(BaseModel):
    """Single-use invite (Secao 6.2). ``token_hash`` is an HMAC/hash of the
    bearer token handed to the contact — the raw token is never persisted,
    mirroring how AuthUser.password_hash never stores a plaintext password."""

    id: str = Field(default_factory=lambda: new_id("pairing"))
    organization_id: str
    trusted_contact_user_id: str
    created_by_user_id: str
    token_hash: str = Field(min_length=1, max_length=128)
    status: PairingInvitationStatus = PairingInvitationStatus.PENDING
    expires_at: datetime
    used_at: Optional[datetime] = None
    used_by_device_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)


class DeviceSession(BaseModel):
    """Revoking a device must invalidate its sessions even if the device is
    offline (Secao 6.2) — ``revoked_at`` is the authority checked on each
    request, independent of whether the device has synced yet."""

    id: str = Field(default_factory=lambda: new_id("devsess"))
    device_id: str
    issued_at: datetime = Field(default_factory=utc_now)
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class PushToken(BaseModel):
    id: str = Field(default_factory=lambda: new_id("pushtok"))
    device_id: str
    provider: PushProvider = PushProvider.FCM
    token: str = Field(min_length=1, max_length=4000)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
