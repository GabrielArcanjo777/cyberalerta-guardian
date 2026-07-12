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


def test_evolution_webhook_without_secret_allowed_in_development(monkeypatch):
    monkeypatch.setattr(config, "evolution_webhook_secret", "")
    monkeypatch.setattr(config, "app_env", "development")
    client = TestClient(app)
    response = client.post("/webhook/evolution", json={})
    # Auth is bypassed in development; the request reaches payload handling.
    assert response.status_code not in (401, 403, 500)


def test_evolution_webhook_without_secret_rejected_in_production(monkeypatch):
    monkeypatch.setattr(config, "evolution_webhook_secret", "")
    monkeypatch.setattr(config, "app_env", "production")
    client = TestClient(app)
    response = client.post("/webhook/evolution", json={})
    assert response.status_code == 500


def test_evolution_webhook_rejects_wrong_secret(monkeypatch):
    monkeypatch.setattr(config, "evolution_webhook_secret", "top-secret")
    client = TestClient(app)
    response = client.post(
        "/webhook/evolution",
        json={},
        headers={"X-Evolution-Webhook-Secret": "wrong"},
    )
    assert response.status_code == 403


def test_evolution_webhook_accepts_correct_secret(monkeypatch):
    monkeypatch.setattr(config, "evolution_webhook_secret", "top-secret")
    client = TestClient(app)
    response = client.post(
        "/webhook/evolution",
        json={},
        headers={"X-Evolution-Webhook-Secret": "top-secret"},
    )
    assert response.status_code not in (401, 403, 500)


# -- production startup guards -------------------------------------------------


def test_production_refuses_empty_evolution_webhook_secret():
    """AppConfig must raise RuntimeError at import time when APP_ENV=production
    and EVOLUTION_WEBHOOK_SECRET is empty."""
    import os as _os

    _os.environ["APP_ENV"] = "production"
    _os.environ["EVOLUTION_WEBHOOK_SECRET"] = ""
    _os.environ["RATE_LIMIT_ENABLED"] = "true"  # satisfy the other prod guard
    try:
        from app.core.config import AppConfig

        AppConfig()
        pytest.fail("RuntimeError expected but not raised")
    except RuntimeError as exc:
        assert "EVOLUTION_WEBHOOK_SECRET" in str(exc)
    finally:
        _os.environ.pop("APP_ENV", None)
        _os.environ.pop("EVOLUTION_WEBHOOK_SECRET", None)
        _os.environ.pop("RATE_LIMIT_ENABLED", None)
        # The config module caches env reads — re-import is not enough.
        # For this test we construct a fresh AppConfig() which re-reads env.
        # The pop above restores the environment for subsequent tests.


def test_production_refuses_rate_limit_disabled():
    """AppConfig must raise RuntimeError when APP_ENV=production and
    RATE_LIMIT_ENABLED=false."""
    import os as _os

    _os.environ["APP_ENV"] = "production"
    _os.environ["RATE_LIMIT_ENABLED"] = "false"
    _os.environ["EVOLUTION_WEBHOOK_SECRET"] = "not-empty"
    try:
        from app.core.config import AppConfig

        AppConfig()
        pytest.fail("RuntimeError expected but not raised")
    except RuntimeError as exc:
        assert "RATE_LIMIT_ENABLED" in str(exc)
    finally:
        _os.environ.pop("APP_ENV", None)
        _os.environ.pop("RATE_LIMIT_ENABLED", None)
        _os.environ.pop("EVOLUTION_WEBHOOK_SECRET", None)


# -- idempotency TTL + bounded growth -------------------------------------------


import time as _time
from app.channel_adapters.idempotency import InMemoryProviderMessageRegistry
from app.channel_adapters.models import ChannelProvider, InboundMessage


def _make_inbound(message_id: str, provider: ChannelProvider = ChannelProvider.EVOLUTION_DEMO) -> InboundMessage:
    return InboundMessage(
        provider=provider,
        external_message_id=message_id,
        from_address="5511900000000",
        to_address="5511900000001",
        body="test",
        timestamp=_time.time(),
    )


def test_idempotency_rejects_duplicate_within_ttl():
    reg = InMemoryProviderMessageRegistry(ttl_seconds=60, max_size=100)
    incoming = _make_inbound("dup-001")
    assert reg.register_inbound(incoming) is True
    assert reg.register_inbound(incoming) is False  # duplicate within TTL


def test_idempotency_expires_after_ttl():
    reg = InMemoryProviderMessageRegistry(ttl_seconds=2, max_size=100)
    incoming = _make_inbound("expire-me")
    assert reg.register_inbound(incoming) is True  # first seen
    # Simulate a short TTL passage — since register_inbound uses time.monotonic()
    # we mutate _seen directly to "age" the entry.
    key = (ChannelProvider.EVOLUTION_DEMO, "expire-me")
    reg._seen[key] = _time.monotonic() - 10  # 10 seconds in the past
    assert reg.register_inbound(incoming) is True  # expired → seen again as new


def test_idempotency_evicts_oldest_when_over_max_size():
    """When max_size is exceeded, the oldest entries by insertion order are
    evicted *before* the new entry is inserted, so the new entry is always
    accepted even when the registry is full."""
    reg = InMemoryProviderMessageRegistry(ttl_seconds=3600, max_size=3)
    # Fill to max
    for i in range(3):
        assert reg.register_inbound(_make_inbound(f"old-{i}")) is True
    assert len(reg._seen) == 3
    # Inserting a 4th entry must evict the oldest (old-0)
    assert reg.register_inbound(_make_inbound("new-1")) is True
    # old-0 should be gone, others remain
    assert not reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "old-0")
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "old-1")
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "old-2")
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "new-1")
    assert len(reg._seen) == 3


def test_max_size_is_never_exceeded_after_register():
    """After every register_inbound() the internal size must be ≤ max_size."""
    reg = InMemoryProviderMessageRegistry(ttl_seconds=3600, max_size=1)
    assert reg.register_inbound(_make_inbound("a")) is True
    assert len(reg._seen) == 1
    assert reg.register_inbound(_make_inbound("b")) is True
    assert len(reg._seen) == 1
    assert not reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "a")
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "b")


def test_has_seen_is_read_only():
    """has_seen must never mutate the registry."""
    reg = InMemoryProviderMessageRegistry(ttl_seconds=1, max_size=10)
    reg.register_inbound(_make_inbound("msg-1"))
    # Age the entry past TTL
    key = (ChannelProvider.EVOLUTION_DEMO, "msg-1")
    old_ts = _time.monotonic() - 10
    reg._seen[key] = old_ts
    # has_seen must return False but NOT remove the expired entry
    snapshot = len(reg._seen)
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "msg-1") is False
    assert len(reg._seen) == snapshot  # read-only invariant


def test_different_providers_do_not_collide():
    reg = InMemoryProviderMessageRegistry(ttl_seconds=60, max_size=100)
    assert reg.register_inbound(_make_inbound("same-id", ChannelProvider.EVOLUTION_DEMO)) is True
    # Same ID on different provider is a different message
    assert reg.register_inbound(_make_inbound("same-id", ChannelProvider.MOCK)) is True
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "same-id") is True
    assert reg.has_seen(ChannelProvider.MOCK, "same-id") is True


def test_timestamp_zero_is_treated_as_existing_entry(monkeypatch):
    """A timestamp of 0.0 (which is falsy) must be treated as a valid entry,
    never confused with 'not present'."""
    # Pin time.monotonic() to a small value so 0.0 is within TTL of 60s
    monkeypatch.setattr(_time, "monotonic", lambda: 10.0)
    reg = InMemoryProviderMessageRegistry(ttl_seconds=60, max_size=100)
    key = (ChannelProvider.EVOLUTION_DEMO, "zero-ts")
    # Inject a valid entry at timestamp 0.0
    reg._seen[key] = 0.0
    # has_seen must recognise the entry (0.0 is not None)
    assert reg.has_seen(ChannelProvider.EVOLUTION_DEMO, "zero-ts") is True
    # register_inbound must reject it as a duplicate
    inbound = _make_inbound("zero-ts", ChannelProvider.EVOLUTION_DEMO)
    assert reg.register_inbound(inbound) is False
    # TTL must be calculated correctly from 0.0: the entry is within 60s
    assert len(reg._seen) == 1
