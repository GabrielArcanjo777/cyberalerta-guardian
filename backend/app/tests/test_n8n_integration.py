import logging

from fastapi.testclient import TestClient

from app.core.config import config
from app.repositories import get_operational_state_repository
from main import app

client = TestClient(app)


def _payload(message_id: str, body: str, *, already_acted: bool = False) -> dict:
    return {
        "message_id": message_id,
        "from": "masked-whatsapp-contact",
        "to": "cyberalerta-demo",
        "body": body,
        "channel": "whatsapp",
        "user_name": "Dona Lucia",
        "trusted_contact_name": "Gabriel",
        "trusted_contact_relation": "filho",
        "already_acted": already_acted,
    }


def test_n8n_health_exposes_local_dry_run_contract():
    response = client.get("/integrations/n8n/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "n8n-integration"
    assert body["whatsapp_inbound_endpoint"] == "/integrations/n8n/whatsapp/inbound"
    assert body["auth_header"] == config.n8n_webhook_header
    assert body["production"] is False


def test_n8n_whatsapp_inbound_returns_actionable_dry_run_response():
    original_secret = config.n8n_webhook_secret
    try:
        config.n8n_webhook_secret = "n8n-test-secret"
        response = client.post(
            "/integrations/n8n/whatsapp/inbound",
            json=_payload(
                "n8n-integration-risk-1",
                "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
            ),
            headers={
                "X-N8N-CyberAlerta-Secret": "n8n-test-secret",
                "X-Request-ID": "req-n8n-risk-1",
                "X-N8N-Execution-ID": "exec-n8n-risk-1",
            },
        )
    finally:
        config.n8n_webhook_secret = original_secret

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "processed"
    assert body["case_id"].startswith("n8n-case-")
    assert body["risk_score"] >= 0
    assert body["n8n_action"] in {"activate_trust_lock", "alert_trusted_contact", "ask_for_confirmation"}
    assert body["trusted_contact_should_alert"] is True
    assert body["safe_to_send"] is True
    assert body["request_id"] == "req-n8n-risk-1"
    assert body["n8n_execution_id"] == "exec-n8n-risk-1"

    stored_case = get_operational_state_repository().cases.get(body["case_id"])
    assert stored_case is not None
    assert stored_case.n8n_action == body["n8n_action"]


def test_n8n_already_acted_maps_to_recovery_action():
    response = client.post(
        "/integrations/n8n/whatsapp/inbound",
        json=_payload(
            "n8n-integration-recovery-1",
            "Cliquei no link e passei o codigo que chegou por SMS.",
            already_acted=True,
        ),
        headers={"X-N8N-Execution-ID": "exec-n8n-recovery-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["n8n_action"] == "start_recovery"
    assert body["recovery_should_start"] is True


def test_n8n_duplicate_message_returns_previous_response():
    payload = _payload(
        "n8n-integration-duplicate-1",
        "Central falsa pedindo token urgente para regularizar acesso.",
    )

    first = client.post("/integrations/n8n/whatsapp/inbound", json=payload)
    second = client.post(
        "/integrations/n8n/whatsapp/inbound",
        json={**payload, "body": "Texto alterado que nao deve reprocessar"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()


def test_n8n_structured_logs_mask_phone_and_message(caplog):
    full_phone = "+5511999990001"
    full_message = "Mensagem sigilosa com Pix urgente e codigo que nao deve aparecer inteira no log"
    caplog.set_level(logging.INFO, logger="cyberalerta.n8n")

    response = client.post(
        "/integrations/n8n/whatsapp/inbound",
        json={**_payload("n8n-integration-logs-1", full_message), "from": full_phone},
        headers={"X-Request-ID": "req-n8n-logs-1", "X-N8N-Execution-ID": "exec-n8n-logs-1"},
    )

    assert response.status_code == 200
    logs = "\n".join(record.getMessage() for record in caplog.records if record.name == "cyberalerta.n8n")
    assert "n8n_inbound_received" in logs
    assert "n8n_response_prepared" in logs
    assert "req-n8n-logs-1" in logs
    assert "exec-n8n-logs-1" in logs
    assert full_phone not in logs
    assert "99999" not in logs
    assert full_message not in logs
