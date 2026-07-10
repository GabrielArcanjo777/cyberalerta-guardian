from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse

from app.auth.dependencies import get_auth_service, get_current_user, require_admin, require_authenticated_user
from app.auth.models import AuthUser, PublicUser
from app.auth.schemas import (
    AdminAuditLogsResponse,
    AdminUserItem,
    AdminUsersResponse,
    ChangePasswordRequest,
    GoogleAuthStatusResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MFACodeRequest,
    MFADisableRequest,
    MFASetupResponse,
    MFAStatusResponse,
    MFAVerifyRequest,
    MeResponse,
    RegisterRequest,
    RecoveryCodesResponse,
)
from app.auth.service import AuthResult, AuthService, GoogleOAuthFlowError
from app.core.config import config

GOOGLE_STATE_COOKIE = "cyberalerta_google_state"


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        config.auth_cookie_name,
        token,
        httponly=True,
        secure=config.auth_cookie_secure,
        samesite=config.auth_cookie_samesite,
        max_age=config.auth_session_expire_seconds,
        path="/",
    )


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(config.auth_cookie_name, path="/")


def _apply_auth_result(response: Response, result: AuthResult) -> LoginResponse:
    if result.session_token:
        _set_session_cookie(response, result.session_token)
    return result.response


def _frontend_url(path: str, params: dict[str, str] | None = None) -> str:
    base = config.frontend_base_url or "http://localhost:3000"
    query = f"?{urlencode(params)}" if params else ""
    return f"{base}{path}{query}"


def _is_browser_navigation(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept


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

    @router.post("/auth/register", response_model=LoginResponse)
    def register(
        payload: RegisterRequest,
        request: Request,
        response: Response,
        service: AuthService = Depends(get_auth_service),
    ) -> LoginResponse:
        return _apply_auth_result(response, service.register(payload, request=request))

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

    @router.post("/auth/mfa/enable", response_model=RecoveryCodesResponse)
    def mfa_enable(
        payload: MFACodeRequest,
        request: Request,
        user: AuthUser = Depends(require_authenticated_user),
        service: AuthService = Depends(get_auth_service),
    ) -> RecoveryCodesResponse:
        updated, recovery_codes = service.enable_mfa(user, payload.code, request=request)
        return RecoveryCodesResponse(
            mfa_enabled=True,
            recovery_codes=recovery_codes,
        )

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

    @router.post("/auth/mfa/recovery-codes/regenerate", response_model=RecoveryCodesResponse)
    def mfa_regenerate_recovery_codes(
        request: Request,
        user: AuthUser = Depends(require_authenticated_user),
        service: AuthService = Depends(get_auth_service),
    ) -> RecoveryCodesResponse:
        if not user.mfa_enabled:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not enabled")
        codes = service.regenerate_recovery_codes(user, request=request)
        return RecoveryCodesResponse(
            mfa_enabled=True,
            recovery_codes=codes,
        )

    @router.get("/auth/google/login")
    def google_login(
        request: Request,
        service: AuthService = Depends(get_auth_service),
    ):
        try:
            url, state = service.google_login_url(request=request)
        except HTTPException as exc:
            if _is_browser_navigation(request):
                reason = "not_configured" if exc.status_code == 503 else "disabled"
                return RedirectResponse(
                    url=_frontend_url("/login", {"google": reason}),
                    status_code=303,
                )
            raise exc
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

    @router.get("/auth/google/status", response_model=GoogleAuthStatusResponse)
    def google_status() -> GoogleAuthStatusResponse:
        configured = bool(config.google_client_id and config.google_client_secret)
        return GoogleAuthStatusResponse(
            enabled=config.google_oauth_enabled,
            configured=config.google_oauth_enabled and configured,
            auto_create_users=config.google_auto_create_users,
            redirect_uri=config.google_redirect_uri,
        )

    @router.get("/auth/google/callback")
    def google_callback(
        request: Request,
        code: str = Query(default=""),
        state: str = Query(default=""),
        service: AuthService = Depends(get_auth_service),
    ):
        try:
            result = service.google_callback(
                code=code,
                state=state,
                cookie_state=request.cookies.get(GOOGLE_STATE_COOKIE),
                request=request,
            )
        except GoogleOAuthFlowError as exc:
            if _is_browser_navigation(request):
                params = {"google": "failed", "reason": exc.reason}
                if exc.stage:
                    params["stage"] = exc.stage
                redirect = RedirectResponse(
                    url=_frontend_url("/login", params),
                    status_code=303,
                )
                redirect.delete_cookie(GOOGLE_STATE_COOKIE, path="/auth/google")
                return redirect
            raise HTTPException(status_code=exc.status_code, detail={"code": exc.reason, "message": exc.detail}) from exc
        except HTTPException as exc:
            if _is_browser_navigation(request):
                redirect = RedirectResponse(
                    url=_frontend_url("/login", {"google": "failed", "reason": "unknown"}),
                    status_code=303,
                )
                redirect.delete_cookie(GOOGLE_STATE_COOKIE, path="/auth/google")
                return redirect
            raise exc

        if result.session_token:
            redirect = RedirectResponse(
                url=_frontend_url("/family-console", {"auth": "google"}),
                status_code=303,
            )
            _set_session_cookie(redirect, result.session_token)
            redirect.delete_cookie(GOOGLE_STATE_COOKIE, path="/auth/google")
            return redirect

        redirect = RedirectResponse(
            url=_frontend_url("/login", {"google": "mfa_required"}),
            status_code=303,
        )
        redirect.delete_cookie(GOOGLE_STATE_COOKIE, path="/auth/google")
        return redirect

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
