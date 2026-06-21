from __future__ import annotations

from collections.abc import Iterable

from fastapi import Depends, HTTPException, Request, status

from app.auth.models import AuthUser, UserRole
from app.auth.service import AuthService
from app.core.config import config
from app.core.security import require_api_key


def get_auth_service() -> AuthService:
    return AuthService()


def get_current_user(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> AuthUser | None:
    token = request.cookies.get(config.auth_cookie_name)
    return service.get_user_from_session(token)


def require_authenticated_user(user: AuthUser | None = Depends(get_current_user)) -> AuthUser:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user


def require_admin(user: AuthUser = Depends(require_authenticated_user)) -> AuthUser:
    if not user.is_admin or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA required")
    return user


def require_role(roles: Iterable[UserRole]):
    allowed = set(roles)

    def dependency(user: AuthUser = Depends(require_authenticated_user)) -> AuthUser:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return dependency


def require_sensitive_access(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> None:
    if config.api_key_enabled:
        if request.headers.get(config.api_key_header):
            require_api_key(request)
            return None
        user = service.get_user_from_session(request.cookies.get(config.auth_cookie_name))
        if user and user.role in {UserRole.ADMIN, UserRole.ANALYST}:
            if user.role == UserRole.ADMIN and not user.mfa_enabled:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA required")
            return None
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not config.auth_require_sensitive_routes:
        return None

    user = service.get_user_from_session(request.cookies.get(config.auth_cookie_name))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if user.role not in {UserRole.ADMIN, UserRole.ANALYST}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if user.role == UserRole.ADMIN and not user.mfa_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="MFA required")
    return None
