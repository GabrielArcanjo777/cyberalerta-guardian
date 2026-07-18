"""Real FCM HTTP v1 sender. Uses google-auth (already a runtime dependency for
Google OIDC) for the service-account OAuth2 bearer token, and requests (also
already a dependency) for the HTTP call — no new packages needed.
"""

from __future__ import annotations

import json

import google.auth.transport.requests
import requests
from google.oauth2 import service_account

from app.notifications.contract import PushProviderError, PushProviderTokenInvalid

_FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
_UNREGISTERED_MARKERS = ("UNREGISTERED", "NOT_FOUND")


class FCMHttpSender:
    name = "fcm"

    def __init__(self, *, project_id: str, service_account_json: str, timeout_seconds: float = 10.0) -> None:
        self._url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        self._timeout = timeout_seconds
        try:
            info = json.loads(service_account_json)
            self._credentials = service_account.Credentials.from_service_account_info(
                info, scopes=[_FCM_SCOPE]
            )
        except (ValueError, KeyError) as exc:
            # Never let a malformed FCM_SERVICE_ACCOUNT_JSON leak into the
            # exception message — it may contain the private key.
            raise PushProviderError("Invalid FCM service account configuration.") from exc

    def _access_token(self) -> str:
        if not self._credentials.valid:
            self._credentials.refresh(google.auth.transport.requests.Request())
        return self._credentials.token

    def send(self, *, token: str, payload: dict) -> None:
        # FCM "data" messages require every value to be a string.
        data = {key: str(value) for key, value in payload.items() if value is not None}
        body = {"message": {"token": token, "data": data}}
        try:
            response = requests.post(
                self._url,
                json=body,
                headers={"Authorization": f"Bearer {self._access_token()}"},
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise PushProviderError(f"FCM request failed: {type(exc).__name__}") from exc

        if response.status_code == 404:
            raise PushProviderTokenInvalid("FCM token no longer registered.")
        if response.status_code == 400 and any(marker in response.text for marker in _UNREGISTERED_MARKERS):
            raise PushProviderTokenInvalid("FCM token no longer registered.")
        if response.status_code >= 400:
            raise PushProviderError(f"FCM responded with status {response.status_code}.")
