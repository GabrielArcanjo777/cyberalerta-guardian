from fastapi.testclient import TestClient

import pytest

from app.auth.crypto import current_totp_code, generate_totp_secret
from app.auth.models import AuthEventType, UserRole
from app.auth.repository import get_auth_repository, reset_auth_repository_for_tests
from app.auth.service import AuthService, auth_rate_limiter
from app.core.config import config
from main import app


PASSWORD = "StrongPass!123"


@pytest.fixture(autouse=True)
def _reset_auth_state():
    original = {
        "api_key_enabled": config.api_key_enabled,
        "cyberalerta_api_key": config.cyberalerta_api_key,
        "auth_require_sensitive_routes": config.auth_require_sensitive_routes,
        "google_oauth_enabled": config.google_oauth_enabled,
        "google_auto_create_users": config.google_auto_create_users,
        "google_auth_allowed_emails": list(config.google_auth_allowed_emails),
        "google_auth_allowed_domains": list(config.google_auth_allowed_domains),
        "n8n_webhook_secret": config.n8n_webhook_secret,
        "n8n_webhook_header": config.n8n_webhook_header,
    }
    reset_auth_repository_for_tests()
    auth_rate_limiter.reset()
    config.api_key_enabled = False
    config.auth_require_sensitive_routes = False
    config.google_oauth_enabled = False
    config.google_auto_create_users = False
    config.google_auth_allowed_emails = []
    config.google_auth_allowed_domains = []
    yield
    reset_auth_repository_for_tests()
    auth_rate_limiter.reset()
    for key, value in original.items():
        setattr(config, key, value)


def _service() -> AuthService:
    return AuthService(get_auth_repository())


def _create_user(email: str, role: UserRole = UserRole.VIEWER, *, is_admin: bool = False):
    return _service().create_user(
        email=email,
        full_name=email.split("@", 1)[0].title(),
        password=PASSWORD,
        role=role,
        is_admin=is_admin,
    )


def _create_mfa_admin(email: str = "admin@example.com") -> str:
    user = _create_user(email, UserRole.ADMIN, is_admin=True)
    secret = generate_totp_secret()
    get_auth_repository().update_user(user.model_copy(update={"mfa_secret": secret, "mfa_enabled": True}))
    return secret


def _login(client: TestClient, email: str, password: str = PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_login_with_correct_password_sets_http_only_cookie():
    _create_user("viewer@example.com")
    client = TestClient(app)

    response = _login(client, "viewer@example.com")

    assert response.status_code == 200
    body = response.json()
    assert body["authenticated"] is True
    assert body["user"]["email"] == "viewer@example.com"
    assert config.auth_cookie_name in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=lax" in response.headers["set-cookie"]


def test_login_with_wrong_password_uses_generic_error():
    _create_user("viewer@example.com")
    client = TestClient(app)

    response = _login(client, "viewer@example.com", "bad-password")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_with_unknown_user_uses_generic_error():
    client = TestClient(app)

    response = _login(client, "missing@example.com")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_logout_clears_session_cookie():
    _create_user("viewer@example.com")
    client = TestClient(app)
    assert _login(client, "viewer@example.com").status_code == 200

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert config.auth_cookie_name in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]


def test_me_without_session_is_public_and_unauthenticated():
    client = TestClient(app)

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "user": None}


def test_me_with_session_returns_current_user():
    _create_user("viewer@example.com")
    client = TestClient(app)
    assert _login(client, "viewer@example.com").status_code == 200

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["authenticated"] is True
    assert response.json()["user"]["email"] == "viewer@example.com"


def test_mfa_setup_and_enable_for_logged_user():
    _create_user("viewer@example.com")
    client = TestClient(app)
    assert _login(client, "viewer@example.com").status_code == 200

    setup = client.post("/auth/mfa/setup")
    assert setup.status_code == 200
    secret = setup.json()["manual_secret"]
    assert setup.json()["otpauth_uri"].startswith("otpauth://totp/")
    assert setup.json()["qr_code_base64"]

    enable = client.post("/auth/mfa/enable", json={"code": current_totp_code(secret)})
    assert enable.status_code == 200
    assert enable.json()["mfa_enabled"] is True


def test_mfa_verify_with_correct_code_creates_session():
    secret = _create_mfa_admin()
    client = TestClient(app)

    login = _login(client, "admin@example.com")
    assert login.status_code == 200
    assert login.json()["mfa_required"] is True

    verify = client.post(
        "/auth/mfa/verify",
        json={"temporary_token": login.json()["temporary_token"], "code": current_totp_code(secret)},
    )

    assert verify.status_code == 200
    assert verify.json()["authenticated"] is True
    assert config.auth_cookie_name in verify.headers["set-cookie"]


def test_mfa_verify_with_wrong_code_is_rejected():
    _create_mfa_admin()
    client = TestClient(app)
    login = _login(client, "admin@example.com")

    response = client.post(
        "/auth/mfa/verify",
        json={"temporary_token": login.json()["temporary_token"], "code": "000000"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_admin_can_access_admin_users_after_mfa():
    secret = _create_mfa_admin()
    client = TestClient(app)
    login = _login(client, "admin@example.com")
    assert client.post(
        "/auth/mfa/verify",
        json={"temporary_token": login.json()["temporary_token"], "code": current_totp_code(secret)},
    ).status_code == 200

    response = client.get("/admin/users")

    assert response.status_code == 200
    assert response.json()["users"][0]["role"] == "admin"


def test_admin_without_mfa_cannot_access_admin_users():
    _create_user("admin@example.com", UserRole.ADMIN, is_admin=True)
    client = TestClient(app)
    assert _login(client, "admin@example.com").status_code == 200

    response = client.get("/admin/users")

    assert response.status_code == 403
    assert response.json()["detail"] == "MFA required"


def test_viewer_cannot_access_admin_users():
    _create_user("viewer@example.com")
    client = TestClient(app)
    assert _login(client, "viewer@example.com").status_code == 200

    response = client.get("/admin/users")

    assert response.status_code == 403


def test_sensitive_routes_can_require_authenticated_admin_or_analyst():
    config.auth_require_sensitive_routes = True
    client = TestClient(app)
    assert client.get("/guardian-console/status").status_code == 401

    _create_user("analyst@example.com", UserRole.ANALYST)
    assert _login(client, "analyst@example.com").status_code == 200

    response = client.get("/guardian-console/status")

    assert response.status_code == 200


def test_google_login_is_blocked_when_disabled():
    client = TestClient(app)

    response = client.get("/auth/google/login", follow_redirects=False)

    assert response.status_code == 403


def test_google_auto_create_is_blocked_by_default():
    service = _service()

    with pytest.raises(Exception):
        service._user_from_google_profile(
            {"sub": "google-user-1", "email": "new@example.com", "name": "New User", "email_verified": "true"}
        )


def test_google_auto_created_user_is_viewer_never_admin():
    config.google_auto_create_users = True
    config.google_auth_allowed_domains = ["example.com"]
    service = _service()

    user = service._user_from_google_profile(
        {"sub": "google-user-1", "email": "new@example.com", "name": "New User", "email_verified": "true"}
    )

    assert user.role == UserRole.VIEWER
    assert user.is_admin is False
    assert user.password_hash is None


def test_n8n_inbound_still_uses_its_own_secret_header():
    config.n8n_webhook_secret = "n8n-test-secret"
    config.n8n_webhook_header = "X-N8N-CyberAlerta-Secret"
    client = TestClient(app)

    response = client.post(
        "/integrations/n8n/whatsapp/inbound",
        json={
            "message_id": "auth-n8n-smoke-1",
            "from": "masked-contact",
            "to": "cyberalerta-demo",
            "body": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
            "channel": "whatsapp",
            "user_name": "Dona Lucia",
            "trusted_contact_name": "Gabriel",
            "trusted_contact_relation": "filho",
            "already_acted": False,
        },
        headers={"X-N8N-CyberAlerta-Secret": "n8n-test-secret"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processed"


def test_health_stays_public_without_session():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_auth_audit_logs_login_failures_without_plain_password():
    _create_user("viewer@example.com")
    client = TestClient(app)
    _login(client, "viewer@example.com", "wrong-password")

    logs = _service().list_audit_logs()

    assert logs[0].event_type == AuthEventType.LOGIN_FAILED
    assert logs[0].email == "viewer@example.com"
    assert "wrong-password" not in (logs[0].reason or "")
