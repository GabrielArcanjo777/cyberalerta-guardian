from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_trusted_circle_status():
    response = client.get("/trusted-circle/status")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "trusted-circle-escalation"
    assert body["real_notifications_enabled"] is False


def test_trusted_circle_escalate_high_risk():
    response = client.post(
        "/trusted-circle/escalate",
        json={
            "case_id": "case-demo-001",
            "risk_level": "alto",
            "protected_person_alias": "Dona Lucia",
            "trusted_contacts": ["Gabriel", "Marcia"],
            "reason": "pedido de Pix urgente com identidade não verificada",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "simulated_notified"
    assert body["sent_real_notification"] is False
    assert body["proof_of_trust_recommended"] is True
    assert "Gabriel" in body["trusted_contacts"]
    assert "Dona Lucia" in body["message_to_guardian"]

    detail = client.get(f"/trusted-circle/escalations/{body['escalation_id']}")
    assert detail.status_code == 200
    assert detail.json()["case_id"] == "case-demo-001"

    case = client.get("/guardian-console/cases/case-demo-001").json()
    assert case["trusted_circle_status"] == "simulated_notified"


def test_trusted_circle_low_risk_not_escalated():
    response = client.post(
        "/trusted-circle/escalate",
        json={
            "case_id": "case-demo-002",
            "risk_level": "baixo",
            "protected_person_alias": "Seu Joao",
            "trusted_contacts": ["Gabriel"],
            "reason": "mensagem genérica sem urgência",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_escalated"
    assert body["sent_real_notification"] is False
    assert body["proof_of_trust_recommended"] is False


def test_trusted_circle_medium_risk_review_suggested():
    response = client.post(
        "/trusted-circle/escalate",
        json={
            "case_id": "case-demo-002",
            "risk_level": "medio",
            "protected_person_alias": "Seu Joao",
            "trusted_contacts": ["Gabriel"],
            "reason": "link suspeito fingindo ser banco",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "review_suggested"
    assert body["sent_real_notification"] is False


def test_trusted_circle_escalation_not_found():
    response = client.get("/trusted-circle/escalations/esc-missing")
    assert response.status_code == 404
