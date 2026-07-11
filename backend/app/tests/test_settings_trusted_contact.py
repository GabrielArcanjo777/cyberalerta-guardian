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
        "guardian_address": main.evolution_demo_service.guardian_address,
        "default_guardian_address": main.dual_bot_service.default_guardian_address,
        "stored": settings_store.get("trusted_contact"),
    }
    yield
    config.trusted_contact = before["trusted_contact"]
    main.evolution_demo_service.guardian_address = before["guardian_address"]
    main.dual_bot_service.default_guardian_address = before["default_guardian_address"]
    if before["stored"] is not None:
        settings_store.put("trusted_contact", before["stored"])


def test_get_returns_current_settings(client: TestClient):
    response = client.get(ENDPOINT)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"trusted_contact", "dry_run", "beta_real_send_enabled"}
    assert body["trusted_contact"] == config.trusted_contact
    assert isinstance(body["dry_run"], bool)
    assert isinstance(body["beta_real_send_enabled"], bool)


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
