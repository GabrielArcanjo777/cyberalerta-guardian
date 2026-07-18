"""Pairing + revocation (Plano Mestre v1.1, Secao 6.2, Secao 8.4 / Sprint 2
Unidades 3 e 5): invitation creation, single-use redemption, org-scoped
device lookup, and revoking a device's access. Push-token registration, the
test push and the ACK/ACTIVE transition are Unidade 4.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from datetime import timedelta
from threading import Lock
from typing import Optional

from fastapi import Request

from app.auth.models import AuthUser, UserRole
from app.auth.repository import AuthRepository, get_auth_repository
from app.core.config import config
from app.core.logging import get_logger, structured_log
from app.devices.models import (
    Device,
    DevicePlatform,
    DeviceSession,
    DeviceState,
    PairingInvitation,
    PairingInvitationStatus,
    utc_now,
)
from app.devices.repository import DeviceRepository, get_device_repository

logger = get_logger("devices")

# Short enough to type/copy on a phone by hand (Sprint 5 will add a QR
# scanner and make this moot). Brute force is bounded by
# PairingRateLimiter below, not by the code's own entropy.
DEFAULT_INVITATION_TTL_MINUTES = 10
PAIRING_CODE_LENGTH = 8
PAIRING_MAX_ATTEMPTS = 5
PAIRING_LOCKOUT_WINDOW_SECONDS = 300
DEVICE_SESSION_TTL_DAYS = 30


def _hash_token(token: str) -> str:
    # Unlike a 256-bit urlsafe token, an 8-digit code has too little entropy
    # for an unkeyed digest to rely on secrecy alone — PairingRateLimiter is
    # what actually makes guessing infeasible. The hash here only avoids
    # persisting the raw code at rest, mirroring body_hash elsewhere.
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _generate_pairing_code() -> str:
    return f"{secrets.randbelow(10 ** PAIRING_CODE_LENGTH):0{PAIRING_CODE_LENGTH}d}"


def _client_ip(request: Optional[Request]) -> Optional[str]:
    if request is None:
        return None
    direct = request.client.host if request.client and request.client.host else None
    forwarded = request.headers.get("X-Forwarded-For")
    # Trust X-Forwarded-For only from a configured trusted proxy, same rule
    # as auth's login rate limiter, so the lockout key cannot be spoofed.
    if forwarded and direct and direct in config.trusted_webhook_ips:
        return forwarded.split(",", 1)[0].strip()
    return direct


class PairingRateLimiter:
    """Failure-lockout limiter for /devices/pair, keyed by client IP —
    mirrors AuthRateLimiter in app/auth/service.py. Needed because the short
    numeric pairing code (PAIRING_CODE_LENGTH) is only safe against
    brute-force guessing when attempts are throttled like this."""

    def __init__(self) -> None:
        self._failures: dict[str, list[float]] = {}
        self._lock = Lock()

    def is_blocked(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - PAIRING_LOCKOUT_WINDOW_SECONDS
        with self._lock:
            hits = [item for item in self._failures.get(key, []) if item >= cutoff]
            self._failures[key] = hits
            return len(hits) >= PAIRING_MAX_ATTEMPTS

    def record_failure(self, key: str) -> None:
        with self._lock:
            self._failures.setdefault(key, []).append(time.monotonic())

    def clear(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._failures.clear()


pairing_rate_limiter = PairingRateLimiter()


class PairingInvitationTargetError(Exception):
    """Target trusted contact does not exist, is not TRUSTED_CONTACT, or
    belongs to a different organization than the requesting actor."""


class PairingInvitationInvalidError(Exception):
    """Token unknown, already used, or revoked."""


class PairingInvitationExpiredError(Exception):
    pass


class PairingAttemptsExceededError(Exception):
    """Too many failed /devices/pair guesses from this client recently."""


class DeviceNotFoundError(Exception):
    """Device does not exist, or exists in a different organization —
    callers must map this to 404 (never 403) per Plano Mestre Secao 6.5."""


class ActorOrganizationRequiredError(Exception):
    """Actor has no organization_id yet — onboarding (Secao 4.1) assigns one
    before device pairing; there is no implicit "no org" bucket to fall into."""


def _require_organization_id(actor: AuthUser) -> str:
    if not actor.organization_id:
        raise ActorOrganizationRequiredError("Actor is not assigned to an organization.")
    return actor.organization_id


class DeviceService:
    def __init__(
        self,
        repository: Optional[DeviceRepository] = None,
        auth_repository: Optional[AuthRepository] = None,
    ) -> None:
        self.repository = repository or get_device_repository()
        self.auth_repository = auth_repository or get_auth_repository()

    def create_pairing_invitation(
        self,
        *,
        actor: AuthUser,
        trusted_contact_user_id: str,
        ttl_minutes: int = DEFAULT_INVITATION_TTL_MINUTES,
    ) -> tuple[PairingInvitation, str]:
        organization_id = _require_organization_id(actor)
        target = self.auth_repository.get_user_by_id(trusted_contact_user_id)
        if (
            target is None
            or target.role != UserRole.TRUSTED_CONTACT
            or target.organization_id != organization_id
        ):
            # Same failure for "doesn't exist" and "exists in another org" —
            # do not let a 422 vs 404 split leak cross-org existence.
            raise PairingInvitationTargetError("Trusted contact not found.")

        raw_token = _generate_pairing_code()
        invitation = self.repository.create_invitation(
            PairingInvitation(
                organization_id=organization_id,
                trusted_contact_user_id=target.id,
                created_by_user_id=actor.id,
                token_hash=_hash_token(raw_token),
                expires_at=utc_now() + timedelta(minutes=ttl_minutes),
            )
        )
        return invitation, raw_token

    def pair_device(
        self,
        *,
        token: str,
        platform: DevicePlatform,
        public_key: str,
        request: Optional[Request] = None,
    ) -> tuple[Device, DeviceSession]:
        rate_limit_key = _client_ip(request) or "unknown"
        if pairing_rate_limiter.is_blocked(rate_limit_key):
            raise PairingAttemptsExceededError("Too many pairing attempts. Try again later.")

        invitation = self.repository.get_invitation_by_token_hash(_hash_token(token))
        if invitation is None or invitation.status != PairingInvitationStatus.PENDING:
            pairing_rate_limiter.record_failure(rate_limit_key)
            raise PairingInvitationInvalidError("Invalid or already-used pairing token.")
        if invitation.expires_at < utc_now():
            self.repository.update_invitation(
                invitation.model_copy(update={"status": PairingInvitationStatus.EXPIRED})
            )
            pairing_rate_limiter.record_failure(rate_limit_key)
            raise PairingInvitationExpiredError("Pairing token expired.")

        pairing_rate_limiter.clear(rate_limit_key)
        device = self.repository.create_device(
            Device(
                organization_id=invitation.organization_id,
                user_id=invitation.trusted_contact_user_id,
                platform=platform,
                public_key=public_key,
                state=DeviceState.PENDING_PAIRING,
            )
        )
        self.repository.update_invitation(
            invitation.model_copy(
                update={
                    "status": PairingInvitationStatus.USED,
                    "used_at": utc_now(),
                    "used_by_device_id": device.id,
                }
            )
        )
        session = self.repository.create_session(
            DeviceSession(device_id=device.id, expires_at=utc_now() + timedelta(days=DEVICE_SESSION_TTL_DAYS))
        )
        return device, session

    def list_devices(self, *, actor: AuthUser) -> list[Device]:
        organization_id = _require_organization_id(actor)
        return self.repository.list_devices_by_organization(organization_id)

    def get_device(self, *, actor: AuthUser, device_id: str) -> Device:
        organization_id = _require_organization_id(actor)
        device = self.repository.get_device(device_id)
        if device is None or device.organization_id != organization_id:
            raise DeviceNotFoundError("Device not found.")
        return device

    def revoke_device(self, *, actor: AuthUser, device_id: str) -> Device:
        """Revocation must work even if the device never comes back online
        (Secao 6.2): flip the device state, revoke every session by id (not
        just rely on the device-state check in require_device_session — this
        is the same defense-in-depth as the safety gates), and drop the push
        token so a stale send can't reach it. Idempotent: revoking an
        already-revoked device is a no-op, not an error."""
        device = self.get_device(actor=actor, device_id=device_id)

        if device.state != DeviceState.REVOKED:
            device = self.repository.update_device(
                device.model_copy(update={"state": DeviceState.REVOKED, "revoked_at": utc_now()})
            )

        for session in self.repository.list_sessions_by_device(device.id):
            if session.revoked_at is None:
                self.repository.update_session(session.model_copy(update={"revoked_at": utc_now()}))

        self.repository.delete_push_token_by_device(device.id)

        structured_log(
            logger,
            "device_revoked",
            device_id=device.id,
            organization_id=device.organization_id,
            actor_id=actor.id,
        )
        return device
