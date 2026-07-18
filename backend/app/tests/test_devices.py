"""Sprint 2, Unidade 2 (Plano Mestre v1.1, Secao 6.2/8.4) — devices module
foundation: Device, PairingInvitation, DeviceSession and PushToken models plus
their repository, in memory and SQLite. No endpoint wiring yet (Unidade 3);
this only proves the persistence layer the pairing flow will sit on top of.
"""

from __future__ import annotations

from datetime import timedelta

from app.devices.models import (
    Device,
    DevicePlatform,
    DeviceSession,
    DeviceState,
    PairingInvitation,
    PairingInvitationStatus,
    PushToken,
    utc_now,
)
from app.devices.repository import InMemoryDeviceRepository, SQLiteDeviceRepository


def _sqlite_url(path: str) -> str:
    # Windows drive letters ("D:\...") get misparsed as a URL scheme otherwise.
    return "sqlite:///" + path.replace("\\", "/")


def _device(**overrides) -> Device:
    defaults = dict(
        organization_id="org-arcanjo",
        user_id="user-gabriel",
        platform=DevicePlatform.ANDROID,
        public_key="pubkey-abc123",
    )
    defaults.update(overrides)
    return Device(**defaults)


# ---------------------------------------------------------------------------
# In-memory
# ---------------------------------------------------------------------------


def test_in_memory_device_lifecycle_pairing_to_active_to_revoked():
    repo = InMemoryDeviceRepository()
    device = repo.create_device(_device())
    assert device.state == DeviceState.PENDING_PAIRING

    activated = repo.update_device(device.model_copy(update={"state": DeviceState.ACTIVE}))
    assert activated.state == DeviceState.ACTIVE
    assert repo.get_device(device.id).state == DeviceState.ACTIVE

    revoked_at = utc_now()
    revoked = repo.update_device(
        activated.model_copy(update={"state": DeviceState.REVOKED, "revoked_at": revoked_at})
    )
    assert revoked.state == DeviceState.REVOKED
    assert repo.get_device(device.id).revoked_at == revoked_at


def test_in_memory_devices_scoped_by_user_and_organization():
    repo = InMemoryDeviceRepository()
    device_a = repo.create_device(_device(organization_id="org-a", user_id="user-a"))
    device_b = repo.create_device(_device(organization_id="org-b", user_id="user-b"))

    assert [d.id for d in repo.list_devices_by_user("user-a")] == [device_a.id]
    assert [d.id for d in repo.list_devices_by_organization("org-b")] == [device_b.id]
    assert repo.list_devices_by_organization("org-a") != repo.list_devices_by_organization("org-b")


def test_in_memory_pairing_invitation_single_use_flow():
    repo = InMemoryDeviceRepository()
    invitation = repo.create_invitation(
        PairingInvitation(
            organization_id="org-arcanjo",
            trusted_contact_user_id="user-gabriel",
            created_by_user_id="user-admin",
            token_hash="hash-of-one-time-token",
            expires_at=utc_now() + timedelta(minutes=15),
        )
    )
    assert invitation.status == PairingInvitationStatus.PENDING
    assert repo.get_invitation_by_token_hash("hash-of-one-time-token").id == invitation.id

    device = repo.create_device(_device())
    used = repo.update_invitation(
        invitation.model_copy(
            update={
                "status": PairingInvitationStatus.USED,
                "used_at": utc_now(),
                "used_by_device_id": device.id,
            }
        )
    )
    assert used.status == PairingInvitationStatus.USED
    assert repo.get_invitation(invitation.id).used_by_device_id == device.id


def test_in_memory_device_session_revocation():
    repo = InMemoryDeviceRepository()
    device = repo.create_device(_device())
    session = repo.create_session(
        DeviceSession(device_id=device.id, expires_at=utc_now() + timedelta(days=7))
    )
    assert repo.get_session(session.id).revoked_at is None

    revoked = repo.update_session(session.model_copy(update={"revoked_at": utc_now()}))
    assert revoked.revoked_at is not None
    assert [s.id for s in repo.list_sessions_by_device(device.id)] == [session.id]


def test_in_memory_push_token_upsert_overwrites_previous_token():
    repo = InMemoryDeviceRepository()
    device = repo.create_device(_device())
    repo.upsert_push_token(PushToken(device_id=device.id, token="token-v1"))
    repo.upsert_push_token(PushToken(device_id=device.id, token="token-v2"))

    assert repo.get_push_token_by_device(device.id).token == "token-v2"

    repo.delete_push_token_by_device(device.id)
    assert repo.get_push_token_by_device(device.id) is None


# ---------------------------------------------------------------------------
# SQLite persistence
# ---------------------------------------------------------------------------


def test_sqlite_device_and_pairing_invitation_persist_across_reopen(tmp_path):
    db = _sqlite_url(str(tmp_path / "devices.db"))

    repo = SQLiteDeviceRepository(sqlite_url=db)
    device = repo.create_device(_device())
    invitation = repo.create_invitation(
        PairingInvitation(
            organization_id="org-arcanjo",
            trusted_contact_user_id="user-gabriel",
            created_by_user_id="user-admin",
            token_hash="hash-of-one-time-token",
            expires_at=utc_now() + timedelta(minutes=15),
        )
    )
    repo.update_invitation(
        invitation.model_copy(
            update={
                "status": PairingInvitationStatus.USED,
                "used_at": utc_now(),
                "used_by_device_id": device.id,
            }
        )
    )
    session = repo.create_session(
        DeviceSession(device_id=device.id, expires_at=utc_now() + timedelta(days=7))
    )
    repo.upsert_push_token(PushToken(device_id=device.id, token="token-v1"))

    reopened = SQLiteDeviceRepository(sqlite_url=db)
    assert reopened.get_device(device.id).platform == DevicePlatform.ANDROID
    fetched_invitation = reopened.get_invitation_by_token_hash("hash-of-one-time-token")
    assert fetched_invitation.status == PairingInvitationStatus.USED
    assert fetched_invitation.used_by_device_id == device.id
    assert reopened.get_session(session.id).device_id == device.id
    assert reopened.get_push_token_by_device(device.id).token == "token-v1"


def test_sqlite_devices_scoped_by_organization_across_reopen(tmp_path):
    db = _sqlite_url(str(tmp_path / "devices_org.db"))

    repo = SQLiteDeviceRepository(sqlite_url=db)
    device_a = repo.create_device(_device(organization_id="org-a", user_id="user-a"))
    device_b = repo.create_device(_device(organization_id="org-b", user_id="user-b"))

    reopened = SQLiteDeviceRepository(sqlite_url=db)
    assert [d.id for d in reopened.list_devices_by_organization("org-a")] == [device_a.id]
    assert [d.id for d in reopened.list_devices_by_organization("org-b")] == [device_b.id]


def test_sqlite_push_token_upsert_overwrites_previous_token(tmp_path):
    db = _sqlite_url(str(tmp_path / "push.db"))

    repo = SQLiteDeviceRepository(sqlite_url=db)
    device = repo.create_device(_device())
    repo.upsert_push_token(PushToken(device_id=device.id, token="token-v1"))
    repo.upsert_push_token(PushToken(device_id=device.id, token="token-v2"))

    reopened = SQLiteDeviceRepository(sqlite_url=db)
    assert reopened.get_push_token_by_device(device.id).token == "token-v2"
