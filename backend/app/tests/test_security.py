from fastapi.testclient import TestClient

from app.core import config
from main import app

client = TestClient(app)


def test_health_endpoint_no_api_key():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_endpoint_requires_api_key_when_enabled():
    original_enabled = config.api_key_enabled
    original_key = config.cyberalerta_api_key
    try:
        config.api_key_enabled = True
        config.cyberalerta_api_key = "dev-change-me"

        response = client.get("/guardian-console/status")
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"
    finally:
        config.api_key_enabled = original_enabled
        config.cyberalerta_api_key = original_key


def test_protected_endpoint_rejects_invalid_api_key_when_enabled():
    original_enabled = config.api_key_enabled
    original_key = config.cyberalerta_api_key
    try:
        config.api_key_enabled = True
        config.cyberalerta_api_key = "dev-change-me"

        response = client.get(
            "/guardian-console/status",
            headers={"X-CyberAlerta-API-Key": "wrong-key"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"
    finally:
        config.api_key_enabled = original_enabled
        config.cyberalerta_api_key = original_key


def test_protected_endpoint_accepts_valid_api_key_when_enabled():
    original_enabled = config.api_key_enabled
    original_key = config.cyberalerta_api_key
    try:
        config.api_key_enabled = True
        config.cyberalerta_api_key = "dev-change-me"

        response = client.get(
            "/guardian-console/status",
            headers={"X-CyberAlerta-API-Key": "dev-change-me"},
        )
        assert response.status_code == 200
    finally:
        config.api_key_enabled = original_enabled
        config.cyberalerta_api_key = original_key


def test_cors_allows_local_origin():
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_analyze_payload_too_long_returns_400():
    original_max = config.max_message_length
    try:
        config.max_message_length = 5
        payload = {
            "user_name": "Maria",
            "age_group": "adult",
            "trusted_contact_name": "João",
            "trusted_contact_relation": "filho",
            "action_type": "pix",
            "channel": "whatsapp",
            "message": "mensagem muito longa",
            "already_acted": False,
        }

        response = client.post("/analyze", json=payload)
        assert response.status_code in {400, 413}
        detail = response.json().get("detail", "")
        assert "exceeds max length" in detail or "too large" in detail.lower()
    finally:
        config.max_message_length = original_max
