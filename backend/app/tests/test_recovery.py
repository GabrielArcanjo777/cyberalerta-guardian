from fastapi.testclient import TestClient
from main import app


def test_recovery_paid_true_returns_checklist():
    client = TestClient(app)
    payload = {
        "paid": True,
        "clicked_link": False,
        "shared_documents": False,
        "shared_password": False,
        "installed_app": False,
        "shared_sms_code": False,
    }
    response = client.post("/recovery", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Contactar instituicao financeira imediatamente." in data["checklist"]
    assert "Registrar ocorrencia de fraude e bloquear transacao." in data["checklist"]


def test_safety_policy_service_exists_and_can_be_called():
    from app.services.safety_policy import SafetyPolicyService

    policy = SafetyPolicyService()
    policy.check_text("Este texto e seguro.")
    try:
        policy.check_text("Este texto contem phishing")
    except ValueError as exc:
        assert "blocked by safety policy" in str(exc)
    else:
        assert False, "SafetyPolicyService did not block forbidden text"
