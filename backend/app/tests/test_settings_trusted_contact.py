from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import main
from app.core.config import config
from app.storage import settings_store
from main import app

ENDPOINT = "/settings/trusted-contact"


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_state():
    """Endpoints mutate process-wide singletons; snapshot and restore them so
    tests stay isolated from each other and from the rest of the suite."""
    before = {
        "trusted_contact": config.trusted_contact,
        "protected_number": config.protected_number,
        "dry_run": config.dry_run,
        "real_send": config.beta_real_send_enabled,
        "guardian_address": main.evolution_demo_service.guardian_address,
        "default_guardian_address": main.dual_bot_service.default_guardian_address,
        "adapter_config": main.evolution_demo_service.adapter.config,
        "service_config": main.evolution_demo_service.config,
        "stored": settings_store.get("trusted_contact"),
        "stored_protected": settings_store.get("protected_number"),
    }
    yield
    config.trusted_contact = before["trusted_contact"]
    config.protected_number = before["protected_number"]
    config.dry_run = before["dry_run"]
    config.beta_real_send_enabled = before["real_send"]
    main.evolution_demo_service.guardian_address = before["guardian_address"]
    main.dual_bot_service.default_guardian_address = before["default_guardian_address"]
    main.evolution_demo_service.adapter.config = before["adapter_config"]
    main.evolution_demo_service.config = before["service_config"]
    if before["stored"] is not None:
        settings_store.put("trusted_contact", before["stored"])
    if before["stored_protected"] is not None:
        settings_store.put("protected_number", before["stored_protected"])


def test_get_returns_current_settings(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"protected_number", "trusted_contact", "dry_run", "beta_real_send_enabled"}
    assert body["trusted_contact"] == config.trusted_contact
    assert body["protected_number"] == config.protected_number
    assert isinstance(body["dry_run"], bool)
    assert isinstance(body["beta_real_send_enabled"], bool)


def test_put_protected_number_updates_and_persists(client: TestClient):
    response = client.put(ENDPOINT, json={"protected_number": "+5511977776666"})
    assert response.status_code == 200
    assert response.json()["protected_number"] == "+5511977776666"
    assert config.protected_number == "+5511977776666"
    assert settings_store.get("protected_number") == "+5511977776666"


def test_put_rejects_malformed_protected_number(client: TestClient):
    response = client.put(ENDPOINT, json={"protected_number": "abc"})
    assert response.status_code == 422


def test_put_both_numbers_together(client: TestClient):
    response = client.put(ENDPOINT, json={
        "protected_number": "+5511977776666",
        "trusted_contact": "+5511999990001",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["protected_number"] == "+5511977776666"
    assert body["trusted_contact"] == "+5511999990001"


def test_put_only_trusted_leaves_protected_untouched(client: TestClient):
    client.put(ENDPOINT, json={"protected_number": "+5511977776666"})
    client.put(ENDPOINT, json={"trusted_contact": "+5511999990001"})
    assert config.protected_number == "+5511977776666"


def test_toggle_dry_run_updates_runtime_and_persists(client: TestClient):
    response = client.put(ENDPOINT, json={"dry_run": False})
    assert response.status_code == 200
    assert response.json()["dry_run"] is False
    assert config.dry_run is False
    assert main.evolution_demo_service.adapter.config.dry_run is False
    assert settings_store.get("dry_run") == "false"

    response = client.put(ENDPOINT, json={"dry_run": True})
    assert response.json()["dry_run"] is True
    assert main.evolution_demo_service.adapter.config.dry_run is True


def test_toggle_real_send_pins_allowlist_to_trusted_contact(client: TestClient):
    client.put(ENDPOINT, json={"trusted_contact": "+5511999990001"})
    response = client.put(ENDPOINT, json={"dry_run": False, "beta_real_send_enabled": True})
    assert response.status_code == 200

    adapter_cfg = main.evolution_demo_service.adapter.config
    assert adapter_cfg.real_send_enabled is True
    # Invariante inviolável: a allowlist fica cravada no contato de confiança.
    assert adapter_cfg.allowed_recipients == ("+5511999990001",)
    # O gate libera SOMENTE o contato de confiança; qualquer outro número
    # (por ex. o remetente) continua bloqueado.
    assert adapter_cfg.real_send_blocked_reason("+5511999990001") is None
    assert adapter_cfg.real_send_blocked_reason("+5511977776666") == "recipient_not_allowed"


def test_toggle_rejects_non_boolean(client: TestClient):
    assert client.put(ENDPOINT, json={"dry_run": "sim"}).status_code == 422
    assert client.put(ENDPOINT, json={"beta_real_send_enabled": 1}).status_code == 422


def test_put_valid_number_updates_and_propagates(client: TestClient):
    response = client.put(ENDPOINT, json={"trusted_contact": "+5511999990001"})
    assert response.status_code == 200
    assert response.json()["trusted_contact"] == "+5511999990001"

    # Runtime config and both service singletons are updated in place.
    assert config.trusted_contact == "+5511999990001"
    assert main.evolution_demo_service.guardian_address == "+5511999990001"
    assert main.dual_bot_service.default_guardian_address == "+5511999990001"


def test_put_persists_to_settings_store(client: TestClient):
    client.put(ENDPOINT, json={"trusted_contact": "+5521988887777"})
    # Value is written to the store so it survives a backend restart.
    assert settings_store.get("trusted_contact") == "+5521988887777"


def test_put_rejects_malformed_number(client: TestClient):
    response = client.put(ENDPOINT, json={"trusted_contact": "not-a-phone"})
    assert response.status_code == 422
    # State is left untouched when validation fails.
    assert config.trusted_contact != "not-a-phone"


def test_put_rejects_too_short_number(client: TestClient):
    response = client.put(ENDPOINT, json={"trusted_contact": "+55119"})
    assert response.status_code == 422


def test_put_empty_clears_contact(client: TestClient):
    client.put(ENDPOINT, json={"trusted_contact": "+5511999990001"})
    response = client.put(ENDPOINT, json={"trusted_contact": ""})
    assert response.status_code == 200
    assert response.json()["trusted_contact"] == ""
    assert config.trusted_contact == ""
    # With no contact, the demo service falls back to simulated alerts.
    assert main.evolution_demo_service.guardian_address is None


def test_put_accepts_number_without_plus(client: TestClient):
    response = client.put(ENDPOINT, json={"trusted_contact": "5511999990001"})
    assert response.status_code == 200
    assert response.json()["trusted_contact"] == "5511999990001"


def test_put_missing_field_treated_as_empty(client: TestClient):
    response = client.put(ENDPOINT, json={})
    assert response.status_code == 200
    assert response.json()["trusted_contact"] == ""
