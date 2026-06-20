from fastapi.testclient import TestClient

from app.core import config
from app.core.security import rate_limiter
from main import app

client = TestClient(app)


def _analysis_payload(message: str = "Mae, troquei de numero. Preciso de Pix urgente.") -> dict:
    return {
        "user_name": "Maria",
        "age_group": "adult",
        "trusted_contact_name": "Joao",
        "trusted_contact_relation": "filho",
        "action_type": "pix",
        "channel": "whatsapp",
        "message": message,
        "already_acted": False,
    }


def _n8n_payload(
    message: str = "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
    message_id: str = "n8n-test-message-1",
) -> dict:
    return {
        "message_id": message_id,
        "from": "masked-contact",
        "to": "sandbox-number",
        "body": message,
        "channel": "whatsapp",
        "provider": "webhook_test",
        "protected_person_alias": "Dona Lucia",
        "guardian_alias": "Gabriel",
        "guardian_address": "guardian-masked",
        "dry_run": True,
    }


def test_health_endpoint_no_api_key():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_security_headers_are_added():
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert response.headers["X-Request-ID"].startswith("req-")


def test_request_id_header_is_preserved():
    response = client.get("/health", headers={"X-Request-ID": "req-preserved-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-preserved-123"


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
    assert response.headers["access-control-allow-origin"] != "*"


def test_cors_allows_local_n8n_origin():
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:5678"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5678"


def test_analyze_empty_message_returns_422():
    response = client.post("/analyze", json=_analysis_payload("   "))
    assert response.status_code == 422
    assert "cannot be empty" in response.json()["detail"]


def test_analyze_payload_too_long_returns_413():
    original_max = config.max_message_length
    try:
        config.max_message_length = 5
        response = client.post("/analyze", json=_analysis_payload("mensagem muito longa"))
        assert response.status_code == 413
        assert "exceeds max length" in response.json()["detail"]
    finally:
        config.max_message_length = original_max


def test_n8n_endpoint_requires_secret_when_configured():
    original_secret = config.n8n_webhook_secret
    try:
        config.n8n_webhook_secret = "n8n-test-secret"

        response = client.post("/integrations/n8n/whatsapp/inbound", json=_n8n_payload())
        assert response.status_code == 401

        response = client.post(
            "/integrations/n8n/whatsapp/inbound",
            json=_n8n_payload(),
            headers={"X-N8N-CyberAlerta-Secret": "wrong-secret"},
        )
        assert response.status_code == 403
    finally:
        config.n8n_webhook_secret = original_secret


def test_n8n_endpoint_accepts_valid_secret_and_trace_headers():
    original_secret = config.n8n_webhook_secret
    try:
        config.n8n_webhook_secret = "n8n-test-secret"

        response = client.post(
            "/integrations/n8n/whatsapp/inbound",
            json=_n8n_payload("Mãe, troquei de número. Preciso de Pix urgente. Não liga agora."),
            headers={
                "X-N8N-CyberAlerta-Secret": "n8n-test-secret",
                "X-Request-ID": "req-test-123",
                "X-N8N-Execution-ID": "exec-test-123",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "processed"
        assert body["case_id"]
        assert body["risk_score"] >= 0
        assert body["n8n_action"] in {
            "activate_trust_lock",
            "alert_trusted_contact",
            "ask_for_confirmation",
            "start_recovery",
        }
        assert body["safe_to_send"] is True
        assert body["n8n_execution_id"] == "exec-test-123"
        assert response.headers["X-Request-ID"] == "req-test-123"
        assert response.headers["X-N8N-Execution-ID"] == "exec-test-123"
    finally:
        config.n8n_webhook_secret = original_secret


def test_n8n_endpoint_rejects_malformed_json():
    response = client.post(
        "/integrations/n8n/whatsapp/inbound",
        content="{",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "json_invalid"


def test_rate_limit_can_block_analyze_when_enabled():
    original_enabled = config.rate_limit_enabled
    original_limit = config.rate_limit_per_minute
    try:
        config.rate_limit_enabled = True
        config.rate_limit_per_minute = 1
        rate_limiter.reset()

        first = client.post("/analyze", json=_analysis_payload())
        second = client.post("/analyze", json=_analysis_payload("Banco falso pedindo codigo urgente."))

        assert first.status_code == 200
        assert second.status_code == 429
        assert second.json()["detail"] == "Rate limit exceeded."
    finally:
        config.rate_limit_enabled = original_enabled
        config.rate_limit_per_minute = original_limit
        rate_limiter.reset()
