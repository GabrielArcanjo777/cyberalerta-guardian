from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.auth.models import AuthAuditLog, PublicUser, UserRole


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class LoginResponse(BaseModel):
    authenticated: bool = False
    mfa_required: bool = False
    temporary_token: Optional[str] = None
    mfa_setup_required: bool = False
    user: Optional[PublicUser] = None


class LogoutResponse(BaseModel):
    status: str = "ok"


class MeResponse(BaseModel):
    authenticated: bool
    user: Optional[PublicUser] = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=1, max_length=256)


class MFASetupResponse(BaseModel):
    otpauth_uri: str
    qr_code_base64: str
    manual_secret: str


class MFACodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=12)


class MFAVerifyRequest(BaseModel):
    temporary_token: str = Field(min_length=1)
    code: str = Field(min_length=6, max_length=12)


class MFAStatusResponse(BaseModel):
    status: str = "ok"
    mfa_enabled: bool


class MFADisableRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)
    code: Optional[str] = Field(default=None, min_length=6, max_length=12)


class AdminUserItem(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_admin: bool
    mfa_enabled: bool


class AdminUsersResponse(BaseModel):
    users: list[AdminUserItem]


class AdminAuditLogsResponse(BaseModel):
    logs: list[AuthAuditLog]
