from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

SAMPLE_PAYLOAD = {
    "protected_person_alias": "Dona Lucia",
    "channel": "whatsapp_mock",
    "content_type": "text",
    "content": "Mae, troquei de numero. Preciso fazer um Pix urgente.",
    "consent": True,
}


def test_simple_channel_status():
    response = client.get("/simple-channel/status")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "simple-channel-intake"
    assert body["whatsapp_real_enabled"] is False
    assert body["monitoring_enabled"] is False
    assert "whatsapp_mock" in body["channels"]


def test_simple_channel_submit_requires_consent():
    payload = {**SAMPLE_PAYLOAD, "consent": False}
    response = client.post("/simple-channel/submit", json=payload)
    assert response.status_code == 400


def test_simple_channel_submit_success():
    response = client.post("/simple-channel/submit", json=SAMPLE_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["channel_case_id"].startswith("ch-")
    assert body["risk_level"] in {"baixo", "medio", "alto", "critico"}
    assert body["simple_reply"]
    assert body["admin_case_created"] is True
    assert body["trust_lock_recommended"] is True
    assert "Pix" in body["simple_reply"] or "golpe" in body["simple_reply"].lower()
