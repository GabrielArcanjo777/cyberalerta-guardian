from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_guardian_console_status():
    response = client.get("/guardian-console/status")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "guardian-admin-case-console"
    assert body["auth_enabled"] is False
    assert body["case_count"] >= 3


def test_guardian_console_list_cases():
    response = client.get("/guardian-console/cases")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 3
    assert body["cases"][0]["case_id"]


def test_guardian_console_case_detail():
    response = client.get("/guardian-console/cases/case-demo-001")
    assert response.status_code == 200
    body = response.json()
    assert body["protected_person_alias"] == "Dona Lucia"
    assert body["risk_level"] == "alto"
    assert len(body["agent_decision_trace"]) >= 2


def test_guardian_console_update_status():
    response = client.patch(
        "/guardian-console/cases/case-demo-002/status",
        json={"status": "verified_safe"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "verified_safe"


def test_guardian_console_from_channel():
    response = client.post(
        "/guardian-console/cases/from-channel",
        json={
            "protected_person_alias": "Dona Lucia",
            "guardian_alias": "Gabriel",
            "source_channel": "whatsapp_mock",
            "received_content_summary": "Pix urgente de numero novo.",
            "risk_score": 88,
            "risk_level": "alto",
            "scam_category": "golpe_pix",
            "detected_signals": ["urgencia", "pedido_pix"],
            "agent_decision": "Trust Lock recomendado.",
            "recommended_action": "Confirmar antes do Pix.",
            "trust_lock_status": "recommended",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["case_id"].startswith("case-")
    assert body["status"] == "open"


def test_simple_channel_creates_guardian_case():
    response = client.post(
        "/simple-channel/submit",
        json={
            "protected_person_alias": "Dona Lucia",
            "channel": "whatsapp_mock",
            "content_type": "text",
            "content": "Mae, troquei de numero. Preciso fazer um Pix urgente.",
            "consent": True,
            "trusted_contact_alias": "Gabriel",
        },
    )
    assert response.status_code == 200
    assert response.json()["admin_case_created"] is True

    cases = client.get("/guardian-console/cases").json()["cases"]
    assert any(case["protected_person_alias"] == "Dona Lucia" for case in cases)
