"""Sprint 2, Unidade 5 (Plano Mestre v1.1, Secao 6.2/8.4/10.5) — revocation and
the Sprint 2 Definition of Done end-to-end scenario: convite -> pareamento ->
push de teste -> ACK -> device ACTIVE -> revogacao -> acesso perdido
imediatamente, mesmo com o device offline (revoked_at e checado a cada
request, nao depende do device "avisar" o servidor).
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.auth.models import UserRole
from app.auth.repository import get_auth_repository, reset_auth_repository_for_tests
from app.auth.service import AuthService, auth_rate_limiter
from app.core.config import config
from app.devices.device_auth import DEVICE_SESSION_HEADER
from app.devices.models import Device, DevicePlatform, DeviceSession, DeviceState, PushToken, utc_now
from app.devices.repository import get_device_repository, reset_device_repository_for_tests
from app.devices.service import DeviceNotFoundError, DeviceService, pairing_rate_limiter
from app.notifications.models import AlertState
from app.notifications.repository import reset_notification_repository_for_tests
from app.notifications.router import get_notification_service
from app.notifications.service import NotificationService
from main import app

PASSWORD = "StrongPass!123"


class FakePushSender:
    name = "fake"

    def __init__(self) -> None:
        self.sent: list[tuple[str, dict]] = []

    def send(self, *, token: str, payload: dict) -> None:
        self.sent.append((token, payload))


@pytest.fixture(autouse=True)
def _reset_state():
    original_sensitive = config.auth_require_sensitive_routes
    reset_auth_repository_for_tests()
    reset_device_repository_for_tests()
    reset_notification_repository_for_tests()
    auth_rate_limiter.reset()
    pairing_rate_limiter.reset()
    config.auth_require_sensitive_routes = False
    yield
    app.dependency_overrides.pop(get_notification_service, None)
    reset_auth_repository_for_tests()
    reset_device_repository_for_tests()
    reset_notification_repository_for_tests()
    auth_rate_limiter.reset()
    pairing_rate_limiter.reset()
    config.auth_require_sensitive_routes = original_sensitive


def _auth_service() -> AuthService:
    return AuthService(get_auth_repository())


def _create_user(email: str, role: UserRole, organization_id: str | None):
    user = _auth_service().create_user(
        email=email, full_name=email.split("@", 1)[0].title(), password=PASSWORD, role=role
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


def _paired_device(organization_id: str = "org-a") -> Device:
    repo = get_device_repository()
    device = repo.create_device(
        Device(organization_id=organization_id, user_id="user-contact", platform=DevicePlatform.ANDROID, public_key="pk")
    )
    return device


# ---------------------------------------------------------------------------
# Service-level revocation behavior
# ---------------------------------------------------------------------------


def test_revoke_device_sets_state_and_revoked_at():
    device = _paired_device()
    operator, _ = _create_operator_and_contact("org-a")

    revoked = DeviceService().revoke_device(actor=operator, device_id=device.id)

    assert revoked.state == DeviceState.REVOKED
    assert revoked.revoked_at is not None


def test_revoke_device_revokes_all_sessions():
    device = _paired_device()
    repo = get_device_repository()
    session = repo.create_session(DeviceSession(device_id=device.id, expires_at=utc_now() + timedelta(days=30)))
    operator, _ = _create_operator_and_contact("org-a")

    DeviceService().revoke_device(actor=operator, device_id=device.id)

    assert repo.get_session(session.id).revoked_at is not None


def test_revoke_device_deletes_push_token():
    device = _paired_device()
    repo = get_device_repository()
    repo.upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    operator, _ = _create_operator_and_contact("org-a")

    DeviceService().revoke_device(actor=operator, device_id=device.id)

    assert repo.get_push_token_by_device(device.id) is None


def test_revoke_device_is_idempotent():
    device = _paired_device()
    operator, _ = _create_operator_and_contact("org-a")
    service = DeviceService()

    first = service.revoke_device(actor=operator, device_id=device.id)
    second = service.revoke_device(actor=operator, device_id=device.id)

    assert first.state == second.state == DeviceState.REVOKED
    # Idempotent means the second call is a no-op, not a fresh revocation.
    assert first.revoked_at == second.revoked_at


def test_revoke_device_cross_organization_raises_not_found():
    device = _paired_device(organization_id="org-a")
    other_operator, _ = _create_operator_and_contact("org-b")

    with pytest.raises(DeviceNotFoundError):
        DeviceService().revoke_device(actor=other_operator, device_id=device.id)


def test_send_test_push_to_revoked_device_fails_with_explicit_reason():
    device = _paired_device()
    repo = get_device_repository()
    repo.upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    operator, _ = _create_operator_and_contact("org-a")
    DeviceService().revoke_device(actor=operator, device_id=device.id)

    alert = NotificationService(
        device_repository=repo, sender=FakePushSender()
    ).send_test_push(actor=operator, device_id=device.id)

    assert alert.state == AlertState.FAILED
    assert alert.failed_reason == "device_revoked"


# ---------------------------------------------------------------------------
# HTTP: revoked session is rejected immediately, even offline
# ---------------------------------------------------------------------------


def test_revoke_endpoint_cross_organization_returns_404():
    device = _paired_device(organization_id="org-a")
    other_operator, _ = _create_operator_and_contact("org-b")
    client = _login(TestClient(app), other_operator.email)

    response = client.post(f"/devices/{device.id}/revoke")

    assert response.status_code == 404


def test_device_session_rejected_after_revocation_even_without_device_activity():
    device = _paired_device()
    repo = get_device_repository()
    session = repo.create_session(DeviceSession(device_id=device.id, expires_at=utc_now() + timedelta(days=30)))
    operator, _ = _create_operator_and_contact("org-a")

    # The device never calls the server again after this point ("offline") —
    # revocation still must take effect on the very next authenticated call.
    admin_client = _login(TestClient(app), operator.email)
    revoke_response = admin_client.post(f"/devices/{device.id}/revoke")
    assert revoke_response.status_code == 200

    push_token_response = TestClient(app).post(
        "/devices/me/push-token",
        json={"token": "fcm-token-123"},
        headers={DEVICE_SESSION_HEADER: session.id},
    )
    assert push_token_response.status_code == 401


# ---------------------------------------------------------------------------
# Sprint 2 Definition of Done, end to end
# ---------------------------------------------------------------------------


def test_full_pairing_push_ack_and_revocation_scenario():
    operator, contact = _create_operator_and_contact("org-a")
    sender = FakePushSender()
    app.dependency_overrides[get_notification_service] = lambda: NotificationService(sender=sender)

    admin_client = _login(TestClient(app), operator.email)

    # 1. Convite de uso unico.
    invitation = admin_client.post(
        "/devices/pairing-invitations", json={"trusted_contact_user_id": contact.id}
    ).json()

    # 2. Pareamento (o "Android real" nesta suite e o cliente HTTP puro).
    pair_response = TestClient(app).post(
        "/devices/pair",
        json={"token": invitation["token"], "platform": "android", "public_key": "device-pubkey"},
    )
    assert pair_response.status_code == 200
    paired = pair_response.json()
    device_id, session_id = paired["device_id"], paired["session_id"]
    assert paired["state"] == DeviceState.PENDING_PAIRING.value

    # 3. Registro do token de push.
    token_response = TestClient(app).post(
        "/devices/me/push-token",
        json={"token": "fcm-real-device-token"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )
    assert token_response.status_code == 200

    # 4. Push de teste disparado pelo admin.
    push_response = admin_client.post(f"/devices/{device_id}/test-push")
    assert push_response.status_code == 200
    push_body = push_response.json()
    assert push_body["state"] == AlertState.SENT.value
    alert_id = push_body["alert_id"]
    assert sender.sent[0][0] == "fcm-real-device-token"

    # 5. ACK de abertura -> device sai de PENDING_PAIRING.
    ack_response = TestClient(app).post(
        f"/devices/me/alerts/{alert_id}/ack",
        json={"event": "opened"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )
    assert ack_response.status_code == 200
    assert ack_response.json()["state"] == AlertState.OPENED.value
    assert admin_client.get(f"/devices/{device_id}").json()["state"] == DeviceState.ACTIVE.value

    # 6. Revogacao pelo admin.
    revoke_response = admin_client.post(f"/devices/{device_id}/revoke")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["state"] == DeviceState.REVOKED.value

    # 7. Acesso perdido imediatamente, mesmo sem o device ter "avisado" nada.
    post_revoke_ack = TestClient(app).post(
        f"/devices/me/alerts/{alert_id}/ack",
        json={"event": "actioned"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )
    assert post_revoke_ack.status_code == 401

    post_revoke_token = TestClient(app).post(
        "/devices/me/push-token",
        json={"token": "another-token"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )
    assert post_revoke_token.status_code == 401
