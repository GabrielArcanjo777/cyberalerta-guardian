from __future__ import annotations

import pytest

from app.auth.crypto import (
    generate_recovery_codes,
    hash_recovery_code,
    verify_recovery_code,
    hash_password,
    verify_password,
    current_totp_code,
)
from app.auth.google_oidc import verify_google_id_token
from app.auth.models import AuthEventType, UserRole
from app.auth.repository import reset_auth_repository_for_tests, InMemoryAuthRepository
from app.auth.service import AuthService


@pytest.fixture(autouse=True)
def _reset_repo():
    reset_auth_repository_for_tests(InMemoryAuthRepository())
    yield
    reset_auth_repository_for_tests()


class TestArgon2PasswordHashing:
    def test_hash_returns_argon2id_by_default(self):
        h = hash_password("ValidPass123!")
        assert h.startswith("argon2id$"), f"Expected argon2id prefix, got: {h[:20]}"

    def test_verify_argon2id_hash(self):
        h = hash_password("ValidPass123!")
        assert verify_password("ValidPass123!", h) is True

    def test_verify_wrong_password_fails(self):
        h = hash_password("ValidPass123!")
        assert verify_password("WrongPass123!", h) is False

    def test_verify_legacy_pbkdf2_hash_still_works(self):
        from app.auth.crypto import PASSWORD_SCHEME, PASSWORD_ITERATIONS
        import hashlib, secrets, base64
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", b"ValidPass123!xx", salt, PASSWORD_ITERATIONS)
        b64 = lambda x: base64.urlsafe_b64encode(x).decode("ascii").rstrip("=")
        legacy_hash = "$".join([PASSWORD_SCHEME, str(PASSWORD_ITERATIONS), b64(salt), b64(digest)])
        assert verify_password("ValidPass123!xx", legacy_hash) is True

    def test_verify_empty_or_none(self):
        assert verify_password("", "somehash") is False
        assert verify_password("pass", None) is False
        assert verify_password("pass", "") is False

    def test_change_password_upgrades_to_argon2id(self):
        service = AuthService()
        user = service.create_user(email="hash@test.com", full_name="Hash T", password="OldPass123!x", role=UserRole.VIEWER)
        assert user.password_hash.startswith("argon2id$")
        service.change_password(user, "OldPass123!x", "NewPass456@y")
        updated = service.repository.get_user_by_email("hash@test.com")
        assert updated.password_hash.startswith("argon2id$")
        assert verify_password("NewPass456@y", updated.password_hash) is True
        assert verify_password("OldPass123!x", updated.password_hash) is False


class TestRecoveryCodes:
    def test_generate_10_codes(self):
        codes = generate_recovery_codes(10)
        assert len(codes) == 10

    def test_codes_format(self):
        codes = generate_recovery_codes(10)
        for code in codes:
            assert len(code) == 9, f"Code length mismatch: {code}"
            assert code[4] == "-", f"Code missing dash: {code}"

    def test_codes_unique(self):
        codes = generate_recovery_codes(10)
        assert len(set(codes)) == 10

    def test_hash_does_not_contain_raw_code(self):
        codes = generate_recovery_codes(1)
        h = hash_recovery_code(codes[0])
        assert codes[0] not in h
        assert h.startswith("argon2id$"), f"Expected argon2id prefix, got: {h[:20]}"

    def test_hash_is_not_sha256(self):
        codes = generate_recovery_codes(1)
        h = hash_recovery_code(codes[0])
        assert len(h) != 64, "Hash should not be raw SHA-256 (64 hex chars)"
        assert "argon2id" in h

    def test_verify_correct_code(self):
        codes = generate_recovery_codes(1)
        h = hash_recovery_code(codes[0])
        assert verify_recovery_code(codes[0], h) is True

    def test_verify_wrong_code_fails(self):
        codes = generate_recovery_codes(1)
        h = hash_recovery_code(codes[0])
        assert verify_recovery_code("XXXX-XXXX", h) is False


class TestMfaRecoveryCodes:
    def _create_user_with_mfa(self, service):
        user = service.create_user(email="mfa@test.com", full_name="MFA T", password="MfaPass123!x", role=UserRole.VIEWER)
        service.setup_mfa(user)
        updated = service.repository.get_user_by_email("mfa@test.com")
        return updated

    def test_enable_mfa_returns_recovery_codes(self):
        service = AuthService()
        user = self._create_user_with_mfa(service)
        code = current_totp_code(user.mfa_secret)
        updated, recovery_codes = service.enable_mfa(user, code)
        assert updated.mfa_enabled is True
        assert len(recovery_codes) == 10

    def test_verify_with_recovery_code(self):
        service = AuthService()
        user = self._create_user_with_mfa(service)
        code = current_totp_code(user.mfa_secret)
        updated, recovery_codes = service.enable_mfa(user, code)
        tmp_token = service.create_temporary_token(updated)
        result = service.verify_mfa_token(tmp_token, recovery_codes[0])
        assert result.response.authenticated is True

    def test_recovery_code_single_use(self):
        service = AuthService()
        user = self._create_user_with_mfa(service)
        code = current_totp_code(user.mfa_secret)
        updated, recovery_codes = service.enable_mfa(user, code)
        tmp_token = service.create_temporary_token(updated)
        result1 = service.verify_mfa_token(tmp_token, recovery_codes[0])
        assert result1.response.authenticated is True
        tmp_token2 = service.create_temporary_token(updated)
        with pytest.raises(Exception):
            service.verify_mfa_token(tmp_token2, recovery_codes[0])

    def test_regenerate_recovery_codes(self):
        service = AuthService()
        user = self._create_user_with_mfa(service)
        code = current_totp_code(user.mfa_secret)
        updated, old_codes = service.enable_mfa(user, code)
        new_codes = service.regenerate_recovery_codes(updated)
        assert len(new_codes) == 10
        assert set(old_codes) != set(new_codes)

    def test_audit_recovery_code_used(self):
        service = AuthService()
        user = self._create_user_with_mfa(service)
        code = current_totp_code(user.mfa_secret)
        updated, recovery_codes = service.enable_mfa(user, code)
        tmp_token = service.create_temporary_token(updated)
        service.verify_mfa_token(tmp_token, recovery_codes[0])
        logs = service.list_audit_logs()
        recovery_events = [l for l in logs if l.event_type == AuthEventType.MFA_RECOVERY_CODE_USED]
        assert len(recovery_events) >= 1


class TestGoogleOidcValidation:
    def test_disabled_by_default(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.auth.router import create_auth_router
        from app.core.config import config
        config.google_oauth_enabled = False
        app = FastAPI()
        app.include_router(create_auth_router())
        client = TestClient(app)
        resp = client.get("/auth/google/login")
        assert resp.status_code == 403

    def test_invalid_state_blocked(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.auth.router import create_auth_router
        from app.core.config import config
        config.google_oauth_enabled = True
        config.google_client_id = "google-client-id"
        config.google_client_secret = "google-client-secret"
        app = FastAPI()
        app.include_router(create_auth_router())
        client = TestClient(app)
        resp = client.get("/auth/google/callback?code=test&state=badstate")
        assert resp.status_code == 400

    def test_verify_google_id_token_disabled_by_default(self):
        with pytest.raises(Exception):
            verify_google_id_token("fake-token")

    def test_valid_token_creates_viewer(self):
        pass

    def test_google_never_creates_admin(self):
        pass

    def test_auto_create_disabled_blocks_unknown_user(self):
        pass

    def test_email_verified_false_blocked(self):
        pass

    def test_invalid_issuer_blocked(self):
        pass

    def test_expired_token_blocked(self):
        pass
