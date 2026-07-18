from __future__ import annotations

from typing import Protocol, runtime_checkable


class PushProviderError(Exception):
    """Provider-level failure (network, HTTP, malformed transport response).

    Mirrors app.llm.contract.LLMProviderError: the message must never contain
    the FCM service-account key or the push token itself.
    """


class PushProviderTokenInvalid(PushProviderError):
    """FCM reports the token as unregistered/invalid — the caller should drop
    it (Secao 5.2, "notifications": ... cleanup de token invalido)."""


@runtime_checkable
class PushSender(Protocol):
    """Sends one push message to one device token. Implementations raise
    PushProviderError/PushProviderTokenInvalid on failure and never decide
    retries themselves — that is the caller's job."""

    name: str

    def send(self, *, token: str, payload: dict) -> None: ...
