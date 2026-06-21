from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse

from app.auth.dependencies import get_auth_service, get_current_user, require_admin, require_authenticated_user
from app.auth.models import AuthUser, PublicUser
from app.auth.schemas import (
    AdminAuditLogsResponse,
    AdminUserItem,
    AdminUsersResponse,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MFACodeRequest,
    MFADisableRequest,
    MFASetupResponse,
    MFAStatusResponse,
    MFAVerifyRequest,
    MeResponse,
)
from app.auth.service import AuthResult, AuthService
from app.core.config import config

GOOGLE_STATE_COOKIE = "cyberalerta_google_state"


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        config.auth_cookie_name,
        token,
        httponly=True,
        secure=config.auth_cookie_secure,
        samesite=config.auth_cookie_samesite,
        max_age=config.auth_access_token_expire_minutes * 60,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(config.auth_cookie_name, path="/")


def _apply_auth_result(response: Response, result: AuthResult) -> LoginResponse:
    if result.session_token:
        _set_session_cookie(response, result.session_token)
    return result.response


def create_auth_router() -> APIRouter:
    router = APIRouter(tags=["auth"])

    @router.post("/auth/login", response_model=LoginResponse)
    def login(
        payload: LoginRequest,
        request: Request,
        response: Response,
        service: AuthService = Depends(get_auth_service),
    ) -> LoginResponse:
        return _apply_auth_result(response, service.login(payload, request=request))

    @router.post("/auth/logout", response_model=LogoutResponse)
    def logout(
        request: Request,
        response: Response,
        user: AuthUser | None = Depends(get_current_user),
        service: AuthService = Depends(get_auth_service),
    ) -> LogoutResponse:
        service.logout(user, request=request)
        _clear_session_cookie(response)
        return LogoutResponse()

    @router.get("/auth/me", response_model=MeResponse)
    def me(user: AuthUser | None = Depends(get_current_user)) -> MeResponse:
        return MeResponse(authenticated=user is not None, user=PublicUser.from_user(user) if user else None)

    @router.post("/auth/change-password", response_model=LogoutResponse)
    def change_password(
        payload: ChangePasswordRequest,
        request: Request,
        user: AuthUser = Depends(require_authenticated_user),
        service: AuthService = Depends(get_auth_service),
    ) -> LogoutResponse:
        service.change_password(user, payload.current_password, payload.new_password, request=request)
        return LogoutResponse()

    @router.post("/auth/mfa/setup", response_model=MFASetupResponse)
    def mfa_setup(
        request: Request,
        user: AuthUser = Depends(require_authenticated_user),
        service: AuthService = Depends(get_auth_service),
    ) -> MFASetupResponse:
        otpauth_uri, qr_code_base64, manual_secret = service.setup_mfa(user, request=request)
        return MFASetupResponse(
            otpauth_uri=otpauth_uri,
            qr_code_base64=qr_code_base64,
            manual_secret=manual_secret,
        )

    @router.post("/auth/mfa/enable", response_model=MFAStatusResponse)
    def mfa_enable(
        payload: MFACodeRequest,
        request: Request,
        user: AuthUser = Depends(require_authenticated_user),
        service: AuthService = Depends(get_auth_service),
    ) -> MFAStatusResponse:
        updated = service.enable_mfa(user, payload.code, request=request)
        return MFAStatusResponse(mfa_enabled=updated.mfa_enabled)

    @router.post("/auth/mfa/verify", response_model=LoginResponse)
    def mfa_verify(
        payload: MFAVerifyRequest,
        request: Request,
        response: Response,
        service: AuthService = Depends(get_auth_service),
    ) -> LoginResponse:
        return _apply_auth_result(response, service.verify_mfa_token(payload.temporary_token, payload.code, request=request))

    @router.post("/auth/mfa/disable", response_model=MFAStatusResponse)
    def mfa_disable(
        payload: MFADisableRequest,
        request: Request,
        user: AuthUser = Depends(require_authenticated_user),
        service: AuthService = Depends(get_auth_service),
    ) -> MFAStatusResponse:
        updated = service.disable_mfa(user, payload.password, payload.code, request=request)
        return MFAStatusResponse(mfa_enabled=updated.mfa_enabled)

    @router.get("/auth/google/login")
    def google_login(
        request: Request,
        service: AuthService = Depends(get_auth_service),
    ):
        url, state = service.google_login_url(request=request)
        response = RedirectResponse(url=url, status_code=302)
        response.set_cookie(
            GOOGLE_STATE_COOKIE,
            state,
            httponly=True,
            secure=config.auth_cookie_secure,
            samesite=config.auth_cookie_samesite,
            max_age=600,
            path="/auth/google",
        )
        return response

    @router.get("/auth/google/callback", response_model=LoginResponse)
    def google_callback(
        request: Request,
        response: Response,
        code: str = Query(default=""),
        state: str = Query(default=""),
        service: AuthService = Depends(get_auth_service),
    ):
        result = service.google_callback(
            code=code,
            state=state,
            cookie_state=request.cookies.get(GOOGLE_STATE_COOKIE),
            request=request,
        )
        _apply_auth_result(response, result)
        response.delete_cookie(GOOGLE_STATE_COOKIE, path="/auth/google")
        return result.response

    @router.get("/admin/users", response_model=AdminUsersResponse)
    def admin_users(
        admin: AuthUser = Depends(require_admin),
        service: AuthService = Depends(get_auth_service),
    ) -> AdminUsersResponse:
        del admin
        return AdminUsersResponse(users=[AdminUserItem.model_validate(user.model_dump()) for user in service.list_users()])

    @router.get("/admin/audit-logs", response_model=AdminAuditLogsResponse)
    def admin_audit_logs(
        admin: AuthUser = Depends(require_admin),
        service: AuthService = Depends(get_auth_service),
    ) -> AdminAuditLogsResponse:
        del admin
        return AdminAuditLogsResponse(logs=service.list_audit_logs(limit=100))

    return router
