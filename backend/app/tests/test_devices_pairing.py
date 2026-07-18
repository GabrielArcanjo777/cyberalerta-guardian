"""Sprint 2, Unidade 3 (Plano Mestre v1.1, Secao 6.2/6.5/8.4) — pairing flow:
invitation creation, single-use redemption, and the org isolation test the
plan mandates from this sprint onward (Secao 6.5: cross-org access is 404,
never 403). Push-token registration/ACK/ACTIVE transition are Unidade 4;
revocation is Unidade 5.
"""

from __future__ import annotations

import hashlib
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.auth.models import UserRole
from app.auth.repository import get_auth_repository, reset_auth_repository_for_tests
from app.auth.service import AuthService, auth_rate_limiter
from app.core.config import config
from app.devices.models import DeviceState, PairingInvitation, utc_now
from app.devices.repository import get_device_repository, reset_device_repository_for_tests
from app.devices.service import (
    PAIRING_CODE_LENGTH,
    PAIRING_MAX_ATTEMPTS,
    DeviceService,
    PairingInvitationExpiredError,
    pairing_rate_limiter,
)
from main import app

PASSWORD = "StrongPass!123"


@pytest.fixture(autouse=True)
def _reset_state():
    original_sensitive = config.auth_require_sensitive_routes
    reset_auth_repository_for_tests()
    reset_device_repository_for_tests()
    auth_rate_limiter.reset()
    pairing_rate_limiter.reset()
    config.auth_require_sensitive_routes = False
    yield
    reset_auth_repository_for_tests()
    reset_device_repository_for_tests()
    auth_rate_limiter.reset()
    pairing_rate_limiter.reset()
    config.auth_require_sensitive_routes = original_sensitive


def _auth_service() -> AuthService:
    return AuthService(get_auth_repository())


def _create_user(email: str, role: UserRole, organization_id: str | None):
    user = _auth_service().create_user(
        email=email,
        full_name=email.split("@", 1)[0].title(),
        password=PASSWORD,
        role=role,
    )
    return get_auth_repository().update_user(user.model_copy(update={"organization_id": organization_id}))


def _login(client: TestClient, email: str) -> TestClient:
    response = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return client


def _create_operator_and_contact(organization_id: str):
    operator = _create_user(f"admin-{organization_id}@example.com", UserRole.ADMIN, organization_id)
    contact = _create_user(f"contact-{organization_id}@example.com", UserRole.TRUSTED_CONTACT, organization_id)
    return operator, contact


def test_create_pairing_invitation_never_persists_raw_token():
    operator, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), operator.email)

    response = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    raw_token = body["token"]
    assert raw_token

    stored = get_device_repository().get_invitation(body["invitation_id"])
    assert stored is not None
    assert stored.token_hash != raw_token
    assert raw_token not in stored.model_dump_json()


def test_create_pairing_invitation_rejects_target_from_another_organization():
    operator, _ = _create_operator_and_contact("org-a")
    _, contact_b = _create_operator_and_contact("org-b")
    client = _login(TestClient(app), operator.email)

    response = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact_b.id}
    )

    assert response.status_code == 404


def test_create_pairing_invitation_requires_operator_role():
    _create_user("viewer@example.com", UserRole.VIEWER, "org-a")
    _, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), "viewer@example.com")

    response = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    )

    assert response.status_code == 403


def test_create_pairing_invitation_requires_actor_to_have_organization():
    operator = _create_user("no-org-admin@example.com", UserRole.ADMIN, None)
    _, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), operator.email)

    response = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    )

    assert response.status_code == 422


def test_pair_device_with_valid_token_creates_pending_device_and_session():
    operator, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), operator.email)
    invitation = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    ).json()

    # Pairing itself is unauthenticated (public + token) — fresh client, no cookies.
    response = TestClient(app).post(
        "/devices/pair",
        json={"token": invitation["token"], "platform": "android", "public_key": "pubkey-abc"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["state"] == DeviceState.PENDING_PAIRING.value
    device = get_device_repository().get_device(body["device_id"])
    assert device.organization_id == "org-a"
    assert device.user_id == contact.id
    session = get_device_repository().get_session(body["session_id"])
    assert session.device_id == device.id
    assert session.revoked_at is None


def test_pair_device_rejects_reused_token():
    operator, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), operator.email)
    invitation = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    ).json()
    pair_body = {"token": invitation["token"], "platform": "android", "public_key": "pubkey-abc"}

    first = TestClient(app).post("/devices/pair", json=pair_body)
    assert first.status_code == 200

    second = TestClient(app).post("/devices/pair", json=pair_body)
    assert second.status_code == 404


def test_pair_device_rejects_unknown_token():
    response = TestClient(app).post(
        "/devices/pair",
        json={"token": "not-a-real-token", "platform": "android", "public_key": "pubkey-abc"},
    )
    assert response.status_code == 404


def test_pairing_invitation_token_is_a_short_numeric_code():
    operator, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), operator.email)

    response = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    )

    token = response.json()["token"]
    assert token.isdigit()
    assert len(token) == PAIRING_CODE_LENGTH


def test_pair_device_locks_out_client_after_too_many_failed_attempts():
    operator, contact = _create_operator_and_contact("org-a")
    client = _login(TestClient(app), operator.email)
    invitation = client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    ).json()

    guesser = TestClient(app)
    for _ in range(PAIRING_MAX_ATTEMPTS):
        bad = guesser.post(
            "/devices/pair",
            json={"token": "00000000", "platform": "android", "public_key": "pubkey-abc"},
        )
        assert bad.status_code == 404

    # Even the real code is now rejected — the client is locked out, not the code.
    locked_out = guesser.post(
        "/devices/pair",
        json={"token": invitation["token"], "platform": "android", "public_key": "pubkey-abc"},
    )
    assert locked_out.status_code == 429


def test_pairing_service_rejects_expired_token_and_marks_invitation_expired():
    from app.devices.models import PairingInvitationStatus

    repo = get_device_repository()
    invitation = repo.create_invitation(
        PairingInvitation(
            organization_id="org-a",
            trusted_contact_user_id="user-contact",
            created_by_user_id="user-admin",
            token_hash=hashlib.sha256(b"expired-token").hexdigest(),
            expires_at=utc_now() - timedelta(minutes=1),
        )
    )

    with pytest.raises(PairingInvitationExpiredError):
        DeviceService(repository=repo).pair_device(
            token="expired-token", platform="android", public_key="pubkey-abc"
        )

    assert repo.get_invitation(invitation.id).status == PairingInvitationStatus.EXPIRED


def test_get_device_cross_organization_returns_404_not_403():
    operator_a, contact_a = _create_operator_and_contact("org-a")
    operator_b, _ = _create_operator_and_contact("org-b")

    invitation = _login(TestClient(app), operator_a.email).post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact_a.id}
    ).json()
    paired = TestClient(app).post(
        "/devices/pair",
        json={"token": invitation["token"], "platform": "android", "public_key": "pubkey-abc"},
    ).json()
    device_id = paired["device_id"]

    # Org A can see its own device.
    own_view = _login(TestClient(app), operator_a.email).get(f"/devices/{device_id}")
    assert own_view.status_code == 200

    # Org B must get 404, never 403 — it should not even learn the device exists.
    cross_org_view = _login(TestClient(app), operator_b.email).get(f"/devices/{device_id}")
    assert cross_org_view.status_code == 404


def test_list_devices_scoped_to_actor_organization():
    operator_a, contact_a = _create_operator_and_contact("org-a")
    operator_b, contact_b = _create_operator_and_contact("org-b")

    for operator, contact in ((operator_a, contact_a), (operator_b, contact_b)):
        invitation = _login(TestClient(app), operator.email).post(
            "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
        ).json()
        TestClient(app).post(
            "/devices/pair",
            json={"token": invitation["token"], "platform": "android", "public_key": "pubkey-abc"},
        )

    listing_a = _login(TestClient(app), operator_a.email).get("/devices").json()
    listing_b = _login(TestClient(app), operator_b.email).get("/devices").json()

    assert len(listing_a["devices"]) == 1
    assert len(listing_b["devices"]) == 1
    assert listing_a["devices"][0]["user_id"] == contact_a.id
    assert listing_b["devices"][0]["user_id"] == contact_b.id
