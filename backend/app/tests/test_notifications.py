"""Sprint 2, Unidade 4 (Plano Mestre v1.1, Secao 4.3/6.2/7.2) — push-token
registration, test-push sending (fail-closed on every unsent path) and ACK
handling, including the PENDING_PAIRING -> ACTIVE promotion the plan gates on
a confirmed test push. Real CASE_ALERT integration is Sprint 5; revocation
cleanup of push tokens is Unidade 5.
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
from app.devices.models import Device, DevicePlatform, DeviceSession, DeviceState, PushToken
from app.devices.repository import InMemoryDeviceRepository, get_device_repository, reset_device_repository_for_tests
from app.devices.service import DeviceService
from app.notifications.contract import PushProviderError, PushProviderTokenInvalid
from app.notifications.models import AckEvent, AlertState, AlertType
from app.notifications.repository import InMemoryAlertRepository, reset_notification_repository_for_tests
from app.notifications.router import get_notification_service
from app.notifications.service import AlertNotFoundError, NotificationService
from main import app

PASSWORD = "StrongPass!123"


class FakePushSender:
    name = "fake"

    def __init__(self, *, fail_with: Exception | None = None) -> None:
        self.sent: list[tuple[str, dict]] = []
        self._fail_with = fail_with

    def send(self, *, token: str, payload: dict) -> None:
        if self._fail_with is not None:
            raise self._fail_with
        self.sent.append((token, payload))


@pytest.fixture(autouse=True)
def _reset_state():
    original_sensitive = config.auth_require_sensitive_routes
    reset_auth_repository_for_tests()
    reset_device_repository_for_tests()
    reset_notification_repository_for_tests()
    auth_rate_limiter.reset()
    config.auth_require_sensitive_routes = False
    yield
    app.dependency_overrides.pop(get_notification_service, None)
    reset_auth_repository_for_tests()
    reset_device_repository_for_tests()
    reset_notification_repository_for_tests()
    auth_rate_limiter.reset()
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


def _paired_device(organization_id: str = "org-a") -> tuple[Device, str]:
    """Create+pair a device through the repository directly (bypasses the
    Unidade 3 HTTP flow, which is already covered in test_devices_pairing.py)
    and return the device plus its session_id bearer token."""
    repo = get_device_repository()
    device = repo.create_device(
        Device(organization_id=organization_id, user_id="user-contact", platform=DevicePlatform.ANDROID, public_key="pk")
    )
    session = repo.create_session(DeviceSession(device_id=device.id, expires_at=_far_future()))
    return device, session.id


def _far_future():
    from app.devices.models import utc_now

    return utc_now() + timedelta(days=30)


# ---------------------------------------------------------------------------
# Push-token registration (device-authenticated)
# ---------------------------------------------------------------------------


def test_register_push_token_requires_device_session_header():
    response = TestClient(app).post("/devices/me/push-token", json={"token": "fcm-token-123"})
    assert response.status_code == 401


def test_register_push_token_rejects_unknown_session():
    response = TestClient(app).post(
        "/devices/me/push-token",
        json={"token": "fcm-token-123"},
        headers={DEVICE_SESSION_HEADER: "does-not-exist"},
    )
    assert response.status_code == 401


def test_register_push_token_rejects_revoked_session():
    device, session_id = _paired_device()
    repo = get_device_repository()
    session = repo.get_session(session_id)
    repo.update_session(session.model_copy(update={"revoked_at": session.issued_at}))

    response = TestClient(app).post(
        "/devices/me/push-token",
        json={"token": "fcm-token-123"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )
    assert response.status_code == 401


def test_register_push_token_with_valid_session_persists_token():
    device, session_id = _paired_device()

    response = TestClient(app).post(
        "/devices/me/push-token",
        json={"token": "fcm-token-123"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )

    assert response.status_code == 200, response.text
    stored = get_device_repository().get_push_token_by_device(device.id)
    assert stored.token == "fcm-token-123"


# ---------------------------------------------------------------------------
# Sending a test push — fail-closed on every path that doesn't end in SENT
# ---------------------------------------------------------------------------


def _service(sender=None) -> NotificationService:
    return NotificationService(
        repository=InMemoryAlertRepository(),
        device_repository=get_device_repository(),
        sender=sender,
    )


def _org_actor(organization_id: str = "org-a"):
    return _create_user(f"admin-{organization_id}@example.com", UserRole.ADMIN, organization_id)


def test_send_test_push_without_configured_sender_fails_closed():
    device, _ = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    actor = _org_actor()

    alert = _service(sender=None).send_test_push(actor=actor, device_id=device.id)

    assert alert.state == AlertState.FAILED
    assert alert.failed_reason == "fcm_not_configured"


def test_send_test_push_without_push_token_fails_closed():
    device, _ = _paired_device()
    actor = _org_actor()

    alert = _service(sender=FakePushSender()).send_test_push(actor=actor, device_id=device.id)

    assert alert.state == AlertState.FAILED
    assert alert.failed_reason == "push_token_missing"


def test_send_test_push_success_marks_alert_sent():
    device, _ = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    actor = _org_actor()
    sender = FakePushSender()

    alert = _service(sender=sender).send_test_push(actor=actor, device_id=device.id)

    assert alert.state == AlertState.SENT
    assert alert.sent_at is not None
    assert len(sender.sent) == 1
    token_used, payload = sender.sent[0]
    assert token_used == "fcm-token"
    assert payload["alert_id"] == alert.id
    assert "protected_person_alias" not in payload or payload.get("protected_person_alias") is None


def test_send_test_push_invalid_token_deletes_token_and_fails():
    device, _ = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    actor = _org_actor()
    sender = FakePushSender(fail_with=PushProviderTokenInvalid("gone"))

    alert = _service(sender=sender).send_test_push(actor=actor, device_id=device.id)

    assert alert.state == AlertState.FAILED
    assert alert.failed_reason == "invalid_token"
    assert get_device_repository().get_push_token_by_device(device.id) is None


def test_send_test_push_provider_error_fails():
    device, _ = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    actor = _org_actor()
    sender = FakePushSender(fail_with=PushProviderError("network down"))

    alert = _service(sender=sender).send_test_push(actor=actor, device_id=device.id)

    assert alert.state == AlertState.FAILED
    assert alert.failed_reason == "provider_error"


def test_send_test_push_cross_organization_returns_not_found_error():
    device, _ = _paired_device(organization_id="org-a")
    other_org_actor = _org_actor(organization_id="org-b")

    from app.devices.service import DeviceNotFoundError

    with pytest.raises(DeviceNotFoundError):
        _service(sender=FakePushSender()).send_test_push(actor=other_org_actor, device_id=device.id)


# ---------------------------------------------------------------------------
# Alert detail fetch (device-authenticated) — what the app calls after
# opening the push, per Secao 4.3: "busca os detalhes permitidos pela API".
# ---------------------------------------------------------------------------


def test_get_alert_returns_detail_for_owning_device():
    device, session_id = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    # Uses the global repositories (no override), same ones the HTTP layer's
    # get_notification_service() reads from — unlike _service()'s isolated
    # in-memory repo, this alert needs to be visible to the GET below.
    alert = NotificationService(sender=FakePushSender()).send_test_push(actor=_org_actor(), device_id=device.id)

    response = TestClient(app).get(
        f"/devices/me/alerts/{alert.id}", headers={DEVICE_SESSION_HEADER: session_id}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["alert_id"] == alert.id
    assert body["type"] == AlertType.TEST.value
    assert body["state"] == AlertState.SENT.value


def test_get_alert_rejects_alert_belonging_to_another_device():
    device_a, _ = _paired_device(organization_id="org-a")
    device_b, session_b = _paired_device(organization_id="org-a")
    get_device_repository().upsert_push_token(PushToken(device_id=device_a.id, token="fcm-token"))
    alert = NotificationService(sender=FakePushSender()).send_test_push(actor=_org_actor(), device_id=device_a.id)

    response = TestClient(app).get(
        f"/devices/me/alerts/{alert.id}", headers={DEVICE_SESSION_HEADER: session_b}
    )

    assert response.status_code == 404


def test_get_alert_requires_device_session():
    response = TestClient(app).get("/devices/me/alerts/some-alert-id")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# ACK handling + PENDING_PAIRING -> ACTIVE promotion
# ---------------------------------------------------------------------------


def test_acknowledge_promotes_pending_pairing_device_to_active_on_opened():
    device, _ = _paired_device()
    assert device.state == DeviceState.PENDING_PAIRING
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    service = _service(sender=FakePushSender())
    alert = service.send_test_push(actor=_org_actor(), device_id=device.id)

    updated_alert = service.acknowledge(device=device, alert_id=alert.id, event=AckEvent.OPENED)

    assert updated_alert.state == AlertState.OPENED
    assert updated_alert.opened_at is not None
    assert get_device_repository().get_device(device.id).state == DeviceState.ACTIVE


def test_acknowledge_is_monotonic_ignores_stale_replay():
    device, _ = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    service = _service(sender=FakePushSender())
    alert = service.send_test_push(actor=_org_actor(), device_id=device.id)

    service.acknowledge(device=device, alert_id=alert.id, event=AckEvent.OPENED)
    replayed = service.acknowledge(device=device, alert_id=alert.id, event=AckEvent.DELIVERED)

    assert replayed.state == AlertState.OPENED  # did not regress to DELIVERED


def test_acknowledge_rejects_alert_belonging_to_another_device():
    device_a, _ = _paired_device(organization_id="org-a")
    device_b, _ = _paired_device(organization_id="org-a")
    get_device_repository().upsert_push_token(PushToken(device_id=device_a.id, token="fcm-token"))
    service = _service(sender=FakePushSender())
    alert = service.send_test_push(actor=_org_actor(), device_id=device_a.id)

    with pytest.raises(AlertNotFoundError):
        service.acknowledge(device=device_b, alert_id=alert.id, event=AckEvent.OPENED)


# ---------------------------------------------------------------------------
# HTTP end-to-end: admin triggers push, device ACKs, device becomes ACTIVE
# ---------------------------------------------------------------------------


def test_test_push_and_ack_http_flow_activates_device():
    device, session_id = _paired_device()
    get_device_repository().upsert_push_token(PushToken(device_id=device.id, token="fcm-token"))
    sender = FakePushSender()
    app.dependency_overrides[get_notification_service] = lambda: NotificationService(sender=sender)

    actor = _org_actor()
    client = _login(TestClient(app), actor.email)
    push_response = client.post(f"/devices/{device.id}/test-push")
    assert push_response.status_code == 200, push_response.text
    alert_id = push_response.json()["alert_id"]
    assert push_response.json()["state"] == AlertState.SENT.value

    ack_response = TestClient(app).post(
        f"/devices/me/alerts/{alert_id}/ack",
        json={"event": "opened"},
        headers={DEVICE_SESSION_HEADER: session_id},
    )
    assert ack_response.status_code == 200, ack_response.text
    assert ack_response.json()["state"] == AlertState.OPENED.value

    device_view = client.get(f"/devices/{device.id}")
    assert device_view.json()["state"] == DeviceState.ACTIVE.value


def test_test_push_endpoint_cross_organization_returns_404():
    device, _ = _paired_device(organization_id="org-a")
    other_actor = _org_actor(organization_id="org-b")
    client = _login(TestClient(app), other_actor.email)

    response = client.post(f"/devices/{device.id}/test-push")

    assert response.status_code == 404
