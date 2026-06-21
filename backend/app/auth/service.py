from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request, status

from app.auth.crypto import (
    build_otpauth_uri,
    build_qr_svg_base64,
    generate_totp_secret,
    hash_password,
    normalize_email,
    sign_token,
    validate_password_strength,
    verify_password,
    verify_token,
    verify_totp,
)
from app.auth.models import AuthAuditLog, AuthEventType, AuthUser, OAuthAccount, PublicUser, UserRole, utc_now
from app.auth.repository import AuthRepository, get_auth_repository
from app.auth.schemas import LoginRequest, LoginResponse
from app.core.config import config

INVALID_CREDENTIALS = "Invalid credentials"
GOOGLE_PROVIDER = "google"


def _client_ip(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return None


def _user_agent(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("User-Agent")


class AuthRateLimiter:
    def __init__(self) -> None:
        self._failures: dict[str, list[float]] = {}

    def is_blocked(self, key: str, *, limit: int = 5, window_seconds: int = 300) -> bool:
        now = time.monotonic()
        cutoff = now - window_seconds
        hits = [item for item in self._failures.get(key, []) if item >= cutoff]
        self._failures[key] = hits
        return len(hits) >= limit

    def record_failure(self, key: str) -> None:
        self._failures.setdefault(key, []).append(time.monotonic())

    def clear(self, key: str) -> None:
        self._failures.pop(key, None)

    def reset(self) -> None:
        self._failures.clear()


auth_rate_limiter = AuthRateLimiter()


@dataclass(frozen=True)
class AuthResult:
    response: LoginResponse
    session_token: str | None = None


class AuthService:
    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.repository = repository or get_auth_repository()

    @property
    def session_seconds(self) -> int:
        return max(1, int(config.auth_access_token_expire_minutes)) * 60

    def login(self, payload: LoginRequest, request: Request | None = None) -> AuthResult:
        email = normalize_email(payload.email)
        key = self._rate_limit_key(request, email, "login")
        if config.auth_rate_limit_enabled and auth_rate_limiter.is_blocked(key):
            self.audit(
                AuthEventType.ACCOUNT_LOCKED,
                email=email,
                success=False,
                reason="too_many_attempts",
                request=request,
            )
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=INVALID_CREDENTIALS)

        user = self.repository.get_user_by_email(email)
        if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
            auth_rate_limiter.record_failure(key)
            self.audit(AuthEventType.LOGIN_FAILED, email=email, success=False, reason="invalid_credentials", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)

        auth_rate_limiter.clear(key)
        if user.mfa_enabled:
            temporary_token = self.create_temporary_token(user)
            self.audit(AuthEventType.LOGIN_SUCCESS, user=user, email=email, success=True, reason="mfa_required", request=request)
            return AuthResult(
                response=LoginResponse(
                    authenticated=False,
                    mfa_required=True,
                    temporary_token=temporary_token,
                    user=PublicUser.from_user(user),
                )
            )

        user = user.model_copy(update={"last_login_at": utc_now()})
        self.repository.update_user(user)
        self.audit(AuthEventType.LOGIN_SUCCESS, user=user, email=email, success=True, request=request)
        return AuthResult(
            response=LoginResponse(
                authenticated=True,
                mfa_setup_required=user.is_admin and not user.mfa_enabled,
                user=PublicUser.from_user(user),
            ),
            session_token=self.create_session_token(user),
        )

    def logout(self, user: AuthUser | None, request: Request | None = None) -> None:
        self.audit(
            AuthEventType.LOGOUT,
            user=user,
            email=user.email if user else None,
            success=True,
            request=request,
        )

    def create_user(
        self,
        *,
        email: str,
        full_name: str,
        password: str | None,
        role: UserRole,
        is_admin: bool = False,
    ) -> AuthUser:
        normalized = normalize_email(email)
        if not normalized or "@" not in normalized:
            raise ValueError("Invalid email.")
        if password is not None:
            errors = validate_password_strength(password)
            if errors:
                raise ValueError(" ".join(errors))
        user = AuthUser(
            email=normalized,
            password_hash=hash_password(password) if password else None,
            full_name=full_name.strip(),
            role=role,
            is_admin=is_admin or role == UserRole.ADMIN,
        )
        created = self.repository.create_user(user)
        if created.is_admin:
            self.audit(AuthEventType.ADMIN_CREATED, user=created, email=created.email, success=True)
        return created

    def change_password(self, user: AuthUser, current_password: str, new_password: str, request: Request | None = None) -> None:
        if not verify_password(current_password, user.password_hash):
            self.audit(AuthEventType.LOGIN_FAILED, user=user, email=user.email, success=False, reason="password_change_failed", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        errors = validate_password_strength(new_password)
        if errors:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)
        updated = user.model_copy(update={"password_hash": hash_password(new_password)})
        self.repository.update_user(updated)
        self.audit(AuthEventType.PASSWORD_CHANGED, user=updated, email=updated.email, success=True, request=request)

    def get_user_from_session(self, token: str | None) -> Optional[AuthUser]:
        payload = verify_token(token, config.auth_secret_key, expected_type="session")
        if not payload:
            return None
        user = self.repository.get_user_by_id(str(payload.get("sub") or ""))
        if not user or not user.is_active:
            return None
        return user

    def create_session_token(self, user: AuthUser) -> str:
        return sign_token(
            {"type": "session", "sub": user.id, "email": user.email, "role": user.role.value},
            config.auth_secret_key,
            expires_in_seconds=self.session_seconds,
        )

    def create_temporary_token(self, user: AuthUser) -> str:
        return sign_token(
            {"type": "mfa", "sub": user.id, "email": user.email},
            config.auth_secret_key,
            expires_in_seconds=300,
        )

    def verify_mfa_token(self, temporary_token: str, code: str, request: Request | None = None) -> AuthResult:
        payload = verify_token(temporary_token, config.auth_secret_key, expected_type="mfa")
        user = self.repository.get_user_by_id(str(payload.get("sub") if payload else "")) if payload else None
        key = self._rate_limit_key(request, str(payload.get("email") if payload else "unknown"), "mfa")
        if config.auth_rate_limit_enabled and auth_rate_limiter.is_blocked(key):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=INVALID_CREDENTIALS)
        if not user or not user.is_active or not verify_totp(user.mfa_secret, code):
            auth_rate_limiter.record_failure(key)
            self.audit(AuthEventType.MFA_FAILED, user=user, email=user.email if user else None, success=False, reason="invalid_mfa", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        auth_rate_limiter.clear(key)
        user = user.model_copy(update={"last_login_at": utc_now()})
        self.repository.update_user(user)
        self.audit(AuthEventType.LOGIN_SUCCESS, user=user, email=user.email, success=True, reason="mfa_verified", request=request)
        return AuthResult(
            response=LoginResponse(authenticated=True, user=PublicUser.from_user(user)),
            session_token=self.create_session_token(user),
        )

    def setup_mfa(self, user: AuthUser, request: Request | None = None) -> tuple[str, str, str]:
        secret = generate_totp_secret()
        updated = user.model_copy(update={"mfa_secret": secret, "mfa_enabled": False})
        self.repository.update_user(updated)
        otpauth_uri = build_otpauth_uri(issuer="CyberAlerta Guardian", account_name=updated.email, secret=secret)
        self.audit(AuthEventType.MFA_SETUP_STARTED, user=updated, email=updated.email, success=True, request=request)
        return otpauth_uri, build_qr_svg_base64(otpauth_uri), secret

    def enable_mfa(self, user: AuthUser, code: str, request: Request | None = None) -> AuthUser:
        if not verify_totp(user.mfa_secret, code):
            self.audit(AuthEventType.MFA_FAILED, user=user, email=user.email, success=False, reason="enable_failed", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        updated = user.model_copy(update={"mfa_enabled": True})
        updated = self.repository.update_user(updated)
        self.audit(AuthEventType.MFA_ENABLED, user=updated, email=updated.email, success=True, request=request)
        return updated

    def disable_mfa(self, user: AuthUser, password: str, code: str | None, request: Request | None = None) -> AuthUser:
        if user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA required")
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        if user.mfa_enabled and not verify_totp(user.mfa_secret, code):
            self.audit(AuthEventType.MFA_FAILED, user=user, email=user.email, success=False, reason="disable_failed", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        updated = user.model_copy(update={"mfa_enabled": False, "mfa_secret": None})
        return self.repository.update_user(updated)

    def google_login_url(self, request: Request | None = None) -> tuple[str, str]:
        if not config.google_oauth_enabled:
            self.audit(AuthEventType.GOOGLE_LOGIN_FAILED, success=False, reason="disabled", request=request)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google OAuth disabled")
        state = sign_token({"type": "google_state"}, config.auth_secret_key, expires_in_seconds=600)
        query = urllib.parse.urlencode(
            {
                "client_id": config.google_client_id,
                "redirect_uri": config.google_redirect_uri,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "nonce": state[-24:],
                "prompt": "select_account",
            }
        )
        self.audit(AuthEventType.GOOGLE_LOGIN_STARTED, success=True, request=request)
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query}", state

    def google_callback(self, *, code: str, state: str, cookie_state: str | None, request: Request | None = None) -> AuthResult:
        if not config.google_oauth_enabled:
            self.audit(AuthEventType.GOOGLE_LOGIN_FAILED, success=False, reason="disabled", request=request)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Google OAuth disabled")
        if not cookie_state or not hmac_compare(state, cookie_state):
            self.audit(AuthEventType.GOOGLE_LOGIN_FAILED, success=False, reason="invalid_state", request=request)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
        if not verify_token(state, config.auth_secret_key, expected_type="google_state"):
            self.audit(AuthEventType.GOOGLE_LOGIN_FAILED, success=False, reason="expired_state", request=request)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
        profile = self._exchange_google_code(code, expected_nonce=state[-24:])
        user = self._user_from_google_profile(profile, request=request)
        if user.mfa_enabled:
            return AuthResult(
                response=LoginResponse(
                    authenticated=False,
                    mfa_required=True,
                    temporary_token=self.create_temporary_token(user),
                    user=PublicUser.from_user(user),
                )
            )
        user = self.repository.update_user(user.model_copy(update={"last_login_at": utc_now()}))
        self.audit(AuthEventType.GOOGLE_LOGIN_SUCCESS, user=user, email=user.email, success=True, request=request)
        return AuthResult(
            response=LoginResponse(authenticated=True, user=PublicUser.from_user(user)),
            session_token=self.create_session_token(user),
        )

    def list_users(self) -> list[PublicUser]:
        return [PublicUser.from_user(user) for user in self.repository.list_users()]

    def list_audit_logs(self, limit: int = 100) -> list[AuthAuditLog]:
        return self.repository.list_audit_logs(limit=limit)

    def audit(
        self,
        event_type: AuthEventType,
        *,
        user: AuthUser | None = None,
        email: str | None = None,
        success: bool,
        reason: str | None = None,
        request: Request | None = None,
    ) -> None:
        if not config.enable_audit_log:
            return
        self.repository.append_audit_log(
            AuthAuditLog(
                user_id=user.id if user else None,
                email=normalize_email(email) if email else None,
                event_type=event_type,
                ip_address=_client_ip(request),
                user_agent=_user_agent(request),
                success=success,
                reason=reason,
            )
        )

    def _rate_limit_key(self, request: Request | None, email: str, bucket: str) -> str:
        return f"{bucket}:{_client_ip(request) or 'unknown'}:{normalize_email(email)}"

    def _exchange_google_code(self, code: str, *, expected_nonce: str | None = None) -> dict:
        if not config.google_client_id or not config.google_client_secret:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google OAuth not configured")
        data = urllib.parse.urlencode(
            {
                "code": code,
                "client_id": config.google_client_id,
                "client_secret": config.google_client_secret,
                "redirect_uri": config.google_redirect_uri,
                "grant_type": "authorization_code",
            }
        ).encode("utf-8")
        try:
            with urllib.request.urlopen(
                urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST"),
                timeout=10,
            ) as response:
                token_payload = json.loads(response.read().decode("utf-8"))
            id_token = token_payload.get("id_token")
            if not id_token:
                raise ValueError("missing id_token")
            with urllib.request.urlopen(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={urllib.parse.quote(id_token)}",
                timeout=10,
            ) as response:
                profile = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS) from exc
        if profile.get("iss") not in {"https://accounts.google.com", "accounts.google.com"}:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        if profile.get("aud") != config.google_client_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        if expected_nonce and profile.get("nonce") and profile.get("nonce") != expected_nonce:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        if str(profile.get("email_verified")).lower() != "true":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        return profile

    def _user_from_google_profile(self, profile: dict, request: Request | None = None) -> AuthUser:
        google_id = str(profile.get("sub") or "")
        email = normalize_email(str(profile.get("email") or ""))
        name = str(profile.get("name") or email)
        if not google_id or not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_CREDENTIALS)
        linked = self.repository.get_oauth_account(GOOGLE_PROVIDER, google_id)
        if linked:
            user = self.repository.get_user_by_id(linked.user_id)
            if user and user.is_active:
                return user
        user = self.repository.get_user_by_email(email)
        if not user:
            if not self._can_auto_create_google_user(email):
                self.audit(AuthEventType.GOOGLE_LOGIN_FAILED, email=email, success=False, reason="auto_create_blocked", request=request)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=INVALID_CREDENTIALS)
            user = self.create_user(email=email, full_name=name, password=None, role=UserRole.VIEWER, is_admin=False)
        self.repository.save_oauth_account(
            OAuthAccount(
                user_id=user.id,
                provider=GOOGLE_PROVIDER,
                provider_user_id=google_id,
                provider_email=email,
            )
        )
        return user

    def _can_auto_create_google_user(self, email: str) -> bool:
        if not config.google_auto_create_users:
            return False
        if email in config.google_auth_allowed_emails:
            return True
        domain = email.rsplit("@", 1)[-1] if "@" in email else ""
        return bool(domain and domain in config.google_auth_allowed_domains)


def hmac_compare(left: str, right: str) -> bool:
    import hmac

    return hmac.compare_digest(left, right)


auth_service = AuthService()
