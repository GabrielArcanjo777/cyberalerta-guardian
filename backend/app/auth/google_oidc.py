from __future__ import annotations

import time
from typing import Any

from app.core.config import config

GOOGLE_ISSUERS = {"https://accounts.google.com", "accounts.google.com"}


class GoogleOidcError(Exception):
    def __init__(self, reason: str, detail: str | None = None) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(reason)


def verify_google_id_token(id_token: str, *, expected_nonce: str | None = None) -> dict[str, Any]:
    if not config.google_client_id:
        raise GoogleOidcError("not_configured", "Google OAuth not configured")
    try:
        from google.auth.transport.requests import Request as GoogleRequest
        from google.oauth2.id_token import verify_oauth2_token
        payload = verify_oauth2_token(id_token, GoogleRequest(), audience=config.google_client_id)
    except GoogleOidcError:
        raise
    except Exception as exc:
        raise GoogleOidcError("invalid_token", str(exc)) from exc
    if not isinstance(payload, dict):
        raise GoogleOidcError("invalid_payload")
    iss = payload.get("iss")
    if iss not in GOOGLE_ISSUERS:
        raise GoogleOidcError("invalid_issuer", str(iss))
    if payload.get("aud") != config.google_client_id:
        raise GoogleOidcError("invalid_audience")
    exp = int(payload.get("exp", 0))
    if exp < int(time.time()):
        raise GoogleOidcError("token_expired")
    iat = int(payload.get("iat", 0))
    if iat > int(time.time()) + 60:
        raise GoogleOidcError("invalid_iat")
    if str(payload.get("email_verified")).lower() != "true":
        raise GoogleOidcError("email_not_verified")
    if expected_nonce and payload.get("nonce") != expected_nonce:
        raise GoogleOidcError("invalid_nonce")
    return payload
