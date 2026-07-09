"""Fase 4 — rate-limit anti-spoofing and security headers."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import config
from app.core.security import _client_identifier
from main import app


class _FakeClient:
    def __init__(self, host: str | None):
        self.host = host


class _FakeRequest:
    def __init__(self, headers: dict, host: str | None):
        self.headers = headers
        self.client = _FakeClient(host)


def test_forwarded_for_ignored_from_untrusted_peer(monkeypatch):
    monkeypatch.setattr(config, "trusted_webhook_ips", [])
    request = _FakeRequest({"X-Forwarded-For": "1.2.3.4"}, "203.0.113.9")
    # Spoofed header must be ignored — the real peer IP is used instead.
    assert _client_identifier(request) == "203.0.113.9"


def test_forwarded_for_honored_from_trusted_proxy(monkeypatch):
    monkeypatch.setattr(config, "trusted_webhook_ips", ["203.0.113.9"])
    request = _FakeRequest({"X-Forwarded-For": "1.2.3.4"}, "203.0.113.9")
    assert _client_identifier(request) == "1.2.3.4"


def test_security_headers_are_present():
    client = TestClient(app)
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_hsts_absent_when_cookies_not_secure(monkeypatch):
    monkeypatch.setattr(config, "auth_cookie_secure", False)
    client = TestClient(app)
    response = client.get("/health")
    assert "Strict-Transport-Security" not in response.headers
