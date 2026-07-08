"""Fase 2 — Evolution instance client (QR pairing, status, reconnect).

Uses a fake transport so no network/Evolution server is needed.
"""

from __future__ import annotations

from typing import Any, Mapping, Tuple

from app.channel_adapters.evolution_demo_adapter import EvolutionDemoConfig
from app.integrations.evolution.instance_client import EvolutionInstanceClient


class FakeTransport:
    def __init__(self, responses: dict[str, Tuple[int, Mapping[str, Any]]], raise_on: set[str] | None = None):
        self._responses = responses
        self._raise_on = raise_on or set()
        self.calls: list[tuple[str, str]] = []

    def request(self, *, method: str, url: str, api_key: str, timeout: float):
        self.calls.append((method, url))
        for suffix, resp in self._responses.items():
            if suffix in url:
                if suffix in self._raise_on:
                    raise ConnectionError("boom")
                return resp
        return (404, {})


def _cfg(**over) -> EvolutionDemoConfig:
    base = dict(api_url="http://evolution.local", api_key="k", instance_name="guardian-demo")
    base.update(over)
    return EvolutionDemoConfig(**base)


def test_not_configured_reports_setup_needed():
    client = EvolutionInstanceClient(_cfg(api_url=None), transport=FakeTransport({}))
    state = client.connection_state()
    assert state.configured is False
    assert state.state == "not_configured"
    assert state.official is False


def test_open_session_is_connected_and_needs_no_qr():
    transport = FakeTransport({"connectionState/guardian-demo": (200, {"instance": {"state": "open"}})})
    client = EvolutionInstanceClient(_cfg(), transport=transport)

    assert client.connection_state().connected is True
    qr = client.get_qr()
    assert qr.connected is True
    assert qr.qr_base64 is None
    # get_qr must NOT hit the connect endpoint when already open
    assert all("/instance/connect/" not in url for _, url in transport.calls)


def test_disconnected_session_returns_qr_code():
    transport = FakeTransport(
        {
            "connectionState/guardian-demo": (200, {"instance": {"state": "connecting"}}),
            "connect/guardian-demo": (200, {"base64": "data:image/png;base64,AAAA", "code": "PAIR-123"}),
        }
    )
    client = EvolutionInstanceClient(_cfg(), transport=transport)

    qr = client.get_qr()
    assert qr.connected is False
    assert qr.qr_base64 == "data:image/png;base64,AAAA"
    assert qr.pairing_code == "PAIR-123"


def test_unreachable_evolution_is_reported_not_crashed():
    transport = FakeTransport(
        {"connectionState/guardian-demo": (200, {})}, raise_on={"connectionState/guardian-demo"}
    )
    client = EvolutionInstanceClient(_cfg(), transport=transport)
    state = client.connection_state()
    assert state.state == "unreachable"
    assert state.connected is False


def test_reconnect_restarts_then_fetches_qr():
    transport = FakeTransport(
        {
            "restart/guardian-demo": (200, {"status": "ok"}),
            "connectionState/guardian-demo": (200, {"instance": {"state": "connecting"}}),
            "connect/guardian-demo": (200, {"base64": "data:image/png;base64,BBBB"}),
        }
    )
    client = EvolutionInstanceClient(_cfg(), transport=transport)

    state = client.reconnect()
    assert any(method == "POST" and "restart/guardian-demo" in url for method, url in transport.calls)
    assert state.qr_base64 == "data:image/png;base64,BBBB"


def test_ensure_connected_reconnects_when_closed():
    transport = FakeTransport(
        {
            "connectionState/guardian-demo": (200, {"instance": {"state": "close"}}),
            "restart/guardian-demo": (200, {"status": "ok"}),
            "connect/guardian-demo": (200, {"base64": "data:image/png;base64,CCCC"}),
        }
    )
    client = EvolutionInstanceClient(_cfg(), transport=transport)

    state = client.ensure_connected()
    assert any("restart/guardian-demo" in url for _, url in transport.calls)
    assert state.qr_base64 == "data:image/png;base64,CCCC"
